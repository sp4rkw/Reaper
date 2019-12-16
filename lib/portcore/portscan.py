import logging
import colorlog
import socket
import sys
import copy
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
import multiprocessing as mp
import requests



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
logc = colorlog.getLogger('logc')
logc.addHandler(handler)
logc.setLevel(logging.INFO)


class portburst():
    def __init__(self, server_list, scan_total, server_info, ports, threadnum, startnum, stopnum):
        self.server_list = server_list   # after doamin scan ,get domain_result
        self.scan_total = scan_total
        self.server_info = server_info   # save banner dict
        self.server_port = {}           # a demo , save server scanned
        self.server_unauthoried = {}    # a demo , save unauthorized warning 
        self.startnum = startnum   # according to -p , we use two strategies
        self.stopnum = stopnum
        self.ports = ports
        self.threadnum = threadnum
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
    
    def scan(self, target_server, scanSite, scan_port, nowi):
        ret = {}
        try:
            flag,res = self.get_socket_info(target_ip=target_server, target_port=scan_port)
            if flag:
                res = str(res, encoding="utf-8")
                logc.info('[+] -- open   {}'.format(str(scan_port)))
                if ('HTTP' in res) or ('HTML' in res):
                    html = self.s.get("http://"+scanSite+":"+str(scan_port), timeout=3)
                    if html.status_code and scan_port != 443:
                        ret[str(scan_port)]="http"
                    else:
                        html = self.s.get("https://"+scanSite+":"+str(scan_port), timeout=3)
                        if html.status_code:
                            ret[str(scan_port)]="https"
                        else:
                            ret[str(scan_port)]='close'
                else:
                    ret[str(scan_port)]='open'  
                # if scan_port == 27017:#[,6379,11211,5900,2375,2181,837]
                #     self.server_unauthoried['check'][str(scan_port)]='Doubtful | MongoDB unauthoried leak'
                # elif scan_port == 6379:
                #     self.server_unauthoried['check'][str(scan_port)]='Doubtful | Redis unauthoried leak'
                # elif scan_port == 11211:
                #     self.server_unauthoried['check'][str(scan_port)]='Doubtful | Memcached unauthoried leak'
                # elif scan_port == 2181:
                #     self.server_unauthoried['check'][str(scan_port)]='Doubtful | ZooKeeper unauthoried leak'
                # elif scan_port == 9200:
                #     self.server_unauthoried['check'][str(scan_port)]='Doubtful | ElasticSearch unauthoried leak'
                self.server_port.update(ret)
        except Exception as e:
            logc.error(str(scan_port) +'\t' +e)
        
    
        
    # this method be used to display and flush
    @staticmethod
    def print_msg(msg=None, left_align=True):
        if left_align:
            sys.stdout.write('\r' + msg)
        sys.stdout.flush()

    # add tasks to threading pools
    def run(self):
        if self.ports:
            with ThreadPoolExecutor(self.threadnum) as executor:
                tasks = []
                for i in range(self.scan_total):
                    for port in self.ports:
                        tasks.append(executor.submit(self.scan, self.server_list[i][1], self.server_list[i][0], int(port), i))
                    wait(tasks, return_when=ALL_COMPLETED)
                    server_info_demo = mp.Manager().dict()
                    server_info_demo.update({'port':self.server_port})
                    self.server_port.clear()
                    server_info_demo.update({'ip':self.server_list[i][1]})
                    if self.server_unauthoried:
                        server_info_demo.update({'check':self.server_unauthoried})
                    else:
                        server_info_demo.update({'check':{'all_port':"no find unauthoried problem"}})
                    self.server_info.update({self.server_list[i][0]:dict(server_info_demo)})
        else:# p x-xxx
            with ThreadPoolExecutor(self.threadnum) as executor:
                tasks = []
                for i in range(self.scan_total):
                    for port in range(self.startnum, self.stopnum, 1):
                        tasks.append(executor.submit(self.scan, self.server_list[i][1], self.server_list[i][0], port, i))
                    wait(tasks, return_when=ALL_COMPLETED)
                    server_info_demo = mp.Manager().dict()
                    server_info_demo.update({'port':self.server_port})
                    # self.server_port.clear()
                    server_info_demo.update({'ip':self.server_list[i][1]})
                    if self.server_unauthoried:
                        server_info_demo.update({'check':self.server_unauthoried})
                    else:
                        server_info_demo.update({'check':{'all_port':"no find unauthoried problem"}})

                    # print(server_info_demo)
                    self.server_info.update({self.server_list[i][0]: dict(server_info_demo)})
                    # print(self.server_info)
