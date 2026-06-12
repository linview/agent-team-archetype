# 代码异味详解

本文档详细说明各种代码异味及其识别方法和重构建议。

## 1. 重复代码（Duplicated Code）

### 识别方法
- 相同或相似的代码片段出现在多个地方
- 复制粘贴代码后的变体
- 相同逻辑在不同函数中重复

### 重构建议
**Extract Function** - 提取公共函数

```go
// ❌ 重复代码
func ValidateUserEmail(email string) error {
    if email == "" {
        return errors.New("邮箱不能为空")
    }
    if !strings.Contains(email, "@") {
        return errors.New("邮箱格式无效")
    }
    return nil
}

func ValidateAdminEmail(email string) error {
    if email == "" {
        return errors.New("邮箱不能为空")
    }
    if !strings.Contains(email, "@") {
        return errors.New("邮箱格式无效")
    }
    // 额外的验证...
    return nil
}

// ✓ 重构后：提取公共函数
func validateEmailFormat(email string) error {
    if email == "" {
        return errors.New("邮箱不能为空")
    }
    if !strings.Contains(email, "@") {
        return errors.New("邮箱格式无效")
    }
    return nil
}

func ValidateUserEmail(email string) error {
    return validateEmailFormat(email)
}

func ValidateAdminEmail(email string) error {
    if err := validateEmailFormat(email); err != nil {
        return err
    }
    // 额外的验证...
    return nil
}
```

## 2. 函数过长（Long Method）

### 识别方法
- 函数超过 20-30 行
- 函数包含多个层次的抽象
- 函数名称难以准确描述其所有行为

### 重构建议
**Extract Function** - 提取小函数

```go
// ❌ 函数过长
func RegisterUser(email, password string) (*User, error) {
    // 验证邮箱
    if email == "" {
        return nil, errors.New("邮箱不能为空")
    }
    if !strings.Contains(email, "@") {
        return nil, errors.New("邮箱格式无效")
    }

    // 验证密码
    if len(password) < 8 {
        return nil, errors.New("密码过短")
    }
    hasLetter := false
    hasDigit := false
    for _, c := range password {
        if unicode.IsLetter(c) {
            hasLetter = true
        }
        if unicode.IsDigit(c) {
            hasDigit = true
        }
    }
    if !hasLetter || !hasDigit {
        return nil, errors.New("密码必须包含字母和数字")
    }

    // 检查邮箱是否已存在
    // ... 更多逻辑

    // 创建用户
    // ... 更多逻辑

    return user, nil
}

// ✓ 重构后：提取小函数
func RegisterUser(email, password string) (*User, error) {
    if err := validateEmail(email); err != nil {
        return nil, err
    }

    if err := validatePassword(password); err != nil {
        return nil, err
    }

    if err := checkEmailUniqueness(email); err != nil {
        return nil, err
    }

    return createUser(email, password)
}

func validateEmail(email string) error {
    if email == "" {
        return errors.New("邮箱不能为空")
    }
    if !strings.Contains(email, "@") {
        return errors.New("邮箱格式无效")
    }
    return nil
}

func validatePassword(password string) error {
    if len(password) < 8 {
        return errors.New("密码过短")
    }

    hasLetter := regexp.MustCompile(`[a-zA-Z]`).MatchString(password)
    hasDigit := regexp.MustCompile(`[0-9]`).MatchString(password)

    if !hasLetter || !hasDigit {
        return errors.New("密码必须包含字母和数字")
    }
    return nil
}
```

## 3. 魔法数字/字符串（Magic Numbers）

### 识别方法
- 代码中直接出现未命名的数字或字符串
- 相同的数字在多处出现
- 数字含义不明确

### 重构建议
**使用命名常量**

```go
// ❌ 魔法数字
func ValidatePassword(password string) error {
    if len(password) < 8 {
        return errors.New("密码过短")
    }
    if len(password) > 128 {
        return errors.New("密码过长")
    }
    return nil
}

// ✓ 重构后：使用命名常量
const (
    MinPasswordLength = 8
    MaxPasswordLength = 128
)

func ValidatePassword(password string) error {
    if len(password) < MinPasswordLength {
        return fmt.Errorf("密码至少需要 %d 个字符", MinPasswordLength)
    }
    if len(password) > MaxPasswordLength {
        return fmt.Errorf("密码最多 %d 个字符", MaxPasswordLength)
    }
    return nil
}
```

