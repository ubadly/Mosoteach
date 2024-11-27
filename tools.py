import platform
import shutil

systemType = 'cls' if platform.system() == 'Windows' else 'clear'

def choice_process(choice):
    choices = sorted(list(map(lambda x: int(x) - 1, set([x for x in choice.strip().split(' ') if x != '']))))
    return choices

def get_terminal_width():
    # 获取终端宽度，默认为 80
    return shutil.get_terminal_size().columns

def center_text(text, width, fill_char=' '):
    # 计算中英文混合字符串实际显示宽度
    def get_str_width(s):
        width = 0
        for c in s:
            width += 2 if ord(c) > 127 else 1
        return width
    
    real_width = get_str_width(text)
    padding = width - real_width
    left_padding = padding // 2
    return fill_char * left_padding + text + fill_char * (padding - left_padding)

def welcome():
    # 获取终端宽度
    term_width = get_terminal_width()
    # 设置内容区域宽度（比终端宽度小一些）
    content_width = min(60, term_width - 4)  # -4 为左右边框预留空间
    
    # 准备显示的内容
    title = "Mosoteach 刷课工具"
    subtitle = "蓝墨云班课自动刷课助手"
    github = "Github: github.com/ubadly/mosoteach"
    star = "觉得好用请给个 Star ⭐"
    prompt = "请按提示输入相关信息..."
    
    # 生成欢迎界面
    border_top = "╔" + "═" * content_width + "╗"
    border_bottom = "╚" + "═" * content_width + "╝"
    separator = "║" + "-" * content_width + "║"
    empty_line = "║" + " " * content_width + "║"

    print(f'''
{border_top}
║{center_text(title, content_width)}║
║{center_text(subtitle, content_width)}║
{separator}
{empty_line}
║{center_text(github, content_width)}║
║{center_text(star, content_width)}║
{empty_line}
║{center_text(prompt, content_width)}║
{border_bottom}
    ''')
