import requests,queue,os,threading
from lxml import etree

class moso():
    def __init__(self):
        self.session = requests.Session()
        self.heasers = {
            'Connection':'close',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36',
            'Referer': 'https://www.mosoteach.cn/web/index.php?c=passport&m=index'
        }
    def login(self,username,password):
        # print('尝试登录...')
        loginURL = 'https://www.mosoteach.cn/web/index.php?c=passport&m=account_login'
        data = {
            'account_name':username,
            'user_pwd':password
        }
        try:
            res = self.session.post(loginURL,data=data,headers=self.heasers).json()
            info = {}
            if res['result_code'] == 0 and res['result_msg'] == 'OK':
                # 用户id
                user_id = res['user']['user_id']
                info['user_id'] = user_id
                # 用户名
                account_name = res['user']['account_name']
                info['account_name'] = account_name
                # 头像
                avatar_url = res['user']['avatar_url']
                info['avatar_url'] = avatar_url
                # 昵称
                nick_name = res['user']['nick_name']
                info['nick_name'] = nick_name
                # 学号
                student_no = res['user']['student_no']
                info['student_no'] = student_no
                # 姓名
                full_name = res['user']['full_name']
                info['full_name'] = full_name
                # 手机号
                phone_number = res['user']['phone_number']
                info['phone_number'] = phone_number
                # 注册时间
                last_sec_update_time = res['user']['last_sec_update_time']
                info['last_sec_update_time'] = last_sec_update_time
                # 学校id
                school_id = res['user']['school_id']
                info['school_id'] = school_id
                # 学校名称
                school_name = res['user']['school_name']
                info['school_name'] = school_name
                # 专业id
                department_id = res['user']['department_id']
                info['department_id'] = department_id
                # 专业名称
                department_name = res['user']['department_name']
                info['department_name'] = department_name
                # print('登录成功！')
                return info
            elif res['result_code'] == 1007:
                result_msg = res['result_msg']
                print(result_msg)
                return False
            else:
                print('未知错误！')
                return False


        except:
            print('可能是网络问题导致登录失败！')

            return False

    def showInfo(self,info):
        print(f'学校：{info["school_name"]}')
        print(f'专业：{info["department_name"]}')
        print(f'学号：{info["student_no"]}')
        print(f'姓名：{info["full_name"]}')
        enter = input('回车确认信息继续...')
        if enter == '':
            return True
        else:
            print('你选择了不继续')
            return False
    def getClazzcourse(self):
        classlist = []
        try:
            url = 'https://www.mosoteach.cn/web/index.php?c=clazzcourse&m=index'
            res = self.session.get(url,headers=self.heasers)
            html = etree.HTML(res.text)
            clazzcourse = html.xpath('//*[@id="main"]/main/section[2]/div[3]/ul/li')
            n = 1
            for clazz in clazzcourse:
                classinfo = {}
                # 班课的索引
                classinfo['index'] = n
                # 班课id
                clazz_id = clazz.xpath('./@data-id')[0]
                classinfo['clazz_id'] = clazz_id
                # 教师
                teacher = clazz.xpath('./div[@class="class-info"]/span[1]/@title')[0]
                classinfo['teacher'] = teacher
                # 科目
                subject = clazz.xpath('./div[@class="class-info"]/span[2]/@title')[0]
                classinfo['subject'] = subject
                # 课程名称
                name = clazz.xpath('./div[@class="class-info"]/span[3]/@title')[0]
                classinfo['name'] = name
                n+=1
                classlist.append(classinfo)

        except:
            print('获取加入的班课失败！')
            return False
        return classlist
    def choiceclass(self,classinfo):
        for info in classinfo:
            print(f"{info['index']}.{info['name']}\t{info['subject']}\t{info['teacher']}")
        choice = input('请输入想要刷的班课序号(多个用,隔开，全选输入all)：')
        if choice == '':
            print('啥也没选...')
            t = input('回车重新选择...')
            os.system('cls')
            return self.choiceclass(classinfo)
        elif choice == 'all':
            cho = []
            print('全选')
            for i in classinfo:
                cho.append(i['index'])
            return cho
        else:
            choice = list(set(choice.strip(',').split(',')))
            choice.sort()
            try:
                if int(choice[-1]) > len(classinfo) and int(choice[0]) < 1:
                    print('看看选择错误了吗？')
                    t = input('回车重新选择...')
                    os.system('cls')
                    return self.choiceclass(classinfo)
                else:
                    return choice
            except:
                print('请检查输入的选择是否符合要求！')
                t = input('回车重新选择...')
                os.system('cls')
                return self.choiceclass(classinfo)
