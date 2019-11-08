import requests
from lxml import etree
from mosoteach import config

class Mosoteach():
    #初始化
    def __init__(self):
        self.data = config.data
        self.headers = config.heasers
        self.root_url = config.url_root
        self.sesson = requests.Session()
    ##获取用户名，班课ID，班课名称信息
    def getClassInfo(self):
        self.sesson.post(self.root_url, data=self.data, headers=self.headers)
        res = self.sesson.get('https://www.mosoteach.cn/web/index.php?c=clazzcourse&m=index', headers=self.headers).text
        html = etree.HTML(res)
        #课程ID
        data = html.xpath('//*[@id="main"]/main/section[2]/div[3]/ul/li/@data-id')
        #课程名称
        name = html.xpath('//*[@id="main"]/main/section[2]/div[3]/ul/li/div[2]/span[2]/text()')
        #用户的姓名
        username = html.xpath('//*[@id="header-box"]/div/div[1]/div[11]/a[1]/span/text()')
        info_list = []
        infos = {}
        for dat, nam in zip(data, name):
            info = {}
            info['name'] = nam
            info['data'] = dat
            info_list.append(info)
        infos['username'] = username
        infos['info'] = info_list
        return infos
    # 获取选择的班课
    def choose(self, info):
        n = 1
        for name in info:
            print(f'{n}.{name["name"]}')
            n += 1
        choices = input('请输入需要刷的班课，多个用逗号隔开：')
        if choices:
            return choices
        else:
            return False
    #刷视频
    def video(self,clazz_course_id,res_id,title):
        url = 'https://www.mosoteach.cn/web/index.php?c=res&m=save_watch_to'
        data = {
            'clazz_course_id':clazz_course_id,
            'res_id': res_id,
            'watch_to': 5000,
            'duration': 5000,
            'current_watch_to': 5000

        }
        err = []
        try:
            self.sesson.post(url, data=data,stream=True,timeout=2)

            ####################
            duration = 100
            dataa = {
                'clazz_course_id': clazz_course_id,
                'res_id': res_id,
                'watch_to': duration,
                'duration': duration,
                'current_watch_to': duration
            }
            self.sesson.post(url, data=dataa,stream=True,timeout=2)
        except:
            err.append(url)
        print(f'{title}刷完！')
        return err
    def qingqiu(self,ids,length):
        '''

        :param ids: id列表
        :param length: 除了视频之外的链接个数
        :return:
        '''
        n = 1
        error = []
        for url in ids:
            print(f'文件进度：{n}/{length}')
            try:
                self.sesson.get(url['url'],stream=True,timeout=2)
            except:
                error.append(url['url'])
            n+=1
        return error
    #解析班课的内容
    def parse(self,clazz_course_id):#解析班课的网页数据
        print('到解析班课页面了')
        '''
        :param clazz_course_id: 班课的ID
        :return:
        '''
        url = f'https://www.mosoteach.cn/web/index.php?c=res&m=index&clazz_course_id={clazz_course_id}'
        response = self.sesson.get(url, headers=self.headers)
        html = etree.HTML(response.text)
        divs = html.xpath('//*[@id="res-list-box"]/div/div[2]/div')
        applications = []
        audios = []
        videos = []
        mosoinks = []
        images = []
        texts = []
        result = {}
        number = len(divs)
        # n = 0
        for div in divs:
            audios_dict = {}
            applications_dict = {}
            mosoinks_dict = {}
            videos_dict = {}
            images_dict = {}
            texts_dict = {}
            type = div.xpath('./@data-mime')[0]#类型
            url = div.xpath('./@data-href')[0]#文件链接
            title = div.xpath('./div[4]/div[1]/span/text()')[0]#文件标题
            data_value = div.xpath('./@data-value')[0]#文件id
            try:
                status_file = div.xpath('./div[4]/div[2]/span[5]/@style')[0]#文件的状态
            except:
                try:
                    status_file = div.xpath('./div[4]/div[2]/span[3]/@style')[0]  # 文件的状态
                except:
                    status_file = div.xpath('./div[4]/div[2]/span[7]/@style')[0]
            # n+=1
            # print(n,status_file)
            if status_file == r'color:#ec6941':
                if type == 'image':
                    images_dict['data_value'] = data_value
                    images_dict['title'] = title
                    images_dict['url'] = url
                    images.append(images_dict)
                elif type == 'application':
                    applications_dict['data_value'] = data_value
                    applications_dict['title'] = title
                    applications_dict['url'] = url
                    applications.append(applications_dict)
                elif type == 'audio':
                    audios_dict['data_value'] = data_value
                    audios_dict['title'] = title
                    audios_dict['url'] = url
                    audios.append(audios_dict)
                elif type == 'mosoink':
                    mosoinks_dict['data_value'] = data_value
                    mosoinks_dict['title'] = title
                    mosoinks_dict['url'] = url
                    mosoinks.append(mosoinks_dict)
                elif type == 'video':
                    videos_dict['data_value'] = data_value
                    videos_dict['title'] = title
                    videos_dict['url'] = url
                    videos.append(videos_dict)
                elif type == 'text':
                    texts_dict['data_value'] = data_value
                    texts_dict['title'] = title
                    texts_dict['url'] = url
                    texts.append(texts_dict)
                result['image'] = images
                result['applications'] = applications
                result['audios'] = audios
                result['mosoinks'] = mosoinks
                result['videos'] = videos
                result['number'] = number
                result['texts'] = texts
        return result

    def _index(self,class_info):
        print('启动班课执行的地方了')
        #读取选择的班课并调用刷课函数
        for dat in class_info:
            # print(dat)
            name = dat['name']
            data = dat['ID']
            print(f'开始班课：{name}')
            result = self.parse(data)
            # print(result)
            if result:
                length = result['number']-len(result['videos'])
                if result['videos']:
                    n = 1
                    for video_info in result['videos']:
                        print(f'视频进度：{n}/{len(result["videos"])}')
                        self.video(data,video_info['data_value'],video_info['title'])
                        n+=1
                else:
                    print('未检测到视频！')
                ids = result['applications']+result['audios']+result['mosoinks']+result['image']+result['texts']
                # print(ids)
                if ids:
                    self.qingqiu(ids, length)
            else:
                print('没有找到可以刷的文件！')



