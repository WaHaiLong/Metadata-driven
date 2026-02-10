# MDA 元数据驱动表单系统部署文档

## 系统概述
MDA（Metadata-Driven Architecture）元数据驱动表单系统是一套轻量化但贴近企业级 ERP 体验的表单系统，支持通过元数据配置表单字段、布局和规则，无需修改代码即可扩展字段和适配多端。

## 技术栈
- Python 3.6+
- tkinter（界面）
- xml.etree（解析）
- JSON（数据持久化）
- pyinstaller（打包）

## 系统结构
```
mda-form-system/
├── erp_form_metadata.xml      # 元数据配置文件
├── mda_form_engine.py         # 核心引擎代码
├── metadata_editor.py         # 元数据可视化编辑器
├── test_mda_form.py           # 单元测试文件
├── test_integration.py        # 集成测试文件
├── DEPLOYMENT.md              # 部署文档
├── 计划.md                     # 项目开发计划
├── .gitignore                 # Git忽略文件
└── dist/
    └── mda_form_engine.exe     # 打包后的可执行文件
```

## 部署方式

### 方式一：直接运行源码
1. **安装Python环境**
   - 下载并安装Python 3.6+（推荐3.10+）
   - 验证安装：`python --version`

2. **克隆仓库**
   ```bash
   git clone https://github.com/WaHaiLong/Metadata-driven.git
   cd Metadata-driven
   ```

3. **运行系统**
   ```bash
   python mda_form_engine.py
   ```

### 方式二：使用打包后的可执行文件
1. **下载可执行文件**
   - 从GitHub仓库的`dist`目录下载`mda_form_engine.exe`

2. **运行可执行文件**
   - 直接双击`mda_form_engine.exe`即可运行
   - 无需安装Python环境

## 元数据配置

### 字段类型
- **TextField**：文本字段，支持多行文本
  - 属性：name, Length, Left, Top, Width, Height, VisibleExt
  - 验证规则：Required

- **ComboBox**：下拉框字段
  - 属性：name, Left, Top, Width, Height, VisibleExt
  - 子元素：Options -> Option

- **MoneyField**：金额字段
  - 属性：name, Length, Left, Top, Width, Height, VisibleExt
  - 验证规则：Required, Number

### 多端适配
- **VisibleExt**：多端可见性配置
  - 格式：三位数编码（PC端、平板端、移动端）
  - 示例：
    - `111`：全端显示
    - `100`：仅PC端显示
    - `010`：仅平板端显示
    - `001`：仅移动端显示

### 验证规则
- **Required**：非空校验
  - `1`：必填
  - `0`：非必填

- **Number**：数字格式校验
  - `1`：必须为数字
  - `0`：不限制

## 使用指南

### 1. 运行表单系统
- 直接运行`mda_form_engine.py`或`mda_form_engine.exe`
- 系统会自动加载`erp_form_metadata.xml`中的配置

### 2. 编辑元数据
- 方式一：直接编辑`erp_form_metadata.xml`文件
- 方式二：运行元数据编辑器
  ```bash
  python metadata_editor.py
  ```

### 3. 操作表单
- **输入数据**：在对应字段中输入数据
- **保存数据**：点击"保存"按钮，数据会保存到`form_data.json`
- **加载数据**：点击"加载"按钮，会从`form_data.json`加载历史数据
- **重置表单**：点击"重置"按钮，清空所有字段
- **提交表单**：点击"提交"按钮，触发表单验证

### 4. 扩展字段
1. 在`erp_form_metadata.xml`中添加新的字段节点
2. 保存配置文件
3. 重新运行表单系统

## 测试

### 运行单元测试
```bash
python -m unittest test_mda_form.py
```

### 运行集成测试
```bash
python -m unittest test_integration.py
```

## 打包部署

### 使用pyinstaller打包
1. **安装pyinstaller**
   ```bash
   pip install pyinstaller
   ```

2. **执行打包命令**
   ```bash
   pyinstaller -F -w mda_form_engine.py
   ```
   - `-F`：生成单文件可执行文件
   - `-w`：无控制台窗口

3. **获取可执行文件**
   - 打包后的文件位于`dist/mda_form_engine.exe`

## 常见问题

### 问题1：表单无法运行
- **原因**：Python环境未安装或版本过低
- **解决**：安装Python 3.6+版本

### 问题2：元数据解析错误
- **原因**：XML格式错误或字段属性缺失
- **解决**：检查XML文件格式，确保所有必要属性都已设置

### 问题3：数据保存失败
- **原因**：文件权限不足或磁盘空间不足
- **解决**：确保程序有写入权限，检查磁盘空间

### 问题4：打包后的可执行文件无法运行
- **原因**：依赖缺失或打包参数错误
- **解决**：重新执行打包命令，确保所有依赖都已包含

## 扩展建议

1. **支持更多字段类型**
   - 日期字段、复选框、单选按钮等

2. **增强验证规则**
   - 正则表达式验证、范围验证等

3. **数据存储优化**
   - 支持SQLite数据库存储

4. **界面美化**
   - 使用更现代的UI库（如PyQt）

5. **Web版本**
   - 使用Flask/FastAPI开发Web版本

## 版本历史
- **v1.0**：基础功能实现
  - 元数据解析和动态渲染
  - 多字段类型支持
  - 基本验证规则
  - 数据持久化
  - 打包部署

## 联系方式
- **GitHub**：https://github.com/WaHaiLong/Metadata-driven
- **邮箱**：[your-email@example.com]

---

*此文档由MDA元数据驱动表单系统自动生成*