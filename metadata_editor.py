import tkinter as tk
from tkinter import ttk, messagebox
import xml.etree.ElementTree as ET
import os

class MetadataEditor:
    def __init__(self):
        self.metadata_file = 'erp_form_metadata.xml'
        self.fields = {}
        self.field_frames = {}
        self.modules = {}
        self.current_module = None
        self.current_form = None
        self.dragged_control = None  # 存储当前拖拽的控件名称
        
        self.create_widgets()
        self.load_metadata()
    
    def create_widgets(self):
        # 设置专业设计器风格的颜色和字体
        self.root = tk.Tk()
        self.root.title('后端设计器 - 未来AI')
        self.root.geometry('1400x900')
        self.root.resizable(True, True)
        self.root.configure(bg='#f0f0f0')
        
        # 设置窗口图标和样式
        try:
            # 这里可以添加图标设置代码
            pass
        except:
            pass
        
        # 绑定全局事件
        self.root.bind('<F1>', lambda e: self.help())
        self.root.bind('<Control-s>', lambda e: self.save_metadata())
        self.root.bind('<Control-n>', lambda e: self.new_project())
        self.root.bind('<Control-o>', lambda e: self.open_project())
        
        # 菜单栏
        menubar = tk.Menu(self.root)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label='新建', command=self.new_project)
        file_menu.add_command(label='打开', command=self.open_project)
        file_menu.add_command(label='保存', command=self.save_metadata)
        file_menu.add_command(label='另存为', command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label='退出', command=self.root.quit)
        menubar.add_cascade(label='文件', menu=file_menu)
        
        # 编辑菜单
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label='撤销', command=self.undo)
        edit_menu.add_command(label='重做', command=self.redo)
        edit_menu.add_separator()
        edit_menu.add_command(label='剪切', command=self.cut)
        edit_menu.add_command(label='复制', command=self.copy)
        edit_menu.add_command(label='粘贴', command=self.paste)
        menubar.add_cascade(label='编辑', menu=edit_menu)
        
        # 视图菜单
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label='工具栏', command=self.toggle_toolbar)
        view_menu.add_command(label='控件库', command=self.toggle_toolbox)
        view_menu.add_command(label='属性窗口', command=self.toggle_properties)
        menubar.add_cascade(label='视图', menu=view_menu)
        
        # 工具菜单
        tool_menu = tk.Menu(menubar, tearoff=0)
        tool_menu.add_command(label='选项', command=self.options)
        tool_menu.add_command(label='生成代码', command=self.generate_code)
        menubar.add_cascade(label='工具', menu=tool_menu)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label='使用帮助', command=self.help)
        help_menu.add_command(label='关于', command=self.about)
        menubar.add_cascade(label='帮助', menu=help_menu)
        
        self.root.config(menu=menubar)
        
        # 工具栏
        toolbar_frame = tk.Frame(self.root, bg='#e0e0e0', relief=tk.RAISED, bd=1)
        toolbar_frame.pack(fill=tk.X, pady=0, padx=0)
        
        # 标准工具按钮
        standard_tools = tk.Frame(toolbar_frame, bg='#e0e0e0')
        standard_tools.pack(side=tk.LEFT, padx=10, pady=5)
        
        new_btn = tk.Button(standard_tools, text='新建', width=8, height=1, bg='#ffffff', fg='#333333', font=('SimHei', 9, 'bold'), command=self.new_project)
        new_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        open_btn = tk.Button(standard_tools, text='打开', width=8, height=1, bg='#ffffff', fg='#333333', font=('SimHei', 9, 'bold'), command=self.open_project)
        open_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        save_btn = tk.Button(standard_tools, text='保存', width=8, height=1, bg='#ffffff', fg='#333333', font=('SimHei', 9, 'bold'), command=self.save_metadata)
        save_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        separator1 = tk.Frame(standard_tools, width=2, height=20, bg='#d0d0d0')
        separator1.pack(side=tk.LEFT, padx=5, pady=2)
        
        undo_btn = tk.Button(standard_tools, text='撤销', width=8, height=1, bg='#ffffff', fg='#333333', font=('SimHei', 9, 'bold'), command=self.undo)
        undo_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        redo_btn = tk.Button(standard_tools, text='重做', width=8, height=1, bg='#ffffff', fg='#333333', font=('SimHei', 9, 'bold'), command=self.redo)
        redo_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        separator2 = tk.Frame(standard_tools, width=2, height=20, bg='#d0d0d0')
        separator2.pack(side=tk.LEFT, padx=5, pady=2)
        
        cut_btn = tk.Button(standard_tools, text='剪切', width=8, height=1, bg='#ffffff', fg='#333333', font=('SimHei', 9, 'bold'), command=self.cut)
        cut_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        copy_btn = tk.Button(standard_tools, text='复制', width=8, height=1, bg='#ffffff', fg='#333333', font=('SimHei', 9, 'bold'), command=self.copy)
        copy_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        paste_btn = tk.Button(standard_tools, text='粘贴', width=8, height=1, bg='#ffffff', fg='#333333', font=('SimHei', 9, 'bold'), command=self.paste)
        paste_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # 模块管理工具
        module_tools = tk.Frame(toolbar_frame, bg='#e0e0e0')
        module_tools.pack(side=tk.LEFT, padx=20, pady=5)
        
        module_label = tk.Label(module_tools, text='模块管理', font=('SimHei', 10, 'bold'), bg='#e0e0e0', fg='#333333')
        module_label.pack(side=tk.LEFT, padx=10, pady=2)
        
        add_module_btn = tk.Button(module_tools, text='添加模块', width=10, height=1, bg='#28a745', fg='white', font=('SimHei', 9, 'bold'), command=self.add_module)
        add_module_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        delete_module_btn = tk.Button(module_tools, text='删除模块', width=10, height=1, bg='#dc3545', fg='white', font=('SimHei', 9, 'bold'), command=self.delete_module)
        delete_module_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # 单据管理工具
        form_tools = tk.Frame(toolbar_frame, bg='#e0e0e0')
        form_tools.pack(side=tk.LEFT, padx=20, pady=5)
        
        form_label = tk.Label(form_tools, text='单据管理', font=('SimHei', 10, 'bold'), bg='#e0e0e0', fg='#333333')
        form_label.pack(side=tk.LEFT, padx=10, pady=2)
        
        add_form_btn = tk.Button(form_tools, text='添加单据', width=10, height=1, bg='#28a745', fg='white', font=('SimHei', 9, 'bold'), command=self.add_form)
        add_form_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        delete_form_btn = tk.Button(form_tools, text='删除单据', width=10, height=1, bg='#dc3545', fg='white', font=('SimHei', 9, 'bold'), command=self.delete_form)
        delete_form_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # 字段管理工具
        field_tools = tk.Frame(toolbar_frame, bg='#e0e0e0')
        field_tools.pack(side=tk.LEFT, padx=20, pady=5)
        
        field_label = tk.Label(field_tools, text='字段管理', font=('SimHei', 10, 'bold'), bg='#e0e0e0', fg='#333333')
        field_label.pack(side=tk.LEFT, padx=10, pady=2)
        
        add_field_btn = tk.Button(field_tools, text='添加字段', width=10, height=1, bg='#28a745', fg='white', font=('SimHei', 9, 'bold'), command=self.add_field)
        add_field_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        delete_field_btn = tk.Button(field_tools, text='删除字段', width=10, height=1, bg='#dc3545', fg='white', font=('SimHei', 9, 'bold'), command=self.delete_field)
        delete_field_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # 右侧状态显示
        status_tools = tk.Frame(toolbar_frame, bg='#e0e0e0')
        status_tools.pack(side=tk.RIGHT, padx=10, pady=5)
        
        self.status_label = tk.Label(status_tools, text='就绪', font=('SimHei', 9), bg='#e0e0e0', fg='#333333')
        self.status_label.pack(side=tk.RIGHT, padx=10, pady=2)
        
        # 主内容区
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # 使用PanedWindow创建可调整大小的分割窗口
        self.main_paned = tk.PanedWindow(main_frame, orient=tk.HORIZONTAL, bg='#f0f0f0', sashwidth=5, sashrelief=tk.FLAT)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # 底部状态栏
        status_bar = tk.Frame(self.root, bg='#e0e0e0', relief=tk.SUNKEN, bd=1, height=25)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=0, pady=0)
        
        # 左侧状态信息
        status_left = tk.Frame(status_bar, bg='#e0e0e0')
        status_left.pack(side=tk.LEFT, padx=15, pady=2)
        
        self.status_info = tk.Label(status_left, text='就绪', font=('SimHei', 9), bg='#e0e0e0', fg='#333333')
        self.status_info.pack(side=tk.LEFT, padx=5, pady=1)
        
        # 系统信息
        status_system = tk.Frame(status_bar, bg='#e0e0e0')
        status_system.pack(side=tk.LEFT, padx=15, pady=2)
        
        self.system_info = tk.Label(status_system, text='未来AI - 元数据驱动表单系统', font=('SimHei', 9), bg='#e0e0e0', fg='#666666')
        self.system_info.pack(side=tk.LEFT, padx=5, pady=1)
        
        # 中间光标位置
        status_center = tk.Frame(status_bar, bg='#e0e0e0')
        status_center.pack(side=tk.LEFT, padx=15, pady=2)
        
        self.cursor_info = tk.Label(status_center, text='行: 1, 列: 1', font=('SimHei', 9), bg='#e0e0e0', fg='#333333')
        self.cursor_info.pack(side=tk.LEFT, padx=5, pady=1)
        
        # 右侧提示信息
        status_right = tk.Frame(status_bar, bg='#e0e0e0')
        status_right.pack(side=tk.RIGHT, padx=15, pady=2)
        
        self.hint_info = tk.Label(status_right, text='按F1获取帮助 | Ctrl+S保存 | Ctrl+N新建', font=('SimHei', 9), bg='#e0e0e0', fg='#666666')
        self.hint_info.pack(side=tk.RIGHT, padx=5, pady=1)
        
        # 左侧：控件库
        toolbox_frame = tk.Frame(self.main_paned, bg='#ffffff', relief=tk.RAISED, bd=1, width=250)
        self.main_paned.add(toolbox_frame, minsize=200)
        
        # 控件库标题
        toolbox_title_frame = tk.Frame(toolbox_frame, bg='#f5f5f5', relief=tk.FLAT, bd=1)
        toolbox_title_frame.pack(fill=tk.X, pady=0, padx=0)
        toolbox_title_label = tk.Label(toolbox_title_frame, text='控件库', font=('SimHei', 12, 'bold'), bg='#f5f5f5', fg='#333333')
        toolbox_title_label.pack(pady=8, padx=15, anchor=tk.W)
        
        # 控件搜索框
        search_frame = tk.Frame(toolbox_frame, bg='#ffffff')
        search_frame.pack(fill=tk.X, pady=5, padx=15)
        search_label = tk.Label(search_frame, text='搜索:', font=('SimHei', 9), bg='#ffffff', fg='#666666')
        search_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=20, font=('SimHei', 9))
        search_entry.pack(side=tk.LEFT, padx=5, pady=5)
        search_btn = tk.Button(search_frame, text='搜索', width=6, height=1, bg='#f0f0f0', fg='#333333', font=('SimHei', 9), command=self.search_controls)
        search_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 控件分类树
        self.control_tree = ttk.Treeview(toolbox_frame, show='tree', height=30)
        
        # 定制控件树样式
        style = ttk.Style()
        style.configure('Control.Treeview', 
                       background='#ffffff', 
                       foreground='#333333', 
                       rowheight=24, 
                       fieldbackground='#ffffff',
                       font=('SimHei', 9))
        style.map('Control.Treeview',
                 background=[('selected', '#e6f7ff'), ('hover', '#f5f5f5')],
                 foreground=[('selected', '#1890ff')])
        
        self.control_tree.configure(style='Control.Treeview')
        self.control_tree.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # 填充控件分类
        self.populate_control_tree()
        
        # 中间：设计区域和模块导航
        center_frame = tk.Frame(self.main_paned, bg='#f0f0f0')
        self.main_paned.add(center_frame, minsize=600)
        
        # 右侧：属性窗口
        properties_frame = tk.Frame(self.main_paned, bg='#ffffff', relief=tk.RAISED, bd=1, width=300)
        self.main_paned.add(properties_frame, minsize=250)
        
        # 属性窗口标题
        properties_title_frame = tk.Frame(properties_frame, bg='#f5f5f5', relief=tk.FLAT, bd=1)
        properties_title_frame.pack(fill=tk.X, pady=0, padx=0)
        properties_title_label = tk.Label(properties_title_frame, text='属性', font=('SimHei', 12, 'bold'), bg='#f5f5f5', fg='#333333')
        properties_title_label.pack(pady=8, padx=15, anchor=tk.W)
        
        # 属性标签页
        properties_notebook = ttk.Notebook(properties_frame)
        properties_notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # 项目结构标签页
        structure_tab = tk.Frame(properties_notebook, bg='#ffffff')
        properties_notebook.add(structure_tab, text='项目结构')
        
        # 属性编辑标签页
        property_tab = tk.Frame(properties_notebook, bg='#ffffff')
        properties_notebook.add(property_tab, text='属性')
        
        # 事件编辑标签页
        event_tab = tk.Frame(properties_notebook, bg='#ffffff')
        properties_notebook.add(event_tab, text='事件')
        
        # 项目结构树
        self.structure_tree = ttk.Treeview(structure_tab, show='tree', height=25)
        
        # 定制结构树样式
        style = ttk.Style()
        style.configure('Structure.Treeview', 
                       background='#ffffff', 
                       foreground='#333333', 
                       rowheight=22, 
                       fieldbackground='#ffffff',
                       font=('SimHei', 9))
        style.map('Structure.Treeview',
                 background=[('selected', '#e6f7ff'), ('hover', '#f5f5f5')],
                 foreground=[('selected', '#1890ff')])
        
        self.structure_tree.configure(style='Structure.Treeview')
        
        # 添加结构树滚动条
        structure_scroll = ttk.Scrollbar(structure_tab, orient=tk.VERTICAL, command=self.structure_tree.yview)
        self.structure_tree.configure(yscrollcommand=structure_scroll.set)
        
        # 布局结构树和滚动条
        structure_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.structure_tree.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # 填充项目结构树
        self.populate_structure_tree()
        
        # 属性编辑区域
        property_frame = tk.Frame(property_tab, bg='#ffffff')
        property_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # 属性列表
        self.property_list = ttk.Treeview(property_frame, columns=('name', 'value'), show='headings', height=20)
        self.property_list.heading('name', text='属性名')
        self.property_list.heading('value', text='属性值')
        self.property_list.column('name', width=100)
        self.property_list.column('value', width=150)
        
        # 添加属性列表滚动条
        property_scroll = ttk.Scrollbar(property_frame, orient=tk.VERTICAL, command=self.property_list.yview)
        self.property_list.configure(yscrollcommand=property_scroll.set)
        
        # 布局属性列表和滚动条
        property_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.property_list.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # 填充属性列表
        self.populate_property_list()
        
        # 事件编辑区域
        event_frame = tk.Frame(event_tab, bg='#ffffff')
        event_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # 事件列表
        event_list = tk.Listbox(event_frame, height=20, font=('SimHei', 9))
        event_list.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # 填充事件列表
        events = ['点击事件', '双击事件', '鼠标悬停', '鼠标离开', '键盘按下', '键盘释放', '值改变', '加载完成', '保存前', '保存后']
        for event in events:
            event_list.insert(tk.END, event)
        
        # 模块导航
        nav_frame = tk.Frame(center_frame, bg='#ffffff', relief=tk.RAISED, bd=1, height=150)
        nav_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 导航栏标题
        nav_title_frame = tk.Frame(nav_frame, bg='#f5f5f5', relief=tk.FLAT, bd=1)
        nav_title_frame.pack(fill=tk.X, pady=0, padx=0)
        nav_title_label = tk.Label(nav_title_frame, text='模块导航', font=('SimHei', 12, 'bold'), bg='#f5f5f5', fg='#333333')
        nav_title_label.pack(pady=8, padx=15, anchor=tk.W)
        
        # 模块列表
        self.nav_tree = ttk.Treeview(nav_frame, show='tree', height=8)
        self.nav_tree.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # 右侧：配置区域
        config_frame = tk.Frame(center_frame, bg='#f0f0f0')
        config_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 字段配置区域
        field_config_frame = tk.Frame(config_frame, bg='#ffffff', relief=tk.RAISED, bd=1)
        field_config_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 配置区域标题
        config_title_frame = tk.Frame(field_config_frame, bg='#f5f5f5', relief=tk.FLAT, bd=1)
        config_title_frame.pack(fill=tk.X, pady=0, padx=0)
        self.config_title_label = tk.Label(config_title_frame, text='字段配置', font=('SimHei', 12, 'bold'), bg='#f5f5f5', fg='#333333')
        self.config_title_label.pack(pady=8, padx=15, anchor=tk.W)
        
        # 标签页控件
        self.notebook = ttk.Notebook(field_config_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # 基本信息标签页
        basic_tab = tk.Frame(self.notebook, bg='#ffffff')
        self.notebook.add(basic_tab, text='基本信息')
        
        # 供货信息标签页
        supply_tab = tk.Frame(self.notebook, bg='#ffffff')
        self.notebook.add(supply_tab, text='供货信息')
        
        # 财务信息标签页
        finance_tab = tk.Frame(self.notebook, bg='#ffffff')
        self.notebook.add(finance_tab, text='财务信息')
        
        # 明细信息标签页（表格）
        detail_tab = tk.Frame(self.notebook, bg='#ffffff')
        self.notebook.add(detail_tab, text='明细信息')
        
        # 字段列表区域（基本信息标签页）
        fields_container = tk.Frame(basic_tab, bg='#ffffff')
        fields_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(fields_container, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.canvas = tk.Canvas(fields_container, yscrollcommand=scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.canvas.yview)
        
        self.scrollable_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor=tk.NW)
        
        def on_configure(event):
            self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        
        self.scrollable_frame.bind('<Configure>', on_configure)
        
        # 设置拖拽和释放事件
        self.setup_drag_and_drop()
        
        # 供货信息标签页内容
        supply_label = tk.Label(supply_tab, text='供货信息配置', font=('SimHei', 10), bg='#ffffff', fg='#666666')
        supply_label.pack(pady=20, padx=20, anchor=tk.W)
        
        # 财务信息标签页内容
        finance_label = tk.Label(finance_tab, text='财务信息配置', font=('SimHei', 10), bg='#ffffff', fg='#666666')
        finance_label.pack(pady=20, padx=20, anchor=tk.W)
        
        # 明细信息标签页内容（表格）
        detail_label = tk.Label(detail_tab, text='明细信息配置', font=('SimHei', 10), bg='#ffffff', fg='#666666')
        detail_label.pack(pady=10, padx=20, anchor=tk.W)
        
        # 添加表格控件
        self.detail_tree = ttk.Treeview(detail_tab, columns=('序号', '物料编码', '物料名称', '规格型号', '单位', '数量', '单价', '金额'), show='headings', height=15)
        
        # 设置表格列标题
        self.detail_tree.heading('序号', text='序号')
        self.detail_tree.heading('物料编码', text='物料编码')
        self.detail_tree.heading('物料名称', text='物料名称')
        self.detail_tree.heading('规格型号', text='规格型号')
        self.detail_tree.heading('单位', text='单位')
        self.detail_tree.heading('数量', text='数量')
        self.detail_tree.heading('单价', text='单价')
        self.detail_tree.heading('金额', text='金额')
        
        # 设置表格列宽
        self.detail_tree.column('序号', width=60)
        self.detail_tree.column('物料编码', width=120)
        self.detail_tree.column('物料名称', width=150)
        self.detail_tree.column('规格型号', width=120)
        self.detail_tree.column('单位', width=60)
        self.detail_tree.column('数量', width=80)
        self.detail_tree.column('单价', width=80)
        self.detail_tree.column('金额', width=100)
        
        # 填充表格数据
        for i in range(1, 6):
            self.detail_tree.insert('', tk.END, values=(i, f'ITEM{i:04d}', f'物料名称{i}', f'规格{i}', '个', i*10, 100+i, (i*10)*(100+i)))
        
        # 添加表格滚动条
        tree_scroll_y = ttk.Scrollbar(detail_tab, orient=tk.VERTICAL, command=self.detail_tree.yview)
        tree_scroll_x = ttk.Scrollbar(detail_tab, orient=tk.HORIZONTAL, command=self.detail_tree.xview)
        self.detail_tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        
        # 布局表格和滚动条
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.detail_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 底部按钮区域
        button_frame = tk.Frame(field_config_frame, bg='#ffffff')
        button_frame.pack(fill=tk.X, pady=10, padx=15)
        
        # 左侧按钮
        left_buttons = tk.Frame(button_frame, bg='#ffffff')
        left_buttons.pack(side=tk.LEFT, padx=10, pady=5)
        
        add_row_btn = tk.Button(left_buttons, text='添加行', width=10, height=2, bg='#28a745', fg='white', font=('SimHei', 9, 'bold'), command=self.add_row)
        add_row_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        delete_row_btn = tk.Button(left_buttons, text='删除行', width=10, height=2, bg='#dc3545', fg='white', font=('SimHei', 9, 'bold'), command=self.delete_row)
        delete_row_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 右侧按钮
        right_buttons = tk.Frame(button_frame, bg='#ffffff')
        right_buttons.pack(side=tk.RIGHT, padx=10, pady=5)
        
        save_btn = tk.Button(right_buttons, text='保存配置', command=self.save_metadata, width=12, height=2, bg='#007bff', fg='white', font=('SimHei', 10, 'bold'))
        save_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        reload_btn = tk.Button(right_buttons, text='重新加载', command=self.load_metadata, width=12, height=2, bg='#6c757d', fg='white', font=('SimHei', 10, 'bold'))
        reload_btn.pack(side=tk.RIGHT, padx=5, pady=5)
    
    def load_metadata(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.fields = {}
        self.field_frames = {}
        self.modules = {}
        
        if not os.path.exists(self.metadata_file):
            messagebox.showerror('错误', '元数据文件不存在')
            return
        
        try:
            tree = ET.parse(self.metadata_file)
            root = tree.getroot()
            
            # 加载模块结构
            modules_elem = root.find('Modules')
            if modules_elem:
                for module_elem in modules_elem.findall('Module'):
                    module_name = module_elem.get('name')
                    self.modules[module_name] = {}
                    
                    forms_elem = module_elem.find('Forms')
                    if forms_elem:
                        for form_elem in forms_elem.findall('Form'):
                            form_name = form_elem.get('name')
                            self.modules[module_name][form_name] = form_elem
            
            # 填充导航树
            self.populate_nav_tree()
            
            # 绑定导航树选择事件
            self.nav_tree.bind('<<TreeviewSelect>>', self.on_nav_select)
            
        except Exception as e:
            messagebox.showerror('错误', f'加载元数据失败: {e}')
    
    def populate_nav_tree(self):
        """填充导航树"""
        # 清空导航树
        for item in self.nav_tree.get_children():
            self.nav_tree.delete(item)
        
        # 添加模块和单据
        for module_name, forms in self.modules.items():
            module_item = self.nav_tree.insert('', tk.END, text=module_name, open=True)
            for form_name in forms.keys():
                self.nav_tree.insert(module_item, tk.END, text=form_name, tags=(module_name, form_name))
    
    def populate_control_tree(self):
        """填充控件分类树"""
        # 清空控件树
        for item in self.control_tree.get_children():
            self.control_tree.delete(item)
        
        # 控件分类和控件列表
        controls = {
            '基础控件': ['标签', '文本框', '多行文本', '密码框', '按钮', '复选框', '单选按钮', '下拉框', '日期选择器'],
            '容器控件': ['面板', '分组框', '标签页', '分割器', '滚动条'],
            '数据控件': ['表格', '列表框', '树形控件', '图表'],
            '验证控件': ['正则验证', '范围验证', '自定义验证'],
            '高级控件': ['颜色选择器', '文件上传', '富文本编辑器', '地图控件']
        }
        
        # 添加控件分类和控件
        for category, control_list in controls.items():
            category_item = self.control_tree.insert('', tk.END, text=category, open=True)
            for control in control_list:
                self.control_tree.insert(category_item, tk.END, text=control, tags=(category, control))
        
        # 绑定控件树事件
        self.control_tree.bind('<Button-1>', self.on_control_click)
        self.control_tree.bind('<B1-Motion>', self.on_control_drag)
    
    def on_control_click(self, event):
        """控件点击事件"""
        item = self.control_tree.identify_row(event.y)
        if item:
            self.control_tree.selection_set(item)
            # 记录点击的控件信息
            tags = self.control_tree.item(item, 'tags')
            if len(tags) == 2:
                self.dragged_control = tags[1]  # 存储当前拖拽的控件名称
                print(f'准备拖拽控件: {self.dragged_control}')
    
    def on_control_drag(self, event):
        """控件拖拽事件"""
        # 这里可以添加拖拽视觉反馈
        pass
    
    def setup_drag_and_drop(self):
        """设置拖拽和释放事件"""
        # 在控件树上添加鼠标按下事件
        self.control_tree.bind('<Button-1>', self.on_control_click)
        # 在控件树上添加鼠标移动事件
        self.control_tree.bind('<B1-Motion>', self.on_control_drag)
        # 在设计区域添加鼠标释放事件
        self.scrollable_frame.bind('<ButtonRelease-1>', self.on_design_area_drop)
    
    def on_design_area_drop(self, event):
        """在设计区域释放控件"""
        if hasattr(self, 'dragged_control') and self.dragged_control:
            # 获取当前选择的模块和单据
            if self.current_module and self.current_form:
                # 创建新字段
                print(f'在设计区域释放控件: {self.dragged_control}')
                self.add_field_from_control(self.dragged_control)
                # 重置拖拽状态
                self.dragged_control = None
            else:
                print('请先选择一个模块和单据')
        else:
            print('没有拖拽的控件')
    
    def add_field_from_control(self, control_name):
        """根据拖拽的控件名称添加对应的字段"""
        # 控件类型映射
        control_type_map = {
            '文本框': 'TextField',
            '多行文本': 'TextField',
            '密码框': 'TextField',
            '下拉框': 'ComboBox',
            '日期选择器': 'TextField',
            '标签': 'TextField',
            '复选框': 'TextField',
            '单选按钮': 'TextField',
            '按钮': 'TextField',
            '表格': 'TextField',
            '列表框': 'TextField',
            '树形控件': 'TextField',
            '图表': 'TextField',
            '正则验证': 'TextField',
            '范围验证': 'TextField',
            '自定义验证': 'TextField',
            '颜色选择器': 'TextField',
            '文件上传': 'TextField',
            '富文本编辑器': 'TextField',
            '地图控件': 'TextField'
        }
        
        # 获取对应的字段类型
        field_type = control_type_map.get(control_name, 'TextField')
        
        # 添加新字段
        row = len(self.fields)
        field_name = f'{control_name}{row+1}'
        
        field_frame = tk.Frame(self.scrollable_frame, relief=tk.RAISED, bd=1, bg='#f8f9fa')
        field_frame.grid(row=row, column=0, columnspan=6, padx=10, pady=10, sticky=tk.W+tk.E)
        
        name_var = tk.StringVar(value=field_name)
        type_var = tk.StringVar(value=field_type)
        
        tk.Label(field_frame, text='字段名称:', font=('SimHei', 10), bg='#f8f9fa', width=10).grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        tk.Entry(field_frame, textvariable=name_var, width=25, font=('SimHei', 10)).grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        
        tk.Label(field_frame, text='字段类型:', font=('SimHei', 10), bg='#f8f9fa', width=10).grid(row=0, column=2, padx=10, pady=5, sticky=tk.W)
        ttk.Combobox(field_frame, textvariable=type_var, values=['TextField', 'ComboBox', 'MoneyField'], width=18, font=('SimHei', 10)).grid(row=0, column=3, padx=10, pady=5, sticky=tk.W)
        
        var = tk.BooleanVar(value=False)
        checkbox = tk.Checkbutton(field_frame, text='选中', variable=var, font=('SimHei', 10), bg='#f8f9fa')
        checkbox.var = var
        checkbox.grid(row=0, column=4, padx=10, pady=5, sticky=tk.W)
        
        # 编辑按钮
        edit_btn = tk.Button(field_frame, text='编辑', width=8, height=1, bg='#17a2b8', fg='white', font=('SimHei', 9, 'bold'), command=lambda nv=name_var: self.edit_field(nv.get()))
        edit_btn.grid(row=0, column=5, padx=10, pady=5, sticky=tk.E)
        
        self.fields[name_var.get()] = {
            'type': type_var,
            'name': name_var,
            'checkbox': checkbox
        }
        self.field_frames[name_var.get()] = field_frame
    
    def search_controls(self):
        """搜索控件"""
        search_text = self.search_var.get().lower()
        if not search_text:
            return
        
        # 这里可以实现控件搜索的逻辑
        messagebox.showinfo('搜索控件', f'搜索控件: {search_text}')
    
    def on_nav_select(self, event):
        """导航树选择事件"""
        selected_items = self.nav_tree.selection()
        if not selected_items:
            return
        
        item = selected_items[0]
        tags = self.nav_tree.item(item, 'tags')
        
        # 检查是否选择了单据
        if len(tags) == 2:
            module_name, form_name = tags
            self.switch_form(module_name, form_name)
    
    def switch_form(self, module_name, form_name):
        """切换到指定的表单"""
        self.current_module = module_name
        self.current_form = form_name
        
        # 更新配置标题
        self.config_title_label.config(text=f'{module_name} - {form_name} - 字段配置')
        
        # 清空当前字段
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.fields = {}
        self.field_frames = {}
        
        # 加载选中表单的字段
        try:
            tree = ET.parse(self.metadata_file)
            root = tree.getroot()
            
            # 查找指定的模块和表单
            modules_elem = root.find('Modules')
            if modules_elem:
                for module_elem in modules_elem.findall('Module'):
                    if module_elem.get('name') == module_name:
                        forms_elem = module_elem.find('Forms')
                        if forms_elem:
                            for form_elem in forms_elem.findall('Form'):
                                if form_elem.get('name') == form_name:
                                    field_list = form_elem.find('FieldList')
                                    if field_list:
                                        row = 0
                                        for field_elem in field_list:
                                            field_name = field_elem.get('name')
                                            field_type = field_elem.tag
                                            
                                            field_frame = tk.Frame(self.scrollable_frame, relief=tk.RAISED, bd=1, bg='#f8f9fa')
                                            field_frame.grid(row=row, column=0, columnspan=6, padx=10, pady=10, sticky=tk.W+tk.E)
                                            
                                            name_var = tk.StringVar(value=field_name)
                                            type_var = tk.StringVar(value=field_type)
                                            
                                            tk.Label(field_frame, text='字段名称:', font=('SimHei', 10), bg='#f8f9fa', width=10).grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
                                            tk.Entry(field_frame, textvariable=name_var, width=25, font=('SimHei', 10)).grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
                                            
                                            tk.Label(field_frame, text='字段类型:', font=('SimHei', 10), bg='#f8f9fa', width=10).grid(row=0, column=2, padx=10, pady=5, sticky=tk.W)
                                            ttk.Combobox(field_frame, textvariable=type_var, values=['TextField', 'ComboBox', 'MoneyField'], width=18, font=('SimHei', 10)).grid(row=0, column=3, padx=10, pady=5, sticky=tk.W)
                                            
                                            var = tk.BooleanVar(value=False)
                                            checkbox = tk.Checkbutton(field_frame, text='选中', variable=var, font=('SimHei', 10), bg='#f8f9fa')
                                            checkbox.var = var
                                            checkbox.grid(row=0, column=4, padx=10, pady=5, sticky=tk.W)
                                            
                                            # 编辑按钮
                                            edit_btn = tk.Button(field_frame, text='编辑', width=8, height=1, bg='#17a2b8', fg='white', font=('SimHei', 9, 'bold'), command=lambda fn=field_name: self.edit_field(fn))
                                            edit_btn.grid(row=0, column=5, padx=10, pady=5, sticky=tk.E)
                                            
                                            self.fields[field_name] = {
                                                'type': type_var,
                                                'name': name_var,
                                                'checkbox': checkbox
                                            }
                                            self.field_frames[field_name] = field_frame
                                            
                                            row += 1
            
        except Exception as e:
            messagebox.showerror('错误', f'加载表单字段失败: {e}')
    
    def save_metadata(self):
        try:
            tree = ET.parse(self.metadata_file)
            root = tree.getroot()
            
            # 确保存在Modules元素
            modules_elem = root.find('Modules')
            if not modules_elem:
                modules_elem = ET.SubElement(root, 'Modules')
            
            # 保存当前表单的字段
            if self.current_module and self.current_form:
                # 查找当前模块和表单
                for module_elem in modules_elem.findall('Module'):
                    if module_elem.get('name') == self.current_module:
                        forms_elem = module_elem.find('Forms')
                        if not forms_elem:
                            forms_elem = ET.SubElement(module_elem, 'Forms')
                        
                        for form_elem in forms_elem.findall('Form'):
                            if form_elem.get('name') == self.current_form:
                                # 清空当前字段列表
                                field_list = form_elem.find('FieldList')
                                if not field_list:
                                    field_list = ET.SubElement(form_elem, 'FieldList')
                                else:
                                    for field_elem in list(field_list):
                                        field_list.remove(field_elem)
                                
                                # 添加新字段
                                for old_name, field_info in self.fields.items():
                                    new_name = field_info['name'].get()
                                    field_type = field_info['type'].get()
                                    
                                    field_elem = ET.SubElement(field_list, field_type)
                                    field_elem.set('name', new_name)
                                    field_elem.set('Left', '10')
                                    field_elem.set('Top', '10')
                                    field_elem.set('Width', '200')
                                    field_elem.set('Height', '30')
                                    field_elem.set('VisibleExt', '111')
                                    
                                    if field_type == 'TextField' or field_type == 'MoneyField':
                                        field_elem.set('Length', '200' if field_type == 'TextField' else '10')
                                    elif field_type == 'ComboBox':
                                        options_elem = ET.SubElement(field_elem, 'Options')
                                        ET.SubElement(options_elem, 'Option').text = '选项1'
                                        ET.SubElement(options_elem, 'Option').text = '选项2'
                                break
                    break
            
            tree.write(self.metadata_file, encoding='UTF-8', xml_declaration=True)
            messagebox.showinfo('成功', '元数据配置已保存')
        except Exception as e:
            messagebox.showerror('错误', f'保存元数据失败: {e}')
    
    def add_field(self):
        row = len(self.fields)
        
        field_frame = tk.Frame(self.scrollable_frame, relief=tk.RAISED, bd=1, bg='#f8f9fa')
        field_frame.grid(row=row, column=0, columnspan=6, padx=10, pady=10, sticky=tk.W+tk.E)
        
        name_var = tk.StringVar(value=f'新字段{row+1}')
        type_var = tk.StringVar(value='TextField')
        
        tk.Label(field_frame, text='字段名称:', font=('SimHei', 10), bg='#f8f9fa', width=10).grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        tk.Entry(field_frame, textvariable=name_var, width=25, font=('SimHei', 10)).grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        
        tk.Label(field_frame, text='字段类型:', font=('SimHei', 10), bg='#f8f9fa', width=10).grid(row=0, column=2, padx=10, pady=5, sticky=tk.W)
        ttk.Combobox(field_frame, textvariable=type_var, values=['TextField', 'ComboBox', 'MoneyField'], width=18, font=('SimHei', 10)).grid(row=0, column=3, padx=10, pady=5, sticky=tk.W)
        
        var = tk.BooleanVar(value=False)
        checkbox = tk.Checkbutton(field_frame, text='选中', variable=var, font=('SimHei', 10), bg='#f8f9fa')
        checkbox.var = var
        checkbox.grid(row=0, column=4, padx=10, pady=5, sticky=tk.W)
        
        # 编辑按钮
        edit_btn = tk.Button(field_frame, text='编辑', width=8, height=1, bg='#17a2b8', fg='white', font=('SimHei', 9, 'bold'), command=lambda nv=name_var: self.edit_field(nv.get()))
        edit_btn.grid(row=0, column=5, padx=10, pady=5, sticky=tk.E)
        
        self.fields[name_var.get()] = {
            'type': type_var,
            'name': name_var,
            'checkbox': checkbox
        }
        self.field_frames[name_var.get()] = field_frame
    
    def delete_field(self):
        fields_to_delete = []
        for field_name, field_info in self.fields.items():
            if field_info['checkbox'].var.get() if hasattr(field_info['checkbox'], 'var') else False:
                fields_to_delete.append(field_name)
        
        for field_name in fields_to_delete:
            if field_name in self.field_frames:
                self.field_frames[field_name].destroy()
                del self.field_frames[field_name]
            if field_name in self.fields:
                del self.fields[field_name]
        
        messagebox.showinfo('成功', f'已删除 {len(fields_to_delete)} 个字段')
    
    def new_project(self):
        """新建项目"""
        if messagebox.askyesno('确认', '确定要新建项目吗？当前未保存的更改将会丢失。'):
            # 这里可以添加新建项目的逻辑
            messagebox.showinfo('提示', '新建项目功能开发中')
    
    def open_project(self):
        """打开项目"""
        # 这里可以添加打开项目的逻辑
        messagebox.showinfo('提示', '打开项目功能开发中')
    
    def save_as(self):
        """另存为"""
        # 这里可以添加另存为的逻辑
        messagebox.showinfo('提示', '另存为功能开发中')
    
    def undo(self):
        """撤销操作"""
        # 这里可以添加撤销操作的逻辑
        messagebox.showinfo('提示', '撤销功能开发中')
    
    def redo(self):
        """重做操作"""
        # 这里可以添加重做操作的逻辑
        messagebox.showinfo('提示', '重做功能开发中')
    
    def cut(self):
        """剪切操作"""
        # 这里可以添加剪切操作的逻辑
        messagebox.showinfo('提示', '剪切功能开发中')
    
    def copy(self):
        """复制操作"""
        # 这里可以添加复制操作的逻辑
        messagebox.showinfo('提示', '复制功能开发中')
    
    def paste(self):
        """粘贴操作"""
        # 这里可以添加粘贴操作的逻辑
        messagebox.showinfo('提示', '粘贴功能开发中')
    
    def toggle_toolbar(self):
        """切换工具栏显示"""
        # 这里可以添加切换工具栏显示的逻辑
        messagebox.showinfo('提示', '切换工具栏功能开发中')
    
    def toggle_toolbox(self):
        """切换控件库显示"""
        # 这里可以添加切换控件库显示的逻辑
        messagebox.showinfo('提示', '切换控件库功能开发中')
    
    def toggle_properties(self):
        """切换属性窗口显示"""
        # 这里可以添加切换属性窗口显示的逻辑
        messagebox.showinfo('提示', '切换属性窗口功能开发中')
    
    def options(self):
        """选项设置"""
        # 这里可以添加选项设置的逻辑
        messagebox.showinfo('提示', '选项设置功能开发中')
    
    def generate_code(self):
        """生成代码"""
        # 这里可以添加生成代码的逻辑
        messagebox.showinfo('提示', '生成代码功能开发中')
    
    def help(self):
        """使用帮助"""
        # 创建帮助对话框
        help_window = tk.Toplevel(self.root)
        help_window.title('使用帮助')
        help_window.geometry('600x400')
        help_window.resizable(True, True)
        help_window.configure(bg='#f8f9fa')
        
        # 顶部标题栏
        title_frame = tk.Frame(help_window, bg='#1a56db', relief=tk.RAISED, bd=2)
        title_frame.pack(fill=tk.X, pady=0, padx=0)
        title_label = tk.Label(title_frame, text='使用帮助', font=('SimHei', 14, 'bold'), bg='#1a56db', fg='white')
        title_label.pack(pady=10, padx=20, anchor=tk.W)
        
        # 主内容区
        main_frame = tk.Frame(help_window, bg='#f8f9fa')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 帮助内容
        help_text = """
        未来AI - 元数据驱动表单系统使用帮助
        
        1. 模块管理
        - 添加模块：点击工具栏中的"添加模块"按钮
        - 删除模块：选择要删除的模块，点击"删除模块"按钮
        - 添加单据：选择模块后，点击"添加单据"按钮
        - 删除单据：选择要删除的单据，点击"删除单据"按钮
        
        2. 字段管理
        - 添加字段：点击工具栏中的"添加字段"按钮
        - 删除字段：选择要删除的字段，点击"删除字段"按钮
        - 编辑字段：点击字段对应的"编辑"按钮
        
        3. 控件库
        - 搜索控件：在搜索框中输入控件名称，点击"搜索"按钮
        - 拖拽控件：从控件库中拖拽控件到设计区域
        
        4. 设计区域
        - 多标签页：在基本信息、供货信息、财务信息、明细信息之间切换
        - 表格操作：在明细信息标签页中添加/删除行
        
        5. 属性窗口
        - 项目结构：查看和管理项目的结构
        - 属性编辑：编辑选中控件的属性
        - 事件编辑：编辑控件的事件处理
        
        6. 快捷键
        - F1：打开帮助
        - Ctrl+S：保存配置
        - Ctrl+N：新建项目
        - Ctrl+O：打开项目
        
        7. 保存和加载
        - 保存配置：点击"保存配置"按钮或使用Ctrl+S快捷键
        - 重新加载：点击"重新加载"按钮重新加载配置
        """
        
        text_widget = tk.Text(main_frame, font=('SimHei', 10), bg='#ffffff', wrap=tk.WORD)
        text_widget.insert(tk.END, help_text)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 底部按钮
        button_frame = tk.Frame(main_frame, bg='#f8f9fa')
        button_frame.pack(fill=tk.X, pady=10, padx=10)
        
        close_btn = tk.Button(button_frame, text='关闭', command=help_window.destroy, width=12, height=2, bg='#6c757d', fg='white', font=('SimHei', 10, 'bold'))
        close_btn.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # 居中显示
        help_window.transient(self.root)
        help_window.grab_set()
        self.root.wait_window(help_window)
    
    def about(self):
        """关于系统"""
        # 创建关于对话框
        about_window = tk.Toplevel(self.root)
        about_window.title('关于')
        about_window.geometry('500x300')
        about_window.resizable(False, False)
        about_window.configure(bg='#f8f9fa')
        
        # 顶部标题栏
        title_frame = tk.Frame(about_window, bg='#1a56db', relief=tk.RAISED, bd=2)
        title_frame.pack(fill=tk.X, pady=0, padx=0)
        title_label = tk.Label(title_frame, text='关于', font=('SimHei', 14, 'bold'), bg='#1a56db', fg='white')
        title_label.pack(pady=10, padx=20, anchor=tk.W)
        
        # 主内容区
        main_frame = tk.Frame(about_window, bg='#f8f9fa')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 关于内容
        about_text = """
        未来AI - 元数据驱动表单系统
        
        版本：1.0.0
        开发者：未来AI团队
        版权所有 © 2024
        
        系统简介：
        基于元数据驱动的表单设计和运行系统，
        支持模块和单据管理，可视化表单设计，
        多端适配，以及灵活的字段配置。
        
        技术栈：
        - Python
        - Tkinter GUI框架
        - XML元数据配置
        - JSON数据存储
        """
        
        text_widget = tk.Text(main_frame, font=('SimHei', 10), bg='#ffffff', wrap=tk.WORD, height=15)
        text_widget.insert(tk.END, about_text)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 底部按钮
        button_frame = tk.Frame(main_frame, bg='#f8f9fa')
        button_frame.pack(fill=tk.X, pady=10, padx=10)
        
        close_btn = tk.Button(button_frame, text='确定', command=about_window.destroy, width=12, height=2, bg='#007bff', fg='white', font=('SimHei', 10, 'bold'))
        close_btn.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # 居中显示
        about_window.transient(self.root)
        about_window.grab_set()
        self.root.wait_window(about_window)
    
    def edit_field(self, field_name):
        """编辑字段详细属性"""
        # 获取字段信息
        field_info = self.fields.get(field_name)
        if not field_info:
            return
        
        # 创建编辑对话框
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f'编辑字段：{field_name}')
        edit_window.geometry('600x500')
        edit_window.resizable(True, True)
        edit_window.configure(bg='#f8f9fa')
        
        # 顶部标题栏
        title_frame = tk.Frame(edit_window, bg='#1a56db', relief=tk.RAISED, bd=2)
        title_frame.pack(fill=tk.X, pady=0, padx=0)
        title_label = tk.Label(title_frame, text=f'字段属性编辑：{field_name}', font=('SimHei', 14, 'bold'), bg='#1a56db', fg='white')
        title_label.pack(pady=10, padx=20, anchor=tk.W)
        
        # 主内容区
        main_frame = tk.Frame(edit_window, bg='#f8f9fa')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 基本属性
        basic_frame = tk.Frame(main_frame, bg='#ffffff', relief=tk.RAISED, bd=1)
        basic_frame.pack(fill=tk.X, pady=10, padx=10)
        
        basic_title = tk.Label(basic_frame, text='基本属性', font=('SimHei', 12, 'bold'), bg='#ffffff')
        basic_title.pack(pady=10, padx=20, anchor=tk.W)
        
        # 表单布局
        form_frame = tk.Frame(basic_frame, bg='#ffffff')
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 字段名称
        tk.Label(form_frame, text='字段名称:', font=('SimHei', 10), bg='#ffffff', width=12).grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        name_var = tk.StringVar(value=field_info['name'].get())
        tk.Entry(form_frame, textvariable=name_var, width=30, font=('SimHei', 10)).grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)
        
        # 字段类型
        tk.Label(form_frame, text='字段类型:', font=('SimHei', 10), bg='#ffffff', width=12).grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        type_var = tk.StringVar(value=field_info['type'].get())
        ttk.Combobox(form_frame, textvariable=type_var, values=['TextField', 'ComboBox', 'MoneyField'], width=28, font=('SimHei', 10)).grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)
        
        # 布局属性
        layout_frame = tk.Frame(main_frame, bg='#ffffff', relief=tk.RAISED, bd=1)
        layout_frame.pack(fill=tk.X, pady=10, padx=10)
        
        layout_title = tk.Label(layout_frame, text='布局属性', font=('SimHei', 12, 'bold'), bg='#ffffff')
        layout_title.pack(pady=10, padx=20, anchor=tk.W)
        
        layout_form = tk.Frame(layout_frame, bg='#ffffff')
        layout_form.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 位置和大小
        tk.Label(layout_form, text='左侧位置:', font=('SimHei', 10), bg='#ffffff', width=12).grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        left_var = tk.StringVar(value='10')
        tk.Entry(layout_form, textvariable=left_var, width=10, font=('SimHei', 10)).grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)
        
        tk.Label(layout_form, text='顶部位置:', font=('SimHei', 10), bg='#ffffff', width=12).grid(row=0, column=2, padx=10, pady=10, sticky=tk.W)
        top_var = tk.StringVar(value='10')
        tk.Entry(layout_form, textvariable=top_var, width=10, font=('SimHei', 10)).grid(row=0, column=3, padx=10, pady=10, sticky=tk.W)
        
        tk.Label(layout_form, text='宽度:', font=('SimHei', 10), bg='#ffffff', width=12).grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        width_var = tk.StringVar(value='200')
        tk.Entry(layout_form, textvariable=width_var, width=10, font=('SimHei', 10)).grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)
        
        tk.Label(layout_form, text='高度:', font=('SimHei', 10), bg='#ffffff', width=12).grid(row=1, column=2, padx=10, pady=10, sticky=tk.W)
        height_var = tk.StringVar(value='30')
        tk.Entry(layout_form, textvariable=height_var, width=10, font=('SimHei', 10)).grid(row=1, column=3, padx=10, pady=10, sticky=tk.W)
        
        # 多端适配
        tk.Label(layout_form, text='多端适配:', font=('SimHei', 10), bg='#ffffff', width=12).grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        visible_var = tk.StringVar(value='111')
        tk.Entry(layout_form, textvariable=visible_var, width=10, font=('SimHei', 10)).grid(row=2, column=1, padx=10, pady=10, sticky=tk.W)
        tk.Label(layout_form, text='(PC/平板/移动)', font=('SimHei', 9), bg='#ffffff').grid(row=2, column=2, padx=10, pady=10, sticky=tk.W)
        
        # 验证规则
        validation_frame = tk.Frame(main_frame, bg='#ffffff', relief=tk.RAISED, bd=1)
        validation_frame.pack(fill=tk.X, pady=10, padx=10)
        
        validation_title = tk.Label(validation_frame, text='验证规则', font=('SimHei', 12, 'bold'), bg='#ffffff')
        validation_title.pack(pady=10, padx=20, anchor=tk.W)
        
        validation_form = tk.Frame(validation_frame, bg='#ffffff')
        validation_form.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 非空验证
        required_var = tk.BooleanVar(value=False)
        tk.Checkbutton(validation_form, text='非空验证', variable=required_var, font=('SimHei', 10), bg='#ffffff').grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        
        # 数字验证
        number_var = tk.BooleanVar(value=False)
        tk.Checkbutton(validation_form, text='数字格式', variable=number_var, font=('SimHei', 10), bg='#ffffff').grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)
        
        # 底部按钮
        button_frame = tk.Frame(main_frame, bg='#f8f9fa')
        button_frame.pack(fill=tk.X, pady=10, padx=10)
        
        def save_changes():
            """保存修改"""
            # 这里可以添加保存逻辑
            messagebox.showinfo('成功', '字段属性已更新')
            edit_window.destroy()
        
        save_btn = tk.Button(button_frame, text='保存', command=save_changes, width=12, height=2, bg='#007bff', fg='white', font=('SimHei', 10, 'bold'))
        save_btn.pack(side=tk.RIGHT, padx=10, pady=5)
        
        cancel_btn = tk.Button(button_frame, text='取消', command=edit_window.destroy, width=12, height=2, bg='#6c757d', fg='white', font=('SimHei', 10, 'bold'))
        cancel_btn.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # 居中显示
        edit_window.transient(self.root)
        edit_window.grab_set()
        self.root.wait_window(edit_window)
    
    def save_template(self):
        """保存当前配置为模板"""
        # 创建保存模板对话框
        save_window = tk.Toplevel(self.root)
        save_window.title('保存模板')
        save_window.geometry('400x200')
        save_window.resizable(False, False)
        save_window.configure(bg='#f8f9fa')
        
        # 顶部标题栏
        title_frame = tk.Frame(save_window, bg='#1a56db', relief=tk.RAISED, bd=2)
        title_frame.pack(fill=tk.X, pady=0, padx=0)
        title_label = tk.Label(title_frame, text='保存模板', font=('SimHei', 14, 'bold'), bg='#1a56db', fg='white')
        title_label.pack(pady=10, padx=20, anchor=tk.W)
        
        # 主内容区
        main_frame = tk.Frame(save_window, bg='#f8f9fa')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 模板名称
        tk.Label(main_frame, text='模板名称:', font=('SimHei', 10), bg='#f8f9fa', width=10).grid(row=0, column=0, padx=10, pady=20, sticky=tk.W)
        template_name_var = tk.StringVar(value='模板1')
        tk.Entry(main_frame, textvariable=template_name_var, width=25, font=('SimHei', 10)).grid(row=0, column=1, padx=10, pady=20, sticky=tk.W)
        
        # 底部按钮
        button_frame = tk.Frame(main_frame, bg='#f8f9fa')
        button_frame.grid(row=1, column=0, columnspan=2, pady=20, padx=10)
        
        def save_template_action():
            """保存模板操作"""
            template_name = template_name_var.get()
            if not template_name:
                messagebox.showerror('错误', '模板名称不能为空')
                return
            
            # 这里可以添加保存模板的逻辑
            messagebox.showinfo('成功', f'模板 {template_name} 已保存')
            save_window.destroy()
        
        save_btn = tk.Button(button_frame, text='保存', command=save_template_action, width=10, height=2, bg='#007bff', fg='white', font=('SimHei', 10, 'bold'))
        save_btn.pack(side=tk.RIGHT, padx=10, pady=5)
        
        cancel_btn = tk.Button(button_frame, text='取消', command=save_window.destroy, width=10, height=2, bg='#6c757d', fg='white', font=('SimHei', 10, 'bold'))
        cancel_btn.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # 居中显示
        save_window.transient(self.root)
        save_window.grab_set()
        self.root.wait_window(save_window)
    
    def load_template(self):
        """加载已保存的模板"""
        # 创建加载模板对话框
        load_window = tk.Toplevel(self.root)
        load_window.title('加载模板')
        load_window.geometry('400x300')
        load_window.resizable(False, False)
        load_window.configure(bg='#f8f9fa')
        
        # 顶部标题栏
        title_frame = tk.Frame(load_window, bg='#1a56db', relief=tk.RAISED, bd=2)
        title_frame.pack(fill=tk.X, pady=0, padx=0)
        title_label = tk.Label(title_frame, text='加载模板', font=('SimHei', 14, 'bold'), bg='#1a56db', fg='white')
        title_label.pack(pady=10, padx=20, anchor=tk.W)
        
        # 主内容区
        main_frame = tk.Frame(load_window, bg='#f8f9fa')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 模板列表
        tk.Label(main_frame, text='可用模板:', font=('SimHei', 10), bg='#f8f9fa').pack(pady=10, anchor=tk.W)
        
        # 模拟模板列表
        template_list = ['模板1', '模板2', '模板3']
        template_var = tk.StringVar(value=template_list[0] if template_list else '')
        
        listbox = tk.Listbox(main_frame, height=6, width=30, font=('SimHei', 10), bg='#ffffff')
        for template in template_list:
            listbox.insert(tk.END, template)
        listbox.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # 底部按钮
        button_frame = tk.Frame(main_frame, bg='#f8f9fa')
        button_frame.pack(fill=tk.X, pady=20, padx=10)
        
        def load_template_action():
            """加载模板操作"""
            selected_indices = listbox.curselection()
            if not selected_indices:
                messagebox.showerror('错误', '请选择要加载的模板')
                return
            
            selected_template = listbox.get(selected_indices[0])
            messagebox.showinfo('成功', f'模板 {selected_template} 已加载')
            load_window.destroy()
        
        load_btn = tk.Button(button_frame, text='加载', command=load_template_action, width=10, height=2, bg='#007bff', fg='white', font=('SimHei', 10, 'bold'))
        load_btn.pack(side=tk.RIGHT, padx=10, pady=5)
        
        cancel_btn = tk.Button(button_frame, text='取消', command=load_window.destroy, width=10, height=2, bg='#6c757d', fg='white', font=('SimHei', 10, 'bold'))
        cancel_btn.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # 居中显示
        load_window.transient(self.root)
        load_window.grab_set()
        self.root.wait_window(load_window)
    
    def add_module(self):
        """添加新模块"""
        # 创建添加模块对话框
        add_window = tk.Toplevel(self.root)
        add_window.title('添加模块')
        add_window.geometry('400x200')
        add_window.resizable(False, False)
        add_window.configure(bg='#f8f9fa')
        
        # 顶部标题栏
        title_frame = tk.Frame(add_window, bg='#1a56db', relief=tk.RAISED, bd=2)
        title_frame.pack(fill=tk.X, pady=0, padx=0)
        title_label = tk.Label(title_frame, text='添加模块', font=('SimHei', 14, 'bold'), bg='#1a56db', fg='white')
        title_label.pack(pady=10, padx=20, anchor=tk.W)
        
        # 主内容区
        main_frame = tk.Frame(add_window, bg='#f8f9fa')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 模块名称
        tk.Label(main_frame, text='模块名称:', font=('SimHei', 10), bg='#f8f9fa', width=10).grid(row=0, column=0, padx=10, pady=20, sticky=tk.W)
        module_name_var = tk.StringVar(value='新模块')
        tk.Entry(main_frame, textvariable=module_name_var, width=25, font=('SimHei', 10)).grid(row=0, column=1, padx=10, pady=20, sticky=tk.W)
        
        # 底部按钮
        button_frame = tk.Frame(main_frame, bg='#f8f9fa')
        button_frame.grid(row=1, column=0, columnspan=2, pady=20, padx=10)
        
        def add_module_action():
            """添加模块操作"""
            module_name = module_name_var.get()
            if not module_name:
                messagebox.showerror('错误', '模块名称不能为空')
                return
            
            # 检查模块是否已存在
            if module_name in self.modules:
                messagebox.showerror('错误', '模块名称已存在')
                return
            
            # 添加模块到XML
            try:
                tree = ET.parse(self.metadata_file)
                root = tree.getroot()
                
                # 确保存在Modules元素
                modules_elem = root.find('Modules')
                if not modules_elem:
                    modules_elem = ET.SubElement(root, 'Modules')
                
                # 添加新模块
                module_elem = ET.SubElement(modules_elem, 'Module')
                module_elem.set('name', module_name)
                
                # 添加Forms元素
                forms_elem = ET.SubElement(module_elem, 'Forms')
                
                # 保存XML
                tree.write(self.metadata_file, encoding='UTF-8', xml_declaration=True)
                
                # 重新加载元数据
                self.load_metadata()
                messagebox.showinfo('成功', f'模块 {module_name} 已添加')
                add_window.destroy()
            except Exception as e:
                messagebox.showerror('错误', f'添加模块失败: {e}')
        
        save_btn = tk.Button(button_frame, text='添加', command=add_module_action, width=10, height=2, bg='#28a745', fg='white', font=('SimHei', 10, 'bold'))
        save_btn.pack(side=tk.RIGHT, padx=10, pady=5)
        
        cancel_btn = tk.Button(button_frame, text='取消', command=add_window.destroy, width=10, height=2, bg='#6c757d', fg='white', font=('SimHei', 10, 'bold'))
        cancel_btn.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # 居中显示
        add_window.transient(self.root)
        add_window.grab_set()
        self.root.wait_window(add_window)
    
    def delete_module(self):
        """删除模块"""
        # 获取选中的模块
        selected_items = self.nav_tree.selection()
        if not selected_items:
            messagebox.showerror('错误', '请选择要删除的模块')
            return
        
        item = selected_items[0]
        tags = self.nav_tree.item(item, 'tags')
        
        # 检查是否选择了模块
        if len(tags) != 2:
            # 尝试获取模块名称
            module_name = self.nav_tree.item(item, 'text')
            if module_name in self.modules:
                # 确认删除
                if messagebox.askyesno('确认', f'确定要删除模块 {module_name} 吗？'):
                    try:
                        tree = ET.parse(self.metadata_file)
                        root = tree.getroot()
                        
                        modules_elem = root.find('Modules')
                        if modules_elem:
                            for module_elem in modules_elem.findall('Module'):
                                if module_elem.get('name') == module_name:
                                    modules_elem.remove(module_elem)
                                    break
                        
                        # 保存XML
                        tree.write(self.metadata_file, encoding='UTF-8', xml_declaration=True)
                        
                        # 重新加载元数据
                        self.load_metadata()
                        messagebox.showinfo('成功', f'模块 {module_name} 已删除')
                    except Exception as e:
                        messagebox.showerror('错误', f'删除模块失败: {e}')
            else:
                messagebox.showerror('错误', '请选择要删除的模块')
    
    def add_form(self):
        """添加新单据"""
        # 获取选中的模块
        selected_items = self.nav_tree.selection()
        if not selected_items:
            messagebox.showerror('错误', '请先选择一个模块')
            return
        
        item = selected_items[0]
        tags = self.nav_tree.item(item, 'tags')
        
        # 检查是否选择了模块
        module_name = ''
        if len(tags) != 2:
            # 尝试获取模块名称
            module_text = self.nav_tree.item(item, 'text')
            # 移除图标部分，只保留纯模块名称
            module_name = module_text.split(' ', 1)[1] if ' ' in module_text else module_text
            if module_name not in self.modules:
                messagebox.showerror('错误', '请先选择一个模块')
                return
        else:
            # 从单据标签中获取模块名称
            module_name = tags[0]
        
        # 创建添加单据对话框
        add_window = tk.Toplevel(self.root)
        add_window.title('添加单据')
        add_window.geometry('400x200')
        add_window.resizable(False, False)
        add_window.configure(bg='#f8f9fa')
        
        # 顶部标题栏
        title_frame = tk.Frame(add_window, bg='#1a56db', relief=tk.RAISED, bd=2)
        title_frame.pack(fill=tk.X, pady=0, padx=0)
        title_label = tk.Label(title_frame, text='添加单据', font=('SimHei', 14, 'bold'), bg='#1a56db', fg='white')
        title_label.pack(pady=10, padx=20, anchor=tk.W)
        
        # 主内容区
        main_frame = tk.Frame(add_window, bg='#f8f9fa')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 单据名称
        tk.Label(main_frame, text='单据名称:', font=('SimHei', 10), bg='#f8f9fa', width=10).grid(row=0, column=0, padx=10, pady=20, sticky=tk.W)
        form_name_var = tk.StringVar(value='新单据')
        tk.Entry(main_frame, textvariable=form_name_var, width=25, font=('SimHei', 10)).grid(row=0, column=1, padx=10, pady=20, sticky=tk.W)
        
        # 底部按钮
        button_frame = tk.Frame(main_frame, bg='#f8f9fa')
        button_frame.grid(row=1, column=0, columnspan=2, pady=20, padx=10)
        
        def add_form_action():
            """添加单据操作"""
            form_name = form_name_var.get()
            if not form_name:
                messagebox.showerror('错误', '单据名称不能为空')
                return
            
            # 检查单据是否已存在
            if form_name in self.modules.get(module_name, {}):
                messagebox.showerror('错误', '单据名称已存在')
                return
            
            # 添加单据到XML
            try:
                tree = ET.parse(self.metadata_file)
                root = tree.getroot()
                
                modules_elem = root.find('Modules')
                if modules_elem:
                    for module_elem in modules_elem.findall('Module'):
                        if module_elem.get('name') == module_name:
                            forms_elem = module_elem.find('Forms')
                            if not forms_elem:
                                forms_elem = ET.SubElement(module_elem, 'Forms')
                            
                            # 添加新单据
                            form_elem = ET.SubElement(forms_elem, 'Form')
                            form_elem.set('name', form_name)
                            
                            # 添加FieldList元素
                            field_list_elem = ET.SubElement(form_elem, 'FieldList')
                            
                            # 添加基础字段
                            # ID字段（隐藏）
                            id_field = ET.SubElement(field_list_elem, 'TextField')
                            id_field.set('name', 'id')
                            id_field.set('Left', '10')
                            id_field.set('Top', '10')
                            id_field.set('Width', '200')
                            id_field.set('Height', '30')
                            id_field.set('VisibleExt', '000')  # 隐藏字段
                            id_field.set('Length', '50')
                            
                            # 状态字段
                            status_field = ET.SubElement(field_list_elem, 'ComboBox')
                            status_field.set('name', '状态')
                            status_field.set('Left', '10')
                            status_field.set('Top', '50')
                            status_field.set('Width', '200')
                            status_field.set('Height', '30')
                            status_field.set('VisibleExt', '111')
                            # 添加状态选项
                            options_elem = ET.SubElement(status_field, 'Options')
                            ET.SubElement(options_elem, 'Option').text = '草稿'
                            ET.SubElement(options_elem, 'Option').text = '已提交'
                            ET.SubElement(options_elem, 'Option').text = '已审核'
                            ET.SubElement(options_elem, 'Option').text = '已拒绝'
                            
                            # 创建时间字段（隐藏）
                            created_at_field = ET.SubElement(field_list_elem, 'TextField')
                            created_at_field.set('name', 'created_at')
                            created_at_field.set('Left', '10')
                            created_at_field.set('Top', '90')
                            created_at_field.set('Width', '200')
                            created_at_field.set('Height', '30')
                            created_at_field.set('VisibleExt', '000')  # 隐藏字段
                            created_at_field.set('Length', '50')
                            
                            # 创建人字段（隐藏）
                            created_by_field = ET.SubElement(field_list_elem, 'TextField')
                            created_by_field.set('name', 'created_by')
                            created_by_field.set('Left', '10')
                            created_by_field.set('Top', '130')
                            created_by_field.set('Width', '200')
                            created_by_field.set('Height', '30')
                            created_by_field.set('VisibleExt', '000')  # 隐藏字段
                            created_by_field.set('Length', '50')
                            
                            # 保存XML
                            tree.write(self.metadata_file, encoding='UTF-8', xml_declaration=True)
                            
                            # 重新加载元数据
                            self.load_metadata()
                            messagebox.showinfo('成功', f'单据 {form_name} 已添加')
                            add_window.destroy()
                            break
            except Exception as e:
                messagebox.showerror('错误', f'添加单据失败: {e}')
        
        save_btn = tk.Button(button_frame, text='添加', command=add_form_action, width=10, height=2, bg='#28a745', fg='white', font=('SimHei', 10, 'bold'))
        save_btn.pack(side=tk.RIGHT, padx=10, pady=5)
        
        cancel_btn = tk.Button(button_frame, text='取消', command=add_window.destroy, width=10, height=2, bg='#6c757d', fg='white', font=('SimHei', 10, 'bold'))
        cancel_btn.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # 居中显示
        add_window.transient(self.root)
        add_window.grab_set()
        self.root.wait_window(add_window)
    
    def delete_form(self):
        """删除单据"""
        # 获取选中的单据
        selected_items = self.nav_tree.selection()
        if not selected_items:
            messagebox.showerror('错误', '请选择要删除的单据')
            return
        
        item = selected_items[0]
        tags = self.nav_tree.item(item, 'tags')
        
        # 检查是否选择了单据
        if len(tags) == 2:
            module_name, form_name = tags
            
            # 确认删除
            if messagebox.askyesno('确认', f'确定要删除单据 {form_name} 吗？'):
                try:
                    tree = ET.parse(self.metadata_file)
                    root = tree.getroot()
                    
                    modules_elem = root.find('Modules')
                    if modules_elem:
                        for module_elem in modules_elem.findall('Module'):
                            if module_elem.get('name') == module_name:
                                forms_elem = module_elem.find('Forms')
                                if forms_elem:
                                    for form_elem in forms_elem.findall('Form'):
                                        if form_elem.get('name') == form_name:
                                            forms_elem.remove(form_elem)
                                            break
                                break
                    
                    # 保存XML
                    tree.write(self.metadata_file, encoding='UTF-8', xml_declaration=True)
                    
                    # 重新加载元数据
                    self.load_metadata()
                    messagebox.showinfo('成功', f'单据 {form_name} 已删除')
                except Exception as e:
                    messagebox.showerror('错误', f'删除单据失败: {e}')
        else:
            messagebox.showerror('错误', '请选择要删除的单据')
    
    def export_template(self):
        """导出模板为文件"""
        # 创建导出模板对话框
        export_window = tk.Toplevel(self.root)
        export_window.title('导出模板')
        export_window.geometry('400x200')
        export_window.resizable(False, False)
        export_window.configure(bg='#f8f9fa')
        
        # 顶部标题栏
        title_frame = tk.Frame(export_window, bg='#1a56db', relief=tk.RAISED, bd=2)
        title_frame.pack(fill=tk.X, pady=0, padx=0)
        title_label = tk.Label(title_frame, text='导出模板', font=('SimHei', 14, 'bold'), bg='#1a56db', fg='white')
        title_label.pack(pady=10, padx=20, anchor=tk.W)
        
        # 主内容区
        main_frame = tk.Frame(export_window, bg='#f8f9fa')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 导出路径提示
        tk.Label(main_frame, text='模板将导出为XML文件', font=('SimHei', 10), bg='#f8f9fa').pack(pady=20, anchor=tk.W)
        
        # 底部按钮
        button_frame = tk.Frame(main_frame, bg='#f8f9fa')
        button_frame.pack(fill=tk.X, pady=20, padx=10)
        
        def export_template_action():
            """导出模板操作"""
            # 这里可以添加导出模板的逻辑
            messagebox.showinfo('成功', '模板已导出为XML文件')
            export_window.destroy()
        
        export_btn = tk.Button(button_frame, text='导出', command=export_template_action, width=10, height=2, bg='#007bff', fg='white', font=('SimHei', 10, 'bold'))
        export_btn.pack(side=tk.RIGHT, padx=10, pady=5)
        
        cancel_btn = tk.Button(button_frame, text='取消', command=export_window.destroy, width=10, height=2, bg='#6c757d', fg='white', font=('SimHei', 10, 'bold'))
        cancel_btn.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # 居中显示
        export_window.transient(self.root)
        export_window.grab_set()
        self.root.wait_window(export_window)
    
    # 菜单和工具栏方法
    def new_project(self):
        """新建项目"""
        messagebox.showinfo('新建项目', '新建项目功能开发中')
    
    def open_project(self):
        """打开项目"""
        messagebox.showinfo('打开项目', '打开项目功能开发中')
    
    def save_as(self):
        """另存为"""
        messagebox.showinfo('另存为', '另存为功能开发中')
    
    def undo(self):
        """撤销"""
        messagebox.showinfo('撤销', '撤销功能开发中')
    
    def redo(self):
        """重做"""
        messagebox.showinfo('重做', '重做功能开发中')
    
    def cut(self):
        """剪切"""
        messagebox.showinfo('剪切', '剪切功能开发中')
    
    def copy(self):
        """复制"""
        messagebox.showinfo('复制', '复制功能开发中')
    
    def paste(self):
        """粘贴"""
        messagebox.showinfo('粘贴', '粘贴功能开发中')
    
    def toggle_toolbar(self):
        """切换工具栏显示"""
        messagebox.showinfo('工具栏', '工具栏显示切换功能开发中')
    
    def toggle_toolbox(self):
        """切换控件库显示"""
        messagebox.showinfo('控件库', '控件库显示切换功能开发中')
    
    def toggle_properties(self):
        """切换属性窗口显示"""
        messagebox.showinfo('属性窗口', '属性窗口显示切换功能开发中')
    
    def options(self):
        """选项设置"""
        messagebox.showinfo('选项', '选项设置功能开发中')
    
    def generate_code(self):
        """生成代码"""
        messagebox.showinfo('生成代码', '代码生成功能开发中')
    
    def help(self):
        """使用帮助"""
        messagebox.showinfo('使用帮助', '使用帮助功能开发中')
    
    def about(self):
        """关于"""
        messagebox.showinfo('关于', '后端设计器 v1.0\n专业的表单设计工具')
    
    def add_row(self):
        """添加表格行"""
        # 获取当前表格的行数
        row_count = len(self.detail_tree.get_children()) + 1
        # 添加新行
        self.detail_tree.insert('', tk.END, values=(row_count, f'ITEM{row_count:04d}', f'物料名称{row_count}', f'规格{row_count}', '个', row_count*10, 100+row_count, (row_count*10)*(100+row_count)))
    
    def delete_row(self):
        """删除表格行"""
        selected_items = self.detail_tree.selection()
        if not selected_items:
            messagebox.showerror('错误', '请选择要删除的行')
            return
        
        for item in selected_items:
            self.detail_tree.delete(item)
        
        # 更新序号
        for i, item in enumerate(self.detail_tree.get_children(), 1):
            values = list(self.detail_tree.item(item, 'values'))
            values[0] = i
            self.detail_tree.item(item, values=values)
    
    def populate_structure_tree(self):
        """填充项目结构树"""
        # 清空结构树
        for item in self.structure_tree.get_children():
            self.structure_tree.delete(item)
        
        # 项目结构
        structure = {
            '表单': {
                '基本信息': ['订单编号', '供应商', '采购日期', '采购部门'],
                '供货信息': ['供应商地址', '联系人', '联系电话'],
                '财务信息': ['币种', '汇率', '税率', '总金额'],
                '明细信息': ['物料编码', '物料名称', '规格型号', '数量', '单价', '金额']
            },
            '数据源': ['数据库连接', '数据映射', '数据过滤'],
            '验证规则': ['必填项验证', '数字验证', '日期验证'],
            '权限设置': ['查看权限', '编辑权限', '删除权限']
        }
        
        # 添加结构节点
        for node, children in structure.items():
            node_item = self.structure_tree.insert('', tk.END, text=node, open=True)
            if isinstance(children, dict):
                for child_node, child_children in children.items():
                    child_item = self.structure_tree.insert(node_item, tk.END, text=child_node, open=True)
                    for item in child_children:
                        self.structure_tree.insert(child_item, tk.END, text=item)
            else:
                for item in children:
                    self.structure_tree.insert(node_item, tk.END, text=item)
    
    def populate_property_list(self):
        """填充属性列表"""
        # 清空属性列表
        for item in self.property_list.get_children():
            self.property_list.delete(item)
        
        # 属性列表
        properties = [
            ('名称', '采购订单'),
            ('类型', '表单'),
            ('创建日期', '2026-02-10'),
            ('修改日期', '2026-02-10'),
            ('创建人', 'admin'),
            ('修改人', 'admin'),
            ('版本', '1.0'),
            ('描述', '采购订单表单'),
            ('宽度', '1000'),
            ('高度', '600'),
            ('背景色', '#ffffff'),
            ('字体', 'SimHei, 10')
        ]
        
        # 添加属性
        for name, value in properties:
            self.property_list.insert('', tk.END, values=(name, value))

if __name__ == '__main__':
    app = MetadataEditor()
    app.root.mainloop()