# 用于根据配置选项生成 service.yaml
import yaml
import copy

def save_dict_to_yaml(dict_value: dict, save_path: str):
    """dict保存为yaml"""
    with open(save_path, 'w') as file:
        file.write(yaml.dump(dict_value, allow_unicode=True))


def read_yaml_to_dict(yaml_path: str, ):
    with open(yaml_path) as file:
        dict_value = yaml.load(file.read(), Loader=yaml.FullLoader)
        return dict_value


def generate_by_configuration(function_name: str, namespace: str, max_scale: int, min_scale: int, keep_alive_window: int, panic_threshold_percentage: float, panic_window_percentage: float, max_inflight: int, image_repo_server_ip: str, image_repo_server_port: int, cpu_limit_in_vcpu: float, memory_limit_in_mb: int):
    config = read_yaml_to_dict(yaml_path="./service.yaml")
    new_config = copy.deepcopy(config)
    print(config)
    #print(config["metadata"])
    new_config["metadata"]["name"] = function_name
    new_config["metadata"]["namespace"] = namespace
    new_config["spec"]["template"]["metadata"]["annotations"]["autoscaling.knative.dev/max-scale"] = str(max_scale)
    new_config["spec"]["template"]["metadata"]["annotations"]["autoscaling.knative.dev/min-scale"] = str(min_scale)
    new_config["spec"]["template"]["metadata"]["annotations"]["autoscaling.knative.dev/window"] = str(keep_alive_window)+"s"
    new_config["spec"]["template"]["metadata"]["annotations"]["autoscaling.knative.dev/panic-threshold-percentage"] = str(panic_threshold_percentage)
    new_config["spec"]["template"]["metadata"]["annotations"]["autoscaling.knative.dev/panic-window-percentage"] = str(panic_window_percentage)
    new_config["spec"]["template"]["spec"]["containerConcurrency"] = max_inflight
    new_config["spec"]["template"]["spec"]["containers"][0]["image"] = f"{image_repo_server_ip}:{image_repo_server_port}/{function_name}:latest"
    new_config["spec"]["template"]["spec"]["containers"][0]["resources"]["limits"]["cpu"] =  f"{cpu_limit_in_vcpu * 1000}m"
    new_config["spec"]["template"]["spec"]["containers"][0]["resources"]["limits"]["memory"] =  f"{memory_limit_in_mb}Mi"
    new_config["spec"]["template"]["spec"]["containers"][0]["resources"]["requests"]["cpu"] =  f"{cpu_limit_in_vcpu * 1000}m"
    new_config["spec"]["template"]["spec"]["containers"][0]["resources"]["requests"]["memory"] =  f"{memory_limit_in_mb}Mi"
    new_config["spec"]["template"]["spec"]["containers"][0]["env"][0]["value"] = function_name
    new_config["spec"]["template"]["spec"]["containers"][0]["env"][2]["value"] = str(max_inflight)
    return new_config


if __name__ == "__main__":
    config_dict = generate_by_configuration(
        function_name="test-intra-parallelism1",
        namespace="faas-scale",
        max_scale=21,
        min_scale=1,
        keep_alive_window=61,
        panic_threshold_percentage=200.1,
        panic_window_percentage=10.1,
        max_inflight=2,
        image_repo_server_ip="192.168.122.12",
        image_repo_server_port=5001,
        cpu_limit_in_vcpu=4,
        memory_limit_in_mb=20480,
    )
    print(f"new_config:{config_dict}")
    save_dict_to_yaml(dict_value=config_dict, save_path="./generated.yaml")