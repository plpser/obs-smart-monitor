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
            f.write("用户A: 大家好\n")
            f.write("用户B: 你好\n")
            f.write(f"这是第{i+1}个测试文件的最后一行\n")
        
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