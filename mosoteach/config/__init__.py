"""
配置模块

存储全局配置和常量
"""

# API URLs
LOGIN_URL = "https://www.mosoteach.cn/web/index.php?c=passport&m=account_login"

# 请求配置
REQUEST_TIMEOUT = 30  # 秒
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://www.mosoteach.cn",
    "Referer": "https://www.mosoteach.cn/web/index.php"
}
