"""
工具函数模块

提供各种辅助功能，如：
- 命令行界面美化
- 用户输入处理
- 日志配置等
"""

import os
import sys
import logging
import platform
from typing import List

# 系统相关
SYSTEM_TYPE = 'cls' if platform.system().lower() == 'windows' else 'clear'


def setup_logging(
    level: int = logging.INFO,
    log_file: str = "mosoteach.log"
) -> None:
    """配置日志系统
    
    Args:
        level: 日志级别
        log_file: 日志文件路径
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def clear_screen() -> None:
    """清除终端屏幕"""
    os.system(SYSTEM_TYPE)


def welcome_screen() -> None:
    """显示欢迎界面"""
    print('*' * 30)
    print('*' + ' ' * 8 + '慕课堂助手' + ' ' * 8 + '*')
    print('*' * 30)


def process_choices(choice_str: str, max_value: int) -> List[int]:
    """处理用户的选择输入
    
    支持以下格式：
    - 单个数字：'1'
    - 多个数字：'1,2,3' 或 '1 2 3'
    - 范围：'1-3'
    
    Args:
        choice_str: 用户输入的选择字符串
        max_value: 最大允许的选择值
        
    Returns:
        List[int]: 处理后的选择列表
        
    Raises:
        ValueError: 当输入格式错误或超出范围时抛出
    """
    # 标准化分隔符
    choice_str = choice_str.replace('，', ',').replace(' ', ',')
    result = []
    
    for item in choice_str.split(','):
        if not item:
            continue
            
        if '-' in item:
            try:
                start, end = map(int, item.split('-'))
                if start < 1 or end > max_value or start > end:
                    raise ValueError(f"范围 {start}-{end} 无效")
                result.extend(range(start - 1, end))
            except ValueError:
                raise ValueError(f"无效的范围格式: {item}")
        else:
            try:
                value = int(item)
                if value < 1 or value > max_value:
                    raise ValueError(f"选择 {value} 超出范围")
                result.append(value - 1)
            except ValueError:
                raise ValueError(f"无效的选择: {item}")
    
    return sorted(list(set(result)))
