import json
import os
import sys
import argparse
from pathlib import Path
from google import genai
import git_utils
import notification_utils

def load_config():
    """加载配置文件"""
    try:
        with open('config/config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ 未找到 config/config.json 文件")
        print("请创建 config/config.json 并配置 project_path")
        exit(1)

def should_exclude(filepath, exclude_patterns):
    """检查文件是否应该被排除"""
    from fnmatch import fnmatch
    for pattern in exclude_patterns:
        if fnmatch(str(filepath), pattern):
            return True
    return False

def scan_project_files(project_path, extensions, exclude_patterns, max_size_kb):
    """扫描项目目录，获取所有符合条件的文件"""
    project_path = Path(project_path)
    
    if not project_path.exists():
        print(f"❌ 项目路径不存在: {project_path}")
        return []
    
    files = []
    max_size_bytes = max_size_kb * 1024
    
    print(f"📁 扫描项目目录: {project_path}")
    print(f"📋 文件类型: {', '.join(extensions)}")
    print(f"📏 文件大小限制: {max_size_kb}KB")
    print()
    
    for extension in extensions:
        # 使用 rglob 递归搜索
        for filepath in project_path.rglob(f"*{extension}"):
            # 检查是否应该排除
            if should_exclude(filepath, exclude_patterns):
                continue
            
            # 检查文件大小
            try:
                file_size = filepath.stat().st_size
                if file_size > max_size_bytes:
                    print(f"⚠️  跳过大文件: {filepath.relative_to(project_path)} ({file_size // 1024}KB)")
                    continue
                
                files.append(filepath)
            except Exception as e:
                print(f"⚠️  无法访问文件: {filepath}: {e}")
                continue
    
    return files

def review_code(code, filename, review_level='moderate'):
    """调用 Gemini API 审查代码"""
    
    # 读取 prompt 模板
    try:
        with open('config/prompt_template.json', 'r', encoding='utf-8') as f:
            prompt_config = json.load(f)
            
        # 验证审核级别
        if review_level not in prompt_config:
            print(f"⚠️  无效的审核级别: {review_level}，使用默认的 moderate")
            review_level = 'moderate'
        
        prompt_template = prompt_config[review_level]['prompt']
    except Exception as e:
        print(f"❌ 无法读取 prompt 模板: {e}")
        return None
    
    # 构建完整的 prompt
    prompt = prompt_template.replace('{code}', code)
    
    # 初始化客户端
    client = genai.Client()
    
    # 尝试多个模型
    models_to_try = [
        "models/gemini-2.5-flash",
        "models/gemini-2.0-flash",
        "models/gemini-flash-latest",
        "models/gemini-3-flash-preview",
    ]
    
    for model in models_to_try:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
            )
            return response.text
        except Exception as e:
            continue
    
    return None

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='iOS 项目代码审查工具')
    parser.add_argument(
        '--mode',
        choices=['full', 'git-diff'],
        default='git-diff',  # 默认使用 git-diff 模式
        help='审查模式: full=扫描整个项目, git-diff=只审查最新commit的变更（默认）'
    )
    args = parser.parse_args()
    
    print("=" * 70)
    print(f"🔍 iOS 项目代码审查工具 - 模式: {args.mode}")
    print("=" * 70)
    print()
    
    # 加载配置
    config = load_config()
    project_path = Path(config['project_path'])
    review_level = config.get('review_level', 'moderate')
    
    # 显示审核级别
    level_desc = {
        'relaxed': '宽松（仅 Bug 和安全问题）',
        'moderate': '中等（Bug、安全、性能问题）',
        'strict': '严格（所有问题）'
    }
    print(f"📊 审核级别: {level_desc.get(review_level, review_level)}")
    print()
    
    if not project_path.exists():
        print(f"❌ 项目路径不存在: {project_path}")
        return
    
    # 根据模式获取文件列表
    if args.mode == 'git-diff':
        print("📋 Git Diff 模式 - 只审查最新 commit 的变更")
        print()
        
        # 检查是否为 Git 仓库
        if not git_utils.is_git_repo(project_path):
            print("❌ 该目录不是 Git 仓库")
            print("   请在 Git 仓库中使用 git-diff 模式")
            return
        
        # 获取 Git 变更的文件
        changed_files = git_utils.get_latest_commit_files(project_path)
        if changed_files is None:
            return
        
        if not changed_files:
            print("✅ 最新 commit 没有文件变更")
            return
        
        # 过滤出符合条件的文件
        files = []
        skipped_reasons = {
            'not_exist': [],
            'wrong_extension': [],
            'excluded': [],
            'too_large': []
        }
        
        for filepath in changed_files:
            full_path = project_path / filepath
            
            # 检查文件是否存在（可能被删除）
            if not full_path.exists():
                skipped_reasons['not_exist'].append(filepath)
                continue
            
            # 检查扩展名
            if full_path.suffix not in config['file_extensions']:
                skipped_reasons['wrong_extension'].append(filepath)
                continue
            
            # 检查排除规则
            if should_exclude(full_path, config['exclude_patterns']):
                skipped_reasons['excluded'].append(filepath)
                continue
            
            # 检查文件大小
            file_size = full_path.stat().st_size
            max_size_bytes = config['max_file_size_kb'] * 1024
            if file_size > max_size_bytes:
                skipped_reasons['too_large'].append(f"{filepath} ({file_size // 1024}KB)")
                continue
            
            files.append(full_path)
        
        print(f"📝 最新 commit 变更了 {len(changed_files)} 个文件")
        print(f"✅ 其中 {len(files)} 个需要审查")
        
        # 显示被跳过的文件统计
        if skipped_reasons['not_exist']:
            print(f"   ⊖ {len(skipped_reasons['not_exist'])} 个文件已删除")
        if skipped_reasons['wrong_extension']:
            print(f"   ⊖ {len(skipped_reasons['wrong_extension'])} 个文件类型不匹配（非 .swift/.m/.h）")
            # 显示前 5 个被跳过的文件类型示例
            examples = list(set([Path(f).suffix for f in skipped_reasons['wrong_extension'][:10]]))
            if examples:
                print(f"      示例扩展名: {', '.join(examples)}")
        if skipped_reasons['excluded']:
            print(f"   ⊖ {len(skipped_reasons['excluded'])} 个文件被排除规则过滤")
        if skipped_reasons['too_large']:
            print(f"   ⊖ {len(skipped_reasons['too_large'])} 个文件过大（>{config['max_file_size_kb']}KB）")
        
    else:
        # 全项目扫描模式
        files = scan_project_files(
            config['project_path'],
            config['file_extensions'],
            config['exclude_patterns'],
            config['max_file_size_kb']
        )
        
        if not files:
            print("✅ 没有找到需要审查的文件")
            return
        
        print(f"✅ 找到 {len(files)} 个文件待审查")
    
    if not files:
        print("✅ 没有需要审查的文件")
        return
    
    print()
    print("=" * 70)
    print(f"🚀 开始审查 {len(files)} 个文件...")
    print("=" * 70)
    
    # 审查每个文件
    all_issues = []
    
    for i, filepath in enumerate(files, 1):
        relative_path = filepath.relative_to(project_path)
        print(f"\n[{i}/{len(files)}] 📂 正在审查: {relative_path}")
        print("-" * 70)
        
        # 判断是否为新文件
        is_new = args.mode == 'git-diff' and git_utils.is_new_file(project_path, str(relative_path))
        
        if is_new:
            print("   📄 新增文件 - 审查全部内容")
            # 读取整个文件内容
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    code_to_review = f.read()
            except Exception as e:
                print(f"⚠️  无法读取文件: {e}")
                continue
        else:
            # 只审查 diff 部分
            if args.mode == 'git-diff':
                print("   📝 修改文件 - 仅审查差异部分")
                diff_content = git_utils.get_file_diff(project_path, str(relative_path))
                
                if not diff_content or not diff_content.strip():
                    print("   ⚠️  未检测到有效差异，跳过")
                    continue
                
                code_to_review = diff_content
            else:
                # full 模式，审查整个文件
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        code_to_review = f.read()
                except Exception as e:
                    print(f"⚠️  无法读取文件: {e}")
                    continue
        
        # 调用 AI 审查
        result = review_code(code_to_review, str(relative_path), review_level)
        
        if result:
            try:
                # 解析 JSON 结果
                review_data = json.loads(result)
                
                if review_data.get('has_issue'):
                    issues = review_data.get('issues', [])
                    print(f"\n   ⚠️  发现 {len(issues)} 个问题：\n")
                    
                    for j, issue in enumerate(issues, 1):
                        line_info = f" [行 {issue['line_number']}]" if 'line_number' in issue and issue['line_number'] else ""
                        print(f"   {j}. [{issue['type'].upper()}]{line_info}")
                        print(f"      问题: {issue['description']}")
                        print(f"      建议: {issue['suggestion']}")
                        print()
                    
                    all_issues.append({
                        'file': str(relative_path),
                        'issues': issues
                    })
                else:
                    print("   ✅ 未发现明显问题")
            except json.JSONDecodeError:
                print(f"   ⚠️  AI 返回格式异常")
        else:
            print("   ❌ 审查失败（API 调用失败）")
            # 发送失败通知
            notification_utils.send_failure_notification("API 调用失败，请检查网络或 API 配额")
    
    # 总结
    print("\n" + "=" * 70)
    print("📊 审查总结")
    print("=" * 70)
    
    if all_issues:
        total_issues = sum(len(item['issues']) for item in all_issues)
        print(f"\n⚠️  共发现 {total_issues} 个问题，涉及 {len(all_issues)} 个文件")
        print("\n问题文件列表：")
        for item in all_issues:
            issue_count = len(item['issues'])
            print(f"  - {item['file']} ({issue_count} 个问题)")
        
        # 生成审查报告 JSON
        import datetime
        report_dir = Path('review_history')
        report_dir.mkdir(exist_ok=True)
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = report_dir / f'review_{timestamp}.json'
        report_data = {
            'timestamp': timestamp,
            'review_level': review_level,
            'total_issues': total_issues,
            'files_with_issues': len(all_issues),
            'details': all_issues
        }
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        # 发送系统通知并打开报告文件
        notification_utils.send_review_summary(total_issues, len(all_issues), level_desc.get(review_level, review_level), str(report_path))
    else:
        print("\n✅ 所有文件审查通过！")
        
        # 发送成功通知
        level_name = level_desc.get(review_level, review_level)
        notification_utils.send_review_summary(0, 0, level_name)
    
    print("\n" + "=" * 70)

if __name__ == '__main__':
    main()
