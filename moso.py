import requests
from parsel import Selector
from concurrent.futures import ThreadPoolExecutor


# 登录
class Loginer:
    def __init__(self, username, passwd, remember='N'):
        '''实例化登录类'''
        self.__username = username
        self.__password = passwd
        self.__remember = remember
        self.__login_url = 'https://www.mosoteach.cn/web/index.php?c=passport&m=account_login'
        self.login_status = None

    @property
    def login(self):
        '''实现登录的操作,用以获取账号的信息'''
        data = {
            'account_name': self.__username,
            'user_pwd': self.__password,
            'remember_me': self.__remember
        }
        try:
            self.login_status = requests.post(self.__login_url, data=data, timeout=5)
            return self.login_status
        except Exception as e:
            print(e)
            return None

    @property
    def get_cookies(self):
        '''以邮箱和手机号的方式登录账号并返回登录成功的cookie值'''
        res = self.login_status
        if res.json()['result_code'] == 0:
            return res.cookies
        else:
            return None

    def get_cookies_phone_capt(self):
        '''待实现'''
        pass

    def show(self):
        res = self.login_status.json()
        username = res['user']['full_name']
        school_name = res['user']['school_name']
        print('%s的%s,你好,欢迎使用!' % (school_name, username))
        t = input('回车继续>>>')

    def login_phone_capt(self):
        pass


# 班课里面的操作
class Clazzcourse:
    def __init__(self, cookies=None):
        self.__cookies = cookies
        self.headers = {
            'Connection': 'close',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36',
            'Referer': 'https://www.mosoteach.cn/web/index.php?c=passport&m=index'
        }
        self.OtherUrls = []
        self.VideUrls = []

    @property
    def join_class_list(self):
        ''''''
        if self.__cookies is None:
            print('请传入一个cookie值!!!')
            return None
        url = 'https://www.mosoteach.cn/web/index.php?c=clazzcourse&m=my_joined'
        try:
            response = requests.post(url, cookies=self.__cookies, timeout=5)
            return response.json()
        except Exception as e:
            print(e)
            return None

    def res_list(self, choice):
        print('正在采集当前班课信息:%s' % choice[0])
        url = f'https://www.mosoteach.cn/web/index.php?c=res&m=index&clazz_course_id={choice[-1]}'
        response = requests.get(url, cookies=self.__cookies)
        selector = Selector(response.text)
        divs = selector.xpath('//*[@id="res-list-box"]/div/div[2]/div')
        for div in divs:
            try:
                type = div.xpath('./@data-mime').get()  # 类型
                url = div.xpath('./@data-href').get()  # 文件链接
                title = div.xpath('./div[4]/div[1]/span/text()').get()  # 文件标题
                data_value = div.xpath('./@data-value').get()  # 文件id
                status_file = div.css('.create-box span[data-is-drag]::attr(data-is-drag)').get()  # 文件的状态
                if status_file == 'N':
                    if type == 'video':
                        info_vides = {}
                        info_vides['url'] = url
                        info_vides['clazz_course_id'] = choice[-1]
                        info_vides['res_id'] = data_value
                        info_vides['title'] = title
                        self.VideUrls.append(info_vides)
                    else:
                        info_other = {}
                        info_other['url'] = url
                        info_other['clazz_course_id'] = choice[-1]
                        info_other['res_id'] = data_value
                        info_other['title'] = title
                        self.OtherUrls.append(info_other)
            except:
                pass

    def video(self, info):
        url = 'https://www.mosoteach.cn/web/index.php?c=res&m=save_watch_to'
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
            requests.post(url, data=data, cookies=self.__cookies, timeout=5)

            ####################
            duration = 100
            dataa = {
                'clazz_course_id': clazz_course_id,
                'res_id': res_id,
                'watch_to': duration,
                'duration': duration,
                'current_watch_to': duration
            }
            requests.post(url, data=dataa, cookies=self.__cookies, timeout=5)

        except Exception as e:
            self.video(info)

    def otherfile(self, info):
        try:
            url = info['url']
            name = info['title']
            print(f'正在刷:{name}')
            requests.head(url, headers=self.headers, cookies=self.__cookies, timeout=2)
        except Exception as e:
            self.otherfile(info)

    def process_file(self):
        executor_video = ThreadPoolExecutor(max_workers=8)
        executor_video.map(self.video, self.VideUrls)
        executor_other = ThreadPoolExecutor(max_workers=8)
        executor_other.map(self.otherfile, self.OtherUrls)
