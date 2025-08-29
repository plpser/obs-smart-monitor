# 📁 项目文件结构

```
obs/
├── 📄 README.md                    # 项目说明文档
├── 🚀 start.py                     # 启动脚本（推荐使用）
├── 🖥️ fileMonitor.py               # 主程序文件
├── 🎬 obs_manager.py               # OBS WebSocket管理器
├── ⚙️ obs_config.json              # OBS配置文件（自动生成）
├── 📦 install_dependencies.py      # 依赖安装脚本
├── 🗜️ build_exe.py                 # 自动化打包脚本
├── 📜 FileMonitor.spec             # PyInstaller配置文件
├── 📃 BUILD.md                     # 打包说明文档
├── 📋 project_structure.md         # 项目结构说明（本文件）
├── 😫 .gitignore                   # Git忽略文件
└── 📁 .git/                        # Git版本控制目录
```

## 🎯 文件功能说明

### 核心文件
- **start.py**: 推荐的启动方式，包含依赖检查和友好界面
- **fileMonitor.py**: 主程序，实现文件监控和OBS自动化
- **obs_manager.py**: OBS WebSocket管理，处理场景切换逻辑

### 配置文件
- **obs_config.json**: 存储OBS连接信息和场景映射表

### 工具文件
- **install_dependencies.py**: 自动安装所需依赖包
- **build_exe.py**: 自动化打包脚本，生成可执行文件
- **FileMonitor.spec**: PyInstaller配置文件，优化打包过程

### 文档
- **README.md**: 项目详细说明文档
- **BUILD.md**: 打包和分发说明文档
- **project_structure.md**: 本文件，项目结构说明

## 🚀 快速开始

1. **启动程序**：`python start.py`
2. **安装依赖**：`python install_dependencies.py`
3. **打包程序**：`python build_exe.py`

### 超时默认选择
- OBS功能选择：10秒后默认选择 'y'（启用）
- 监控模式选择：3秒后默认选择 '1'（实际模式）