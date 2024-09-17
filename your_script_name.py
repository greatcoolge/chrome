import requests
import socket
import time
import yaml
import os

LATENCY_THRESHOLD = 6  # 延迟阈值（毫秒）
SUBSCRIPTION_URLS = [
    "https://raw.githubusercontent.com/chengaopan/AutoMergePublicNodes/master/snippets/nodes.yml",
    # 可以继续添加更多的订阅链接
]
OUTPUT_DIR = "sub"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "available_proxies.yaml")
LOCAL_SUBSCRIPTION_FILE = os.path.join(OUTPUT_DIR, "nodes.yml")  # 下载到本地的文件路径

# 确保输出目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 使用 TCP 连接测试节点的可用性和延迟
def tcp_connection_test(server, port, timeout=5):
    try:
        latencies = []
        for _ in range(3):  # 测试 3 次取平均值
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            start_time = time.time()
            result = sock.connect_ex((server, port))
            end_time = time.time()
            latency = (end_time - start_time) * 1000

            if result == 0:  # 0 表示连接成功
                latencies.append(latency)
            sock.close()

        if latencies:
            average_latency = sum(latencies) / len(latencies)
            return True, average_latency
        else:
            return False, None
    except Exception as e:
        print(f"TCP 连接测试失败: {e}")
        return False, None

# 检测代理的可用性和延迟
def check_proxies_availability(proxies):
    available_proxies = []
    print(f"正在测试 {len(proxies)} 个代理节点的可用性...")
    for index, proxy in enumerate(proxies, start=1):
        server = proxy.get("server")
        port = proxy.get("port")
        name = proxy.get("name")

        if server and port:
            is_available, latency = tcp_connection_test(server, int(port))
            if is_available and latency <= LATENCY_THRESHOLD:
                print(f"节点 {index} ({name}): {server}:{port} 可用，延迟 {latency:.2f} ms")
                available_proxies.append(proxy)
            else:
                print(f"节点 {index} ({name}): {server}:{port} 延迟过高或不可用，移除")
        else:
            print(f"节点 {index} ({name}) 的信息不完整，跳过检查")
    return available_proxies

# 从本地订阅文件获取代理节点列表
def fetch_proxies_from_local_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            proxies_config = yaml.safe_load(f)
            return proxies_config.get("proxies", [])
    except Exception as e:
        print(f"读取本地订阅文件失败: {e}")
        return []

# 下载订阅文件到本地
def download_subscription_to_local(subscription_url, local_file_path):
    try:
        response = requests.get(subscription_url)
        if response.status_code == 200:
            with open(local_file_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"订阅文件已下载到 {local_file_path}")
        else:
            print(f"无法下载订阅文件: {response.status_code}")
    except Exception as e:
        print(f"下载订阅文件失败: {e}")

# 将可用的代理节点保存到文件
def save_available_proxies(proxies, output_file):
    if not proxies:
        print("没有可用的代理，跳过保存。")
        return
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump({"proxies": proxies}, f, allow_unicode=True)
        print(f"可用代理已保存到 {output_file}")
    except Exception as e:
        print(f"保存代理到文件失败: {e}")

def main():
    all_proxies = []

    # 下载订阅文件到本地
    for url in SUBSCRIPTION_URLS:
        if url:  # 确保 URL 不为空
            download_subscription_to_local(url, LOCAL_SUBSCRIPTION_FILE)
        else:
            print("订阅链接为空，跳过...")

    # 从本地文件中读取代理节点
    proxies = fetch_proxies_from_local_file(LOCAL_SUBSCRIPTION_FILE)
    if proxies:
        print(f"共找到 {len(proxies)} 个代理节点，开始测试...")
        available_proxies = check_proxies_availability(proxies)
        print(f"共找到 {len(available_proxies)} 个可用代理")
        save_available_proxies(available_proxies, OUTPUT_FILE)
    else:
        print("没有找到代理节点，或解析失败。")

if __name__ == "__main__":
    main()
