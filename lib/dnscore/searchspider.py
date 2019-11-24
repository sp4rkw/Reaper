import requests
import asyncio
import aiohttp
import re
import sys

class DomainSpider():
    def __init__(self, url, domainlist):
        self.url = url
        self.event_loop = asyncio.get_event_loop()
        self.headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"}
        self.domainlist = domainlist
        self.find_total = 0
        self.scan_remain = 4000

    async def searchspider1(self, target):
        conn = aiohttp.TCPConnector(limit=100)
        self.scan_remain -= 10
        self.print_msg("remain " + str(self.scan_remain) + "  | Found" + str(self.find_total) + '\r')
        async with aiohttp.ClientSession(connector=conn) as session:
            async with session.get(target, headers=self.headers) as r:
                res = await r.text()
                demo = re.findall(r'style="text-decoration:none;">.{2,15}' + self.url , res)
                demo = [i.replace('style="text-decoration:none;">https://','') for i in demo]
                demo = [i.replace('style="text-decoration:none;">http://','') for i in demo]
                demo = [i.replace('style="text-decoration:none;">','') for i in demo]
                demo = set(demo)
                self.domainlist.update(demo)
                self.find_total += 1

    async def searchspider2(self, target):
        conn = aiohttp.TCPConnector(limit=100)
        self.scan_remain -= 10
        self.print_msg("remain " + str(self.scan_remain) + "  | Found" + str(self.find_total) + '\r')
        async with aiohttp.ClientSession(connector=conn) as session:
            async with session.get(target, headers=self.headers) as r:
                res = await r.text()
                demo = re.findall(r'<cite>.{2,15}<strong>' + self.url, res)
                demo = [i.replace('<cite>http://','') for i in demo]
                demo = [i.replace('<cite>https://','') for i in demo]
                demo = [i.replace('<strong>','') for i in demo]
                demo = set(demo)
                self.domainlist.update(demo)
                self.find_total += 1
        

    @staticmethod
    def print_msg(msg=None, left_align=True):
        if left_align:
            sys.stdout.write('\r' + msg)
        sys.stdout.flush()


    def run(self):
        tasks = []
        for i in range(0, 200):
            url = 'https://www.baidu.com/s?wd=site:%s&pn=%d' % (self.url, i*10)
            tasks.append(self.searchspider1(url))
        self.event_loop.run_until_complete(asyncio.gather(*tasks))
        tasks = []
        for i in range(0, 200):
            url = 'https://cn.bing.com/search?q=site:%s&first=%d' % (self.url, i * 10)
            tasks.append(self.searchspider2(url))
        self.event_loop.run_until_complete(asyncio.gather(*tasks))
        self.event_loop.close()     


# url = "test.com.cn"
# list1 = set()
# abc = DomainSpider(url,list1)
# abc.run()
# print(list1)











