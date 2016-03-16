#!/usr/bin/python

import requests
import json
import sys

views = {
    "cluster":"group_by_spectrum_old_clustered",
    "spectrum":"group_by_spectrum_old_unclustered",
    "cluster_peptide":"group_by_peptide_old_clustered",
    "spectrum_peptide":"group_by_peptide_old_unclustered"
}

task = sys.argv[1]

fdr = .01

def find_file_name(task):
    url = 'http://proteomics2.ucsd.edu/ProteoSAFe/result_json.jsp?task=' + task + '&view=' + "view_result_list"
    r = requests.get(url).json()['blockData'][0]['MzTab_file']
    return r;

def encode_filter(parameter,value,display):
    if display:
        equals = '%22%3A%22'
    else:
        equals = '%2522%253A%2522'
    if display:
        encoded_filter = parameter.replace(' ','%20') + equals + str(value)
    else:
        encoded_filter = parameter.replace(' ','%2520') + equals + str(value)
    return encoded_filter

def count(task,view,filter_dict):
    file_name = find_file_name(task)
    db_filename = view + "-main_" + file_name.replace(".mzTab", ".db")
    url = "https://proteomics2.ucsd.edu/ProteoSAFe/QueryResult?task=" + task + "&file=" + db_filename + "&pageSize=1&offset=0&query=" + encode_all_filters(filter_dict, display=False)
    r = int(requests.get(url).json()[0]['total_rows'])
    return r

def link(task,view,filter_dict):
    url = 'http://proteomics2.ucsd.edu/ProteoSAFe/result.jsp?task=' + task + '&view=' + view + "&query=" + encode_all_filters(filter_dict, display=True)
    return url

def encode_all_filters(filter_dict, display, upper = True, lower = True):
    if display:
        start = '#%7B%22'
    else:
        start = '%2523%257B%2522'
    if display:
        combine = '%22%2C%22'
    else:
        combine = '%2522%252C%2522'
    if display:
        end = '%22%7D'
    else:
        end = '%2522%257D'
    string_acc = []
    for key,value in filter_dict.items():
        if len(value) == 1:
            string_acc.append(encode_filter(key+"_input",value[0],display))
        else:
            if value[0]:
                string_acc.append(encode_filter(key+"_lowerinput",value[0],display))
            if value[1]:
                string_acc.append(encode_filter(key+"_upperinput",value[1],display))
    return start + combine.join(string_acc) + end

def hyperlink(task,view,filter_dict):
    try:
        c = count(task,views[view],filter_dict)
        url = link(task,views[view],filter_dict)
        hlink = "=HYPERLINK(\"" + url + "\"," + str(c) + ")"
    except:
        hlink = ""
    return hlink
