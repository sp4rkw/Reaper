# -*- coding: UTF-8 -*-
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED


def titleGet(s, subdomain, title_result, status_result):
    try:
        html = s.get(subdomain, timeout=3)
        re_status = html.status_code
        html.encoding = html.apparent_encoding
        soup= BeautifulSoup(html.text,'lxml')
        title_result[subdomain] = soup.title.string
        status_result[subdomain] = re_status
    except:
        title_result[subdomain] = 'none'
        status_result[subdomain] = 'none'


def titlerun(domain_result):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8',
        'Referer': 'https://www.baidu.com',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'close',
    }
    s = requests.session()
    s.headers.update(headers)
    title_result = {}
    status_result = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        tasks = []
        for url in domain_result:
            tasks.append(executor.submit(titleGet, s, url, title_result, status_result))
        wait(tasks, return_when=ALL_COMPLETED)
    print("[+ TITLE] 页面标题查询成功")
    return title_result,status_result


if __name__ == "__main__":
    domain_result,status_code = ['http://www9.tutorabc.com.cn','https://www9.tutorabc.com.cn','http://sec.tutorabc.com.cn','https://sec.tutorabc.com.cn']
    demo = titlerun(domain_result)
    print(demo)
    pass

