# 重构示例集

本文档提供完整的重构示例，展示真实场景下的重构过程。

## 示例 1：用户注册函数重构

### 场景
一个用户注册函数承担了太多职责：验证邮箱、验证密码、检查唯一性、创建用户。

### 重构前

```go
func RegisterUser(email, password string) (*User, error) {
    // 验证邮箱
    if email == "" {
        return nil, errors.New("邮箱不能为空")
    }
    if !strings.Contains(email, "@") {
        return nil, errors.New("邮箱格式无效")
    }
    if !strings.Contains(email, ".") {
        return nil, errors.New("邮箱格式无效")
    }

    // 验证密码
    if len(password) < 8 {
        return nil, errors.New("密码过短")
    }
    if len(password) > 128 {
        return nil, errors.New("密码过长")
    }

    hasLetter := false
    hasDigit := false
    hasSpecial := false
    for _, c := range password {
        if unicode.IsLetter(c) {
            hasLetter = true
        }
        if unicode.IsDigit(c) {
            hasDigit = true
        }
        if unicode.IsPunct(c) || unicode.IsSymbol(c) {
            hasSpecial = true
        }
    }
    if !hasLetter || !hasDigit || !hasSpecial {
        return nil, errors.New("密码必须包含字母、数字和特殊字符")
    }

    // 检查邮箱是否已存在
    existingUser, err := db.FindUserByEmail(email)
    if err != nil {
        return nil, fmt.Errorf("数据库错误: %w", err)
    }
    if existingUser != nil {
        return nil, errors.New("邮箱已被注册")
    }

    // 创建用户
    hashedPassword, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
    if err != nil {
        return nil, fmt.Errorf("密码加密失败: %w", err)
    }

    user := &User{
        ID:       generateID(),
        Email:    email,
        Password: string(hashedPassword),
        CreatedAt: time.Now(),
        UpdatedAt: time.Now(),
    }

    if err := db.SaveUser(user); err != nil {
        return nil, fmt.Errorf("保存用户失败: %w", err)
    }

    return user, nil
}
```

### 重构后

```go
func RegisterUser(email, password string) (*User, error) {
    if err := validateEmail(email); err != nil {
        return nil, err
    }

    if err := validatePassword(password); err != nil {
        return nil, err
    }

    if err := checkEmailAvailability(email); err != nil {
        return nil, err
    }

    return createUser(email, password)
}

// validateEmail 验证邮箱格式
func validateEmail(email string) error {
    if email == "" {
        return errors.New("邮箱不能为空")
    }

    emailRegex := regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
    if !emailRegex.MatchString(email) {
        return errors.New("邮箱格式无效")
    }

    return nil
}

// validatePassword 验证密码强度
func validatePassword(password string) error {
    const (
        MinPasswordLength = 8
        MaxPasswordLength = 128
    )

    if len(password) < MinPasswordLength {
        return fmt.Errorf("密码至少需要 %d 个字符", MinPasswordLength)
    }

    if len(password) > MaxPasswordLength {
        return fmt.Errorf("密码最多 %d 个字符", MaxPasswordLength)
    }

    hasLetter := regexp.MustCompile(`[a-zA-Z]`).MatchString(password)
    hasDigit := regexp.MustCompile(`[0-9]`).MatchString(password)
    hasSpecial := regexp.MustCompile(`[!@#$%^&*(),.?":{}|<>]`).MatchString(password)

    if !hasLetter || !hasDigit || !hasSpecial {
        return errors.New("密码必须包含字母、数字和特殊字符")
    }

    return nil
}

// checkEmailAvailability 检查邮箱是否可用
func checkEmailAvailability(email string) error {
    existingUser, err := db.FindUserByEmail(email)
    if err != nil {
        return fmt.Errorf("数据库错误: %w", err)
    }

    if existingUser != nil {
        return errors.New("邮箱已被注册")
    }

    return nil
}

