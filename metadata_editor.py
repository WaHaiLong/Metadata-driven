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
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        title_frame = tk.Frame(main_frame, bg='#f0f0f0', relief=tk.RAISED, bd=2)
        title_frame.pack(fill=tk.X, pady=10)
        title_label = tk.Label(title_frame, text='元数据配置编辑器', font=('SimHei', 14, 'bold'), bg='#f0f0f0')
        title_label.pack(pady=5, padx=10, anchor=tk.W)
        
        self.fields_frame = tk.Frame(main_frame)
        self.fields_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(self.fields_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.canvas = tk.Canvas(self.fields_frame, yscrollcommand=scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.canvas.yview)
        
        self.scrollable_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor=tk.NW)
        
        def on_configure(event):
            self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        
        self.scrollable_frame.bind('<Configure>', on_configure)
        
        button_frame = tk.Frame(main_frame, bg='#f0f0f0', relief=tk.SUNKEN, bd=2)
        button_frame.pack(fill=tk.X, pady=10)
        
        save_btn = tk.Button(button_frame, text='保存配置', command=self.save_metadata, width=12)
        save_btn.pack(side=tk.LEFT, padx=10, pady=5)
        
        reload_btn = tk.Button(button_frame, text='重新加载', command=self.load_metadata, width=12)
        reload_btn.pack(side=tk.LEFT, padx=10, pady=5)
        
        add_btn = tk.Button(button_frame, text='添加字段', command=self.add_field, width=12)
        add_btn.pack(side=tk.LEFT, padx=10, pady=5)
        
        delete_btn = tk.Button(button_frame, text='删除字段', command=self.delete_field, width=12)
        delete_btn.pack(side=tk.LEFT, padx=10, pady=5)
    
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
                
                field_frame = tk.Frame(self.scrollable_frame, relief=tk.RAISED, bd=1, bg='#e0e0e0')
                field_frame.grid(row=row, column=0, columnspan=5, padx=5, pady=5, sticky=tk.W+tk.E)
                
                name_var = tk.StringVar(value=field_name)
                type_var = tk.StringVar(value=field_type)
                
                tk.Label(field_frame, text='字段名称:', width=10).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
                tk.Entry(field_frame, textvariable=name_var, width=20).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
                
                tk.Label(field_frame, text='字段类型:', width=10).grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
                ttk.Combobox(field_frame, textvariable=type_var, values=['TextField', 'ComboBox', 'MoneyField'], width=15).grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
                
                var = tk.BooleanVar(value=False)
                checkbox = tk.Checkbutton(field_frame, text='选中', variable=var)
                checkbox.var = var
                checkbox.grid(row=0, column=4, padx=5, pady=5, sticky=tk.E)
                
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
        
        field_frame = tk.Frame(self.scrollable_frame, relief=tk.RAISED, bd=1, bg='#e0e0e0')
        field_frame.grid(row=row, column=0, columnspan=5, padx=5, pady=5, sticky=tk.W+tk.E)
        
        name_var = tk.StringVar(value=f'新字段{row+1}')
        type_var = tk.StringVar(value='TextField')
        
        tk.Label(field_frame, text='字段名称:', width=10).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        tk.Entry(field_frame, textvariable=name_var, width=20).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        tk.Label(field_frame, text='字段类型:', width=10).grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        ttk.Combobox(field_frame, textvariable=type_var, values=['TextField', 'ComboBox', 'MoneyField'], width=15).grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        
        var = tk.BooleanVar(value=False)
        checkbox = tk.Checkbutton(field_frame, text='选中', variable=var)
        checkbox.var = var
        checkbox.grid(row=0, column=4, padx=5, pady=5, sticky=tk.E)
        
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

if __name__ == '__main__':
    root = tk.Tk()
    app = MetadataEditor(root)
    root.mainloop()