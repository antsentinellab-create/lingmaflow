---
name: test-driven-development
version: 1.0
triggers:
  - 寫測試
  - pytest
  - TDD
  - 單元測試
  - 測試
  - unit test
  - test first
priority: high
---

# Test-Driven Development - 測試驅動開發

## 核心原則

**先寫失敗的測試，再寫最少的程式碼讓測試通過，最後重構**。這個循環稱為 RED-GREEN-REFACTOR。

### 為什麼需要 TDD？

- ❌ **不要**先寫程式碼再補測試
- ❌ **不要**為了測試而測試
- ✅ **要**讓測試驅動設計
- ✅ **要**保持測試與程式碼同步演化

## RED-GREEN-REFACTOR 循環

### 1️⃣ RED - 寫一個失敗的測試

```python
# 第一步：寫一個會失敗的測試
def test_add_two_numbers():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    
# 執行測試 → FAIL (add 函式還不存在)
```

**重點：**
- 測試應該表達「意圖」而非「實作細節」
- 一次只測試一個行為
- 測試名稱應該清楚描述預期的行為

### 2️⃣ GREEN - 寫最少的程式碼讓測試通過

```python
# 第二步：實作剛好足夠的功能
def add(a, b):
    return a + b
    
# 執行測試 → PASS ✓
```

**重點：**
- 不要過度設計
- 可以寫「愚蠢」的實作（例如直接 return 預期值）
- 編譯錯誤也算 RED，解決後進入 GREEN

### 3️⃣ REFACTOR - 重構並保持測試通過

```python
# 第三步：重構程式碼
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b
    
# 執行測試 → 仍然 PASS ✓
```

**重點：**
- 保持程式碼簡潔、可讀、可維護
- 移除重複程式碼
- 改善命名和結構
- **測試必須始終通過**

## TDD 紀律

### ✅ 必須遵守的規則

1. **先寫測試**
   - 在寫任何功能程式碼之前，先寫測試
   - 測試失敗是预期的（RED）

2. **一次一個測試**
   - 不要一次寫多個測試
   - 完成一個 RED-GREEN-REFACTOR 循環後再寫下一個

3. **最少的程式碼**
   - 只寫剛好足夠讓測試通過的程式碼
   - 不要預測未來的需求

4. **保持測試通過**
   - 任何時候都不應該有失敗的測試
   - 如果新測試失敗，先修復它

### ❌ 禁止的行為

#### 1. 先寫程式碼再補測試

```python
# ❌ 錯誤做法
def calculate_discount(price, discount_rate):
    # 實作了 50 行邏輯
    ...

# 然後才想起來要寫測試
def test_calculate_discount():
    ...

# ✅ 正確做法
def test_calculate_discount_10_percent():
    assert calculate_discount(100, 0.1) == 90

# RED → 寫實作 → GREEN → REFACTOR
```

#### 2. 一次寫太多測試

```python
# ❌ 不要這樣做
def test_add_positive_numbers():
    assert add(2, 3) == 5

def test_add_negative_numbers():
    assert add(-1, -2) == -3

def test_add_mixed_numbers():
    assert add(-1, 1) == 0

# 全部寫完才執行 → 違反 TDD 精神

# ✅ 應該這樣做
# 1. 寫 test_add_positive_numbers → RED
# 2. 實作 → GREEN
# 3. REFACTOR
# 4. 寫下一個測試
```

#### 3. 過度設計

```python
# ❌ 不要一開始就寫抽象工廠模式
class AdderFactory:
    @staticmethod
    def create_adder():
        return NumberAdder()

class NumberAdder:
    def add(self, a, b):
        return a + b

# ✅ 直接寫簡單的函式
def add(a, b):
    return a + b
```

## 測試撰寫技巧

### 測試名稱應該描述意圖

```python
# ❌ 模糊的名稱
def test_add():
    ...

# ✅ 清楚的名稱
def test_add_two_positive_numbers_returns_sum():
    assert add(2, 3) == 5

def test_add_negative_and_positive_returns_difference():
    assert add(-1, 1) == 0
```

