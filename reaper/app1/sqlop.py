import time
import json
from app1.models import Subdomain
from app1.models import Subdomaintask
from app1.models import Awvs
import requests
from bs4 import BeautifulSoup
from urllib.request import quote
from django.db.models import F



'''前后端django通杀'''

def Selectawvs(domain):
    results = Awvs.objects.filter(waitnum__gt=F('overnum')) #不是域名就返回空
    if results:
        return 'fail'
    else:
        subdomain = Subdomain.objects.filter(groupdomain = domain).filter(status = '200').values_list('subdomain', flat=True)
        return subdomain

def Inserawvs(domain, waitnum):
    awvs = Awvs()
    awvs.taskname = domain
    awvs.waitnum = str(waitnum)
    awvs.overnum = '0'
    awvs.save()
    awvs_id = awvs.id
    return awvs_id


def SelectDomain(domain):
    results = Subdomain.objects.filter(groupdomain = domain) #不是域名就返回空
    results_list = []
    iddomain = 1
    if results:
        for line in results:
            now = int(line.wtime)
            timeArray = time.localtime(now)
            otherStyleTime = time.strftime("%Y--%m--%d %H:%M:%S", timeArray)
            demo_list = [str(iddomain), line.subdomain, line.title, line.status, line.banner, line.cdn, line.record, line.ipwhere, otherStyleTime]# 顺序 id,url,title,cnd,record,ipwhere,time
            results_list.append(demo_list)
            iddomain = iddomain + 1
    else:
        results_list = []
    return results_list

#subdomain	title	status	cdn	record	ipwhere	groupdomain 	顺序  注意banner没弄
def InserDomain(data, data1, data2, data3, data4, data5, data6):
    subdomain = Subdomain()
    for x in data:
        subdomain.subdomain = x
        subdomain.title = data1[x]
        subdomain.status = data2[x]
        subdomain.cdn = data3[x]
        subdomain.record = data4
        subdomain.ipwhere = data5[x]
        subdomain.groupdomain = data6
        subdomain.wtime = str(int(time.time()))
        subdomain.save()
    return 'true'


def InserTask(domain):
    subdomaintask = Subdomaintask()
    subdomaintask.task = domain
    subdomaintask.intime = str(int(time.time()))
    subdomaintask.flag = '0'
    result = "" # 成功与否的标志 1 ok
    try:
        subdomaintask.save()
        result = "1"
    except:
        result = "0"
    return result

def DeleteTask(domain):
    subdomaintask = Subdomaintask.objects.get(task = domain)
    subdomain = Subdomain.objects.filter(groupdomain = domain)
    result = "" # 成功与否的标志 1 ok
    try:
        subdomaintask.delete()
        subdomain.delete()
        result = "1"
    except:
        result = "0"
    return result



def SelectTask():
    results = Subdomaintask.objects.all()
    i = 1
    results_list = []
    if results:
        for line in results:
            intime = ""
            outtime = ""
            com = ""
            if line.intime:
                now = int(line.intime)
                timeArray = time.localtime(now)
                intime = time.strftime("%Y--%m--%d %H:%M:%S", timeArray)
            else:
                intime = "未记录"
            if line.outtime:
                now = int(line.outtime)
                timeArray = time.localtime(now)
                outtime = time.strftime("%Y--%m--%d %H:%M:%S", timeArray)
            else:
                outtime = "未记录"
            if line.flag == "1":
                com = "已完成"
            else:
                com = "未完成"
            demo_list = [str(i), line.task, intime, outtime, com]
            results_list.append(demo_list)
            i = i + 1
    else:
        results_list = []
    return results_list


def recordrun(domain, querytype):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8',
        'Referer': 'https://www.baidu.com',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'close',
    }
    record_data = {} # 利用dict去重
    s = requests.session()
    s.headers.update(headers)
    url = ""
    record_data_list = []
    if querytype == '2':
        url = "http://icp.chinaz.com/"
        html = s.get(url=url, timeout= 5)# 获取初始分配 cookie
        url = "http://icp.chinaz.com/Home/PageData"
        qdata = {"pageNo":1,"pageSize":"1000","Kw":domain}
        r = s.post(url, data=qdata, timeout=5)
        r_array = json.loads(r.text)['data']
        for line in r_array:
            # 备案单位	网站域名	网站名称	网站备案号	备案日期
            demo = [domain, line['host'], line['webName'], line['permit'], line['verifyTime']]
            record_data_list.append(demo)
        return record_data_list
    else:
        url = "http://icp.chinaz.com/"+domain
        html = s.get(url=url, timeout= 5)
        html.encoding = html.apparent_encoding
        soup= BeautifulSoup(html.text,'lxml')
        table_data = soup.find_all('ul', class_ = 'bor-t1s IcpMain01')[0]
        li_data = table_data.find_all('li')
        data1 = li_data[0].p.a.string
        data4 = li_data[2].p.font.string
        data3 = li_data[3].p.string
        data5 = li_data[7].p.string
        # 备案单位	网站域名	网站名称	网站备案号	备案日期
        demo = [data1, domain, data3, data4, data5]
        record_data_list.append(demo)

        return record_data_list









