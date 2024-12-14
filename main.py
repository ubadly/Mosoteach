"""
蓝墨云班课助手主程序入口
"""

import argparse
import sys
from mosoteach.core.moso import Loginer, Course
from mosoteach.gui.app import start_gui

def main():
    """主程序入口"""
    parser = argparse.ArgumentParser(description='蓝墨云班课助手')
    parser.add_argument('--username', help='登录账号（手机号）')
    parser.add_argument('--password', help='登录密码')
    parser.add_argument('--course-id', help='课程ID（可选）')
    parser.add_argument('--gui', action='store_true', help='启动图形界面')

    args = parser.parse_args()

    # 如果指定了--gui参数，启动图形界面
    if args.gui:
        sys.exit(start_gui())
        
    # 检查命令行模式所需的参数
    if not args.username or not args.password:
        parser.print_help()
        sys.exit(1)

    try:
        # 登录
        loginer = Loginer()
        cookies = loginer.login(args.username, args.password)
        
        # 创建课程对象
        course = Course(cookies)
        
        if args.course_id:
            # 完成指定课程的资源
            course.complete_resources(args.course_id)
        else:
            # 完成所有课程的资源
            for class_info in course.join_class_list:
                if isinstance(class_info, dict):
                    course_id = class_info.get('id')
                    if course_id:
                        course.complete_resources(course_id)
                        
        print("任务完成！")
        
    except Exception as e:
        print(f"发生错误: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
