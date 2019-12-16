import pymysql



def InserDomain(domain_result, domain):
    db = pymysql.connect("localhost","root","123456","reaper")
    cursor = db.cursor()
    for x in domain_result:
        sql2 = "select ip from domainre where ip = '{}'".format(x[1])
        cursor.execute(sql2) # 执行sql语句
        results2 = cursor.fetchall()
        if results2:
            continue
        sql = "INSERT INTO domainre(subdomain, ip, domain) VALUES ('{}','{}','{}')".format(x[0],x[1],domain)
        try:
            cursor.execute(sql) # 执行sql语句
            db.commit()         # 提交到数据库执行
        except:
            db.rollback()       # 如果发生错误则回滚
    db.close()

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

def InserPort(server_info):
    db = pymysql.connect("localhost","root","123456","reaper")
    cursor = db.cursor()
    urllist = [x for x in server_info]
    for u in urllist:
        for p in server_info[u]['port']:
            sql = "INSERT INTO portre(ip, port, portdata) VALUES ('{}','{}','{}')".format(server_info[u]['ip'], p, server_info[u]['port'][p])
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