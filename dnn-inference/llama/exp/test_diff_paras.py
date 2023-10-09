# 用来调用本地api，并记录延迟
import requests
import time
import random
from multiprocessing import Pool


class ServiceInvoker:
    def __init__(self, ip="127.0.0.1", port=8080, model_name="llama2-7b-chat") -> None:
        self.url = f"http://{ip}:{port}/predictions/{model_name}"
        self.model_name = model_name

        pass

    def make_prediction_request(self, input_text: str):
    
        try:
            start_t = time.time()
            # 发送请求
            response = requests.post(self.url, data=input_text, headers={"Content-Type": "text/plain"})
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




if __name__ == "__main__":
    # test_invoke()

    # test_mapping()

    test_exp()