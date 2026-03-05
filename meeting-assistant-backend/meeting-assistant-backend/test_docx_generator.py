"""Test script for DOCX generator with comprehensive Markdown formats."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.utils.docx_generator import generate_meeting_minutes_docx


def test_markdown_conversion():
    """Test various Markdown formats."""
    test_content = """### 一、会议概况

本次会议于2024年3月5日召开，主要讨论了项目进展和下一步计划。

**基本信息**：
- 时间：2024年3月5日 14:00-16:00
- 地点：第一会议室
- 主持人：张三
- 记录人：李四

---

## 二、会议议程

### （一）项目进展汇报

各部门汇报当前工作进展情况。

1. 后端开发 - 已完成API接口开发，正在优化性能
2. 前端开发 - 页面基本完成，正在进行联调
3. 测试工作 - 单元测试覆盖率已达85%

### （二）技术讨论

针对以下技术问题进行了深入讨论：

- 数据库查询优化方案
- 缓存策略的实施
- 前端性能提升措施

### （三）问题与解决方案

遇到的主要问题及解决方案：

| 问题描述 | 影响范围 | 解决方案 | 负责人 |
| --- | --- | --- | --- |
| API响应慢 | 全部用户 | 添加Redis缓存 | 王五 |
| 页面加载慢 | 移动端 | 图片懒加载 | 赵六 |
| 数据同步问题 | 订单模块 | 优化事务处理 | 钱七 |

---

## 三、会议决议

经讨论，形成以下决议：

一、**所有部门需在3月15日前完成当前阶段任务**

二、技术组需在一周内完成性能优化工作

三、下周一开始进行系统联调测试

> 重要提醒：各部门请务必按时完成任务，如有困难请及时沟通协调。

---

## 四、下一步工作安排

### （一）本周重点工作

1. 完成性能优化
2. 修复已知bug
3. 准备测试数据

### （二）下周计划

a. 开始系统集成测试
b. 编写用户手册
c. 准备演示环境

### （三）注意事项

- *代码提交前请进行自测*
- 每天下午5点前更新进度
- 遇到问题及时在群里沟通

~~原定于周五的发布推迟到下周一~~

### （四）技术参考

示例代码：
```
def process_order(order_id):
    # 订单处理逻辑
    order = get_order(order_id)
    if order.status == 'pending':
        order.process()
    return order
```

---

五、散会

会议于16:00结束，下次会议时间为3月12日14:00。
"""

    # Generate DOCX
    print("Generating DOCX from Markdown...")
    print("-" * 50)

    docx_bytes = generate_meeting_minutes_docx(
        meeting_title="项目进度讨论会",
        content=test_content
    )

    # Save to file
    output_path = Path(__file__).parent / "test_output_comprehensive.docx"
    with open(output_path, 'wb') as f:
        f.write(docx_bytes)

    print(f"✓ DOCX generated successfully!")
    print(f"  Path: {output_path}")
    print(f"  Size: {len(docx_bytes):,} bytes")
    print("-" * 50)

    # Display markdown format summary
    print("\nMarkdown formats tested:")
    print("  • Headings: #, ##, ###")
    print("  • Chinese numbering: （一）（二）, 一、二、")
    print("  • Bold: **text**")
    print("  • Italic: *text*")
    print("  • Bold+Italic: ***text***")
    print("  • Lists: 1. 2. 3., a. b. c., - ")
    print("  • Code spans: `code`")
    print("  • Horizontal rule: ---")
    print("  • Blockquotes: > quote")
    print("  • Strikethrough: ~~text~~")
    print("  • Tables: | col | col |")

    return output_path


if __name__ == "__main__":
    test_markdown_conversion()
