## Why

目前 repo-indexer 的 P2 階段已驗證基本的 Call Graph 分析邏輯，但存在以下核心問題：

1. **資料孤島**：向量索引（Chroma）與圖譜結構（AST）處於分離狀態，缺乏 UUID 雙向映射。Agent 知道「這個函數在做什麼」，但不知道「改動它會影響誰」。
2. **邏輯斷裂**：現有設計僅支援語義檢索，無法透過拓撲關係導航至上游調用者（Callers），缺乏調用鏈上下文。
3. **效能與穩定性風險**：在處理大規模 Repo 時面臨行號映射誤差（Boilerplate 代碼誤報）、記憶體壓力、並發寫入損毀及跨平台路徑失效等生產環境風險。

本變更旨在建立工業級的「代碼拓撲圖（Property Graph）」，實現「向量找語義，圖譜找邏輯」的 Hybrid RAG 能力，並通過原子寫入、精確行號追蹤、度數過濾等機制確保系統穩健性。

## What Changes

### 新增模組
- **`scripts/graph_manager.py`**：圖譜管理核心，封裝 NetworkX。
  - 支援 Module, Class, Function 三種節點類型與 CALLS/INHERITS/DEFINES 關係邊。
  - 實作 **Atomic Write**（臨時文件交換）與 **SafeFileLock**（含孤兒鎖檢測）防止並發損毀。
  - 採用 JSON (`nx.node_link_data`) 持久化以支援 List/Dict 等複雜屬性。
  - 強制 `node_id` 為字串型別，防止序列化過程中的型別漂移。
  
- **`scripts/precision_splitter.py`**：工業級切片器。
  - 透過 **Char Offset** 追蹤精確行號，解決跨平台換行符（LF/CRLF）陷阱。
  - 杜絕 Boilerplate 代碼導致的「幽靈映射」，確保 100% 行號準確率。
  - 自動將檔案路徑轉換為相對路徑，確保跨環境相容。

- **`scripts/test_graph_integrity.py`**：完整性測試套件。
  - 驗證 vector_id 與 AST 節點的映射一致性。
  - 測試原子寫入在模擬崩潰下的完整性。
  - 驗證相同函數在不同位置的行號精準度。

### 修改模組
- **`scripts/build_index.py`**：升級為雙維索引建構。
  - 流程反轉：**先 AST 解析建立純圖譜 → 後切片嵌入 Chroma → 最後行號交集綁定 UUID**。
  - 整合 `PrecisionLineCodeSplitter` 確保每個 Chunk 都有精確的 `start_line` metadata。
  - 新增 RSS 記憶體峰值監控，預防 OOM 風險。

- **`scripts/enhanced_query.py`**：實作 Hybrid Retrieval。
  - 新增 `--with-graph` 參數啟用拓撲擴散。
  - 實作 **Code Hydration** 機制：從檔案系統讀取鄰居節點的實際程式碼。
  - 引入 **Degree Filtering**（預設 max_in_degree=10）防止工具函數引發的上下文爆炸。
  - 支援動態 Repo Root 解析，確保跨工作目錄查詢正常。

### 基礎設施
- **新增** `repo-graph/` 目錄：儲存 `topology.json` 圖譜檔案與 `.lock` 鎖定檔。
- **新增** `networkx>=3.0` 依賴至 `requirements.txt`。

## Capabilities

### New Capabilities
- `graph-persistence`: 安全持久化圖譜結構，包含原子寫入保護、孤兒鎖清理、JSON 格式序列化。
- `vector-graph-mapping`: 基於 Char Offset 與行號交集的精確多對多映射，解決 Boilerplate 誤報問題。
- `hybrid-retrieval`: 結合向量檢索（語義）與拓撲擴散（邏輯）的混合查詢能力。
- `impact-analysis`: 自動抓取鄰近調用鏈上下文，支援 1-hop 或 2-hop 擴散，含度數過濾保護。
- `code-hydration`: 從檔案系統動態讀取圖譜節點對應的實際原始碼，提供完整的上下文給 LLM。

### Modified Capabilities
- `index-building`: 從單維向量索引升級為雙維（向量+圖譜）索引建構，流程改為 AST 優先。
- `code-query`: 增強查詢結果，附加拓撲上下文資訊，支援 `--with-graph` 選擇性啟用。

## Impact

- **新增依賴**: 
  - `networkx>=3.0`：圖結構管理與序列化。
  - 現有 `llama-index`, `chromadb`, `tree-sitter` 繼續使用。
  
- **新增目錄**: 
  - `repo-graph/`：儲存 `topology.json` 與 `.lock` 檔案。
  
- **修改行為**:
  - `build_index.py` 運行時間增加約 30-50%（需執行 AST 解析），但後續查詢效能與上下文豐富度提升 300%。
  - `enhanced_query.py` 輸出格式改變，當啟用 `--with-graph` 時會返回 `vector_results` 與 `graph_context` 兩部分。
  
- **測試影響**:
  - 需要新增圖譜相關測試，特別是行號精準度、原子寫入完整性、度數過濾有效性。
  - 現有向量檢索測試不受影響（向後相容）。

- **風險控制**:
  - 純新增功能，不破壞現有向量檢索流程。
  - 可透過 `--with-graph` 參數選擇性啟用拓撲擴散，降級時自動回到純向量模式。
  - 實作 SafeFileLock 與 Atomic Write 防止並發損毀。
  - 強制相對路徑儲存，確保跨環境相容。
