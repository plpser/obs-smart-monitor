import os
import time
import glob
import signal
import sys
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from obs_manager import OBSManager

class FileMonitor(FileSystemEventHandler):
    """文件监控类，监控指定文件的变化"""
    
    def __init__(self, file_path, obs_manager=None):
        """
        初始化文件监控器
        :param file_path: 要监控的文件路径
        :param obs_manager: OBS管理器实例
        """
        self.file_path = os.path.abspath(file_path)
        self.file_dir = os.path.dirname(self.file_path)
        self.file_name = os.path.basename(self.file_path)
        self.last_modified_time = 0
        self.check_interval = 600  # 10分钟 = 600秒
        self.content_check_interval = 0.5  # 0.5秒
        self.obs_manager = obs_manager
        
        # 检查文件是否存在
        if not os.path.exists(self.file_path):
            self._print_warning(f"文件 {self.file_path} 不存在")
        else:
            self.last_modified_time = os.path.getmtime(self.file_path)
            self._print_info(f"开始监控文件: {os.path.basename(self.file_path)}")
    
    def _print_info(self, message):
        """打印信息消息"""
        timestamp = time.strftime('%H:%M:%S')
        print(f"\n🗓️ [{timestamp}] {message}")
    
    def _print_success(self, message):
        """打印成功消息"""
        timestamp = time.strftime('%H:%M:%S')
        print(f"\n✅ [{timestamp}] {message}")
    
    def _print_warning(self, message):
        """打印警告消息"""
        timestamp = time.strftime('%H:%M:%S')
        print(f"\n⚠️ [{timestamp}] {message}")
    
    def _print_error(self, message):
        """打印错误消息"""
        timestamp = time.strftime('%H:%M:%S')
        print(f"\n❌ [{timestamp}] {message}")
    
    def _print_obs_status(self, message, status_type="info"):
        """打印OBS相关状态信息"""
        timestamp = time.strftime('%H:%M:%S')
        if status_type == "success":
            print(f"\n🎬 [{timestamp}] {message}")
        elif status_type == "warning":
            print(f"\n⚠️ [{timestamp}] OBS: {message}")
        elif status_type == "error":
            print(f"\n❌ [{timestamp}] OBS: {message}")
        else:
            print(f"\n🎥 [{timestamp}] OBS: {message}")
    
    def _extract_user_speech(self, line):
        """
        提取用户发言内容，去除时间戳和用户标识等前缀
        支持多种格式：
        - 2025-08-29 22:53:09[用户发言]t： 有黄水吗
        - [用户发言]用户名： 内容
        - 时间 用户名： 内容
        """
        if not line or not line.strip():
            return "空内容"
        
        original_line = line.strip()
        
        # 匹配模式1: 2025-08-29 22:53:09[用户发言]t： 有黄水吗
        import re
        pattern1 = r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\[用户发言\][^：]*：\s*(.*)'
        match1 = re.match(pattern1, original_line)
        if match1:
            content = match1.group(1).strip()
            return content if content else "空内容"
        
        # 匹配模式2: [用户发言]用户名： 内容
        pattern2 = r'\[用户发言\][^：]*：\s*(.*)'
        match2 = re.match(pattern2, original_line)
        if match2:
            content = match2.group(1).strip()
            return content if content else "空内容"
        
        # 匹配模式3: 时间戳 用户名： 内容
        pattern3 = r'\d{2}:\d{2}:\d{2}\s+[^：]*：\s*(.*)'
        match3 = re.match(pattern3, original_line)
        if match3:
            content = match3.group(1).strip()
            return content if content else "空内容"
        
        # 如果没有匹配到任何模式，返回原始内容
        return original_line
    
    def _extract_number_with_kan(self, content):
        """
        检测用户发言内容中是否同时包含"看"字和数字
        支持两种规则：
        1. 包含"看"字和"108"字符，且还有其他数字：返回其他数字+108
        2. 包含"看"字和数字（普通情况）：返回提取到的数字
        
        :param content: 用户发言的纯净内容
        :return: 提取到的数字字符串或None
        """
        import re
        
        if not content or not content.strip():
            return None
        
        # 检查是否包含"看"字
        if "看" not in content:
            return None
        
        # 规则1: 检查是否包含"看"字和"108"字符
        if "108" in content:
            # 提取所有数字（包括整数和小数）
            number_pattern = r'\d+(?:\.\d+)?'
            numbers = re.findall(number_pattern, content)
            
            # 过滤掉"108"，查找其他数字
            other_numbers = [num for num in numbers if num != "108"]
            
            if other_numbers:
                # 返回第一个其他数字+108
                try:
                    base_number = float(other_numbers[0])
                    result = base_number + 108
                    # 如果结果是整数，返回整数字符串
                    if result.is_integer():
                        return str(int(result))
                    else:
                        return str(result)
                except ValueError:
                    return None
            else:
                # 只有108，没有其他数字
                return None
        
        # 规则2: 普通情况，提取所有数字（包括整数和小数）
        number_pattern = r'\d+(?:\.\d+)?'
        numbers = re.findall(number_pattern, content)
        
        if numbers:
            # 如果有多个数字，返回第一个
            return numbers[0]
        
        return None
    
    def _print_content_change(self, content):
        """打印文件内容变化"""
        timestamp = time.strftime('%H:%M:%S')
        
        # 提取纯净的用户发言内容
        clean_content = self._extract_user_speech(content)
        
        # 检测是否包含"看"字和数字
        extracted_number = self._extract_number_with_kan(clean_content)
        
        print(f"\n📄 [{timestamp}] 文件内容变化")
        print(f"   📁 文件: {os.path.basename(self.file_path)}")
        print(f"   📝 原始内容: {content}")
        print(f"   ✨ 用户发言: {clean_content}")
        
        # 显示数字检测结果
        if extracted_number is not None:
            print(f"   🔢 检测结果: 发现“看”字和数字 -> {extracted_number}")
            
            # OBS场景自动切换
            if self.obs_manager and self.obs_manager.connected:
                if self.obs_manager.is_in_cooldown():
                    remaining = self.obs_manager.get_cooldown_remaining()
                    self._print_obs_status(f"场景切换冷却中，剩余 {remaining:.0f} 秒", "warning")
                else:
                    success = self.obs_manager.switch_scene_by_number(extracted_number)
                    if success:
                        # 检查是否有延迟设置
                        delay = self.obs_manager.config["scene_settings"].get("switch_delay", 5)
                        if delay > 0:
                            self._print_obs_status(f"场景切换命令已发出，{delay}秒后执行", "info")
                        else:
                            self._print_obs_status(f"场景已切换到编号 {extracted_number}", "success")
                    else:
                        self._print_obs_status(f"无法切换到编号 {extracted_number} 的场景", "error")
            elif self.obs_manager and not self.obs_manager.connected:
                self._print_obs_status("未连接到OBS，无法自动切换场景", "warning")
        else:
            print(f"   ❌ 检测结果: 未检测到“看”字和数字的组合")
        
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
                clean_content = self._extract_user_speech(last_line)
                extracted_number = self._extract_number_with_kan(clean_content)
                print(f"   📝 新文件原始内容: {last_line}")
                print(f"   ✨ 新文件用户发言: {clean_content}")
                if extracted_number is not None:
                    print(f"   🔢 检测结果: 发现“看”字和数字 -> {extracted_number}")
                else:
                    print(f"   ❌ 检测结果: 未检测到“看”字和数字的组合")
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
                    clean_content = self._extract_user_speech(last_line)
                    extracted_number = self._extract_number_with_kan(clean_content)
                    print(f"   📝 新文件原始内容: {last_line}")
                    print(f"   ✨ 新文件用户发言: {clean_content}")
                    if extracted_number is not None:
                        print(f"   🔢 检测结果: 发现“看”字和数字 -> {extracted_number}")
                    else:
                        print(f"   ❌ 检测结果: 未检测到“看”字和数字的组合")
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
            print("   • 提取纯净用户发言内容")
            print("   • 检测“看”字和数字组合")
            print("   • 监控文件删除并自动切换")
            print("   • 定期检查更新文件")
            print("\n⏹️ 按 Ctrl+C 停止监控")
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
            print("\n\n⏹️ 停止文件监控...")
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
            print(f"\n⚠️ 在目录 {log_directory} 中没有找到含有'用户发言记录'的文件")
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
        print(f"   🕰️ 创建时间: {create_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   📝 修改时间: {modify_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return latest_file
        
    except Exception as e:
        print(f"\n❌ 查找文件时出错: {str(e)}")
        return None

def timeout_input(prompt, timeout, default_value):
    """
    带超时的输入函数
    :param prompt: 提示信息
    :param timeout: 超时时间(秒)
    :param default_value: 默认值
    :return: 用户输入或默认值
    """
    def timeout_handler(signum, frame):
        raise TimeoutError()
    
    try:
        # 设置信号处理器
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)
        
        try:
            result = input(prompt).strip()
            signal.alarm(0)  # 取消闹钟
            return result
        except TimeoutError:
            print(f"\n⏰ 超时，使用默认选择: {default_value}")
            return default_value
        finally:
            signal.signal(signal.SIGALRM, old_handler)
    except AttributeError:
        # Windows系统不支持signal.SIGALRM，使用替代方案
        import threading
        import time
        
        result = [None]  # type: list[str | None]
        
        def get_input():
            try:
                result[0] = input(prompt).strip()
            except EOFError:
                pass
        
        input_thread = threading.Thread(target=get_input)
        input_thread.daemon = True
        input_thread.start()
        input_thread.join(timeout)
        
        if result[0] is None:
            print(f"\n⏰ 超时，使用默认选择: {default_value}")
            return default_value
        else:
            return result[0]

