# ! /usr/bin/python
# -*- coding:utf-8 -*-


import aiohttp, asyncio
import time
import difflib
import random
import requests
from urllib import parse
import logging
import colorlog

handler = colorlog.StreamHandler()
formatter = colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s [%(name)s] [%(levelname)s] %(message)s%(reset)s',
    datefmt=None,
    reset=True,
    log_colors={
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
    },
    secondary_log_colors={},
    style='%')
handler.setFormatter(formatter)
log = colorlog.getLogger('logdir')
log.addHandler(handler)
log.setLevel(logging.INFO)




class dirburst(object):
    def __init__(self, scanSite, scanDict, coroutineNum, x_code, largeparam, lineparam, w_buff):
        self.scanSite = scanSite  # focus this url need a / end
        self.scanDict = scanDict
        self.loop = asyncio.get_event_loop()  # make a eventloop
        self.sem = asyncio.Semaphore(coroutineNum)
        self.tasks = []
        self.x_code = x_code  # stop some response code, default 404
        self.largeparam = largeparam  # for heuristicAnalysic
        self.key = largeparam
        self.lineparam = lineparam    # for heuristicAnalysic
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8',
            'Referer': 'https://www.baidu.com',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'close',
        }
        self.loop = asyncio.get_event_loop()
        self.scan_remain = 0
        self.find_total = 0
        self.w_buff = w_buff

    async def run(self):
        async with aiohttp.ClientSession() as session:
            tasks = []
            [tasks.append(self.control_sem(self.scanSite + '{}'.format(i), session)) for i in
             self.scanDict]  # assemble tasks
            await asyncio.wait(tasks)

    async def control_sem(self, url, session):
        async with self.sem:
            await self.fetch(url, session)

    async def fetch(self, url, session):
        async with session.get(url, headers=self.headers) as resp:
            status_code = resp.status
            if status_code != 404 and (status_code not in self.x_code):
                try:
                    data = await resp.text()
                    info = parse.urlsplit(url)
                    netloc = info.netloc[0:info.netloc.index(':')]
                    port = info.netloc[info.netloc.index(':') + 1:]
                    data_len = len(data)
                    data_line = len(data.split('\n'))
                    if data_len == self.key:
                        self.w_buff.put({'netloc': netloc, 'url': self.scanSite, 'port': port, 'status_code': {"code" : status_code, "size" : data_len, "line": data_line}})
                        log.info("code：" + str(status_code) + "    " + "line：" + str(data_line) + "     "  +"size：" + str(data_len) + "     " + self.scanSite)
                        self.key = 1
                        self.find_total += 1
                    else:
                        pass

                    if data_len != self.largeparam and data_line != self.lineparam:
                        self.w_buff.put({'netloc': netloc, 'url': url, 'port': port, 'status_code': {"code" : status_code, "size" : data_len, "line": data_line}})
                        log.info("code：" + str(status_code) + "    " + "line：" + str(data_line) + "     "  +"size：" + str(data_len) + "     " + url)
                        self.find_total += 1
                    else:
                        pass
                except:
                    pass
            else:
                pass

    def start(self):
        self.loop.run_until_complete(self.run())
'''

class dirsemburst(object):
    def __init__(self, scanSite, scanDict, coroutineNum, x_code, largeparam, lineparam, server_info_list):
        self.scanSite = scanSite  # focus this url need a / end
        self.scanDict = scanDict
        self.loop = asyncio.get_event_loop()  # make a eventloop
        self.sem = asyncio.Semaphore(coroutineNum)
        self.tasks = []
        self.x_code = x_code  # stop some response code, default 404
        self.largeparam = largeparam  # for heuristicAnalysic
        self.lineparam = lineparam    # for heuristicAnalysic
        self.key = largeparam
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8',
            'Referer': 'https://www.baidu.com',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'close',
        }
        self.loop = asyncio.get_event_loop()
        self.scan_remain = 0
        self.find_total = 0
        self.server_info_list = server_info_list

    async def run(self):
        async with aiohttp.ClientSession() as session:
            tasks = []
            [tasks.append(self.control_sem(self.scanSite + '{}'.format(i), session)) for i in
             self.scanDict]  # assemble tasks
            await asyncio.wait(tasks)

    async def control_sem(self, url, session):
        async with self.sem:
            await self.fetch(url, session)

    async def fetch(self, url, session):
        async with session.get(url, headers=self.headers) as resp:
            status_code = resp.status
            if status_code != 404 and (status_code not in self.x_code):
                try:
                    data = await resp.text()
                    info = parse.urlsplit(url)
                    netloc = info.netloc[0:info.netloc.index(':')]
                    port = info.netloc[info.netloc.index(':') + 1:]
                    data_len = len(data)
                    data_line = len(data.split('\n'))
                    if data_len == self.key:
                        self.server_info_list.append({'netloc': netloc, 'url': self.scanSite, 'port': port, 'status_code': {"code":status_code,"size":data_len}})
                        log.info("code：" + str(status_code) + "    " + "line：" + str(data_line) + "     "  +"size：" + str(data_len) + "     " + self.scanSite)
                        self.key = 1
                        self.find_total += 1
                    else:
                        pass

                    if data_len != self.largeparam and data_line != self.lineparam:
                        self.server_info_list.append({'netloc': netloc, 'url': url, 'port': port, 'status_code': {"code":status_code,"size":data_len}})
                        log.info("code：" + str(status_code) + "    " + "line：" + str(data_line) + "     "  +"size：" + str(data_len) + "     " + url)
                        self.find_total += 1
                    else:
                        pass
                except:
                    pass
            else:
                pass

    def start(self):
        self.loop.run_until_complete(self.run())

'''



