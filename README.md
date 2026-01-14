# iOS 代码审查工具 (AIAgent)

> 🍎 **macOS 平台专用** - 基于 Google Gemini AI 的自动化 iOS 代码审查工具

[![Platform](https://img.shields.io/badge/platform-macOS-lightgrey.svg)](https://www.apple.com/macos/)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## ✨ 功能特性

- 🤖 **AI 驱动审查** - 使用 Google Gemini 模型进行智能代码分析
- 🎯 **三种审核级别** - 宽松/中等/严格，满足不同场景需求
- 📊 **Git 集成** - 支持全项目扫描和 Git Diff 模式
- 🔔 **系统通知** - macOS 通知中心实时反馈审查结果
- 📝 **详细报告** - 自动生成 JSON 格式的审查报告
- 🪝 **Git Hook** - 自动化 commit 后审查流程
- 🌍 **中文支持** - 完整的中文界面和审查建议

## 📋 系统要求

- **操作系统**: macOS 10.14+
- **Python**: 3.8 或更高版本
- **Git**: 2.0 或更高版本
- **网络**: 需要访问 Google Gemini API

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd AIAgent
```

### 2. 安装依赖

```bash
# 创建虚拟环境
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
pip install google-generativeai
```

### 3. 配置 API Key

```bash
# 设置 Google Gemini API Key
export GOOGLE_API_KEY="your-api-key-here"

# 或添加到 ~/.zshrc 永久生效
echo 'export GOOGLE_API_KEY="your-api-key-here"' >> ~/.zshrc
```

### 4. 配置项目路径

编辑 `config/config.json`：

```json
{
    "project_path": "/path/to/your/ios/project",
    "file_extensions": [".swift", ".m", ".h"],
    "exclude_patterns": [
        "**/Pods/**",
        "**/build/**",
        "**/DerivedData/**"
    ],
    "max_file_size_kb": 100,
    "review_level": "moderate"
}
```

### 5. 运行审查

```bash
# Git Diff 模式（默认）- 只审查最新 commit
python scan_project.py

# 全项目扫描模式
python scan_project.py --mode full
```

## 🔧 工作流程

### 方式一：手动运行

```
┌─────────────────┐
│  修改代码并提交  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ python scan_    │
│   project.py    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AI 分析代码    │
│  (Gemini API)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  生成审查报告   │
│  (JSON 格式)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  系统通知提醒   │
│  (macOS 通知)   │
└─────────────────┘
```

### 方式二：Git Hook 自动化

```
┌─────────────────┐
│   git commit    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ post-commit     │
│   hook 触发     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  后台运行审查   │
│  (不阻塞提交)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  审查完成通知   │
│  + 报告生成     │
└─────────────────┘
```

## 🪝 安装 Git Hook

### 自动安装（推荐）

```bash
# 给安装脚本添加执行权限
chmod +x install_hook.sh

# 安装到目标项目
./install_hook.sh /path/to/your/ios/project
```

### 手动安装

```bash
# 1. 复制 hook 文件
cp post-commit /path/to/your/project/.git/hooks/

# 2. 添加执行权限
chmod +x /path/to/your/project/.git/hooks/post-commit

# 3. 编辑 hook 文件，修改 AIAgent 路径
vim /path/to/your/project/.git/hooks/post-commit
```

详细说明请参考 [INSTALL_HOOK.md](INSTALL_HOOK.md)

## 📊 审核级别说明

### 🟢 relaxed（宽松）
- **关注**: Bug 和安全问题
- **忽略**: 代码风格、性能优化
- **适用**: 快速迭代、原型开发

### 🟡 moderate（中等）- 默认
- **关注**: Bug、安全、性能问题
- **忽略**: 代码风格（除非严重影响可读性）
- **适用**: 日常开发、功能迭代

### 🔴 strict（严格）
- **关注**: 所有问题（Bug、安全、性能、风格）
- **忽略**: 无
- **适用**: 代码审查、发布前检查

## 📁 项目结构

```
AIAgent/
├── config/
│   ├── config.json           # 项目配置
│   └── prompt_template.json  # AI 提示词模板
├── review_history/           # 审查报告存储目录
│   └── review_*.json        # 历史审查报告
├── scan_project.py          # 主程序
├── git_utils.py             # Git 工具函数
├── notification_utils.py    # 通知工具函数
├── post-commit              # Git Hook 模板
├── install_hook.sh          # Hook 安装脚本
├── INSTALL_HOOK.md          # Hook 安装指南
└── README.md                # 本文件
```

## 🎯 使用示例

### 示例 1: 审查最新 commit

```bash
$ python scan_project.py

======================================================================
🔍 iOS 项目代码审查工具 - 模式: git-diff
======================================================================

📊 审核级别: 中等（Bug、安全、性能问题）

📋 Git Diff 模式 - 只审查最新 commit 的变更

📝 最新 commit 变更了 3 个文件
✅ 其中 3 个需要审查

======================================================================
🚀 开始审查 3 个文件...
======================================================================

[1/3] 📂 正在审查: ContentView.swift
----------------------------------------------------------------------
   📝 修改文件 - 仅审查差异部分

   ⚠️  发现 2 个问题：

   1. [BUG] [行 45]
      问题: 数组越界风险
      建议: 添加边界检查

   2. [PERFORMANCE] [行 120]
      问题: 主线程执行耗时操作
      建议: 移至后台线程

...

📄 详细报告已保存: review_history/review_20260113_173923.json
💡 使用以下命令打开报告:
   open review_history/review_20260113_173923.json
```

### 示例 2: 切换审核级别

```bash
# 编辑配置文件
vim config/config.json

# 修改 review_level
{
    "review_level": "strict"  # relaxed | moderate | strict
}

# 运行审查
python scan_project.py
```

## 🔔 通知说明

审查完成后会发送 macOS 系统通知：

- ✅ **成功**: "代码审查完成 - 所有文件审查通过"
- ⚠️ **发现问题**: "代码审查完成 - 发现 X 个问题，涉及 X 个文件"
- ❌ **失败**: "代码审查失败 - API 调用失败，请检查网络或配额"

## 📝 报告格式

审查报告以 JSON 格式保存在 `review_history/` 目录：

```json
{
  "timestamp": "20260113_173923",
  "review_level": "moderate",
  "total_issues": 2,
  "files_with_issues": 1,
  "details": [
    {
      "file": "ContentView.swift",
      "issues": [
        {
          "type": "bug",
          "line_number": 45,
          "description": "数组越界风险",
          "suggestion": "添加边界检查"
        }
      ]
    }
  ]
}
```

## ⚙️ 高级配置

### 自定义文件类型

```json
{
    "file_extensions": [
        ".swift",
        ".m",
        ".h",
        ".mm",
        ".cpp"
    ]
}
```

### 自定义排除规则

```json
{
    "exclude_patterns": [
        "**/Pods/**",
        "**/Carthage/**",
        "**/build/**",
        "**/.build/**",
        "**/DerivedData/**",
        "**/*.generated.swift",
        "**/Tests/**"
    ]
}
```

### 调整文件大小限制

```json
{
    "max_file_size_kb": 200  // 默认 100KB
}
```

## 🐛 常见问题

### Q: API 调用失败？
**A**: 检查以下几点：
1. API Key 是否正确设置
2. 网络连接是否正常
3. API 配额是否用尽（免费版有限制）

### Q: Hook 没有运行？
**A**: 检查：
1. Hook 文件是否有执行权限：`ls -l .git/hooks/post-commit`
2. AIAgent 路径是否正确
3. 虚拟环境是否正确激活

### Q: 通知没有显示？
**A**: 确保：
1. 系统通知权限已开启
2. 终端有通知权限（系统偏好设置 → 通知）

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题或建议，请提交 Issue。

---

**注意**: 本工具仅支持 macOS 平台，需要 Google Gemini API Key。
