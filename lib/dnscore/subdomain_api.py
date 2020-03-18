# -*- coding: UTF-8 -*-
'''
Desprition:
    subdomainApi接口
    - crt.sh
    - baidu search
    - certspotter
    - entrust
    - ximcx
    - securitytrails
    - hackertarget
    - threatminer
    - sitedossier
    - ip168

'''
import requests
import re
from bs4 import BeautifulSoup
# import eventlet as ev
# ev.monkey_patch()
requests.packages.urllib3.disable_warnings()


def CertSh_Api(domain):
    domain_links = set()
    result = set()
    try:
        url = 'https://crt.sh/?q='+domain
        r = requests.get(url=url,timeout=20, verify=False)
        links = re.findall(b'<A href="(\?id=\d.+)">',r.content)
        for link in links:
            domain_links.add('https://crt.sh/'+link.decode())
        for domain_link in domain_links:
            try:
                r1 = requests.get(url=domain_link,timeout=30, verify=False)
                if b'Subject&nbsp;Alternative&nbsp;Name:&nbsp;' in r1.content:
                    domains = re.findall(b'DNS:(.*?)<BR>', r1.content)
                    for domain_ in domains:
                        if domain in domain_.decode():
                            result.add(domain_.decode().replace('*.', ''))
            except Exception as e:
                try:
                    r1 = requests.get(url=domain_link, timeout=20, verify=False)
                    if b'Subject&nbsp;Alternative&nbsp;Name:&nbsp;' in r1.content:
                        domains = re.findall(b'DNS:(.*?)<BR>', r1.content)
                        for domain_ in domains:
                            if domain in domain_.decode():
                                result.add(domain_.decode().replace('*.', ''))
                except:
                    pass
    except Exception as e:
        return CertSh_Api(domain)
    print('[+ CertSh API] CertSh接口 : {} 捕获子域名总数 : {}'.format(domain, len(result)))
    return list(result)


def Baidu_Api(domain):
    result = set()
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'zh,zh-CN;q=0.9,en-US;q=0.8,en;q=0.7',
               'Cache-Control': 'max-age=0', 'Connection': 'keep-alive',
               'Host': 'ce.baidu.com', 'Upgrade-Insecure-Requests': '1',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
    url = 'http://ce.baidu.com/index/getRelatedSites?site_address=' + domain
    try:
        r = requests.get(url, headers=headers, timeout=10, verify=False)
        content = r.json()
        data = content.get('data')
        for u in data:
            if u.get('domain') != None:
                result.add(u.get('domain'))
    except Exception as e:
        pass
    print('[+ BaiDu API] 百度接口 : {} 捕获子域名总数 : {}'.format(domain, len(result)))
    return list(result)


def Certspotter_Api(domain):
    result = set()
    try:
        url = 'https://api.certspotter.com/v1/issuances'
        params = {'domain': domain,
                  'include_subdomains': 'true',
                  'expand': 'dns_names'}
        response = requests.get(url=url,params=params)
        rest = (response.json())
        for c in rest:
            try:
                for c1 in (c['dns_names']):
                    if domain in c1:
                        result.add(c1.replace('*.',''))
            except:
                pass
    except Exception as e:
        pass
    print('[+ Certspotter API] Certspotter接口 : {} 捕获子域名总数 : {}'.format(domain, len(result)))
    return list(result)


def Entrus_Api(domain):
    result = set()
    try:
        url = 'https://ctsearch.entrust.com/api/v1/certificates'
        params = {'fields': 'subjectDN',
                  'domain': domain,
                  'includeExpired': 'true'}
        response = requests.get(url=url,params=params)
        rest = (response.json())
        for c in rest:
            try:
                result.add(c['subjectDN'].split(',')[0].replace('cn=', '').replace('*.', ''))
            except:
                pass
    except Exception as e:
        pass
    print('[+ Entrus API] Entrus接口 : {} 捕获子域名总数 : {}'.format(domain, len(result)))
    return list(result)



def Ximcx_Api(domain):
    result = set()
    try:
        url = "http://sbd.ximcx.cn/DomainServlet"
        data = {'domain':domain}
        response = requests.post(url=url,data=data)
        rest = (response.json()['data'])
        for res in rest:
            try:
                result.add(res['domain'])
            except Exception as e :
                pass
    except Exception as e:
        pass
    print('[+ Ximcx API] Ximcx接口 : {} 捕获子域名总数 : {}'.format(domain, len(result)))
    return list(result)


