# 重构技术详解

本文档详细说明各种重构技术的步骤、适用场景和注意事项。

## 1. 提取函数（Extract Function）

### 步骤
1. 创建一个新函数，用它表达代码的意图
2. 将原代码复制到新函数中
3. 检查原代码中的变量，看哪些是局部变量，哪些是参数
4. 将局部变量声明移到新函数中
5. 将需要从原函数传入的变量作为参数传递
6. 将原代码替换为新函数调用

### 适用场景
- 函数过长，难以理解
- 代码片段可以被独立命名
- 需要提高代码复用性

### 示例

```go
// 重构前
func PrintOwing(invoice *Invoice) {
    printBanner()

    // 计算未付款金额
    outstanding := 0.0
    for _, order := range invoice.Orders {
        outstanding += order.Amount
    }

    // 打印详情
    fmt.Printf("客户: %s\n", invoice.Customer)
    fmt.Printf("未付金额: %.2f\n", outstanding)
}

// 重构后
func PrintOwing(invoice *Invoice) {
    printBanner()
    outstanding := calculateOutstanding(invoice)
    printDetails(invoice, outstanding)
}

func calculateOutstanding(invoice *Invoice) float64 {
    outstanding := 0.0
    for _, order := range invoice.Orders {
        outstanding += order.Amount
    }
    return outstanding
}

func printDetails(invoice *Invoice, outstanding float64) {
    fmt.Printf("客户: %s\n", invoice.Customer)
    fmt.Printf("未付金额: %.2f\n", outstanding)
}
```

### 注意事项
- 新函数名应该准确表达其功能
- 如果新函数和原函数在同一个类中，考虑是否应该保持私有
- 确保新函数是纯粹的，不产生副作用

## 2. 内联函数（Inline Function）

### 步骤
1. 检查函数，确保它不是多态的
2. 找到函数的所有调用点
3. 将函数体替换到每个调用点
4. 删除函数定义

### 适用场景
- 函数体和函数名一样清晰
- 函数只是简单委托，没有增加价值
- 需要减少不必要的间接层

### 示例

```go
// 重构前
func getRating(driver *Driver) int {
    return moreThanFiveLateDeliveries(driver) ? 2 : 1
}

func moreThanFiveLateDeliveries(driver *Driver) bool {
    return driver.NumberOfLateDeliveries > 5
}

// 重构后（函数名没有增加额外价值）
func getRating(driver *Driver) int {
    return driver.NumberOfLateDeliveries > 5 ? 2 : 1
}
```

### 注意事项
- 不要内联复杂的函数
- 如果函数被多处调用，内联会导致重复代码
- 考虑函数是否真的没有价值

## 3. 提取变量（Extract Variable）

### 步骤
1. 找到难以理解的表达式
2. 声明一个新变量，给它一个有意义的名字
3. 将表达式的结果赋值给新变量
4. 用新变量替换原表达式

### 适用场景
- 表达式过于复杂
- 需要解释表达式的含义
- 需要在多处使用相同的表达式

### 示例

```go
// 重构前
func Price(order *Order) float64 {
    return order.Quantity*order.ItemPrice -
        max(0, order.Quantity-500)*order.ItemPrice*0.05 +
        min(order.Quantity*order.ItemPrice*0.1, 100)
}

// 重构后
func Price(order *Order) float64 {
    basePrice := order.Quantity * order.ItemPrice
    quantityDiscount := max(0, order.Quantity-500) * order.ItemPrice * 0.05
    shipping := min(basePrice*0.1, 100)
    return basePrice - quantityDiscount + shipping
}
```

### 注意事项
- 变量名应该准确表达其含义
- 避免过度提取简单表达式
- 考虑表达式是否应该成为函数

## 4. 重命名（Rename Variable/Function）

### 步骤
1. 找到需要重命名的变量或函数
2. 检查所有使用它的地方
3. 在一处修改名字
4. 运行测试确保没有破坏功能
5. 重复直到所有地方都更新

### 适用场景
- 命名不能准确表达意图
- 命名过于简短或模糊
- 需要提高代码可读性

### 示例

```go
// 重构前
func calc(u *User) float64 {
    var t float64
    for _, o := range u.Orders {
        t += o.Amount
    }
    return t
}

// 重构后
func calculateTotalOrderAmount(user *User) float64 {
    totalAmount := 0.0
    for _, order := range user.Orders {
        totalAmount += order.Amount
    }
    return totalAmount
}
```

### 注意事项
- 使用有意义的名称
- 遵循语言命名约定
- 考虑使用领域术语

## 5. 引入参数对象（Introduce Parameter Object）

### 步骤
1. 创建一个新的数据结构/类
2. 将经常一起出现的参数作为字段
3. 在所有使用这些参数的地方使用新结构
4. 编译并测试

### 适用场景
- 多个参数总是一起出现
- 参数过多导致函数难以使用
- 可以发现新的抽象

### 示例

