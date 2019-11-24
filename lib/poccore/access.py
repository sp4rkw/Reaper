import sys
import socket
from pymongo import MongoClient
from redis import StrictRedis
from kazoo.client import KazooClient
from elasticsearch import Elasticsearch


def mongo_get(hosts):
    try:
        client = MongoClient(hosts, 27017)
        dbs = client.database_names()
        if dbs:
            return True
        else:
            return False
    except:
        return False


def check_redis(ip):
    try:
        redis = StrictRedis(host=ip,port=6379,db=0,password='')
        if(redis.dbsize()):
            return True
        else:
            return False
    except:
        return False

# 检测是否存在zookeeper未授权漏洞
def check_zookeeper(ip):
    try:
        zk = KazooClient(hosts='{}:{}'.format(ip, 2181))
        zk.start()
        chidlrens = zk.get_children('/')
        if len(chidlrens) > 0:
            zk.stop()
            return True
        else:
            zk.stop()
            return False
    except Exception as e:
        return False

def check_elasticsearch(ip):
    port =  9200
    try:
        es = Elasticsearch("{}:{}".format(ip, port), timeout=5)  # 连接Elasticsearch,延时5秒
        if es:
            return True
        else:
            return False
    except Exception as e:
        return False


def check_Memcached(url):
    port = int(url.split(':')[-1]) if ':' in url else 11211
    payload = '\x73\x74\x61\x74\x73\x0a'  # command:stats
    s = socket.socket()
    socket.setdefaulttimeout(10)
    try:
        host = url.split(':')[0]
        s.connect((host, port))
        s.send(payload)
        recvdata = s.recv(2048)  # response larger than 1024
        s.close()
        if recvdata:
            return True
        else:
            return False
    except Exception as e:
        return False
