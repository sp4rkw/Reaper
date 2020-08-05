# ! /usr/bin/python
# -*- coding:utf-8 -*-
import argparse
import logging
import colorlog
import sys


handler = colorlog.StreamHandler()
formatter = colorlog.ColoredFormatter(
    '%(log_color)s%(message)s%(reset)s',
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
                              \__|     闪光          V 2.0.0     
                                                                                                                                                                                                                                                                                                                                                                       
    ''')
    parser = argparse.ArgumentParser(
        formatter_class = argparse.RawDescriptionHelpFormatter,
        description='''
Script's type help：
1. operate oneforall json
2. run awvs
3. delete all awvs data''')
    parser.add_argument(
        "-t", 
        "--type", 
        type=str, 
        help='Appoint the type of script function')
    parser.add_argument(
        "-d", 
        "--domain", 
        type=str,
        help="Appoint target url")
    args = parser.parse_args()
    if args.domain is None:
        log.error("[+ ERROR] Please input domain and type' parameter")
        log.error("[+ HELP] python start.py -u test.com -t 1")
        sys.exit()
    return args

