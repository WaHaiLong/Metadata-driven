# 用户体验测试技能

class UserExperienceTesting:
    """
    用户体验测试技能
    用于确保系统的用户体验良好，防止类似添加按钮无响应的问题
    """
    
    def __init__(self):
        self.name = "用户体验测试"
        self.description = "确保系统的用户体验良好，包括创建测试场景、收集用户反馈和提供改进建议"
        self.version = "1.0"
    
    def create_test_scenarios(self, feature_type):
        """
        创建用户体验测试场景
        
        Args:
            feature_type: 功能类型
            
        Returns:
            list: 测试场景列表
        """
        scenarios = {
            "user_operation": [
                {
                    "id": "UX-001",
                    "name": "添加按钮操作",
                    "description": "测试用户点击添加按钮后的完整操作流程",
                    "steps": [
                        "1. 打开表单系统",
                        "2. 选择一个模块和单据",
                        "3. 点击添加按钮",
                        "4. 观察是否重置表单",
                        "5. 观察是否显示字段输入区域",
                        "6. 观察是否显示重置成功提示",
                        "7. 填写表单数据",
                        "8. 点击保存按钮",
                        "9. 观察是否保存成功",
                        "10. 观察数据列表是否更新"
                    ],
                    "expected_outcomes": [
                        "表单应重置为空",
                        "应显示字段输入区域",
                        "应显示重置成功提示",
                        "数据应保存成功",
                        "数据列表应显示新记录"
                    ],
                    "priority": "high"
                },
                {
                    "id": "UX-002",
                    "name": "编辑按钮操作",
                    "description": "测试用户点击编辑按钮后的完整操作流程",
                    "steps": [
                        "1. 打开表单系统",
                        "2. 选择一个模块和单据",
                        "3. 在数据列表中选择一条记录",
                        "4. 点击编辑按钮",
                        "5. 观察是否显示字段输入区域",
                        "6. 观察是否加载记录数据",
                        "7. 修改表单数据",
                        "8. 点击保存按钮",
                        "9. 观察是否保存成功",
                        "10. 观察数据列表是否更新"
                    ],
                    "expected_outcomes": [
                        "应显示字段输入区域",
                        "应加载选中记录的数据",
                        "数据应保存成功",
                        "数据列表应显示更新后的记录"
                    ],
                    "priority": "high"
                },
                {
                    "id": "UX-003",
                    "name": "删除按钮操作",
                    "description": "测试用户点击删除按钮后的完整操作流程",
                    "steps": [
                        "1. 打开表单系统",
                        "2. 选择一个模块和单据",
                        "3. 在数据列表中选择一条记录",
                        "4. 点击删除按钮",
                        "5. 观察是否显示确认对话框",
                        "6. 点击确认删除",
                        "7. 观察是否删除成功",
                        "8. 观察数据列表是否更新"
                    ],
                    "expected_outcomes": [
                        "应显示删除确认对话框",
                        "记录应删除成功",
                        "数据列表应不再显示该记录"
                    ],
                    "priority": "high"
                }
            ],
            
            "ui_navigation": [
                {
                    "id": "UX-004",
                    "name": "模块导航",
                    "description": "测试用户在模块之间导航的体验",
                    "steps": [
                        "1. 打开表单系统",
                        "2. 在左侧导航树中展开模块",
                        "3. 点击不同的单据",
                        "4. 观察是否正确切换表单",
                        "5. 观察表单标题是否更新"
                    ],
                    "expected_outcomes": [
                        "模块应可展开/折叠",
                        "单据应可点击选择",
                        "表单应正确切换",
                        "表单标题应更新"
                    ],
                    "priority": "medium"
                },
                {
                    "id": "UX-005",
                    "name": "数据列表交互",
                    "description": "测试用户与数据列表的交互体验",
                    "steps": [
                        "1. 打开表单系统",
                        "2. 选择一个模块和单据",
                        "3. 观察数据列表的显示",
                        "4. 尝试选择不同的记录",
                        "5. 观察表格滚动是否流畅"
                    ],
                    "expected_outcomes": [
                        "数据列表应正确显示",
                        "记录应可选择",
                        "表格滚动应流畅"
                    ],
                    "priority": "medium"
                }
            ],
            
            "error_handling": [
                {
                    "id": "UX-006",
                    "name": "错误提示",
                    "description": "测试系统的错误处理和提示",
                    "steps": [
                        "1. 打开表单系统",
                        "2. 选择一个模块和单据",
                        "3. 点击添加按钮",
                        "4. 不填写必填字段",
                        "5. 点击保存按钮",
                        "6. 观察错误提示"
                    ],
                    "expected_outcomes": [
                        "应显示明确的错误提示",
                        "错误提示应指出具体的问题",
                        "错误提示应易于理解"
                    ],
                    "priority": "medium"
                }
            ]
        }
        
        return scenarios.get(feature_type, [])
    
    def collect_user_feedback(self, test_scenario, feedback_items):
        """
        收集用户反馈
        
        Args:
            test_scenario: 测试场景
            feedback_items: 反馈项列表
            
        Returns:
            dict: 反馈报告
        """
        feedback_report = {
            "scenario": test_scenario,
            "feedback_items": feedback_items,
            "overall_rating": 0,
            "suggestions": [],
            "issues": []
        }
        
        # 计算总体评分
        if feedback_items:
            total_rating = sum(item.get('rating', 0) for item in feedback_items)
            feedback_report['overall_rating'] = total_rating / len(feedback_items)
        
        # 提取建议和问题
        for item in feedback_items:
            if item.get('suggestions'):
                feedback_report['suggestions'].extend(item['suggestions'])
            if item.get('issues'):
                feedback_report['issues'].extend(item['issues'])
        
        return feedback_report
    
    def generate_usability_report(self, test_results):
        """
        生成可用性报告
        
        Args:
            test_results: 测试结果列表
            
        Returns:
            str: 可用性报告内容
        """
        report = "# 系统可用性测试报告\n\n"
        
        # 总体情况
        total_tests = len(test_results)
        passed_tests = sum(1 for r in test_results if r.get('status') == 'passed')
        failed_tests = sum(1 for r in test_results if r.get('status') == 'failed')
        
        report += f"## 1. 总体情况\n"
        report += f"- 总测试场景: {total_tests}\n"
        report += f"- 通过: {passed_tests}\n"
        report += f"- 失败: {failed_tests}\n"
        report += f"- 通过率: {(passed_tests/total_tests*100):.1f}%\n\n"
        
        # 详细结果
        report += "## 2. 详细测试结果\n\n"
        
        for result in test_results:
            report += f"### 2.1 {result.get('scenario', {}).get('name', '测试场景')}\n"
            report += f"**ID**: {result.get('scenario', {}).get('id', 'N/A')}\n"
            report += f"**状态**: {result.get('status', 'N/A')}\n"
            report += f"**描述**: {result.get('scenario', {}).get('description', 'N/A')}\n"
            
            if result.get('issues'):
                report += "**问题**:\n"
                for issue in result.get('issues', []):
                    report += f"- {issue}\n"
            
            if result.get('suggestions'):
                report += "**建议**:\n"
                for suggestion in result.get('suggestions', []):
                    report += f"- {suggestion}\n"
            
            report += "\n"
        
        # 总结和建议
        report += "## 3. 总结和建议\n\n"
        
        all_issues = []
        all_suggestions = []
        
        for result in test_results:
            all_issues.extend(result.get('issues', []))
            all_suggestions.extend(result.get('suggestions', []))
        
        if all_issues:
            report += "### 3.1 发现的问题\n"
            for issue in set(all_issues):
                report += f"- {issue}\n"
            report += "\n"
        
        if all_suggestions:
            report += "### 3.2 改进建议\n"
            for suggestion in set(all_suggestions):
                report += f"- {suggestion}\n"
            report += "\n"
        
        report += "### 3.3 结论\n"
        if failed_tests == 0:
            report += "系统可用性测试通过，所有功能都能正常使用。\n"
        else:
            report += f"系统可用性测试发现 {failed_tests} 个问题，需要进行相应的改进。\n"
        
        return report
    
    def provide_ux_improvement_suggestions(self, issues):
        """
        提供用户体验改进建议
        
        Args:
            issues: 发现的问题列表
            
        Returns:
            list: 改进建议列表
        """
        suggestions = []
        
        for issue in issues:
            if "添加按钮" in issue and "无响应" in issue:
                suggestions.append("确保添加按钮的点击事件正确绑定")
                suggestions.append("确保添加操作包含完整的流程步骤")
                suggestions.append("确保显示必要的用户界面")
            
            elif "编辑按钮" in issue and "无响应" in issue:
                suggestions.append("确保编辑按钮的点击事件正确绑定")
                suggestions.append("确保编辑操作包含完整的流程步骤")
                suggestions.append("确保验证记录选择")
            
            elif "保存" in issue and "失败" in issue:
                suggestions.append("检查保存逻辑是否正确")
                suggestions.append("添加适当的错误处理")
                suggestions.append("提供明确的错误提示")
            
            elif "界面" in issue and "显示" in issue:
                suggestions.append("确保UI组件正确显示")
                suggestions.append("检查布局和定位")
                suggestions.append("确保响应式设计")
        
        # 通用建议
        suggestions.extend([
            "提供更清晰的用户操作反馈",
            "优化表单填写流程",
            "确保界面元素的一致性",
            "添加操作引导和帮助信息"
        ])
        
        return list(set(suggestions))
    
    def create_user_journey_map(self, user_goal):
        """
        创建用户旅程地图
        
        Args:
            user_goal: 用户目标
            
        Returns:
            dict: 用户旅程地图
        """
        journey = {
            "user_goal": user_goal,
            "stages": []
        }
        
        if user_goal == "添加新记录":
            journey["stages"] = [
                {
                    "stage": "开始",
                    "user_actions": ["打开表单系统", "选择模块和单据"],
                    "system_responses": ["显示系统主界面", "显示选定的表单"],
                    "emotions": ["中性", "期待"],
                    "pain_points": [],
                    "opportunities": []
                },
                {
                    "stage": "发起添加",
                    "user_actions": ["点击添加按钮"],
                    "system_responses": ["重置表单", "显示字段区域", "显示重置提示"],
                    "emotions": ["期待"],
                    "pain_points": ["如果按钮无响应"],
                    "opportunities": ["提供清晰的操作反馈"]
                },
                {
                    "stage": "填写表单",
                    "user_actions": ["填写各个字段"],
                    "system_responses": ["验证输入", "提供实时反馈"],
                    "emotions": ["专注"],
                    "pain_points": ["表单验证不明确", "字段提示不足"],
                    "opportunities": ["添加字段验证提示", "提供填写帮助"]
                },
                {
                    "stage": "提交保存",
                    "user_actions": ["点击保存按钮"],
                    "system_responses": ["验证数据", "保存记录", "显示保存成功提示"],
                    "emotions": ["期待", "满意"],
                    "pain_points": ["保存失败无提示", "保存过程卡顿"],
                    "opportunities": ["添加保存进度提示", "提供详细的错误信息"]
                },
                {
                    "stage": "完成",
                    "user_actions": ["查看数据列表"],
                    "system_responses": ["刷新数据列表", "显示新记录"],
                    "emotions": ["满意"],
                    "pain_points": ["数据列表未更新"],
                    "opportunities": ["自动刷新数据", "高亮显示新记录"]
                }
            ]
        
        return journey

# 示例用法
if __name__ == "__main__":
    ux_tester = UserExperienceTesting()
    
    # 创建用户操作测试场景
    operation_scenarios = ux_tester.create_test_scenarios("user_operation")
    print("\n=== 用户操作测试场景 ===")
    for scenario in operation_scenarios:
        print(f"ID: {scenario['id']}")
        print(f"名称: {scenario['name']}")
        print(f"优先级: {scenario['priority']}")
        print()
    
    # 创建用户旅程地图
    journey = ux_tester.create_user_journey_map("添加新记录")
    print("\n=== 用户旅程地图 ===")
    print(f"用户目标: {journey['user_goal']}")
    print("阶段数: {len(journey['stages'])}")
