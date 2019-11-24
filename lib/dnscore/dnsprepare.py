# ! /usr/bin/python
# -*- coding:utf-8 -*-


def dnsprepare(subname_dict):  
    subname_list = []
    domain_count = 0
    create_limit = 30000  # 300000 is be set for save memory
    count = 0
    count_list = []
    
    with open(subname_dict) as f:
        for i in f.readlines():
            domain_count += 1
            count += 1
            count_list.append(i.replace('\n', ''))
            if count == create_limit:
                subname_list.append(count_list)
                count_list = []
                count = 0
        if count_list != []:
            subname_list.append(count_list)
            count_list = []
    return subname_list,domain_count


