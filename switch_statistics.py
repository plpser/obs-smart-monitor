"""
场景切换统计管理器
功能：
1. 统计成功切换的次数
2. 每个整点打印统计信息
3. 将切换记录保存到数据库
"""

import sqlite3
import threading
import time
from datetime import datetime, timedelta
import schedule
import os

class SwitchStatistics:
    """场景切换统计管理器"""
    
    def __init__(self, db_path="switch_records.db"):
        """
        初始化统计管理器
        :param db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.session_switch_count = 0  # 本次启动后的切换次数
        self.lock = threading.Lock()
        
        # 初始化数据库
        self._init_database()
        
        # 启动定时任务
        self._start_scheduler()
        
        print(f"📊 统计系统已启动，数据库: {self.db_path}")
    
    def _init_database(self):
        """初始化数据库，创建表结构"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建切换记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS switch_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    switch_time TEXT NOT NULL,
                    user_content TEXT NOT NULL,
                    scene_number TEXT NOT NULL,
                    scene_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建统计表（按小时统计）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS hourly_statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hour_time TEXT NOT NULL UNIQUE,
                    switch_count INTEGER NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
            print("✅ 数据库初始化成功")
            
        except sqlite3.Error as e:
            print(f"❌ 数据库初始化失败: {e}")
    
    def record_switch(self, user_content, scene_number, scene_name=None):
        """
        记录一次成功的场景切换
        :param user_content: 用户发言内容
        :param scene_number: 场景编号
        :param scene_name: 场景名称
        """
        with self.lock:
            try:
                # 更新本次启动的计数
                self.session_switch_count += 1
                
                # 记录到数据库
                switch_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO switch_records (switch_time, user_content, scene_number, scene_name)
                    VALUES (?, ?, ?, ?)
                ''', (switch_time, user_content, str(scene_number), scene_name))
                
                conn.commit()
                conn.close()
                
                print(f"📈 切换统计 - 本次启动: {self.session_switch_count} 次")
                
            except sqlite3.Error as e:
                print(f"❌ 记录切换失败: {e}")
    
    def get_session_count(self):
        """获取本次启动后的切换次数"""
        return self.session_switch_count
    
    def get_total_count(self):
        """获取总切换次数"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM switch_records')
            total_count = cursor.fetchone()[0]
            
            conn.close()
            return total_count
            
        except sqlite3.Error as e:
            print(f"❌ 获取总计数失败: {e}")
            return 0
    
    def get_today_count(self):
        """获取今天的切换次数"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) FROM switch_records 
                WHERE DATE(switch_time) = ?
            ''', (today,))
            
            today_count = cursor.fetchone()[0]
            
            conn.close()
            return today_count
            
        except sqlite3.Error as e:
            print(f"❌ 获取今日计数失败: {e}")
            return 0
    
    def get_current_hour_count(self):
        """获取当前小时的切换次数"""
        try:
            current_hour = datetime.now().strftime('%Y-%m-%d %H')
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) FROM switch_records 
                WHERE strftime('%Y-%m-%d %H', switch_time) = ?
            ''', (current_hour,))
            
            hour_count = cursor.fetchone()[0]
            
            conn.close()
            return hour_count
            
        except sqlite3.Error as e:
            print(f"❌ 获取当前小时计数失败: {e}")
            return 0
    
    def _print_hourly_statistics(self):
        """打印整点统计信息"""
        try:
            current_time = datetime.now()
            hour_time = current_time.strftime('%Y-%m-%d %H:00')
            
            session_count = self.get_session_count()
            total_count = self.get_total_count()
            today_count = self.get_today_count()
            hour_count = self.get_current_hour_count()
            
            # 更新小时统计表
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO hourly_statistics (hour_time, switch_count)
                VALUES (?, ?)
            ''', (hour_time, hour_count))
            
            conn.commit()
            conn.close()
            
            # 打印统计信息
            print("\n" + "=" * 60)
            print(f"📊 【整点统计】- {current_time.strftime('%H:00')}")
            print(f"   🚀 本次启动: {session_count:,} 次切换")
            print(f"   📅 今日总计: {today_count:,} 次切换")
            print(f"   ⏰ 当前小时: {hour_count:,} 次切换")
            print(f"   📈 历史总计: {total_count:,} 次切换")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ 打印整点统计失败: {e}")
    
    def _start_scheduler(self):
        """启动定时任务调度器"""
        def job():
            self._print_hourly_statistics()
        
        # 设置每个整点触发
        schedule.every().hour.at(":00").do(job)
        
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(1)
        
        # 启动调度器线程
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        print("⏰ 整点统计定时器已启动")
    
    def get_recent_records(self, limit=10):
        """获取最近的切换记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT switch_time, user_content, scene_number, scene_name
                FROM switch_records
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
            
            records = cursor.fetchall()
            conn.close()
            
            return records
            
        except sqlite3.Error as e:
            print(f"❌ 获取最近记录失败: {e}")
            return []
    
    def print_recent_records(self, limit=5):
        """打印最近的切换记录"""
        records = self.get_recent_records(limit)
        
        if not records:
            print("📝 暂无切换记录")
            return
        
        print(f"\n📝 最近 {len(records)} 次切换记录:")
        print("   时间                | 场景    | 用户发言")
        print("   ------------------|--------|------------------")
        
        for record in records:
            switch_time, user_content, scene_number, scene_name = record
            # 截断过长的用户发言
            truncated_content = user_content[:15] + "..." if len(user_content) > 15 else user_content
            scene_display = f"{scene_number}"
            if scene_name:
                scene_display += f"({scene_name})"
            
            print(f"   {switch_time} | {scene_display:<6} | {truncated_content}")
    
    def export_statistics(self, output_file="switch_statistics.txt"):
        """导出统计数据到文件"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                current_time = datetime.now()
                
                f.write(f"场景切换统计报告\n")
                f.write(f"生成时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 50 + "\n\n")
                
                # 基本统计
                session_count = self.get_session_count()
                total_count = self.get_total_count()
                today_count = self.get_today_count()
                
                f.write(f"基本统计:\n")
                f.write(f"  本次启动: {session_count:,} 次\n")
                f.write(f"  今日总计: {today_count:,} 次\n")
                f.write(f"  历史总计: {total_count:,} 次\n\n")
                
                # 最近记录
                records = self.get_recent_records(20)
                f.write(f"最近 {len(records)} 次切换记录:\n")
                f.write("-" * 50 + "\n")
                
                for record in records:
                    switch_time, user_content, scene_number, scene_name = record
                    f.write(f"时间: {switch_time}\n")
                    f.write(f"场景: {scene_number}")
                    if scene_name:
                        f.write(f"({scene_name})")
                    f.write(f"\n用户发言: {user_content}\n")
                    f.write("-" * 30 + "\n")
            
            print(f"✅ 统计数据已导出到: {output_file}")
            
        except Exception as e:
            print(f"❌ 导出统计数据失败: {e}")

def main():
    """测试统计系统"""
    print("📊 场景切换统计系统测试")
    print("=" * 50)
    
    stats = SwitchStatistics()
    
    # 模拟一些切换记录
    test_records = [
        ("看8", "8", "8米项链"),
        ("看114", "114", "6米项链108颗"),
        ("看12", "12", "12号场景"),
        ("看116", "116", "8米项链108颗"),
    ]
    
    print("\n📝 添加测试记录...")
    for content, number, name in test_records:
        stats.record_switch(content, number, name)
        time.sleep(1)
    
    # 显示统计信息
    print(f"\n📊 当前统计:")
    print(f"  本次启动: {stats.get_session_count()} 次")
    print(f"  今日总计: {stats.get_today_count()} 次")
    print(f"  历史总计: {stats.get_total_count()} 次")
    
    # 显示最近记录
    stats.print_recent_records()
    
    # 导出统计
    stats.export_statistics("test_statistics.txt")
    
    print("\n✅ 测试完成")

if __name__ == "__main__":
    main()