import socket
import sys
import copy
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
import multiprocessing as mp
import requests
from bs4 import BeautifulSoup
import telnetlib



class portburst():
    def __init__(self, server_list, server_info, threadnum, startnum, stopnum):
        self.server_list = server_list   # after doamin scan ,get domain_result
        self.server_info = server_info   # save banner dict
        self.server_port = {}           # a demo , save server scanned
        self.startnum = startnum   # according to -p , we use two strategies
        self.stopnum = stopnum
        self.threadnum = threadnum
        self.weakport = ['21', '22', '23', '80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '90', '161', '389', '443',
'445', '873', '1025', '1099', '1433', '1521', '2082', '2083', '2222', '2601', '2604', '3128', '3306', '3312', '3311', '3389', '4440', '4848', '5432', '5560', '7778', '5900', '5901', '5902', '5902', '5984', '6082', '6379', '7001', '7002', '7778', '8080', '8649', '8081', '8088', '8090', '8083', '8649', '9000',
'9200', '9043', '10000', '11211', '27017', '28017', '50000', '50060', '50030']
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8',
            'Referer': 'https://www.baidu.com',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'close',
        }
        self.s = requests.session()
        self.s.headers.update(self.headers)
        self.run()

    def get_socket_info(self, target_ip, target_port):
        #socket get banner
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.3)
            s.connect((target_ip, target_port))
            s.send(b'HELLO\r\n')
            data = s.recv(1024).split(b'\r\n')[0].strip(b'\r\n')
            return True, data
        except Exception as e:
            return False,'off'
    
    def scan(self, target_server, scan_port):
        ret = {}
        try:
            flag,res = self.get_socket_info(target_ip=target_server, target_port=int(scan_port))
            if flag:
                res = str(res, encoding="utf-8")
                print('[+] -- open   {}'.format(str(scan_port)))
                if ('HTTP' in res) or ('HTML' in res):
                    try:
                        html = self.s.get("http://"+target_server+":"+str(scan_port), timeout=3)
                        html.encoding = html.apparent_encoding
                        soup= BeautifulSoup(html.text,'lxml')
                        param_ret = {'name':'http', 'state':'open'}
                        param_ret.update({'title':soup.title.string})
                        ret.update({str(scan_port):param_ret})
                    except:
                        try:
                            html = self.s.get("https://"+target_server+":"+scan_port, timeout=3)
                            html.encoding = html.apparent_encoding
                            soup= BeautifulSoup(html.text,'lxml')
                            param_ret = {'name':'https', 'state':'open'}
                            param_ret.update({'title':soup.title.string})
                            ret.update({str(scan_port):param_ret})
                        except:
                            ret[scan_port]={'name':'http', 'state':'close'}
                else:
                    ret[scan_port]={'name':'none', 'state':'open'}
                self.server_info[target_server].update(ret)
        except Exception as e:
            print(str(scan_port) +'\t' +e)


    def get_ip_status(self, ip, port, xkey):
        server = telnetlib.Telnet()      # 创建一个Telnet对象
        ret = {}
        try:
            server.open(ip,port,timeout=0.3)         # 利用Telnet对象的open方法进行tcp链接
            ret[str(port)]={'name':'none', 'state':'open'}
            print(ret)
            if not str(port) in xkey:
                self.server_info[ip].update(ret)
        except:
            pass
        server.close()

    # add tasks to threading pools
    def run(self):
        with ThreadPoolExecutor(max_workers=self.threadnum) as executor:
            tasks = []
            for target_ip in self.server_list:
                tasks = []
                for port in range(self.startnum, self.stopnum, 1):
                    tasks.append(executor.submit(self.scan, str(target_ip), str(port)))
                wait(tasks, return_when=ALL_COMPLETED)
        
        for x in self.server_list:
            xkey  = list(self.server_info[x].keys())   # 拿到目前每个ip的存活端口（已经检测端口）
            with ThreadPoolExecutor(max_workers=100) as executor:
                tasks = []
                for port in range(self.startnum, self.stopnum, 1):
                    tasks.append(executor.submit(self.get_ip_status, str(x), int(port), xkey))
                wait(tasks, return_when=ALL_COMPLETED)
        

'''
['21', '22', '23', '80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '90', '161', '389', '443',
'445', '873', '1025', '1099', '1433', '1521', '2082', '2083', '2222', '2601', '2604', '3128', '3306', '3312', '3311', '3389', '4440', '4848', '5432', '5560', '7778', '5900', '5901', '5902', '5902', '5984', '6082', '6379', '7001', '7002', '7778', '8080', '8649', '8081', '8088', '8090', '8083', '8649', '9000',
'9200', '9043', '10000', '11211', '27017', '28017', '50000', '50060', '50030']
'''