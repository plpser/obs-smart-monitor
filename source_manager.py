"""
OBS源信息管理模块
功能：
1. 获取所有场景的源信息
2. 读取VLC视频源的播放列表
3. 获取当前视频源的详细信息
4. 监控源状态变化
"""

import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any

try:
    import obsws_python as obs
except ImportError:
    print("⚠️ 需要安装 obsws-python: pip install obsws-python")
    obs = None

class SourceManager:
    """OBS源信息管理器"""
    
    def __init__(self, obs_client=None):
        """
        初始化源管理器
        :param obs_client: OBS WebSocket客户端实例
        """
        self.obs_client = obs_client
        self.sources_cache = {}  # 源信息缓存
        self.vlc_sources = {}   # VLC源信息缓存
        self.source_monitor_active = False
        self.monitor_thread = None
        self.monitor_interval = 5  # 监控间隔（秒）
        
    def set_obs_client(self, obs_client):
        """设置OBS客户端"""
        self.obs_client = obs_client
        
    def get_all_scenes_sources(self) -> Dict[str, List[Dict]]:
        """
        获取所有场景的源信息
        :return: 场景名称 -> 源列表的字典
        """
        if not self.obs_client:
            print("❌ OBS客户端未连接")
            return {}
        
        try:
            # 获取所有场景
            scenes_resp = self.obs_client.get_scene_list()
            scenes_sources = {}
            
            for scene in scenes_resp.scenes:
                scene_name = scene['sceneName']
                
                # 获取场景中的源
                scene_items_resp = self.obs_client.get_scene_item_list(scene_name)
                sources = []
                
                for item in scene_items_resp.scene_items:
                    source_info = {
                        'item_id': item.get('sceneItemId'),
                        'source_name': item.get('sourceName'),
                        'source_type': None,
                        'source_kind': None,
                        'enabled': item.get('sceneItemEnabled', True),
                        'visible': True,
                        'settings': {},
                        'properties': {}
                    }
                    
                    # 获取源的详细信息
                    try:
                        source_resp = self.obs_client.get_input_settings(item.get('sourceName'))
                        source_info['source_type'] = source_resp.input_kind
                        source_info['settings'] = source_resp.input_settings or {}
                    except Exception as e:
                        print(f"⚠️ 获取源 {item.get('sourceName')} 设置失败: {e}")
                    
                    # 获取源属性
                    try:
                        props_resp = self.obs_client.get_input_properties_list_property_items(
                            item.get('sourceName'), 'playlist'
                        )
                        source_info['properties'] = props_resp.__dict__ if hasattr(props_resp, '__dict__') else {}
                    except Exception as e:
                        # 不是所有源都有playlist属性，这是正常的
                        pass
                    
                    sources.append(source_info)
                
                scenes_sources[scene_name] = sources
                
            self.sources_cache = scenes_sources
            return scenes_sources
            
        except Exception as e:
            print(f"❌ 获取场景源信息失败: {e}")
            return {}
    
    def get_vlc_sources_info(self) -> Dict[str, Dict]:
        """
        获取所有VLC视频源的详细信息
        :return: VLC源信息字典
        """
        if not self.obs_client:
            print("❌ OBS客户端未连接")
            return {}
        
        vlc_sources = {}
        
        try:
            # 获取所有输入源
            inputs_resp = self.obs_client.get_input_list()
            
            for input_item in inputs_resp.inputs:
                input_name = input_item.get('inputName')
                input_kind = input_item.get('inputKind')
                
                # 检查是否为VLC视频源
                if input_kind and 'vlc' in input_kind.lower():
                    vlc_info = self._get_vlc_source_details(input_name)
                    if vlc_info:
                        vlc_sources[input_name] = vlc_info
                        
        except Exception as e:
            print(f"❌ 获取VLC源信息失败: {e}")
        
        self.vlc_sources = vlc_sources
        return vlc_sources
    
    def _get_vlc_source_details(self, source_name: str) -> Optional[Dict]:
        """
        获取VLC源的详细信息
        :param source_name: 源名称
        :return: VLC源详细信息
        """
        try:
            # 获取VLC源设置
            settings_resp = self.obs_client.get_input_settings(source_name)
            settings = settings_resp.input_settings or {}
            
            vlc_info = {
                'source_name': source_name,
                'source_type': settings_resp.input_kind,
                'settings': settings,
                'playlist': [],
                'current_item': None,
                'current_index': -1,
                'status': 'unknown',
                'duration': 0,
                'position': 0
            }
            
            # 提取播放列表信息
            if 'playlist' in settings:
                playlist = settings['playlist']
                if isinstance(playlist, list):
                    vlc_info['playlist'] = [
                        {
                            'index': idx,
                            'path': item.get('value', ''),
                            'name': self._extract_filename(item.get('value', '')),
                            'selected': item.get('selected', False),
                            'hidden': item.get('hidden', False)
                        }
                        for idx, item in enumerate(playlist)
                    ]
                    
                    # 查找当前播放项
                    current_items = [item for item in vlc_info['playlist'] if item['selected']]
                    if current_items:
                        vlc_info['current_item'] = current_items[0]
                        vlc_info['current_index'] = current_items[0]['index']
            
            # 获取其他设置
            vlc_info['loop'] = settings.get('loop', False)
            vlc_info['shuffle'] = settings.get('shuffle', False)
            vlc_info['playback_behavior'] = settings.get('playback_behavior', 'stop_restart')
            vlc_info['network_caching'] = settings.get('network_caching', 400)
            
            return vlc_info
            
        except Exception as e:
            print(f"❌ 获取VLC源 {source_name} 详细信息失败: {e}")
            return None
    
    def _extract_filename(self, file_path: str) -> str:
        """从文件路径提取文件名"""
        if not file_path:
            return ""
        
        # 处理网络URL
        if file_path.startswith(('http://', 'https://', 'rtmp://', 'rtsp://')):
            return file_path.split('/')[-1] or file_path
        
        # 处理本地文件路径
        import os
        return os.path.basename(file_path)
    
    def get_source_status(self, source_name: str) -> Dict:
        """
        获取源的实时状态信息
        :param source_name: 源名称
        :return: 源状态信息
        """
        if not self.obs_client:
            return {'error': 'OBS客户端未连接'}
        
        try:
            # 获取源的基本状态
            status_info = {
                'source_name': source_name,
                'active': False,
                'showing': False,
                'width': 0,
                'height': 0,
                'timestamp': datetime.now().isoformat()
            }
            
            # 检查源是否存在
            try:
                settings_resp = self.obs_client.get_input_settings(source_name)
                status_info['active'] = True
                status_info['source_type'] = settings_resp.input_kind
            except:
                return status_info
            
            # 获取源的显示状态（在哪些场景中可见）
            scenes_sources = self.sources_cache or self.get_all_scenes_sources()
            showing_scenes = []
            
            for scene_name, sources in scenes_sources.items():
                for source in sources:
                    if source['source_name'] == source_name and source.get('enabled', False):
                        showing_scenes.append(scene_name)
            
            status_info['showing_scenes'] = showing_scenes
            status_info['showing'] = len(showing_scenes) > 0
            
            return status_info
            
        except Exception as e:
            return {'error': f'获取源状态失败: {e}'}
    
    def get_vlc_current_media_info(self, source_name: str) -> Dict:
        """
        获取VLC源当前播放的媒体信息
        :param source_name: VLC源名称
        :return: 当前媒体信息
        """
        vlc_info = self._get_vlc_source_details(source_name)
        if not vlc_info:
            return {'error': 'VLC源不存在或获取失败'}
        
        media_info = {
            'source_name': source_name,
            'current_media': vlc_info.get('current_item'),
            'playlist_count': len(vlc_info.get('playlist', [])),
            'current_index': vlc_info.get('current_index', -1),
            'settings': {
                'loop': vlc_info.get('loop', False),
                'shuffle': vlc_info.get('shuffle', False),
                'playback_behavior': vlc_info.get('playback_behavior', 'stop_restart')
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return media_info
    
    def start_source_monitoring(self):
        """开始源信息监控"""
        if self.source_monitor_active:
            return
        
        self.source_monitor_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_sources, daemon=True)
        self.monitor_thread.start()
        print("📊 源信息监控已启动")
    
    def stop_source_monitoring(self):
        """停止源信息监控"""
        self.source_monitor_active = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2)
        print("⏹️ 源信息监控已停止")
    
    def _monitor_sources(self):
        """源信息监控线程"""
        while self.source_monitor_active:
            try:
                # 更新所有场景源信息
                self.get_all_scenes_sources()
                
                # 更新VLC源信息
                self.get_vlc_sources_info()
                
                time.sleep(self.monitor_interval)
                
            except Exception as e:
                print(f"⚠️ 源监控过程中出错: {e}")
                time.sleep(self.monitor_interval)
    
    def print_sources_summary(self):
        """打印源信息摘要"""
        if not self.sources_cache:
            self.get_all_scenes_sources()
        
        print(f"\n📊 源信息摘要 - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60)
        
        total_sources = 0
        vlc_count = 0
        
        for scene_name, sources in self.sources_cache.items():
            print(f"\n🎬 场景: {scene_name}")
            print(f"   📝 源数量: {len(sources)}")
            
            for source in sources:
                source_name = source.get('source_name', 'Unknown')
                source_type = source.get('source_type', 'Unknown')
                enabled = "✅" if source.get('enabled') else "❌"
                
                print(f"   {enabled} {source_name} ({source_type})")
                
                # 如果是VLC源，显示额外信息
                if source_type and 'vlc' in source_type.lower():
                    vlc_count += 1
                    vlc_info = self.vlc_sources.get(source_name)
                    if vlc_info:
                        current = vlc_info.get('current_item')
                        playlist_count = len(vlc_info.get('playlist', []))
                        if current:
                            print(f"      🎵 当前播放: {current.get('name', 'Unknown')}")
                        print(f"      📋 播放列表: {playlist_count} 项")
                
                total_sources += 1
        
        print(f"\n📈 统计信息:")
        print(f"   📊 总源数: {total_sources}")
        print(f"   🎥 VLC源数: {vlc_count}")
        print(f"   🎬 场景数: {len(self.sources_cache)}")
        print("=" * 60)
    
    def print_vlc_sources_detail(self):
        """打印VLC源详细信息"""
        vlc_sources = self.get_vlc_sources_info()
        
        if not vlc_sources:
            print("📝 未找到VLC视频源")
            return
        
        print(f"\n🎥 VLC源详细信息 - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60)
        
        for source_name, vlc_info in vlc_sources.items():
            print(f"\n📺 源名称: {source_name}")
            print(f"   🎯 类型: {vlc_info.get('source_type', 'Unknown')}")
            
            current_item = vlc_info.get('current_item')
            if current_item:
                print(f"   ▶️ 当前播放: {current_item.get('name', 'Unknown')}")
                print(f"   📍 播放索引: {vlc_info.get('current_index', -1) + 1}")
            else:
                print(f"   ⏹️ 当前播放: 无")
            
            playlist = vlc_info.get('playlist', [])
            print(f"   📋 播放列表: {len(playlist)} 项")
            
            settings = vlc_info.get('settings', {})
            print(f"   🔄 循环播放: {'✅' if settings.get('loop') else '❌'}")
            print(f"   🔀 随机播放: {'✅' if settings.get('shuffle') else '❌'}")
            print(f"   ⚙️ 播放行为: {settings.get('playback_behavior', 'unknown')}")
            
            if playlist:
                print(f"   📑 播放列表详情:")
                for item in playlist[:5]:  # 只显示前5项
                    current_mark = "▶️" if item.get('selected') else "   "
                    print(f"      {current_mark} {item['index']+1}. {item['name']}")
                
                if len(playlist) > 5:
                    print(f"      ... 还有 {len(playlist) - 5} 项")
        
        print("=" * 60)
    
    def export_sources_info(self, output_file: str = "sources_info.json"):
        """
        导出源信息到JSON文件
        :param output_file: 输出文件名
        """
        try:
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'scenes_sources': self.sources_cache,
                'vlc_sources': self.vlc_sources,
                'summary': {
                    'total_scenes': len(self.sources_cache),
                    'total_sources': sum(len(sources) for sources in self.sources_cache.values()),
                    'vlc_sources_count': len(self.vlc_sources)
                }
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 源信息已导出到: {output_file}")
            
        except Exception as e:
            print(f"❌ 导出源信息失败: {e}")

def main():
    """测试源管理器功能"""
    print("🎬 OBS源管理器测试")
    print("=" * 50)
    
    # 这里需要OBS连接才能测试
    print("⚠️ 需要OBS WebSocket连接才能测试源管理功能")
    print("💡 请在OBS管理器中调用源管理器功能")
    
    # 创建源管理器实例（无OBS连接）
    source_manager = SourceManager()
    
    print("\n📝 源管理器功能:")
    print("1. get_all_scenes_sources() - 获取所有场景源信息")
    print("2. get_vlc_sources_info() - 获取VLC源信息")
    print("3. get_source_status() - 获取源状态")
    print("4. get_vlc_current_media_info() - 获取VLC当前媒体信息")
    print("5. start_source_monitoring() - 开始源监控")
    print("6. print_sources_summary() - 打印源摘要")
    print("7. print_vlc_sources_detail() - 打印VLC源详情")
    print("8. export_sources_info() - 导出源信息")

if __name__ == "__main__":
    main()