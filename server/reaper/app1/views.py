from django.shortcuts import render
from django.http import HttpResponse
import json
import re
import IPy
import pymysql
import time
from .sqlop import *
from .forms import TaskForm


# config all
token = "123456"
host = '192.168.1.111'
user = 'root'
pwd = '123456'
database = 'reaper'


def index(request):
    if request.COOKIES.get('key', '123456'):
        messagetask = ""
        if request.method == 'POST':
            # 接受request.POST参数构造form类的实例
            form = TaskForm(request.POST)
            if form.is_valid(): # 判断参数合法性
                param1 = form.cleaned_data['task_domain'] # 获取表单字段
                result = SelectTask('0', host, user, pwd, database) # 去重
                if result:
                    exist_task = [x[1] for x in result]
                    if param1 in exist_task:
                        messagetask = "任务已经存在，等待执行"
                else:
                    result = InserTask(param1, host, user, pwd, database)
                    if result:
                        messagetask = "成功加入任务"
                    else:
                        messagetask = "任务加入异常"
            form = TaskForm()
        # 如果是通过GET方法请求数据，返回一个空的表单
        else:
            form = TaskForm()
        return render(request, 'forms-basic.html', {'form':form, 'messagetask':messagetask})# 防止中文乱码的返回形式
    else:
        result = {"data":{}, "status":403, "msg":"未授权"}
        return HttpResponse(json.dumps(result,ensure_ascii=False),content_type="application/json,charset=utf-8")# 防止中文乱码的返回形式




def queryweb(request):
    param = request.GET.keys()
    if request.COOKIES.get('key', '123456'):
        if not 'param1' in param:
            result = {"data":{}, "status":203, "msg":"参数错误"}
            return HttpResponse(json.dumps(result,ensure_ascii=False),content_type="application/json,charset=utf-8")# 防止中文乱码的返回形式
        else:
            param1 = request.GET['param1']
            result = SelectDomain(param1, host, user, pwd, database)
            return render(request, 'tables-data.html', {'result':result})# 防止中文乱码的返回形式
    else:
        result = {"data":{}, "status":403, "msg":"未授权"}
        return HttpResponse(json.dumps(result,ensure_ascii=False),content_type="application/json,charset=utf-8")# 防止中文乱码的返回形式




