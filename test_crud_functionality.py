import unittest
import os
import json
import time
from mda_form_engine import MDAFormEngine

class TestCRUDFunctionality(unittest.TestCase):
    def setUp(self):
        # 创建测试元数据
        self.test_metadata = '''<?xml version="1.0" encoding="UTF-8"?>
<FormMetadata>
    <Modules>
        <Module name="测试模块">
            <Forms>
                <Form name="测试单据">
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
            </Forms>
        </Module>
    </Modules>
</FormMetadata>'''
        
        with open('test_crud_metadata.xml', 'w', encoding='utf-8') as f:
            f.write(self.test_metadata)
        
        # 清理可能存在的旧数据文件
        self.test_data_file = 'data_测试模块_测试单据.json'
        if os.path.exists(self.test_data_file):
            os.remove(self.test_data_file)
        
        # 创建引擎实例
        self.engine = MDAFormEngine('test_crud_metadata.xml')
        self.engine.current_module = '测试模块'
        self.engine.current_form = '测试单据'
    
    def tearDown(self):
        # 清理测试文件
        if os.path.exists('test_crud_metadata.xml'):
            os.remove('test_crud_metadata.xml')
        if os.path.exists(self.test_data_file):
            os.remove(self.test_data_file)
    
    def test_add_record(self):
        """测试添加记录功能"""
        # 模拟字段值
        test_data = {
            '测试字段': '测试值',
            '测试下拉框': '选项1',
            '测试金额': '100.5'
        }
        
        # 模拟字段控件
        class MockWidget:
            def __init__(self, value):
                self.value = value
            def get(self):
                return self.value
        
        # 设置模拟字段控件
        self.engine.field_widgets = {
            '测试字段': MockWidget('测试值'),
            '测试下拉框': MockWidget('选项1'),
            '测试金额': MockWidget('100.5')
        }
        
        # 保存数据（模拟添加记录）
        self.engine.save_data()
        
        # 验证数据文件存在
        self.assertTrue(os.path.exists(self.test_data_file))
        
        # 验证数据已保存
        with open(self.test_data_file, 'r', encoding='utf-8') as f:
            records = json.load(f)
        
        self.assertGreater(len(records), 0)
        self.assertEqual(records[0]['测试字段'], '测试值')
        self.assertEqual(records[0]['测试下拉框'], '选项1')
        self.assertEqual(records[0]['测试金额'], '100.5')
        self.assertIn('id', records[0])
        self.assertIn('created_at', records[0])
    
    def test_update_record(self):
        """测试更新记录功能"""
        # 先添加一条记录
        test_data = {
            '测试字段': '测试值',
            '测试下拉框': '选项1',
            '测试金额': '100.5'
        }
        
        # 模拟字段控件
        class MockWidget:
            def __init__(self, value):
                self.value = value
            def get(self):
                return self.value
        
        # 设置模拟字段控件
        self.engine.field_widgets = {
            '测试字段': MockWidget('测试值'),
            '测试下拉框': MockWidget('选项1'),
            '测试金额': MockWidget('100.5')
        }
        
        # 保存数据（添加记录）
        self.engine.save_data()
        
        # 加载数据
        with open(self.test_data_file, 'r', encoding='utf-8') as f:
            records = json.load(f)
        
        record_id = records[0]['id']
        
        # 更新记录
        self.engine.field_widgets = {
            '测试字段': MockWidget('更新后的值'),
            '测试下拉框': MockWidget('选项2'),
            '测试金额': MockWidget('200.75')
        }
        
        # 模拟ID字段
        self.engine.field_widgets['id'] = MockWidget(record_id)
        
        # 保存数据（更新记录）
        self.engine.save_data()
        
        # 验证数据已更新
        with open(self.test_data_file, 'r', encoding='utf-8') as f:
            updated_records = json.load(f)
        
        self.assertEqual(len(updated_records), len(records))
        updated_record = next((r for r in updated_records if r['id'] == record_id), None)
        self.assertIsNotNone(updated_record)
        self.assertEqual(updated_record['测试字段'], '更新后的值')
        self.assertEqual(updated_record['测试下拉框'], '选项2')
        self.assertEqual(updated_record['测试金额'], '200.75')
    
    def test_delete_record(self):
        """测试删除记录功能"""
        # 先添加一条记录
        test_data = {
            '测试字段': '测试值',
            '测试下拉框': '选项1',
            '测试金额': '100.5'
        }
        
        # 模拟字段控件
        class MockWidget:
            def __init__(self, value):
                self.value = value
            def get(self):
                return self.value
        
        # 设置模拟字段控件
        self.engine.field_widgets = {
            '测试字段': MockWidget('测试值'),
            '测试下拉框': MockWidget('选项1'),
            '测试金额': MockWidget('100.5')
        }
        
        # 保存数据（添加记录）
        self.engine.save_data()
        
        # 加载数据
        with open(self.test_data_file, 'r', encoding='utf-8') as f:
            records = json.load(f)
        
        record_id = records[0]['id']
        initial_count = len(records)
        
        # 删除记录
        self.engine.delete_record(record_id)
        
        # 验证数据已删除
        with open(self.test_data_file, 'r', encoding='utf-8') as f:
            deleted_records = json.load(f)
        
        self.assertEqual(len(deleted_records), initial_count - 1)
        deleted_record = next((r for r in deleted_records if r['id'] == record_id), None)
        self.assertIsNone(deleted_record)
    
    def test_get_records(self):
        """测试获取记录列表功能"""
        # 添加多条记录
        test_records = [
            {'测试字段': '值1', '测试下拉框': '选项1', '测试金额': '100.5'},
            {'测试字段': '值2', '测试下拉框': '选项2', '测试金额': '200.75'},
            {'测试字段': '值3', '测试下拉框': '选项1', '测试金额': '300.0'}
        ]
        
        # 模拟字段控件
        class MockWidget:
            def __init__(self, value):
                self.value = value
            def get(self):
                return self.value
        
        for record in test_records:
            self.engine.field_widgets = {
                '测试字段': MockWidget(record['测试字段']),
                '测试下拉框': MockWidget(record['测试下拉框']),
                '测试金额': MockWidget(record['测试金额'])
            }
            self.engine.save_data()
            time.sleep(0.1)  # 确保时间戳不同
        
        # 验证数据数量
        with open(self.test_data_file, 'r', encoding='utf-8') as f:
            records = json.load(f)
        
        self.assertEqual(len(records), len(test_records))
    
    def test_export_data(self):
        """测试导出数据功能"""
        # 添加一条记录
        test_data = {
            '测试字段': '测试值',
            '测试下拉框': '选项1',
            '测试金额': '100.5'
        }
        
        # 模拟字段控件
        class MockWidget:
            def __init__(self, value):
                self.value = value
            def get(self):
                return self.value
        
        # 设置模拟字段控件
        self.engine.field_widgets = {
            '测试字段': MockWidget('测试值'),
            '测试下拉框': MockWidget('选项1'),
            '测试金额': MockWidget('100.5')
        }
        
        # 保存数据
        self.engine.save_data()
        
        # 导出数据
        self.engine.export_data()
        
        # 验证导出文件存在
        export_filename = 'export_测试模块_测试单据.csv'
        self.assertTrue(os.path.exists(export_filename))
        
        # 清理导出文件
        if os.path.exists(export_filename):
            os.remove(export_filename)

if __name__ == '__main__':
    unittest.main()
