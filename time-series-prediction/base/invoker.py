# 用于调用Knative Function
import json
import os
import requests
from multiprocessing.pool import Pool
import subprocess

class KnativeInvoker:
    def __init__(self, gateway_ip=None, gateway_port=None) -> None:
        if gateway_ip and gateway_port != None:
            self.gateway_ip = gateway_ip
            self.gateway_port = gateway_port
        else:
            self.init()

    def init(self):
        # 从环境变量中初始化
        self.gateway_ip = os.environ.get("GATEWAY_IP", "192.168.122.11")
        self.gateway_port = os.environ.get("GATEWAY_PORT", 31895)

    def invoke_sync_function(self, namespace="faas-scaler", function_name="helloworld-python", data=None):
        headers = {
            "Host": f"{function_name}.{namespace}.example.com"
        }
        url = "http://" + self.gateway_ip + ":" + str(self.gateway_port) + "/function"
        response = requests.post(url, headers=headers, json=data)
        if str(response) == '<Response [200]>': # 成功调用了
            content = response.content.decode('utf-8')
        else:
            content = "<Response [404]>"
        return content

    def invoke_sync_function_dict(self, args):
        namespace = args["namespace"]
        function_name = args["function_name"]
        data =args["data"]
        res = self.invoke_sync_function(namespace=namespace, function_name=function_name, data=data)
        return res

    def mapping(self, namespace, function_name, data):
        return f"{namespace}-{function_name}-{data}"

    def sync_map(self, namespace="faas-scaler", function_name="helloworld-python", data_list=[]):
        map_data_list = [{
                "namespace": namespace,
                "function_name": function_name,
                "data": data,
            }
            for data in data_list]
        
        with Pool(processes=len(map_data_list)) as pool:
            results = pool.map(self.invoke_sync_function_dict, map_data_list)
        return results

    def hey_invoke_sync_function(self, namespace="faas-scaler", function_name="helloworld-python", n_request=1, data=None):
        # 调用hey来并发调用
        cmd = f"hey -c {n_request} -n 1 -q 1 -m POST -z 1s -host '{function_name}.{namespace}.example.com' -d {json.dumps(data)} http://192.168.122.11:31895/function"
        hey_output = subprocess.getoutput(
            cmd=cmd
        )
        print(f"hey_output:{hey_output}")




        


if __name__ == "__main__":
    my_invoker = KnativeInvoker()

    # response = my_invoker.invoke_sync_function(namespace="default", function_name="helloworld-python", data="123")
    # print(response)

    response = my_invoker.sync_map(namespace="default", function_name="helloworld-python", data_list=["123","234","345"])
    print(response)

    # my_invoker.hey_invoke_sync_function(namespace="default", function_name="helloworld-python", n_request=10,  data="123")

    