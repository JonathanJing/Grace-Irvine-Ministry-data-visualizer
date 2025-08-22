# Grace Irvine Ministry Data Visualizer

用于读取 Google Sheet（总表 A,Q,R,S,T,U），清洗为标准事实/维度表，并使用 Streamlit 可视化。后端使用 Python（DuckDB 本地存储），未来可迁移到 Google Cloud Run + BigQuery。

## 快速开始（本地）

1. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```
2. 配置
   - 编辑 `configs/config.yaml`：确认 `spreadsheet_id`、`sheet_name`、列映射与时区
   - 准备 Google OAuth 凭据：将 `client_secret.json` 放入 `configs/`
3. 首次授权
   - 运行一次采集任务（后续命令 `python jobs/ingest_job.py`）：会弹出浏览器进行 Google 授权
4. 启动 Streamlit
   ```bash
   streamlit run app/ui.py
   ```

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

