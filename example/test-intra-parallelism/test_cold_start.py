import os
def test():
    if not os.path.exists("/tmp/COLD_START"):
        os.mknod("/tmp/COLD_START")
        COLD_START_FLAG = True
    else:
        COLD_START_FLAG = False
    return str(COLD_START_FLAG)


if __name__ == "__main__":
    print(test())