'''历史版本
        #判断是否是ip，再a.com，利用domain查询空数据就默认单个子域名
        param1 = request.GET['param1']
        iplist = []
        if bool(re.search('[a-z]', param1)):
            db = pymysql.connect("localhost","root","123456","reaper")
            cursor = db.cursor()
            sql0 = "select ip from domainre where domain = '{}' and personkey = '{}'".format(param1, param2)####先主后副
            cursor.execute(sql0) # 执行sql语句
            results = cursor.fetchall()
            iplist = [x[0] for x in results]
            if not iplist:
                sql1 = "select ip from domainre where subdomain = '{}' and personkey = '{}'".format(param1, param2)####先主后副
                cursor.execute(sql1) # 执行sql语句
                results = cursor.fetchall()
                iplist = [x[0] for x in results]
            if not iplist:
                result = {"data":{},"code":"202"}
                return HttpResponse(json.dumps(result,ensure_ascii=False),content_type="application/json,charset=utf-8")# 防止中文乱码的返回形式
            try:
                sql2 = "select ip,port,banner,title from portre where ip in (%s) and (banner = 'http' or banner = 'https') and personkey = '" % ','.join(['%s'] * len(iplist))+param2+"'"
                cursor.execute(sql2, iplist) # 执行sql语句
                results = cursor.fetchall()
                demojson = {} # 临时变量参数
                if results:
                    url_list = [x[2]+"://"+x[0]+":"+x[1] for x in results] # 拿到https://1.1.1.1:443 形式
                    title_list = [x[3] for x in results] # 拿到title
                    for i in range(len(url_list)):
                        demojson.update({url_list[i]:title_list[i]})
                db.close()
                result = {"data":demojson,"code":"200"}
                return HttpResponse(json.dumps(result,ensure_ascii=False),content_type="application/json,charset=utf-8")# 防止中文乱码的返回形式
            except:
                result = {"data":{},"code":"202"}
                return HttpResponse(json.dumps(result,ensure_ascii=False),content_type="application/json,charset=utf-8")# 防止中文乱码的返回形式
        else:
            if ',' in param1:
                iplist = param1.split(",")
            else:
                ips = IPy.IP(param1) # 解析ip格式，ips类型<class 'IPy.IP'>
                iplist = [str(p) for p in ips]
            if not iplist:
                result = {"data":{},"code":"202"}
                return HttpResponse(json.dumps(result,ensure_ascii=False),content_type="application/json,charset=utf-8")# 防止中文乱码的返回形式
            try:
                db = pymysql.connect("localhost","root","123456","reaper")
                cursor = db.cursor()
                sql2 = "select ip,port,banner,title from portre where ip in (%s) and (banner = 'http' or banner = 'https' and personkey = '" % ','.join(['%s'] * len(iplist))+param2+"'"
                results = cursor.fetchall()
                url_list = [x[2]+"://"+x[0]+":"+x[1] for x in results] # 拿到https://1.1.1.1:443 形式
                title_list = [x[3] for x in results] # 拿到title
                demojson = {} # 临时变量参数
                for i in range(len(url_list)):
                    demojson.update({url_list[i]:title_list[i]})
                db.close()
                result = {"data":demojson,"code":"200"}
                return HttpResponse(json.dumps(result,ensure_ascii=False),content_type="application/json,charset=utf-8")# 防止中文乱码的返回形式
            except:
                result = {"data":{},"code":"202"}
                return HttpResponse(json.dumps(result,ensure_ascii=False),content_type="application/json,charset=utf-8")# 防止中文乱码的返回形式
'''

'''暂时关闭
def queryport(request):
    param = request.GET.keys()
    if not 'key' in param:
        result = {"data":{},"code":"202"}
        return HttpResponse(json.dumps(result,ensure_ascii=False),content_type="application/json,charset=utf-8")# 防止中文乱码的返回形式
    elif not 'param1' in param:
        result = {"data":{},"code":"202"}
        return HttpResponse(json.dumps(result,ensure_ascii=False),content_type="application/json,charset=utf-8")# 防止中文乱码的返回形式
    else:
        #判断是否是ip，再a.com，利用domain查询空数据就默认单个子域名
        param1 = request.GET['param1']
        param2 = request.GET['key']
        iplist = []
        if bool(re.search('[a-z]', param1)):
            db = pymysql.connect("localhost","root","123456","reaper")
            cursor = db.cursor()
            sql0 = "select ip from domainre where domain = '{}' and personkey = '{}'".format(param1, param2)####先主后副
            cursor.execute(sql0) # 执行sql语句
            results = cursor.fetchall()
            iplist = [x[0] for x in results]
            if not iplist:
                sql1 = "select ip from domainre where subdomain = '{}' and personkey = '{}'".format(param1, param2)####先主后副
                cursor.execute(sql1) # 执行sql语句
                results = cursor.fetchall()
                iplist = [x[0] for x in results]
            if not iplist:
                result = {"data":{},"code":"202"}
                return HttpResponse(json.dumps(result,ensure_ascii=False),content_type="application/json,charset=utf-8")# 防止中文乱码的返回形式
            try:
                sql2 = "select ip,port,banner,state from portre where ip in (%s)" % ','.join(['%s'] * len(iplist))+" and personkey = '{}'".format(param2)
                cursor.execute(sql2, iplist) # 执行sql语句
                results = cursor.fetchall()
                demojson = {} # 临时变量参数
                for x in results:
                    demojson.update({x[0]:{}})
                for x in results:
                    demojson[x[0]].update({x[1]:{'banner':x[2],'state':x[3]}})
                db.close()
                result = {"data":demojson,"code":"200"}
                return HttpResponse(json.dumps(result,ensure_ascii=False),content_type="application/json,charset=utf-8")# 防止中文乱码的返回形式
            except:
                result = {"data":{},"code":"202"}
                return HttpResponse(json.dumps(result,ensure_ascii=False),content_type="application/json,charset=utf-8")# 防止中文乱码的返回形式
        else:
            if ',' in param1:
                iplist = param1.split(",")
            else:
                ips = IPy.IP(param1) # 解析ip格式，ips类型<class 'IPy.IP'>
                iplist = [str(p) for p in ips]
            if not iplist:
                result = {"data":{},"code":"202"}
                return HttpResponse(json.dumps(result,ensure_ascii=False),content_type="application/json,charset=utf-8")# 防止中文乱码的返回形式
            try:
                db = pymysql.connect("localhost","root","123456","reaper")
                cursor = db.cursor()
                sql2 = "select ip,port,banner,state from portre where ip in (%s)" % ','.join(['%s'] * len(iplist))+" and personkey = '{}'".format(param2)
                cursor.execute(sql2, iplist) # 执行sql语句
                results = cursor.fetchall()
                demojson = {} # 临时变量参数
                for x in results:
                    demojson.update({x[0]:{}})
                for x in results:
                    demojson[x[0]].update({x[1]:{'banner':x[2],'state':x[3]}})
                db.close()
                result = {"data":demojson,"code":"200"}
                return HttpResponse(json.dumps(result,ensure_ascii=False),content_type="application/json,charset=utf-8")# 防止中文乱码的返回形式
            except:
                result = {"data":{},"code":"202"}
                return HttpResponse(json.dumps(result,ensure_ascii=False),content_type="application/json,charset=utf-8")# 防止中文乱码的返回形式
'''

