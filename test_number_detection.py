"""
测试"看"字和数字检测功能
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

def test_number_detection():
    """测试数字检测功能"""
    
    # 测试用例
    test_cases = [
        "看123号房间",           # 应该返回 "123"
        "看房间456",             # 应该返回 "456"
        "我想看7.5个小时",        # 应该返回 "7.5"
        "看看这个",               # 应该返回 None（没有数字）
        "房间123很好",            # 应该返回 None（没有"看"字）
        "看房间88和99",           # 应该返回 "88"（第一个数字）
        "看12.34和56.78",        # 应该返回 "12.34"
        "",                      # 应该返回 None（空内容）
        "看",                     # 应该返回 None（只有"看"字）
        "看0号",                  # 应该返回 "0"
        "看100.0房间",            # 应该返回 "100.0"
        "想看看电影",              # 应该返回 None（没有数字）
        "看第1集",                # 应该返回 "1"
    ]
    
    print("🔢 “看”字和数字检测功能测试")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        result = _extract_number_with_kan(test_case)
        
        # 判断测试结果状态
        if result is not None:
            status = "✅ 检测到"
            status_detail = f"数字: {result}"
        else:
            status = "❌ 未检测到"
            status_detail = "无匹配结果"
        
        print(f"\n测试用例 {i}:")
        print(f"   📝 输入内容: '{test_case}'")
        print(f"   {status} {status_detail}")
        print("   " + "-" * 45)
    
    # 统计测试结果
    positive_cases = ["看123号房间", "看房间456", "我想看7.5个小时", "看房间88和99", "看12.34和56.78", "看0号", "看100.0房间", "看第1集"]
    negative_cases = ["看看这个", "房间123很好", "", "看", "想看看电影"]
    
    print(f"\n📊 测试统计:")
    print(f"   预期有数字的用例: {len(positive_cases)} 个")
    print(f"   预期无数字的用例: {len(negative_cases)} 个")
    print(f"   总测试用例: {len(test_cases)} 个")

if __name__ == "__main__":
    test_number_detection()