### Arrange-Act-Assert 模式

```python
def test_withdraw_from_account():
    # Arrange - 準備測試資料
    account = Account(balance=1000)
    
    # Act - 執行被測試的操作
    account.withdraw(200)
    
    # Assert - 驗證結果
    assert account.balance == 800
```

### 測試邊界條件

```python
def test_divide():
    # 正常情況
    assert divide(10, 2) == 5
    
    # 邊界條件
    assert divide(10, 1) == 10
    assert divide(10, 10) == 1
    
    # 異常情況
    with pytest.raises(ValueError):
        divide(10, 0)
```

## 範例工作流程

### 實作一個簡單的 Stack

```python
# Step 1: 寫第一個測試
def test_stack_creation():
    stack = Stack()
    assert stack.is_empty()

# RED → 執行測試

# Step 2: 實作
class Stack:
    def is_empty(self):
        return True

# GREEN → 測試通過

# Step 3: 重構（暫時不需要）

# Step 4: 下一個測試
def test_push_one_item():
    stack = Stack()
    stack.push(42)
    assert not stack.is_empty()

# RED → 修改實作
class Stack:
    def __init__(self):
        self.items = []
    
    def push(self, item):
        self.items.append(item)
    
    def is_empty(self):
        return len(self.items) == 0

# GREEN → 測試通過

# Step 5: 繼續添加測試和實作
def test_pop_item():
    stack = Stack()
    stack.push(42)
    assert stack.pop() == 42

# RED → 實作 pop 方法 → GREEN → REFACTOR
```

## 測試覆蓋率目標

### 建議的覆蓋率

- **語句覆蓋率:** ≥ 90%
- **分支覆蓋率:** ≥ 80%
- **臨界值覆蓋率:** 100%

### 使用 pytest-cov

```bash
# 執行測試並計算覆蓋率
pytest --cov=myapp tests/

# 產生 HTML 報告
pytest --cov=myapp --cov-report=html tests/

# 設定最低覆蓋率要求
pytest --cov=myapp --cov-fail-under=90 tests/
```

### .coveragerc 設定

```ini
[run]
source = myapp
omit = 
    */tests/*
    */__main__.py
    */setup.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
```

## 常見問題

### Q: 測試應該多詳細？

**A:** 測試應該覆蓋：
- 正常路徑（happy path）
- 邊界條件
- 錯誤處理
- 常見的用戶錯誤

### Q: 如何測試私有方法？

**A:** 透過公開 API 間接測試：

```python
# ❌ 不要直接測試 private method
def test_private_helper():
    obj._private_helper()

# ✅ 透過 public method 測試
def test_public_method_uses_helper():
    result = obj.public_method()
    assert result == expected
```

### Q: 測試失敗了怎麼辦？

**A:** 
1. 確認測試是正確的
2. 找出程式碼的問題
3. 修復程式碼
4. 確保測試通過
5. **不要刪除或修改測試來迎合錯誤的程式碼**

## 與其他技能的整合

### Brainstorming → TDD

Brainstorming 確定了功能需求，TDD 將需求轉化為具體的測試案例。

### Writing Plans → TDD

每個任務的 done condition 應該包含測試要求，例如：
- [ ] 實作 user registration API
- [ ] 測試覆蓋率達到 90%

### Subagent-Driven → TDD

執行計劃時，對每個任務應用 TDD 流程。

### Systematic Debugging → TDD

當測試失敗時，使用 systematic debugging 找出原因。

## 下一步

開始實踐 TDD：

1. **選擇一個小功能**開始練習
2. **嚴格遵守** RED-GREEN-REFACTOR 循環
3. **逐步建立**完整的測試套件
4. **持續改進**測試品質

---

**版本:** 1.0  
**最後更新:** 2026-04-02  
**相關技能:** brainstorming, writing-plans, systematic-debugging, subagent-driven
