---
name: systematic-debugging
version: 1.0
triggers:
  - debug
  - 除錯
  - 錯誤
  - bug
  - fix
  - 失敗
  - error
  - exception
priority: normal
---

# Systematic Debugging - 系統化除錯

## 核心原則

**除錯是一個系統化的過程，不是猜謎遊戲**。遵循科學方法：觀察、假設、驗證、修復。

### 為什麼需要系統化除錯？

- ❌ **不要**隨機修改程式碼碰運氣
- ❌ **不要**一次改變多個地方
- ✅ **要**系統化地縮小問題範圍
- ✅ **要**記錄並驗證每個假設

## 除錯流程

### 步驟 1: 重現問題

**在修復之前，必須能夠穩定重現問題。**

```markdown
## 問題重現步驟

1. 環境：[OS, Python version, dependencies]
2. 執行：[具體的命令]
3. 輸入：[輸入資料]
4. 預期結果：[應該發生的事]
5. 實際結果：[實際發生的事]
6. 發生頻率：[總是/有時/很少]
```

**檢查清單：**
- [ ] 能在本地環境重現嗎？
- [ ] 能在測試環境重現嗎？
- [ ] 有最小重現範例嗎？
- [ ] 問題是確定性的還是隨機的？

### 步驟 2: 閱讀完整錯誤訊息

**錯誤訊息是最好的朋友，仔細閱讀每一個字。**

```python
# ❌ 不要只看最後一行
Traceback (most recent call last):
  File "app.py", line 42, in <module>
    result = process_data(data)
  File "processor.py", line 15, in process_data
    return validate(data)
  File "validator.py", line 8, in validate
    raise ValidationError("Invalid email format")
ValidationError: Invalid email format

# ✅ 要從上到下完整閱讀
# 1. 錯誤類型：ValidationError
# 2. 錯誤訊息：Invalid email format
# 3. Stack trace: app.py → processor.py → validator.py
# 4. 問題位置：validator.py line 8
```

**常見錯誤類型：**
- `TypeError`: 型別錯誤
- `ValueError`: 值錯誤
- `KeyError`: 字典 key 不存在
- `IndexError`: 陣列索引超出範圍
- `AttributeError`: 屬性不存在
- `ImportError`: 匯入模組失敗

### 步驟 3: 縮小問題範圍

**使用二分法或逐步排除法找到問題根源。**

#### 方法 1: 二分法

```python
# 問題發生在 A → B → C → D 之間

# Step 1: 在 B 和 C 之間檢查
check_state_after_B()

# 如果狀態正確 → 問題在 C → D
# 如果狀態錯誤 → 問題在 B 或之前
```

#### 方法 2: 添加日誌

```python
import logging

logging.basicConfig(level=logging.DEBUG)

def process_data(data):
    logging.debug(f"Input data: {data}")
    
    result = validate(data)
    logging.debug(f"Validation result: {result}")
    
    return transform(result)
```

#### 方法 3: 使用 debugger

```bash
# 使用 pdb
python -m pdb app.py

# 常用命令
# n (next) - 執行下一行
# s (step) - 進入函式
# c (continue) - 繼續執行
# l (list) - 顯示程式碼
# p variable (print) - 列印變數
# q (quit) - 退出 debugger
```

### 步驟 4: 建立假設並驗證

**基於觀察提出可能的原因，然後逐一驗證。**

```markdown
## 假設驗證表

| 假設 | 驗證方法 | 結果 | 結論 |
|------|---------|------|------|
| 輸入資料格式錯誤 | print(data) | 確認 | ✅ 可能是原因 |
| 資料庫連線中斷 | check_connection() | 正常 | ❌ 排除 |
| 記憶體不足 | free -m | 充足 | ❌ 排除 |
```

### 步驟 5: 修復並驗證

**找到根本原因後，實施修復並全面驗證。**

