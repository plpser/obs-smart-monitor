"""
智能文件监控 + OBS自动化系统启动脚本
"""
import os
import sys
import subprocess

def check_dependencies():
    """检查依赖是否已安装"""
    try:
        import watchdog
        import obsws_python
        return True
    except ImportError:
        return False

def install_dependencies():
    """安装依赖包"""
    print("📦 正在安装依赖包...")
    try:
        subprocess.run([sys.executable, "install_dependencies.py"], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def show_welcome():
    """显示欢迎界面"""
    print("🎬" + "=" * 60)
    print("    智能文件监控 + OBS自动化系统")
    print("    Intelligent File Monitor + OBS Automation")
    print("=" * 63)
    print("\n✨ 系统功能:")
    print("   🔍 实时监控用户发言文件")
    print("   🧠 智能提取用户发言内容")
    print("   🔢 自动检测“看”字和数字组合")
    print("   🎬 基于数字自动切换OBS场景")
    print("   ⏰ 120秒后自动返回默认场景")
    print("   🛡️ 冷却期间拒绝新的切换请求")

def main():
    """主启动函数"""
    show_welcome()
    
    # 检查依赖
    print("\n🔧 系统检查...")
    if not check_dependencies():
        print("❌ 缺少必要的依赖包")
        if input("是否现在安装? (y/n): ").lower().startswith('y'):
            if install_dependencies():
                print("✅ 依赖安装完成")
            else:
                print("❌ 依赖安装失败，请手动运行: python install_dependencies.py")
                return
        else:
            print("请先安装依赖后再运行系统")
            return
    else:
        print("✅ 所有依赖都已安装")
    
    # 检查配置文件
    print("\n📄 配置文件检查...")
    if not os.path.exists("obs_config.json"):
        print("⚠️ OBS配置文件不存在，将在首次连接时自动创建")
    else:
        print("✅ OBS配置文件存在")
    
    # 显示使用提示
    print("\n📖 使用提示:")
    print("1. 确保 OBS Studio 已启动并启用 WebSocket 服务器")
    print("2. 程序将自动检测用户发言中的“看X”模式")
    print("3. 检测到数字后自动切换到对应编号的OBS场景")
    print("4. 120秒后自动返回默认场景")
    print("5. 按 Ctrl+C 可以随时退出程序")
    
    # 启动主程序
    print(f"\n🚀 启动主程序...")
    print("=" * 63)
    
    try:
        subprocess.run([sys.executable, "fileMonitor.py"])
    except KeyboardInterrupt:
        print("\n👋 程序已退出")
    except Exception as e:
        print(f"\n❌ 程序运行出错: {e}")

if __name__ == "__main__":
    main()