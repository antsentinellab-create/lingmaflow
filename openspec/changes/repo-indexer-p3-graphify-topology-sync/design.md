## Context

目前 repo-indexer 的架構位於 `.lingma/skills/repo-indexer/`：
- `scripts/build_index.py`：使用 LlamaIndex CodeSplitter 切片並存入 Chroma (`repo-index/`)
- `scripts/call_graph.py`：使用 Tree-sitter 解析 AST，但僅為暫時性分析，未持久化
- `scripts/enhanced_query.py`：僅支援向量檢索與 Reranker，缺乏圖譜導航能力

P2 階段已驗證基本的 Call Graph 分析邏輯，現在需要將其整合到完整的索引建構流程中，實現「向量找語義，圖譜找邏輯」的 Hybrid RAG 能力。經過五輪技術審查，已識別並解決以下關鍵風險：
1. Chunk 與 AST 維度錯位（多對多映射）
2. NetworkX 3.0+ API 棄用（改用 JSON）
3. 拓撲擴散缺水合機制
4. 建構順序因果倒置
5. GraphML 序列化異常（List 不相容）
6. 預設行號導致的幽靈映射
7. 上下文爆炸（工具函數無差別擴散）
8. 絕對路徑跨環境失效
9. 換行符跨平台陷阱（LF vs CRLF）
10. 大檔案 JSON 記憶體壓力
11. 檔案鎖孤兒問題

## Goals / Non-Goals

**Goals:**
- 實作 `GraphManager` 類別，封裝 NetworkX 進行圖結構管理，採用 JSON 持久化
- 定義 Module、Class、Function 三種節點類型及其屬性（含相對路徑、行號範圍）
- 建立 Chroma UUID 與圖譜節點的雙向映射機制（多對多，基於行號交集）
- 實作 **Atomic Write** 與 **SafeFileLock**（含孤兒鎖檢測）確保並發安全
- 實作 `PrecisionLineCodeSplitter`，透過 Char Offset 追蹤精確行號，解決 LF/CRLF 陷阱
- 升級 `build_index.py` 為雙維索引建構（AST 優先 → Chunking → UUID 綁定）
- 實作 Hybrid Retrieval：向量檢索 + 拓撲擴散（含 Degree Filtering）
- 實作 Code Hydration：從檔案系統讀取鄰居節點的實際原始碼
- 強制 `node_id` 為字串型別，防止序列化過程中的型別漂移
- 新增 RSS 記憶體峰值監控，預防 OOM 風險
- 完整的單元測試覆蓋（特別是行號精準度、原子寫入完整性、度數過濾有效性）

**Non-Goals:**
- 圖譜視覺化（Mermaid 或其他 UI）
- 增量更新圖譜（每次重建）
- 分散式圖譜儲存或圖資料庫（如 Neo4j、Kùzu）
- 即時圖譜同步（批次處理即可）
- 複雜的圖演算法（如最短路徑、社群偵測、PageRank）
- 支援多種程式語言的細緻語法（先聚焦 Python）
- 熱重載或動態更新圖譜

## Decisions

### 1. 映射策略：行號交集 (Line Number Intersection)

**選擇**: 維持 CodeSplitter 的 40 行重疊切片以確保語義完整。在 `build_index.py` 中，透過 `PrecisionLineCodeSplitter` 取得的 `start_line` 與 AST 節點的 `[start, end]` 範圍進行比對，建立 `vector_id ↔ [node_ids]` 的多對多關係。

**原因**:
- RAG 檢索品質優先：強制按函數邊界切片會導致大型函數成為超大 Chunk，稀釋向量相似度
- 多對多映射更符合現實：一個 Chunk 可能涉及多個函數的交互邏輯
- 實施風險較低：不需改動現有的 LlamaIndex CodeSplitter 核心邏輯，僅在 metadata 提取層增強

**替代方案考慮**:
- Semantic Chunking（完全按函數邊界切片）：會破壞代碼的語義連貫性，不利於向量檢索
- 單一映射（1:1）：無法處理跨函數的 Chunk，導致資訊遺失

### 2. 持久化格式：JSON (Node Link Data)

