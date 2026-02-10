import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class MDAFormEngine:
    def __init__(self, metadata_file):
        self.metadata_file = metadata_file
        self.fields = {}
        self.field_widgets = {}
        self.root = None
        self.form_frame = None
        self.modules = {}
        self.current_module = None
        self.current_form = None
        self.form_name = "测试表单"
        self.load_metadata()
    
    def load_metadata(self):
        tree = ET.parse(self.metadata_file)
        root = tree.getroot()
        
        # 检查是否有Modules节点（新格式）
        modules_elem = root.find('Modules')
        if modules_elem:
            self.load_modules(modules_elem)
        else:
            # 向后兼容：旧格式
            form = root.find('Form')
            if form is not None:
                self.form_name = form.get('name')
                self.load_fields(form.find('FieldList'))
    
    def load_modules(self, modules_elem):
        """加载模块结构"""
        for module_elem in modules_elem.findall('Module'):
            module_name = module_elem.get('name')
            self.modules[module_name] = {}
            
            forms_elem = module_elem.find('Forms')
            if forms_elem:
                for form_elem in forms_elem.findall('Form'):
                    form_name = form_elem.get('name')
                    self.modules[module_name][form_name] = {
                        'fields': {}
                    }
                    
                    field_list = form_elem.find('FieldList')
                    if field_list:
                        for field_elem in field_list:
                            field_type = field_elem.tag
                            field_name = field_elem.get('name')
                            field_info = {
                                'type': field_type,
                                'left': int(field_elem.get('Left', 10)),
                                'top': int(field_elem.get('Top', 10)),
                                'width': int(field_elem.get('Width', 200)),
                                'height': int(field_elem.get('Height', 30)),
                                'visible_ext': field_elem.get('VisibleExt', '111')
                            }
                            
                            if field_type == 'TextField':
                                field_info['length'] = int(field_elem.get('Length', 200))
                            elif field_type == 'ComboBox':
                                field_info['options'] = [opt.text for opt in field_elem.find('Options').findall('Option')]
                            elif field_type == 'MoneyField':
                                field_info['length'] = int(field_elem.get('Length', 10))
                            
                            validation = field_elem.find('Validation')
                            if validation is not None:
                                field_info['validation'] = {}
                                if validation.find('Required') is not None:
                                    field_info['validation']['required'] = validation.find('Required').text == '1'
                                if validation.find('Number') is not None:
                                    field_info['validation']['number'] = validation.find('Number').text == '1'
                            
                            self.modules[module_name][form_name]['fields'][field_name] = field_info
    
    def load_fields(self, field_list_elem):
        """加载字段（旧格式）"""
        for field_elem in field_list_elem:
            field_type = field_elem.tag
            field_name = field_elem.get('name')
            field_info = {
                'type': field_type,
                'left': int(field_elem.get('Left', 10)),
                'top': int(field_elem.get('Top', 10)),
                'width': int(field_elem.get('Width', 200)),
                'height': int(field_elem.get('Height', 30)),
                'visible_ext': field_elem.get('VisibleExt', '111')
            }
            
            if field_type == 'TextField':
                field_info['length'] = int(field_elem.get('Length', 200))
            elif field_type == 'ComboBox':
                field_info['options'] = [opt.text for opt in field_elem.find('Options').findall('Option')]
            elif field_type == 'MoneyField':
                field_info['length'] = int(field_elem.get('Length', 10))
            
            validation = field_elem.find('Validation')
            if validation is not None:
                field_info['validation'] = {}
                if validation.find('Required') is not None:
                    field_info['validation']['required'] = validation.find('Required').text == '1'
                if validation.find('Number') is not None:
                    field_info['validation']['number'] = validation.find('Number').text == '1'
            
            self.fields[field_name] = field_info
    
    def set_current_form(self, module_name, form_name):
        """设置当前表单"""
        self.current_module = module_name
        self.current_form = form_name
        self.form_name = form_name
        
        # 加载当前表单的字段
        if module_name in self.modules and form_name in self.modules[module_name]:
            self.fields = self.modules[module_name][form_name]['fields']
        else:
            self.fields = {}
    
    def is_visible(self, visible_ext):
        return visible_ext[0] == '1'  # 简化处理，只考虑PC端
    
    def validate_form(self):
        for field_name, field_info in self.fields.items():
            if not self.is_visible(field_info['visible_ext']):
                continue
            
            widget = self.field_widgets.get(field_name)
            if not widget:
                continue
            
            validation = field_info.get('validation', {})
            if validation.get('required'):
                value = widget.get() if hasattr(widget, 'get') else ''
                if isinstance(value, str) and not value.strip():
                    messagebox.showerror('验证错误', f'{field_name} 不能为空')
                    return False
            
            if validation.get('number'):
                value = widget.get() if hasattr(widget, 'get') else ''
                if value and isinstance(value, str):
                    try:
                        float(value)
                    except ValueError:
                        messagebox.showerror('验证错误', f'{field_name} 必须是数字')
                        return False
        
        messagebox.showinfo('验证成功', '表单验证通过')
        return True
    
    def save_data(self):
        data = {}
        for field_name, widget in self.field_widgets.items():
            if hasattr(widget, 'get'):
                value = widget.get()
                if isinstance(value, str):
                    value = value.strip()
                data[field_name] = value
        
        # 为每个单据创建独立的数据文件
        if self.current_module and self.current_form:
            filename = f'data_{self.current_module}_{self.current_form}.json'
        else:
            filename = 'form_data.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        messagebox.showinfo('保存成功', f'表单数据已保存到 {filename}')
    
    def load_data(self):
        # 为每个单据创建独立的数据文件
        if self.current_module and self.current_form:
            filename = f'data_{self.current_module}_{self.current_form}.json'
        else:
            filename = 'form_data.json'
        
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for field_name, value in data.items():
                    widget = self.field_widgets.get(field_name)
                    if widget:
                        if hasattr(widget, 'delete') and hasattr(widget, 'insert'):
                            widget.delete(0, tk.END)
                            widget.insert(0, value)
                        elif hasattr(widget, 'set'):
                            widget.set(value)
                
                messagebox.showinfo('加载成功', f'历史数据已加载 from {filename}')
            except Exception as e:
                messagebox.showerror('加载错误', f'加载数据失败: {e}')
    
    def reset_form(self):
        for widget in self.field_widgets.values():
            if hasattr(widget, 'delete') and hasattr(widget, 'insert'):
                widget.delete(0, tk.END)
            elif hasattr(widget, 'set'):
                widget.set('')
        messagebox.showinfo('重置成功', '表单已重置')
    
    def create_form(self):
        self.root = tk.Tk()
        self.root.title(self.form_name)
        self.root.geometry('1200x800')
        self.root.resizable(True, True)
        
        # 设置ERP风格的颜色和字体
        self.root.configure(bg='#f8f9fa')
        
        # 全局样式设置
        style = ttk.Style()
        
        # 配置按钮样式
        style.configure('TButton',
                       font=('SimHei', 10),
                       padding=[10, 5],
                       relief=tk.FLAT)
        
        # 配置标签样式
        style.configure('TLabel',
                       font=('SimHei', 10),
                       foreground='#333333')
        
        # 配置输入框样式
        style.configure('TEntry',
                       font=('SimHei', 10),
                       padding=[5, 3])
        
        # 配置下拉框样式
        style.configure('TCombobox',
                       font=('SimHei', 10),
                       padding=[5, 3])
        
        # 配置滚动条样式
        style.configure('Vertical.TScrollbar',
                       gripcount=0,
                       background='#f0f0f0',
                       darkcolor='#f0f0f0',
                       lightcolor='#f0f0f0',
                       troughcolor='#f0f0f0',
                       arrowcolor='#666666')
        
        style.configure('Horizontal.TScrollbar',
                       gripcount=0,
                       background='#f0f0f0',
                       darkcolor='#f0f0f0',
                       lightcolor='#f0f0f0',
                       troughcolor='#f0f0f0',
                       arrowcolor='#666666')
        
        # 顶部标题栏
        title_frame = tk.Frame(self.root, bg='#1a56db', relief=tk.RAISED, bd=0)
        title_frame.pack(fill=tk.X, pady=0, padx=0)
        
        # 左侧：系统名称
        left_title = tk.Frame(title_frame, bg='#1a56db')
        left_title.pack(side=tk.LEFT, padx=20, pady=5)
        
        system_label = tk.Label(left_title, text='未来AI', font=('SimHei', 14, 'bold'), bg='#1a56db', fg='white')
        system_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        module_label = tk.Label(left_title, text='智能云', font=('SimHei', 12), bg='#1a56db', fg='white')
        module_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # 右侧：用户信息和快捷操作
        right_title = tk.Frame(title_frame, bg='#1a56db')
        right_title.pack(side=tk.RIGHT, padx=20, pady=5)
        
        # 通知按钮
        notify_btn = tk.Button(right_title, text='🔔', font=('SimHei', 12), bg='#1a56db', fg='white', bd=0, width=3, height=1)
        notify_btn.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # 设置按钮
        settings_btn = tk.Button(right_title, text='⚙️', font=('SimHei', 12), bg='#1a56db', fg='white', bd=0, width=3, height=1)
        settings_btn.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # 用户信息
        user_label = tk.Label(right_title, text='张明华', font=('SimHei', 12), bg='#1a56db', fg='white')
        user_label.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # 登录按钮
        login_btn = tk.Button(right_title, text='注册账号', font=('SimHei', 10), bg='#1a56db', fg='white', bd=0, width=8, height=1)
        login_btn.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # 工具栏
        toolbar_frame = tk.Frame(self.root, bg='#e9ecef', relief=tk.RAISED, bd=1)
        toolbar_frame.pack(fill=tk.X, pady=0, padx=0)
        
        toolbar_label = tk.Label(toolbar_frame, text='操作', font=('SimHei', 10, 'bold'), bg='#e9ecef')
        toolbar_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # 帮助系统
        help_label = tk.Label(toolbar_frame, text='帮助', font=('SimHei', 10, 'bold'), bg='#e9ecef')
        help_label.pack(side=tk.LEFT, padx=20, pady=5)
        
        help_btn = tk.Button(toolbar_frame, text='使用指南', command=self.show_help, width=10, height=1, bg='#17a2b8', fg='white', font=('SimHei', 9, 'bold'))
        help_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        guide_btn = tk.Button(toolbar_frame, text='操作引导', command=self.show_guide, width=10, height=1, bg='#17a2b8', fg='white', font=('SimHei', 9, 'bold'))
        guide_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 主内容区
        main_frame = tk.Frame(self.root, bg='#f8f9fa')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧导航栏
        nav_frame = tk.Frame(main_frame, bg='#f0f2f5', relief=tk.RAISED, bd=0, width=220)
        nav_frame.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)
        
        # 导航栏标题
        nav_title_frame = tk.Frame(nav_frame, bg='#f0f2f5', relief=tk.FLAT, bd=0)
        nav_title_frame.pack(fill=tk.X, pady=10, padx=10)
        nav_title_label = tk.Label(nav_title_frame, text='模块导航', font=('SimHei', 12, 'bold'), bg='#f0f2f5', fg='#333333')
        nav_title_label.pack(pady=5, padx=10, anchor=tk.W)
        
        # 模块列表
        self.nav_tree = ttk.Treeview(nav_frame, show='tree', height=25)
        
        # 定制导航树样式
        style = ttk.Style()
        style.configure('Custom.Treeview', 
                       background='#f0f2f5', 
                       foreground='#333333', 
                       rowheight=28, 
                       fieldbackground='#f0f2f5',
                       font=('SimHei', 10))
        style.configure('Custom.Treeview.Item',
                       padding=[10, 5])
        style.map('Custom.Treeview',
                 background=[('selected', '#e6f7ff'), ('hover', '#f5f5f5')],
                 foreground=[('selected', '#1890ff')])
        
        self.nav_tree.configure(style='Custom.Treeview')
        self.nav_tree.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # 填充模块和单据
        self.populate_nav_tree()
        
        # 绑定导航点击事件
        self.nav_tree.bind('<<TreeviewSelect>>', self.on_nav_select)
        
        # 右侧表单区域
        form_frame = tk.Frame(main_frame, bg='#f8f9fa')
        form_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # 操作按钮栏
        action_frame = tk.Frame(form_frame, bg='#ffffff', relief=tk.FLAT, bd=1)
        action_frame.pack(fill=tk.X, pady=0, padx=0)
        
        # 左侧操作按钮
        left_actions = tk.Frame(action_frame, bg='#ffffff')
        left_actions.pack(side=tk.LEFT, padx=10, pady=5)
        
        new_btn = tk.Button(left_actions, text='新增', command=self.save_data, width=8, height=1, bg='#1890ff', fg='white', font=('SimHei', 9, 'bold'))
        new_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        edit_btn = tk.Button(left_actions, text='修改', command=self.load_data, width=8, height=1, bg='#1890ff', fg='white', font=('SimHei', 9, 'bold'))
        edit_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        delete_btn = tk.Button(left_actions, text='删除', command=self.reset_form, width=8, height=1, bg='#ff4d4f', fg='white', font=('SimHei', 9, 'bold'))
        delete_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 右侧操作按钮
        right_actions = tk.Frame(action_frame, bg='#ffffff')
        right_actions.pack(side=tk.RIGHT, padx=10, pady=5)
        
        refresh_btn = tk.Button(right_actions, text='刷新', command=self.load_data, width=8, height=1, bg='#f0f0f0', fg='#333333', font=('SimHei', 9, 'bold'))
        refresh_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        export_btn = tk.Button(right_actions, text='导出', command=self.save_data, width=8, height=1, bg='#f0f0f0', fg='#333333', font=('SimHei', 9, 'bold'))
        export_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # 表单容器
        form_container = tk.Frame(form_frame, bg='#ffffff', relief=tk.FLAT, bd=0)
        form_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # 表单标题
        form_title_frame = tk.Frame(form_container, bg='#fafafa', relief=tk.FLAT, bd=0)
        form_title_frame.pack(fill=tk.X, pady=0, padx=0)
        self.form_title_label = tk.Label(form_title_frame, text='表单信息', font=('SimHei', 12, 'bold'), bg='#fafafa', fg='#333333')
        self.form_title_label.pack(pady=10, padx=20, anchor=tk.W)
        
        # 字段容器
        self.fields_frame = tk.Frame(form_container, bg='#ffffff')
        self.fields_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 底部按钮区域
        button_frame = tk.Frame(form_container, bg='#ffffff', relief=tk.FLAT, bd=0)
        button_frame.pack(fill=tk.X, pady=10, padx=20)
        
        # 左侧按钮
        left_buttons = tk.Frame(button_frame, bg='#ffffff')
        left_buttons.pack(side=tk.LEFT, padx=10, pady=5)
        
        save_btn = tk.Button(left_buttons, text='保存', command=self.save_data, width=10, height=2, bg='#1890ff', fg='white', font=('SimHei', 10, 'bold'))
        save_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        load_btn = tk.Button(left_buttons, text='加载', command=self.load_data, width=10, height=2, bg='#52c41a', fg='white', font=('SimHei', 10, 'bold'))
        load_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        reset_btn = tk.Button(left_buttons, text='重置', command=self.reset_form, width=10, height=2, bg='#faad14', fg='white', font=('SimHei', 10, 'bold'))
        reset_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 右侧按钮
        right_buttons = tk.Frame(button_frame, bg='#ffffff')
        right_buttons.pack(side=tk.RIGHT, padx=10, pady=5)
        
        submit_btn = tk.Button(right_buttons, text='提交', command=self.validate_form, width=10, height=2, bg='#1890ff', fg='white', font=('SimHei', 10, 'bold'))
        submit_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # 初始化显示第一个表单
        self.initialize_first_form()
    
    def populate_nav_tree(self):
        """填充导航树"""
        # 清空现有内容
        for item in self.nav_tree.get_children():
            self.nav_tree.delete(item)
        
        # 模块图标映射
        module_icons = {
            '采购管理': '📦',
            '销售管理': '💼',
            '库存管理': '🏪',
            '财务管理': '💰',
            '人力资源': '👥',
            '生产管理': '🏭',
            'CRM': '👤'
        }
        
        # 添加模块和单据
        for module_name, forms in self.modules.items():
            # 获取模块图标
            icon = module_icons.get(module_name, '📁')
            
            # 添加模块
            module_item = self.nav_tree.insert('', tk.END, text=f'{icon} {module_name}', open=True)
            
            # 添加单据
            for form_name in forms:
                self.nav_tree.insert(module_item, tk.END, text=f'📄 {form_name}', tags=(module_name, form_name))
    
    def on_nav_select(self, event):
        """导航选择事件"""
        selected_items = self.nav_tree.selection()
        if not selected_items:
            return
        
        item = selected_items[0]
        tags = self.nav_tree.item(item, 'tags')
        if len(tags) == 2:
            module_name, form_name = tags
            self.switch_form(module_name, form_name)
    
    def switch_form(self, module_name, form_name):
        """切换表单"""
        # 设置当前表单
        self.set_current_form(module_name, form_name)
        
        # 更新标题
        self.root.title(f"{module_name} - {form_name}")
        self.form_title_label.config(text=f"{form_name}信息")
        
        # 清空现有字段控件
        for widget in self.fields_frame.winfo_children():
            widget.destroy()
        self.field_widgets.clear()
        
        # 模拟数据，用于测试表格布局
        if form_name == '采购订单' or form_name == '销售订单':
            # 显示表格布局
            test_data = [
                {'订单编号': 'PO20260210001', '供应商': '上海金蝶软件有限公司', '金额': '10000.00', '状态': '已审核', '创建日期': '2026-02-10'},
                {'订单编号': 'PO20260210002', '供应商': '北京用友网络科技股份有限公司', '金额': '20000.00', '状态': '未审核', '创建日期': '2026-02-10'},
                {'订单编号': 'PO20260210003', '供应商': '深圳华为技术有限公司', '金额': '30000.00', '状态': '已审核', '创建日期': '2026-02-09'},
                {'订单编号': 'PO20260210004', '供应商': '杭州阿里巴巴网络技术有限公司', '金额': '40000.00', '状态': '未审核', '创建日期': '2026-02-09'},
                {'订单编号': 'PO20260210005', '供应商': '腾讯科技(深圳)有限公司', '金额': '50000.00', '状态': '已审核', '创建日期': '2026-02-08'}
            ]
            self.render_table(test_data)
        else:
            # 渲染字段
            self.render_fields()
            # 加载表单数据
            self.load_data()
    
    def render_fields(self):
        """渲染字段"""
        # 计算最大字段数量和布局
        max_columns = 2
        field_count = 0
        
        for field_name, field_info in self.fields.items():
            if not self.is_visible(field_info['visible_ext']):
                continue
            
            # 计算行列位置
            row = field_count // max_columns
            col = field_count % max_columns
            
            # 字段标签
            label_frame = tk.Frame(self.fields_frame, bg='#ffffff')
            label_frame.grid(row=row, column=col*2, padx=15, pady=12, sticky=tk.W)
            label = tk.Label(label_frame, text=field_name, font=('SimHei', 10), bg='#ffffff', anchor=tk.W, width=15, fg='#333333')
            label.pack(pady=2, anchor=tk.W)
            
            # 字段输入控件
            input_frame = tk.Frame(self.fields_frame, bg='#ffffff')
            input_frame.grid(row=row, column=col*2+1, padx=15, pady=12, sticky=tk.W)
            
            if field_info['type'] == 'TextField':
                if field_info['height'] > 30:
                    text_widget = tk.Text(input_frame, wrap=tk.WORD, width=35, height=4, font=('SimHei', 10), relief=tk.SOLID, bd=1, bg='#ffffff')
                    text_widget.pack(pady=2)
                    text_widget.bind('<KeyRelease>', lambda e, w=text_widget, l=field_info['length']: self.limit_text(w, l))
                    self.field_widgets[field_name] = text_widget
                else:
                    entry = tk.Entry(input_frame, width=35, font=('SimHei', 10), relief=tk.SOLID, bd=1, bg='#ffffff')
                    entry.pack(pady=2)
                    entry.bind('<KeyRelease>', lambda e, w=entry, l=field_info['length']: self.limit_text(w, l))
                    self.field_widgets[field_name] = entry
            elif field_info['type'] == 'ComboBox':
                combobox = ttk.Combobox(input_frame, values=field_info['options'], width=33, font=('SimHei', 10))
                combobox.pack(pady=2)
                self.field_widgets[field_name] = combobox
            elif field_info['type'] == 'MoneyField':
                entry = tk.Entry(input_frame, width=35, font=('SimHei', 10), relief=tk.SOLID, bd=1, bg='#ffffff')
                entry.pack(pady=2)
                self.field_widgets[field_name] = entry
            
            field_count += 1
    
    def render_table(self, data):
        """渲染表格数据"""
        # 清空现有内容
        for widget in self.fields_frame.winfo_children():
            widget.destroy()
        
        # 创建表格
        columns = list(data[0].keys()) if data else []
        
        if columns:
            # 创建表格框架
            table_frame = tk.Frame(self.fields_frame, bg='#ffffff')
            table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # 创建滚动条
            scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
            scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
            
            # 创建表格
            table = ttk.Treeview(table_frame, 
                                columns=columns, 
                                show='headings', 
                                yscrollcommand=scrollbar_y.set, 
                                xscrollcommand=scrollbar_x.set)
            
            # 配置滚动条
            scrollbar_y.config(command=table.yview)
            scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
            
            scrollbar_x.config(command=table.xview)
            scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
            
            # 设置列标题
            for col in columns:
                table.heading(col, text=col)
                table.column(col, width=120, anchor=tk.CENTER)
            
            # 填充数据
            for row in data:
                table.insert('', tk.END, values=list(row.values()))
            
            # 定制表格样式
            style = ttk.Style()
            style.configure('Custom.Treeview', 
                           background='#ffffff', 
                           foreground='#333333', 
                           rowheight=25, 
                           fieldbackground='#ffffff',
                           font=('SimHei', 9))
            style.map('Custom.Treeview',
                     background=[('selected', '#e6f7ff'), ('hover', '#f5f5f5')],
                     foreground=[('selected', '#1890ff')])
            
            table.configure(style='Custom.Treeview')
            table.pack(fill=tk.BOTH, expand=True)
            
            # 分页控件
            pagination_frame = tk.Frame(self.fields_frame, bg='#ffffff')
            pagination_frame.pack(fill=tk.X, padx=10, pady=10)
            
            page_info = tk.Label(pagination_frame, text='共 100 条记录，第 1/10 页', font=('SimHei', 9), bg='#ffffff', fg='#666666')
            page_info.pack(side=tk.LEFT, padx=10, pady=5)
            
            page_buttons = tk.Frame(pagination_frame, bg='#ffffff')
            page_buttons.pack(side=tk.RIGHT, padx=10, pady=5)
            
            first_btn = tk.Button(page_buttons, text='首页', width=6, height=1, bg='#f0f0f0', fg='#333333', font=('SimHei', 9))
            first_btn.pack(side=tk.LEFT, padx=5, pady=5)
            
            prev_btn = tk.Button(page_buttons, text='上一页', width=6, height=1, bg='#f0f0f0', fg='#333333', font=('SimHei', 9))
            prev_btn.pack(side=tk.LEFT, padx=5, pady=5)
            
            next_btn = tk.Button(page_buttons, text='下一页', width=6, height=1, bg='#f0f0f0', fg='#333333', font=('SimHei', 9))
            next_btn.pack(side=tk.LEFT, padx=5, pady=5)
            
            last_btn = tk.Button(page_buttons, text='末页', width=6, height=1, bg='#f0f0f0', fg='#333333', font=('SimHei', 9))
            last_btn.pack(side=tk.LEFT, padx=5, pady=5)
    
    def initialize_first_form(self):
        """初始化显示第一个表单"""
        if self.modules:
            first_module = next(iter(self.modules))
            if self.modules[first_module]:
                first_form = next(iter(self.modules[first_module]))
                self.switch_form(first_module, first_form)
        else:
            # 渲染当前字段
            self.render_fields()
            # 加载历史数据
            self.load_data()
    
    def limit_text(self, widget, max_length):
        current_text = widget.get('1.0', tk.END) if hasattr(widget, 'get') and widget.cget('class') == 'Text' else widget.get()
        if len(current_text) > max_length:
            if hasattr(widget, 'delete'):
                if widget.cget('class') == 'Text':
                    widget.delete(f'1.0+{max_length}c', tk.END)
                else:
                    widget.delete(max_length, tk.END)
    
    def run(self):
        self.create_form()
        self.root.mainloop()
    
    def show_help(self):
        """显示使用指南"""
        help_window = tk.Toplevel(self.root)
        help_window.title('使用指南')
        help_window.geometry('700x500')
        help_window.resizable(True, True)
        help_window.configure(bg='#f8f9fa')
        
        # 顶部标题栏
        title_frame = tk.Frame(help_window, bg='#1a56db', relief=tk.RAISED, bd=2)
        title_frame.pack(fill=tk.X, pady=0, padx=0)
        title_label = tk.Label(title_frame, text='使用指南', font=('SimHei', 16, 'bold'), bg='#1a56db', fg='white')
        title_label.pack(pady=10, padx=20, anchor=tk.W)
        
        # 主内容区
        main_frame = tk.Frame(help_window, bg='#f8f9fa')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 帮助内容
        content_frame = tk.Frame(main_frame, bg='#ffffff', relief=tk.RAISED, bd=1)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 帮助文本
        help_text = """使用指南

1. 表单填写
   - 在各个字段中输入相应的数据
   - 文本字段支持多行输入
   - 下拉框可以选择预设的选项
   - 金额字段只能输入数字

2. 操作按钮
   - 保存：将当前表单数据保存到本地
   - 加载：从本地加载之前保存的数据
   - 重置：清空所有字段的内容
   - 提交：验证表单数据并提交

3. 验证规则
   - 非空字段：必须填写内容
   - 数字字段：只能输入数字格式

4. 多端适配
   - 系统会根据设备类型自动调整显示

5. 常见问题
   - 保存失败：检查文件权限
   - 验证错误：按照提示修改输入内容
   - 字段显示：确保字段在当前设备上可见

6. 高级功能
   - 使用元数据编辑器可以添加、修改字段
   - 支持配置模板的保存和加载

如有其他问题，请联系系统管理员。"""
        
        text_widget = tk.Text(content_frame, font=('SimHei', 10), wrap=tk.WORD, bg='#ffffff')
        text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)
        
        # 底部按钮
        button_frame = tk.Frame(main_frame, bg='#f8f9fa')
        button_frame.pack(fill=tk.X, pady=10, padx=10)
        
        close_btn = tk.Button(button_frame, text='关闭', command=help_window.destroy, width=12, height=2, bg='#6c757d', fg='white', font=('SimHei', 10, 'bold'))
        close_btn.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # 居中显示
        help_window.transient(self.root)
        help_window.grab_set()
        self.root.wait_window(help_window)
    
    def show_guide(self):
        """显示操作引导"""
        guide_window = tk.Toplevel(self.root)
        guide_window.title('操作引导')
        guide_window.geometry('700x400')
        guide_window.resizable(True, True)
        guide_window.configure(bg='#f8f9fa')
        
        # 顶部标题栏
        title_frame = tk.Frame(guide_window, bg='#1a56db', relief=tk.RAISED, bd=2)
        title_frame.pack(fill=tk.X, pady=0, padx=0)
        title_label = tk.Label(title_frame, text='操作引导', font=('SimHei', 16, 'bold'), bg='#1a56db', fg='white')
        title_label.pack(pady=10, padx=20, anchor=tk.W)
        
        # 主内容区
        main_frame = tk.Frame(guide_window, bg='#f8f9fa')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 引导内容
        content_frame = tk.Frame(main_frame, bg='#ffffff', relief=tk.RAISED, bd=1)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 引导步骤
        guide_steps = [
            "1. 打开表单系统",
            "2. 填写表单字段",
            "3. 点击保存按钮保存数据",
            "4. 点击加载按钮恢复数据",
            "5. 点击提交按钮验证并提交"
        ]
        
        steps_frame = tk.Frame(content_frame, bg='#ffffff')
        steps_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        for i, step in enumerate(guide_steps, 1):
            step_frame = tk.Frame(steps_frame, bg='#ffffff')
            step_frame.pack(fill=tk.X, pady=10, padx=10)
            
            step_num = tk.Label(step_frame, text=str(i), font=('SimHei', 12, 'bold'), bg='#1a56db', fg='white', width=3, height=2)
            step_num.pack(side=tk.LEFT, padx=10, pady=5)
            
            step_text = tk.Label(step_frame, text=step, font=('SimHei', 11), bg='#ffffff', anchor=tk.W)
            step_text.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.X, expand=True)
        
        # 底部按钮
        button_frame = tk.Frame(main_frame, bg='#f8f9fa')
        button_frame.pack(fill=tk.X, pady=10, padx=10)
        
        close_btn = tk.Button(button_frame, text='关闭', command=guide_window.destroy, width=12, height=2, bg='#6c757d', fg='white', font=('SimHei', 10, 'bold'))
        close_btn.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # 居中显示
        guide_window.transient(self.root)
        guide_window.grab_set()
        self.root.wait_window(guide_window)

if __name__ == '__main__':
    engine = MDAFormEngine('erp_form_metadata.xml')
    engine.run()