```markdown
## 修復檢查清單

- [ ] 修復能解決當前問題嗎？
- [ ] 現有測試仍然通過嗎？
- [ ] 需要添加新測試防止回歸嗎？
- [ ] 修復會引入其他問題嗎？
- [ ] 需要在其他環境驗證嗎？
```

## 除錯工具

### Python Debugger (pdb)

```python
import pdb

def problematic_function():
    x = 42
    pdb.set_trace()  # 設定斷點
    y = x / 0  # 會在這裡暫停
    return y
```

### Logging

```python
import logging

# 設定 logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 使用
logger = logging.getLogger(__name__)
logger.debug("詳細資訊")
logger.info("一般資訊")
logger.warning("警告")
logger.error("錯誤")
logger.critical("嚴重錯誤")
```

### Exception Handling

```python
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"SpecificError: {e}", exc_info=True)
    handle_specific_error(e)
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise
finally:
    cleanup()
```

## 常見問題模式

### 1. NoneType Error

```python
# 錯誤：AttributeError: 'NoneType' object has no attribute 'foo'

# 原因：函式沒有 return 或 return None

# 修復：
def get_data():
    if condition:
        return Data()
    return None  # 明確 return None

# 使用前檢查
data = get_data()
if data is not None:
    data.foo()
```

### 2. Mutable Default Arguments

```python
# ❌ 錯誤
def append_to_list(item, my_list=[]):  # mutable default
    my_list.append(item)
    return my_list

# ✅ 正確
def append_to_list(item, my_list=None):
    if my_list is None:
        my_list = []
    my_list.append(item)
    return my_list
```

### 3. Variable Scope Issues

```python
# ❌ 錯誤
x = 10
def modify_global():
    x = 20  # 這建立了新的 local variable

# ✅ 正確
x = 10
def modify_global():
    global x
    x = 20
```

### 4. Off-by-One Errors

```python
# ❌ 錯誤
for i in range(len(items)):  # 可能超出範圍
    process(items[i])

# ✅ 正確
for item in items:
    process(item)

# 或使用 enumerate
for i, item in enumerate(items):
    print(f"{i}: {item}")
```

## 預防勝於治療

### 1. 編寫清晰的程式碼

```python
# ❌ 難以理解
d = [x * 2 for x in data if x > 0]

# ✅ 清晰
positive_numbers = [x for x in data if x > 0]
doubled = [x * 2 for x in positive_numbers]
```

### 2. 使用有意義的名稱

```python
# ❌ 模糊
def calc(a, b):
    return a * b

# ✅ 清晰
def calculate_area(width, height):
    return width * height
```

### 3. 添加文件字串

```python
def process_payment(amount, currency):
    """
    Process a payment transaction.
    
    Args:
        amount: Payment amount (must be positive)
        currency: Currency code (e.g., 'USD', 'EUR')
    
    Returns:
        Transaction ID string
    
    Raises:
        ValueError: If amount is negative
        InvalidCurrencyError: If currency code is invalid
    """
    ...
```

### 4. 編寫測試

```python
def test_process_payment_negative_amount():
    with pytest.raises(ValueError):
        process_payment(-100, 'USD')
```

## 與其他技能的整合

### TDD → Debugging

TDD 可以預防大部分 bug，當測試失敗時，使用 debugging 技巧找出原因。

### Subagent-Driven → Debugging

執行任務時遇到錯誤，暫停並使用 debugging skill。

### Brainstorming → Debugging

複雜問題可能需要 brainstorming 來集思廣益。

## 除錯心態

### ✅ 健康的心態

- 錯誤是學習的機會
- 每個 bug 都有原因
- 系統化方法最有效
- 求助是聰明的表現

### ❌ 不健康的心態

- 都是別人的錯
- 一定是機器問題
- 我應該憑直覺就知道
- 求助是軟弱的表現

---

**版本:** 1.0  
**最後更新:** 2026-04-02  
**相關技能:** test-driven-development, subagent-driven, brainstorming
