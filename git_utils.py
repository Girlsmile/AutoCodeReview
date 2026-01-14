"""
Git 工具模块
提供 Git 仓库操作相关的工具函数
"""

import subprocess
from pathlib import Path


def get_changed_files(project_path, commit_range='HEAD~1..HEAD'):
    """
    获取指定范围内变更的文件列表
    
    Args:
        project_path: 项目路径
        commit_range: commit 范围，默认为最近一次 commit
        
    Returns:
        list: 变更的文件路径列表，如果失败返回 None
    """
    try:
        result = subprocess.run(
            ['git', 'diff', '--name-only', commit_range],
            capture_output=True,
            text=True,
            check=True,
            cwd=project_path
        )
        
        changed_files = result.stdout.strip().split('\n')
        changed_files = [f for f in changed_files if f]  # 移除空行
        
        return changed_files
    except subprocess.CalledProcessError as e:
        print(f"❌ 获取 Git 变更失败: {e}")
        print("   请确保项目是一个 Git 仓库且有至少 2 次 commit")
        return None


def get_latest_commit_files(project_path):
    """
    获取最近一次 commit 中变更的文件
    
    Args:
        project_path: 项目路径
        
    Returns:
        list: 变更的文件路径列表，如果失败返回 None
    """
    return get_changed_files(project_path, 'HEAD~1..HEAD')


def is_git_repo(project_path):
    """
    检查目录是否是 Git 仓库
    
    Args:
        project_path: 项目路径
        
    Returns:
        bool: 是否为 Git 仓库
    """
    try:
        subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            capture_output=True,
            check=True,
            cwd=project_path
        )
        return True
    except subprocess.CalledProcessError:
        return False


def get_commit_count(project_path):
    """
    获取 commit 数量
    
    Args:
        project_path: 项目路径
        
    Returns:
        int: commit 数量，如果失败返回 0
    """
    try:
        result = subprocess.run(
            ['git', 'rev-list', '--count', 'HEAD'],
            capture_output=True,
            text=True,
            check=True,
            cwd=project_path
        )
        return int(result.stdout.strip())
    except subprocess.CalledProcessError:
        return 0


def get_file_diff(project_path, filepath, commit_range='HEAD~1..HEAD'):
    """
    获取文件的 diff 内容
    
    Args:
        project_path: 项目路径
        filepath: 文件相对路径
        commit_range: commit 范围
        
    Returns:
        str: diff 内容，如果失败返回 None
    """
    try:
        result = subprocess.run(
            ['git', 'diff', commit_range, '--', filepath],
            capture_output=True,
            text=True,
            check=True,
            cwd=project_path
        )
        return result.stdout
    except subprocess.CalledProcessError:
        return None


def is_new_file(project_path, filepath, commit_range='HEAD~1..HEAD'):
    """
    判断文件是否为新增文件
    
    Args:
        project_path: 项目路径
        filepath: 文件相对路径
        commit_range: commit 范围
        
    Returns:
        bool: 是否为新增文件
    """
    try:
        # 使用 --diff-filter=A 只显示新增文件
        result = subprocess.run(
            ['git', 'diff', '--diff-filter=A', '--name-only', commit_range, '--', filepath],
            capture_output=True,
            text=True,
            check=True,
            cwd=project_path
        )
        # 如果输出包含该文件路径，说明是新增文件
        return filepath in result.stdout
    except subprocess.CalledProcessError:
        return False
