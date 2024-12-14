"""
慕课堂助手配置文件
"""

# API配置
API_BASE_URL = "https://www.mosoteach.cn/web/index.php"
LOGIN_URL = f"{API_BASE_URL}?c=passport&m=account_login"

# 请求配置
REQUEST_TIMEOUT = 5
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36'
DEFAULT_HEADERS = {
    'Connection': 'close',
    'User-Agent': USER_AGENT,
    'Referer': 'https://www.mosoteach.cn/web/index.php?c=passport&m=index'
}
