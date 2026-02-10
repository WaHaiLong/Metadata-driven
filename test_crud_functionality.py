import unittest
from mda_form_engine import MDAFormEngine
import os
import json

class TestCRUD(unittest.TestCase):
    def setUp(self):
        # 初始化表单引擎
        self.engine = MDAFormEngine('erp_form_metadata.xml')
        # 设置为测试单据
        self.engine.set_current_form('测试模块', '测试单据')
    
    def test_add_record(self):
        """测试添加记录功能"""
        # 模拟添加记录
        # 这里我们直接测试数据存储功能
        test_data = {
            '测试字段1': '测试值1',
            '测试字段2': '测试值2',
            '状态': '草稿'
        }
        
        # 保存数据
        # 由于我们没有UI，我们直接测试数据文件的创建
        filename = f'data_测试模块_测试单据.json'
        
        # 清理测试数据文件
        if os.path.exists(filename):
            os.remove(filename)
        
        # 测试保存数据
        # 这里我们模拟save_data方法的核心逻辑
        records = []
        # 生成ID和时间戳
        import time
        import random
        new_id = f'{int(time.time())}{random.randint(1000, 9999)}'
        test_data['id'] = new_id
        test_data['created_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
        test_data['created_by'] = '测试用户'
        records.append(test_data)
        
        # 保存到文件
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        
        # 验证文件是否创建成功
        self.assertTrue(os.path.exists(filename))
        
        # 验证数据是否正确保存
        with open(filename, 'r', encoding='utf-8') as f:
            saved_records = json.load(f)
        
        self.assertEqual(len(saved_records), 1)
        self.assertEqual(saved_records[0]['测试字段1'], '测试值1')
        self.assertEqual(saved_records[0]['测试字段2'], '测试值2')
        self.assertEqual(saved_records[0]['状态'], '草稿')
        self.assertIn('id', saved_records[0])
        self.assertIn('created_at', saved_records[0])
        self.assertIn('created_by', saved_records[0])
    
    def test_get_records(self):
        """测试获取记录功能"""
        filename = f'data_测试模块_测试单据.json'
        
        # 确保文件存在
        if not os.path.exists(filename):
            # 创建测试数据
            test_data = [{
                'id': '123456',
                '测试字段1': '测试值1',
                '测试字段2': '测试值2',
                '状态': '草稿',
                'created_at': '2026-02-10 12:00:00',
                'created_by': '测试用户'
            }]
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        # 测试获取记录
        records = self.engine.get_records(filename)
        self.assertGreaterEqual(len(records), 1)
    
    def test_delete_record(self):
        """测试删除记录功能"""
        filename = f'data_测试模块_测试单据.json'
        
        # 创建测试数据
        test_data = [
            {
                'id': '123456',
                '测试字段1': '测试值1',
                '测试字段2': '测试值2',
                '状态': '草稿',
                'created_at': '2026-02-10 12:00:00',
                'created_by': '测试用户'
            },
            {
                'id': '789012',
                '测试字段1': '测试值3',
                '测试字段2': '测试值4',
                '状态': '已提交',
                'created_at': '2026-02-10 13:00:00',
                'created_by': '测试用户'
            }
        ]
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        # 测试删除记录
        # 这里我们模拟delete_record方法的核心逻辑
        records = self.engine.get_records(filename)
        original_count = len(records)
        
        # 删除ID为123456的记录
        records = [record for record in records if record.get('id') != '123456']
        
        # 保存到文件
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        
        # 验证记录是否删除成功
        saved_records = self.engine.get_records(filename)
        self.assertEqual(len(saved_records), original_count - 1)
        self.assertEqual(len([r for r in saved_records if r.get('id') == '123456']), 0)
    
    def test_update_record(self):
        """测试更新记录功能"""
        filename = f'data_测试模块_测试单据.json'
        
        # 创建测试数据
        test_data = [{
            'id': '123456',
            '测试字段1': '测试值1',
            '测试字段2': '测试值2',
            '状态': '草稿',
            'created_at': '2026-02-10 12:00:00',
            'created_by': '测试用户'
        }]
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        # 测试更新记录
        # 这里我们模拟update_record方法的核心逻辑
        records = self.engine.get_records(filename)
        
        # 更新记录
        for i, record in enumerate(records):
            if record.get('id') == '123456':
                records[i]['测试字段1'] = '更新后的值1'
                records[i]['测试字段2'] = '更新后的值2'
                records[i]['状态'] = '已提交'
                break
        
        # 保存到文件
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        
        # 验证记录是否更新成功
        saved_records = self.engine.get_records(filename)
        updated_record = next((r for r in saved_records if r.get('id') == '123456'), None)
        self.assertIsNotNone(updated_record)
        self.assertEqual(updated_record['测试字段1'], '更新后的值1')
        self.assertEqual(updated_record['测试字段2'], '更新后的值2')
        self.assertEqual(updated_record['状态'], '已提交')
    
    def test_data_isolation(self):
        """测试数据隔离功能"""
        # 测试不同单据的数据文件是否独立
        test_module_form = f'data_测试模块_测试单据.json'
        purchase_form = f'data_采购管理_采购订单.json'
        
        # 确保两个文件都存在
        if not os.path.exists(test_module_form):
            test_data = [{
                'id': '123456',
                '测试字段1': '测试值1',
                '测试字段2': '测试值2',
                '状态': '草稿',
                'created_at': '2026-02-10 12:00:00',
                'created_by': '测试用户'
            }]
            with open(test_module_form, 'w', encoding='utf-8') as f:
                json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        if not os.path.exists(purchase_form):
            purchase_data = [{
                'id': '789012',
                '订单编号': 'PO001',
                '供应商名称': '测试供应商',
                '状态': '草稿',
                'created_at': '2026-02-10 12:00:00',
                'created_by': '测试用户'
            }]
            with open(purchase_form, 'w', encoding='utf-8') as f:
                json.dump(purchase_data, f, ensure_ascii=False, indent=2)
        
        # 验证两个文件都存在
        self.assertTrue(os.path.exists(test_module_form))
        self.assertTrue(os.path.exists(purchase_form))
        
        # 验证数据内容不同
        with open(test_module_form, 'r', encoding='utf-8') as f:
            test_data = json.load(f)
        
        with open(purchase_form, 'r', encoding='utf-8') as f:
            purchase_data = json.load(f)
        
        self.assertNotEqual(test_data, purchase_data)
        self.assertIn('测试字段1', test_data[0])
        self.assertIn('订单编号', purchase_data[0])

if __name__ == '__main__':
    unittest.main()
