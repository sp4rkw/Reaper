import asyncio
import os
import sys
import dns.resolver as Resolver
from lib.dnscore.dnsburst import dnsburst
from lib.dnscore.subdomain_api import *
from lib.webcore.titlesearch import *
# from lib.portcore.portscan import portburst
# from lib.portcore.port2scan import port2scan
from lib.webcore.cdn_detect import *
from lib.webcore.record import recordrun
from lib.dnscore.dnsprepare import dnsprepare
import requests
import plugins.sqlop as sqlop
import configparser
import re
import IPy
import pymysql
import time
import yagmail
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED




def step1(subname_dict, domain, host, user, pwd, database):
    print("[+ DNSBURST API] 开始DNS爆破")
    print("[+ DICT] 确认字典路径："+ subname_dict)
    # current_domain_list = sqlop.SelectDomain(domain, personkey) # 取出数据库已有数据，通过ip来进行去重
    timeout_domain = []
    allip_dict = {}
    domain_result = []  # subname list
    subname_list,domain_count = dnsprepare(subname_dict)  # scan domain list
    print("[+ DICT] 子域名字典已加载，共{}".format(str(domain_count)))
    s = dnsburst(
        domain=domain,
        subdomain_list=subname_list,
        allip_dict=allip_dict,
        create_limit=30000,
        timeout_domain=timeout_domain,
        domain_result=domain_result)
    s.get_analysis()
    s.run()

    api_sublist = subdomainApi(domain)# 各个api接口获取的字典列表

    domain_result.extend(api_sublist)
    domain_result = list(set(domain_result)) # 去重资产

    # for domain2 in domain_result:
    #     domain_result2 = [] # 第二层子域名收集
    #     print("[+ DICT] 子域名字典已加载，共{}".format(str(domain_count)))
    #     api_sublist = subdomainApi(domain2)# 各个api接口获取的字典列表
    #     domain_result2.extend(api_sublist)
    #     domain_result2 = list(set(domain_result2))
    #     domain_result.extend(domain_result2)

    # 网页标题信息/https信息收集
    print('[+ DNSBURST API] '+"总共发现" + str(len(domain_result)) + "个子域名")
    domain_result_add = []
    for subdomain in domain_result:
        domain_result_add.append("http://"+subdomain)
        domain_result_add.append("https://"+subdomain)
    title_result = titlerun(domain_result_add)

    # cdn加载
    cdn_demo,ip_demo = cdnrun(domain_result) # 回来的是没有http/https的形式，补全
    cdn_dict = {}
    ip_dict = {}
    for line in cdn_demo.keys():
        cdn_dict['http://'+line] = cdn_demo[line]
        cdn_dict['https://'+line] = cdn_demo[line]
    for line in ip_demo.keys():    
        ip_dict['http://'+line] = ip_demo[line]
        ip_dict['https://'+line] = ip_demo[line]
    
    # 备案信息查询模块
    recorddata = recordrun(domain)


    #domain_result, domain, title_result, cdn_dict, ip_dict, recorddata, host, user, pwd, database
    sqlop.InserDomain(domain_result_add, domain, title_result, cdn_dict, ip_dict, recorddata, host, user, pwd, database) # 插入子域名的结果
    # domain_result.clear() # 节约空间，释放变量



'''端口暂时不开启
def step2(domain, iplist, personkey, startnum, stopnum, threadnum):
    current_domain_list = ""
    if domain:
        current_domain_list = sqlop.SelectDomain(domain, personkey) # 第二次查询，相当于拿到目前数据库的子域名情况，只需要ip列表
    else:
        current_domain_list = iplist

    print("====================step2===================")
    server_info = {}
    for ip in current_domain_list:
        server_info.update({ip:{}})


    portburst(
    server_list = current_domain_list,
    server_info = server_info,
    startnum = startnum,
    stopnum = stopnum,
    threadnum = threadnum)

    print(server_info)
    sqlop.InserPort(server_info, personkey)
    port2scan(current_domain_list, personkey)
    print("Port scan has been over")
'''

