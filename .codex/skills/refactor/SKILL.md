---
name: refactor
description: |
  安全重构代码技能。当用户明确提到"重构"、"代码异味"或需要在TDD循环的Refactor阶段改进代码内部结构时使用。

  **仅在以下场景触发**：
  - 用户明确说"重构这段代码"
  - 提到"代码异味"并要求改进
  - TDD循环中的Refactor阶段
  - 代码审查中需要改进内部结构但不改变功能

  **注意**：如果用户只是说"优化"、"改进"或"提升性能"，不应该触发此技能，除非明确提到"重构"。
---

# 安全重构

## 核心原则

**重构不改变外部行为，只改进内部结构。测试必须始终通过。**

重构是改善既有代码设计的过程，通过一系列小的、保持行为的变换来提高代码质量。每个变换都称为一个"重构"。

## 何时重构

### 在 TDD 循环中
- 每个 Red-Green 循环后都应检查是否需要重构
- 不要等到代码"完全烂掉"才重构
- 小步重构，频繁重构

### 重构信号（Code Smells）

**快速识别代码需要重构的信号**：

#### 1. 重复代码
相同的代码片段出现在多个地方 → 提取公共函数

#### 2. 函数过长
函数超过 20-30 行，包含多个抽象层次 → 提取小函数

#### 3. 魔法数字
代码中出现未命名的数字 → 使用命名常量

#### 4. 参数过多
函数参数超过 3-4 个 → 引入参数对象

#### 5. 深层嵌套
条件嵌套超过 3 层 → 使用卫语句（Guard Clauses）

**💡 详细说明**：参见 [references/code-smells.md](references/code-smells.md)

## 重构技术速查

### 1. 提取函数（Extract Function）

**何时使用**：函数过长，代码片段可以被独立命名

```go
// 重构前
func PrintOwing(invoice *Invoice) {
    printBanner()
    outstanding := 0.0
    for _, order := range invoice.Orders {
        outstanding += order.Amount
    }
    fmt.Printf("未付金额: %.2f\n", outstanding)
}

// 重构后
func PrintOwing(invoice *Invoice) {
    printBanner()
    outstanding := calculateOutstanding(invoice)
    fmt.Printf("未付金额: %.2f\n", outstanding)
}
```

### 2. 内联函数（Inline Function）

**何时使用**：函数体和函数名一样清晰

```go
// 重构前
func getRating(driver *Driver) int {
    return moreThanFiveLateDeliveries(driver) ? 2 : 1
}

// 重构后
func getRating(driver *Driver) int {
    return driver.NumberOfLateDeliveries > 5 ? 2 : 1
}
```

### 3. 提取变量（Extract Variable）

**何时使用**：表达式难以理解

```go
// 重构前
func Price(order *Order) float64 {
    return order.Quantity*order.ItemPrice -
        max(0, order.Quantity-500)*order.ItemPrice*0.05
}

// 重构后
func Price(order *Order) float64 {
    basePrice := order.Quantity * order.ItemPrice
    quantityDiscount := max(0, order.Quantity-500) * order.ItemPrice * 0.05
    return basePrice - quantityDiscount
}
```

### 4. 重命名（Rename）

**何时使用**：命名不能准确表达意图

```go
// 重构前
func calc(u *User) float64 { ... }

// 重构后
func calculateTotalOrderAmount(user *User) float64 { ... }
```

### 5. 卫语句（Guard Clauses）

**何时使用**：深层嵌套的条件

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

**💡 详细技术**：参见 [references/techniques.md](references/techniques.md)

## 标准重构流程

### 步骤 1：确保测试通过

```bash
go test ./... -v
```

所有测试必须是绿色的才能开始重构

### 步骤 2：进行小的重构

- 一次只做一个小改动
- 例如：只重命名一个变量，或只提取一个函数

### 步骤 3：运行测试

```bash
go test ./... -v
```

确保重构没有破坏功能

### 步骤 4：提交（可选）

```bash
git add .
git commit -m "refactor: 提取 validateEmail 函数"
```

### 步骤 5：重复步骤 2-4

继续下一个小的重构

## 重构检查清单

每次重构后检查：

- [ ] 所有测试都通过
- [ ] 代码更易读
- [ ] 没有引入新的复杂性
- [ ] 没有改变外部行为
- [ ] 函数/变量命名更清晰
- [ ] 消除了重复代码
- [ ] 降低了耦合度

## 重构原则

### DO（应该做）

✓ **小步重构** - 每次只改一个地方
✓ **频繁测试** - 每次改动后都运行测试
✓ **保持绿灯** - 重构过程中测试必须始终通过
✓ **改善命名** - 好的命名是最好的文档
✓ **消除重复** - DRY (Don't Repeat Yourself)
✓ **简化逻辑** - 能用简单方法就不用复杂方法

### DON'T（不应该做）

✗ **不要同时重构和添加功能** - 一次只做一件事
✗ **不要在红灯时重构** - 测试失败时先让测试通过
✗ **不要大规模重构** - 避免一次改动太多代码
✗ **不要盲目重构** - 确保重构有明确目的
✗ **不要过度设计** - 不要为未来可能不会发生的需求重构

## 输出格式

重构时输出：

```
♻️  重构：[重构内容简述]
   原因：[为什么需要重构]
   技术：[使用的重构技术]

✓ 运行测试
   结果：PASS（X个测试，耗时 Yms）

✓ 重构完成
   改进：[具体改进说明]
```

## 示例输出

```
♻️  重构：提取邮箱验证逻辑
   原因：RegisterUser 和 UpdateUserEmail 中存在重复的验证代码
   技术：Extract Function

   提取前：2 处重复，共 8 行代码
   提取后：1 个函数 validateEmail，被 2 处调用

✓ 运行测试
   命令：go test ./internal/user -v
   结果：PASS
   覆盖率：85.2%

✓ 重构完成
   改进：
   - 消除了 8 行重复代码
   - 提高了可维护性（邮箱验证逻辑集中在一处）
   - 测试覆盖率保持不变
```

## 何时停止重构

满足以下条件即可停止当前重构：

1. ✓ 代码清晰易读，意图明确
2. ✓ 没有明显的代码异味
3. ✓ 函数职责单一，长度适中（< 30 行）
4. ✓ 没有重复代码
5. ✓ 命名准确描述了意图
6. ✓ 所有测试通过

**记住**：重构是持续的过程，不要追求一次性完美。每个 TDD 循环做一点改进即可。

## 更多资源

### 📚 完整示例

真实场景的重构案例：
- [examples.md](examples.md) - 端到端重构示例

### 📖 详细参考

深入理解重构：
- [references/code-smells.md](references/code-smells.md) - 代码异味详解
- [references/techniques.md](references/techniques.md) - 重构技术详解

### 📖 参考资料

- 《重构：改善既有代码的设计》- Martin Fowler
- TDD 循环 (tdd-cycle skill)
- 测试优先 (test-first skill)
- SOLID 原则
