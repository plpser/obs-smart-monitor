import os
import time
import glob
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileMonitor(FileSystemEventHandler):
    """文件监控类，监控指定文件的变化"""
    
    def __init__(self, file_path):
        """
        初始化文件监控器
        :param file_path: 要监控的文件路径
        """
        self.file_path = os.path.abspath(file_path)
        self.file_dir = os.path.dirname(self.file_path)
        self.file_name = os.path.basename(self.file_path)
        self.last_modified_time = 0
        self.check_interval = 600  # 10分钟 = 600秒
        self.content_check_interval = 0.5  # 0.5秒
        
        # 检查文件是否存在
        if not os.path.exists(self.file_path):
            self._print_warning(f"文件 {self.file_path} 不存在")
        else:
            self.last_modified_time = os.path.getmtime(self.file_path)
            self._print_info(f"开始监控文件: {os.path.basename(self.file_path)}")
    
    def _print_info(self, message):
        """打印信息消息"""
        timestamp = time.strftime('%H:%M:%S')
        print(f"\n📅 [{timestamp}] {message}")
    
    def _print_success(self, message):
        """打印成功消息"""
        timestamp = time.strftime('%H:%M:%S')
        print(f"\n✅ [{timestamp}] {message}")
    
    def _print_warning(self, message):
        """打印警告消息"""
        timestamp = time.strftime('%H:%M:%S')
        print(f"\n⚠️  [{timestamp}] {message}")
    
    def _print_error(self, message):
        """打印错误消息"""
        timestamp = time.strftime('%H:%M:%S')
        print(f"\n❌ [{timestamp}] {message}")
    
    def _print_content_change(self, content):
        """打印文件内容变化"""
        timestamp = time.strftime('%H:%M:%S')
        print(f"\n📄 [{timestamp}] 文件内容变化")
        print(f"   📁 文件: {os.path.basename(self.file_path)}")
        print(f"   📝 最后一行: {content}")
        print("   " + "-" * 50)
    
    def _print_file_switch(self, old_file, new_file):
        """打印文件切换信息"""
        timestamp = time.strftime('%H:%M:%S')
        print(f"\n🔄 [{timestamp}] 文件切换")
        print(f"   ⛔ 原文件: {os.path.basename(old_file)}")
        print(f"   ✅ 新文件: {os.path.basename(new_file)}")
        print("   " + "-" * 50)
    
    def get_last_line(self):
        """获取文件的最后一行内容"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                if lines:
                    # 去除末尾的换行符
                    last_line = lines[-1].strip()
                    return last_line if last_line else "最后一行为空"
                else:
                    return "文件为空"
        except FileNotFoundError:
            return "文件不存在"
        except Exception as e:
            return f"读取文件出错: {str(e)}"
    
    def on_modified(self, event):
        """文件修改事件处理"""
        if event.is_directory:
            return
        
        # 检查是否是我们要监控的文件
        if os.path.abspath(event.src_path) == self.file_path:
            current_modified_time = os.path.getmtime(self.file_path)
            
            # 避免重复触发（有时会触发多次修改事件）
            if current_modified_time > self.last_modified_time:
                self.last_modified_time = current_modified_time
                
                last_line = self.get_last_line()
                self._print_content_change(last_line)
    
    def on_created(self, event):
        """文件创建事件处理"""
        if event.is_directory:
            return
        
        if os.path.abspath(event.src_path) == self.file_path:
            self._print_success(f"文件已创建: {os.path.basename(self.file_path)}")
            last_line = self.get_last_line()
            self._print_content_change(last_line)
    
    def on_deleted(self, event):
        """文件删除事件处理"""
        if event.is_directory:
            return
        
        if os.path.abspath(event.src_path) == self.file_path:
            self._print_warning(f"文件被删除: {os.path.basename(self.file_path)}")
            print("   🔍 正在查找新的用户发言记录文件...")
            
            # 重新查找最新文件
            log_directory = os.path.dirname(self.file_path)
            new_file = find_latest_user_speech_log(log_directory)
            
            if new_file and new_file != self.file_path:
                old_file = self.file_path
                # 更新监控目标
                self.file_path = os.path.abspath(new_file)
                self.file_name = os.path.basename(self.file_path)
                self.last_modified_time = os.path.getmtime(self.file_path) if os.path.exists(self.file_path) else 0
                
                self._print_file_switch(old_file, new_file)
                # 显示新文件的最后一行
                last_line = self.get_last_line()
                print(f"   📝 新文件最后一行: {last_line}")
            else:
                self._print_error("没有找到其他可监控的文件")
    
    def check_for_newer_files(self):
        """检查是否有更新的用户发言记录文件"""
        try:
            log_directory = os.path.dirname(self.file_path)
            newer_file = find_latest_user_speech_log(log_directory)
            
            if newer_file and newer_file != self.file_path:
                # 检查新文件的创建时间是否更新
                current_create_time = os.path.getctime(self.file_path) if os.path.exists(self.file_path) else 0
                new_create_time = os.path.getctime(newer_file)
                
                if new_create_time > current_create_time:
                    old_file = self.file_path
                    # 更新监控目标
                    self.file_path = os.path.abspath(newer_file)
                    self.file_name = os.path.basename(self.file_path)
                    self.last_modified_time = os.path.getmtime(self.file_path)
                    
                    self._print_success("发现更新的文件")
                    self._print_file_switch(old_file, newer_file)
                    # 显示新文件的最后一行
                    last_line = self.get_last_line()
                    print(f"   📝 新文件最后一行: {last_line}")
                    return True
        except Exception as e:
            self._print_error(f"检查新文件时出错: {str(e)}")
        
        return False
    
    def start_monitoring(self):
        """开始监控文件"""
        observer = Observer()
        observer.schedule(self, self.file_dir, recursive=False)
        observer.start()
        
        try:
            print("\n" + "=" * 60)
            print("🚀 文件监控已启动")
            print("\n📈 监控参数:")
            print(f"   • 内容变化检测: 实时 ({self.content_check_interval}秒间隔)")
            print(f"   • 新文件检测: 每 {self.check_interval//60} 分钟")
            print(f"   • 当前监控: {os.path.basename(self.file_path)}")
            print("\n📝 功能说明:")
            print("   • 监控文件内容变化")
            print("   • 监控文件删除并自动切换")
            print("   • 定期检查更新文件")
            print("\n⏹️  按 Ctrl+C 停止监控")
            print("=" * 60)
            
            check_counter = 0
            while True:
                time.sleep(self.content_check_interval)
                check_counter += 1
                
                # 每10分钟检查一次是否有更新的文件
                if check_counter >= (self.check_interval / self.content_check_interval):
                    self._print_info("定期检查是否有更新文件...")
                    if not self.check_for_newer_files():
                        print("   ✅ 当前文件仍是最新")
                    check_counter = 0
                    
        except KeyboardInterrupt:
            print("\n\n⏹️  停止文件监控...")
            observer.stop()
        
        observer.join()

def find_latest_user_speech_log(log_directory):
    """
    查找指定目录中最新的含有'用户发言记录'的文件
    :param log_directory: 日志文件目录
    :return: 最新文件的完整路径，如果没有找到则返回None
    """
    try:
        # 检查目录是否存在
        if not os.path.exists(log_directory):
            print(f"\n❌ 错误: 目录 {log_directory} 不存在")
            return None
        
        # 搜索含有'用户发言记录'的文件
        pattern = os.path.join(log_directory, "*用户发言记录*.txt")
        matching_files = glob.glob(pattern)
        
        if not matching_files:
            print(f"\n⚠️  在目录 {log_directory} 中没有找到含有'用户发言记录'的文件")
            return None
        
        # 根据创建时间排序，获取最新的文件
        latest_file = max(matching_files, key=os.path.getctime)
        
        # 获取文件信息
        file_size = os.path.getsize(latest_file)
        create_time = datetime.fromtimestamp(os.path.getctime(latest_file))
        modify_time = datetime.fromtimestamp(os.path.getmtime(latest_file))
        
        print(f"\n🔍 找到最新的用户发言记录文件:")
        print(f"   📁 文件名: {os.path.basename(latest_file)}")
        print(f"   💾 文件大小: {file_size:,} 字节")
        print(f"   🕰️  创建时间: {create_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   📝 修改时间: {modify_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return latest_file
        
    except Exception as e:
        print(f"\n❌ 查找文件时出错: {str(e)}")
        return None

def main():
    """主函数"""
    # 设置日志文件目录
    # 实际路径
    actual_log_directory = r"C:\Users\Administrator\AppData\Local\Programs\FlyAiLive1\logs"
    # 测试路径
    test_log_directory = "test_logs"
    
    print("🚀 " + "=" * 50)
    print("📄 文件监控程序 - 智能版")
    print("=" * 54)
    print("\n📊 请选择监控模式:")
    print("   1️⃣  实际模式 - 监控 FlyAiLive1 日志目录")
    print("   2️⃣  测试模式 - 监控本地 test_logs 文件夹")
    
    while True:
        try:
            choice = input("\n➡️  请输入选择 (1/2): ").strip()
            if choice == "1":
                log_directory = actual_log_directory
                print(f"\n✅ 已选择实际模式: {log_directory}")
                break
            elif choice == "2":
                log_directory = test_log_directory
                # 检查测试目录是否存在
                if not os.path.exists(log_directory):
                    print(f"\n⚠️  测试目录 {log_directory} 不存在")
                    create_test = input("🛠️  是否创建测试文件? (y/n): ").strip().lower()
                    if create_test == 'y':
                        try:
                            import subprocess
                            subprocess.run(["python", "create_test_files.py"], check=True)
                            print("\n✅ 测试文件创建成功")
                        except Exception as e:
                            print(f"\n❌ 创建测试文件失败: {e}")
                            continue
                    else:
                        continue
                print(f"\n✅ 已选择测试模式: {log_directory}")
                break
            else:
                print("\n❌ 无效选择，请输入 1 或 2")
        except KeyboardInterrupt:
            print("\n\n⏹️  程序退出")
            return
    
    print("\n" + "-" * 54)
    print("🔍 正在查找最新的'用户发言记录'文件...")
    
    # 查找最新的用户发言记录文件
    file_to_monitor = find_latest_user_speech_log(log_directory)
    
    if file_to_monitor is None:
        print("\n❌ 无法找到适合的文件进行监控，程序退出")
        return
    
    # 创建文件监控器
    monitor = FileMonitor(file_to_monitor)
    
    # 显示当前文件的最后一行内容
    current_last_line = monitor.get_last_line()
    print(f"\n📝 当前最后一行: {current_last_line}")
    
    # 开始监控
    monitor.start_monitoring()

if __name__ == "__main__":
    main()