import nmap
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
import pymysql


class port2scan(object):
    def __init__(self, domain):
        self.domain = domain
        self.tasks = []
        self.run()

    def run(self):
        db = pymysql.connect("localhost","root","123456","reaper")
        cursor = db.cursor()
        sql1 = "select DISTINCT ip from domainre where domain = '{}'".format(self.domain)
        cursor.execute(sql1) # 执行sql语句
        results1 = cursor.fetchall()
        iplist = [row[0] for row in results1]
        with ThreadPoolExecutor(10) as executor:
            for ip in iplist:
                sql2 = "select port from portre where portdata = 'open' and ip = '{}'".format(ip)
                cursor.execute(sql2) # 执行sql语句
                results2 = cursor.fetchall()
                if not results2:
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
            sql = "UPDATE portre SET portdata = \"{}\" WHERE ip ='{}' and port = '{}'".format(portdata,ip,p)
            try:
                cursor.execute(sql)  # 执行SQL语句
                db.commit()          # 提交到数据库执行
            except:
                db.rollback()        # 发生错误时回滚
        cursor.close()


   