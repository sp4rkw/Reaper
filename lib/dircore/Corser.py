import gevent
from gevent import monkey
monkey.patch_ssl()
monkey.patch_socket()
from lib.dircore.corscheck import CORSCheck
# from corscheck import CORSCheck
from gevent.queue import Queue
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
loge = colorlog.getLogger('loge')
loge.addHandler(handler)
loge.setLevel(logging.INFO)


class CORS(object):
    def __init__(self, url):
        self.url = url
        self.results = []




    def scan(self, cfg):
        while not cfg["queue"].empty():
            try:
                item = cfg["queue"].get(timeout=1.0)
                cors_check = CORSCheck(item)
                msg = cors_check.check_one_by_one()
                if msg:
                    self.results.append(msg)
            except Exception as e:
                loge.error(e)
                break


    def cors(self):
        queue = Queue()
        cfg = {"queue": queue}
        queue.put(self.url)
        loge.info("[+]--"+self.url+" - Start CORS scaning...")
        threads = [gevent.spawn(self.scan, cfg) for i in range(50)]
        try:
            gevent.joinall(threads)
        except KeyboardInterrupt as e:
            pass
        loge.info("[+]--"+self.url+" - Finished")
        return self.results

if __name__ == "__main__":    
    re = CORS("https://api.biligame.com")
    sss = re.cors()
    print(sss)