def querytask(request):
    if request.COOKIES.get('key', '123456'):
        result = SelectTask('3', host, user, pwd, database)
        return render(request, 'tables-data2.html', {'result':result})# 防止中文乱码的返回形式
    else:
        result = {"data":{}, "status":403, "msg":"未授权"}
        return HttpResponse(json.dumps(result,ensure_ascii=False),content_type="application/json,charset=utf-8")# 防止中文乱码的返回形式





def newfullscan(request):
    if request.COOKIES.get('key', '123456'):
        messagetask = ""
        if request.method == 'POST':
            # 接受request.POST参数构造form类的实例
            form = TaskForm(request.POST)
            if form.is_valid(): # 判断参数合法性
                param1 = form.cleaned_data['task_domain'] # 获取表单字段
                result = SelectTask('0', host, user, pwd, database) # 去重
                if result:
                    exist_task = [x[1] for x in result]
                    if param1 in exist_task:
                        messagetask = "任务已经存在，等待执行"
                else:
                    result = InserTask(param1, host, user, pwd, database)
                    if result:
                        messagetask = "成功加入任务"
                    else:
                        messagetask = "任务加入异常"
            form = TaskForm()
        # 如果是通过GET方法请求数据，返回一个空的表单
        else:
            form = TaskForm()
        return render(request, 'forms-basic.html', {'form':form, 'messagetask':messagetask})# 防止中文乱码的返回形式
    else:
        result = {"data":{}, "status":403, "msg":"未授权"}
        return HttpResponse(json.dumps(result,ensure_ascii=False),content_type="application/json,charset=utf-8")# 防止中文乱码的返回形式

    


