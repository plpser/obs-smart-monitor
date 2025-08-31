# 📡 OBS源管理器使用指南

## 📋 功能概述

OBS源管理器 (`source_manager.py`) 提供了完整的OBS源信息管理功能，特别针对VLC视频源进行了深度集成。

## 🚀 核心功能

### 1. 📊 场景源信息获取
- 获取所有场景中的源列表
- 读取源的基本属性（类型、启用状态等）
- 获取源的详细设置信息

### 2. 🎥 VLC视频源管理
- **播放列表获取**: 读取VLC源的完整播放列表
- **当前播放项**: 识别当前正在播放的视频文件
- **播放设置**: 获取循环、随机播放等设置
- **媒体信息**: 提取视频文件名和路径信息

### 3. 📈 源状态监控
- 实时监控源的状态变化
- 定期更新源信息缓存
- 检测源的可见性和活跃状态

### 4. 📤 数据导出
- 导出完整的源信息到JSON文件
- 包含场景结构和VLC播放列表详情

## 🛠️ 使用方法

### 基本使用

```python
from obs_manager import OBSManager

# 初始化OBS管理器
manager = OBSManager()

# 连接OBS
if manager.connect():
    # 获取所有场景源信息
    sources_info = manager.get_sources_info()
    
    # 获取VLC源信息
    vlc_sources = manager.get_vlc_sources_info()
    
    # 显示源信息摘要
    manager.print_sources_summary()
    
    # 显示VLC源详情
    manager.print_vlc_sources_detail()
    
    # 断开连接
    manager.disconnect()
```

### VLC源播放列表处理

```python
# 获取VLC源信息
vlc_sources = manager.get_vlc_sources_info()

for source_name, vlc_info in vlc_sources.items():
    print(f"VLC源: {source_name}")
    
    # 当前播放项
    current_item = vlc_info.get('current_item')
    if current_item:
        print(f"当前播放: {current_item['name']}")
        print(f"文件路径: {current_item['path']}")
    
    # 播放列表
    playlist = vlc_info.get('playlist', [])
    print(f"播放列表共 {len(playlist)} 项:")
    
    for item in playlist:
        status = "▶️" if item['selected'] else "⏸️"
        print(f"  {status} {item['index']+1}. {item['name']}")
    
    # 播放设置
    settings = vlc_info.get('settings', {})
    print(f"循环播放: {settings.get('loop')}")
    print(f"随机播放: {settings.get('shuffle')}")
```

### 源状态监控

```python
# 开始源监控
manager.start_source_monitoring()

# 监控会在后台运行，定期更新源信息

# 停止源监控
manager.stop_source_monitoring()
```

## 📊 输出格式示例

### 源信息摘要输出
```
📊 源信息摘要 - 14:30:15
============================================================

🎬 场景: 默认场景
   📝 源数量: 3
   ✅ 网络摄像头 (dshow_input)
   ✅ VLC视频源 (vlc_source)
      🎵 当前播放: 示例视频.mp4
      📋 播放列表: 5 项
   ❌ 音频输入 (wasapi_input_capture)

📈 统计信息:
   📊 总源数: 8
   🎥 VLC源数: 2
   🎬 场景数: 3
```

### VLC源详细输出
```
🎥 VLC源详细信息 - 14:30:15
============================================================

📺 源名称: VLC视频源
   🎯 类型: vlc_source
   ▶️ 当前播放: 宣传片.mp4
   📍 播放索引: 2
   📋 播放列表: 5 项
   🔄 循环播放: ✅
   🔀 随机播放: ❌
   ⚙️ 播放行为: stop_restart
   📑 播放列表详情:
         1. 开场视频.mp4
      ▶️ 2. 宣传片.mp4
         3. 产品介绍.mp4
         4. 用户评价.mp4
         5. 结束画面.mp4
```

## 🎯 VLC源数据结构

### VLC源信息格式
```json
{
  "source_name": "VLC视频源",
  "source_type": "vlc_source",
  "playlist": [
    {
      "index": 0,
      "path": "/path/to/video1.mp4",
      "name": "video1.mp4",
      "selected": false,
      "hidden": false
    },
    {
      "index": 1,
      "path": "/path/to/video2.mp4", 
      "name": "video2.mp4",
      "selected": true,
      "hidden": false
    }
  ],
  "current_item": {
    "index": 1,
    "path": "/path/to/video2.mp4",
    "name": "video2.mp4",
    "selected": true
  },
  "current_index": 1,
  "settings": {
    "loop": true,
    "shuffle": false,
    "playback_behavior": "stop_restart",
    "network_caching": 400
  }
}
```

## 🧪 测试和调试

### 运行测试脚本
```bash
# 运行完整的源管理器测试
python test_source_manager.py

# 选择测试模式
# 1 - 自动测试所有功能
# 2 - 交互模式手动测试
```

### 交互测试命令
- `1` - 获取所有源信息
- `2` - 获取VLC源信息  
- `3` - 显示源摘要
- `4` - 显示VLC详情
- `5` - 开始源监控
- `6` - 停止源监控
- `7` - 导出源信息
- `q` - 退出

## 📁 文件导出

### 导出源信息
```python
# 导出到默认文件
manager.export_sources_info()

# 导出到指定文件
manager.export_sources_info("my_sources_info.json")
```

### 导出文件格式
```json
{
  "timestamp": "2025-08-31T14:30:15",
  "scenes_sources": {
    "场景名": [
      {
        "source_name": "源名称",
        "source_type": "源类型",
        "enabled": true,
        "settings": {}
      }
    ]
  },
  "vlc_sources": {
    "VLC源名": {
      "playlist": [],
      "current_item": {},
      "settings": {}
    }
  },
  "summary": {
    "total_scenes": 3,
    "total_sources": 8,
    "vlc_sources_count": 2
  }
}
```

## 🔧 配置和扩展

### 源监控配置
```python
# 设置监控间隔（默认5秒）
manager.source_manager.monitor_interval = 10

# 开始监控
manager.start_source_monitoring()
```

### 自定义源处理
可以扩展 `SourceManager` 类来支持其他类型的源：

```python
class CustomSourceManager(SourceManager):
    def get_custom_source_info(self, source_name):
        # 自定义源信息获取逻辑
        pass
```

## ⚠️ 注意事项

1. **OBS连接**: 确保OBS Studio已启动并启用WebSocket服务器
2. **VLC源**: 只有VLC视频源才会显示播放列表信息
3. **权限**: 某些源属性可能需要特定权限才能访问
4. **性能**: 源监控会定期查询OBS，注意监控间隔设置
5. **错误处理**: 源信息获取失败是正常的，程序会继续运行

## 🚀 未来功能规划

- 源属性实时变更监听
- 播放进度和时长信息获取
- 源控制操作（播放/暂停/切换）
- 更多源类型的深度集成
- 源性能监控和统计

---

📅 **创建时间**: 2025-08-31  
📝 **版本**: v1.0.0  
👤 **维护者**: OBS智能监控系统开发团队