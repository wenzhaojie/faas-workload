import time
import numpy as np

def handle(input_data):
    output_data = input_data
    # 大矩阵乘法
    a = np.random.rand(10000,10000)
    b = np.random.rand(10000,10000)
    start_t = time.time()
    for i in range(10):
        c = np.multiply(a, b)
    compute_t = time.time() - start_t
    print(f"compute_t:{compute_t}")
    return output_data


if __name__ == "__main__":
    handle("123")