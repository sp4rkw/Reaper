# -*- coding: UTF-8 -*-
'''
Desprition:
    脚本用于配合reaper-web端使用

Author:
    闪光   https://sp4rkw.blog.csdn.net/

Modify:2020-08-04 16:34:09
'''

import os,configparser,sys,requests,pymysql,time,json
from scripts.SqlOperation import InserTask,UpdateTask,SelectDomain
from scripts.oneforall import rundomain
from scripts.ReaperLogo import get_init_params
from scripts.awvs import awvs_reaper,del_targets
'''
Desprition:
    读取本地配置文件并加载

Parameters:
    domain: 目标域名

Returns:
    Null

Modify:2020-08-04 17:18:44
'''
def start(domain, rtype): # target 为目标
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

    '''读取awvs配置'''
    items = dict(con.items('awvs'))
    awvs_token = items['token']
    items = dict(con.items('awvs')) 
    awvs_website = items['website']

    
    print("[+ CONFIG] config.ini 配置加载完毕")
    if rtype == '1':
        InserTask(domain, host, user, password, database)
        print("[+ TASK] 任务已经成功加入数据库，正在执行中")
        rundomain(domain, host, user, password, database)
        print("[+ TASK] 任务已经执行完毕，访问链接查看详细")
        UpdateTask(domain, host, user, password, database)
        print("[+ RESULT] http://127.0.0.1/queryweb?param1="+domain)
    elif rtype == '2':
        try:
            print("[+ TASK] 正在提取目标子域名，去除冗余数据中")# 去重机制两点，基于200，基于title
            data = SelectDomain(domain, host, user, password, database)
            domainlist = []
            titlelist = []
            if data['status'] == 201:
                print("[+ TASK] 数据提取失败，请检查系统中是否存在该域名资产")
            else:
                for domain in data['data']:
                    if data['data'][domain]['title'] not in titlelist:
                        titlelist.append(data['data'][domain]['title'])
                        domainlist.append(domain)
                print("[+ TASK] 数据提取成功，共 {} 条数据".format(str(len(domainlist))))
            awvs_reaper(domainlist, awvs_token, awvs_website)
            print("[+ TASK] AWVS扫描任务执行完毕，请前往 "+ awvs_website +"/#/scans")
        except:
            print("[+ TASK] awvs连接失败，请检查配置")
    else:
        try:
            del_targets(awvs_token, awvs_website)
            print("[+ TASK] AWVS清理任务执行完毕，请前往 "+ awvs_website +"/#/scans")
        except:
            print("[+ TASK] awvs连接失败，请检查配置")



if __name__ == "__main__":
    args = get_init_params()
    domain = args.domain
    rtype = args.type
    start(domain, rtype)

