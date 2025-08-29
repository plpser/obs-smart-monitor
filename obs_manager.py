import json
import time
import threading
from datetime import datetime, timedelta
try:
    import obsws_python as obs
except ImportError:
    print("⚠️ 需要安装 obsws-python: pip install obsws-python")
    obs = None

class OBSManager:
    """OBS WebSocket管理器"""
    
    def __init__(self, config_path="obs_config.json"):
        """
        初始化OBS管理器
        :param config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config = self.load_config()
        self.ws = None
        self.connected = False
        self.current_scene = None
        self.switch_end_time = None
        self.switch_lock = threading.Lock()
        self.switch_timer = None
        
    def load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ 配置文件不存在: {self.config_path}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ 配置文件格式错误: {e}")
            return None
    
    def reload_config(self):
        """重新加载配置文件"""
        old_config = self.config
        self.config = self.load_config()
        
        if self.config:
            print(f"✅ 配置文件已重新加载")
            return True
        else:
            print(f"❌ 配置文件重新加载失败，恢复旧配置")
            self.config = old_config
            return False
    
    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"❌ 保存配置文件失败: {e}")
            return False
    
    def connect(self):
        """连接到OBS WebSocket"""
        if obs is None:
            print("❌ obsws-python 未安装，无法连接OBS")
            return False
        
        if not self.config:
            print("❌ 配置文件加载失败，无法连接OBS")
            return False
        
        try:
            conn_config = self.config["obs_connection"]
            self.ws = obs.ReqClient(
                host=conn_config["host"],
                port=conn_config["port"],
                password=conn_config["password"],
                timeout=conn_config.get("connect_timeout", 5)
            )
            
            # 测试连接
            version_info = self.ws.get_version()
            self.connected = True
            
            print(f"✅ 成功连接到OBS WebSocket")
            print(f"   📡 OBS版本: {version_info.obs_version}")
            print(f"   🔌 WebSocket版本: {version_info.obs_web_socket_version}")
            
            # 获取当前场景
            current_scene_resp = self.ws.get_current_program_scene()
            self.current_scene = current_scene_resp.current_program_scene_name
            print(f"   🎬 当前场景: {self.current_scene}")
            
            return True
            
        except Exception as e:
            print(f"❌ 连接OBS失败: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """断开OBS连接"""
        if self.ws:
            try:
                self.ws.disconnect()
                self.connected = False
                print("🔌 已断开OBS连接")
            except Exception as e:
                print(f"⚠️ 断开连接时出错: {e}")
    
    def get_scene_list(self):
        """获取所有场景列表"""
        if not self.connected or not self.ws:
            print("❌ OBS未连接")
            return []
        
        try:
            scenes_resp = self.ws.get_scene_list()
            scene_names = [scene['sceneName'] for scene in scenes_resp.scenes]
            print(f"🎬 获取到 {len(scene_names)} 个场景:")
            for i, scene in enumerate(scene_names, 1):
                print(f"   {i}. {scene}")
            return scene_names
        except Exception as e:
            print(f"❌ 获取场景列表失败: {e}")
            return []
    
    def update_scene_config(self):
        """更新场景配置到配置文件"""
        if not self.config:
            print("❌ 配置文件未加载")
            return False
            
        if not self.connected:
            if not self.connect():
                return False
        
        scene_names = self.get_scene_list()
        if not scene_names:
            return False
        
        # 更新配置
        scenes_config = {}
        for i, scene_name in enumerate(scene_names, 1):
            scenes_config[str(i)] = {
                "name": scene_name,
                "number": i,
                "enabled": True,
                "description": f"场景{i}: {scene_name}"
            }
        
        self.config["scene_settings"]["scenes"] = scenes_config
        
        # 设置默认场景（如果不存在或不在列表中）
        default_scene = self.config["scene_settings"]["default_scene"]
        if default_scene not in scene_names:
            if scene_names:
                self.config["scene_settings"]["default_scene"] = scene_names[0]
                print(f"🔄 默认场景已更新为: {scene_names[0]}")
        
        if self.save_config():
            print(f"✅ 场景配置已更新到 {self.config_path}")
            return True
        
        return False
    
    def switch_scene(self, scene_name):
        """切换到指定场景"""
        if not self.connected or not self.ws:
            print("❌ OBS未连接")
            return False
        
        try:
            self.ws.set_current_program_scene(scene_name)
            self.current_scene = scene_name
            print(f"🎬 场景已切换到: {scene_name}")
            return True
        except Exception as e:
            print(f"❌ 切换场景失败: {e}")
            return False
    
    def switch_scene_by_number(self, number):
        """根据数字切换场景"""
        if not self.config:
            print("❌ 配置文件未加载")
            return False
            
        with self.switch_lock:
            # 检查是否在切换冷却期间
            if self.switch_end_time and datetime.now() < self.switch_end_time:
                remaining = (self.switch_end_time - datetime.now()).total_seconds()
                print(f"⏳ 场景切换冷却中，剩余 {remaining:.0f} 秒")
                return False
            
            # 查找对应的场景
            scenes = self.config["scene_settings"]["scenes"]
            target_scene = None
            
            for scene_id, scene_info in scenes.items():
                if scene_info.get("number") == int(number) and scene_info.get("enabled", True):
                    target_scene = scene_info["name"]
                    break
            
            if not target_scene:
                print(f"❌ 未找到编号 {number} 对应的场景")
                return False
            
            # 切换场景
            if self.switch_scene(target_scene):
                # 设置切换时间和定时器
                duration = self.config["scene_settings"]["switch_duration"]
                self.switch_end_time = datetime.now() + timedelta(seconds=duration)
                
                print(f"⏰ 场景切换成功，{duration}秒后自动回到默认场景")
                
                # 取消之前的定时器
                if self.switch_timer:
                    self.switch_timer.cancel()
                
                # 设置新的定时器
                self.switch_timer = threading.Timer(duration, self._return_to_default)
                self.switch_timer.start()
                
                return True
            
            return False
    
    def _return_to_default(self):
        """返回默认场景"""
        if not self.config:
            return
            
        default_scene = self.config["scene_settings"]["default_scene"]
        if default_scene and self.switch_scene(default_scene):
            print(f"🏠 已自动返回默认场景: {default_scene}")
        
        with self.switch_lock:
            self.switch_end_time = None
    
    def is_in_cooldown(self):
        """检查是否在冷却期"""
        if self.switch_end_time:
            return datetime.now() < self.switch_end_time
        return False
    
    def get_cooldown_remaining(self):
        """获取剩余冷却时间"""
        if self.is_in_cooldown() and self.switch_end_time:
            return (self.switch_end_time - datetime.now()).total_seconds()
        return 0
    
    def print_scene_mapping(self):
        """打印场景映射信息"""
        if not self.config:
            print("❌ 配置文件未加载")
            return
            
        scenes = self.config["scene_settings"]["scenes"]
        if not scenes:
            print("❌ 没有配置的场景")
            return
        
        print("\n🎬 场景映射表:")
        print("   编号 | 场景名称 | 状态")
        print("   ----|---------|----")
        for scene_id, scene_info in scenes.items():
            status = "✅启用" if scene_info.get("enabled", True) else "❌禁用"
            print(f"   {scene_info['number']:^4} | {scene_info['name']:<15} | {status}")
        
        default_scene = self.config["scene_settings"]["default_scene"]
        duration = self.config["scene_settings"]["switch_duration"]
        print(f"\n🏠 默认场景: {default_scene}")
        print(f"⏰ 切换保持时间: {duration}秒")
    
    def __del__(self):
        """析构函数，确保断开连接"""
        if self.switch_timer:
            self.switch_timer.cancel()
        self.disconnect()

def main():
    """测试OBS管理器"""
    print("🎬 OBS WebSocket管理器测试")
    print("=" * 50)
    
    manager = OBSManager()
    
    # 连接OBS
    if manager.connect():
        # 更新场景配置
        manager.update_scene_config()
        
        # 显示场景映射
        manager.print_scene_mapping()
        
        # 测试场景切换
        print(f"\n📝 测试功能（输入场景编号进行切换，输入0退出）:")
        while True:
            try:
                user_input = input("请输入场景编号: ").strip()
                if user_input == "0":
                    break
                
                number = int(user_input)
                manager.switch_scene_by_number(number)
                
            except ValueError:
                print("❌ 请输入有效的数字")
            except KeyboardInterrupt:
                break
    
    # 断开连接
    manager.disconnect()
    print("\n👋 测试完成")

if __name__ == "__main__":
    main()