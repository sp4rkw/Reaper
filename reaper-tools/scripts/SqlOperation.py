import pymysql,time,json




def InserDomain(domain_result, domain, title_result, status_result, cdn_dict, ip_dict, recorddata, host, user, pwd, database):
    db = pymysql.connect(host, user, pwd, database)
    cursor = db.cursor()
    for x in domain_result:
        sql = "INSERT INTO subdomain(subdomain, wtime, title, status, cdn, record, ipwhere, groupdomain) VALUES ('{}','{}','{}','{}','{}','{}', '{}', '{}')".format(x, str(int(time.time())), title_result[x], status_result[x], cdn_dict[x], recorddata, ip_dict[x], domain)
        try:
            cursor.execute(sql) # 执行sql语句
            db.commit()       # 提交到数据库执行
        except:
            db.rollback()       # 如果发生错误则回滚
    db.close()

'''
Desprition:
    用于去重提取所有子域名

Parameters:
    domain: 目标子域名/同名json文件处理
    host: 数据库ip
    user: 数据库用户
    pwd: 数据库用户对应密码
    database: reaper所在数据库

Returns:
    Null

Modify:2020-08-05 12:00:25
'''
def SelectDomain(domain, host, user, pwd, database):
    db = pymysql.connect(host, user, pwd, database)
    cursor = db.cursor()
    sql = "select subdomain,title from subdomain where groupdomain = '{}' and status = '{}'".format(domain, '200')
    cursor.execute(sql) # 执行sql语句
    results = cursor.fetchall()
    db.close()
    results_dict = {}
    if results:
        results_dict = {"data":{}, "status":200, "msg":"成功获取"}
        for line in results:
            results_dict['data'][line[0]] = {"title":line[1]}
    else:
        results_dict = {"status":201, "msg":"获取数据为空", "data":""}
    return results_dict

'''
Desprition:
    用于任务记录，将任务插入数据库

Parameters:
    domain: 目标子域名/同名json文件处理
    host: 数据库ip
    user: 数据库用户
    pwd: 数据库用户对应密码
    database: reaper所在数据库

Returns:
    Null

Modify:2020-08-04 16:44:01
'''
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


'''
Desprition:
    用于记录任务完成时间

Parameters:
    domain: 目标子域名/同名json文件处理
    host: 数据库ip
    user: 数据库用户
    pwd: 数据库用户对应密码
    database: reaper所在数据库

Returns:
    Null

Modify:2020-08-05 10:50:52
'''
def UpdateTask(domain, host, user, pwd, database):
    db = pymysql.connect(host, user, pwd, database)
    cursor = db.cursor()
    sql = "update subdomaintask set flag = '{}', outtime = '{}' where task = '{}'".format('1', str(int(time.time())), domain)
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