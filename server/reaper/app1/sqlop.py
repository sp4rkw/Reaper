import pymysql
import time
import json

'''前后端django通杀'''

def SelectDomain(domain, host, user, pwd, database):
    db = pymysql.connect(host, user, pwd, database)
    cursor = db.cursor()
    sql = ""
    if domain == "*":
        sql = "select subdomain,title,wtime,cdn,record,ipwhere from subdomain"
    else:
        sql = "select subdomain,title,wtime,cdn,record,ipwhere from subdomain where groupdomain = '{}'".format(domain)
    cursor.execute(sql) # 执行sql语句
    results = cursor.fetchall()
    db.close()
    results_list = []
    iddomain = 1
    if results:
        for line in results:
            now = int(line[2])
            timeArray = time.localtime(now)
            otherStyleTime = time.strftime("%Y--%m--%d %H:%M:%S", timeArray)
            demo_list = [str(iddomain), line[0], line[1], line[3], line[4], line[5], otherStyleTime]# 顺序 id,url,title,cnd,record,ipwhere,time
            results_list.append(demo_list)
            iddomain = iddomain + 1
    else:
        results_list = []
    return results_list

def InserTask(domain, host, user, pwd, database):
    db = pymysql.connect(host, user, pwd, database)
    cursor = db.cursor()
    sql = "INSERT INTO subdomaintask(task, intime, flag) VALUES ('{}','{}','{}')".format(domain, str(int(time.time())), '0')
    result = "" # 成功与否的标志 1 ok
    try:
        cursor.execute(sql) # 执行sql语句
        db.commit()       # 提交到数据库执行
        result = "1"
    except:
        db.rollback()       # 如果发生错误则回滚
        result = "0"
    db.close()
    return result

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
    results_list = []
    i = 1
    if flag == '1' or flag == '0':
        if results:
            for line in results:
                intime = ""
                outtime = ""
                if line[1]:
                    now = int(line[1])
                    timeArray = time.localtime(now)
                    intime = time.strftime("%Y--%m--%d %H:%M:%S", timeArray)
                else:
                    intime = "未记录"
                if line[2]:
                    now = int(line[2])
                    timeArray = time.localtime(now)
                    outtime = time.strftime("%Y--%m--%d %H:%M:%S", timeArray)
                else:
                    outtime = "未记录"
                demo_list = [str(i), line[0], intime, outtime]
                results_list.append(demo_list)
                i = i + 1
        else:
            results_list = []
    else:
        if results:
            for line in results:
                intime = ""
                outtime = ""
                com = ""
                if line[1]:
                    now = int(line[1])
                    timeArray = time.localtime(now)
                    intime = time.strftime("%Y--%m--%d %H:%M:%S", timeArray)
                else:
                    intime = "未记录"
                if line[2]:
                    now = int(line[2])
                    timeArray = time.localtime(now)
                    outtime = time.strftime("%Y--%m--%d %H:%M:%S", timeArray)
                else:
                    outtime = "未记录"
                if line[3] == "1":
                    com = "已完成"
                else:
                    com = "未完成"
                demo_list = [str(i), line[0], intime, outtime, com]
                results_list.append(demo_list)
                i = i + 1
        else:
            results_list = []
    return results_list




if __name__ == "__main__":
    a = ['1','2','3','4']
    b = 'aaa'
    c = {'1':'a','2':'b','3':'c','4':'d'}
    host = '192.168.1.111'
    user = 'root'
    pwd = '123456'
    database = 'reaper'
    a = SelectDomain('chesupai.cn', host, user, pwd, database)
    # a = SelectTask('3', host, user, pwd, database)
    print(a)
    # InserDomain(a,b,c)