// createUser 创建新用户
func createUser(email, password string) (*User, error) {
    hashedPassword, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
    if err != nil {
        return nil, fmt.Errorf("密码加密失败: %w", err)
    }

    user := &User{
        ID:        generateID(),
        Email:     email,
        Password:  string(hashedPassword),
        CreatedAt: time.Now(),
        UpdatedAt: time.Now(),
    }

    if err := db.SaveUser(user); err != nil {
        return nil, fmt.Errorf("保存用户失败: %w", err)
    }

    return user, nil
}
```

### 改进点
- ✅ 每个函数职责单一
- ✅ 函数名清晰表达意图
- ✅ 提高了可测试性
- ✅ 便于复用和维护

## 示例 2：订单处理函数重构

### 场景
订单处理函数包含深层嵌套和重复逻辑。

### 重构前

```go
func ProcessOrder(order *Order) (*OrderResult, error) {
    result := &OrderResult{}

    if order != nil {
        if order.Customer != nil {
            if order.Customer.IsActive {
                if len(order.Items) > 0 {
                    total := 0.0
                    for _, item := range order.Items {
                        if item.Price > 0 && item.Quantity > 0 {
                            total += item.Price * float64(item.Quantity)
                        } else {
                            result.Status = "invalid_item"
                            return result, errors.New("商品价格或数量无效")
                        }
                    }

                    if total > 0 {
                        if total < 10000 {
                            if order.Customer.CreditLimit >= total {
                                order.Total = total
                                order.Status = "approved"
                                if err := db.Save(order); err != nil {
                                    result.Status = "db_error"
                                    return result, err
                                }
                                result.Status = "success"
                                result.OrderID = order.ID
                                result.Total = total
                            } else {
                                result.Status = "insufficient_credit"
                                return result, errors.New("信用额度不足")
                            }
                        } else {
                            result.Status = "amount_too_large"
                            return result, errors.New("订单金额过大")
                        }
                    } else {
                        result.Status = "invalid_amount"
                        return result, errors.New("订单金额无效")
                    }
                } else {
                    result.Status = "empty_order"
                    return result, errors.New("订单为空")
                }
            } else {
                result.Status = "inactive_customer"
                return result, errors.New("客户未激活")
            }
        } else {
            result.Status = "missing_customer"
            return result, errors.New("缺少客户信息")
        }
    } else {
        result.Status = "nil_order"
        return result, errors.New("订单为空")
    }
}
```

### 重构后

```go
func ProcessOrder(order *Order) (*OrderResult, error) {
    if err := validateOrder(order); err != nil {
        return &OrderResult{Status: getErrorStatus(err)}, err
    }

    total := calculateOrderTotal(order)

    if err := validateOrderAmount(total); err != nil {
        return &OrderResult{Status: getErrorStatus(err)}, err
    }

    if err := checkCreditLimit(order.Customer, total); err != nil {
        return &OrderResult{Status: getErrorStatus(err)}, err
    }

    return finalizeOrder(order, total)
}

// validateOrder 验证订单基本信息
func validateOrder(order *Order) error {
    if order == nil {
        return errors.New("订单为空")
    }

    if order.Customer == nil {
        return errors.New("缺少客户信息")
    }

    if !order.Customer.IsActive {
        return errors.New("客户未激活")
    }

    if len(order.Items) == 0 {
        return errors.New("订单为空")
    }

    return validateOrderItems(order.Items)
}

// validateOrderItems 验证订单商品
func validateOrderItems(items []OrderItem) error {
    for _, item := range items {
        if item.Price <= 0 {
            return errors.New("商品价格无效")
        }
        if item.Quantity <= 0 {
            return errors.New("商品数量无效")
        }
    }
    return nil
}

// calculateOrderTotal 计算订单总额
func calculateOrderTotal(order *Order) float64 {
    total := 0.0
    for _, item := range order.Items {
        total += item.Price * float64(item.Quantity)
    }
    return total
}

// validateOrderAmount 验证订单金额
func validateOrderAmount(total float64) error {
    if total <= 0 {
        return errors.New("订单金额无效")
    }

    const MaxOrderAmount = 10000
    if total > MaxOrderAmount {
        return errors.New("订单金额过大")
    }

    return nil
}