def main():
    """主函数"""
    # 设置日志文件目录
    # 实际路径
    actual_log_directory = r"C:\Users\Administrator\AppData\Local\Programs\FlyAiLive1\logs"
    # 测试路径
    test_log_directory = "test_logs"
    
    print("🚀 " + "=" * 50)
    print("📄 文件监控程序 - 智能版 + OBS自动化")
    print("=" * 54)
    
    # 初始化OBS管理器
    print("\n🎥 初始化OBS管理器...")
    obs_manager = OBSManager()
    
    # 询问是否启用OBS功能
    while True:
        try:
            obs_choice = timeout_input("🎬 是否启用OBS自动场景切换功能? (y/n) [默认y, 10秒]: ", 10, "y")
            if obs_choice.lower() in ['y', 'yes', '是', '']:
                if obs_manager.connect():
                    # 更新场景配置
                    obs_manager.update_scene_config()
                    obs_manager.print_scene_mapping()
                    print("✅ OBS功能已启用")
                else:
                    print("⚠️ OBS连接失败，将禁用自动切换功能")
                    obs_manager = None
                break
            elif obs_choice.lower() in ['n', 'no', '否']:
                print("❌ OBS功能已禁用")
                obs_manager = None
                break
            else:
                print("❌ 请输入 y 或 n")
        except KeyboardInterrupt:
            print("\n\n⏹️ 程序退出")
            return
    
    print("\n📊 请选择监控模式:")
    print("   1️⃣ 实际模式 - 监控 FlyAiLive1 日志目录")
    print("   2️⃣ 测试模式 - 监控本地 test_logs 文件夹")
    
    while True:
        try:
            choice = timeout_input("\n➡️ 请输入选择 (1/2) [默认1, 3秒]: ", 3, "1")
            if choice == "1":
                log_directory = actual_log_directory
                print(f"\n✅ 已选择实际模式: {log_directory}")
                break
            elif choice == "2":
                log_directory = test_log_directory
                # 检查测试目录是否存在
                if not os.path.exists(log_directory):
                    print(f"\n⚠️ 测试目录 {log_directory} 不存在")
                    create_test = timeout_input("🛠️ 是否创建测试文件? (y/n): ", 5, "n")
                    if create_test.lower().startswith('y'):
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
            print("\n\n⏹️ 程序退出")
            if obs_manager:
                obs_manager.disconnect()
            return
    
    print("\n" + "-" * 54)
    print("🔍 正在查找最新的'用户发言记录'文件...")
    
    # 查找最新的用户发言记录文件
    file_to_monitor = find_latest_user_speech_log(log_directory)
    
    if file_to_monitor is None:
        print("\n❌ 无法找到适合的文件进行监控，程序退出")
        if obs_manager:
            obs_manager.disconnect()
        return
    
    # 创建文件监控器（传入OBS管理器）
    monitor = FileMonitor(file_to_monitor, obs_manager)
    
    # 显示当前文件的最后一行内容
    current_last_line = monitor.get_last_line()
    clean_content = monitor._extract_user_speech(current_last_line)
    extracted_number = monitor._extract_number_with_kan(clean_content)
    
    print(f"\n📝 当前最后一行:")
    print(f"   📝 原始内容: {current_last_line}")
    print(f"   ✨ 用户发言: {clean_content}")
    
    # 显示数字检测结果
    if extracted_number is not None:
        print(f"   🔢 检测结果: 发现“看”字和数字 -> {extracted_number}")
    else:
        print(f"   ❌ 检测结果: 未检测到“看”字和数字的组合")
    
    # 开始监控
    try:
        monitor.start_monitoring()
    finally:
        # 确保断开OBS连接
        if obs_manager:
            obs_manager.disconnect()

if __name__ == "__main__":
    main()
