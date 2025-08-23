# Grace Irvine Ministry Data Visualizer

用于读取 Google Sheet（总表 A,Q,R,S,T,U），清洗为标准事实/维度表，并使用 Streamlit 可视化。后端使用 Python（DuckDB 本地存储），未来可迁移到 Google Cloud Run + BigQuery。

## 快速开始（本地）

### 1. 设置虚拟环境
```bash
# 创建并激活虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置 Google Sheets 认证（Service Account）
```bash
# 运行服务账号设置助手
python setup_service_account.py

# 手动设置步骤：
# 1. 在 Google Cloud Console 创建服务账号
# 2. 下载 JSON 密钥文件
# 3. 重命名为 service_account.json
# 4. 放入 configs/ 目录
# 5. 在 Google Sheets 中与服务账号邮箱共享
```

### 3. 启动应用
```bash
# 使用脚本启动（推荐）
./run_app.sh

# 或者手动启动
python -m streamlit run app/ui.py
```

### 4. 测试连接
- 在应用中点击"手动刷新（读取 Google Sheet）"
- 无需浏览器认证（使用服务账号）
- 数据会自动从 Google Sheets 读取

## 目录结构
```
app/                # Streamlit UI
ingest/             # Google Sheets 抽取、转换、入库
storage/            # DuckDB/BigQuery 存储与 Schema
metrics/            # 聚合查询与指标
jobs/               # 定时作业入口
infra/              # Docker/部署脚本
configs/            # 配置与本地凭据
```

## 部署（Cloud Run 预留）
- 使用 `Dockerfile` 构建镜像
- 使用服务账号访问 Google Sheets / BigQuery
- 使用 Cloud Scheduler 触发 Cloud Run Job 执行采集

> 列 A 为日期，Q,R,S,T,U 为人员列；每个非空单元格代表该日该类型的一次服事记录。

