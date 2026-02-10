import xml.etree.ElementTree as ET

# 测试添加新单据
def test_add_form():
    # 解析XML文件
    tree = ET.parse('erp_form_metadata.xml')
    root = tree.getroot()
    
    # 找到Modules元素
    modules_elem = root.find('Modules')
    
    if modules_elem:
        # 查找或创建测试模块
        test_module = None
        for module_elem in modules_elem.findall('Module'):
            if module_elem.get('name') == '测试模块':
                test_module = module_elem
                break
        
        if not test_module:
            # 创建新的测试模块
            test_module = ET.SubElement(modules_elem, 'Module')
            test_module.set('name', '测试模块')
            # 创建Forms元素
            forms_elem = ET.SubElement(test_module, 'Forms')
        else:
            # 查找Forms元素
            forms_elem = test_module.find('Forms')
            if not forms_elem:
                forms_elem = ET.SubElement(test_module, 'Forms')
        
        # 添加新单据
        form_elem = ET.SubElement(forms_elem, 'Form')
        form_elem.set('name', '测试单据')
        
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
        
        # 添加业务字段
        test_field1 = ET.SubElement(field_list_elem, 'TextField')
        test_field1.set('name', '测试字段1')
        test_field1.set('Left', '10')
        test_field1.set('Top', '170')
        test_field1.set('Width', '200')
        test_field1.set('Height', '30')
        test_field1.set('VisibleExt', '111')
        test_field1.set('Length', '200')
        
        test_field2 = ET.SubElement(field_list_elem, 'TextField')
        test_field2.set('name', '测试字段2')
        test_field2.set('Left', '10')
        test_field2.set('Top', '210')
        test_field2.set('Width', '200')
        test_field2.set('Height', '30')
        test_field2.set('VisibleExt', '111')
        test_field2.set('Length', '200')
        
        # 保存XML
        tree.write('erp_form_metadata.xml', encoding='UTF-8', xml_declaration=True)
        print('成功添加测试单据')

if __name__ == '__main__':
    test_add_form()
