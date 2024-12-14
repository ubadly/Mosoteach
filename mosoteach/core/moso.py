"""
慕课堂核心功能模块

提供与慕课堂平台交互的核心功能，包括：
- 用户登录
- 课程信息获取
- 资源下载等
"""

import logging
from typing import Optional, Dict, Any, Union, List, Tuple

import requests
from parsel import Selector

from mosoteach.config import LOGIN_URL, REQUEST_TIMEOUT, DEFAULT_HEADERS

# 配置日志
logger = logging.getLogger(__name__)


class MosoteachError(Exception):
    """慕课堂相关错误的基类"""
    pass


class LoginError(MosoteachError):
    """登录相关错误"""
    pass


class CourseError(MosoteachError):
    """课程相关错误"""
    pass


class Loginer:
    """慕课堂登录类
    
    处理用户登录相关的功能，包括账号密码登录和获取cookies等。
    
    Attributes:
        username (str): 用户名（手机号或邮箱）
        remember (str): 是否记住登录状态
    """
    
    def __init__(self, username: str, passwd: str, remember: str = 'N'):
        self._username = username
        self._password = passwd
        self._remember = remember
        self._session = requests.Session()
        self._session.headers.update(DEFAULT_HEADERS)
        self.login_status = None

    @property
    def login(self) -> Optional[requests.Response]:
        """执行登录操作
        
        Returns:
            Response: 登录请求的响应对象
            
        Raises:
            LoginError: 当登录失败时抛出
        """
        data = {
            'account_name': self._username,
            'user_pwd': self._password,
            'remember_me': self._remember
        }
        try:
            self.login_status = self._session.post(
                LOGIN_URL,
                data=data,
                timeout=REQUEST_TIMEOUT
            )
            return self.login_status
        except requests.RequestException as e:
            logger.error(f"登录请求失败: {str(e)}")
            raise LoginError(f"登录失败: {str(e)}")

    @property
    def get_cookies(self) -> Optional[requests.cookies.RequestsCookieJar]:
        """获取登录成功后的cookies
        
        Returns:
            RequestsCookieJar: 包含登录信息的cookies
            
        Raises:
            LoginError: 当未登录或登录失败时抛出
        """
        if not self.login_status:
            raise LoginError("尚未登录")
            
        response = self.login_status.json()
        if response.get('result_code') == 0:
            return self.login_status.cookies
        else:
            error_msg = response.get('result_msg', '未知错误')
            raise LoginError(f"登录失败: {error_msg}")

    def show_welcome(self) -> None:
        """显示登录成功的欢迎信息"""
        if not self.login_status:
            raise LoginError("尚未登录")
            
        try:
            res = self.login_status.json()
            username = res['user']['full_name']
            school_name = res['user']['school_name']
            logger.info(f"用户 {username} 来自 {school_name} 登录成功")
            print(f'{school_name}的{username},你好,欢迎使用!')
            input('回车继续>>>')
        except (KeyError, ValueError) as e:
            logger.error(f"解析用户信息失败: {str(e)}")
            raise LoginError("获取用户信息失败")


