# 文档化设计决策技能

class DocumentationDesignDecisions:
    """
    文档化设计决策技能
    用于记录和管理设计决策，防止类似添加按钮无响应的问题
    """
    
    def __init__(self):
        self.name = "文档化设计决策"
        self.description = "记录和管理设计决策，包括创建设计文档、跟踪决策变更和提供设计指导"
        self.version = "1.0"
    
    def create_design_document(self, component_name, details):
        """
        创建设计文档
        
        Args:
            component_name: 组件名称
            details: 设计详情
            
        Returns:
            str: 设计文档内容
        """
        document = f"""# {component_name} 设计文档

## 1. 概述
{details.get('overview', '组件概述')}

## 2. 功能需求
{details.get('requirements', '功能需求描述')}

## 3. 设计决策

### 3.1 架构设计
{details.get('architecture', '架构设计描述')}

### 3.2 界面设计
{details.get('ui_design', '界面设计描述')}

### 3.3 数据设计
{details.get('data_design', '数据设计描述')}

## 4. 实现细节

### 4.1 核心功能
{details.get('core_features', '核心功能实现')}

### 4.2 关键方法
{details.get('key_methods', '关键方法描述')}

### 4.3 异常处理
{details.get('error_handling', '异常处理策略')}

## 5. 测试计划
{details.get('test_plan', '测试计划描述')}

## 6. 版本历史

| 版本 | 日期 | 变更描述 | 变更人 |
|------|------|----------|--------|
| 1.0  | {details.get('date', '2026-02-10')} | 初始设计 | {details.get('author', '系统')} |
"""
        
        return document
    
    def record_design_decision(self, decision_id, decision_details):
        """
        记录设计决策
        
        Args:
            decision_id: 决策ID
            decision_details: 决策详情
            
        Returns:
            dict: 决策记录
        """
        decision = {
            "id": decision_id,
            "title": decision_details.get("title", "设计决策"),
            "description": decision_details.get("description", ""),
            "rationale": decision_details.get("rationale", ""),
            "alternatives": decision_details.get("alternatives", []),
            "consequences": decision_details.get("consequences", []),
            "status": decision_details.get("status", "已批准"),
            "date": decision_details.get("date", "2026-02-10"),
            "author": decision_details.get("author", "系统")
        }
        
        return decision
    
    def generate_user_operation_design(self, operation_type):
        """
        生成用户操作设计文档
        
        Args:
            operation_type: 操作类型
            
        Returns:
            str: 设计文档内容
        """
        designs = {
            "add": """# 添加操作设计文档

## 1. 概述
添加操作允许用户创建新的记录，包括表单重置、字段显示和数据保存等步骤。

## 2. 功能需求
- 用户点击添加按钮后，系统应重置表单
- 系统应显示字段输入区域
- 系统应提供用户反馈
- 用户填写数据后应能保存记录

## 3. 设计决策

### 3.1 界面设计
- 添加按钮应位于操作工具栏
- 点击添加按钮后，表单区域应显示字段输入控件
- 应显示重置成功的提示信息

### 3.2 流程设计
1. 用户点击添加按钮
2. 系统调用 reset_form() 重置表单
3. 系统调用 fields_frame.pack() 显示字段区域
4. 系统显示 "表单已重置，可添加新记录" 提示
5. 用户填写表单数据
6. 用户点击保存按钮
7. 系统验证并保存数据
8. 系统刷新数据列表

## 4. 实现细节

### 4.1 核心方法
```python
def add_record(self):
    # 1. 重置表单
    self.reset_form()
    # 2. 显示字段区域
    if hasattr(self, 'fields_frame'):
        self.fields_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    # 3. 提供用户反馈
    messagebox.showinfo('重置成功', '表单已重置，可添加新记录')
```

### 4.2 关键步骤
- 表单重置：清空所有字段值
- 字段显示：确保用户可以看到输入界面
- 用户反馈：提供明确的操作结果提示

## 5. 测试计划
- 测试点击添加按钮后是否重置表单
- 测试是否显示字段输入区域
- 测试是否显示重置成功提示
- 测试添加新记录并保存的完整流程
""",
            
            "edit": """# 编辑操作设计文档

## 1. 概述
编辑操作允许用户修改现有记录，包括加载记录数据、显示字段区域和更新数据等步骤。

## 2. 功能需求
- 用户选择记录后，系统应加载记录数据
- 系统应显示字段输入区域
- 用户修改数据后应能保存更新

## 3. 设计决策

### 3.1 界面设计
- 编辑按钮应位于操作工具栏
- 点击编辑按钮后，表单区域应显示字段输入控件和加载的记录数据

### 3.2 流程设计
1. 用户在数据列表中选择一条记录
2. 用户点击编辑按钮
3. 系统验证记录选择
4. 系统调用 fields_frame.pack() 显示字段区域
5. 系统调用 load_data() 加载记录数据
6. 用户修改表单数据
7. 用户点击保存按钮
8. 系统验证并保存更新
9. 系统刷新数据列表

## 4. 实现细节

### 4.1 核心方法
```python
def edit_record(self, record_id):
    # 1. 验证记录ID
    if not record_id:
        messagebox.showinfo('提示', '请选择要编辑的记录')
        return
    # 2. 显示字段区域
    if hasattr(self, 'fields_frame'):
        self.fields_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    # 3. 加载记录数据
    self.load_data(record_id)
```

### 4.2 关键步骤
- 记录选择验证：确保用户选择了有效的记录
- 字段显示：确保用户可以看到输入界面
- 数据加载：确保正确加载现有记录数据

## 5. 测试计划
- 测试未选择记录时点击编辑按钮的提示
- 测试选择记录后点击编辑按钮是否显示字段区域
- 测试是否正确加载记录数据
- 测试修改记录并保存的完整流程
""",
            
            "delete": """# 删除操作设计文档

## 1. 概述
删除操作允许用户移除现有记录，包括确认操作、执行删除和刷新数据等步骤。

## 2. 功能需求
- 用户选择记录后，系统应要求确认删除
- 确认后系统应执行删除操作
- 删除后系统应刷新数据列表

## 3. 设计决策

### 3.1 界面设计
- 删除按钮应位于操作工具栏
- 点击删除按钮后，系统应显示确认对话框

### 3.2 流程设计
1. 用户在数据列表中选择一条记录
2. 用户点击删除按钮
3. 系统验证记录选择
4. 系统显示删除确认对话框
5. 用户确认删除
6. 系统执行删除操作
7. 系统刷新数据列表
8. 系统显示删除成功提示

## 4. 实现细节

### 4.1 核心方法
```python
def delete_record(self, record_id):
    # 1. 验证记录ID
    if not record_id:
        messagebox.showinfo('提示', '请选择要删除的记录')
        return
    # 2. 确认删除操作
    if messagebox.askyesno('确认', '确定要删除这条记录吗？'):
        # 3. 执行删除操作
        # 4. 刷新数据列表
        self.refresh_data_list()
        # 5. 提供用户反馈
        messagebox.showinfo('操作成功', '记录已删除')
```

### 4.2 关键步骤
- 记录选择验证：确保用户选择了有效的记录
- 删除确认：防止误操作
- 数据刷新：确保用户看到最新的数据状态

## 5. 测试计划
- 测试未选择记录时点击删除按钮的提示
- 测试选择记录后点击删除按钮是否显示确认对话框
- 测试确认删除后是否成功删除记录
- 测试删除后数据列表是否更新
"""
        }
        
        return designs.get(operation_type, "# 操作设计文档")
    
    def generate_implementation_guide(self, feature_type):
        """
        生成实现指南
        
        Args:
            feature_type: 功能类型
            
        Returns:
            str: 实现指南内容
        """
        guides = {
            "user_operation": """# 用户操作实现指南

## 1. 基本流程

### 1.1 通用操作流程
1. **验证输入**：检查操作所需的参数是否有效
2. **显示界面**：确保用户可以看到相关的操作界面
3. **执行操作**：执行核心业务逻辑
4. **提供反馈**：向用户提供明确的操作结果
5. **刷新数据**：更新相关的数据显示

### 1.2 操作类型
- **添加操作**：重置表单 → 显示字段 → 提供反馈
- **编辑操作**：验证选择 → 显示字段 → 加载数据 → 提供反馈
- **删除操作**：验证选择 → 确认操作 → 执行删除 → 刷新数据 → 提供反馈

## 2. 实现规范

### 2.1 代码结构
```python
def operation_method(self{params}):
    """操作描述"""
    # 1. 验证输入
    {validation_code}
    
    # 2. 显示界面（如果需要）
    if hasattr(self, 'fields_frame'):
        self.fields_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # 3. 执行核心操作
    {core_operation}
    
    # 4. 提供用户反馈
    messagebox.showinfo('操作成功', '操作结果描述')
    
    # 5. 刷新相关数据
    self.refresh_data_list()
```

### 2.2 界面处理
- **显示字段区域**：使用 `fields_frame.pack()` 确保用户可以看到输入界面
- **隐藏字段区域**：使用 `fields_frame.pack_forget()` 在不需要时隐藏
- **更新界面**：在数据变更后及时更新相关的UI组件

### 2.3 用户反馈
- **操作成功**：使用 `messagebox.showinfo()` 提供成功提示
- **操作失败**：使用 `messagebox.showerror()` 提供错误提示
- **操作确认**：使用 `messagebox.askyesno()` 进行操作确认

## 3. 常见问题及解决方案

### 3.1 问题：点击按钮后无响应
**解决方案**：
- 检查函数是否正确实现
- 检查是否显示了必要的用户界面
- 检查是否提供了用户反馈

### 3.2 问题：数据未保存
**解决方案**：
- 检查保存逻辑是否正确
- 检查是否调用了 `save_data()` 方法
- 检查是否处理了异常情况

### 3.3 问题：界面未更新
**解决方案**：
- 检查是否调用了 `refresh_data_list()` 方法
- 检查是否正确处理了UI组件的显示/隐藏

## 4. 最佳实践

1. **完整流程**：确保每个操作都包含完整的流程步骤
2. **用户体验**：提供清晰的界面反馈和操作提示
3. **错误处理**：合理处理异常情况，提供友好的错误提示
4. **代码一致性**：保持类似操作的代码结构一致
5. **测试覆盖**：为每个操作编写相应的测试用例
"""
        }
        
        return guides.get(feature_type, "# 实现指南")
    
    def create_version_history(self, component_name, versions):
        """
        创建版本历史
        
        Args:
            component_name: 组件名称
            versions: 版本列表
            
        Returns:
            str: 版本历史内容
        """
        history = f"# {component_name} 版本历史\n\n"
        
        history += "| 版本 | 日期 | 变更描述 | 变更人 |\n"
        history += "|------|------|----------|--------|\n"
        
        for version in versions:
            history += f"| {version.get('version', '1.0')} | {version.get('date', '2026-02-10')} | {version.get('description', '变更描述')} | {version.get('author', '系统')} |\n"
        
        return history

# 示例用法
if __name__ == "__main__":
    doc = DocumentationDesignDecisions()
    
    # 创建添加操作设计文档
    add_design = doc.generate_user_operation_design("add")
    print("\n=== 添加操作设计文档 ===")
    print(add_design[:500] + "...")  # 显示前500字符
    
    # 创建实现指南
    guide = doc.generate_implementation_guide("user_operation")
    print("\n=== 用户操作实现指南 ===")
    print(guide[:500] + "...")  # 显示前500字符
