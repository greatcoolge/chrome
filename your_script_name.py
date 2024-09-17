import base64
import requests
import socket
import time
import yaml

# 延迟阈值（毫秒）
LATENCY_THRESHOLD = 6  # 设置为 6 毫秒，可以根据需要调整
SUBSCRIPTION_URLS = [  # 支持多个订阅链接
    "https://raw.githubusercontent.com/chengaopan/AutoMergePublicNodes/master/snippets/nodes.yml",
    "",
    # 可以继续添加更多的订阅链接
]
OUTPUT_FILE = "available_proxies.yaml"  # 输出文件

# 使用 TCP 连接测试节点的可用性和延迟
def tcp_connection_test(server, port, timeout=5):
    try:
        latencies = []
        for _ in range(3):  # 测试 3 次取平均值
            # 创建一个 TCP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)

            # 记录连接开始时间
            start_time = time.time()

            # 尝试连接服务器
            result = sock.connect_ex((server, port))

            # 记录连接结束时间
            end_time = time.time()

            # 计算延迟（毫秒）
            latency = (end_time - start_time) * 1000

            # 检查连接是否成功（返回值 0 表示成功）
            if result == 0:
                latencies.append(latency)
            else:
                print(f"{server}:{port} 不可用")

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

# 从订阅链接获取代理节点列表
def fetch_proxies_from_subscription(subscription_url):
    try:
        response = requests.get(subscription_url)
        if response.status_code == 200:
            # 订阅内容是 Base64 编码的，需要解码
            decoded_data = base64.b64decode(response.content).decode("utf-8")
            # 解析 YAML 格式的代理配置
            proxies_config = yaml.safe_load(decoded_data)
            return proxies_config.get("proxies", [])
        else:
            print(f"无法获取订阅链接: {response.status_code}")
            return []
    except Exception as e:
        print(f"获取订阅内容失败: {e}")
        return []

# 将可用的代理节点保存到文件
def save_available_proxies(proxies, output_file):
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump({"proxies": proxies}, f, allow_unicode=True)
        print(f"可用代理已保存到 {output_file}")
    except Exception as e:
        print(f"保存代理到文件失败: {e}")

def main():
    all_proxies = []

    # 从多个订阅中获取代理节点
    for url in SUBSCRIPTION_URLS:
        print(f"正在从 {url} 获取代理节点...")
        proxies = fetch_proxies_from_subscription(url)
        all_proxies.extend(proxies)

    if all_proxies:
        print(f"共找到 {len(all_proxies)} 个代理节点，开始测试...")
        available_proxies = check_proxies_availability(all_proxies)

        # 保存可用的代理到文件
        save_available_proxies(available_proxies, OUTPUT_FILE)
    else:
        print("没有找到代理节点，或解析失败。")

if __name__ == "__main__":
    main()
