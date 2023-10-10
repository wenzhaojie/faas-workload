# 用来调用本地api，并记录延迟
import requests
import time
import random
from multiprocessing import Pool
import subprocess
import os
import json


class ServiceInvoker:
    def __init__(self, ip="127.0.0.1", port=8080, model_name="llama2-7b-chat") -> None:
        self.url = f"http://{ip}:{port}/predictions/{model_name}"
        self.model_name = model_name

        pass

    def make_prediction_request(self, input_text: str):
    
        try:
            start_t = time.time()
            # 发送请求
            response = requests.post(self.url, data=input_text, headers={"Content-Type": "text/plain"}, timeout=60)
            end_t = time.time()
            latency = end_t - start_t
            # 打印响应的状态码和内容
            status_code = response.status_code
            output_text = response.text
            res_dict = {
                "start_t": start_t,
                "end_t": end_t,
                "latency": latency,
                "status_code": status_code,
                "input_text": input_text,
                "output_text": output_text,
                "input_len": len(input_text),
                "output_len": len(output_text),
                "output_speed": len(output_text) / latency,
                "model_name": self.model_name
            }
            return res_dict

        except Exception as e:
            print(f"An error occurred: {str(e)}")

    def mapping(self, input_text_list: list):
        # 用多进程方式并行调用make_prediction_request
        with Pool(processes=64) as pool:
            res_dict_list = pool.map(self.make_prediction_request, input_text_list)
        return res_dict_list



def test_invoke():
    invoker = ServiceInvoker()
    res_dict = invoker.make_prediction_request("what is the recipe of mayonnaise?")
    print(res_dict)

def test_mapping():
    invoker = ServiceInvoker()
    input_text_list = ["what is the recipe of mayonnaise?", "what is the recipe of mayonnaise?", "what is the recipe of mayonnaise?"]
    res_dict_list = invoker.mapping(input_text_list)
    print(res_dict_list)



class InputGenerator:
    def __init__(self, base_question_txt_path="./100_question.txt") -> None:
        self.base_question_txt_path = base_question_txt_path
        pass

    def get_input_text_list(self):
        # 读取base_question.txt
        with open(self.base_question_txt_path, "r") as f:
            lines = f.readlines()
        # 生成输入
        input_text_list = []
        for line in lines:
            input_text_list.append(line.strip())
        return input_text_list
    
    def random_choice_batch(self, input_text_list, batch_size=1):
        # 随机从input_text_list选择batch_size个作为batch
        batch = random.choices(input_text_list, k=batch_size)
        return batch
    
    def dublicate_random_choice_batch(self, input_text_list, batch_size=1):
        # 随机从input_text_list选择1个并复制batch_size次作为batch
        batch = random.choices(input_text_list, k=1)
        batch = batch * batch_size
        return batch
    


def exp(batch_size=1, num_worker=1):
    summary_res_dict_list = []
    batch_history = []

    # 获取输入
    input_generator = InputGenerator()
    input_text_list = input_generator.get_input_text_list()

    repeat = 50
    for i in range(repeat):
        print(f"Repeat {i+1}/{repeat}")
        # 随机选择batch_size个作为batch, 但是不能和之前的batch重复
        while True:
            batch = input_generator.dublicate_random_choice_batch(input_text_list, batch_size=batch_size)
            if batch not in batch_history:
                break
        
        # 调用服务
        invoker = ServiceInvoker()
        res_dict_list = invoker.mapping(batch)
        batch_history.append(batch)

        # 在res_dict_list中添加batch_size和num_worker
        for res_dict in res_dict_list:
            res_dict["batch_size"] = batch_size
            res_dict["num_worker"] = num_worker

        summary_res_dict_list.extend(res_dict_list)

    # 写入csv文件
    import csv
    csv_file_path = f"./exp_result_batch_size_{batch_size}_num_worker_{num_worker}.csv"
    with open(csv_file_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=summary_res_dict_list[0].keys())
        writer.writeheader()
        writer.writerows(summary_res_dict_list)
    print(f"Write to {csv_file_path} successfully!")



