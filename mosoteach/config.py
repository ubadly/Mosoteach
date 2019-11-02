#你的账号
username = ''
#你的密码
password = ''
#"Y"表示记住，"N"表示不记住，就是网站的保持登录三十天，不过在这里并没有什么卵用
rember = 'N'
#请求登录的链接
url_root = 'https://www.mosoteach.cn/web/index.php?c=passport&m=account_login'

#请求头
heasers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36',
    'Referer':'https://www.mosoteach.cn/web/index.php?c=passport&m=index'
}
#登录的表单数据
data = {
    'account_name':username,
    'user_pwd':password,
    'remember_me':rember
}