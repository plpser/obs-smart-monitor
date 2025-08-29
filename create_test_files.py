"""
用于测试文件监控程序的辅助脚本
创建模拟的用户发言记录文件
"""
import os
import time
from datetime import datetime

def create_test_files():
    """创建测试用的用户发言记录文件"""
    
    # 在当前目录创建测试目录
    test_dir = "test_logs"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    
    # 创建几个测试文件
    files = [
        "用户发言记录_2025_01_01.txt",
        "用户发言记录_2025_01_02.txt", 
        "用户发言记录_2025_01_03.txt"
    ]
    
    for i, filename in enumerate(files):
        filepath = os.path.join(test_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"这是测试文件 {filename}\n")
            f.write(f"创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("2025-08-29 22:50:15[用户发言]张三： 大家好\n")
            f.write("2025-08-29 22:51:30[用户发言]李四： 你好张三\n")
            f.write("2025-08-29 22:52:45[用户发言]王五： 今天天气不错\n")
            # 添加一些包含"看"字和数字的测试内容
            f.write(f"2025-08-29 22:53:0{i+1}[用户发言]测试用户： 看{100+i*10}号房间\n")
            # 添加更多测试案例
            test_cases = [
                f"2025-08-29 22:54:0{i+1}[用户发言]用户A： 我想看{i+1}集\n",
                f"2025-08-29 22:55:0{i+1}[用户发言]用户B： 看看这个\n",
                f"2025-08-29 22:56:0{i+1}[用户发言]用户C： 看{i+2}.5个小时\n"
            ]
            for test_case in test_cases:
                f.write(test_case)
        
        # 设置不同的创建时间（让最后一个文件是最新的）
        if i < len(files) - 1:
            time.sleep(1)
    
    print(f"测试文件已创建在 {test_dir} 目录下:")
    for filename in files:
        filepath = os.path.join(test_dir, filename)
        create_time = datetime.fromtimestamp(os.path.getctime(filepath))
        print(f"  {filename} - 创建时间: {create_time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    create_test_files()