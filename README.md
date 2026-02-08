# 基于城市功能区空间关系的交通流预测系统

## 项目简介

这是一个基于城市功能区空间关系的交通流预测系统，利用深度学习模型（LSTM、GRU）对城市交通流量进行预测。系统提供了完整的Web界面和API服务，支持全国城市的交通流预测、历史数据查询和模型配置等功能。

## 技术栈

### 后端技术
- **Python 3.8+**
- **FastAPI** - 高性能API框架
- **Flask** - Web前端服务
- **PyTorch** - 深度学习框架
- **MySQL** - 数据存储
- **SQLAlchemy** - ORM框架

### 深度学习模型
- **LSTM** - 长短期记忆网络
- **GRU** - 门控循环单元

### 数据处理
- **NumPy** - 数值计算
- **Pandas** - 数据处理
- **scikit-learn** - 机器学习工具

### 前端技术
- **HTML5/CSS3/JavaScript**
- **Bootstrap** - 响应式UI框架

## 项目结构

```
traffic_project/
├── backup/            # 数据库备份
├── configs/           # 配置文件
├── data/              # 数据存储
│   ├── models/        # 训练好的模型
│   ├── processed/     # 处理后的数据
│   └── raw/           # 原始数据
├── database/          # 数据库相关文件
├── logs/              # 日志文件
├── scripts/           # 辅助脚本
├── src/               # 源代码
│   ├── api/           # API路由
│   ├── data/          # 数据处理模块
│   ├── models/        # 模型定义
│   ├── models_db/     # 数据库模型
│   ├── prediction/    # 预测模块
│   ├── scripts/       # 训练脚本
│   ├── training/      # 训练模块
│   └── utils/         # 工具函数
├── static/            # 静态资源
├── templates/         # HTML模板
├── .env               # 环境变量
├── .gitignore         # Git忽略文件
├── app_web.py         # Web前端服务入口
├── fix_avatar_urls.sql # 数据库修复脚本
├── requirements.txt   # 依赖包
├── run_api.py         # API服务入口
└── setup.py           # 安装脚本
```

## 快速开始

### 环境要求

- Python 3.8+
- MySQL 5.7+

### 安装步骤

1. **克隆项目**

```bash
git clone <repository-url>
cd traffic_project
```

2. **安装依赖**

```bash
pip install -r requirements.txt
```

3. **配置数据库**

- 创建MySQL数据库
- 运行初始化脚本

```bash
mysql -u root -p < database/init.sql
```

4. **配置环境变量**

编辑 `.env` 文件，设置数据库连接信息等。

5. **启动服务**

- 启动API服务

```bash
python run_api.py
```

- 启动Web前端服务

```bash
python app_web.py
```

### 访问系统

- Web界面: http://127.0.0.1:5000
- API文档: http://127.0.0.1:8000/docs

## 使用说明

### 1. 用户认证

- **注册**：访问 `/register` 页面注册新账号
- **登录**：访问 `/login` 页面登录系统

### 2. 交通流预测

- **全国城市预测**：访问 `/input` 页面，输入城市信息和预测参数
- **查看结果**：预测完成后，系统会跳转到结果页面展示预测数据

### 3. 历史数据

- **查看历史**：访问 `/history` 页面查看历史预测数据

### 4. 个人中心

- **个人信息**：访问 `/profile` 页面查看和修改个人信息

### 5. 模型配置

- **模型参数**：访问 `/model-config` 页面配置模型参数

## 模型训练

### 训练默认模型

```bash
python src/scripts/train_model.py
```

### 训练特定模型

```bash
# 训练LSTM模型
python src/scripts/train_model.py --model lstm

# 训练GRU模型
python src/scripts/train_model.py --model gru
```

### 模型评估

训练完成后，模型会自动进行评估并保存最佳模型到 `data/models/best/` 目录。

## API文档

系统提供了完整的RESTful API，可通过以下方式访问：

- **Swagger UI**：http://127.0.0.1:8000/docs
- **ReDoc**：http://127.0.0.1:8000/redoc

### 主要API端点

- **认证**：`/api/auth/*` - 登录、注册、刷新令牌
- **预测**：`/api/predict/*` - 交通流预测
- **历史**：`/api/history/*` - 历史数据查询
- **用户**：`/api/user/*` - 用户信息管理

## 数据说明

### 原始数据

- **PEMS04**：PeMS (Performance Measurement System) 数据集，包含交通流量、速度等数据

### 数据预处理

1. **数据清洗**：处理缺失值和异常值
2. **特征工程**：提取时间特征、空间特征等
3. **数据标准化**：使用MinMaxScaler进行数据标准化

## 贡献指南

1. **Fork** 项目仓库
2. **创建** 新分支 (`git checkout -b feature/AmazingFeature`)
3. **提交** 更改 (`git commit -m 'Add some AmazingFeature'`)
4. **推送** 到分支 (`git push origin feature/AmazingFeature`)
5. **开启** Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 部署指南

### 本地部署

本地部署适用于开发和测试环境，步骤如下：

1. **环境准备**
   - 安装Python 3.8+
   - 安装MySQL 5.7+
   - 配置数据库连接

2. **启动服务**
   - 启动API服务：`python run_api.py`
   - 启动Web前端服务：`python app_web.py`

### Docker部署

Docker部署适用于生产环境，提供了更好的隔离性和可移植性。

1. **创建Dockerfile**

```Dockerfile
# 基础镜像
FROM python:3.8-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 暴露端口
EXPOSE 5000 8000

# 启动服务
CMD ["bash", "-c", "python run_api.py & python app_web.py"]
```

2. **构建镜像**

```bash
docker build -t traffic-prediction .
```

3. **运行容器**

```bash
docker run -d \
  --name traffic-prediction \
  -p 5000:5000 \
  -p 8000:8000 \
  -e DB_HOST=your-db-host \
  -e DB_USER=your-db-user \
  -e DB_PASSWORD=your-db-password \
  -e DB_NAME=your-db-name \
  traffic-prediction
```

### 云服务部署

可以部署到各种云服务平台，如AWS、阿里云、腾讯云等。

1. **AWS部署**
   - 使用EC2实例运行服务
   - 使用RDS作为数据库
   - 配置安全组开放端口

2. **阿里云部署**
   - 使用ECS实例运行服务
   - 使用RDS作为数据库
   - 配置安全组开放端口



## 致谢

- **PeMS**：提供交通流量数据集
- **PyTorch**：深度学习框架
- **FastAPI**：高性能API框架
- **Flask**：Web框架

感谢所有为项目做出贡献的开发者！