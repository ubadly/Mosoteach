"""
工具函数测试模块
"""

import unittest
from mosoteach.utils.tools import process_choices


class TestTools(unittest.TestCase):
    """测试工具函数"""

    def test_process_choices_single(self):
        """测试单个选择"""
        result = process_choices("1", 5)
        self.assertEqual(result, [0])

    def test_process_choices_multiple(self):
        """测试多个选择"""
        result = process_choices("1,3,5", 5)
        self.assertEqual(result, [0, 2, 4])

    def test_process_choices_range(self):
        """测试范围选择"""
        result = process_choices("1-3", 5)
        self.assertEqual(result, [0, 1, 2])

    def test_process_choices_invalid(self):
        """测试无效输入"""
        with self.assertRaises(ValueError):
            process_choices("6", 5)

    def test_process_choices_mixed(self):
        """测试混合输入"""
        result = process_choices("1,3-5", 5)
        self.assertEqual(result, [0, 2, 3, 4])


if __name__ == '__main__':
    unittest.main()
