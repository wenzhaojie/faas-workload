# 用于进行实验并收集实验数据
import multiprocessing
import invoker
import io_helper
import time
from multiprocessing import Manager
import csv
import json
import copy
import os

import sys
sys.path.insert(0, "/home/wzj/GiteeProjects/faas-scaler")
from src.core.datasets import Azure_dataset, Crane_dataset

my_invoker = invoker.KnativeInvoker()
my_io_helper = io_helper.Redis()

def put_input_data():
    my_io_helper.put_obj(
        obj_key="input_data_key",
        obj="123",
    )
    print(f"已经初始化了input_data_key!")


def invocation_in_sec(res_queue, namespace="faas-scaler", function_name="test-intra-parallelism", handler="matmul", timestamp=0, n_request=1):
    input_obj = {
        "invoke_t": time.time(), # 发出调用请求的时间戳
        "timestamp": timestamp, # 模拟请求调用的第几秒
        "n_request": n_request, # 一秒调用有几个并发请求
        "index": 0, # 第几个并发请求
        "input_data_key": "input_data_key",
        "output_data_key": "output_data_key",
        "handler": handler,
    }
    # 开始并发调用
    data_list = []
    for index in range(n_request):
        _input_obj = copy.deepcopy(input_obj)
        _input_obj["index"] = index
        data_list.append(_input_obj)

    response = my_invoker.sync_map(
        namespace=namespace,
        function_name=function_name,
        data_list=data_list,
    )

    res_queue.put(response)
    return response


def test(namespace="faas-scaler", function_name="test-intra-parallelism", log_path="test.csv"):
    m = Manager()
    res_queue = m.Queue()
    invocation_in_sec(res_queue=res_queue, namespace="faas-scaler", function_name="test-intra-parallelism", handler="matmul", timestamp=0, n_request=3)

    # 展示结果保存
    print("从缓存队列中取结果!")
    log_dict_list = []
    while not res_queue.empty():
        res = res_queue.get()
        log_dict_list.extend(res)

    print(f"log_dict_list:{log_dict_list}")


def do_exp(namespace="faas-scaler", function_name="test-intra-parallelism", handler="matmul", trace_hash_function="default", start_day=0, end_day=3, log_dir="logs/"):
    # 进行一次调用
    put_input_data()
    m = Manager()
    res_queue = m.Queue()

    process_list = []

    for timestamp in range(10):
        start_time = time.time()
        print(f"当前模拟调用第{timestamp}秒")
        n_request = 3
        p = multiprocessing.Process(target=invocation_in_sec, args=(res_queue, namespace, function_name, handler, timestamp, n_request))
        process_list.append(p)
        p.start()
        end_time = time.time()
        send_time = end_time - start_time
        print(f"休息{1-send_time}秒")
        time.sleep(1-send_time)
    
    for process in process_list:
        process.join()

    
    # 展示结果保存
    print("从缓存队列中取结果!")
    result_dict_list = []
    while not res_queue.empty():
        res = res_queue.get()
        print(f"type(res):{type(res)}")
        res = [json.loads(item) for item in res]
        result_dict_list.extend(res)

    print(f"log_dict_list:{result_dict_list}")

    print("写入csv!")
    filename = f"{trace_hash_function}-day{start_day}-to-day{end_day}-{handler}-log.csv"
    log_path = os.path.join(log_dir, filename)
    with open(log_path, 'w', newline='') as csvfile:
        fieldnames = list(result_dict_list[0].keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(result_dict_list)

# 分析 result_dict_list
def analysis(result_dict_list):
    pass 


    


if __name__ == "__main__":
    # test()
    do_exp()
