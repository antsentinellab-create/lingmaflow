## 1. 環境設置與依賴

- [x] 1.1 將 `networkx>=3.0` 加入 `.lingma/skills/repo-indexer/scripts/requirements.txt`
- [x] 1.2 建立 `.lingma/skills/repo-indexer/repo-graph/` 目錄並包含 `.gitkeep` 檔案
- [x] 1.3 驗證 `.lingma/skills/repo-indexer/scripts/` 中的現有檔案：build_index.py, enhanced_query.py, call_graph.py
- [x] 1.4 安裝依賴套件：`.venv/bin/pip install networkx llama-index chromadb tree-sitter-python`

## 2. 核心實作 - GraphManager 含原子寫入

- [ ] 2.1 建立 `.lingma/skills/repo-indexer/scripts/graph_manager.py` 模組
- [ ] 2.2 實作 `GraphManager.__init__(db_path="repo-graph/topology.json")` 使用 NetworkX DiGraph
- [ ] 2.3 實作 `add_node(node_id: str, ...)` 含嚴格型別斷言：`assert isinstance(node_id, str)`
- [ ] 2.4 實作 `link_vector_to_node(vector_id, chunk_start, chunk_end, file_path)` 使用行號交集邏輯
- [ ] 2.5 實作 `get_nodes_by_vector_id(vector_id)` 用於從 vector_to_nodes 索引進行反向查詢
- [ ] 2.6 實作 `get_filtered_neighbors(node_id, hop=1, max_in_degree=10)` 含度數過濾以跳過工具函數
- [ ] 2.7 實作 `save()` 使用原子寫入模式：tempfile.mkstemp() → json.dump() → os.replace()
- [ ] 2.8 實作 `SafeFileLock` 類別使用 fcntl.flock() 與孤兒鎖檢測（5分鐘超時 + PID 檢查）
- [ ] 2.9 實作 `load()` 使用 `nx.node_link_graph()` 並重建 vector_to_nodes 反向索引
- [ ] 2.10 確保所有 file_path 屬性儲存為相對路徑（非絕對路徑）

## 3. 精確切片器 - 字元偏移量行號追蹤

- [ ] 3.1 建立 `.lingma/skills/repo-indexer/scripts/precision_splitter.py` 模組
- [ ] 3.2 實作 `PrecisionLineCodeSplitter` 類別繼承 LlamaIndex CodeSplitter
- [ ] 3.3 覆寫 `get_nodes_from_documents()` 以在切片過程中追蹤字元偏移量
- [ ] 3.4 實作跨平台換行符正規化：使用 `newline=''` 讀取，將 `\r\n` 轉換為 `\n`
- [ ] 3.5 使用 `content[:char_pos].count('\n') + 1` 計算每個 chunk 的精確 start_line
- [ ] 3.6 注入精確 metadata：`node.metadata['start_line']`, `node.metadata['end_line']`, `node.metadata['file_path']`（相對路徑）
- [ ] 3.7 移除所有模糊比對邏輯（str.find, str.index）以防止樣板代碼錯位
- [ ] 3.8 測試三個不同位置的相同 `def hello(): pass` 以驗證 100% 準確率

## 4. 索引建構整合 - AST 優先的雙維建構

- [ ] 4.1 修改 `.lingma/skills/repo-indexer/scripts/build_index.py` 以匯入 GraphManager 和 PrecisionLineCodeSplitter
- [ ] 4.2 重構建構流程：階段 1 - 使用 CallGraphAnalyzer 解析 AST 以建立純圖譜結構
- [ ] 4.3 階段 2 - 使用 PrecisionLineCodeSplitter 取代標準 CodeSplitter 以獲得精確行號
- [ ] 4.4 階段 3 - Chroma 儲存後，對每個 chunk 呼叫 `graph_manager.link_vector_to_node()` 使用行號交集
- [ ] 4.5 在儲存至圖譜節點前將所有檔案路徑轉換為相對路徑（使用 `Path.relative_to(repo_root)`）
- [ ] 4.6 新增 RSS 記憶體監控日誌鉤子：每處理 100 個檔案記錄一次 `psutil.Process.memory_info().rss`（單位：MB），作為未來是否切換至 ijson 的科學依據
- [ ] 4.7 在索引結束時呼叫 `graph_manager.save()` 含原子寫入保護
- [ ] 4.8 驗證 topology.json 存在且在建構完成後為有效的 JSON

## 5. 增強查詢 - 混合檢索含代碼水合

- [ ] 5.1 修改 `.lingma/skills/repo-indexer/scripts/enhanced_query.py` 以新增 `--with-graph` CLI 參數
- [ ] 5.2 新增 `--max-in-degree` 參數（預設值：10）用於可配置的度數過濾
- [ ] 5.3 新增 `--repo-root` 參數（預設值："."）用於動態路徑解析
- [ ] 5.4 當啟用 --with-graph 時初始化 GraphManager
- [ ] 5.5 實作階段 1：向量搜尋（重用現有的 retriever 邏輯）
- [ ] 5.6 實作階段 2：從結果中提取 vector_ids 並查詢對應的 AST 節點 ID
- [ ] 5.7 實作階段 3：呼叫 `graph_manager.get_filtered_neighbors()` 進行拓撲擴散
- [ ] 5.8 實作 `_hydrate_code(node_id)` 方法從檔案系統讀取實際原始碼使用相對路徑 + repo_root
- [ ] 5.9 格式化輸出以包含 `vector_results` 和 `graph_context` 含水合的代碼片段
- [ ] 5.10 優雅處理遺失的 vector_id：降級至純向量模式並顯示警告訊息

