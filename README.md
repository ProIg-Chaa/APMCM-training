# APMCM-training

## 项目开发使用要点

### 0. 前提
- 本项目使用Git进行版本控制，所有成员需要在本地安装Git。在练习阶段，所有成员一律使用dev分支进行开发。所有成员一律使用conda/micromamba/mamba进行环境管理。

### 1. 环境配置

- 本训练项目使用统一的环境配置文件，确保所有成员使用相同的环境（暂定）任何成员在修改环境后，都需要在 requirements.txt或environment.yaml 中更新环境配置。
### 2. 代码规范(代码尽量保持统一，文件名必须统一)

- 代码文件命名规范：使用下划线分隔单词，如 `my_model.py`。
- 函数和变量命名规范：使用小写字母和下划线，如 `my_function`。
- 类命名规范：使用首字母大写的驼峰命名法，如 `MyClass`。
  
### 3. 提交规范

- 提交前，确保代码已经通过测试。
- 提交前应该更新各个说明文档，例如data/README.md、README.md、experiment/log.txt等，当你修改或者添加了某一模块的代码或者文件，添加必要的说明。可随需要添加说明文件。
- 提交时，使用相应git命令。




# 项目结构
```none
├─README.md ← 项目说明文件（当前文件）
│
├─corecode/ ← 主要模型与算法代码（核心代码区）
│ └── utils/ ← 工具函数与配置文件（如数据加载、模型定义等）
│ 
│ 
│ 
│
├─data/ ← 数据存放区（原始数据与处理结果）
│ ├── raw/ ← 原始数据
│ ├── processed/ ← 预处理后数据
│ └── README.md ← 数据说明文档
│
├─experiments/ 
│ 
│ 
│
├─paper/ ← 论文撰写区（LaTeX 或 Markdown）
│ 
│ 
│ 
│ 
│
└─results/ ← 输出结果（图表、模型评估、结果总结）
├── figures/datafeature/
├── tables/
└── summary.txt
```


DAY 1:
每个人完成一道题目2024 C

1.参考优秀论文，看看优秀论文做了些什么 论文结构 数据可视化(matplotlib,matlab)
2.把实现代码放在仓库里边，根据代码分类放置