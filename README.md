# 蓝墨云班课助手

一个帮助你自动完成蓝墨云班课学习的工具。

## 功能特点

- 现代化的图形界面
- 支持账号密码登录
- 支持多课程同时选择
- 支持多资源批量刷课
- 实时显示刷课进度
- 友好的错误提示

## 更新日志

### 2024-12-14
- 添加现代化图形界面
- 支持多课程、多资源批量刷课
- 优化用户体验和界面设计

### 2022-11-10
- 修复mp3文件无法刷课的问题
- 适配官方接口变动

## 安装

1. 克隆仓库：
```bash
git clone https://github.com/ubadly/Mosoteach.git
cd Mosoteach
```

2. 创建并激活虚拟环境（可选）：
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

## 运行

### 图形界面模式（推荐）

```bash
python run.py --gui
```

### 命令行模式

```bash
# 完成所有课程
python run.py --username 手机号 --password 密码

# 完成指定课程
python run.py --username 手机号 --password 密码 --course-id 课程ID
```

## 开发计划

- [x] 现代化图形界面
- [x] 多课程批量处理
- [x] 实时进度显示

## 贡献

欢迎提交 Issue 和 Pull Request。

## 许可证

MIT License
