"""生成测试 Token"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.jwt_generator import print_test_tokens

if __name__ == "__main__":
    print_test_tokens()
