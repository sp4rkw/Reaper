# ! /usr/bin/python
# -*- coding:utf-8 -*-
import argparse
import logging
import colorlog
import sys


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
log = colorlog.getLogger('logo')
log.addHandler(handler)
log.setLevel(logging.INFO)



def get_init_params():
    print('''                                                                                                                           
$$$$$$$\                                                    
$$  __$$\                                                   
$$ |  $$ | $$$$$$\   $$$$$$\   $$$$$$\   $$$$$$\   $$$$$$\  
$$$$$$$  |$$  __$$\  \____$$\ $$  __$$\ $$  __$$\ $$  __$$\ 
$$  __$$< $$$$$$$$ | $$$$$$$ |$$ /  $$ |$$$$$$$$ |$$ |  \__|
$$ |  $$ |$$   ____|$$  __$$ |$$ |  $$ |$$   ____|$$ |      
$$ |  $$ |\$$$$$$$\ \$$$$$$$ |$$$$$$$  |\$$$$$$$\ $$ |      
\__|  \__| \_______| \_______|$$  ____/  \_______|\__|      
                              $$ |                          
                              $$ |                          
                              \__|                  V 1.0        
                                                                                                                                                                                                                                                                                                                                                                              
    ''')
    parser = argparse.ArgumentParser(description='easy to collect information')
    parser.add_argument(
        "-cp", 
        "--pctnum", 
        type=int, 
        default=8000,
        help='Appoint the num of coroutine|dns')
    parser.add_argument(
        "-cd", 
        "--dctnum", 
        type=int,
        default=100,
        help="Appoint the num of coroutine|dir")
    # parser.add_argument(
    #     "-d1",
    #     "--dict1",
    #     type=str,
    #     help='Appoint a dictionary for dnssearch',
    #     default='subnames_full.txt')
    # parser.add_argument(
    #     "-d2", 
    #     "--dict2", 
    #     default='dicc.txt', 
    #     help="Appoint a dictionary for dirsearch")
    parser.add_argument(
        "-u", 
        "--domain", 
        type=str,
        help='Target domain name')
    parser.add_argument(
        "-p", 
        "--port", 
        type=str, 
        help='Appoint which port should be scanned')
    parser.add_argument(
        "-mp", 
        "--process", 
        dest="process",
        type=int,
        default=2, 
        help="Appoint the num of process")
    parser.add_argument(
        "-r", 
        "--retrycount", 
        type=str, 
        default=5,
        help='Appoint a number for the max retry times')
    parser.add_argument(
        "-s", 
        "--script", 
        type=str, 
        help='Appoint a script to scan warning port')
    parser.add_argument(
        "-t", 
        "--threadnum", 
        type=int, 
        default=100,
        help='Appoint the num of threading')
    parser.add_argument(
        "-x", 
        "--xcode", 
        type=str, 
        help='stop show which code of response')
    parser.add_argument(
        "-v", 
        "--version", 
        action='version', 
        version=' 1.0')
    parser.add_argument(
        "--checkpoc", 
        type=str,
        help="choose unauthorized check checkpoc,use MongoDB,Redis,Memcached,ZooKeeper,ElasticSearch")
    parser.add_argument(
        "--cors", 
        action='store_true',
        default=False, 
        help="check cors or not")
    # parser.add_argument(
    #     "--dns", 
    #     type=str, 
    #     help='Appoint a dnsserver')
    parser.add_argument(
        "--engine", 
        action='store_true',
        default=False, 
        help="find subdomain by SE or not")
    # parser.add_argument(
    #     "--redirect", 
    #     action='store_true',
    #     default=False, 
    #     help="allow redirect or not") # --redirect   True
    args = parser.parse_args()
    if args.domain is None:
        log.error("Please input domain ")
        log.error("[+]---python start.py -u test.com  -p 21-20000 -d1 subnames_full.txt -d2 dicc.txt -cd 100 -x 403,402,401,302,301 --engine --cors")
        sys.exit()
    return args

