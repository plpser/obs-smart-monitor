"""
调试数字检测功能
"""
import re

def _extract_number_with_kan(content):
    """
    检测用户发言内容中是否同时包含"看"字和数字
    如果满足条件，返回提取到的数字；否则返回None
    
    :param content: 用户发言的纯净内容
    :return: 提取到的数字字符串或None
    """
    if not content or not content.strip():
        return None
    
    # 检查是否包含"看"字
    if "看" not in content:
        return None
    
    # 提取所有数字（包括整数和小数）
    number_pattern = r'\d+(?:\.\d+)?'
    numbers = re.findall(number_pattern, content)
    
    if numbers:
        # 如果有多个数字，返回第一个
        return numbers[0]
    
    return None

# 测试用例
test_cases = [
    "看看10的啊",
    "看10",
    "看10号",
    "看看这个",
    "看看10",
    "我想看10号房间",
    "看一看10的",
    "看第10个"
]

print("🔍 调试数字检测功能")
print("=" * 50)

for test_case in test_cases:
    result = _extract_number_with_kan(test_case)
    status = "✅ 检测到" if result else "❌ 未检测到"
    print(f"输入: '{test_case}' -> {status}: {result}")