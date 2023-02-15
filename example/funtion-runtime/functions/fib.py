import time
import numpy as np

def handle(input_data):
    n_time = 1
    # 单线程计算
    start_t = time.time()
    for i in range(n_time):
        fib(n=int(10000000))
    compute_t = time.time() - start_t
    output_data = []
    print(f"compute_t:{compute_t}")
    return output_data


def fib(n: int) -> int:
    MOD = 10 ** 9 + 7
    if n < 2:
        return n
    p, q, r = 0, 0, 1
    for i in range(2, n + 1):
        p = q
        q = r
        r = (p + q) % MOD
    return r


if __name__ == "__main__":
    handle(2)