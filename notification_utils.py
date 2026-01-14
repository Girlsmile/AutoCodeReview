import subprocess
import os


def send_review_summary(total_issues: int, file_count: int, level_name: str, report_path: str = None):
    """Send a macOS notification after code review.

    Args:
        total_issues: Total number of issues found.
        file_count: Number of files with issues.
        level_name: Review level description.
        report_path: Optional path to the JSON report file.
    """
    title = "代码审查完成"
    if total_issues == 0:
        message = f"所有文件审查通过！审核级别: {level_name}"
    else:
        message = f"发现 {total_issues} 个问题，涉及 {file_count} 个文件"
    
    # 发送系统通知到右上角
    try:
        subprocess.run([
            "osascript",
            "-e",
            f'display notification "{message}" with title "{title}" sound name "default"'
        ], check=False)
    except Exception as e:
        print(f"⚠️ 发送通知失败: {e}")
    
    # 在控制台输出报告路径
    if report_path:
        print(f"\n📄 详细报告已保存: {report_path}")
        print(f"💡 使用以下命令打开报告:")
        print(f"   open {report_path}")


def send_failure_notification(reason="API 调用失败"):
    """Send notification when review fails.
    
    Args:
        reason: Failure reason description
    """
    title = "❌ 代码审查失败"
    message = f"原因: {reason}"
    
    try:
        subprocess.run([
            "osascript",
            "-e",
            f'display notification "{message}" with title "{title}" sound name "Basso"'
        ], check=False)
    except Exception as e:
        print(f"⚠️ 发送通知失败: {e}")


