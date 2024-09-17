import requests
import os

test_url = "https://raw.githubusercontent.com/chengaopan/AutoMergePublicNodes/master/snippets/nodes.yml"
test_file_path = "test/nodes.yml"

# 确保目录存在
if not os.path.exists(os.path.dirname(test_file_path)):
    print(f"目录不存在，正在创建: {os.path.dirname(test_file_path)}")
    os.makedirs(os.path.dirname(test_file_path))

try:
    response = requests.get(test_url)
    print(f"响应状态码: {response.status_code}")
    if response.status_code == 200:
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"测试文件已成功下载到 {test_file_path}")
        
        # 确认文件是否成功创建
        if os.path.isfile(test_file_path):
            print(f"文件存在: {test_file_path}")
        else:
            print(f"文件不存在: {test_file_path}")
    else:
        print(f"无法下载测试文件: {response.status_code}")
except Exception as e:
    print(f"下载测试文件失败: {e}")