```go
// 重构前
func CreateInvoice(customerName, customerEmail, customerPhone string,
                   amount float64, dueDate time.Time) *Invoice {
    // ...
}

// 重构后
type Customer struct {
    Name  string
    Email string
    Phone string
}

func CreateInvoice(customer Customer, amount float64, dueDate time.Time) *Invoice {
    // ...
}
```

### 注意事项
- 新结构应该有明确的含义
- 考虑是否应该放在单独的文件中
- 可能会发现新的行为应该移到新结构中

## 6. 卫语句（Guard Clauses）

### 步骤
1. 找到嵌套的条件判断
2. 将每个条件翻转并提前返回
3. 将正常流程放在最后

### 适用场景
- 深层嵌套的条件
- 多个边界条件检查
- 需要突出正常流程

### 示例

```go
// 重构前：嵌套条件
func GetPayAmount(employee *Employee) float64 {
    var result float64
    if employee.IsSeparated {
        result = 0
    } else {
        if employee.IsRetired {
            result = 0
        } else {
            result = employee.Salary
        }
    }
    return result
}

// 重构后：卫语句
func GetPayAmount(employee *Employee) float64 {
    if employee.IsSeparated {
        return 0
    }
    if employee.IsRetired {
        return 0
    }
    return employee.Salary
}
```

### 注意事项
- 确保每个卫语句都有明确的返回值
- 保持代码的对称性
- 避免过度使用导致函数有多个出口点

## 7. 函数组合（Compose Method）

### 步骤
1. 将大函数分解为多个小函数
2. 每个小函数做一件事
3. 在主函数中按逻辑顺序调用这些小函数

### 适用场景
- 函数过长且复杂
- 函数包含多个抽象层次
- 需要提高可读性

### 示例

```go
// 重构前
func ProcessOrder(order *Order) error {
    // 验证
    if order.Customer == nil {
        return errors.New("客户不能为空")
    }
    if len(order.Items) == 0 {
        return errors.New("订单不能为空")
    }

    // 计算金额
    total := 0.0
    for _, item := range order.Items {
        total += item.Price * float64(item.Quantity)
    }

    // 保存
    order.Total = total
    order.Status = "processed"
    return db.Save(order)
}

// 重构后
func ProcessOrder(order *Order) error {
    if err := validateOrder(order); err != nil {
        return err
    }

    total := calculateOrderTotal(order)
    applyTotalToOrder(order, total)

    return saveOrder(order)
}

func validateOrder(order *Order) error {
    if order.Customer == nil {
        return errors.New("客户不能为空")
    }
    if len(order.Items) == 0 {
        return errors.New("订单不能为空")
    }
    return nil
}

func calculateOrderTotal(order *Order) float64 {
    total := 0.0
    for _, item := range order.Items {
        total += item.Price * float64(item.Quantity)
    }
    return total
}

func applyTotalToOrder(order *Order, total float64) {
    order.Total = total
    order.Status = "processed"
}

func saveOrder(order *Order) error {
    return db.Save(order)
}
```

### 注意事项
- 每个小函数应该有清晰的职责
- 函数名应该形成一个可读的叙述
- 避免过度分解导致函数调用链过长

## 8. 替换算法（Substitute Algorithm）

### 步骤
1. 准备新的算法实现
2. 在新函数中实现新算法
3. 运行测试确保新算法正确
4. 替换旧算法的调用点

### 适用场景
- 发现更清晰的算法
- 需要优化性能
- 旧算法难以理解

### 示例

```go
// 重构前：低效的查找
func findUser(users []User, id string) *User {
    for _, user := range users {
        if user.ID == id {
            return &user
        }
    }
    return nil
}

// 重构后：使用 map
func findUser(userMap map[string]*User, id string) *User {
    return userMap[id]
}
```

### 注意事项
- 确保新算法的边界条件正确
- 比较新旧算法的性能
- 考虑是否需要保留旧算法作为参考

## 9. 提取接口（Extract Interface）

### 步骤
1. 创建新的接口
2. 将共同方法声明添加到接口中
3. 让相关类实现接口
4. 更新使用这些类的代码，使用接口类型

### 适用场景
- 多个类有相同的方法
- 需要降低耦合
- 需要提高可测试性

### 示例

```go
// 重构前
func ProcessPayment(creditCard *CreditCard, amount float64) error {
    return creditCard.Charge(amount)
}

// 重构后
type PaymentProcessor interface {
    Charge(amount float64) error
}

type CreditCard struct { ... }
func (c *CreditCard) Charge(amount float64) error { ... }

type PayPal struct { ... }
func (p *PayPal) Charge(amount float64) error { ... }

func ProcessPayment(processor PaymentProcessor, amount float64) error {
    return processor.Charge(amount)
}
```

### 注意事项
- 接口应该小而专注
- 接口命名应该清晰表达意图
- 避免过度使用接口

## 参考资料

- 《重构：改善既有代码的设计》- Martin Fowler
- 《重构与模式》- Joshua Kerievsky