## 4. 过多的参数（Long Parameter List）

### 识别方法
- 函数参数超过 3-4 个
- 多个参数经常一起出现
- 参数列表难以记忆

### 重构建议
**引入参数对象（Introduce Parameter Object）**

```go
// ❌ 参数过多
func CreateUser(email, password, firstName, lastName, phone, address, city, country, zipCode string) (*User, error) {
    // ...
}

// ✓ 重构后：使用结构体
type UserRegistration struct {
    Email     string
    Password  string
    FirstName string
    LastName  string
    Phone     string
    Address   string
    City      string
    Country   string
    ZipCode   string
}

func CreateUser(reg UserRegistration) (*User, error) {
    // ...
}
```

## 5. 深层嵌套（Deep Nesting）

### 识别方法
- 代码嵌套层次超过 3 层
- 大量的 if-else 嵌套
- 难以识别正常流程

### 重构建议
**卫语句（Guard Clauses）**

```go
// ❌ 深层嵌套
func ProcessUser(user *User) error {
    if user != nil {
        if user.Email != "" {
            if isValidEmail(user.Email) {
                if !emailExists(user.Email) {
                    // 实际逻辑
                    return save(user)
                } else {
                    return errors.New("邮箱已存在")
                }
            } else {
                return errors.New("邮箱无效")
            }
        } else {
            return errors.New("邮箱为空")
        }
    } else {
        return errors.New("用户为 nil")
    }
}

// ✓ 重构后：早返回（Guard Clauses）
func ProcessUser(user *User) error {
    if user == nil {
        return errors.New("用户为 nil")
    }

    if user.Email == "" {
        return errors.New("邮箱为空")
    }

    if !isValidEmail(user.Email) {
        return errors.New("邮箱无效")
    }

    if emailExists(user.Email) {
        return errors.New("邮箱已存在")
    }

    return save(user)
}
```

## 6. 过大的类（Large Class）

### 识别方法
- 类/结构体包含过多字段
- 类承担过多职责
- 难以理解和维护

### 重构建议
**拆分类（Extract Class）**

## 7. 特性依恋（Feature Envy）

### 识别方法
- 函数频繁访问另一个对象的内部数据
- 函数对其他对象的数据比对自己的数据更感兴趣

### 重构建议
**Move Function** - 将函数移到它感兴趣的数据所在的类中

## 8. 数据泥团（Data Clumps）

### 识别方法
- 多个参数总是一起出现
- 多个字段总是一起使用

### 重构建议
**提取值对象（Extract Value Object）**

```go
// ❌ 数据泥团
func CalculateTotal(startDay, startMonth, startYear int, endDay, endMonth, endYear int) float64 {
    // ...
}

// ✓ 重构后：提取值对象
type Date struct {
    Day   int
    Month int
    Year  int
}

func CalculateTotal(startDate, endDate Date) float64 {
    // ...
}
```

## 9. 基本类型偏执（Primitive Obsession）

### 识别方法
- 过度使用基本类型（字符串、数字）
- 缺少领域特定的类型

### 重构建议
**引入类型（Introduce Type）**

```go
// ❌ 基本类型偏执
func SendEmail(to, subject, body string) error {
    // ...
}

// ✓ 重构后：引入类型
type Email struct {
    address string
}

type EmailSubject struct {
    text string
}

type EmailBody struct {
    content string
}

func SendEmail(to Email, subject EmailSubject, body EmailBody) error {
    // ...
}
```

## 10. 过多的注释（Comments）

### 识别方法
- 大量注释解释代码在做什么
- 注释比代码还多
- 注释成为理解代码的唯一方式

### 重构建议
**重构代码使其自解释**

```go
// ❌ 过多的注释
// 检查用户是否有足够的余额
if user.Balance >= order.Total {
    // 如果余额足够，扣除金额
    user.Balance -= order.Total
    // 返回成功
    return true
} else {
    // 如果余额不足，返回失败
    return false
}

// ✓ 重构后：代码自解释
if user.hasSufficientBalanceFor(order) {
    user.deduct(order.Total)
    return true
}
return false
```

## 参考资料

- 《重构：改善既有代码的设计》- Martin Fowler
- 《代码整洁之道》- Robert C. Martin
