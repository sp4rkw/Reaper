import pymysql
import time
import json




def InserDomain(domain_result, domain, title_result, cdn_dict, ip_dict, recorddata, host, user, pwd, database):
    db = pymysql.connect(host, user, pwd, database)
    cursor = db.cursor()
    for x in domain_result:
        sql = "INSERT INTO subdomain(subdomain, wtime, title, cdn, record, ipwhere, groupdomain) VALUES ('{}','{}','{}','{}','{}','{}', '{}')".format(x, str(int(time.time())), title_result[x], cdn_dict[x], recorddata, ip_dict[x], domain)
        try:
            cursor.execute(sql) # 执行sql语句
            db.commit()       # 提交到数据库执行
        except:
            db.rollback()       # 如果发生错误则回滚
    db.close()

def SelectDomain(domain, host, user, pwd, database):
    db = pymysql.connect(host, user, pwd, database)
    cursor = db.cursor()
    sql = "select subdomain,title,wtime,fingerprint,waf from subdomain where groupdomain = '{}'".format(domain)
    cursor.execute(sql) # 执行sql语句
    results = cursor.fetchall()
    db.close()
    results_dict = {}
    if results:
        results_dict = {"data":{}, "status":200, "msg":"成功获取"}
        for line in results:
            results_dict['data'][line[0]] = {"title":line[1], "wtime":line[2], "fingerprint":line[3], "waf":line[4]}
    else:
        results_dict = {"status":201, "msg":"获取数据为空", "data":""}
    results_json = json.dumps(results_dict)
    return results_json

def InserTask(domain, host, user, pwd, database):
    db = pymysql.connect(host, user, pwd, database)
    cursor = db.cursor()
    sql = "INSERT INTO subdomaintask(task, intime, flag) VALUES ('{}','{}','{}')".format(domain, str(int(time.time())), '0')
    try:
        cursor.execute(sql) # 执行sql语句
        db.commit()       # 提交到数据库执行
    except:
        db.rollback()       # 如果发生错误则回滚
    db.close()

def SelectTask(flag, host, user, pwd, database):
    db = pymysql.connect(host, user, pwd, database)
    cursor = db.cursor()
    sql = "" 
    if flag == '1' or flag == '0':
        sql = "select task,intime,outtime from subdomaintask where flag = '{}'".format(flag)
    else:
        sql = "select task,intime,outtime,flag from subdomaintask"
    cursor.execute(sql) # 执行sql语句
    results = cursor.fetchall()
    db.close()
    results_dict = {}
    if flag == '1' or flag == '0':
        if results:
            results_dict = {"data":{}, "status":200, "msg":"成功获取"}
            for line in results:
                results_dict['data'][line[0]] = {"intime":line[1], "outtime":line[2]}
        else:
            results_dict = {"status":201, "msg":"获取数据为空", "data":""}
    else:
        if results:
            results_dict = {"data":{}, "status":200, "msg":"成功获取"}
            for line in results:
                results_dict['data'][line[0]] = {"intime":line[1], "outtime":line[2], "flag":line[3]}
        else:
            results_dict = {"status":201, "msg":"获取数据为空", "data":""}
    results_json = json.dumps(results_dict)
    return results_json

'''结构
{
    "status":200,
    "msg":"成功获取",
    "data":{
        "1.x.com":{
            "title":"demo1",
            "wtime":"121131331", #时间戳
            "fingerprint":"none",
            "waf":"none"
        },
        "2.x.com":{
            "title":"demo2",
            "wtime":"121131331", #时间戳
            "fingerprint":"none",
            "waf":"none"
        }
    }
  }
'''

if __name__ == "__main__":
    a = ['1','2','3','4']
    b = 'aaa'
    c = {'1':'a','2':'b','3':'c','4':'d'}
    host = '192.168.1.111'
    user = 'root'
    pwd = '123456'
    database = 'reaper'
    # a = SelectDomain('chesupai.cn', host, user, pwd, database)
    a = SelectTask('3', host, user, pwd, database)
    print(a)
    # InserDomain(a,b,c)












def DeleteDomain(domain):
    db = pymysql.connect("localhost","root","123456","reaper")
    cursor = db.cursor()
    sql = "delete * from domainre where domain ='{}'".format(domain)
    try:
        cursor.execute(sql) # 执行sql语句
        db.commit()         # 提交到数据库执行
    except:
        db.rollback()       # 如果发生错误则回滚
    db.close()

def InserPort(server_info, key):
    db = pymysql.connect("localhost","root","123456","reaper")
    cursor = db.cursor()
    for ip in server_info:
        sql2 = "select port from portre where ip = '{}' and personkey = '{}'".format(ip, key) # 二次扫描的时候，已经有结果的端口直接更新不插入
        cursor.execute(sql2) # 执行sql语句
        results = cursor.fetchall()
        results_list = [x[0] for x in results]
        for p in server_info[ip]:
            list_p = list(server_info[ip][p].keys()) # 拿到server_info中的所有key
            banner = server_info[ip][p]['name'] if 'name' in list_p else ""
            state = server_info[ip][p]['state'] if 'state' in list_p else ""
            title = server_info[ip][p]['title'] if 'title' in list_p else ""
            sql = ""
            if p in results_list:
                sql = "UPDATE portre SET banner = '{}', state = '{}', title = '{}', updatetime = '{}' WHERE ip ='{}' and port = '{}' and personkey = '{}'".format(banner, state, title, str(int(time.time())), ip, p, key)
            else:
                sql = "INSERT INTO portre(ip, port, banner, state, title, updatetime, personkey) VALUES ('{}','{}','{}','{}','{}','{}','{}')".format(ip, p, banner, state, title, str(int(time.time())), key)
            try:
                cursor.execute(sql) # 执行sql语句
                db.commit()         # 提交到数据库执行
            except:
                db.rollback()       # 如果发生错误则回滚
    db.close()

def DeletePort(domain):
    db = pymysql.connect("localhost","root","123456","reaper")
    cursor = db.cursor()
    sql = "delete from domainre where ip = (select DISTINCT ip from domainre where domain = '{}')".format(domain)
    try:
        cursor.execute(sql) # 执行sql语句
        db.commit()         # 提交到数据库执行
    except:
        db.rollback()       # 如果发生错误则回滚
    db.close()