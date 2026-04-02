## ADDED Requirements

### Requirement: InjectionError exception
系統 SHALL 定義 InjectionError 異常類別

#### Scenario: Inherit from Exception
- **WHEN** 建立 InjectionError 物件
- **THEN** 可作為一般 Exception 捕獲

#### Scenario: Descriptive error message
- **WHEN** 拋出 InjectionError
- **THEN** 錯誤訊息應指出無法寫入的原因（如權限、路徑不存在等）

### Requirement: Validate output path
inject() SHALL 在寫入前驗證路徑的可寫性

#### Scenario: Valid writable path
- **WHEN** 呼叫 inject(output_path) 且路徑可寫入
- **THEN** 成功寫入檔案，不拋出異常

#### Scenario: Permission denied
- **WHEN** 呼叫 inject(output_path) 但沒有寫入權限
- **THEN** 拋出 InjectionError

#### Scenario: Directory structure creation
- **WHEN** 呼叫 inject(output_path) 且 parent directories 不存在
- **THEN** 嘗試建立必要的目錄結構，失敗時拋出 InjectionError