def Sec_Api(domain):
    result = set()
    try:
        url = "https://api.securitytrails.com/v1/domain/{}/subdomains".format(domain)
        querystring = {"apikey":seckey}
        response = requests.request("GET", url, params=querystring)
        rest = (response.json())
        subdomains = rest['subdomains']
        for s in subdomains:
                result.add(s+'.'+domain)
    except:
        pass
    print('[+ SecurityTrails API] SecTra接口 : {} 捕获子域名总数 : {}'.format(domain, len(result)))
    return list(result)


def Hackert_Api(domain):
    result = set()
    try:
        url = "https://api.hackertarget.com/hostsearch/?q={}".format(domain)
        response = requests.get(url)
        rest = response.content.decode().split('\n')
        for r in rest:
                result.add(r.split(',')[0])
    except Exception as e:
        pass
    print('[+ Hackertarget API] Hackertarget接口 : {} 捕获子域名总数 : {}'.format(domain, len(result)))
    return list(result)



def Threatminer_Api(domain):
    result = set()
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/40.0',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Accept-Language': 'en-GB,en;q=0.5',
                   'Accept-Encoding': 'gzip, deflate',
                   }
        url = "https://www.threatminer.org/getData.php?e=subdomains_container&q={}&t=0&rt=10&p=1".format(domain)
        response = requests.get(url,headers=headers)
        rest = response.content.decode()
        res = re.findall('">(.*?)</a></td><',rest)[1:]
        for r in res:
                result.add(r)
    except Exception as e:
        pass
    print('[+ Threatminer API] Threatminer接口 : {} 捕获子域名总数 : {}'.format(domain, len(result)))
    return list(result)

def Sitedossier_Api(domain):
    result = set()
    try:
        url = "http://www.sitedossier.com/parentdomain/{}".format(domain)
        response = requests.get(url)
        rest = response.text
        res = re.findall('<a href="/site/(.*?)">',rest)
        for r in res:
            if domain in r:
                result.add(r.strip('.'))
    except Exception as e:
        pass
    print('[+ Sitedossier API] Sitedossier接口 : {} 捕获子域名总数 : {}'.format(domain, len(result)))
    return list(result)

def ip168_Api(domain):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8',
        'Referer': 'https://www.baidu.com',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'close',
    }
    s = requests.session()
    s.headers.update(headers)
    url = "https://site.ip138.com/"+domain+"/domain.htm"
    domain_list = []
    try:
        html = s.get(url=url, timeout= 5)
        html.encoding = html.apparent_encoding
        soup= BeautifulSoup(html.text,'lxml')
        recordstring = soup.find_all(class_= 'panel')[0].find_all(target="_blank")
        for line in recordstring:
            domain_list.append(line.string)
    except:
        pass
    print('[+ IP168 API] IP168接口 : {} 捕获子域名总数 : {}'.format(domain, len(domain_list)))
    return domain_list

def subdomainApi(domain):
    Baidu_res = Baidu_Api(domain)
    SecTra = Sec_Api(domain)
    CertSP = Certspotter_Api(domain)
    XimcX = Ximcx_Api(domain)
    EntrU = Entrus_Api(domain)
    Hackert = Hackert_Api(domain)
    Sitedossier = Sitedossier_Api(domain)
    Threatminer = Threatminer_Api(domain)
    CertSh = []
    # with eventlet.Timeout(20,False):# 防止时间过长
        # CertSh = CertSh_Api(domain)
    Ip168 = ip168_Api(domain)
    Baidu_res.extend(SecTra)
    Baidu_res.extend(CertSP)
    Baidu_res.extend(XimcX)
    Baidu_res.extend(EntrU)
    Baidu_res.extend(CertSh)
    Baidu_res.extend(Hackert)
    Baidu_res.extend(Sitedossier)
    Baidu_res.extend(Threatminer)
    Baidu_res.extend(Ip168)
    return Baidu_res

if __name__ == "__main__":
    CertSh_Api("chinahr.com")
    # Baidu_res = subdomainApi("chesupai.com")
    # print(Baidu_res)