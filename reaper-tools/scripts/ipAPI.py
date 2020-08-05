import requests
from bs4 import BeautifulSoup

def IPrun(domain):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8',
        'Referer': 'https://www.baidu.com',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'close',
    }
    s = requests.session()
    s.headers.update(headers)
    url = "https://www.ip.cn//?ip="+domain
    try:
        html = s.get(url=url, timeout= 5)
        html.encoding = html.apparent_encoding
        soup= BeautifulSoup(html.text,'lxml')
        recordstring = soup.find_all(class_= 'well')[0].p.next_sibling.code.string
        if recordstring:
            return recordstring
    except:
        return ""
