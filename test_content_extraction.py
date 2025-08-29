"""
测试用户发言内容提取功能
"""
import re

def test_extract_user_speech():
    """测试用户发言内容提取函数"""
    
    def _extract_user_speech(line):
        """
        提取用户发言内容，去除时间戳和用户标识等前缀
        支持多种格式：
        - 2025-08-29 22:53:09[用户发言]t： 有黄水吗
        - [用户发言]用户名： 内容
        - 时间 用户名： 内容
        """
        if not line or not line.strip():
            return "空内容"
        
        original_line = line.strip()
        
        # 匹配模式1: 2025-08-29 22:53:09[用户发言]t： 有黄水吗
        pattern1 = r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\[用户发言\][^：]*：\s*(.*)'
        match1 = re.match(pattern1, original_line)
        if match1:
            content = match1.group(1).strip()
            return content if content else "空内容"
        
        # 匹配模式2: [用户发言]用户名： 内容
        pattern2 = r'\[用户发言\][^：]*：\s*(.*)'
        match2 = re.match(pattern2, original_line)
        if match2:
            content = match2.group(1).strip()
            return content if content else "空内容"
        
        # 匹配模式3: 时间戳 用户名： 内容
        pattern3 = r'\d{2}:\d{2}:\d{2}\s+[^：]*：\s*(.*)'
        match3 = re.match(pattern3, original_line)
        if match3:
            content = match3.group(1).strip()
            return content if content else "空内容"
        
        # 如果没有匹配到任何模式，返回原始内容
        return original_line
    
    # 测试用例
    test_cases = [
        "2025-08-29 22:53:09[用户发言]t： 有黄水吗",
        "[用户发言]张三： 今天天气怎么样？",
        "14:30:15 李四： 大家好",
        "2025-08-30 10:15:30[用户发言]admin： 这是一条测试消息",
        "[用户发言]用户A： ",
        "普通的文本内容",
        "",
        "2025-08-29 22:53:09[用户发言]： 没有用户名的消息"
    ]
    
    print("🧪 用户发言内容提取测试")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        result = _extract_user_speech(test_case)
        print(f"\n测试用例 {i}:")
        print(f"   📝 原始内容: {repr(test_case)}")
        print(f"   ✨ 提取结果: {repr(result)}")
        print("   " + "-" * 50)

if __name__ == "__main__":
    test_extract_user_speech()