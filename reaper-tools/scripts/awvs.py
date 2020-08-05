import requests
import json
import time
import queue
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


# 请自行对接子域名列表，格式demo见main
# linux服务器配合screen持久化运行
#注意，无授权请勿扫描，后果自负

'''
Desprition:
    此函数用于服务器性能范围内执行扫描任务

Parameters:
    domainlist: 子域名列表
    awvs_token: awvs的token
    website: awvs站点地址

Returns:
    Null

Modify:2020-08-05 14:36:54
'''
def awvs_reaper(domainlist, awvs_token, website):# 接受域名list类型
    headers = {
        'X-Auth': awvs_token,
        'Content-type': 'application/json;charset=utf8'
    }

    api_running_url = website+'/api/v1/me/stats'
    api_add_url = website+"/api/v1/targets"
    api_run_url = website+"/api/v1/scans"

    # 先把所有任务添加上并调整速度
    target_list = []
    for target in domainlist:
        data = '{"address":"%s","description":"create_by_reaper","criticality":"10"}'% target
        r = requests.post(url=api_add_url, headers=headers, data=data, verify=False).json()
        target_id = r['target_id']
        api_speed_url = website+"/api/v1/targets/{}/configuration".format(target_id)
        data = json.dumps({"scan_speed":"fast"})# slow最慢，一般建议fast
        r = requests.patch(url=api_speed_url, headers=headers, data=data, verify=False)
        target_list.append(target_id)

    target_num = len(target_list)
    print("[+ AWVS] 已经成功写入任务，正在按最大规划执行")
    idcount = 0
    if target_num <= 3:
        for target_id in target_list:
            data = '{"profile_id":"11111111-1111-1111-1111-111111111111","schedule":{"disable":false,"start_date":null,"time_sensitive":false},"target_id":"%s"}'% target_id
            r = requests.post(url=api_run_url, headers=headers, data=data, verify=False).json()
            idcount = idcount + 1
            print("[+ AWVS] 当前进度: {}/{}".format(str(idcount), str(target_num)))
    else:
        r = requests.get(url=api_running_url, headers=headers, verify=False).json()
        runnum = int(r['scans_running_count']) # 正在扫描的个数
        flag = 1 # 做数组标志位
        while flag < target_num:
            if flag < 3:
                target_id = target_list[flag]
                flag = flag + 1
                data = '{"profile_id":"11111111-1111-1111-1111-111111111111","schedule":{"disable":false,"start_date":null,"time_sensitive":false},"target_id":"%s"}'% target_id
                r = requests.post(url=api_run_url, headers=headers, data=data, verify=False).json()
                r = requests.get(url=api_running_url, headers=headers, verify=False).json()
                runnum = int(r['scans_running_count']) # 正在扫描的个数
                idcount = idcount + 1
                print("[+ AWVS] 当前进度: {}/{}".format(str(idcount), str(target_num)))
            elif runnum < 4:
                target_id = target_list[flag]
                flag = flag + 1
                data = '{"profile_id":"11111111-1111-1111-1111-111111111111","schedule":{"disable":false,"start_date":null,"time_sensitive":false},"target_id":"%s"}'% target_id
                r = requests.post(url=api_run_url, headers=headers, data=data, verify=False).json()
                r = requests.get(url=api_running_url, headers=headers, verify=False).json()
                runnum = int(r['scans_running_count']) # 正在扫描的个数
                idcount = idcount + 1
                print("[+ AWVS] 当前进度: {}/{}".format(str(idcount), str(target_num)))
                time.sleep(30)
            else:
                pass
    return target_num



'''
Desprition:
    用于删除awvs的多余的任务

Parameters:
    awvs_token: awvs的token
    website: awvs站点地址

Returns:
    Null

Modify:2020-08-05 14:34:36
'''
def del_targets(awvs_token, website):
    headers = {
        'X-Auth': awvs_token,
        'Content-type': 'application/json;charset=utf8'
    }
    response = requests.get(website + "/api/v1/targets", headers=headers, verify=False)
    content = json.loads(response.content)
    print("[+ AWVS] awvs连接成功，开始清理")
    targets_id = queue.Queue()
    for cent in content['targets']:
        targets_id.put([cent['address'],cent['target_id']])
    if targets_id.qsize() == 0:
        return 0
    else:
        while not targets_id.empty():
            targets_info = targets_id.get()
            response = requests.delete(website + "/api/v1/targets/" + targets_info[1], headers=headers, verify=False)