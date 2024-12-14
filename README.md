# Mosoteach
蓝墨云云班课刷分数
## 2022-11-10更新
好家伙，代码写的够乱的，不过我记得当时为了写这个脚本让我茶不思饭不想的，对我颇有影响！

我刚无聊测试一下发现mp3的文件不会刷上，原来是官方有些改动，我又按照原来的风格适配了一下，能用就行。。。



## 使用说明

需要python3x版本

执行pip install -r requirements.txt安装所需环境

执行python main.py即可

## 下载连接
[Releases](https://github.com/xiaoqingfengATGH/mosoteach/releases)

# 慕课堂助手

一个用于简化慕课堂操作的命令行工具。

## 功能特点

- 支持账号密码登录
- 班课信息查看
- 资源批量下载（开发中）
- 友好的命令行界面
- 完善的错误处理和日志记录

## 安装

1. 克隆仓库：
```bash
git clone https://github.com/ubadly/mosoteach.git
cd mosoteach
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

1. 首次使用时，复制配置文件模板：
```bash
cp config/config.example.yaml config/config.yaml
```

2. 编辑 `config/config.yaml` 根据需要修改配置

3. 运行主程序：
```bash
python run.py
```

## 项目结构

```
mosoteach/
├── mosoteach/           # 主包目录
│   ├── __init__.py
│   ├── main.py         # 主程序入口
│   ├── config.py       # 配置文件
│   ├── core/           # 核心功能目录
│   │   ├── __init__.py
│   │   └── moso.py    # 慕课堂核心功能
│   └── utils/          # 工具函数目录
│       ├── __init__.py
│       └── tools.py    # 通用工具函数
├── config/             # 配置文件目录
│   └── config.example.yaml  # 配置文件模板
├── tests/              # 测试目录
│   └── test_tools.py   # 工具函数测试
├── run.py             # 启动脚本
├── requirements.txt    # 项目依赖
└── README.md          # 项目文档
```

## 开发指南

1. 代码风格遵循 PEP 8 规范
2. 所有函数和类都应该有文档字符串
3. 使用类型提示增强代码可读性
4. 保持适当的错误处理和日志记录

## 运行测试

```bash
python -m unittest discover tests
```

## 贡献指南

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

- 项目维护者：ubadly
- 邮箱：1577134779@qq.com
- 项目链接：https://github.com/ubadly/mosoteach
