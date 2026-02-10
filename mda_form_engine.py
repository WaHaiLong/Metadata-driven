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
        if modules_elem is not None:
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
            if forms_elem is not None:
                for form_elem in forms_elem.findall('Form'):
                    form_name = form_elem.get('name')
                    self.modules[module_name][form_name] = {
                        'fields': {}
                    }
                    
                    field_list = form_elem.find('FieldList')
                    if field_list is not None:
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
                    
                    # 加载明细表格配置
                    detail_table = form_elem.find('DetailTable')
                    if detail_table is not None:
                        self.modules[module_name][form_name]['detail_columns'] = []
                        for column_elem in detail_table.findall('Column'):
                            column_info = {
                                'name': column_elem.get('name'),
                                'width': int(column_elem.get('width', 100)),
                                'type': column_elem.get('type', 'TextField')
                            }
                            self.modules[module_name][form_name]['detail_columns'].append(column_info)
    
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
        """验证表单数据"""
        errors = []
        
        # 验证主表数据
        for field_name, field_info in self.fields.items():
            if not self.is_visible(field_info['visible_ext']):
                continue
            
            widget = self.field_widgets.get(field_name)
            if not widget:
                continue
            
            # 获取字段值
            if hasattr(widget, 'get'):
                if widget.cget('class') == 'Text':
                    value = widget.get('1.0', tk.END).strip()
                else:
                    value = widget.get()
                    if isinstance(value, str):
                        value = value.strip()
            else:
                value = ''
            
            # 验证规则
            validation = field_info.get('validation', {})
            
            # 非空验证
            if validation.get('required'):
                if not value:
                    errors.append(f'{field_name} 不能为空')
            
            # 数字验证
            if validation.get('number'):
                if value:
                    try:
                        float(value)
                    except ValueError:
                        errors.append(f'{field_name} 必须是数字')
            
            # 长度验证
            if field_info.get('length'):
                max_length = field_info['length']
                if len(value) > max_length:
                    errors.append(f'{field_name} 长度不能超过 {max_length} 个字符')
            
            # 自定义验证规则
            custom_error = self.custom_validation(field_name, value, field_info)
            if custom_error:
                errors.append(custom_error)
        
        # 验证明细数据
        if hasattr(self, 'detail_tree') and self.detail_tree:
            detail_errors = self.validate_detail_data()
            errors.extend(detail_errors)
        
        # 显示验证结果
        if errors:
            error_message = '\n'.join(errors)
            messagebox.showerror('验证错误', f'请检查以下错误：\n\n{error_message}')
            return False
        else:
            messagebox.showinfo('验证成功', '表单验证通过')
            return True
    
    def validate_detail_data(self):
        """验证明细数据"""
        errors = []
        if not hasattr(self, 'detail_tree') or not self.detail_tree:
            return errors
        
        # 获取明细列配置
        if self.current_module and self.current_form:
            form_config = self.modules.get(self.current_module, {}).get(self.current_form, {})
            detail_columns = form_config.get('detail_columns', [])
            if detail_columns:
                # 检查是否有数据
                if not self.detail_tree.get_children():
                    errors.append('明细表格不能为空')
                    return errors
                
                # 验证每一行数据
                for i, item in enumerate(self.detail_tree.get_children()):
                    values = self.detail_tree.item(item, 'values')
                    row_num = i + 1
                    
                    # 验证必填字段
                    for j, col in enumerate(detail_columns):
                        if j < len(values):
                            value = values[j]
                            # 这里可以根据列类型添加验证规则
                            # 例如：物料编码和物料名称为必填
                            if col['name'] in ['物料编码', '物料名称']:
                                if not value:
                                    errors.append(f'明细行 {row_num}：{col["name"]} 不能为空')
                            # 验证数字字段
                            if col['name'] in ['数量', '单价', '金额']:
                                if value:
                                    try:
                                        float(value)
                                    except ValueError:
                                        errors.append(f'明细行 {row_num}：{col["name"]} 必须是数字')
        
        return errors
    
    def calculate_detail_amounts(self):
        """计算明细数据的金额"""
        if hasattr(self, 'detail_tree') and self.detail_tree:
            # 获取明细列配置
            if self.current_module and self.current_form:
                form_config = self.modules.get(self.current_module, {}).get(self.current_form, {})
                detail_columns = form_config.get('detail_columns', [])
                if detail_columns:
                    # 查找数量、单价、金额列的索引
                    quantity_idx = -1
                    price_idx = -1
                    amount_idx = -1
                    
                    for i, col in enumerate(detail_columns):
                        if col['name'] == '数量':
                            quantity_idx = i
                        elif col['name'] == '单价':
                            price_idx = i
                        elif col['name'] == '金额':
                            amount_idx = i
                    
                    # 计算金额
                    if quantity_idx != -1 and price_idx != -1 and amount_idx != -1:
                        total_amount = 0
                        for item in self.detail_tree.get_children():
                            values = list(self.detail_tree.item(item, 'values'))
                            try:
                                quantity = float(values[quantity_idx]) if values[quantity_idx] else 0
                                price = float(values[price_idx]) if values[price_idx] else 0
                                amount = quantity * price
                                values[amount_idx] = round(amount, 2)
                                total_amount += amount
                                # 更新金额字段
                                self.detail_tree.item(item, values=values)
                            except:
                                pass
                        
                        # 可以在这里更新表头的总计金额
                        return total_amount
        
        return 0
    
    def custom_validation(self, field_name, value, field_info):
        """自定义验证规则"""
        # 这里可以添加自定义的验证规则
        # 例如：邮箱格式验证、手机号验证等
        
        # 示例：如果字段名包含"邮箱"，验证邮箱格式
        if '邮箱' in field_name or 'email' in field_name.lower():
            if value and '@' not in value:
                return f'{field_name} 格式不正确，必须包含 @ 符号'
        
        # 示例：如果字段名包含"手机"，验证手机号格式
        if '手机' in field_name or 'phone' in field_name.lower():
            if value and (len(value) != 11 or not value.isdigit()):
                return f'{field_name} 格式不正确，必须是11位数字'
        
        return None
    
    def save_data(self):
        data = {}
        for field_name, widget in self.field_widgets.items():
            if hasattr(widget, 'get'):
                value = widget.get()
                if isinstance(value, str):
                    value = value.strip()
                data[field_name] = value
        
        # 添加明细数据
        if hasattr(self, 'detail_tree') and self.detail_tree:
            detail_data = []
            for item in self.detail_tree.get_children():
                values = self.detail_tree.item(item, 'values')
                if values:
                    # 获取明细列配置
                    if self.current_module and self.current_form:
                        form_config = self.modules.get(self.current_module, {}).get(self.current_form, {})
                        detail_columns = form_config.get('detail_columns', [])
                        if detail_columns:
                            row_data = {}
                            for i, column in enumerate(detail_columns):
                                if i < len(values):
                                    row_data[column['name']] = values[i]
                            detail_data.append(row_data)
            data['details'] = detail_data
        
        # 为每个单据创建独立的数据文件
        if self.current_module and self.current_form:
            filename = f'data_{self.current_module}_{self.current_form}.json'
        else:
            filename = 'form_data.json'
        
        # 检查是否有ID字段，判断是新增还是更新
        record_id = data.get('id')
        
        # 加载现有数据
        records = self.get_records(filename)
        
        if record_id:
            # 更新现有记录
            updated = False
            for i, record in enumerate(records):
                if record.get('id') == record_id:
                    records[i] = data
                    updated = True
                    break
            if not updated:
                # 如果没找到记录，添加为新记录
                records.append(data)
            message = '记录已更新'
        else:
            # 新增记录，生成唯一ID
            import time
            import random
            new_id = f'{int(time.time())}{random.randint(1000, 9999)}'
            data['id'] = new_id
            data['created_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
            records.append(data)
            message = '记录已添加'
        
        # 保存数据
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        
        # 只在GUI环境中显示消息框
        if hasattr(self, 'root') and self.root is not None:
            messagebox.showinfo('操作成功', message)
        
        # 刷新数据列表
        self.refresh_data_list()
        
        # 保存成功后显示数据列表
        # 不再隐藏字段区域，让数据列表正常显示
        # if hasattr(self, 'fields_frame'):
        #     self.fields_frame.pack_forget()
    
    def load_data(self, record_id=None):
        # 为每个单据创建独立的数据文件
        if self.current_module and self.current_form:
            filename = f'data_{self.current_module}_{self.current_form}.json'
        else:
            filename = 'form_data.json'
        
        if os.path.exists(filename):
            try:
                if record_id:
                    # 加载特定记录
                    record = self.get_record_by_id(filename, record_id)
                    if record:
                        for field_name, value in record.items():
                            # 跳过明细数据，单独处理
                            if field_name == 'details':
                                continue
                            widget = self.field_widgets.get(field_name)
                            if widget:
                                if hasattr(widget, 'delete') and hasattr(widget, 'insert'):
                                    widget.delete(0, tk.END)
                                    widget.insert(0, value)
                                elif hasattr(widget, 'set'):
                                    widget.set(value)
                        
                        # 加载明细数据
                        detail_data = record.get('details', [])
                        if detail_data and hasattr(self, 'detail_tree') and self.detail_tree:
                            # 清空现有明细数据
                            for item in self.detail_tree.get_children():
                                self.detail_tree.delete(item)
                            # 添加明细数据
                            for i, detail_row in enumerate(detail_data):
                                # 获取明细列配置
                                form_config = self.modules.get(self.current_module, {}).get(self.current_form, {})
                                detail_columns = form_config.get('detail_columns', [])
                                if detail_columns:
                                    values = []
                                    for column in detail_columns:
                                        values.append(detail_row.get(column['name'], ''))
                                    # 插入明细行
                                    self.detail_tree.insert('', tk.END, values=values)
                        
                        messagebox.showinfo('加载成功', '记录数据已加载')
                    else:
                        messagebox.showerror('加载错误', '记录不存在')
                else:
                    # 加载数据列表
                    self.refresh_data_list()
            except Exception as e:
                messagebox.showerror('加载错误', f'加载数据失败: {e}')
        else:
            # 首次使用，显示空列表
            self.refresh_data_list()
    
    def get_records(self, filename):
        """获取记录列表"""
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    records = json.load(f)
                # 确保返回的是列表
                if isinstance(records, list):
                    return records
                else:
                    # 兼容旧格式，将单个对象转换为列表
                    return [records]
            except:
                return []
        else:
            return []
    
    def get_record_by_id(self, filename, record_id):
        """根据ID获取记录"""
        records = self.get_records(filename)
        for record in records:
            if record.get('id') == record_id:
                return record
        return None
    
    def refresh_data_list(self):
        """刷新数据列表"""
        if self.current_module and self.current_form:
            # 只有在UI初始化后才更新界面
            if hasattr(self, 'root') and self.root is not None:
                # 显示加载状态
                if hasattr(self, 'form_title_label'):
                    original_text = self.form_title_label.cget('text')
                    self.form_title_label.config(text=f'{original_text} - 加载中...')
                    self.root.update()  # 强制更新界面
                
                # 清空fields_frame并重新渲染表格
                if hasattr(self, 'fields_frame'):
                    # 清空现有内容
                    for widget in self.fields_frame.winfo_children():
                        widget.destroy()
                    
                    # 加载并显示实际数据列表
                    filename = f'data_{self.current_module}_{self.current_form}.json'
                    records = self.get_records(filename)
                    
                    if records:
                        # 显示数据列表
                        self.render_table(records)
                    else:
                        # 显示空数据提示
                        empty_data = [{'提示': '暂无数据，请点击新增按钮添加记录'}]
                        self.render_table(empty_data)
                
                # 恢复原始标题
                if hasattr(self, 'form_title_label'):
                    self.form_title_label.config(text=f'{self.current_form}信息')
    
    def delete_record(self, record_id):
        """删除记录"""
        if not record_id:
            messagebox.showerror('错误', '请选择要删除的记录')
            return
        
        # 为每个单据创建独立的数据文件
        if self.current_module and self.current_form:
            filename = f'data_{self.current_module}_{self.current_form}.json'
        else:
            filename = 'form_data.json'
        
        if os.path.exists(filename):
            try:
                # 加载现有数据
                records = self.get_records(filename)
                
                # 找到并删除记录
                original_count = len(records)
                records = [record for record in records if record.get('id') != record_id]
                
                if len(records) < original_count:
                    # 保存数据
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(records, f, ensure_ascii=False, indent=2)
                    
                    messagebox.showinfo('操作成功', '记录已删除')
                    # 刷新数据列表
                    self.refresh_data_list()
                else:
                    messagebox.showerror('错误', '记录不存在')
            except Exception as e:
                messagebox.showerror('错误', f'删除记录失败: {e}')
        else:
            messagebox.showerror('错误', '数据文件不存在')
    
    def add_record(self):
        """添加新记录"""
        # 重置表单，准备添加新记录
        self.reset_form()
        # 清空fields_frame并显示字段编辑区域
        if hasattr(self, 'fields_frame'):
            # 清空现有内容
            for widget in self.fields_frame.winfo_children():
                widget.destroy()
            
            # 创建字段容器
            fields_container = tk.Frame(self.fields_frame, bg='#ffffff')
            fields_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # 为每个字段创建一行
            for field_name, field_info in self.fields.items():
                if not self.is_visible(field_info['visible_ext']):
                    continue
                
                # 创建行框架
                field_row = tk.Frame(fields_container, bg='#ffffff')
                field_row.pack(fill=tk.X, pady=8, padx=10)
                
                # 字段标签
                label_frame = tk.Frame(field_row, bg='#ffffff')
                label_frame.pack(side=tk.LEFT, padx=10, pady=2, fill=tk.Y)
                label = tk.Label(label_frame, text=field_name, font=('SimHei', 10), bg='#ffffff', anchor=tk.W, width=15, fg='#333333')
                label.pack(pady=2, anchor=tk.W)
                
                # 字段输入控件
                input_frame = tk.Frame(field_row, bg='#ffffff')
                input_frame.pack(side=tk.LEFT, padx=10, pady=2, fill=tk.Y, expand=True)
                
                if field_info['type'] == 'TextField':
                    if field_info['height'] > 30:
                        text_widget = tk.Text(input_frame, wrap=tk.WORD, width=50, height=4, font=('SimHei', 10), relief=tk.SOLID, bd=1, bg='#ffffff')
                        text_widget.pack(pady=2, fill=tk.X, expand=True)
                        text_widget.bind('<KeyRelease>', lambda e, w=text_widget, l=field_info['length']: self.limit_text(w, l))
                        self.field_widgets[field_name] = text_widget
                    else:
                        entry = tk.Entry(input_frame, width=50, font=('SimHei', 10), relief=tk.SOLID, bd=1, bg='#ffffff')
                        entry.pack(pady=2, fill=tk.X, expand=True)
                        entry.bind('<KeyRelease>', lambda e, w=entry, l=field_info['length']: self.limit_text(w, l))
                        self.field_widgets[field_name] = entry
                elif field_info['type'] == 'ComboBox':
                    combobox = ttk.Combobox(input_frame, values=field_info['options'], width=48, font=('SimHei', 10))
                    combobox.pack(pady=2, fill=tk.X, expand=True)
                    self.field_widgets[field_name] = combobox
                elif field_info['type'] == 'MoneyField':
                    entry = tk.Entry(input_frame, width=50, font=('SimHei', 10), relief=tk.SOLID, bd=1, bg='#ffffff')
                    entry.pack(pady=2, fill=tk.X, expand=True)
                    self.field_widgets[field_name] = entry
            
            # 添加明细表格
            if self.current_module and self.current_form:
                form_config = self.modules.get(self.current_module, {}).get(self.current_form, {})
                detail_columns = form_config.get('detail_columns', [])
                if detail_columns:
                    # 创建明细表格区域
                    detail_frame = tk.Frame(fields_container, bg='#ffffff', relief=tk.RAISED, bd=1)
                    detail_frame.pack(fill=tk.BOTH, expand=True, pady=15, padx=10)
                    
                    # 明细表格标题
                    detail_title = tk.Label(detail_frame, text='明细信息', font=('SimHei', 12, 'bold'), bg='#ffffff', fg='#333333')
                    detail_title.pack(pady=10, padx=10, anchor=tk.W)
                    
                    # 创建明细表格
                    columns = [col['name'] for col in detail_columns]
                    self.detail_tree = ttk.Treeview(detail_frame, columns=columns, show='headings', height=10)
                    
                    # 设置表格列
                    for i, col in enumerate(detail_columns):
                        self.detail_tree.heading(col['name'], text=col['name'])
                        self.detail_tree.column(col['name'], width=col['width'])
                    
                    # 添加滚动条
                    scrollbar_y = ttk.Scrollbar(detail_frame, orient=tk.VERTICAL, command=self.detail_tree.yview)
                    scrollbar_x = ttk.Scrollbar(detail_frame, orient=tk.HORIZONTAL, command=self.detail_tree.xview)
                    self.detail_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
                    
                    # 布局表格和滚动条
                    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
                    scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
                    self.detail_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                    
                    # 明细表格操作按钮
                    detail_buttons = tk.Frame(detail_frame, bg='#ffffff')
                    detail_buttons.pack(fill=tk.X, pady=10, padx=10)
                    
                    add_row_btn = tk.Button(detail_buttons, text='添加行', command=self.add_detail_row, width=10, height=1, bg='#28a745', fg='white', font=('SimHei', 9, 'bold'))
                    add_row_btn.pack(side=tk.LEFT, padx=5, pady=5)
                    
                    delete_row_btn = tk.Button(detail_buttons, text='删除行', command=self.delete_detail_row, width=10, height=1, bg='#dc3545', fg='white', font=('SimHei', 9, 'bold'))
                    delete_row_btn.pack(side=tk.LEFT, padx=5, pady=5)
                    
                    calculate_btn = tk.Button(detail_buttons, text='计算金额', command=self.calculate_detail_amounts, width=10, height=1, bg='#17a2b8', fg='white', font=('SimHei', 9, 'bold'))
                    calculate_btn.pack(side=tk.LEFT, padx=5, pady=5)
            
            # 显示字段区域
            self.fields_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    def update_record(self, record_id):
        """更新现有记录"""
        # 加载记录数据到表单
        self.load_data(record_id)
    
    def reset_form(self):
        for widget in self.field_widgets.values():
            if hasattr(widget, 'delete') and hasattr(widget, 'insert'):
                widget.delete(0, tk.END)
            elif hasattr(widget, 'set'):
                widget.set('')
        messagebox.showinfo('重置成功', '表单已重置，可添加新记录')
    
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
        
        new_btn = tk.Button(left_actions, text='新增', command=self.add_record, width=8, height=1, bg='#1890ff', fg='white', font=('SimHei', 9, 'bold'))
        new_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        edit_btn = tk.Button(left_actions, text='修改', command=self.edit_selected_record, width=8, height=1, bg='#1890ff', fg='white', font=('SimHei', 9, 'bold'))
        edit_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        delete_btn = tk.Button(left_actions, text='删除', command=self.delete_selected_record, width=8, height=1, bg='#ff4d4f', fg='white', font=('SimHei', 9, 'bold'))
        delete_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 右侧操作按钮
        right_actions = tk.Frame(action_frame, bg='#ffffff')
        right_actions.pack(side=tk.RIGHT, padx=10, pady=5)
        
        refresh_btn = tk.Button(right_actions, text='刷新', command=self.refresh_data_list, width=8, height=1, bg='#f0f0f0', fg='#333333', font=('SimHei', 9, 'bold'))
        refresh_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        
        export_btn = tk.Button(right_actions, text='导出', command=self.export_data, width=8, height=1, bg='#f0f0f0', fg='#333333', font=('SimHei', 9, 'bold'))
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
        
        # 只有在UI初始化后才更新界面
        if hasattr(self, 'root') and self.root is not None:
            # 更新标题
            self.root.title(f"{module_name} - {form_name}")
            if hasattr(self, 'form_title_label'):
                self.form_title_label.config(text=f"{form_name}信息")
            
            # 清空现有字段控件
            if hasattr(self, 'fields_frame'):
                for widget in self.fields_frame.winfo_children():
                    widget.destroy()
            self.field_widgets.clear()
            
            # 加载并显示实际数据列表
            filename = f'data_{self.current_module}_{self.current_form}.json'
            records = self.get_records(filename)
            
            if records:
                # 显示数据列表
                self.render_table(records)
            else:
                # 显示空数据提示
                empty_data = [{'提示': '暂无数据，请点击新增按钮添加记录'}]
                self.render_table(empty_data)
            
            # 先渲染字段（默认不显示）
            self.render_fields()
            # 隐藏字段编辑区域，但保持表格显示
            # 注意：不再隐藏整个fields_frame，因为表格也在其中
            # 而是在点击编辑时再显示字段编辑区域
    
    def render_fields(self):
        """渲染字段"""
        # 只有在UI初始化后才渲染字段
        if hasattr(self, 'fields_frame'):
            # 注意：不再清空现有内容，因为表格也在fields_frame中
            # 而是在需要编辑时再显示字段编辑区域
            pass
    
    def render_table(self, data):
        """渲染表格数据"""
        # 只有在UI初始化后才渲染表格
        if hasattr(self, 'fields_frame'):
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
                self.table = ttk.Treeview(table_frame, 
                                    columns=columns, 
                                    show='headings', 
                                    yscrollcommand=scrollbar_y.set, 
                                    xscrollcommand=scrollbar_x.set)
                
                # 配置滚动条
                scrollbar_y.config(command=self.table.yview)
                scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
                
                scrollbar_x.config(command=self.table.xview)
                scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
                
                # 设置列标题
                for col in columns:
                    self.table.heading(col, text=col)
                    self.table.column(col, width=120, anchor=tk.CENTER)
                
                # 填充数据
                for row in data:
                    # 存储ID作为item的tags
                    item_id = row.get('id', '')
                    self.table.insert('', tk.END, values=list(row.values()), tags=(item_id,))
                
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
                
                # 添加交替行颜色
                style.configure('Custom.Treeview.Row',
                               background=[('odd', '#ffffff'), ('even', '#f9f9f9')])
                
                self.table.configure(style='Custom.Treeview')
                self.table.pack(fill=tk.BOTH, expand=True)
                
                # 绑定表格点击事件
                self.table.bind('<ButtonRelease-1>', self.on_table_click)
                # 绑定表格双击事件，支持双击编辑
                self.table.bind('<Double-1>', self.on_table_double_click)
                
                # 表格操作按钮
                table_buttons_frame = tk.Frame(self.fields_frame, bg='#ffffff')
                table_buttons_frame.pack(fill=tk.X, padx=10, pady=10)
                
                # 左侧按钮
                left_buttons = tk.Frame(table_buttons_frame, bg='#ffffff')
                left_buttons.pack(side=tk.LEFT, padx=10, pady=5)
                
                refresh_btn = tk.Button(left_buttons, text='刷新', command=self.refresh_data_list, width=8, height=1, bg='#1890ff', fg='white', font=('SimHei', 9, 'bold'))
                refresh_btn.pack(side=tk.LEFT, padx=5, pady=5)
                
                # 右侧按钮
                right_buttons = tk.Frame(table_buttons_frame, bg='#ffffff')
                right_buttons.pack(side=tk.RIGHT, padx=10, pady=5)
                
                edit_btn = tk.Button(right_buttons, text='编辑选中', command=self.edit_selected_record, width=10, height=1, bg='#1890ff', fg='white', font=('SimHei', 9, 'bold'))
                edit_btn.pack(side=tk.RIGHT, padx=5, pady=5)
                
                delete_btn = tk.Button(right_buttons, text='删除选中', command=self.delete_selected_record, width=10, height=1, bg='#ff4d4f', fg='white', font=('SimHei', 9, 'bold'))
                delete_btn.pack(side=tk.RIGHT, padx=5, pady=5)
                
                # 分页控件
                pagination_frame = tk.Frame(self.fields_frame, bg='#ffffff')
                pagination_frame.pack(fill=tk.X, padx=10, pady=10)
                
                total_records = len(data)
                page_info = tk.Label(pagination_frame, text=f'共 {total_records} 条记录，第 1/1 页', font=('SimHei', 9), bg='#ffffff', fg='#666666')
                page_info.pack(side=tk.LEFT, padx=10, pady=5)
                
                page_buttons = tk.Frame(pagination_frame, bg='#ffffff')
                page_buttons.pack(side=tk.RIGHT, padx=10, pady=5)
                
                first_btn = tk.Button(page_buttons, text='首页', width=6, height=1, bg='#f0f0f0', fg='#333333', font=('SimHei', 9), state=tk.DISABLED)
                first_btn.pack(side=tk.LEFT, padx=5, pady=5)
                
                prev_btn = tk.Button(page_buttons, text='上一页', width=6, height=1, bg='#f0f0f0', fg='#333333', font=('SimHei', 9), state=tk.DISABLED)
                prev_btn.pack(side=tk.LEFT, padx=5, pady=5)
                
                next_btn = tk.Button(page_buttons, text='下一页', width=6, height=1, bg='#f0f0f0', fg='#333333', font=('SimHei', 9), state=tk.DISABLED)
                next_btn.pack(side=tk.LEFT, padx=5, pady=5)
                
                last_btn = tk.Button(page_buttons, text='末页', width=6, height=1, bg='#f0f0f0', fg='#333333', font=('SimHei', 9), state=tk.DISABLED)
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
        current_text = widget.get('1.0', tk.END) if hasattr(widget, 'get') and widget.winfo_class() == 'Text' else widget.get()
        if len(current_text) > max_length:
            if hasattr(widget, 'delete'):
                if widget.winfo_class() == 'Text':
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
    
    def on_table_click(self, event):
        """表格点击事件"""
        # 这里可以添加表格点击的处理逻辑
        pass
    
    def on_table_double_click(self, event):
        """表格双击事件，支持双击编辑"""
        selected_items = self.table.selection()
        if selected_items:
            self.edit_selected_record()
    
    def edit_selected_record(self):
        """编辑选中的记录"""
        selected_items = self.table.selection()
        if not selected_items:
            messagebox.showinfo('提示', '请选择要编辑的记录')
            return
        
        item = selected_items[0]
        # 获取记录ID
        tags = self.table.item(item, 'tags')
        if tags:
            record_id = tags[0]
            if record_id:
                # 清空fields_frame并显示字段编辑区域
                if hasattr(self, 'fields_frame'):
                    # 清空现有内容
                    for widget in self.fields_frame.winfo_children():
                        widget.destroy()
                    
                    # 创建字段容器
                    fields_container = tk.Frame(self.fields_frame, bg='#ffffff')
                    fields_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                    
                    # 为每个字段创建一行
                    for field_name, field_info in self.fields.items():
                        if not self.is_visible(field_info['visible_ext']):
                            continue
                        
                        # 创建行框架
                        field_row = tk.Frame(fields_container, bg='#ffffff')
                        field_row.pack(fill=tk.X, pady=8, padx=10)
                        
                        # 字段标签
                        label_frame = tk.Frame(field_row, bg='#ffffff')
                        label_frame.pack(side=tk.LEFT, padx=10, pady=2, fill=tk.Y)
                        label = tk.Label(label_frame, text=field_name, font=('SimHei', 10), bg='#ffffff', anchor=tk.W, width=15, fg='#333333')
                        label.pack(pady=2, anchor=tk.W)
                        
                        # 字段输入控件
                        input_frame = tk.Frame(field_row, bg='#ffffff')
                        input_frame.pack(side=tk.LEFT, padx=10, pady=2, fill=tk.Y, expand=True)
                        
                        if field_info['type'] == 'TextField':
                            if field_info['height'] > 30:
                                text_widget = tk.Text(input_frame, wrap=tk.WORD, width=50, height=4, font=('SimHei', 10), relief=tk.SOLID, bd=1, bg='#ffffff')
                                text_widget.pack(pady=2, fill=tk.X, expand=True)
                                text_widget.bind('<KeyRelease>', lambda e, w=text_widget, l=field_info['length']: self.limit_text(w, l))
                                self.field_widgets[field_name] = text_widget
                            else:
                                entry = tk.Entry(input_frame, width=50, font=('SimHei', 10), relief=tk.SOLID, bd=1, bg='#ffffff')
                                entry.pack(pady=2, fill=tk.X, expand=True)
                                entry.bind('<KeyRelease>', lambda e, w=entry, l=field_info['length']: self.limit_text(w, l))
                                self.field_widgets[field_name] = entry
                        elif field_info['type'] == 'ComboBox':
                            combobox = ttk.Combobox(input_frame, values=field_info['options'], width=48, font=('SimHei', 10))
                            combobox.pack(pady=2, fill=tk.X, expand=True)
                            self.field_widgets[field_name] = combobox
                        elif field_info['type'] == 'MoneyField':
                            entry = tk.Entry(input_frame, width=50, font=('SimHei', 10), relief=tk.SOLID, bd=1, bg='#ffffff')
                            entry.pack(pady=2, fill=tk.X, expand=True)
                            self.field_widgets[field_name] = entry
                    
                    # 添加明细表格
                    if self.current_module and self.current_form:
                        form_config = self.modules.get(self.current_module, {}).get(self.current_form, {})
                        detail_columns = form_config.get('detail_columns', [])
                        if detail_columns:
                            # 创建明细表格区域
                            detail_frame = tk.Frame(fields_container, bg='#ffffff', relief=tk.RAISED, bd=1)
                            detail_frame.pack(fill=tk.BOTH, expand=True, pady=15, padx=10)
                            
                            # 明细表格标题
                            detail_title = tk.Label(detail_frame, text='明细信息', font=('SimHei', 12, 'bold'), bg='#ffffff', fg='#333333')
                            detail_title.pack(pady=10, padx=10, anchor=tk.W)
                            
                            # 创建明细表格
                            columns = [col['name'] for col in detail_columns]
                            self.detail_tree = ttk.Treeview(detail_frame, columns=columns, show='headings', height=10)
                            
                            # 设置表格列
                            for i, col in enumerate(detail_columns):
                                self.detail_tree.heading(col['name'], text=col['name'])
                                self.detail_tree.column(col['name'], width=col['width'])
                            
                            # 添加滚动条
                            scrollbar_y = ttk.Scrollbar(detail_frame, orient=tk.VERTICAL, command=self.detail_tree.yview)
                            scrollbar_x = ttk.Scrollbar(detail_frame, orient=tk.HORIZONTAL, command=self.detail_tree.xview)
                            self.detail_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
                            
                            # 布局表格和滚动条
                            scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
                            scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
                            self.detail_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                            
                            # 明细表格操作按钮
                            detail_buttons = tk.Frame(detail_frame, bg='#ffffff')
                            detail_buttons.pack(fill=tk.X, pady=10, padx=10)
                            
                            add_row_btn = tk.Button(detail_buttons, text='添加行', command=self.add_detail_row, width=10, height=1, bg='#28a745', fg='white', font=('SimHei', 9, 'bold'))
                            add_row_btn.pack(side=tk.LEFT, padx=5, pady=5)
                            
                            delete_row_btn = tk.Button(detail_buttons, text='删除行', command=self.delete_detail_row, width=10, height=1, bg='#dc3545', fg='white', font=('SimHei', 9, 'bold'))
                            delete_row_btn.pack(side=tk.LEFT, padx=5, pady=5)
                    
                    # 显示字段区域
                    self.fields_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
                # 加载记录数据
                self.load_data(record_id)
            else:
                messagebox.showinfo('提示', '该记录无法编辑')
    
    def delete_selected_record(self):
        """删除选中的记录"""
        selected_items = self.table.selection()
        if not selected_items:
            messagebox.showinfo('提示', '请选择要删除的记录')
            return
        
        item = selected_items[0]
        # 获取记录ID
        tags = self.table.item(item, 'tags')
        if tags:
            record_id = tags[0]
            if record_id:
                if messagebox.askyesno('确认', '确定要删除这条记录吗？'):
                    self.delete_record(record_id)
            else:
                messagebox.showinfo('提示', '该记录无法删除')
    
    def add_detail_row(self):
        """在明细表格中添加新行"""
        if hasattr(self, 'detail_tree') and self.detail_tree:
            # 获取明细列配置
            if self.current_module and self.current_form:
                form_config = self.modules.get(self.current_module, {}).get(self.current_form, {})
                detail_columns = form_config.get('detail_columns', [])
                if detail_columns:
                    # 创建空行数据
                    values = [''] * len(detail_columns)
                    # 插入新行
                    self.detail_tree.insert('', tk.END, values=values)
                    messagebox.showinfo('成功', '已添加新行')
    
    def delete_detail_row(self):
        """删除明细表格中选中的行"""
        if hasattr(self, 'detail_tree') and self.detail_tree:
            selected_items = self.detail_tree.selection()
            if selected_items:
                for item in selected_items:
                    self.detail_tree.delete(item)
                messagebox.showinfo('成功', '已删除选中的行')
            else:
                messagebox.showinfo('提示', '请选择要删除的行')
    
    def export_data(self):
        """导出数据"""
        # 为每个单据创建独立的数据文件
        if self.current_module and self.current_form:
            filename = f'data_{self.current_module}_{self.current_form}.json'
        else:
            filename = 'form_data.json'
        
        if os.path.exists(filename):
            try:
                # 加载数据
                records = self.get_records(filename)
                
                # 导出为CSV文件
                import csv
                export_filename = f'export_{self.current_module}_{self.current_form}.csv'
                
                if records:
                    # 获取所有字段名
                    fieldnames = list(records[0].keys())
                    
                    with open(export_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(records)
                    
                    messagebox.showinfo('导出成功', f'数据已导出到 {export_filename}')
                else:
                    messagebox.showinfo('提示', '没有数据可导出')
            except Exception as e:
                messagebox.showerror('导出错误', f'导出数据失败: {e}')
        else:
            messagebox.showinfo('提示', '没有数据可导出')
    
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
            "2. 在左侧选择要操作的模块和单据",
            "3. 点击新增按钮添加新记录",
            "4. 填写表单字段并点击保存",
            "5. 在数据列表中选择记录进行编辑或删除",
            "6. 点击刷新按钮查看最新数据"
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