class HeuristicAnalysis(object):
    def __init__(self, scanSite):
        self.scanSite = scanSite
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8',
            'Referer': 'https://www.baidu.com',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'close',
        }

    def stringSimilar(self, s1, s2):
        return difflib.SequenceMatcher(None, s1, s2).quick_ratio()

    def createToken(self):
        token = ''
        for i in range(16):
            token = token + random.choice('abcdefghijklmnopqrstuvwxyz1234567890')
        return token

    def TestNetwork(self):
        try:
            s = requests.session()
            s.headers.update(self.headers)
            html = s.get(self.scanSite, timeout=3)
            if html.status_code:
                return True
            else:
                return False
        except:
            return False

    def scan(self):
        s = requests.session()
        s.headers.update(self.headers)
        html = s.get(self.scanSite + self.createToken())
        html.encoding = html.apparent_encoding
        if html.status_code == 404:
            return True, 1, 1
        else:
            data1 = html.text
            html2 = s.get(self.scanSite + self.createToken())
            html2.encoding = html.apparent_encoding
            if html2.status_code == 404:
                return True, 1, 1
            else:
                data2 = html2.text
                similar_param = self.stringSimilar(data1, data2)
                if similar_param > 0.9:  # set limit 0.9, you can flexble choose
                    return False, len(data1), len(data1.split('\n'))
                else:
                    return True, 1, 1

'''
def dirStart(url_3, dir_dict, coroutineNum, x_code):
    server_info_list = []
    sss = HeuristicAnalysis(url_3)
    if sss.TestNetwork():
        a, b, c = sss.scan()
        print("stopsize:"+str(b)+"      stopline:"+str(c))
        aaa = dirsemburst(url_3, dir_dict, coroutineNum, x_code, b, c, server_info_list)
        aaa.start()
    else:
        info = parse.urlsplit(url_3)
        netloc = info.netloc[0:info.netloc.index(':')]
        port = info.netloc[info.netloc.index(':') + 1:]
        server_info_list.append({'netloc': netloc, 'url': url_3, 'port': port, 'status_code': 'NETWORK ERROR.'})
    return server_info_list

'''

def process_start(url_list, dir_dict, coroutineNum, x_code, w_buff):
    flag = 0
    for u in url_list:
        flag +=1 
        print('\033[1;45m '+str(flag)+' \033[0m')  # 有高亮
        sss = HeuristicAnalysis(u)
        if sss.TestNetwork():
            a, b, c = sss.scan()
            aaa = dirburst(u, dir_dict, coroutineNum, x_code, b, c, w_buff)
            aaa.start()
        else:
            info = parse.urlsplit(u)
            netloc = info.netloc[0:info.netloc.index(':')]
            port = info.netloc[info.netloc.index(':') + 1:]
            w_buff.put({'netloc': netloc, 'url': u, 'port': port, 'status_code': 'NETWORK ERROR.'})
            pass

if __name__ == "__main__":
    # # t1 = time.time()
    dir_path = "D:/1tools/reaper/dict/dicc1.txt"
    dir_dict = []
    with open(dir_path) as f:
        data = f.readlines()
        dir_dict = [i.replace("\n",'').replace("\r",'') for i in data]

    # # s = dirburst("https://www.anquanxiaozhan.com/",dir_dict,100,x_code=[403,302,301])
    # # s.start()
    # # t2 = time.time()
    # # print(t2-t1)
    # # process
    # # url_list = ['http://www.biligame.com:888/']


    sss = HeuristicAnalysis("http://ops.biligame.com:80/")
    if sss.TestNetwork():
        print("11111")
        # a, b, c = sss.scan()
        # print("stopsize:"+str(b)+"      stopline:"+str(c))
        # aaa = dirburst("https://www.biligame.com:443/", dir_dict, 100, [403,301], b, c, 1)
        # aaa.start()
    # print(len(dir_dict))
    # _demo = dirStart("https://www.anquanxiaozhan.com:443/",dir_dict,100,x_code=[])
    # print(_demo)

