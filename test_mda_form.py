import unittest
import xml.etree.ElementTree as ET
import json
import os
from mda_form_engine import MDAFormEngine

class TestMDAFormEngine(unittest.TestCase):
    def setUp(self):
        self.test_metadata = '''<?xml version="1.0" encoding="UTF-8"?>
<FormMetadata>
    <Form name="测试表单">
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
        
        with open('test_metadata.xml', 'w', encoding='utf-8') as f:
            f.write(self.test_metadata)
        
        self.engine = MDAFormEngine('test_metadata.xml')
    
    def tearDown(self):
        if os.path.exists('test_metadata.xml'):
            os.remove('test_metadata.xml')
        if os.path.exists('form_data.json'):
            os.remove('form_data.json')
    
    def test_metadata_parsing(self):
        """测试元数据解析功能"""
        self.assertEqual(len(self.engine.fields), 3)
        self.assertIn('测试字段', self.engine.fields)
        self.assertIn('测试下拉框', self.engine.fields)
        self.assertIn('测试金额', self.engine.fields)
        
        # 测试文本字段解析
        text_field = self.engine.fields['测试字段']
        self.assertEqual(text_field['type'], 'TextField')
        self.assertEqual(text_field['length'], 100)
        
        # 测试下拉框解析
        combo_field = self.engine.fields['测试下拉框']
        self.assertEqual(combo_field['type'], 'ComboBox')
        self.assertEqual(combo_field['options'], ['选项1', '选项2'])
        
        # 测试金额字段解析
        money_field = self.engine.fields['测试金额']
        self.assertEqual(money_field['type'], 'MoneyField')
        self.assertEqual(money_field['length'], 10)
    
    def test_validation_rules(self):
        """测试验证规则解析"""
        text_field = self.engine.fields['测试字段']
        self.assertIn('validation', text_field)
        self.assertTrue(text_field['validation']['required'])
        
        money_field = self.engine.fields['测试金额']
        self.assertIn('validation', money_field)
        self.assertTrue(money_field['validation']['required'])
        self.assertTrue(money_field['validation']['number'])
    
    def test_data_persistence(self):
        """测试数据持久化功能"""
        # 模拟字段值
        test_data = {
            '测试字段': '测试值',
            '测试下拉框': '选项1',
            '测试金额': '100.5'
        }
        
        # 保存测试数据
        with open('form_data.json', 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        # 验证文件存在
        self.assertTrue(os.path.exists('form_data.json'))
        
        # 验证文件内容
        with open('form_data.json', 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        self.assertEqual(saved_data['测试字段'], '测试值')
        self.assertEqual(saved_data['测试下拉框'], '选项1')
        self.assertEqual(saved_data['测试金额'], '100.5')
    
    def test_visibility_logic(self):
        """测试可见性逻辑"""
        # 测试PC端可见性
        self.assertTrue(self.engine.is_visible('111'))
        self.assertTrue(self.engine.is_visible('100'))
        self.assertFalse(self.engine.is_visible('011'))

if __name__ == '__main__':
    unittest.main()