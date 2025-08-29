"""
智能文件监控程序 + OBS自动化 - 自动打包脚本
自动化打包成Windows可执行文件(.exe)
"""

import os
import subprocess
import sys
import shutil
from datetime import datetime

def print_status(message, status_type="info"):
    """打印状态信息"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    if status_type == "success":
        print(f"✅ [{timestamp}] {message}")
    elif status_type == "warning":
        print(f"⚠️ [{timestamp}] {message}")
    elif status_type == "error":
        print(f"❌ [{timestamp}] {message}")
    else:
        print(f"📦 [{timestamp}] {message}")

def check_dependencies():
    """检查必要的依赖"""
    print_status("检查打包依赖...")
    
    try:
        import PyInstaller
        print_status(f"PyInstaller 版本: {PyInstaller.__version__}", "success")
    except ImportError:
        print_status("PyInstaller 未安装", "error")
        print_status("正在安装 PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print_status("PyInstaller 安装成功", "success")
    
    # 检查项目依赖
    required_modules = ['watchdog', 'obsws_python']
    for module in required_modules:
        try:
            __import__(module.replace('-', '_'))
            print_status(f"✓ {module} 已安装", "success")
        except ImportError:
            print_status(f"依赖 {module} 未安装", "warning")
            print_status("请先运行: python install_dependencies.py")
            return False
    
    return True

def clean_build_files():
    """清理之前的构建文件"""
    print_status("清理之前的构建文件...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.pyc', '*.pyo']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print_status(f"删除目录: {dir_name}")
    
    # 清理 .pyc 文件
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith(('.pyc', '.pyo')):
                os.remove(os.path.join(root, file))

def build_executable():
    """构建可执行文件"""
    print_status("开始构建可执行文件...")
    
    # 使用 .spec 文件构建
    if os.path.exists('FileMonitor.spec'):
        cmd = ['pyinstaller', '--clean', 'FileMonitor.spec']
        print_status(f"执行命令: {' '.join(cmd)}")
    else:
        # 如果没有 .spec 文件，使用基本命令
        cmd = [
            'pyinstaller',
            '--onefile',
            '--console',
            '--name=智能文件监控程序',
            '--hidden-import=watchdog',
            '--hidden-import=obsws_python',
            '--add-data=obs_config.json;.',
            'fileMonitor.py'
        ]
        print_status(f"执行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print_status("构建成功!", "success")
        return True
    except subprocess.CalledProcessError as e:
        print_status(f"构建失败: {e}", "error")
        if e.stdout:
            print("标准输出:")
            print(e.stdout)
        if e.stderr:
            print("错误输出:")
            print(e.stderr)
        return False

def copy_required_files():
    """复制必要的配置文件到输出目录"""
    print_status("复制配置文件...")
    
    if not os.path.exists('dist'):
        print_status("dist 目录不存在", "error")
        return False
    
    files_to_copy = [
        'obs_config.json',
        'README.md',
        'install_dependencies.py'
    ]
    
    for file_name in files_to_copy:
        if os.path.exists(file_name):
            shutil.copy2(file_name, 'dist/')
            print_status(f"复制文件: {file_name}")
    
    return True

def create_distribution_package():
    """创建发布包"""
    print_status("创建发布包...")
    
    # 创建发布目录
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    release_dir = f"FileMonitor_Release_{timestamp}"
    
    if os.path.exists(release_dir):
        shutil.rmtree(release_dir)
    
    os.makedirs(release_dir)
    
    # 复制可执行文件
    exe_file = None
    if os.path.exists('dist'):
        for file in os.listdir('dist'):
            if file.endswith('.exe'):
                exe_file = file
                shutil.copy2(os.path.join('dist', file), release_dir)
                print_status(f"复制可执行文件: {file}")
                break
    
    if not exe_file:
        print_status("未找到可执行文件", "error")
        return False
    
    # 复制配置文件
    config_files = ['obs_config.json', 'README.md']
    for file_name in config_files:
        if os.path.exists(file_name):
            shutil.copy2(file_name, release_dir)
        elif os.path.exists(os.path.join('dist', file_name)):
            shutil.copy2(os.path.join('dist', file_name), release_dir)
    
    # 创建使用说明
    usage_text = f"""
智能文件监控程序 + OBS自动化 - 使用说明

📦 发布包内容:
- {exe_file} - 主程序 (双击运行)
- obs_config.json - OBS配置文件
- README.md - 详细说明文档

🚀 使用方法:
1. 确保OBS Studio已启动并开启WebSocket服务器
2. 双击运行 {exe_file}
3. 按提示选择配置选项
4. 程序将自动监控文件并提供OBS自动化功能

⚠️ 注意事项:
- 首次运行可能需要管理员权限
- 确保OBS WebSocket配置正确
- 建议将整个文件夹放置在合适的位置

🔧 故障排除:
- 如果程序无法启动，请检查系统环境
- 如果OBS连接失败，请检查WebSocket设置
- 详细说明请参阅 README.md

📅 构建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    with open(os.path.join(release_dir, '使用说明.txt'), 'w', encoding='utf-8') as f:
        f.write(usage_text)
    
    print_status(f"发布包创建完成: {release_dir}", "success")
    
    # 创建压缩包
    try:
        import zipfile
        zip_name = f"{release_dir}.zip"
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(release_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_name = os.path.relpath(file_path, os.path.dirname(release_dir))
                    zipf.write(file_path, arc_name)
        print_status(f"压缩包创建完成: {zip_name}", "success")
    except Exception as e:
        print_status(f"创建压缩包失败: {e}", "warning")
    
    return release_dir

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 智能文件监控程序 + OBS自动化 - 自动打包工具")
    print("=" * 60)
    
    # 检查依赖
    if not check_dependencies():
        print_status("依赖检查失败，请先安装必要的依赖", "error")
        return
    
    # 清理构建文件
    clean_build_files()
    
    # 构建可执行文件
    if not build_executable():
        print_status("构建失败", "error")
        return
    
    # 复制必要文件
    copy_required_files()
    
    # 创建发布包
    release_dir = create_distribution_package()
    
    if release_dir:
        print("\n" + "=" * 60)
        print_status("打包完成！", "success")
        print(f"📂 发布包位置: {os.path.abspath(release_dir)}")
        print("💡 您可以将发布包分发给其他用户使用")
        print("=" * 60)
    
    # 询问是否清理临时文件
    try:
        choice = input("\n🗑️ 是否清理临时构建文件? (y/n) [默认: y]: ").strip().lower()
        if choice in ['', 'y', 'yes']:
            clean_build_files()
            print_status("临时文件已清理", "success")
    except KeyboardInterrupt:
        print("\n👋 打包完成")

if __name__ == "__main__":
    main()