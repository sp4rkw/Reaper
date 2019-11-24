import asyncio
import aiodns
import os
import logging
import colorlog
import json
import math
import copy
import dns.resolver as Resolver
import lib.dircore.Corser as Corser
from lib.dircore.Scanner import Prepare4
import lib.dircore.dirbrust as Dirbrust
import multiprocessing as mp
from lib.dnscore.dnsburst import dnsburst
from lib.dnscore.searchspider import DomainSpider
from lib.portcore.portscan import portburst
from lib.portcore.oneportscan import Oneportburst
from lib.poccore.access import *
from plugins.reaperLogo import get_init_params
from lib.dnscore.dnsprepare import dnsprepare
import requests


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
log = colorlog.getLogger('log')
log.addHandler(handler)
log.setLevel(logging.INFO)


def main():
    args = get_init_params()
    domain = args.domain  # scan  domain
    subname_dict = args.dict1  # dict  name
    dns_server = None
    startnum = None
    stopnum = None
    ports = None
    xcode = []
    script = None
    pctnum = args.pctnum
    threadnum = args.threadnum
    retrycount = args.retrycount
    dic_path = args.dict2
    process = int(args.process)
    # redirect = args.redirect
    engine = args.engine
    coroutine = args.dctnum
    cors = args.cors
    if args.dns:
        dns_server = args.dns.split(",") #dns server
    if args.port and '-' in args.port:
        startnum = int(args.port.split('-')[0])
        stopnum = int(args.port.split('-')[1])
    elif args.port:
        ports = args.port.split(',')
    else:
        startnum = 21
        stopnum = 65534
    if args.xcode:
        ycode = args.xcode.split(',')
        xcode = [int(x) for x in ycode]
    if args.checkpoc:
        script = args.checkpoc.split(',')
    if os.name == 'nt':  # subname_dict  
        subname_dict = os.getcwd() + '\\dict\\' + subname_dict
        save_name = os.getcwd() + '\\output\\' + domain + '.json'
        dic_path = os.getcwd() + '\\dict\\' + dic_path
    else:
        subname_dict = os.getcwd() + '/dict/' + subname_dict
        save_name = os.getcwd() + '/output/' + domain + '.json'
        dic_path = os.getcwd() + '/dict/' + dic_path

    
    log.warning("====================step1===================")
    log.info("choose subname dict：" + subname_dict)

    domain_result = []  # subname list
    subname_list,domain_count = dnsprepare(subname_dict)  # scan domain list
    log.info("A total of {} domain names need to be scanned".format(str(domain_count)))
    s = dnsburst(
        domain=domain,
        subdomain_list=subname_list,
        domain_result=domain_result,
        domain_count=domain_count,
        dns_servers=dns_server,
        ctnum=pctnum,
        retrycount=retrycount)
    s.run()
    subname_list.clear()

    domain_demo = set()
    if engine:
        SS = DomainSpider(domain,domain_demo)
        SS.run()
        domain_demo = list(domain_demo)
        domain_keys = [x[0] for x in domain_result]
        domain_value = [x[1] for x in domain_result]
        domain_value = set(domain_value)
        for x in domain_demo:
            if x in domain_keys:
                pass
            else:
                A = Resolver.query(x,'A').response.answer
                if len(A) > 1:
                    B = A[1].items
                    C = None if len(A) < 3 else A[2].items 
                    B = C if 'com' in str(B[0]) else B
                    if str(B[0]) in domain_value:
                        pass
                    else:
                        domain_result.append([x,str(B[0])])  
                        domain_value.add(str(B[0])) 
        log.info("Total  scan " + str(domain_count+4000) + " times")      
    else:
        log.info("Total  scan " + str(domain_count) + " times")

    log.warning("Total  find " + str(len(domain_result)) + " subdomain")

    log.warning("subdomain scan has been over")

    log.warning("====================step2===================")
    mulManager = mp.Manager()  # multiprocess's manager,  to create  queue and lock and list and value
    server_info = mulManager.dict() 
    if len(domain_result) < process:
        p = portburst(
            server_list = domain_result,
            scan_total = len(domain_result),
            server_info = server_info,
            startnum = startnum,
            stopnum = stopnum,
            ports = ports,
            threadnum = threadnum)
    else:
        domain_sp = []
        ts = []
        for i in range(process):
            l = math.floor(len(domain_result)/process)
            domain_sp.append(domain_result[i * l: i * l + l])
        if len(domain_result) % process != 0:
            s = math.floor(len(domain_result) / process)
            for x in domain_result[process * s:]:
                domain_sp[process-1].append(x)
        for i in range(process):
            p = mp.Process(target=portburst,
                           args=(domain_sp[i], len(domain_sp[i]),
                                 server_info, ports, threadnum, startnum,
                                 stopnum))
            ts.append(p)
            p.start()

        for pr in ts:
            pr.join()
        
            
    domain_result.clear()
    server_info = dict(server_info)
    
    log.warning("Port scan has been over")
    log.warning("====================step3===================")
    # print(server_info)




    mulManager = mp.Manager() # multiprocess's manager,  to create  queue and lock and list and value
    writer_buff = mulManager.Queue() # the scan dir result buff
    processList = []
    url_list = Prepare4(server_info)

    dir_dict = []
    with open(dic_path) as f:
        data = f.readlines()
        dir_dict = [i.replace("\n",'').replace("\r",'') for i in data]

    if len(url_list) <= process:
        for i in range(len(url_list)):
            processList.append(mp.Process(target=Dirbrust.process_start,
                                          args=([url_list[i]], dir_dict, coroutine, xcode, writer_buff)))
    else:
        length = len(url_list)
        sp = range(0, len(url_list), math.ceil(length / process))
        url_chuck = [url_list[j:j+math.ceil(length/process)] for j in sp]
        for i in range(process):
            processList.append(mp.Process(target=Dirbrust.process_start,
                                          args=(url_chuck[i],
                                                dir_dict, coroutine, xcode, writer_buff)))

    for p in processList:
        p.start()
    for p in processList:
        p.join()

    for u in server_info:
        server_info[u]['url'] = {}

    while not writer_buff.empty():
        w = writer_buff.get()
        server_info[w['netloc']]['url'][w['url']] = w['status_code']

    # start cors check
    if cors:
        for u in server_info:
            cors_demo = {}
            for port in server_info[u]['port']:
                if server_info[u]['port'][port] not in ['http','https']:
                    pass
                else:
                    furl = server_info[u]['port'][port] + '://' + u + ':' + port
                    ccc = Corser.CORS(furl)
                    result = ccc.cors()
                    if result:
                        cors_demo.update({port:str(result)})
                    else:
                        cors_demo.update({port:"[{'no find'}]"})
            if cors_demo:
                server_info[u].update({'cors':cors_demo})
            else:
                server_info[u].update({'cors': {"allports" : '[{no web port}]'}})

    if not script:
        pass
    else:
        for xx in server_info:
            for yy in server_info[xx]['port']:
                if yy == 27017 and 'MongoDB' in script:
                    if mongo_get(server_info[xx]['ip']):
                        server_info[xx]['check']['27017']='confirm | MongoDB unauthoried leak'
                    else:
                        server_info[xx]['check']['27017']='filter | MongoDB unauthoried leak'
                elif yy == 6379 and 'Redis' in script:
                    if check_redis(server_info[xx]['ip']):
                        server_info[xx]['check']['6379']='confirm | Redis unauthoried leak'
                    else:
                        server_info[xx]['check']['6379']='filter | Redis unauthoried leak'
                elif yy == 11211 and 'Memcached' in script:
                    if check_Memcached(server_info[xx]['ip']):
                        server_info[xx]['check']['11211']='confirm | Memcached unauthoried leak'
                    else:
                        server_info[xx]['check']['11211']='filter | Memcached unauthoried leak'
                elif yy == 2181 and 'ZooKeeper' in script:
                    if check_zookeeper(server_info[xx]['ip']):
                        server_info[xx]['check']['2181']='confirm | ZooKeeper unauthoried leak'
                    else:
                        server_info[xx]['check']['2181']='filter | ZooKeeper unauthoried leak'
                elif yy == 9200 and 'ElasticSearch' in script:
                    if check_elasticsearch(server_info[xx]['ip']):
                        server_info[xx]['check']['837']='confirm | ElasticSearch unauthoried leak'
                    else:
                        server_info[xx]['check']['837']='filter | ElasticSearch unauthoried leak'


    # write it
    with open(save_name,'w') as f:
        f.write(json.dumps(server_info))
    server_info.clear()
    log.warning("The result is save in " + save_name)
    url = "http://127.0.0.1:10502/receiveFile"
    files = {'file':open(save_name,'r')}
    
    # try:
    reponse = requests.post(url,files=files)
    try:
        if reponse.status_code == 200:
            log.warning("Sucess | you can view index.html")
        else:
            log.error("Fail | java server can't run")
    except:
        log.error("Fail | java server can't run")

    
    

if __name__ == "__main__":
    main()
