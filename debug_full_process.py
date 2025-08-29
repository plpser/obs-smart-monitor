"""
完整流程调试脚本
"""
import json
from obs_manager import OBSManager

def test_full_process():
    """测试完整的检测和切换流程"""
    print("🔧 完整流程调试")
    print("=" * 50)
    
    # 1. 检查配置文件
    print("\n📄 1. 检查配置文件...")
    try:
        with open("obs_config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("✅ 配置文件加载成功")
        print(f"   🌐 OBS地址: {config['obs_connection']['host']}:{config['obs_connection']['port']}")
        print(f"   🔑 密码: {'已设置' if config['obs_connection']['password'] else '未设置'}")
        print(f"   🏠 默认场景: {config['scene_settings']['default_scene']}")
        print(f"   ⏰ 切换时长: {config['scene_settings']['switch_duration']}秒")
        
        # 检查场景10是否存在
        scenes = config['scene_settings']['scenes']
        if '10' in scenes:
            scene_10 = scenes['10']
            print(f"   🎬 场景10: {scene_10['name']} (启用: {scene_10['enabled']})")
        else:
            print("   ❌ 场景10不存在")
            
    except Exception as e:
        print(f"❌ 配置文件错误: {e}")
        return
    
    # 2. 测试OBS连接
    print("\n🔌 2. 测试OBS连接...")
    obs_manager = OBSManager()
    
    if obs_manager.connect():
        print("✅ OBS连接成功")
        print(f"   📺 当前场景: {obs_manager.current_scene}")
        
        # 3. 测试数字检测
        print("\n🔍 3. 测试数字检测...")
        test_content = "看看10的啊"
        
        # 模拟内容提取过程
        def _extract_number_with_kan(content):
            import re
            if not content or not content.strip():
                return None
            if "看" not in content:
                return None
            number_pattern = r'\d+(?:\.\d+)?'
            numbers = re.findall(number_pattern, content)
            if numbers:
                return numbers[0]
            return None
        
        extracted_number = _extract_number_with_kan(test_content)
        print(f"   📝 测试内容: '{test_content}'")
        print(f"   🔢 检测结果: {extracted_number}")
        
        if extracted_number:
            # 4. 测试场景切换
            print(f"\n🎬 4. 测试场景切换到编号 {extracted_number}...")
            
            # 检查是否在冷却期
            if obs_manager.is_in_cooldown():
                remaining = obs_manager.get_cooldown_remaining()
                print(f"   ⏳ 当前在冷却期，剩余 {remaining:.0f} 秒")
            else:
                print("   ✅ 不在冷却期，可以切换")
                
                # 尝试切换
                success = obs_manager.switch_scene_by_number(extracted_number)
                if success:
                    print(f"   🎉 场景切换成功到编号 {extracted_number}")
                else:
                    print(f"   ❌ 场景切换失败")
        else:
            print("   ❌ 数字检测失败，无法切换")
            
    else:
        print("❌ OBS连接失败")
        print("   请检查:")
        print("   1. OBS Studio是否已启动")
        print("   2. WebSocket服务器是否已启用")
        print("   3. 连接地址和端口是否正确")
        print("   4. 密码是否正确")
    
    # 断开连接
    obs_manager.disconnect()
    print("\n👋 调试完成")

if __name__ == "__main__":
    test_full_process()