def test_exp():
    # exp(batch_size=1, num_worker=1)
    # exp(batch_size=2, num_worker=1)
    # exp(batch_size=3, num_worker=1)
    # exp(batch_size=4, num_worker=1)
    # exp(batch_size=5, num_worker=1)
    # exp(batch_size=6, num_worker=1)
    # exp(batch_size=12, num_worker=1)
    # exp(batch_size=24, num_worker=1)
    # exp(batch_size=32, num_worker=1)
    # exp(batch_size=32, num_worker=2)
    # exp(batch_size=24, num_worker=2)
    exp(batch_size=12, num_worker=2)



# 修改model-config.yaml
def modify_model_config(min_workers, max_workers, batch_size, max_batch_delay=5000, max_length=500, template_path="../model-config.yaml", save_path="../model_store/llama2-7b-chat/model-config.yaml"):
    import yaml
    with open(template_path, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    config["batchSize"] = batch_size
    config["maxBatchDelay"] = max_batch_delay
    config["maxWorkers"] = max_workers
    config["minWorkers"] = min_workers

    config["handler"]["max_length"] = max_length

    # 保存
    with open(save_path, "w") as f:
        yaml.dump(config, f)
    print(f"Save to {save_path} successfully!")


def test_modify_model_config():
    modify_model_config(min_workers=1, max_workers=1, batch_size=1, max_length=100)


# 启动torch服务
def start_serving(num_workers=1, batch_size=1, max_length=100):
    # 首先终止之前的服务
    stop_serving()

    # 修改model-config.yaml
    modify_model_config(min_workers=num_workers, max_workers=num_workers, batch_size=batch_size, max_length=max_length)

    # 启动服务
    command = [
        "torchserve",
        "--start",
        "--ncs",
        "--ts-config",
        "config.properties",
        "--model-store",
        "model_store",
        "--models",
        "llama2-7b-chat"
    ]

    # 进入上一级目录
    os.chdir("..")

    # 使用Popen以非阻塞方式运行命令
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # 阻塞地等待命令完成
    # process.communicate()

    # 返回当前目录
    os.chdir("./exp")

    # 测试服务是否启动成功 curl -X GET http://127.0.0.1:8081/models/llama2-7b-chat
    # UNLOADING READY
    while True:
        try:
            response = requests.get("http://127.0.0.1:8081/models/llama2-7b-chat")
        except Exception as e:
            continue
        res_text = response.text
        # json.loads(res_text)
        res = json.loads(res_text)
        # print(res[0]["workers"][0])
        time.sleep(1)

        # res[0]["workers"] 中的所有status都是READY
        if all([worker["status"] == "READY" for worker in res[0]["workers"]]):
            break
    print("Model is ready!")
    # num_workers=1, batch_size=1, max_length=100
    print(f"num_workers={num_workers}, batch_size={batch_size}, max_length={max_length}")

    # 等待10秒
    print("Wait for 10 seconds...")
    time.sleep(10)


def stop_serving():
    # 终止服务 用 getoutput
    cmd = "torchserve --stop"
    output = subprocess.getoutput(cmd)
    print(output)
    # 等待10秒
    print("Wait for 10 seconds...")
    time.sleep(10)

def test_start_serving():
    start_serving(num_workers=1, batch_size=1, max_length=100)
    

def test_stop_serving():
    stop_serving()
    print("Stop serving successfully!")


def get_metrics():
    # nvidia-smi获取metrics
    cmd = "nvidia-smi --query-gpu=utilization.gpu,utilization.memory,memory.total,memory.free,memory.used --format=csv"
    output = subprocess.getoutput(cmd)
    
    # output 是csv格式的字符串，转换成字典
    output = output.split("\n")
    output = [line.split(",") for line in output]
    output = output[1:]
    output = [{"gpu_util": line[0], "memory_util": line[1], "memory_total": line[2], "memory_free": line[3], "memory_used": line[4]} for line in output][0]

    return output



def test_get_metrics():
    get_metrics()
    

def automatic_exp(batch_size_list=[1,2,4,8,16,32], num_worker_list=[1,2], max_length_list=[50,100], save_dir="./results/2023-10-10", min_index=0, max_index=1):

    # 创建save_dir
    os.makedirs(save_dir, exist_ok=True)
    
    # 获取输入
    input_generator = InputGenerator()
    input_text_list = input_generator.get_input_text_list()

    total_res_dict_list = []

    
    for num_worker in num_worker_list:
        for batch_size in batch_size_list:
            for max_length in max_length_list:

                # 启动服务
                start_serving(num_workers=num_worker, batch_size=batch_size, max_length=max_length)

                # 等待5秒
                print("Wait for 5 seconds...")
                time.sleep(5)

                # 记录metrics
                metrics_dict = get_metrics()
                inited_gpu_memory_used = metrics_dict["memory_used"]

                
                summary_res_dict_list = []

                for index in range(min_index, min(len(input_text_list), max_index)):
                    print(f"index={index}")
                    # data
                    data = input_text_list[index]
                    # batch 
                    batch = [data] * batch_size

                    print(f"batch: {batch}")
                    
                    # 调用服务
                    invoker = ServiceInvoker()

                    # retry 3 times
                    try:
                        # 等待5秒
                        print("Wait for 5 seconds...")
                        time.sleep(5)
                        start_t = time.time()
                        res_dict_list = invoker.mapping(batch)
                        end_t = time.time()
                        batch_t = end_t - start_t

                        print(f"batch_t: {batch_t}, batch_size: {batch_size}, num_worker: {num_worker}, max_length: {max_length}, index: {index}")
                        print("output_text:", res_dict_list[0]["output_text"])
                    
                    except Exception as e:
                        print(f"An error occurred: {str(e)}")
                        # 跳过
                        continue

                    # 记录metrics
                    metrics_dict = get_metrics()
                    runtime_gpu_memory_used = metrics_dict["memory_used"]

                    
                    # 在res_dict_list中添加batch_size和num_worker和max_length
                    for res_dict in res_dict_list:
                        res_dict["batch_size"] = batch_size
                        res_dict["num_worker"] = num_worker
                        res_dict["max_length"] = max_length
                        res_dict["inited_gpu_memory_used"] = inited_gpu_memory_used
                        res_dict["runtime_gpu_memory_used"] = runtime_gpu_memory_used
                        res_dict["index"] = index
                        res_dict["batch_t"] = batch_t

                    summary_res_dict_list.extend(res_dict_list)
                    total_res_dict_list.extend(res_dict_list)

                    # 等待5秒
                    print("Wait for 5 seconds...")
                    time.sleep(5)

                # 写入csv文件
                import csv
                csv_file_name = f"exp_result_batch_size_{batch_size}_num_worker_{num_worker}_max_length_{max_length}.csv"

                csv_file_path = os.path.join(save_dir, csv_file_name)

                with open(csv_file_path, "w", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=summary_res_dict_list[0].keys())
                    writer.writeheader()
                    writer.writerows(summary_res_dict_list)
                print(f"Write to {csv_file_path} successfully!")


    # 写入csv文件
    import csv
    csv_file_name = f"exp_result_total.csv"
    csv_file_path = os.path.join(save_dir, csv_file_name)
    with open(csv_file_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=total_res_dict_list[0].keys())
        writer.writeheader()
        writer.writerows(total_res_dict_list)
    print(f"Write to {csv_file_path} successfully!")



def test_automatic_exp():
    automatic_exp(batch_size_list=[16], num_worker_list=[1,2,], max_length_list=[200], save_dir="./results/2023-10-10/test", min_index=14, max_index=100,)



def exp1():
    automatic_exp(batch_size_list=[1,2,4,8,16,32,], num_worker_list=[1,2], max_length_list=[50,100,], save_dir="./results/2023-10-10-21-44-exp1", max_index=10,)








if __name__ == "__main__":
    # test_invoke()

    # test_mapping()

    test_exp()

    # test_modify_model_config()

    # test_start_serving()

    # test_stop_serving()

    # test_get_metrics()
    
    # test_automatic_exp()
    
    # exp1()