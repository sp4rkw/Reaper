import sys
import asyncio
import aiodns
import os
import uuid
import argparse


class dnsburst():
    def __init__(self,
                 subdomain_list,
                 domain,
                 allip_dict,
                 timeout_domain,
                 create_limit,
                 domain_result,
                 dns_servers=None):
        self.loop = asyncio.get_event_loop()
        self.subdomain_list = subdomain_list
        self.resolver = aiodns.DNSResolver(timeout=2, loop=self.loop)
        if dns_servers is None:   # '192.168.102.81','192.168.102.82'  
            self.resolver.nameservers = [
                '223.5.5.5', '223.6.6.6', '114.114.114.114'
            ]
        self.domain = domain
        self.allip_dict = allip_dict
        self.ip_con = 5
        self.domain_result = domain_result
        self.scan_total = 0
        self.find_total = 0
        self.semaphore = asyncio.Semaphore(
            8000)
        self.timeout_domain = timeout_domain
        self.create_limit = create_limit  
        self.limit_timeout = 6

    async def scan(self, sub_domain, sem):
        async with sem:
            self.scan_total += 1
            try:
                res = await self.resolver.query(sub_domain, "A")
                ret = [ip.host for ip in res]
                if self.is_analysis(ret):
                    print('[+ FIND] '+sub_domain + '\t' + str(ret))
                    self.domain_result.append(sub_domain)
                    self.find_total += 1
            except aiodns.error.DNSError as e:
                err_code, err_msg = e.args[0], e.args[1]
                # 1:  DNS server returned answer with no data
                # 4:  Domain name not found
                # 11: Could not contact DNS servers
                # 12: Timeout while contacting DNS servers
                if err_code not in [1, 4, 11, 12]:
                    print('[+ ERROR] '+'{domain} {exception}'.format(
                        domain=sub_domain, exception=e))
                if err_code in [11, 12]:
                    self.timeout_domain.append(sub_domain)
            except Exception as e:
                print('[+ ERROR] '+e)

    def is_analysis(self, ret):
        if ret == []:
            return False
        for ip in ret:
            if ip in self.allip_dict.keys():
                if self.allip_dict[ip] < self.ip_con:
                    self.allip_dict[ip] += 1
                else:
                    # print(sub_domain+"   May be a general analysis")
                    return False
            else:
                self.allip_dict[ip] = 1
        return True

    def get_analysis(self):
        print('[+ FIND] '+'探索是否存在泛解析机制')
        for _ in range(10):
            try:
                res = self.resolver.query(str(uuid.uuid4())+'.'+self.domain, "A")
                res = self.loop.run_until_complete(res)
                for ip in res:
                    self.allip_dict[ip.host] = 5
            except aiodns.error.DNSError as e:
                err_code, err_msg = e.args[0], e.args[1]
                # 1:  DNS server returned answer with no data
                # 4:  Domain name not found
                # 11: Could not contact DNS servers
                # 12: Timeout while contacting DNS servers
                if err_code not in [1, 4, 11, 12]:
                    print('[+ ERROR] '+'{domain} {exception}'.format(
                        domain=self.domain, exception=e))
            except Exception as e:
                print('[+ ERROR] '+e)

    def run(self):
        for namelist in self.subdomain_list:
            tasks = [
                asyncio.ensure_future(
                    self.scan(
                        sub_domain=sub.replace("." + self.domain, '') + "." +
                        self.domain,
                        sem=self.semaphore)) for sub in namelist
            ]  # 内存占用太大
            self.loop.run_until_complete(asyncio.wait(tasks))

        while self.timeout_domain != [] and len(
                self.timeout_domain) > 10 and self.limit_timeout > 0:
            self.limit_timeout -= 1
            err_domain = self.list_of_groups(self.timeout_domain,
                                             self.create_limit)
            self.timeout_domain = []
            for namelist in err_domain:
                tasks = [
                    asyncio.ensure_future(
                        self.scan(
                            sub_domain=sub.replace("." + self.domain, '') + "."
                            + self.domain,
                            sem=self.semaphore)) for sub in namelist
                ]  # 内存占用太大
                self.loop.run_until_complete(asyncio.wait(tasks))
        # self.loop.close()         #  最后关闭
        print('[+ DNSBURST API] '+"总共扫描" + str(self.scan_total) + "次")

    def list_of_groups(self, init_list, children_list_len):
        list_of_groups = zip(*(iter(init_list), ) * children_list_len)
        end_list = [list(i) for i in list_of_groups]
        count = len(init_list) % children_list_len
        end_list.append(init_list[-count:]) if count != 0 else end_list
        return end_list


