import platform

systemType = 'cls' if platform.system() == 'Windows' else 'clear'


def choice_process(choice):
    choices = sorted(list(map(lambda x: int(x) - 1, set([x for x in choice.strip().split(' ') if x != '']))))
    return choices
