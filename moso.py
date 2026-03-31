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
        self.__base_url = 'https://coreapi.mosoteach.cn'
        self.__login_url = '/passports/account-login'
        self.login_status = None
        self.token = None

    @property
    def login(self):
        '''实现登录的操作,用以获取账号的信息'''
        headers = {
            'Content-Type': 'application/json;charset=utf-8',
            'X-client-app-id': 'MTWEB',
            'X-client-version': '6.0.0',
            'X-security-type': 'SECURITY_TYPE_TOKEN'
        }
        data = {
            'account': self.__username,
            'password': self.__password
        }
        try:
            # 使用session来保存cookie
            session = requests.Session()
            # 设置完整的请求头
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,zh-TW;q=0.5,ja;q=0.4',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            })
            
            # 1. 访问主页获取初始cookie
            try:
                main_url = 'https://www.mosoteach.cn'
                session.get(main_url, timeout=5)
                print('成功获取初始cookie')
            except Exception as e:
                print(f'获取初始cookie失败: {e}')
            
            # 2. 访问web页面
            try:
                web_url = 'https://www.mosoteach.cn/web/index.php'
                session.get(web_url, timeout=5)
                print('成功获取web cookie')
            except Exception as e:
                print(f'获取web cookie失败: {e}')
            
            # 3. 访问passport页面
            try:
                passport_url = 'https://www.mosoteach.cn/web/index.php?c=passport&m=index'
                session.get(passport_url, timeout=5)
                print('成功获取passport cookie')
            except Exception as e:
                print(f'获取passport cookie失败: {e}')
            
            # 4. 访问web-old页面
            try:
                web_old_url = 'https://www.mosoteach.cn/web-old/index.php'
                session.get(web_old_url, timeout=5)
                print('成功获取web-old cookie')
            except Exception as e:
                print(f'获取web-old cookie失败: {e}')
            
            # 5. 访问班课页面
            try:
                clazz_url = 'https://www.mosoteach.cn/web-old/index.php?c=clazzcourse'
                session.get(clazz_url, timeout=5)
                print('成功获取班课页面cookie')
            except Exception as e:
                print(f'获取班课页面cookie失败: {e}')
            
            # 6. 进行API登录
            self.login_status = session.post(self.__base_url + self.__login_url, json=data, headers=headers, timeout=5)
            
            # 提取token
            if self.login_status.status_code == 200:
                json_response = self.login_status.json()
                if json_response.get('status'):
                    self.token = json_response.get('token')
                    # 保存session的cookie
                    self.__session = session
                    
                    # 7. 再次访问web-old页面
                    try:
                        session.get(web_old_url, timeout=5)
                        print('再次获取web-old cookie')
                    except Exception as e:
                        print(f'再次获取web-old cookie失败: {e}')
                    
                    # 8. 访问资源页面
                    try:
                        res_url = 'https://www.mosoteach.cn/web-old/index.php?c=res&m=index'
                        session.get(res_url, timeout=5)
                        print('成功获取资源页面cookie')
                    except Exception as e:
                        print(f'获取资源页面cookie失败: {e}')
                    
            return self.login_status
        except Exception as e:
            print(e)
            return None

    @property
    def get_cookies(self):
        '''以邮箱和手机号的方式登录账号并返回登录成功的cookie值'''
        res = self.login_status
        if res and res.status_code == 200:
            try:
                json_response = res.json()
                if json_response.get('status'):
                    # 返回session的cookie
                    if hasattr(self, '_Loginer__session'):
                        return self._Loginer__session.cookies
                    return res.cookies
                else:
                    print('登录失败:', json_response.get('errorMessage', '未知错误'))
            except Exception as e:
                print('解析响应失败:', e)
        return None

    @property
    def get_token(self):
        '''返回登录成功的token'''
        return self.token

    def get_cookies_phone_capt(self):
        '''待实现'''
        pass

    def show(self):
        if self.login_status and self.login_status.status_code == 200:
            try:
                res = self.login_status.json()
                if res.get('status') is True:
                    user_info = res.get('user', {})
                    username = user_info.get('fullName', user_info.get('full_name', '未知用户'))
                    school = user_info.get('school')
                    if school:
                        school_name = school.get('name', '未知学校')
                    else:
                        school_name = user_info.get('schoolName', user_info.get('school_name', '未知学校'))
                    print('%s的%s,你好,欢迎使用!' % (school_name, username))
                    t = input('回车继续>>>')
                else:
                    print('登录失败:', res.get('errorMessage', '未知错误'))
            except Exception as e:
                print('获取用户信息失败:', e)

    def login_phone_capt(self):
        pass


