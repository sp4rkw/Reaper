from django.shortcuts import render
from django.http import HttpResponse
import json
import re
import time
from .sqlop import *
from .forms import TaskForm
from .forms import RecordForm
from app1 import task
from django.core import serializers


# auth token
cookies_key = "key"
cookies_value = "123456"


def index(request):
    if request.COOKIES.get(cookies_key) == cookies_value:
        result = {"data":{}, "status":403, "msg":"已授权"}
        return HttpResponse(json.dumps(result,ensure_ascii=False),content_type="application/json,charset=utf-8")# 防止中文乱码的返回形式
    else:
        result = {"data":{}, "status":403, "msg":"未授权"}
        return HttpResponse(json.dumps(result,ensure_ascii=False),content_type="application/json,charset=utf-8")# 防止中文乱码的返回形式

def xraypocgenerate(request):
    param = request.GET.keys()
    if request.COOKIES.get(cookies_key) == cookies_value:
        return render(request, 'xray-poc-generation.html')# 防止中文乱码的返回形式
    else:
        result = {"data":{}, "status":403, "msg":"未授权"}
        return HttpResponse(json.dumps(result,ensure_ascii=False),content_type="application/json,charset=utf-8")# 防止中文乱码的返回形式


def queryweb(request):
    param = request.GET.keys()
    if request.COOKIES.get(cookies_key) == cookies_value:
        if not 'param1' in param:
            result = {"data":{}, "status":203, "msg":"参数错误"}
            return HttpResponse(json.dumps(result,ensure_ascii=False),content_type="application/json,charset=utf-8")# 防止中文乱码的返回形式
        else:
            param1 = request.GET['param1']
            result = SelectDomain(param1)
            return render(request, 'tables-data.html', {'result':result})# 防止中文乱码的返回形式
    else:
        result = {"data":{}, "status":403, "msg":"未授权"}
        return HttpResponse(json.dumps(result,ensure_ascii=False),content_type="application/json,charset=utf-8")# 防止中文乱码的返回形式

def querytask(request):
    if request.COOKIES.get(cookies_key) == cookies_value:
        result = SelectTask()
        return render(request, 'tables-data2.html', {'result':result})# 防止中文乱码的返回形式
    else:
        result = {"data":{}, "status":403, "msg":"未授权"}
        return HttpResponse(json.dumps(result,ensure_ascii=False),content_type="application/json,charset=utf-8")# 防止中文乱码的返回形式

def queryrecord(request):
    form_title = '备案查询'
    if request.COOKIES.get(cookies_key) == cookies_value:
        record_data = {}
        messagetask = ""
        if request.method == 'POST':
            # 接受request.POST参数构造form类的实例
            form = RecordForm(request.POST)
            if form.is_valid(): # 判断参数合法性
                param1 = form.cleaned_data['querytype'] # 获取表单字段
                param2 = form.cleaned_data['record'] # 获取表单字段
                record_data = recordrun(param2, param1)
                # 首先要判断数据库有没有这个企业的数据，有的话直接查数据库，没有的话差接口存本地
                # 目前不考虑存本地先，只考虑查接口

                if record_data:
                    messagetask = "任务查询成功"
                else:
                    messagetask = "任务查询异常"
            form = RecordForm()
        # 如果是通过GET方法请求数据，返回一个空的表单
        else:
            form = RecordForm()
        return render(request, 'beian.html', {'form':form, 'messagetask':messagetask, 'result':record_data, 'form_title':form_title})# 防止中文乱码的返回形式
    else:
        result = {"data":{}, "status":403, "msg":"未授权"}
        return HttpResponse(json.dumps(result,ensure_ascii=False),content_type="application/json,charset=utf-8")# 防止中文乱码的返回形式  

def newawvs(request):
    form_title = '新建awvs任务'
    if request.COOKIES.get(cookies_key) == cookies_value:
        messagetask = ""
        if request.method == 'POST':
            # 接受request.POST参数构造form类的实例
            form = TaskForm(request.POST)
            if form.is_valid(): # 判断参数合法性
                messagetask = "请直接通过命令行执行"
                #     messagetask = "任务加入异常"
            form = TaskForm()
        # 如果是通过GET方法请求数据，返回一个空的表单
        else:
            form = TaskForm()
        return render(request, 'forms-basic.html', {'form':form, 'messagetask':messagetask, 'form_title':form_title})# 防止中文乱码的返回形式
    else:
        result = {"data":{}, "status":403, "msg":"未授权"}
        return HttpResponse(json.dumps(result,ensure_ascii=False),content_type="application/json,charset=utf-8")# 防止中文乱码的返回形式 


def newfullscan(request):
    form_title = '新建任务'
    if request.COOKIES.get(cookies_key) == cookies_value:
        messagetask = ""
        if request.method == 'POST':
            # 接受request.POST参数构造form类的实例
            form = TaskForm(request.POST)
            if form.is_valid(): # 判断参数合法性
                messagetask = "请直接通过命令行执行"
            form = TaskForm()
        # 如果是通过GET方法请求数据，返回一个空的表单
        else:
            form = TaskForm()
        return render(request, 'forms-basic.html', {'form':form, 'messagetask':messagetask, 'form_title':form_title})# 防止中文乱码的返回形式
    else:
        result = {"data":{}, "status":403, "msg":"未授权"}
        return HttpResponse(json.dumps(result,ensure_ascii=False),content_type="application/json,charset=utf-8")# 防止中文乱码的返回形式

def deletefullscan(request):
    form_title = '删除任务'
    if request.COOKIES.get(cookies_key) == cookies_value:
        messagetask = ""
        if request.method == 'POST':
            # 接受request.POST参数构造form类的实例
            form = TaskForm(request.POST)
            if form.is_valid(): # 判断参数合法性
                param1 = form.cleaned_data['task_domain'] # 获取表单字段
                result = DeleteTask(param1)
                if result:
                    messagetask = "成功删除任务"
                else:
                    messagetask = "任务删除异常"
            form = TaskForm()
        # 如果是通过GET方法请求数据，返回一个空的表单
        else:
            form = TaskForm()
        return render(request, 'forms-basic.html', {'form':form, 'messagetask':messagetask, 'form_title':form_title})# 防止中文乱码的返回形式
    else:
        result = {"data":{}, "status":403, "msg":"未授权"}
        return HttpResponse(json.dumps(result,ensure_ascii=False),content_type="application/json,charset=utf-8")# 防止中文乱码的返回形式   