## 6. 測試基礎設施 - 圖譜完整性驗證

- [ ] 6.1 建立 `.lingma/skills/repo-indexer/scripts/test_graph_integrity.py` 測試套件
- [ ] 6.2 使用 tmp_path 設置 pytest fixtures 含臨時 repo-graph 目錄
- [ ] 6.3 建立輔助函數以建構已知結構的範例圖譜供測試使用
- [ ] 6.4 Mock Chroma 回應以進行隔離的單元測試（無需真實嵌入）

## 7. 單元測試 - GraphManager 核心功能

- [ ] 7.1 測試 `add_node()` 建立含正確屬性的節點（type, file_path, start_line, end_line, vector_ids=[]）
- [ ] 7.2 測試 `add_node()` 當 node_id 非字串時拋出 TypeError（例如：tuple, int）
- [ ] 7.3 測試 `link_vector_to_node()` 正確連結 vector_id 至具有交集行號範圍的節點
- [ ] 7.4 測試多對多映射：當 chunk 橫跨多個函數時，一個 vector_id 連結至多個節點
- [ ] 7.5 測試 `get_nodes_by_vector_id()` 回傳正確的節點 ID 列表
- [ ] 7.6 測試 `get_filtered_neighbors()` 跳過 in_degree > max_in_degree 閾值的節點
- [ ] 7.7 測試 `save()` 在寫入期間建立 topology.json 檔案和 .lock 檔案
- [ ] 7.8 測試 `load()` 正確還原圖譜並重建 vector_to_nodes 索引
- [ ] 7.9 測試空圖譜操作回傳適當的預設值（空列表、None）

## 8. 單元測試 - 原子寫入與並發安全

- [ ] 8.1 測試原子寫入：模擬 json.dump 期間崩潰並驗證無損毀的 topology.json 存在
- [ ] 8.2 測試 SafeFileLock：兩個並發的 save() 呼叫應正確序列化（第二個等待第一個）
- [ ] 8.3 測試孤兒鎖檢測：建立含舊時間戳記（>5 分鐘）的 .lock 檔案並驗證其自動清除
- [ ] 8.4 測試含 List 屬性的 JSON 序列化：驗證 vector_ids 列表在 save/load 週期後正確保留

## 9. 單元測試 - 精確行號映射

- [ ] 9.1 測試 PrecisionLineCodeSplitter 處理 CRLF 檔案：驗證正規化後行號符合預期值
- [ ] 9.2 測試不同位置的三個相同函數：驗證每個 chunk 映射至正確的函數節點（無幽靈映射）
- [ ] 9.3 測試橫跨多個函數的 chunk：驗證 vector_id 連結至所有交集節點（多對多）
- [ ] 9.4 測試相對路徑轉換：驗證 file_path 儲存為相對路徑，非絕對路徑

## 10. 整合測試 - 端到端工作流

- [ ] 10.1 在 AI-Factory 專案上執行 `build_index.py` 並驗證 repo-graph/topology.json 已生成
- [ ] 10.2 驗證 topology.json 結構：檢查節點數量是否符合預期的函數/類別/模組定義
- [ ] 10.3 執行測試腳本抽查映射一致性：驗證 Chroma UUIDs 與圖譜 vector_ids 相符（預期 100% 匹配率）
- [ ] 10.4 執行 `enhanced_query.py "trace_impact WorkflowOrchestrator" --with-graph` 並驗證輸出包含 graph_context
- [ ] 10.5 比較有無 --with-graph 的查詢結果：驗證圖譜上下文新增呼叫者/被呼叫者資訊
- [ ] 10.6 測試度數過濾：查詢呼叫 logger.info 的函數並驗證 logger 節點被排除（in_degree > 10）
- [ ] 10.7 測試代碼水合：驗證 graph_context 包含實際原始碼片段，不僅是節點 ID
- [ ] 10.8 監控 build_index.py 期間的 RSS 記憶體峰值與增長趨勢：確保無 OOM 錯誤（當前專案規模應 < 2GB），並記錄 node_link_data 轉換時的記憶體壓力

## 11. 文件與清理

- [ ] 11.1 為 graph_manager.py 中所有公開方法新增 docstrings 說明參數與回傳型別
- [ ] 11.2 更新 `.lingma/skills/repo-indexer/SKILL.md` 含 Hybrid RAG 使用範例與 --with-graph 旗標文件
- [ ] 11.3 更新 `.lingma/skills/repo-indexer/README.md` 含顯示雙維索引流程的架構圖
- [ ] 11.4 在 build_index.py 中新增內聯註解說明 AST 優先建構順序的原理
- [ ] 11.5 新增疑難排解章節：常見問題（孤兒鎖、路徑解析失敗）與解決方案
- [ ] 11.6 執行完整測試套件：`pytest scripts/test_graph_integrity.py -v` 並確保 100% 通過率
- [ ] 11.7 驗證所有完成條件已達成：檔案存在、測試全綠、topology.json 已生成
- [ ] 11.8 更新 TASK_STATE.md 含完成狀態與做出的關鍵決策
- [ ] 11.9 將此變更歸檔至 openspec/changes/archive/
