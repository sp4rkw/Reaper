import asyncio,aiodns,sys
import logging
import colorlog

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
logb = colorlog.getLogger('logb')
logb.addHandler(handler)
logb.setLevel(logging.INFO)


class dnsburst():
    def __init__(self, subdomain_list, domain, domain_result, domain_count, ctnum, retrycount, dns_servers=None):
        self.loop = asyncio.get_event_loop()
        self.subdomain_list = subdomain_list
        self.resolver = aiodns.DNSResolver(timeout=2, loop=self.loop)
        self.domain = domain
        self.domain_result = domain_result
        self.scan_remain = domain_count
        self.domain_count = domain_count
        self.find_total = 0
        self.retrycount = retrycount  # retry max number
        self.semaphore = asyncio.Semaphore(ctnum)  # limit the number of coroutines
        self.checkGA = set()   #check General analysis
        self.errordomain = []  # retry to query dns
        if dns_servers is None:  
            self.resolver.nameservers = [
                '119.29.29.29' , '223.5.5.5', '114.114.114.114' 
            ]
        else:
            self.resolver.nameservers = dns_servers

    async def scan(self, sub_domain, sem):
        async with sem:
            self.scan_remain -= 1
            self.print_msg("remain " + str(self.scan_remain) + "  | Found" + str(self.find_total) + '\r')
            try:
                res = await self.resolver.query(sub_domain, "A")
                ret = []
                ret.append(sub_domain)
                for ip in res:
                    ret.append(str(ip.host))
                    break
                if ret[1] in self.checkGA:    #check General analysis 没有交集返回true
                    pass
                else:
                    self.checkGA.add(ret[1])
                    logb.info(ret[0] + '\t' + str(ret[1:]))
                    self.domain_result.append(ret)
                    self.find_total += 1
            except aiodns.error.DNSError as e:
                err_code, err_msg = e.args[0], e.args[1]
                # 1:  DNS server returned answer with no data
                # 4:  Domain name not found
                # 11: Could not contact DNS servers
                # 12: Timeout while contacting DNS servers
                if err_code not in [1, 4, 11, 12]:
                    logb.error('{0} {1}'.format(sub_domain, e))
                if err_code in [11, 12]:
                    logb.error("[+]--"+sub_domain+"/t"+"can't query with network")
                    self.errordomain.append(sub_domain)
            except Exception as e:
                logb.error(e)
                logb.error(sub_domain)
        
                    

    @staticmethod
    def print_msg(msg=None, left_align=True):
        if left_align:
            sys.stdout.write('\r' + msg)
        sys.stdout.flush()

    def run(self):
        for namelist in self.subdomain_list:
            tasks = [
                asyncio.ensure_future(
                    self.scan(
                        sub_domain=sub.replace("." + self.domain, '') + "." +
                        self.domain,
                        sem=self.semaphore)) for sub in namelist
            ]
            self.loop.run_until_complete(asyncio.wait(tasks))

            self.retrycount = 5
            while len(self.errordomain) != 0 and self.retrycount > 0:
                self.retrycount -= 1
                if len(self.errordomain) > 50:
                    logb.error('Please check network, dnsquery is error for network')
                    sys.exit()
                else:
                    errordemo = self.errordomain
                    self.errordomain = []
                    tasks = [
                    asyncio.ensure_future(
                        self.scan(
                            sub_domain=sub,
                            sem=self.semaphore)) for sub in errordemo
                    ]
                    self.loop.run_until_complete(asyncio.wait(tasks))

        # self.loop.close()         #  最后关闭

