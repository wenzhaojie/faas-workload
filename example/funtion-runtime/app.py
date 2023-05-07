import multiprocessing
import time
start_init_t = time.time()
import os
import json
from flask import Flask, request
import io_helper
import rs_monitor
from importlib import import_module


app = Flask(__name__)
my_io_helper = io_helper.Redis()
end_init_t = time.time()


@app.route('/')
def hello_world():
    target = os.environ.get('TARGET', 'World')
    return 'Hello WZJ {}!\n'.format(target)

@app.route('/cold_start_flag')
def cold_start_flag():
    cold_start_flag = os.path.exists("/tmp/COLD_START")
    return str(cold_start_flag)

@app.route('/init')
def init():
    if not os.path.exists("/tmp/COLD_START"):
        os.mknod("/tmp/COLD_START")
        COLD_START_FLAG = True
    else:
        COLD_START_FLAG = False
    return str(COLD_START_FLAG)

@app.route('/function', methods=['POST']) 
def lambda_handler():
    '''
    input_obj = {
        "invoke_t": 1664205522.7819338, # 发出调用请求的时间戳
        "input_data_key": "input_data_key",
        "output_data_key": "output_data_key"
        "handler": "matmul"
    }
    '''
    try:
        start_handler_t = time.time()
        # 判断是否冷启动
        # 法1: 估算时间法
        delta_time = start_handler_t - end_init_t
        if delta_time < 0.5:
            COLD_START = True
        else:
            COLD_START = False
        # 法2: 保存文件法
        if not os.path.exists("/tmp/COLD_START"):
            COLD_START_FLAG = True
            try:
                os.mknod("/tmp/COLD_START")
            except:
                pass
        else:
            COLD_START_FLAG = False


        # 得到请求调用输入
        data = request.get_data()
        _str = data.decode('utf-8')
        input_obj = json.loads(_str)

        # 获取调用的信息
        invoke_t = input_obj["invoke_t"]
        input_data_key = input_obj["input_data_key"]
        output_data_key = input_obj["output_data_key"]
        handler = input_obj["handler"]

        # 下载input_data
        input_data, download_t, download_pickle_t = my_io_helper.get_obj(
            obj_key=input_data_key
        )

        # 调用函数
        start_exec_t = time.time()
        handle = getattr(import_module(f"functions.{handler}"), 'handle')
        output_data = handle(input_data)
        end_exec_t = time.time()
        compute_t = end_exec_t - start_exec_t

        # 上传output_data
        upload_t, upload_pickle_t = my_io_helper.put_obj(
            obj_key=output_data_key,
            obj=output_data
        )
        # finish_t
        finish_t = time.time()
        # 生成 log_dict
        log_dict = {
            "init_t": end_init_t - start_init_t,
            "delta_t": delta_time,
            "mapping_delay": start_handler_t - invoke_t,
            "download_t": download_t,
            "download_pickle_t": download_pickle_t,
            "upload_t": upload_t,
            "upload_pickle_t": upload_pickle_t,
            "compute_t": compute_t,
            "finish_t": finish_t,
            "response_t": finish_t - invoke_t,
            "COLD_START": COLD_START,
            "COLD_START_FLAG": COLD_START_FLAG,
        }
        # 生成 result_dict
        FUNCTION_NAME = os.environ.get('FUNCTION_NAME', 'default')
        result_dict = {
            "function_name": FUNCTION_NAME,
            "output_data_key": output_data_key
        }
        # 生成 resource_dict
        try:
            resource_dict = rs_monitor.get_function_resource()
        except Exception:
            resource_dict = {"Exception": "Happened!"}

        # 生成 response
        response = {
            "input_obj": input_obj,
            "log_dict": log_dict,
            "resource_dict": resource_dict,
            "result_dict": result_dict
        }
        # # 删除 input_key
        # my_io_helper.del_key(key=input_data_key)
        return response

    except Exception as e:
        return str(e)


if __name__ == "__main__":
    # 获取CPU核心数
    cpu_count = multiprocessing.cpu_count()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), threaded=False, processes=cpu_count)