// checkCreditLimit 检查信用额度
func checkCreditLimit(customer *Customer, amount float64) error {
    if customer.CreditLimit < amount {
        return errors.New("信用额度不足")
    }
    return nil
}

// finalizeOrder 完成订单
func finalizeOrder(order *Order, total float64) (*OrderResult, error) {
    order.Total = total
    order.Status = "approved"

    if err := db.Save(order); err != nil {
        return &OrderResult{Status: "db_error"}, err
    }

    return &OrderResult{
        Status:  "success",
        OrderID: order.ID,
        Total:   total,
    }, nil
}

// getErrorStatus 根据错误返回状态码
func getErrorStatus(err error) string {
    errorStatusMap := map[string]string{
        "订单为空":              "nil_order",
        "缺少客户信息":            "missing_customer",
        "客户未激活":             "inactive_customer",
        "订单为空":              "empty_order",
        "商品价格无效":            "invalid_item",
        "商品数量无效":            "invalid_item",
        "订单金额无效":            "invalid_amount",
        "订单金额过大":            "amount_too_large",
        "信用额度不足":            "insufficient_credit",
    }

    msg := err.Error()
    if status, ok := errorStatusMap[msg]; ok {
        return status
    }
    return "unknown_error"
}
```

### 改进点
- ✅ 使用卫语句消除深层嵌套
- ✅ 每个函数职责单一
- ✅ 提高了可读性和可测试性
- ✅ 错误处理更加清晰

## 示例 3：价格计算函数重构

### 场景
价格计算逻辑复杂，包含多个条件和不明确的表达式。

### 重构前

```go
func CalculatePrice(order *Order) float64 {
    price := order.Quantity * order.ItemPrice

    if order.Quantity >= 100 {
        price = price * 0.9
    } else if order.Quantity >= 50 {
        price = price * 0.95
    } else if order.Quantity >= 10 {
        price = price * 0.98
    }

    if order.Customer.IsVIP {
        price = price * 0.85
    } else if order.Customer.IsMember {
        price = price * 0.9
    }

    if order.ShippingMethod == "express" {
        price = price + 20
    } else if order.ShippingMethod == "standard" {
        price = price + 10
    } else {
        price = price + 5
    }

    if price > 1000 {
        price = price - 20
    }

    return price
}
```

### 重构后

```go
func CalculatePrice(order *Order) float64 {
    basePrice := calculateBasePrice(order)
    discountedPrice := applyDiscounts(order, basePrice)
    finalPrice := addShipping(order, discountedPrice)
    return applyBulkDiscount(finalPrice)
}

// calculateBasePrice 计算基础价格
func calculateBasePrice(order *Order) float64 {
    return order.Quantity * order.ItemPrice
}

// applyDiscounts 应用折扣
func applyDiscounts(order *Order, price float64) float64 {
    price = applyQuantityDiscount(order.Quantity, price)
    price = applyCustomerDiscount(order.Customer, price)
    return price
}

// applyQuantityDiscount 应用数量折扣
func applyQuantityDiscount(quantity int, price float64) float64 {
    discountRates := map[int]float64{
        10:  0.98,  // 10+ 件：2% 折扣
        50:  0.95,  // 50+ 件：5% 折扣
        100: 0.90,  // 100+ 件：10% 折扣
    }

    applicableRate := 1.0
    for threshold, rate := range discountRates {
        if quantity >= threshold && rate < applicableRate {
            applicableRate = rate
        }
    }

    return price * applicableRate
}

// applyCustomerDiscount 应用客户折扣
func applyCustomerDiscount(customer *Customer, price float64) float64 {
    var discountRate float64

    switch {
    case customer.IsVIP:
        discountRate = 0.85  // VIP：15% 折扣
    case customer.IsMember:
        discountRate = 0.90  // 会员：10% 折扣
    default:
        discountRate = 1.00  // 无折扣
    }

    return price * discountRate
}