def start(): # target 为目标
    config_txt = "config.ini" # 统一配置文件，将命令行模式转变为ini
    if os.name == 'nt':  # 根据当前路径重新赋值为绝对路径 
        config_txt = sys.path[0] + "\\" +config_txt
    else:
        config_txt = sys.path[0] + "/" +config_txt

    '''读取配置文件'''
    # 创建配置文件对象
    con = configparser.ConfigParser()
    # 读取文件
    con.read(config_txt, encoding='utf-8')
    # 获取所有section
    sections = con.sections()
    # 获取特定section
    items = dict(con.items('port')) # 端口参数 21-65534默认
    startnum = int(items['startnum'])
    items = dict(con.items('port')) 
    stopnum = int(items['stopnum'])
    items = dict(con.items('dns')) 	# dns爆破字典
    subname_dict = items['subdict']
    items = dict(con.items('port')) # 端口扫描线程数目控制
    threadnum = int(items['threadnum'])

    '''读取邮箱配置'''
    items = dict(con.items('email'))
    email = items['email']
    items = dict(con.items('email')) 
    code = items['code']
    items = dict(con.items('email'))
    emailpower = False if 'False' == items['emailpower'] else True

    '''读取mysql配置'''
    items = dict(con.items('mysql'))
    host = items['host']
    items = dict(con.items('mysql')) 
    user = items['user']
    items = dict(con.items('mysql')) 
    password = items['password']
    items = dict(con.items('mysql')) 
    database = items['database']
    
    print("[+ CONFIG] config.ini 配置加载完毕")

    '''处理子域名字典'''
    if os.name == 'nt':  # 根据当前路径重新赋值为绝对路径 
        subname_dict = sys.path[0] + '\\dict\\' + subname_dict
    else:
        subname_dict = sys.path[0] + '/dict/' + subname_dict

    '''取出任务，标记完成，添加取出任务时间'''
    task_list = [] # 目前数据库需要去执行的任务
    db = pymysql.connect(host, user, password, database)
    cursor = db.cursor()
    sql0 = "select task from subdomaintask where flag = '0'"
    cursor.execute(sql0) # 执行sql语句
    results = cursor.fetchall()
    if results:
        for line in results:
            task_list.append(line[0])
    del(results)
    

    if task_list:
        print("[+ TASK] 本次任务清单已加载完毕，共{}个任务".format(str(len(task_list))))
        for domain in task_list:
            step1(subname_dict, domain, host, user, password, database)
            sql1 = "UPDATE subdomaintask SET flag = '1', outtime = '{}' WHERE task = '{}'".format(str(int(time.time())), domain)
            try:
                cursor.execute(sql1) # 执行sql语句
                db.commit()         # 提交到数据库执行
            except:
                db.rollback()       # 如果发生错误则回滚
            print("[+ TASK] 任务 {} 已经完成".format(domain))
    else:
        print("[+ TASK] 本次未发现待完成任务，自动终止")




    '''target处理：1.域名 2. ip类-列表型，逗号分隔型'''

    # iplist = "" # 从ip开始
    
    # if bool(re.search('[a-z]', target)):
    #     domain = target
    #     step1(subname_dict, domain, personkey, pctnum, engine)
    #     step2(domain, None, personkey, startnum, stopnum, threadnum)
    # else:
    #     if ',' in target:
    #         iplist = target.split(",")
    #     else:
    #         ips = IPy.IP(target) # 解析ip格式，ips类型<class 'IPy.IP'>
    #         iplist = [str(p) for p in ips]
    #     step2(None, iplist, personkey, startnum, stopnum, threadnum)

    # if emailpower:
    #     # 登录你的邮箱
    #     yag = yagmail.SMTP(user = email, password = code, host = 'smtp.qq.com')
    #     # 发送邮件
    #     yag.send(to = [targetemail], subject = 'Reaper - 扫描任务已经结束', contents = ['下述任务已经扫描结束，请上线查看', target])


if __name__ == "__main__":
    start()