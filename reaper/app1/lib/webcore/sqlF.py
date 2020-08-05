import pymysql
import time


def InserDomain(domain_result, title_result, status_result, cdn_dict, recorddata, ip_dict, domain):
    host = '127.0.0.1'
    user = 'root'
    pwd = 'd178f33f48514618'
    database = 'reaper'
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