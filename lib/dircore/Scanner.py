from urllib import parse
from gevent import monkey; monkey.patch_socket(); monkey.patch_ssl()
from gevent.lock import BoundedSemaphore
import gevent
import requests
import logging
import colorlog
import sys

import multiprocessing as mp



handler = colorlog.StreamHandler()
formatter = colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s [%(name)s] [%(levelname)s] %(message)s%(reset)s',
    datefmt=None,
    reset=True,
    log_colors={
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
    },
    secondary_log_colors={},
    style='%')
handler.setFormatter(formatter)
logd = colorlog.getLogger('logd')
logd.addHandler(handler)
logd.setLevel(logging.INFO)


headers = {"user-agent":
           'user-agentMozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
           '(KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'}
requests.adapters.DEFAULT_RETRIES = 6
rs = requests.session()
rs.keep_alive = False


def print_msg(msg=None, left_align=True):
    if left_align:
        sys.stdout.write('\r' + msg)
    sys.stdout.flush()


def controller(pid, lock, tasks_url, gcount, tasks_done, process, 
               coroutine, allow_redirects, xcode, dict2_num, writer_buff):
    try:
        # 信号量 避免读写冲突
        sem = BoundedSemaphore(1)

        while not tasks_url.empty():
            # 判断当前协程数，若不足则补满
            if gcount[pid] < int(coroutine/process):
                # 读取queue的时候上锁 避免计数错误
                with lock:
                    tasks_gevent = []
                    # 600 每一个的协程控制在coroutine/process core
                    while gcount[pid] < int(coroutine/process) and not tasks_url.empty():
                        with sem:
                            gcount[pid] += 1
                        u = tasks_url.get()
                        tasks_gevent.append(gevent.spawn(scan, url=u, pid=pid, lock=lock, sem=sem,
                                            gcount=gcount, tasks_done=tasks_done,
                                            allow_redirects=allow_redirects, xcode=xcode, dict_num=dict2_num,
                                            writer_buff=writer_buff))
                # 等待完成
                gevent.joinall(tasks_gevent)
                
    except Exception as e:
        logd.error(e)
    finally:
        pass
    return


def test_controller(test_urls, writer_buff):
    tasks_gevent = []
    error_cnt = mp.Manager().Value('i', 0)
    sem = BoundedSemaphore(1)
    l = test_urls.qsize()
    for i in range(l):
        tasks_gevent.append(gevent.spawn(test_scan, url=test_urls.get(), writer_buff=writer_buff,
                                         error_cnt=error_cnt, sem=sem))
    gevent.joinall(tasks_gevent)
    # if error_cnt.value >= 3:
    #     return False
    # else:
    #     return True


def test_scan(url, writer_buff, error_cnt, sem):
    info = parse.urlsplit(url)
    netloc = info.netloc[0:info.netloc.index(':')]
    port = info.netloc[info.netloc.index(':')+1:]
    try:

        r = rs.get(url=url, headers=headers, timeout=10, allow_redirects=False)
        xstatus_code = r.status_code
        logd.info('[+] -- find   {}\t{}'.format(str(xstatus_code), url))
        writer_buff.put({'netloc': netloc, 'url':url,'port': port, 'status_code': xstatus_code})
    except Exception as e:
        writer_buff.put({'netloc': netloc, 'url':url,'port': port, 'status_code': "can't connect"})
        logd.error(url)
        logd.error(e)
    return


def scan(url, pid, lock, sem, gcount, tasks_done, allow_redirects, xcode, dict_num, writer_buff):
    stcode = 0
    info = parse.urlsplit(url)
    netloc = info.netloc[:info.netloc.index(':')]
    try:
        r = rs.get(url=url, headers=headers, timeout=10, allow_redirects=allow_redirects)
        xstatus_code = r.status_code
        stcode = r.status_code
        if xstatus_code != 404:
            if xcode:
                if xstatus_code not in xcode:
                    logd.info('[+] -- find   {}\t{}'.format(str(xstatus_code), url))
                    writer_buff.put({'netloc': netloc, 'url': url, 'status_code': xstatus_code})
            else:    
                logd.info('[+] -- find   {}\t{}'.format(str(xstatus_code), url))
                writer_buff.put({'netloc': netloc, 'url': url, 'status_code': xstatus_code})
    except Exception as e:
        if ConnectTimeoutError in e:
            logd.error(url + '    connect error')
        else:
            logd.error(e)
    finally:
        with sem:
            gcount[pid] -= 1
        with lock:
            tasks_done.value += 1
            if tasks_done.value % 50 == 0 and tasks_done.value != 0:
                print_msg("scanned " + str(tasks_done.value) + "  | Total" + str(dict_num) + '\r')
    return


def writer(writer_buff):
    try:
        fw = open('result.txt', 'a')
        while not writer_buff.empty():
            wbf = writer_buff.get()
            fw.writelines(wbf)
            # print(wbf)
    except Exception as e:
        if ConnectTimeoutError in e:
            logd.error('connect error')
        else:
            logd.error(e)
    finally:
        fw.close()
    return


def read_path(dic_path, url_apd_list):
    with open(dic_path) as f:
        for line in f.readlines():
            if line.startswith('/'):
                line.replace('/', '', 1)
            url_apd_list.append(line.replace('\n', '').replace('\r', ''))

# 首先在start里定义 test_url=mulManager. Queue

def test_prepare(web_list2, test_url):
    padding = ['test1', 'test2', 'test3', 'test4', 'test5']
   
    # count = 0
 
    for u in web_list2:
        for port in web_list2[u]['port']:
            # old
            if web_list2[u]['port'][port] not in ['http','https']:
                pass
            else:
                # count +=1
                furl = web_list2[u]['port'][port] + '://' + u + ':' + port
                if not furl.endswith('/'):
                    furl += '/'
                for apd in padding:
                    test_url.put(furl + apd)
            

    # print(count)


def Prepare2(url_apd_list, tasks_url, web_list2):
    print("Preparing...")
    for u in web_list2:
        for port in web_list2[u]['port']:
            if web_list2[u]['port'][port] not in ['http','https']:
                pass
            else:
                furl = web_list2[u]['port'][port] + '://' + u + ':' + port
                if not furl.endswith('/'):
                    furl += '/'
                for apd in url_apd_list:
                    tasks_url.put(furl + apd)
    print("Prepared.")
    return


def Prepare3(url_apd_list, tasks_url, web_list2):
    print("Preparing...")
    li = []
    for u in web_list2:
        for port in web_list2[u]['port']:
            if web_list2[u]['port'][port] not in ['http','https']:
                pass
            else:
                furl = web_list2[u]['port'][port] + '://' + u + ':' + port
                if not furl.endswith('/'):
                    furl += '/'
                for apd in url_apd_list:
                    tasks_url.put(furl + apd)
                    li.append(furl + apd)
    print("Prepared.")
    return li


def Prepare4(web_list2):
    print("Preparing...")
    li = []
    for u in web_list2:
        for port in web_list2[u]['port']:
            if web_list2[u]['port'][port] not in ['http','https']:
                pass
            else:
                furl = web_list2[u]['port'][port] + '://' + u + ':' + port
                if not furl.endswith('/'):
                    furl += '/'
                    li.append(furl)
    print("Prepared.")
    return li