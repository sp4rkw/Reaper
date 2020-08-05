import requests
from bs4 import BeautifulSoup

def recordrun(domain):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8',
        'Referer': 'https://www.baidu.com',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'close',
    }
    s = requests.session()
    s.headers.update(headers)
    url = "https://site.ip138.com/"+domain+"/beian.htm"
    try:
        html = s.get(url=url, timeout= 5)
        html.encoding = html.apparent_encoding
        soup= BeautifulSoup(html.text,'lxml')
        recordstring = soup.find_all(class_= 'date')[0].next_sibling.next_sibling.string
        # print(recordstring)
        print("[+ RECORD] 备案接口查询成功")
        return recordstring
    except:
        return ""

if __name__ == "__main__":
    recordrun("www.58.com")
    # a = recordrun("www.58.com")
    # print(a)