**選擇**: 使用 `nx.node_link_data()` 轉換為 JSON 格式，而非 GraphML 或 Pickle。

**原因**:
- JSON 原生支援 List/Dict 等複雜資料結構，無需手動轉換
- 人類可讀性佳，方便除錯與版本控制（Git Diff）
- NetworkX 原生支援 `node_link_data` / `node_link_graph`，API 穩定
- 跨語言相容性優於 Pickle

**替代方案考慮**:
- GraphML：不支援 Python List 屬性，需手動轉換為字串，增加複雜度
- Pickle (gpickle)：NetworkX 3.0+ 已移除相關 API，且有安全性疑慮
- 圖資料庫（Neo4j/Kùzu）：過度設計，增加部署與維護成本

### 3. 並發安全：Atomic Write + SafeFileLock

**選擇**: 
- **Atomic Write**：先寫入 `topology.json.tmp`，完成後執行 `os.replace()` 原子替換
- **SafeFileLock**：使用 `fcntl.flock()` 取得排他鎖，並實作超時機制（5 分鐘）檢測孤兒鎖

**原因**:
- `os.replace()` 在 POSIX 系統上是原子操作，確保不會出現截斷的 JSON 檔案
- File Lock 防止多進程同時寫入導致的競態條件
- 孤兒鎖檢測（檢查 .lock 檔案的 mtime 與 PID）防止自動化腳本死鎖

**實作細節**:
```python
# Atomic Write
fd, tmp_path = tempfile.mkstemp(dir=db_path.parent, suffix='.json.tmp')
with os.fdopen(fd, 'w') as f:
    json.dump(data, f)
os.replace(tmp_path, db_path)  # 原子替換

# SafeFileLock with timeout
if lock_age > 300 seconds and pid not in running_processes:
    break_stale_lock()
```

**替代方案考慮**:
- 無鎖設計：在高並發環境下會導致資料損毀
- 資料庫事務：增加依賴與複雜度，對於 JSON 檔案來說過度設計

### 4. 拓撲擴散：度數過濾 (Degree Filtering)

**選擇**: 在 `enhanced_query.py` 中，當啟用 `--with-graph` 時，檢查鄰居節點的 In-Degree（被呼叫次數）。若大於閾值（預設 10），則視為通用工具函數（如 `logger.info`, `utils.get_time`）並跳過水合。

**原因**:
- 防止上下文爆炸：高度數節點的擴散會抓取數百個無關的呼叫者，撐爆 LLM 的 Context Window
- 提升查詢相關性：過濾掉通用工具函數後，保留的鄰居更可能是業務邏輯相關的代碼

**實作細節**:
```python
def get_filtered_neighbors(self, node_id: str, hop: int = 1, max_in_degree: int = 10):
    for neighbor in neighbors:
        if self.graph.in_degree(neighbor) > max_in_degree:
            continue  # 跳過高度數節點
        filtered_neighbors.append(neighbor)
```

**替代方案考慮**:
- 無過濾擴散：會導致 Token 用量暴增，查詢成本提高 10-100 倍
- PageRank 排序：計算成本高，且對於小型專案收益不明顯

### 5. 跨平台一致性：換行符正規化

**選擇**: 在 `PrecisionLineCodeSplitter` 讀取檔案時，統一使用 `newline=''` 開啟，並將所有 `\r\n` 強制轉換為 `\n`，確保 `char_offset` 與 `count('\n')` 在所有作業系統上行為一致。

**原因**:
- Windows 使用 `\r\n`（2 字元），Linux/Mac 使用 `\n`（1 字元）
- 若不正規化，`content[:char_pos].count('\n')` 會產生 ±1 的行號位移
- Tree-sitter 解析時也基於正規化後的內容，確保 AST 節點的行號與 Chunk 一致

**實作細節**:
```python
with open(file_path, 'r', encoding='utf-8', newline='') as f:
    raw_content = f.read()
content = raw_content.replace('\r\n', '\n').replace('\r', '\n')
```

**替代方案考慮**:
- 依賴 Python 自動轉換：會導致 `char_offset` 與實際檔案位置不一致
- 分別處理不同平台：增加維護成本，且容易遺漏邊緣情況

