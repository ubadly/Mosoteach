import os
from time import sleep

from moso import *
from tools import *


def login(user, pwd):
    lg = Loginer(user, pwd)
    if lg.login:
        try:
            lg.show()
            return lg.get_cookies
        except:
            pass
    else:
        return None


def get_class_id():
    course_list = course.join_class_list
    data = course_list['data']
    for num, dat in enumerate(data, start=1):
        course_name = dat['course']['name']
        clazz_name = dat['clazz']['name']
        creater_name = dat['creater']['full_name']
        print(num, course_name, clazz_name, creater_name)
    choice = input('请选择你需要操作的班课(多个用空格隔开,全选输入all):')
    if choice.upper() == 'ALL':
        choices_result = [x for x in range(len(data))]
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


def main():
    # 清屏
    os.system(systemType)
    welcome()
    choices = get_class_id()
    if choices:
        for choice in choices:
            # 将文件放入列表
            course.res_list(choice)
        if course.OtherUrls or course.VideUrls or course.AudioUrls:
            course.process_file()
        else:
            print('没有可以刷的文件!')
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
    cookies = login(username, password)
    if cookies:
        course = Clazzcourse(cookies=cookies)
        main()
    else:
        print('乖乖啊,账号或者密码错了!!!')
    t = input('输入任意键退出>>>')
