#!/usr/bin/python

import requests
import grequests
import json
import math
from collections import OrderedDict, namedtuple
import urllib.parse

def find_file_name(task,view):
    params = OrderedDict([
        ('task', task),
        ('view', view)
    ])
    url = 'http://proteomics2.ucsd.edu/ProteoSAFe/result_json.jsp'
    r = requests.get(url,params)
    r.raise_for_status()
    file_name = r.json()['blockData']['file']
    return file_name

def count(task,view,filter_dict):
    params = OrderedDict([
        ('task', task),
        ('file', find_file_name(task,view)),
        ('pageSize', 1),
        ('offset', 0),
        ('query', encode_all_filters(filter_dict))
    ])
    url = 'https://proteomics2.ucsd.edu/ProteoSAFe/QueryResult'
    r = requests.get(url,params)
    r.raise_for_status()
    row_count = int(r.json()['total_rows'])
    return row_count

def get_all(task,view,filter_dict,page_size=2500,request_limit=20):
    result = []
    c = count(task,view,filter_dict)
    total_pages = math.ceil(c/page_size)
    url = 'https://proteomics2.ucsd.edu/ProteoSAFe/QueryResult'
    params = [
        ('task', task),
        ('file', find_file_name(task,view)),
        ('query', encode_all_filters(filter_dict))
    ]
    rs = (
        grequests.get(url, params = OrderedDict(params + [('pageSize', page_size),('offset', page_offset * page_size)]))
        for page_offset in range(0,total_pages)
    )
    all_responses = []
    for l in grequests.imap(rs,size=request_limit):
        all_responses += l.json()['row_data']
    return all_responses

def link(task,view,filter_dict):
    params = OrderedDict([
        ('task', task),
        ('view', view),
        ('query', encode_all_filters(filter_dict))
    ])
    url = 'http://proteomics2.ucsd.edu/ProteoSAFe/result.jsp?' + urllib.parse.urlencode(params, safe = "#")
    return url

def encode_all_filters(filter_dict):
    new_filter_dict = OrderedDict([
        (k[0],k[1])
        for key in filter_dict
        for k in set_filter_limit(key,filter_dict[key])
    ])
    return "#" + str(json.dumps(new_filter_dict,separators = (',', ':')))

def set_filter_limit(key,value):
    filter_acc = []
    if len(value) == 1:
        filter_acc.append([key+"_input",str(value[0])])
    else:
        if value[0]:
            filter_acc.append([key+"_lowerinput",str(value[0])])
        if value[1]:
            filter_acc.append([key+"_upperinput",str(value[1])])
    return filter_acc

def hyperlink(task,view,filter_dict):
    try:
        c = count(task,view,filter_dict)
        url = link(task,view,filter_dict)
        hlink = "=HYPERLINK(\"" + url + "\"," + str(c) + ")"
    except:
        hlink = ""
    return hlink