### 6. 型別防護：強制字串 ID

**選擇**: 在 `GraphManager.add_node()` 入口處加入 `assert isinstance(node_id, str)`，並在文件規範中強制規定 `node_id` 必須為字串。

**原因**:
- NetworkX 的 `node_link_data` 在轉 JSON 時，會將非字串類型的節點 ID 統一轉為字串
- 若記憶體中的 ID 是 Tuple 或數字，載入後會變成 String，導致後續的 ID 匹配邏輯失效
- 早期失敗（Fail Fast）比隱性錯誤更容易除錯

**實作細節**:
```python
def add_node(self, node_id: str, ...):
    if not isinstance(node_id, str):
        raise TypeError(f"node_id must be a string. Got {type(node_id)}")
```

### 7. 建構順序：AST 優先 (AST-First Construction)

**選擇**: 反轉原有的建構流程，改為：
1. **Phase 1**: 遍歷所有 Python 檔案，執行 Tree-sitter 解析，建立純 AST 圖譜（節點 + 邊）
2. **Phase 2**: 執行 CodeSplitter 切片，嵌入並存入 Chroma，取得 UUID
3. **Phase 3**: 遍歷每個 Chunk，根據 `file_path` 與 `start_line/end_line`，與 AST 節點進行行號交集比對，綁定 `vector_id`

**原因**:
- 避免「平行時空」問題：若先根據 Chunk 建立節點，再根據 AST 建立節點，兩者的 ID 命名規則若不完全對齊，會產生孤立節點
- AST 是權威來源：函數定義、類別繼承等結構化資訊只能從 AST 獲得，Chunk 只是文字片段

**實作細節**:
```python
# Phase 1: AST Parsing
for py_file in python_files:
    analyzer.parse_file_to_graph(py_file, graph_manager)

# Phase 2: Chunking & Embedding
nodes = splitter.get_nodes_from_documents(documents)
for node in nodes:
    chroma_uuid = collection.add(...)
    
    # Phase 3: Line Number Intersection
    graph_manager.link_vector_to_node(
        vector_id=chroma_uuid,
        chunk_start=node.metadata['start_line'],
        chunk_end=node.metadata['end_line'],
        file_path=node.metadata['file_path']
    )
```

### 8. Code Hydration：動態路徑解析

**選擇**: 在 `enhanced_query.py` 的 `_hydrate_code()` 方法中，從圖譜節點讀取相對路徑，並動態拼接當前的 Repo Root，再讀取實際檔案的行範圍。

**原因**:
- 拓撲擴散回傳的鄰居節點 ID 本身沒有意義，LLM 需要看到實際的原始碼才能理解上下文
- 相對路徑確保跨環境相容（不同開發者、CI/CD 環境）

**實作細節**:
```python
def _hydrate_code(self, node_id: str) -> Optional[str]:
    attrs = self.graph.nodes[node_id]
    relative_path = attrs['file_path']
    start_line = attrs['start_line']
    end_line = attrs['end_line']
    
    full_path = self.repo_root / relative_path
    with open(full_path, 'r') as f:
        lines = f.readlines()
        return ''.join(lines[start_line-1:end_line])
```

## Risks / Trade-offs

### [Risk] 大檔案 JSON 的記憶體壓力

**風險**: 當 Repo 規模達到 10 萬個節點（含複雜關係邊）時，`nx.node_link_data()` 會將整個圖譜轉為巨大的 Python Dict，隨後 `json.dump()` 會在記憶體中再產生一份字串，可能瞬間消耗數 GB 記憶體，導致 OOM。

**緩解**:
- 目前在 `tasks.md` 中加入 RSS 記憶體峰值監控任務
- 若未來圖譜超過 500MB，考慮改用 `ijson`（串流寫入）或切換至圖資料庫（如 Kùzu）
- 當前 AI-Factory 專案規模（< 1000 檔案）尚可應付

### [Risk] Tree-sitter 解析準確性

**風險**: 動態語言特性（如 `getattr`、`eval`、`importlib`）可能導致 CALLS 關係遺漏。

