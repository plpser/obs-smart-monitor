"""
OBS WebSocket 依赖安装脚本
"""
import subprocess
import sys

def install_dependencies():
    """安装必要的依赖包"""
    dependencies = [
        "watchdog",      # 文件监控
        "obsws-python",  # OBS WebSocket客户端
        "schedule",      # 定时任务调度器
    ]
    
    print("🔧 开始安装依赖包...")
    
    for package in dependencies:
        try:
            print(f"📦 正在安装 {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} 安装成功")
        except subprocess.CalledProcessError as e:
            print(f"❌ {package} 安装失败: {e}")
            return False
    
    print("\n🎉 所有依赖包安装完成！")
    return True

def check_dependencies():
    """检查依赖是否已安装"""
    print("🔍 检查依赖包...")
    
    try:
        import watchdog
        print("✅ watchdog 已安装")
    except ImportError:
        print("❌ watchdog 未安装")
        return False
    
    try:
        import obsws_python
        print("✅ obsws-python 已安装")
    except ImportError:
        print("❌ obsws-python 未安装")
        return False
    
    try:
        import schedule
        print("✅ schedule 已安装")
    except ImportError:
        print("❌ schedule 未安装")
        return False
    
    print("🎉 所有依赖包都已正确安装！")
    return True

if __name__ == "__main__":
    print("🚀 OBS文件监控系统依赖管理")
    print("=" * 40)
    
    if check_dependencies():
        print("\n✅ 系统已准备就绪，可以运行主程序！")
    else:
        print("\n📥 开始安装缺失的依赖...")
        if install_dependencies():
            print("\n✅ 依赖安装完成，可以运行主程序！")
        else:
            print("\n❌ 依赖安装失败，请手动安装")
    
    print("\n📖 使用说明:")
    print("1. 确保 OBS Studio 已安装并启动")
    print("2. 在 OBS 中启用 WebSocket 服务器")
    print("3. 运行: python fileMonitor.py")