class Course:
    """班课管理类"""
    
    def __init__(self, cookies: requests.cookies.RequestsCookieJar):
        self._cookies = cookies
        self._session = requests.Session()
        self._session.headers.update(DEFAULT_HEADERS)
        self._session.cookies.update(cookies)

    @property
    def join_class_list(self) -> Dict[str, Any]:
        """获取已加入的班课列表
        
        Returns:
            Dict: 包含班课信息的字典
            
        Raises:
            CourseError: 获取班课列表失败时抛出
        """
        url = "https://www.mosoteach.cn/web/index.php?c=clazzcourse&m=my_joined"
        try:
            response = self._session.get(url, timeout=REQUEST_TIMEOUT)
            data = response.json()
            if data.get('result_code') == 0:
                return data
            else:
                error_msg = data.get('result_msg', '未知错误')
                raise CourseError(f"获取班课列表失败: {error_msg}")
        except requests.RequestException as e:
            logger.error(f"请求班课列表失败: {str(e)}")
            raise CourseError(f"获取班课列表失败: {str(e)}")
        except ValueError as e:
            logger.error(f"解析班课列表失败: {str(e)}")
            raise CourseError(f"解析班课列表失败: {str(e)}")

    def get_resources(self, course_id: str) -> List[Dict[str, Any]]:
        """获取班课资源列表"""
        url = f"https://www.mosoteach.cn/web/index.php?c=res&m=index&clazz_course_id={course_id}"
        try:
            response = self._session.get(url, timeout=REQUEST_TIMEOUT)
            selector = Selector(response.text)
            resources = []
            
            # 获取所有资源项
            divs = selector.xpath('//*[@id="res-list-box"]/div/div[2]/div')
            for div in divs:
                try:
                    type = div.xpath('./@data-mime').get()  # 类型
                    url = div.xpath('./@data-href').get()  # 文件链接
                    title = div.xpath('./div[4]/div[1]/span/text()').get()  # 文件标题
                    data_value = div.xpath('./@data-value').get()  # 文件id
                    status_file = div.css('.create-box span[data-is-drag]::attr(data-is-drag)').get()  # 文件的状态
                    
                    # 只处理未完成的资源
                    if status_file == 'N':
                        resource = {
                            'id': data_value,
                            'name': title,
                            'type': type,
                            'url': url,
                            'clazz_course_id': course_id
                        }
                        resources.append(resource)
                except Exception as e:
                    logger.debug(f"解析资源项失败: {str(e)}")
                    continue
                    
            return resources
        except requests.RequestException as e:
            logger.error(f"请求资源列表失败: {str(e)}")
            raise CourseError(f"获取资源列表失败: {str(e)}")
        except Exception as e:
            logger.error(f"解析资源列表失败: {str(e)}")
            raise CourseError(f"解析资源列表失败: {str(e)}")

    def complete_resource(self, course_id: str, resource: Dict[str, str]) -> bool:
        """完成资源学习
        
        根据资源类型使用不同的请求方式：
        - 视频：发送两次观看进度
        - 音频：请求音频URL
        - 其他：访问资源URL
        """
        try:
            print(f'正在刷: {resource["name"]}')
            
            if resource['type'] == 'video':
                return self._complete_video({
                    'clazz_course_id': course_id,
                    'res_id': resource['id'],
                    'title': resource['name'],
                    'url': resource['url']
                })
            elif resource['type'] == 'audio':
                return self._complete_audio({
                    'clazz_course_id': course_id,
                    'res_id': resource['id'],
                    'title': resource['name'],
                    'url': resource['url']
                })
            else:
                return self._complete_other({
                    'url': resource['url'],
                    'title': resource['name']
                })
        except Exception as e:
            logger.error(f"处理资源失败: {str(e)}")
            return False

    def _complete_video(self, info: Dict[str, str], max_retries: int = 3) -> bool:
        """处理视频资源"""
        url = 'https://www.mosoteach.cn/web/index.php?c=res&m=save_watch_to'
        
        # 第一次请求：设置较长的观看时间
        data1 = {
            'clazz_course_id': info['clazz_course_id'],
            'res_id': info['res_id'],
            'watch_to': 5000,
            'duration': 5000,
            'current_watch_to': 5000
        }
        
        # 第二次请求：设置100%完成
        data2 = {
            'clazz_course_id': info['clazz_course_id'],
            'res_id': info['res_id'],
            'watch_to': 100,
            'duration': 100,
            'current_watch_to': 100
        }
        
        for attempt in range(max_retries):
            try:
                # 发送两次请求
                self._session.post(url, data=data1, timeout=5)
                self._session.post(url, data=data2, timeout=5)
                logger.info(f"视频资源完成: {info['title']}")
                return True
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"处理视频资源失败: {str(e)}")
                    return False
                continue

    def _complete_audio(self, info: Dict[str, str], max_retries: int = 3) -> bool:
        """处理音频资源"""
        url = "https://www.mosoteach.cn/web/index.php?c=res&m=request_url_for_json"
        data = {
            "file_id": info['res_id'],
            "type": "VIEW",
            "clazz_course_id": info['clazz_course_id']
        }
        
        for attempt in range(max_retries):
            try:
                self._session.post(url, data=data, timeout=3)
                logger.info(f"音频资源完成: {info['title']}")
                return True
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"处理音频资源失败: {str(e)}")
                    return False
                continue

    def _complete_other(self, info: Dict[str, str], max_retries: int = 3) -> bool:
        """处理其他类型资源"""
        for attempt in range(max_retries):
            try:
                self._session.head(info['url'], timeout=2)
                logger.info(f"其他资源完成: {info['title']}")
                return True
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"处理其他资源失败: {str(e)}")
                    return False
                continue

    def complete_all_resources(self, course_id: str) -> Tuple[int, int]:
        """完成班课所有资源"""
        try:
            resources = self.get_resources(course_id)
            total = len(resources)
            success = 0
            
            for resource in resources:
                if self.complete_resource(course_id, resource):
                    success += 1
                else:
                    print(f"完成资源失败: {resource['name']} ({resource['type']})")
                    
            return success, total
        except Exception as e:
            logger.error(f"批量完成资源时发生错误: {str(e)}")
            return 0, 0
