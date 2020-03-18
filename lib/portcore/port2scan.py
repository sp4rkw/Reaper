import nmap
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
import pymysql
import time
import json

class port2scan(object):
    def __init__(self, iplist, key): # 获取当前数据库目标域名对于的ip列表
        self.iplist = iplist
        self.personkey = key
        self.tasks = []
        self.run()

    def run(self):
        db = pymysql.connect("localhost","root","123456","reaper")
        cursor = db.cursor()
        with ThreadPoolExecutor(10) as executor:
            for ip in self.iplist:
                sql2 = "select port from portre where banner = 'none' and ip = '{}' and personkey = '{}'".format(ip, self.personkey)
                cursor.execute(sql2) # 执行sql语句
                results2 = cursor.fetchall()
                if not results2: # 判断是否存在取值，没有取值直接进下一轮循环
                    continue
                portlist = [row[0] for row in results2]
                port_str = ','.join(portlist)
                self.tasks.append(executor.submit(self.NmapPool,ip,port_str,portlist))
            wait(self.tasks, return_when=ALL_COMPLETED)
            db.close()

    def NmapPool(self, ip, port_str, portlist):
        nm = nmap.PortScanner()
        print("[+] -- rescan   {}".format(ip))
        nm.scan(ip, port_str,"-sS -sV -Pn")
        data = nm[ip]
        data = dict(data)
        db = pymysql.connect("localhost","root","123456","reaper")
        cursor = db.cursor()
        for p in portlist:
            p_int = int(p)
            portdata = str(data['tcp'][p_int]) if 'tcp' in data.keys() and p_int in data['tcp'].keys() else 'close'
            if portdata == "close":
                sql = "UPDATE portre SET state = 'close', updatetime = '{}' WHERE ip ='{}' and port = '{}' and personkey = '{}'".format(str(int(time.time())), ip, p, self.personkey)
                try:
                    cursor.execute(sql)  # 执行SQL语句
                    db.commit()          # 提交到数据库执行
                except:
                    db.rollback()        # 发生错误时回滚
            else:
                portdata = portdata.replace('\'','\"')
                portdata = json.loads(portdata)
                sql = "UPDATE portre SET banner = '{}', state = '{}', updatetime = '{}' WHERE ip ='{}' and port = '{}' and personkey = '{}'".format(portdata["name"], portdata["state"],str(int(time.time())), ip, p, self.personkey)
                try:
                    cursor.execute(sql)  # 执行SQL语句
                    db.commit()          # 提交到数据库执行
                except:
                    db.rollback()        # 发生错误时回滚
        cursor.close()


   