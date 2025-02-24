import re
from datetime import datetime
from elasticsearch import Elasticsearch

log_file = 'output.log'
trx_count = 0
error_code = []
sum_request_time = 0
request_count = 0
elasticpass = 'elasticpass123'

client = Elasticsearch("http://127.0.0.1:9200")

def push_doc(metric,value):
    doc = {
        'metric_name': metric,
        'value': value,
        'timestamp': datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    }

    client.index(index="processed_metric", document=doc)

def push_parsed_log(service, http_code, path, req_time):
    doc = {
        'service_name': service,
        'endpoint_path': path,
        'http_code': http_code,
        'request_time_in_ms': req_time,
        'timestamp': datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    }

    client.index(index="parsed_log", document=doc)

def ratio_error_code(error_code):

    count_5xx = 0
    count_4xx = 0
    count_else = 0
    for code in error_code:
        if code[0] == '4':
            count_4xx += 1
        elif code[0] == '5':
            count_5xx += 1
        else:
            count_else += 1
    
    push_doc('Total Number of HTTP 5xx error', count_5xx)
    push_doc('Total Number of HTTP 4xx error', count_4xx)
    push_doc('Total Number of non HTTP 5xx or 4xx error', count_else)

def average_req_time(request_time, request_count):
    average_time = request_time/request_count
    push_doc('Average HTTP Request Time', str(round(average_time, 2)))

with open(log_file, 'r') as file:
    for line in file:
        match = re.match(
            r'(\d{2}/\d{2}/\d{2}:\d{2}:\d{2}:\d{2}) (\w+) (\d{3}) (\w+) (\w+) (\w+) "(.*?)"', line)
        if match:
            trx_count += 1
            request_count += 1
            timestamp = match.group(1)
            service = match.group(2)
            error_code.append(match.group(3))
            request_time = match.group(4).split('ms')[0]
            sum_request_time += int(match.group(4).split('ms')[0])
            ## PUSH HTTP CODE TO ELASTICSEARCH ###
            push_parsed_log(service, match.group(3), match.group(7), match.group(4).split('ms')[0])
    ### CALCULATE RATIO OF 5xx, 4xx, and other HTTP CODE ###
    ratio_error_code(error_code)
    ### CALCULATE AVERAGE REQUEST TIME ###
    average_req_time(sum_request_time, request_count)
    ### PUSH TOTAL REQUEST/TRANSACTION ###
    push_doc('Total Transaction from log', trx_count)
            