// addShipping 添加运费
func addShipping(order *Order, price float64) float64 {
    shippingCosts := map[string]float64{
        "express":  20.0,
        "standard": 10.0,
        "economy":  5.0,
    }

    shipping, ok := shippingCosts[order.ShippingMethod]
    if !ok {
        shipping = 5.0  // 默认运费
    }

    return price + shipping
}

// applyBulkDiscount 应用大额订单折扣
func applyBulkDiscount(price float64) float64 {
    const (
        BulkThreshold   = 1000
        BulkDiscount    = 20
    )

    if price > BulkThreshold {
        return price - BulkDiscount
    }
    return price
}
```

### 改进点
- ✅ 使用命名常量替代魔法数字
- ✅ 提取变量使逻辑更清晰
- ✅ 每个步骤独立且易于理解
- ✅ 便于单独测试每个步骤
- ✅ 易于扩展新的折扣规则

## 示例 4：重复代码消除

### 场景
多个函数中存在重复的验证逻辑。

### 重构前

```go
func CreateUser(name, email, phone string) (*User, error) {
    if name == "" {
        return nil, errors.New("姓名不能为空")
    }
    if len(name) > 50 {
        return nil, errors.New("姓名过长")
    }
    if email == "" {
        return nil, errors.New("邮箱不能为空")
    }
    if !strings.Contains(email, "@") {
        return nil, errors.New("邮箱格式无效")
    }
    if phone == "" {
        return nil, errors.New("电话不能为空")
    }
    if len(phone) < 10 {
        return nil, errors.New("电话号码过短")
    }

    user := &User{
        Name:  name,
        Email: email,
        Phone: phone,
    }
    db.Save(user)
    return user, nil
}

func UpdateUser(user *User, name, email, phone string) error {
    if name == "" {
        return errors.New("姓名不能为空")
    }
    if len(name) > 50 {
        return errors.New("姓名过长")
    }
    if email == "" {
        return errors.New("邮箱不能为空")
    }
    if !strings.Contains(email, "@") {
        return errors.New("邮箱格式无效")
    }
    if phone == "" {
        return errors.New("电话不能为空")
    }
    if len(phone) < 10 {
        return errors.New("电话号码过短")
    }

    user.Name = name
    user.Email = email
    user.Phone = phone
    return db.Save(user)
}
```

### 重构后

```go
func CreateUser(name, email, phone string) (*User, error) {
    if err := validateUserData(name, email, phone); err != nil {
        return nil, err
    }

    user := &User{
        Name:  name,
        Email: email,
        Phone: phone,
    }
    db.Save(user)
    return user, nil
}

func UpdateUser(user *User, name, email, phone string) error {
    if err := validateUserData(name, email, phone); err != nil {
        return err
    }

    user.Name = name
    user.Email = email
    user.Phone = phone
    return db.Save(user)
}

// validateUserData 验证用户数据
func validateUserData(name, email, phone string) error {
    if err := validateName(name); err != nil {
        return err
    }

    if err := validateEmail(email); err != nil {
        return err
    }

    if err := validatePhone(phone); err != nil {
        return err
    }

    return nil
}

// validateName 验证姓名
func validateName(name string) error {
    if name == "" {
        return errors.New("姓名不能为空")
    }
    const MaxNameLength = 50
    if len(name) > MaxNameLength {
        return errors.New("姓名过长")
    }
    return nil
}

// validateEmail 验证邮箱
func validateEmail(email string) error {
    if email == "" {
        return errors.New("邮箱不能为空")
    }
    if !strings.Contains(email, "@") {
        return errors.New("邮箱格式无效")
    }
    return nil
}

// validatePhone 验证电话
func validatePhone(phone string) error {
    if phone == "" {
        return errors.New("电话不能为空")
    }
    const MinPhoneLength = 10
    if len(phone) < MinPhoneLength {
        return errors.New("电话号码过短")
    }
    return nil
}
```

### 改进点
- ✅ 消除重复代码
- ✅ 提高代码复用性
- ✅ 验证逻辑集中管理
- ✅ 便于维护和修改

## 参考资料

- 《重构：改善既有代码的设计》- Martin Fowler
- 《代码整洁之道》- Robert C. Martin
