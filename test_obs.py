"""
OBS WebSocket 连接测试脚本
"""
from obs_manager import OBSManager

def test_obs_connection():
    """测试OBS连接"""
    print("🎬 OBS WebSocket 连接测试")
    print("=" * 50)
    
    # 创建OBS管理器
    manager = OBSManager()
    
    # 尝试连接
    print("🔌 正在连接OBS...")
    if manager.connect():
        print("✅ 连接成功！")
        
        # 获取场景列表
        print("\n📋 获取场景列表...")
        scenes = manager.get_scene_list()
        
        if scenes:
            # 更新配置文件
            print("\n💾 更新配置文件...")
            if manager.update_scene_config():
                print("✅ 配置文件更新成功")
                
                # 显示场景映射
                manager.print_scene_mapping()
                
                # 测试场景切换
                print(f"\n🎯 测试场景切换功能:")
                print("输入场景编号进行测试，输入 0 退出")
                
                while True:
                    try:
                        user_input = input("\n请输入场景编号 (0-退出): ").strip()
                        
                        if user_input == "0":
                            break
                        
                        number = int(user_input)
                        print(f"🔄 尝试切换到场景编号 {number}...")
                        
                        success = manager.switch_scene_by_number(number)
                        if success:
                            print(f"✅ 场景切换成功！")
                            print(f"⏰ 将在120秒后自动返回默认场景")
                        else:
                            print(f"❌ 场景切换失败")
                            
                    except ValueError:
                        print("❌ 请输入有效的数字")
                    except KeyboardInterrupt:
                        print("\n👋 退出测试")
                        break
            else:
                print("❌ 配置文件更新失败")
        else:
            print("❌ 未获取到场景列表")
    else:
        print("❌ 连接失败！")
        print("\n🔧 请检查:")
        print("1. OBS Studio 是否已启动")
        print("2. WebSocket 服务器是否已启用")
        print("3. 连接信息是否正确 (host, port, password)")
    
    # 断开连接
    manager.disconnect()
    print("\n👋 测试完成")

def show_obs_setup_guide():
    """显示OBS设置指南"""
    print("📖 OBS WebSocket 设置指南")
    print("=" * 50)
    print("1. 打开 OBS Studio")
    print("2. 点击 '工具' -> 'WebSocket 服务器设置'")
    print("3. 勾选 '启用 WebSocket 服务器'")
    print("4. 设置端口 (默认: 4455)")
    print("5. 设置密码 (可选，建议留空)")
    print("6. 点击 '确定' 保存设置")
    print("7. 运行此测试脚本验证连接")
    print("\n💡 提示:")
    print("- 如果连接失败，请检查防火墙设置")
    print("- 确保 OBS 版本支持 WebSocket (28.0+)")

if __name__ == "__main__":
    print("🎬 OBS WebSocket 测试工具")
    print("=" * 50)
    
    while True:
        print("\n请选择操作:")
        print("1. 测试 OBS 连接")
        print("2. 查看设置指南")
        print("0. 退出")
        
        try:
            choice = input("\n请输入选择 (0-2): ").strip()
            
            if choice == "1":
                test_obs_connection()
            elif choice == "2":
                show_obs_setup_guide()
            elif choice == "0":
                print("👋 再见！")
                break
            else:
                print("❌ 无效选择，请输入 0-2")
                
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break