**緩解**:
- 文件說明限制：靜態分析無法捕捉動態調用
- 優先保證正確性（不漏報誤報），而非完整性
- 未來可結合執行時追蹤（profiling）補充

### [Risk] 行號映射的精準度

**風險**: 若 `PrecisionLineCodeSplitter` 的 Char Offset 計算錯誤，會導致 vector_id 綁定到錯誤的 AST 節點。

**緩解**:
- 實作嚴格的測試案例：在檔案頭、中、尾放置三個一模一樣的 `def hello(): pass`，驗證是否能精準產出三個不同的 ID 且行號全對
- 統一新行符為 `\n`，消除跨平台差異
- 使用 `newline=''` 讀取檔案，防止 Python 自動轉換

### [Trade-off] 建圖時間 vs 查詢效能

**選擇**: 接受較長的建圖時間（+30-50%），換取查詢時的拓撲上下文。

**原因**:
- 建圖是離線操作（一天一次或手動觸發）
- 查詢是線上操作（頻繁執行），需要快速回應與豐富上下文
- 空間換時間的典型 trade-off

### [Risk] 孤兒鎖誤判

**風險**: 若 `.lock` 檔案存在超過 5 分鐘，但原進程仍在運行（例如長時間的索引建構），可能會被誤判為孤兒鎖並強制清除。

**緩解**:
- 進一步檢查 PID 是否還在進程清單中（`psutil.pid_exists()`）
- 若 PID 仍存在，延長等待時間而非強制清除
- 記錄警告訊息，提醒使用者檢查進程狀態

## Migration Plan

### 階段 1: 核心實作（本次）
1. 實作 `scripts/graph_manager.py`（含 Atomic Write、SafeFileLock、JSON 持久化）
2. 實作 `scripts/precision_splitter.py`（Char Offset 追蹤、換行符正規化）
3. 修改 `scripts/build_index.py` 整合雙維索引建構（AST 優先流程）
4. 升級 `scripts/enhanced_query.py` 實作 Hybrid Retrieval（含 Code Hydration、Degree Filtering）
5. 編寫 `scripts/test_graph_integrity.py`

### 階段 2: 驗證與除錯
1. 執行 `build_index.py`，驗證 `repo-graph/topology.json` 生成且無損毀
2. 執行測試案例，驗證行號精準度（Boilerplate 測試）
3. 模擬並發寫入，驗證 Atomic Write 與 SafeFileLock 的有效性
4. 執行 `enhanced_query.py "trace_impact WorkflowOrchestrator" --with-graph`，驗證拓撲導航與水合結果
5. 監控 RSS 記憶體峰值，確保無 OOM 風險

### 階段 3: 整合與文件
1. 更新 `.lingma/skills/repo-indexer/SKILL.md` 與 `README.md`，說明 Hybrid RAG 功能
2. 添加使用範例與 CLI 參數說明
3. 歸檔此變更

**回滾策略**:
- 若圖譜建構失敗，可降級為純向量模式（移除 `--with-graph` 參數）
- 刪除 `repo-graph/` 目錄即可恢復原狀
- 使用 git revert 回滾程式碼變更

## Open Questions

1. **是否需要支援增量更新？**
   - 目前是每次重建，對於大型專案可能耗時
   - 未來可考慮偵測檔案變更，僅更新受影響的節點與邊

2. **度數閾值（max_in_degree）是否應設為可配置？**
   - 目前硬編碼為 10
   - 未來可改為 CLI 參數 `--max-in-degree N`，讓使用者根據專案特性調整

3. **是否需要圖譜視覺化工具？**
   - 目前僅程式化存取
   - 未來可提供 Mermaid 或 Graphviz 匯出功能，協助開發者理解代碼結構

4. **如何處理循環依賴？**
   - NetworkX 可處理循環，但拓撲擴散時需注意避免無限迴圈
   - 目前已實作 `visited set` 防止重複訪問

5. **是否需要支援多語言？**
   - 目前僅針對 Python
   - 未來可擴展 Tree-sitter grammar 支援 JavaScript、TypeScript、Go 等語言