'''历史版本
        #任务直接存储，处理问题交给运行部分
        param1 = request.GET['param1']
        param2 = request.GET['key']
        db = pymysql.connect("localhost","root","123456","reaper")
        cursor = db.cursor()
        sql0  = "select id from owner where personkey = '{}'".format(param2)
        cursor.execute(sql0)
        results = cursor.fetchall()
        if not results:
            result = {"data":"身份异常，请确认key","code":"201"}
            return HttpResponse(json.dumps(result,ensure_ascii=False),content_type="application/json,charset=utf-8")# 防止中文乱码的返回形式
        sql  = "select id from taskre where state = 'wait' and task = '{}' and type = 'fullscan' and personkey = '{}'".format(param1,param2)
        cursor.execute(sql)
        results = cursor.fetchall()
        if results:
            result = {"data":"任务已经存储,排队执行中,请勿重复提交","code":"201"}
            return HttpResponse(json.dumps(result,ensure_ascii=False),content_type="application/json,charset=utf-8")# 防止中文乱码的返回形式
        try:
            sql1 = "INSERT INTO taskre(task, state, type, updatetime, personkey) VALUES ('{}','wait','fullscan','{}','{}')".format(param1,str(int(time.time())), param2)
            try:
                cursor.execute(sql1) # 执行sql语句
                db.commit()         # 提交到数据库执行
            except:
                db.rollback()       # 如果发生错误则回滚
            db.close()
            result = {"data":"任务已经存储,等待执行","code":"200"}
            return HttpResponse(json.dumps(result,ensure_ascii=False),content_type="application/json,charset=utf-8")# 防止中文乱码的返回形式
        except:
            result = {"data":"服务器异常","code":"202"}
            return HttpResponse(json.dumps(result,ensure_ascii=False),content_type="application/json,charset=utf-8")# 防止中文乱码的返回形式
'''

'''暂时关闭
def newportscan(request):
    param = request.GET.keys()
    if not 'key' in param:
        result = {"data":{},"code":"202"}
        return HttpResponse(json.dumps(result,ensure_ascii=False),content_type="application/json,charset=utf-8")# 防止中文乱码的返回形式
    elif not 'param1' in param:
        result = {"data":{},"code":"202"}
        return HttpResponse(json.dumps(result,ensure_ascii=False),content_type="application/json,charset=utf-8")# 防止中文乱码的返回形式
    else:
        #任务直接存储，处理问题交给运行部分
        param1 = request.GET['param1']
        param2 = request.GET['key']
        db = pymysql.connect("localhost","root","123456","reaper")
        cursor = db.cursor()
        sql0  = "select id from owner where personkey = '{}'".format(param2)
        cursor.execute(sql0)
        results = cursor.fetchall()
        if not results:
            result = {"data":"身份异常，请确认key","code":"201"}
            return HttpResponse(json.dumps(result,ensure_ascii=False),content_type="application/json,charset=utf-8")# 防止中文乱码的返回形式
        sql  = "select id from taskre where state = 'wait' and task = '{}' and type = 'portscan' and personkey = '{}'".format(param1,param2)
        cursor.execute(sql)
        results = cursor.fetchall()
        if results:
            result = {"data":"任务已经存储,排队执行中,请勿重复提交","code":"201"}
            return HttpResponse(json.dumps(result,ensure_ascii=False),content_type="application/json,charset=utf-8")# 防止中文乱码的返回形式
        try:
            sql1 = "INSERT INTO taskre(task, state, type, updatetime, personkey) VALUES ('{}','wait','portscan','{}','{}')".format(param1,str(int(time.time())), param2)
            try:
                cursor.execute(sql1) # 执行sql语句
                db.commit()         # 提交到数据库执行
            except:
                db.rollback()       # 如果发生错误则回滚
            db.close()
            result = {"data":"任务已经存储,等待执行","code":"200"}
            return HttpResponse(json.dumps(result,ensure_ascii=False),content_type="application/json,charset=utf-8")# 防止中文乱码的返回形式
        except:
            result = {"data":"服务器异常","code":"202"}
            return HttpResponse(json.dumps(result,ensure_ascii=False),content_type="application/json,charset=utf-8")# 防止中文乱码的返回形式
'''