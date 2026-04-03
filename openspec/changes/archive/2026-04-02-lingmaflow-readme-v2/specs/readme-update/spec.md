## ADDED Requirements

### Requirement: README 文檔完整性
README.md  SHALL 包含 LingmaFlow v0.2.1 的完整功能說明，包括安裝、使用、CLI 命令、OpenSpec 整合和已知問題。

#### Scenario: 用戶查看安裝說明
- **WHEN** 用戶閱讀 README 的安裝章節
- **THEN** 能看到完整的安裝步驟（建立虛擬環境、pip install、驗證安裝）

#### Scenario: 用戶查看 OpenSpec 整合範例
- **WHEN** 用戶閱讀 OpenSpec 整合章節
- **THEN** 能看到完整的 spec-driven 工作流程範例，包含 proposal → design → specs → tasks

#### Scenario: 用戶遇到已知問題
- **WHEN** 用戶在實戰中遇到問題（如 checkpoint result 顯示物件、Done Conditions 消失等）
- **THEN** 能在「已知問題」章節找到對應的問題描述、原因分析和解決方案

### Requirement: 雙語支持
README.md SHALL 同時提供中文（繁體）和英文版本，每個主要章節都應有雙語內容。

#### Scenario: 中文用戶閱讀
- **WHEN** 中文母語用戶閱讀 README
- **THEN** 能找到完整的中文說明，包括所有功能、範例和故障排除

#### Scenario: 英文用戶閱讀
- **WHEN** 英文母語用戶閱讀 README
- **THEN** 能找到完整的英文說明，內容與中文版對等

### Requirement: 已知問題章節格式
已知問題章節 SHALL 採用標準化格式：問題編號、標題、症狀、原因、解決方案。

#### Scenario: 問題描述清晰
- **WHEN** 用戶查看某個已知問題
- **THEN** 能看到明確的「症狀」描述，包含實際的終端輸出或錯誤訊息

#### Scenario: 問題解決方案可執行
- **WHEN** 用戶需要解決某個問題
- **THEN** 能提供可直接複製貼上執行的解決方案代碼或命令
