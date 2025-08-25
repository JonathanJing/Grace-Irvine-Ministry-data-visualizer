# Grace Irvine 媒体部事工数据可视化分析平台

一个现代化的教会事工管理与数据分析平台，专为Grace Irvine教会媒体部设计。通过智能数据清洗、深度分析和交互式可视化，帮助事工领袖更好地了解同工参与模式，优化事工安排，提升服事效果。

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.37.0-red.svg)
![DuckDB](https://img.shields.io/badge/DuckDB-1.0.0-yellow.svg)
![Google Sheets](https://img.shields.io/badge/Google%20Sheets-API-green.svg)
![Cloud Run](https://img.shields.io/badge/Cloud%20Run-Ready-blue.svg)

## ✨ 核心功能特色

### 📊 智能数据分析
- **总体概况分析**: 时间范围、参与率、负担分布等关键指标
- **同工排行榜**: 最近4周和季度的活跃度排名对比
- **增减分析**: 同工新增/离开趋势和环比变化分析
- **事工流动**: 桑基图展示同工在不同事工间的流动模式
- **参与统计**: 详细的同工参与频率和类型分布

### 🔄 自动化数据管道
- **实时数据同步**: 通过Google Sheets API自动获取最新数据
- **智能数据清洗**: 自动处理重复记录、标准化名称、时间窗口验证
- **增量式更新**: 支持快速增量数据更新，避免重复处理
- **数据完整性保证**: 多层校验确保数据质量和一致性

### 📈 高级可视化设计
- **交互式图表**: 基于Plotly的丰富交互体验
- **多维度分析**: 时间、人员、事工类型等多角度数据透视
- **智能洞察**: 自动生成数据洞察和趋势分析
- **响应式设计**: 适配不同屏幕尺寸的现代化UI

## 🏗️ 技术架构设计

### 数据流架构
```
Google Sheets → 数据提取 → 清洗转换 → DuckDB存储 → 聚合计算 → Streamlit展示
     ↓              ↓         ↓         ↓         ↓         ↓
   原始表格      API读取    标准化     本地数据库   统计查询   交互界面
```

### 核心技术栈
- **前端界面**: Streamlit - 快速构建数据应用
- **数据存储**: DuckDB - 高性能分析型数据库
- **数据可视化**: Plotly - 交互式图表库
- **数据处理**: Pandas - 数据操作和分析
- **API集成**: Google Sheets API - 数据源连接
- **部署平台**: Google Cloud Run - 无服务器容器部署

### 数据模型设计
```sql
-- 核心事实表
service_fact: 记录每次服事
├── fact_id (主键)
├── volunteer_id (同工ID) 
├── service_type_id (事工类型)
├── service_date (服事日期)
└── source_row_id (数据溯源)

-- 维度表
date_dim: 日期维度 (年/季度/月)
volunteer: 同工信息
service_type: 事工类型定义
```

## 🧮 智能数据清洗流程

### 1. 原始数据提取
```python
# 从Google Sheets读取A-U列数据
raw_data = sheets_client.read_range_a_to_u()
```

### 2. 数据标准化处理
- **日期解析**: 智能识别多种日期格式
- **姓名标准化**: 去除空格、统一编码格式
- **重复记录处理**: 基于日期+同工+事工的去重逻辑
- **数据溯源**: 为每条记录生成唯一标识用于追踪

### 3. 业务规则应用
```yaml
# 配置文件示例 (config.yaml)
columns:
  date: "A"  # 日期列
  roles:     # 事工角色定义
    - key: "Q"
      service_type: "音控"
    - key: "R" 
      service_type: "导播"
      valid_until_row: 69  # 行有效性窗口
```

### 4. 质量检查与验证
- **数据完整性**: 检查必填字段
- **时间范围验证**: 确保日期在合理范围内
- **业务逻辑校验**: 应用事工特定的验证规则

## 🎨 可视化设计思路

### 设计原则
1. **用户体验优先**: 直观易懂的界面设计
2. **数据驱动洞察**: 不仅展示数据，更提供分析见解
3. **交互式探索**: 支持用户自主筛选和深入分析
4. **美观现代**: 采用现代设计语言和配色方案

### 关键可视化组件

#### 📊 总体概况仪表板
```python
# 核心KPI展示
- 数据时间范围和记录总数
- 同工活跃率(饼图+名单)
- 参与负担分布(箱型图+Top10柱状图)
- 事工类别分布(环形图)
- 月度活动趋势(双轴图)
```

#### 🏆 同工排行榜
```python
# 双时间段对比分析
create_volunteer_ranking_chart()
├── 最近4周排行(金银铜配色)
├── 最近季度排行
└── 对比分析图表
```

#### 🌊 事工流动桑基图
```python
# 复杂流动关系可视化
create_volunteer_ministry_flow_sankey()
├── 月份-事工节点
├── 同工流动连线
├── 流动强度表示
└── 悬停详情展示
```

### 交互设计特色
- **智能筛选**: 多维度过滤器
- **实时计算**: 即时响应用户操作
- **数据下载**: 支持CSV导出
- **详情展开**: 可展开查看明细数据

## ☁️ 云端部署方案

### 部署架构
```
Internet → Cloud Load Balancer → Cloud Run Service
                                      ↓
                              Container Instance
                                      ↓
                              Streamlit App + DuckDB
                                      ↓
                              Google Sheets API
```

### 自动化部署流程

#### 1. 容器化配置
```dockerfile
# 多阶段构建优化
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["streamlit", "run", "app/ui.py", "--server.port=8080"]
```

#### 2. 一键部署脚本
```bash
# deploy_cloud_run.sh - 完全自动化部署
./infra/deploy_cloud_run.sh
├── 设置Google Cloud项目
├── 启用必要的API服务
├── 构建并推送容器镜像
├── 部署到Cloud Run
└── 配置服务访问权限
```

#### 3. 环境配置
```bash
# 环境变量设置
export PROJECT_ID="your-project-id"
export REGION="us-central1" 
export SERVICE_NAME="ministry-visualizer"

# 服务账号认证
GOOGLE_APPLICATION_CREDENTIALS=/app/configs/service_account.json
```

### 生产环境优化
- **自动扩缩容**: 根据流量自动调整实例数量
- **高可用性**: 多区域部署提高可靠性
- **监控告警**: Cloud Monitoring集成
- **成本优化**: 按需付费，空闲时自动缩容至0

## 🚀 快速开始

### 本地开发环境设置

#### 1. 环境准备
```bash
# 克隆项目
git clone <repository-url>
cd Grace-Irvine-Ministry-data-visualizer

# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

#### 2. Google Sheets认证配置
```bash
# 方式一: 使用服务账号(推荐)
# 1. 在Google Cloud Console创建服务账号
# 2. 下载JSON密钥文件并重命名为service_account.json
# 3. 放置到configs/目录下
# 4. 在Google Sheets中与服务账号邮箱共享表格

# 方式二: 运行自动化设置(如果可用)
python setup_service_account.py
```

#### 3. 配置文件设置
```yaml
# configs/config.yaml
spreadsheet_id: "你的Google表格ID"
sheet_name: "总表"
columns:
  date: "A"
  roles:
    - key: "Q"
      service_type: "音控"
    # 更多角色配置...
```

#### 4. 启动应用
```bash
# 使用便捷脚本
./run_app.sh

# 或手动启动
streamlit run app/ui.py

# 浏览器访问: http://localhost:8501
```

### 云端部署

#### 一键部署到Google Cloud Run
```bash
# 设置项目ID
export PROJECT_ID="your-google-cloud-project-id"

# 执行部署脚本
./infra/deploy_cloud_run.sh

# 部署完成后会显示访问URL
```

## 📁 项目结构详解

```
Grace-Irvine-Ministry-data-visualizer/
├── app/                      # 前端应用
│   ├── ui.py                # Streamlit主界面
│   └── visualizations.py   # 图表可视化组件
├── ingest/                  # 数据摄取模块
│   ├── sheets_client.py     # Google Sheets客户端
│   └── transform.py         # 数据转换逻辑
├── storage/                 # 数据存储层
│   └── duckdb_store.py     # DuckDB数据访问对象
├── metrics/                 # 数据聚合分析
│   └── aggregations.py     # 统计查询函数
├── jobs/                    # 任务调度
│   └── ingest_job.py       # 数据摄取任务
├── configs/                 # 配置文件
│   ├── config.yaml         # 主配置文件
│   └── service_account.json # Google服务账号密钥
├── infra/                   # 基础设施
│   ├── Dockerfile          # 容器构建文件
│   └── deploy_cloud_run.sh # 部署脚本
├── data/                    # 本地数据存储
└── docs/                    # 文档资料
```

## 🔧 高级功能配置

### 自定义分析维度
```python
# 在metrics/aggregations.py中添加新的分析函数
def load_custom_analysis():
    """自定义分析逻辑"""
    # 实现你的分析需求
```

### 扩展可视化组件
```python
# 在app/visualizations.py中添加新图表
def create_custom_chart(df):
    """创建自定义图表"""
    # 使用Plotly构建图表
```

### 数据源扩展
- 支持多个Google Sheets
- 集成其他数据源(CSV, 数据库等)
- 实时数据流处理

## 🤝 贡献指南

### 开发流程
1. Fork项目到你的GitHub账户
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开Pull Request

### 代码规范
- 遵循PEP 8 Python编码规范
- 添加适当的文档字符串
- 编写必要的测试用例
- 保持代码简洁易读

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🆘 支持与帮助

### 常见问题
- **Q: 无法连接Google Sheets?**
  A: 检查服务账号配置和表格共享权限

- **Q: 数据显示不完整?**
  A: 确认config.yaml中的列配置正确

- **Q: 部署失败?**
  A: 检查Google Cloud项目权限和API启用状态

### 获取帮助
- 查看 [文档目录](docs/) 中的详细指南
- 提交 [Issue](../../issues) 报告问题
- 联系项目维护者

---

📧 **联系信息**: 如有任何疑问或建议，欢迎通过GitHub Issues联系我们。

🎯 **项目目标**: 通过数据驱动的方式，帮助教会更好地管理和优化事工安排，提升服事效果和同工参与度。