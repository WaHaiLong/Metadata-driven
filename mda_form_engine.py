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
        self.load_metadata()
    
    def load_metadata(self):
        tree = ET.parse(self.metadata_file)
        root = tree.getroot()
        form = root.find('Form')
        self.form_name = form.get('name')
        field_list = form.find('FieldList')
        
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
            if validation:
                field_info['validation'] = {}
                if validation.find('Required') is not None:
                    field_info['validation']['required'] = validation.find('Required').text == '1'
                if validation.find('Number') is not None:
                    field_info['validation']['number'] = validation.find('Number').text == '1'
            
            self.fields[field_name] = field_info
    
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
        
        with open('form_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        messagebox.showinfo('保存成功', '表单数据已保存')
    
    def load_data(self):
        if os.path.exists('form_data.json'):
            try:
                with open('form_data.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for field_name, value in data.items():
                    widget = self.field_widgets.get(field_name)
                    if widget:
                        if hasattr(widget, 'delete') and hasattr(widget, 'insert'):
                            widget.delete(0, tk.END)
                            widget.insert(0, value)
                        elif hasattr(widget, 'set'):
                            widget.set(value)
                
                messagebox.showinfo('加载成功', '历史数据已加载')
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
        self.root.geometry('800x600')
        self.root.resizable(True, True)
        
        # 设置ERP风格的颜色和字体
        self.root.configure(bg='#f8f9fa')
        
        # 顶部标题栏
        title_frame = tk.Frame(self.root, bg='#1a56db', relief=tk.RAISED, bd=2)
        title_frame.pack(fill=tk.X, pady=0, padx=0)
        title_label = tk.Label(title_frame, text=self.form_name, font=('SimHei', 16, 'bold'), bg='#1a56db', fg='white')
        title_label.pack(pady=10, padx=20, anchor=tk.W)
        
        # 工具栏
        toolbar_frame = tk.Frame(self.root, bg='#e9ecef', relief=tk.RAISED, bd=1)
        toolbar_frame.pack(fill=tk.X, pady=0, padx=0)
        
        toolbar_label = tk.Label(toolbar_frame, text='操作', font=('SimHei', 10, 'bold'), bg='#e9ecef')
        toolbar_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # 主内容区
        main_frame = tk.Frame(self.root, bg='#f8f9fa')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 表单区域
        form_container = tk.Frame(main_frame, bg='#ffffff', relief=tk.RAISED, bd=1)
        form_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 表单标题
        form_title_frame = tk.Frame(form_container, bg='#f8f9fa', relief=tk.FLAT, bd=1)
        form_title_frame.pack(fill=tk.X, pady=10, padx=10)
        form_title_label = tk.Label(form_title_frame, text='表单信息', font=('SimHei', 12, 'bold'), bg='#f8f9fa')
        form_title_label.pack(pady=5, padx=10, anchor=tk.W)
        
        # 字段容器
        self.form_frame = tk.Frame(form_container, bg='#ffffff')
        self.form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
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
            label_frame = tk.Frame(self.form_frame, bg='#ffffff')
            label_frame.grid(row=row, column=col*2, padx=10, pady=10, sticky=tk.W)
            label = tk.Label(label_frame, text=field_name, font=('SimHei', 10), bg='#ffffff', anchor=tk.W, width=15)
            label.pack(pady=2, anchor=tk.W)
            
            # 字段输入控件
            input_frame = tk.Frame(self.form_frame, bg='#ffffff')
            input_frame.grid(row=row, column=col*2+1, padx=10, pady=10, sticky=tk.W)
            
            if field_info['type'] == 'TextField':
                if field_info['height'] > 30:
                    text_widget = tk.Text(input_frame, wrap=tk.WORD, width=30, height=4, font=('SimHei', 10))
                    text_widget.pack(pady=2)
                    text_widget.bind('<KeyRelease>', lambda e, w=text_widget, l=field_info['length']: self.limit_text(w, l))
                    self.field_widgets[field_name] = text_widget
                else:
                    entry = tk.Entry(input_frame, width=30, font=('SimHei', 10))
                    entry.pack(pady=2)
                    entry.bind('<KeyRelease>', lambda e, w=entry, l=field_info['length']: self.limit_text(w, l))
                    self.field_widgets[field_name] = entry
            elif field_info['type'] == 'ComboBox':
                combobox = ttk.Combobox(input_frame, values=field_info['options'], width=28, font=('SimHei', 10))
                combobox.pack(pady=2)
                self.field_widgets[field_name] = combobox
            elif field_info['type'] == 'MoneyField':
                entry = tk.Entry(input_frame, width=30, font=('SimHei', 10))
                entry.pack(pady=2)
                self.field_widgets[field_name] = entry
            
            field_count += 1
        
        # 底部按钮区域
        button_frame = tk.Frame(main_frame, bg='#f8f9fa')
        button_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # 左侧按钮
        left_buttons = tk.Frame(button_frame, bg='#f8f9fa')
        left_buttons.pack(side=tk.LEFT, padx=10, pady=5)
        
        save_btn = tk.Button(left_buttons, text='保存', command=self.save_data, width=12, height=2, bg='#007bff', fg='white', font=('SimHei', 10, 'bold'))
        save_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        load_btn = tk.Button(left_buttons, text='加载', command=self.load_data, width=12, height=2, bg='#6c757d', fg='white', font=('SimHei', 10, 'bold'))
        load_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        reset_btn = tk.Button(left_buttons, text='重置', command=self.reset_form, width=12, height=2, bg='#dc3545', fg='white', font=('SimHei', 10, 'bold'))
        reset_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 右侧按钮
        right_buttons = tk.Frame(button_frame, bg='#f8f9fa')
        right_buttons.pack(side=tk.RIGHT, padx=10, pady=5)
        
        submit_btn = tk.Button(right_buttons, text='提交', command=self.validate_form, width=12, height=2, bg='#28a745', fg='white', font=('SimHei', 10, 'bold'))
        submit_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
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

if __name__ == '__main__':
    engine = MDAFormEngine('erp_form_metadata.xml')
    engine.run()