"""
慕课堂助手主程序

提供命令行界面，处理用户交互和主要业务流程。
"""

import os
import sys
import logging
import requests
from typing import List, Tuple, Optional

from mosoteach.core.moso import Loginer, LoginError, Course, CourseError
from mosoteach.utils.tools import setup_logging, clear_screen, welcome_screen, process_choices

logger = logging.getLogger(__name__)


def login(username: str, password: str) -> Optional[requests.cookies.RequestsCookieJar]:
    """处理用户登录
    
    Args:
        username: 用户名（手机号或邮箱）
        password: 密码
        
    Returns:
        Optional[RequestsCookieJar]: 登录成功返回cookies，失败返回None
    """
    try:
        login_client = Loginer(username, password)
        login_client.login
        login_client.show_welcome()
        return login_client.get_cookies
    except LoginError as e:
        logger.error(f"登录失败: {str(e)}")
        print(f"登录失败: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"发生未知错误: {str(e)}")
        print(f"发生错误: {str(e)}")
        return None


def get_course_selection(cookies: requests.cookies.RequestsCookieJar) -> Optional[List[Tuple[str, str]]]:
    """获取用户选择的班课
    
    Args:
        cookies: 登录成功后的cookies
        
    Returns:
        Optional[List[Tuple[str, str]]]: 返回选中的班课列表，每个元素为(课程名, 课程ID)
    """
    try:
        course_client = Course(cookies)
        course_list = course_client.join_class_list
        
        data = course_list.get('data', [])
        if not data:
            logger.info("没有找到任何班课")
            print("没有找到任何班课！")
            return None
            
        # 显示班课列表
        print("\n=== 已加入的班课 ===")
        for num, course in enumerate(data, start=1):
            print(f"{num}. {course['course']['name']} - "
                  f"{course['clazz']['name']} - "
                  f"{course['creater']['full_name']}")

        # 获取用户选择
        choice = input('\n请选择班课(多个用空格隔开,全选输入all): ').strip()
        
        if not choice:
            logger.info("用户未选择任何班课")
            print('未选择任何班课!')
            return None
            
        if choice.upper() == 'ALL':
            choices = list(range(len(data)))
        else:
            try:
                choices = process_choices(choice, max_value=len(data))
            except ValueError as e:
                logger.error(f"选择处理失败: {str(e)}")
                print(f"输入有误: {str(e)}")
                return None

        # 返回选中的班课信息
        return [(data[i]['course']['name'], data[i]['id']) 
                for i in choices]
                
    except CourseError as e:
        logger.error(f"获取班课列表失败: {str(e)}")
        print(f"获取班课列表失败: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"处理班课选择时发生错误: {str(e)}")
        print(f"处理班课选择时发生错误: {str(e)}")
        return None


def main():
    """主程序入口"""
    try:
        # 设置日志
        setup_logging()
        
        # 清屏并显示欢迎信息
        clear_screen()
        welcome_screen()
        
        # 获取登录信息
        username = input('手机号或邮箱 >>> ').strip()
        password = input('密码 >>> ').strip()
        
        if not username or not password:
            logger.error("用户名或密码为空")
            print("用户名和密码不能为空!")
            return
            
        # 登录
        cookies = login(username, password)
        if not cookies:
            return
            
        # 获取班课选择
        selected_courses = get_course_selection(cookies)
        if not selected_courses:
            return
            
        # 显示选中的班课并开始刷课
        print("\n开始处理选中的班课：")
        course_client = Course(cookies)
        
        for name, course_id in selected_courses:
            print(f"\n正在处理班课: {name}")
            success, total = course_client.complete_all_resources(course_id)
            print(f"班课 {name} 处理完成: {success}/{total} 个资源完成")
        
    except KeyboardInterrupt:
        logger.info("用户中断程序")
        print("\n程序已终止")
    except Exception as e:
        logger.error(f"程序运行时发生错误: {str(e)}")
        print(f"发生错误: {str(e)}")
    finally:
        logger.info("程序结束")


if __name__ == '__main__':
    main()