class processfile():
    def __init__(self,session,clazz_course_id):
        self.session = session
        self.headers = moso().heasers
        self.clazz_course_id = clazz_course_id
    def video(self,QvideUrls):
        url = 'https://www.mosoteach.cn/web/index.php?c=res&m=save_watch_to'
        while not QvideUrls.empty():
            try:
                info = QvideUrls.get_nowait()
                clazz_course_id = info['clazz_course_id']
                res_id = info['res_id']
                name = info['title']
                data = {
                    'clazz_course_id': clazz_course_id,
                    'res_id': res_id,
                    'watch_to': 5000,
                    'duration': 5000,
                    'current_watch_to': 5000
                }
                try:
                    print(f'正在刷:{name}')
                    self.session.post(url, data=data, stream=True, timeout=5)

                    ####################
                    duration = 100
                    dataa = {
                        'clazz_course_id': clazz_course_id,
                        'res_id': res_id,
                        'watch_to': duration,
                        'duration': duration,
                        'current_watch_to': duration
                    }
                    self.session.post(url, data=dataa, stream=True, timeout=5)
                except Exception as e:
                    pass

            except:
                pass

    def otherfile(self,QotherUrls):
        while not QotherUrls.empty():
            try:
                info = QotherUrls.get_nowait()
                url = info['url']
                name = info['title']
                print(f'正在刷:{name}')
                self.session.get(url,headers=self.headers,stream=True,timeout=2)
            except Exception as e:
                pass
    def getfiles(self,clazz_id):
        QotherUrls = queue.Queue()
        QvideUrls = queue.Queue()
        url = f'https://www.mosoteach.cn/web/index.php?c=res&m=index&clazz_course_id={clazz_id}'
        res = self.session.get(url,headers=self.headers)
        html = etree.HTML(res.text)
        divs = html.xpath('//*[@id="res-list-box"]/div/div[2]/div')
        for div in divs:
            try:
                type = div.xpath('./@data-mime')[0]  # 类型
                url = div.xpath('./@data-href')[0]  # 文件链接
                title = div.xpath('./div[4]/div[1]/span/text()')[0]  # 文件标题
                data_value = div.xpath('./@data-value')[0]  # 文件id
                try:
                    status_file = div.xpath('./div[4]/div[2]/span[5]/@data-is-drag')[0]  # 文件的状态
                except:
                    try:
                        status_file = div.xpath('./div[4]/div[2]/span[7]/@data-is-drag')[0]  # 文件的状态
                    except:
                        status_file = div.xpath('./div[4]/div[2]/span[3]/@data-is-drag')[0]  # 文件的状态
                if status_file == 'N':
                    if type == 'video':
                        info_vides = {}
                        info_vides['url'] = url
                        info_vides['clazz_course_id'] = self.clazz_course_id
                        info_vides['res_id'] = data_value
                        info_vides['title'] = title
                        QvideUrls.put(info_vides)
                    else:
                        info_other = {}
                        info_other['url'] = url
                        info_other['clazz_course_id'] = self.clazz_course_id
                        info_other['res_id'] = data_value
                        info_other['title'] = title
                        QotherUrls.put(info_other)
            except:
                pass
        if QvideUrls.empty() and QotherUrls.empty():
            print('当前班课没有可刷的文件！')
        else:
            print(f'当前班课检测到{QvideUrls.qsize()+QotherUrls.qsize()}个可刷文件')
        if QvideUrls.qsize():
            tasks = []
            # 开启多线程
            for v in range(1, threadsum+1):
                t = threading.Thread(target=self.video, args=(QvideUrls,))
                tasks.append(t)
            # 批量启动线程
            for vt in tasks:
                vt.start()
            # 批量阻塞线程
            for ij in tasks:
                ij.join()
            # self.video(clazz_id,QvideUrls)
        if QotherUrls.qsize():
            tasks = []
            # 开启多线程
            for o in range(1,threadsum+1):
                t = threading.Thread(target=self.otherfile,args=(QotherUrls,))
                tasks.append(t)
            # 批量启动线程
            for ot in tasks:
                ot.start()
            # 批量阻塞线程
            for oj in tasks:
                oj.join()
def welcome():
    print('''
   那就这样吧
再爱都曲终人散了
'''
    )
def main(username,password):

    # 初始化程序
    bk = moso()
    # 登录
    result = bk.login(username, password)
    if result:
        # 判断是否登录成功
        if bk.showInfo(result):
            os.system('cls')
            print('获取到加入的班课：')
            classinfo = bk.getClazzcourse()
            choices = bk.choiceclass(classinfo)
        else:
            t = input('回车退出刷课程序....')
            exit(0)

        for choice in choices:
            choice = int(choice) - 1
            clazz_id = classinfo[choice]['clazz_id']
            name = classinfo[choice]['name']
            subject = classinfo[choice]['subject']
            teacher = classinfo[choice]['teacher']
            print(f'开始班课：{name}/{subject}/{teacher}')
            df = processfile(bk.session,clazz_id)
            df.getfiles(clazz_id)
    else:
        print('登录失败')
if __name__ == '__main__':
    # 线程数
    threadsum = 16
    username = input('学号：')
    password = input('密码：')
    os.system('cls')
    welcome()
    main(username,password)
    t= input('回车退出刷课程序....')
    exit(0)