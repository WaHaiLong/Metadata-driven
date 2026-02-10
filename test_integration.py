import unittest
import os
import json
import time
from mda_form_engine import MDAFormEngine

class TestIntegration(unittest.TestCase):
    def setUp(self):
        # 使用现有的元数据文件进行测试
        self.test_metadata = '''<?xml version="1.0" encoding="UTF-8"?>
<FormMetadata>
    <Form name="集成测试表单">
        <FieldList>
            <TextField name="测试字段" Length="100" Left="10" Top="10" Width="200" Height="30" VisibleExt="111">
                <Validation>
                    <Required>1</Required>
                </Validation>
            </TextField>
            <ComboBox name="测试下拉框" Left="10" Top="50" Width="200" Height="30" VisibleExt="111">
                <Options>
                    <Option>选项1</Option>
                    <Option>选项2</Option>
                </Options>
            </ComboBox>
            <MoneyField name="测试金额" Length="10" Left="10" Top="90" Width="200" Height="30" VisibleExt="111">
                <Validation>
                    <Required>1</Required>
                    <Number>1</Number>
                </Validation>
            </MoneyField>
        </FieldList>
    </Form>
</FormMetadata>'''
        
        with open('test_integration_metadata.xml', 'w', encoding='utf-8') as f:
            f.write(self.test_metadata)
        
        # 清理可能存在的旧数据文件
        if os.path.exists('form_data.json'):
            os.remove('form_data.json')
    
    def tearDown(self):
        if os.path.exists('test_integration_metadata.xml'):
            os.remove('test_integration_metadata.xml')
        if os.path.exists('form_data.json'):
            os.remove('form_data.json')
    
    def test_engine_initialization(self):
        """测试引擎初始化"""
        engine = MDAFormEngine('test_integration_metadata.xml')
        self.assertIsNotNone(engine)
        self.assertEqual(len(engine.fields), 3)
        self.assertIn('测试字段', engine.fields)
        self.assertIn('测试下拉框', engine.fields)
        self.assertIn('测试金额', engine.fields)
    
    def test_data_persistence_flow(self):
        """测试数据持久化流程"""
        # 创建引擎
        engine = MDAFormEngine('test_integration_metadata.xml')
        
        # 模拟字段值
        test_data = {
            '测试字段': '集成测试值',
            '测试下拉框': '选项1',
            '测试金额': '200.75'
        }
        
        # 保存测试数据
        with open('form_data.json', 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        # 验证文件存在
        self.assertTrue(os.path.exists('form_data.json'))
        
        # 验证文件内容
        with open('form_data.json', 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        self.assertEqual(saved_data['测试字段'], '集成测试值')
        self.assertEqual(saved_data['测试下拉框'], '选项1')
        self.assertEqual(saved_data['测试金额'], '200.75')
    
    def test_field_validation_rules(self):
        """测试字段验证规则"""
        engine = MDAFormEngine('test_integration_metadata.xml')
        
        # 验证文本字段的非空规则
        text_field = engine.fields['测试字段']
        self.assertIn('validation', text_field)
        self.assertTrue(text_field['validation']['required'])
        
        # 验证金额字段的规则
        money_field = engine.fields['测试金额']
        self.assertIn('validation', money_field)
        self.assertTrue(money_field['validation']['required'])
        self.assertTrue(money_field['validation']['number'])
    
    def test_visibility_control(self):
        """测试可见性控制"""
        engine = MDAFormEngine('test_integration_metadata.xml')
        
        # 验证所有字段在PC端可见
        for field_name, field_info in engine.fields.items():
            self.assertTrue(engine.is_visible(field_info['visible_ext']))
    
    def test_metadata_structure(self):
        """测试元数据结构完整性"""
        engine = MDAFormEngine('test_integration_metadata.xml')
        
        # 验证表单名称
        self.assertEqual(engine.form_name, '集成测试表单')
        
        # 验证字段属性
        for field_name, field_info in engine.fields.items():
            self.assertIn('type', field_info)
            self.assertIn('left', field_info)
            self.assertIn('top', field_info)
            self.assertIn('width', field_info)
            self.assertIn('height', field_info)
            self.assertIn('visible_ext', field_info)
            
            # 验证字段类型特定属性
            if field_info['type'] == 'TextField':
                self.assertIn('length', field_info)
            elif field_info['type'] == 'ComboBox':
                self.assertIn('options', field_info)
            elif field_info['type'] == 'MoneyField':
                self.assertIn('length', field_info)

if __name__ == '__main__':
    unittest.main()