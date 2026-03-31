import os
from time import sleep

from moso import *
from tools import *


def login(user, pwd):
    lg = Loginer(user, pwd)
    if lg.login:
        try:
            lg.show()
            return lg.get_cookies, lg.get_token
        except:
            pass
    else:
        return None, None


def get_class_id():
    course_list = course.join_class_list
    data = course_list['data']
    for num, dat in enumerate(data, start=1):
        course_name = dat['course']['name']
        clazz_name = dat['clazz']['name']
        # 处理creater字段不存在和fullName/full_name字段名的问题
        creater_name = dat.get('creater', {}).get('full_name', dat.get('creater', {}).get('fullName', '未知教师'))
        print(num, course_name, clazz_name, creater_name)
    choice = input('请选择你需要操作的班课(多个用空格隔开,全选输入all):')
    if choice.upper() == 'ALL':
        # 自动处理所有班课
        choice_list = []
        for dat in data:
            course_id = dat['id']
            course_name = dat['course']['name']
            choice_list.append((course_name, course_id))
        return choice_list
    elif choice == '':
        print('啥也没选择!')
        sleep(2)
        return None
    else:
        choices_result = choice_process(choice)
        if choices_result[-1] > len(data) or choices_result[0] < 0:
            print('看看输入的错误没!')
            return None
        choice_list = []
        for i in choices_result:
            course_id = data[i]['id']
            course_name = data[i]['course']['name']
            choice_list.append((course_name, course_id))
        return choice_list


def select_group_and_resource(clazz_course_id, course_name):
    '''选择资源组和单个资源'''    
    # 获取资源组
    groups = course.get_resource_groups(clazz_course_id)
    if not groups:
        print('获取资源组失败!')
        return None
    
    # 显示资源组
    print(f'\n班课: {course_name}')
    print('资源组列表:')
    group_list = list(groups.values())
    for i, group in enumerate(group_list, start=1):
        print(f'{i}. {group["name"]} ({len(group["resources"])}个资源)')
    
    # 选择资源组
    group_choice = input('请选择资源组编号(输入0表示选择所有组):')
    if group_choice == '0':
        selected_groups = group_list
    else:
        try:
            group_idx = int(group_choice) - 1
            if 0 <= group_idx < len(group_list):
                selected_groups = [group_list[group_idx]]
            else:
                print('输入错误!')
                return None
        except:
            print('输入错误!')
            return None
    
    # 显示选中组的资源
    print('\n资源列表:')
    all_resources = []
    for group in selected_groups:
        print(f'\n组: {group["name"]}')
        for i, resource in enumerate(group["resources"], start=1):
            resource_id = resource.get('id')
            resource_name = resource.get('name')
            resource_type = resource.get('mimeType', '未知')
            resource_status = resource.get('viewFlag', '未知')
            all_resources.append((resource, group["name"]))
            print(f'{len(all_resources)}. {resource_name} (类型: {resource_type}, 状态: {resource_status})')
    
    # 选择资源
    resource_choice = input('请选择资源编号(多个用空格隔开,全选输入all):')
    if resource_choice.upper() == 'ALL':
        selected_resources = all_resources
    else:
        try:
            indices = list(map(int, resource_choice.split()))
            selected_resources = []
            for idx in indices:
                if 1 <= idx <= len(all_resources):
                    selected_resources.append(all_resources[idx-1])
                else:
                    print(f'资源编号 {idx} 不存在!')
        except:
            print('输入错误!')
            return None
    
    # 处理选中的资源
    if selected_resources:
        for resource, group_name in selected_resources:
            resource_id = resource.get('id')
            resource_name = resource.get('name')
            resource_type = resource.get('mimeType', '')
            duration = resource.get('metaDuration', 100)
            
            # 构建资源信息
            info = {
                'clazz_course_id': clazz_course_id,
                'res_id': resource_id,
                'title': f'[{group_name}] {resource_name}',
                'duration': duration,
                'viewFlag': resource.get('viewFlag', 'N')  # 保存资源状态
            }
            
            # 根据资源类型刷课
            if resource_type.startswith('video/'):
                course.video(info)
            elif resource_type.startswith('audio/'):
                course.audiofile(info)
            else:
                course.otherfile(info)
    else:
        print('没有选择资源!')
    
    return True

def main():
    # 清屏
    os.system(systemType)
    welcome()
    choices = get_class_id()
    if choices:
        # 检查是否是全选
        is_all = False
        if len(choices) == len(course.join_class_list.get('data', [])):
            is_all = True
        
        for choice in choices:
            course_name, clazz_course_id = choice
            
            # 如果是全选，自动选择刷整个班课的所有资源
            if is_all:
                print(f'\n正在处理班课: {course_name}')
                # 将文件放入列表
                course.res_list(choice)
            else:
                # 询问用户选择刷课方式
                print(f'\n班课: {course_name}')
                print('1. 刷整个班课的所有资源')
                print('2. 选择资源组和单个资源')
                mode_choice = input('请选择刷课方式(1/2):')
                
                if mode_choice == '1':
                    # 将文件放入列表
                    course.res_list(choice)
                elif mode_choice == '2':
                    # 选择资源组和单个资源
                    select_group_and_resource(clazz_course_id, course_name)
                    continue
                else:
                    print('输入错误!')
                    continue
        
        if course.OtherUrls or course.VideUrls or course.AudioUrls:
            course.process_file()
        else:
            print('没有可以刷的文件!')
        
        # 确保提示不会被刷上去
        print('\n' + '='*50)
        is_continue = input('是否继续选择?(y)')
        if is_continue.upper() == "Y":
            main()
        else:
            print('你选择了退出!')
            sleep(1)


if __name__ == '__main__':
    welcome()
    username = input('手机号或邮箱号>>>')
    password = input('密码>>>')
    cookies, token = login(username, password)
    if cookies or token:
        course = Clazzcourse(cookies=cookies, token=token)
        main()
    else:
        print('乖乖啊,账号或者密码错了!!!')
    t = input('输入任意键退出>>>')
