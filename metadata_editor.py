import tkinter as tk
from tkinter import ttk, messagebox
import xml.etree.ElementTree as ET
import os

class MetadataEditor:
    def __init__(self, root):
        self.root = root
        self.root.title('元数据编辑器')
        self.root.geometry('800x600')
        
        self.metadata_file = 'erp_form_metadata.xml'
        self.fields = {}
        self.field_frames = {}
        
        self.create_widgets()
        self.load_metadata()
    
    def create_widgets(self):
        # 设置ERP风格的颜色和字体
        self.root.configure(bg='#f8f9fa')
        
        # 顶部标题栏
        title_frame = tk.Frame(self.root, bg='#1a56db', relief=tk.RAISED, bd=2)
        title_frame.pack(fill=tk.X, pady=0, padx=0)
        title_label = tk.Label(title_frame, text='元数据配置编辑器', font=('SimHei', 16, 'bold'), bg='#1a56db', fg='white')
        title_label.pack(pady=10, padx=20, anchor=tk.W)
        
        # 工具栏
        toolbar_frame = tk.Frame(self.root, bg='#e9ecef', relief=tk.RAISED, bd=1)
        toolbar_frame.pack(fill=tk.X, pady=0, padx=0)
        
        # 配置操作
        toolbar_label = tk.Label(toolbar_frame, text='配置操作', font=('SimHei', 10, 'bold'), bg='#e9ecef')
        toolbar_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # 模板管理
        template_label = tk.Label(toolbar_frame, text='模板管理', font=('SimHei', 10, 'bold'), bg='#e9ecef')
        template_label.pack(side=tk.LEFT, padx=20, pady=5)
        
        # 模板按钮
        save_template_btn = tk.Button(toolbar_frame, text='保存模板', command=self.save_template, width=10, height=1, bg='#ffc107', fg='black', font=('SimHei', 9, 'bold'))
        save_template_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        load_template_btn = tk.Button(toolbar_frame, text='加载模板', command=self.load_template, width=10, height=1, bg='#ffc107', fg='black', font=('SimHei', 9, 'bold'))
        load_template_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        export_template_btn = tk.Button(toolbar_frame, text='导出模板', command=self.export_template, width=10, height=1, bg='#ffc107', fg='black', font=('SimHei', 9, 'bold'))
        export_template_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 主内容区
        main_frame = tk.Frame(self.root, bg='#f8f9fa')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 左侧：字段配置区域
        config_frame = tk.Frame(main_frame, bg='#ffffff', relief=tk.RAISED, bd=1)
        config_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 配置区域标题
        config_title_frame = tk.Frame(config_frame, bg='#f8f9fa', relief=tk.FLAT, bd=1)
        config_title_frame.pack(fill=tk.X, pady=10, padx=10)
        config_title_label = tk.Label(config_title_frame, text='字段配置', font=('SimHei', 12, 'bold'), bg='#f8f9fa')
        config_title_label.pack(pady=5, padx=10, anchor=tk.W)
        
        # 字段列表区域
        fields_container = tk.Frame(config_frame, bg='#ffffff')
        fields_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
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
        
        # 底部按钮区域
        button_frame = tk.Frame(main_frame, bg='#f8f9fa')
        button_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # 左侧按钮
        left_buttons = tk.Frame(button_frame, bg='#f8f9fa')
        left_buttons.pack(side=tk.LEFT, padx=10, pady=5)
        
        save_btn = tk.Button(left_buttons, text='保存配置', command=self.save_metadata, width=12, height=2, bg='#007bff', fg='white', font=('SimHei', 10, 'bold'))
        save_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        reload_btn = tk.Button(left_buttons, text='重新加载', command=self.load_metadata, width=12, height=2, bg='#6c757d', fg='white', font=('SimHei', 10, 'bold'))
        reload_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 右侧按钮
        right_buttons = tk.Frame(button_frame, bg='#f8f9fa')
        right_buttons.pack(side=tk.RIGHT, padx=10, pady=5)
        
        add_btn = tk.Button(right_buttons, text='添加字段', command=self.add_field, width=12, height=2, bg='#28a745', fg='white', font=('SimHei', 10, 'bold'))
        add_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        delete_btn = tk.Button(right_buttons, text='删除字段', command=self.delete_field, width=12, height=2, bg='#dc3545', fg='white', font=('SimHei', 10, 'bold'))
        delete_btn.pack(side=tk.RIGHT, padx=5, pady=5)
    
    def load_metadata(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.fields = {}
        self.field_frames = {}
        
        if not os.path.exists(self.metadata_file):
            messagebox.showerror('错误', '元数据文件不存在')
            return
        
        try:
            tree = ET.parse(self.metadata_file)
            root = tree.getroot()
            form = root.find('Form')
            field_list = form.find('FieldList')
            
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
            messagebox.showerror('错误', f'加载元数据失败: {e}')
    
    def save_metadata(self):
        try:
            tree = ET.parse(self.metadata_file)
            root = tree.getroot()
            form = root.find('Form')
            field_list = form.find('FieldList')
            
            for field_elem in list(field_list):
                field_list.remove(field_elem)
            
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

if __name__ == '__main__':
    root = tk.Tk()
    app = MetadataEditor(root)
    root.mainloop()