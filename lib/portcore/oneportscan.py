import logging
import colorlog
import socket
import sys
from concurrent.futures import ThreadPoolExecutor

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
logh = colorlog.getLogger('logh')
logh.addHandler(handler)
logh.setLevel(logging.INFO)


class Oneportburst():
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
    
    def scan(self, target_server, scan_port, nowi):
        ret = {}
        try:
            flag,res = self.get_socket_info(target_ip=target_server, target_port=scan_port)
            if flag:
                res = str(res, encoding="utf-8")
                logh.info('[+] -- open   {}\t{}'.format(str(scan_port), res))
                if res[:4] == 'HTTP':
                    ret[str(scan_port)]='https'
                elif 'html' in res:
                    ret[str(scan_port)]='http'
                else:
                    ret[str(scan_port)]=res  
                if scan_port == 27017:#[,6379,11211,5900,2375,2181,837]
                    self.server_unauthoried['check'][str(scan_port)]='Doubtful | MongoDB unauthoried leak'
                elif scan_port == 6379:
                    self.server_unauthoried['check'][str(scan_port)]='Doubtful | Redis unauthoried leak'
                elif scan_port == 11211:
                    self.server_unauthoried['check'][str(scan_port)]='Doubtful | Memcached unauthoried leak'
                elif scan_port == 2181:
                    self.server_unauthoried['check'][str(scan_port)]='Doubtful | ZooKeeper unauthoried leak'
                elif scan_port == 9200:
                    self.server_unauthoried['check'][str(scan_port)]='Doubtful | ElasticSearch unauthoried leak'
                self.server_port.update(ret)
        except Exception as e:
            logh.error(str(scan_port) +'\t' +e)
        
    

    # add tasks to threading pools
    def run(self):
        if self.ports:
            with ThreadPoolExecutor(self.threadnum) as executor:
                for i in range(self.scan_total):
                    for port in self.ports:
                        executor.submit(self.scan, self.server_list[i][1], int(port), i)
                    server_info_demo = {}
                    server_info_demo.update({'port':self.server_port})
                    self.server_port.clear()
                    server_info_demo.update({'ip':self.server_list[i][1]})
                    server_info_demo.update({'check':self.server_unauthoried})
                    self.server_info.update({self.server_list[i][0]:server_info_demo})
        else:
            with ThreadPoolExecutor(self.threadnum) as executor:
                for i in range(self.scan_total):
                    for port in range(self.startnum, self.stopnum, 1):
                        executor.submit(self.scan, self.server_list[i][1], port, i)
                    server_info_demo = {}
                    server_info_demo.update({'port':self.server_port})
                    self.server_port.clear()
                    server_info_demo.update({'ip':self.server_list[i][1]})
                    server_info_demo.update({'check':self.server_unauthoried})
                    self.server_info.update({self.server_list[i][0]:server_info_demo})
                    