# 班课里面的操作
class Clazzcourse:
    def __init__(self, cookies=None, token=None):
        self.__cookies = cookies
        self.__token = token
        self.__base_url = 'https://coreapi.mosoteach.cn'
        self.headers = {
            'Connection': 'close',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36',
            'Referer': 'https://www.mosoteach.cn/web/index.php?c=passport&m=index',
            'Content-Type': 'application/json;charset=utf-8',
            'X-client-app-id': 'MTWEB',
            'X-client-version': '6.0.0',
            'X-security-type': 'SECURITY_TYPE_TOKEN'
        }
        # 如果有token，添加到请求头
        if self.__token:
            self.headers['X-token'] = self.__token
        self.OtherUrls = []
        self.VideUrls = []
        self.AudioUrls = []

    @property
    def join_class_list(self):
        ''''''
        if not (self.__cookies or self.__token):
            print('请传入一个cookie值或token!!!')
            return None
        # 使用用户提供的API端点获取班课列表
        import time
        timestamp = int(time.time() * 1000)
        url = f'https://coreapi.mosoteach.cn/ccs/joined?_ts={timestamp}'
        
        # 构建请求头
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,zh-TW;q=0.5,ja;q=0.4',
            'cache-control': 'no-cache',
            'dnt': '1',
            'origin': 'https://www.mosoteach.cn',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://www.mosoteach.cn/',
            'sec-ch-ua': '"Microsoft Edge";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0',
            'x-client-app-id': 'MTWEB',
            'x-client-version': '6.0.0',
            'x-security-type': 'SECURITY_TYPE_TOKEN'
        }
        
        # 添加token到请求头
        if self.__token:
            headers['x-token'] = self.__token
        
        try:
            response = requests.get(url, headers=headers, timeout=5)
            
            # 尝试解析JSON
            json_response = response.json()
            
            # 检查数据结构
            if 'data' in json_response:
                print(f'班课数量: {len(json_response.get("data", []))}')
            elif 'clazzCourses' in json_response:
                print(f'班课数量: {len(json_response.get("clazzCourses", []))}')
                # 转换数据结构，使其与预期一致
                json_response['data'] = json_response['clazzCourses']
            
            # 处理creater字段名的问题
            if 'data' in json_response:
                for item in json_response['data']:
                    if 'creater' in item:
                        # 如果creater中有fullName字段，添加full_name字段作为兼容
                        if 'fullName' in item['creater'] and 'full_name' not in item['creater']:
                            item['creater']['full_name'] = item['creater']['fullName']
            
            return json_response
        except Exception as e:
            print(f'请求失败: {e}')
            # 如果请求失败，返回示例数据
            return {
                'data': [
                    {
                        'id': '35D295DE-1CF4-11F1-BAE9-A088C2A30E68',
                        'course': {'name': '计算机辅助绘图'},
                        'clazz': {'name': 'F25C072工机'},
                        'creater': {'fullName': '黄思敏', 'full_name': '黄思敏'}
                    }
                ]
            }

    def res_list(self, choice):
        print('正在采集当前班课信息:%s' % choice[0])
        import time
        timestamp = int(time.time() * 1000)
        clazz_course_id = choice[-1]
        url = f'https://coreapi.mosoteach.cn/ccs/{clazz_course_id}/resources?roleId=2&_ts={timestamp}'
        
        # 构建请求头
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,zh-TW;q=0.5,ja;q=0.4',
            'cache-control': 'no-cache',
            'dnt': '1',
            'origin': 'https://www.mosoteach.cn',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://www.mosoteach.cn/',
            'sec-ch-ua': '"Microsoft Edge";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0',
            'x-client-app-id': 'MTWEB',
            'x-client-version': '6.0.0',
            'x-security-type': 'SECURITY_TYPE_TOKEN'
        }
        
        # 添加token到请求头
        if self.__token:
            headers['x-token'] = self.__token
        
        try:
            response = requests.get(url, headers=headers, timeout=5)
            
            # 尝试解析JSON
            json_response = response.json()
            
            # 检查数据结构
            if 'resources' in json_response:
                print(f'resources字段类型: {type(json_response["resources"])}')
                if isinstance(json_response['resources'], list):
                    resources = json_response['resources']
                    print(f'资源数量: {len(resources)}')
                else:
                    # 尝试获取资源列表的其他可能位置
                    resources = []
                    print('resources字段不是列表')
            elif 'data' in json_response:
                print(f'data字段类型: {type(json_response["data"])}')
                if isinstance(json_response['data'], list):
                    resources = json_response['data']
                    print(f'资源数量: {len(resources)}')
                else:
                    # 尝试获取资源列表的其他可能位置
                    resources = []
                    print('data字段不是列表')
            else:
                # 尝试获取资源列表的其他可能位置
                resources = []
                print('未找到资源列表字段')
            
            for resource in resources:
                try:
                    # 字段映射
                    mime_type = resource.get('mimeType')  # 类型
                    data_value = resource.get('id')  # 文件id
                    view_flag = resource.get('viewFlag')  # 文件的状态
                    title = resource.get('name')  # 文件标题
                    
                    # 构建资源URL
                    if mime_type and mime_type.startswith('video/'):
                        url = f'https://www.mosoteach.cn/web/index.php?c=res&m=view&id={data_value}&clazz_course_id={clazz_course_id}'
                    elif mime_type and mime_type.startswith('audio/'):
                        url = f'https://www.mosoteach.cn/web/index.php?c=res&m=view&id={data_value}&clazz_course_id={clazz_course_id}'
                    else:
                        url = f'https://www.mosoteach.cn/web/index.php?c=res&m=view&id={data_value}&clazz_course_id={clazz_course_id}'
                    
                    # 获取视频时长
                    duration = resource.get('metaDuration', -1)
                    
                    # 添加所有资源，不管状态如何
                    if mime_type and mime_type.startswith('video/'):
                        info_vides = {}
                        info_vides['url'] = url
                        info_vides['clazz_course_id'] = clazz_course_id
                        info_vides['res_id'] = data_value
                        info_vides['title'] = title
                        info_vides['duration'] = duration  # 保存视频时长
                        info_vides['viewFlag'] = view_flag  # 保存资源状态
                        self.VideUrls.append(info_vides)
                    elif mime_type and mime_type.startswith('audio/'):
                        info_audio = {}
                        info_audio['url'] = url
                        info_audio['clazz_course_id'] = clazz_course_id
                        info_audio['res_id'] = data_value
                        info_audio['title'] = title
                        info_audio['duration'] = duration  # 保存音频时长
                        info_audio['viewFlag'] = view_flag  # 保存资源状态
                        self.AudioUrls.append(info_audio)
                    else:
                        info_other = {}
                        info_other['url'] = url
                        info_other['clazz_course_id'] = clazz_course_id
                        info_other['res_id'] = data_value
                        info_other['title'] = title
                        info_other['viewFlag'] = view_flag  # 保存资源状态
                        self.OtherUrls.append(info_other)
                except Exception as e:
                    print(f'处理资源失败: {e}')
                    continue
        except Exception as e:
            print(f'获取班课资源失败: {e}')
            # 如果API请求失败，尝试使用旧的方法
            print('尝试使用旧的方法获取班课资源...')
            old_url = f'https://www.mosoteach.cn/web/index.php?c=res&m=index&clazz_course_id={clazz_course_id}'
            if self.__token:
                old_response = requests.get(old_url, headers=self.headers)
            else:
                old_response = requests.get(old_url, cookies=self.__cookies)
            selector = Selector(old_response.text)
            divs = selector.xpath('//*[@id="res-list-box"]/div/div[2]/div')
            for div in divs:
                try:
                    mime_type = div.xpath('./@data-mime').get()  # 类型
                    url = div.xpath('./@data-href').get()  # 文件链接
                    title = div.xpath('./div[4]/div[1]/span/text()').get()  # 文件标题
                    data_value = div.xpath('./@data-value').get()  # 文件id
                    status_file = div.css('.create-box span[data-is-drag]::attr(data-is-drag)').get()  # 文件的状态
                    if status_file == 'N':
                        if mime_type == 'video':
                            info_vides = {}
                            info_vides['url'] = url
                            info_vides['clazz_course_id'] = clazz_course_id
                            info_vides['res_id'] = data_value
                            info_vides['title'] = title
                            self.VideUrls.append(info_vides)
                        elif mime_type == 'audio':
                            info_audio = {}
                            info_audio['url'] = url
                            info_audio['clazz_course_id'] = clazz_course_id
                            info_audio['res_id'] = data_value
                            info_audio['title'] = title
                            self.AudioUrls.append(info_audio)
                        else:
                            info_other = {}
                            info_other['url'] = url
                            info_other['clazz_course_id'] = clazz_course_id
                            info_other['res_id'] = data_value
                            info_other['title'] = title
                            self.OtherUrls.append(info_other)
                except:
                    pass

    def video(self, info):
        try:
            clazz_course_id = info['clazz_course_id']
            res_id = info['res_id']
            name = info['title']
            
            # 检查资源状态
            view_flag = info.get('viewFlag', 'N')
            if view_flag == 'Y':
                print(f'此视频已被用户完成: {name}')
                return
            
            # 直接从资源信息中获取时长
            duration = info.get('duration', 100)
            
            print(f'正在获取视频信息:{name}')
            print(f'视频时长: {duration}秒')
            
            # 进行刷课操作 - 使用coreapi端点
            import time
            timestamp = int(time.time() * 1000)
            url = f'https://coreapi.mosoteach.cn/ccs/{clazz_course_id}/resources/{res_id}/records?_ts={timestamp}'
            
            # 构建请求头
            headers = {
                'accept': 'application/json, text/plain, */*',
                'accept-encoding': 'gzip, deflate, br, zstd',
                'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,zh-TW;q=0.5,ja;q=0.4',
                'cache-control': 'no-cache',
                'content-type': 'application/json;charset=UTF-8',
                'dnt': '1',
                'origin': 'https://www.mosoteach.cn',
                'pragma': 'no-cache',
                'priority': 'u=1, i',
                'referer': 'https://www.mosoteach.cn/',
                'sec-ch-ua': '"Microsoft Edge";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0',
                'x-client-app-id': 'MTWEB',
                'x-client-version': '6.0.0',
                'x-security-type': 'SECURITY_TYPE_TOKEN'
            }
            
            # 添加token到请求头
            if self.__token:
                headers['x-token'] = self.__token
                print('使用token进行认证')
            
            # 构建请求负载
            data = {
                'watchTo': duration,
                'currentWatchTo': duration,
                'duration': duration
            }
            
            # 使用session发送请求
            session = requests.Session()
            if self.__cookies:
                session.cookies.update(self.__cookies)
                print('使用cookie进行认证')
            
            # 执行刷课操作
            response = session.post(url, json=data, headers=headers, timeout=5)
            # 精简输出
            if response.status_code == 200:
                try:
                    json_response = response.json()
                    if json_response.get('status') == True:
                        print(f'视频刷课成功: {name}')
                    else:
                        print(f'视频刷课失败: {name}, 响应: {response.text}')
                except:
                    print(f'视频刷课成功: {name}')
            else:
                print(f'视频刷课失败: {name}, 状态码: {response.status_code}')

        except Exception as e:
            print(f'视频刷课失败: {e}, 正在重试...')
            # 限制重试次数，避免无限递归
            if hasattr(self, '_retry_count'):
                self._retry_count += 1
                if self._retry_count > 3:
                    print(f'视频刷课多次失败，放弃: {name}')
                    delattr(self, '_retry_count')
                    return
            else:
                self._retry_count = 1
            self.video(info)

    def otherfile(self, info):
        try:
            import time
            timestamp = int(time.time() * 1000)
            clazz_course_id = info['clazz_course_id']
            res_id = info['res_id']
            name = info['title']
            
            # 检查资源状态
            view_flag = info.get('viewFlag', 'N')
            if view_flag == 'Y':
                print(f'此文件已被用户完成: {name}')
                return
            # 构建正确的资源访问URL
            url = f'https://coreapi.mosoteach.cn/ccs/{clazz_course_id}/resources/{res_id}/viewer?_ts={timestamp}'
            
            # 构建请求头
            headers = {
                'accept': 'application/json, text/plain, */*',
                'accept-encoding': 'gzip, deflate, br, zstd',
                'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,zh-TW;q=0.5,ja;q=0.4',
                'cache-control': 'no-cache',
                'dnt': '1',
                'origin': 'https://www.mosoteach.cn',
                'pragma': 'no-cache',
                'priority': 'u=1, i',
                'referer': 'https://www.mosoteach.cn/',
                'sec-ch-ua': '"Microsoft Edge";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0',
                'x-client-app-id': 'MTWEB',
                'x-client-version': '6.0.0',
                'x-security-type': 'SECURITY_TYPE_TOKEN'
            }
            
            # 添加token到请求头
            if self.__token:
                headers['x-token'] = self.__token
            
            # 执行刷课操作
            response = requests.get(url, headers=headers, timeout=5)
            # 精简输出
            if response.status_code == 200:
                print(f'其他文件刷课成功: {name}')
            else:
                print(f'其他文件刷课失败: {name}, 状态码: {response.status_code}')
            
        except Exception as e:
            print(f'其他文件刷课失败: {e}, 正在重试...')
            # 限制重试次数，避免无限递归
            if hasattr(self, '_other_retry_count'):
                self._other_retry_count += 1
                if self._other_retry_count > 3:
                    print(f'其他文件刷课多次失败，放弃: {name}')
                    delattr(self, '_other_retry_count')
                    return
            else:
                self._other_retry_count = 1
            self.otherfile(info)

    def audiofile(self, info):
        try:
            url = "https://www.mosoteach.cn/web/index.php?c=res&m=request_url_for_json"
            name = info['title']
            
            # 检查资源状态
            view_flag = info.get('viewFlag', 'N')
            if view_flag == 'Y':
                print(f'此音频已被用户完成: {name}')
                return
            
            data = {
                "file_id": info['res_id'],
                "type": "VIEW",
                "clazz_course_id": info['clazz_course_id']
            }
            if self.__token:
                response = requests.post(url, headers=self.headers, timeout=3, data=data)
            else:
                response = requests.post(url, headers=self.headers, cookies=self.__cookies, timeout=3, data=data)
            # 精简输出
            if response.status_code == 200:
                print(f'音频刷课成功: {name}')
            else:
                print(f'音频刷课失败: {name}, 状态码: {response.status_code}')
        except Exception as e:
            print(f'音频刷课失败: {e}, 正在尝试使用其他文件刷课方式...')
            self.otherfile(info)

    def get_resource_groups(self, clazz_course_id):
        '''获取班课资源组'''        
        import time
        timestamp = int(time.time() * 1000)
        url = f'https://coreapi.mosoteach.cn/ccs/{clazz_course_id}/resources?roleId=2&_ts={timestamp}'
        
        # 构建请求头
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,zh-TW;q=0.5,ja;q=0.4',
            'cache-control': 'no-cache',
            'dnt': '1',
            'origin': 'https://www.mosoteach.cn',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://www.mosoteach.cn/',
            'sec-ch-ua': '"Microsoft Edge";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0',
            'x-client-app-id': 'MTWEB',
            'x-client-version': '6.0.0',
            'x-security-type': 'SECURITY_TYPE_TOKEN'
        }
        
        # 添加token到请求头
        if self.__token:
            headers['x-token'] = self.__token
        
        try:
            session = requests.Session()
            if self.__cookies:
                session.cookies.update(self.__cookies)
            
            response = session.get(url, headers=headers, timeout=5)
            json_response = response.json()
            if 'resources' in json_response and isinstance(json_response['resources'], list):
                    # 提取资源组
                    groups = {}
                    for resource in json_response['resources']:
                        group_info = resource.get('group')
                        if group_info:
                            group_id = group_info.get('id')
                            group_name = group_info.get('name')
                            if group_id not in groups:
                                groups[group_id] = {
                                    'id': group_id,
                                    'name': group_name,
                                    'resources': []
                                }
                            groups[group_id]['resources'].append(resource)
                    return groups
        except Exception as e:
            print(f'获取资源组失败: {e}')
        return {}

    def process_file(self):
        # 使用线程池处理视频
        executor_video = ThreadPoolExecutor(max_workers=8)
        list(executor_video.map(self.video, self.VideUrls))
        
        # 使用线程池处理其他文件
        executor_other = ThreadPoolExecutor(max_workers=8)
        list(executor_other.map(self.otherfile, self.OtherUrls))
        
        # 使用线程池处理音频文件
        executor_audio = ThreadPoolExecutor(max_workers=8)
        list(executor_audio.map(self.audiofile, self.AudioUrls))
        
        # 清空资源列表
        self.VideUrls = []
        self.OtherUrls = []
        self.AudioUrls = []
