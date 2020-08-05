import os,sys,json,pymysql,time
from scripts.cdn_detect import cdnrun
from scripts.titlesearch import titlerun
from scripts.record import recordrun
'''
Desprition:
    用于将oneforall获取的json文件解析出来放入reaper数据库

Parameters:
    domain: 目标子域名/同名json文件处理
    host: 数据库ip
    user: 数据库用户
    pwd: 数据库用户对应密码
    database: reaper所在数据库

Returns:
    Null

Modify:2020-08-04 16:10:54
'''
def rundomain(domain, host, user, pwd, database):
    # oneforall结果文件绝对路径获取
    if os.name == 'nt':  # 根据当前路径重新赋值为绝对路径 
        oneforall_json = sys.path[0] + "\\result\\" + domain + ".json"
    else:
        oneforall_json = sys.path[0] + "/result/" + domain + ".json"

    # 如果本地不存在该文件，直接返回
    if not os.path.exists(oneforall_json):
        print("[+ LOADING] "+ domain + ".json" + "文件不存在")
        return "fail"
    
    # 加载oneforall文件
    f = open(oneforall_json, "r", encoding="utf-8")
    oneforall = json.load(f)
    f.close()
    print("[+ JSONLOAD] "+ domain + ".json" + "文件已加载")

    # 网页标题信息/https信息收集
    domain_result_add = [] # 带http格式
    domain_result = [] # 不带http的格式
    banner_result = {}
    for line in oneforall:
        domain_result_add.append(line['url'])
        domain_result.append(line['subdomain'])
        if line['banner']:
            banner_result[line['url']] = line['banner'].replace("\'","")
        else:
            banner_result[line['url']] = 'none'     
    
    title_result,status_result = titlerun(domain_result_add)

    # cdn加载
    cdn_demo,ip_demo = cdnrun(domain_result) # 回来的是没有http/https的形式，补全
    cdn_dict = {}
    ip_dict = {}
    for line in cdn_demo.keys():
        cdn_dict['http://'+line] = cdn_demo[line]
    for line in ip_demo.keys():    
        ip_dict['http://'+line] = ip_demo[line]  
    
    # 备案信息查询模块
    recorddata = recordrun(domain)

    db = pymysql.connect(host, user, pwd, database)
    cursor = db.cursor()
    for x in domain_result_add:
        sql = "INSERT INTO subdomain(subdomain, wtime, title, status, banner, cdn, record, ipwhere, groupdomain) VALUES ('{}','{}','{}','{}','{}','{}', '{}', '{}', '{}')".format(x, str(int(time.time())), title_result[x], status_result[x], banner_result[x], cdn_dict[x], recorddata, ip_dict[x], domain)
        # try:
        cursor.execute(sql) # 执行sql语句
        db.commit()       # 提交到数据库执行
        # except:
        #     db.rollback()       # 如果发生错误则回滚
    db.close()
    return 1