class PaserDate():
    def __init__(self):
        pass
    def welcome(self):
        print('''
  那就这样吧
再爱都曲终人散了
    '''
        )
    def start(self):
        # 实例化moso方法
        bk = Mosoteach()
        # 获取班课的列表信息
        cla_info = bk.getClassInfo()
        # 获取选择的班课信息
        choices = bk.choose(cla_info['info'])
        if choices:
            # 判断选择是否正确
            choices_list = list(choices.replace(',', ''))
            # 去重
            choice = list(set(choices_list))
            # 判断选对了没有
            choice.sort(reverse=True)
            if int(choice[0]) > len(cla_info['info']):
                print('仔细看看你选对了没有')
                return False
            # 选择的个数
            cho_len = len(choice)
            # 打印选择的课程
            print(f'{cla_info["username"][0].strip()},你选择了{cho_len}个课程，如下：')
            print('*' * 50)
            #需要提交到刷课的课程ID集合
            cho_list = []
            for n in choice:
                cho_dic = {}
                print(cla_info['info'][int(n) - 1]['name'])
                cho_dic['name'] = (cla_info['info'][int(n) - 1]['name'])
                cho_dic['ID'] = (cla_info['info'][int(n) - 1]['data'])
                cho_list.append(cho_dic)

            # print(cho_list)
            print('*' * 50)
            sure = input('确认请回车，退出任意键！')
            if sure is '':
                print('开始刷分数')
                bk._index(cho_list)
            else:
                print('你啥也没选择')
            print('全部刷完了')
        else:
            print('啥也选呀！')

