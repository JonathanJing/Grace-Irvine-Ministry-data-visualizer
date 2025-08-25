# 🚀 Google Cloud Run 部署指南

## 📋 部署前准备

### 1. 确保本地环境设置完成
- ✅ 已有 `configs/service_account.json` 文件
- ✅ 应用可以在本地正常运行
- ✅ Google Sheets 数据访问正常

### 2. Google Cloud 账户和项目设置

#### 2.1 登录 Google Cloud
```bash
gcloud auth login
```

#### 2.2 创建新项目（或使用现有项目）
```bash
# 创建新项目
gcloud projects create ministry-data-visualizer-2024 --name="Ministry Data Visualizer"

# 或者列出现有项目
gcloud projects list
```

#### 2.3 设置项目 ID
```bash
export PROJECT_ID=ministry-data-visualizer-2024  # 替换为你的项目 ID
gcloud config set project $PROJECT_ID
```

#### 2.4 启用计费（必需）
- 访问 [Google Cloud Console](https://console.cloud.google.com)
- 选择你的项目
- 导航到 "计费" -> 启用计费账户

## 🚀 自动部署

### 使用部署脚本
```bash
# 设置项目 ID（替换为你的实际项目 ID）
export PROJECT_ID=ministry-data-visualizer-2024

# 运行部署脚本
./infra/deploy_cloud_run.sh
```

部署脚本会自动：
1. 设置 Google Cloud 项目
2. 启用必需的 API（Cloud Build, Cloud Run）
3. 构建 Docker 镜像
4. 部署到 Cloud Run
5. 显示应用 URL

## 🔧 手动部署步骤

如果需要手动控制部署过程：

### 1. 启用 API
```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
```

### 2. 构建镜像
```bash
cd infra
gcloud builds submit --tag gcr.io/$PROJECT_ID/ministry-visualizer:latest ..
```

### 3. 部署到 Cloud Run
```bash
gcloud run deploy ministry-visualizer \
  --region us-central1 \
  --image gcr.io/$PROJECT_ID/ministry-visualizer:latest \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 10 \
  --set-env-vars=STREAMLIT_SERVER_HEADLESS=true,GOOGLE_APPLICATION_CREDENTIALS=/app/configs/service_account.json
```

## 📊 部署后检查

### 1. 获取应用 URL
```bash
gcloud run services describe ministry-visualizer --region=us-central1 --format="value(status.url)"
```

### 2. 查看日志
```bash
gcloud logs tail --service=ministry-visualizer
```

### 3. 测试应用
访问应用 URL，确保：
- ✅ 页面正常加载
- ✅ 可以点击 "手动刷新（读取 Google Sheet）"
- ✅ 数据正常显示和可视化

## 🔄 更新部署

要更新已部署的应用：

```bash
# 重新运行部署脚本
export PROJECT_ID=your-project-id
./infra/deploy_cloud_run.sh
```

## 🛠️ 故障排除

### 常见问题

1. **权限错误**
   ```bash
   # 确保已登录并设置项目
   gcloud auth login
   gcloud config set project $PROJECT_ID
   ```

2. **API 未启用**
   ```bash
   # 手动启用 API
   gcloud services enable cloudbuild.googleapis.com run.googleapis.com
   ```

3. **内存不足**
   - 在部署时增加内存：`--memory 2Gi`

4. **超时问题**
   - 增加超时时间：`--timeout 900`

### 查看详细日志
```bash
# 实时日志
gcloud logs tail --service=ministry-visualizer --follow

# 特定时间范围的日志
gcloud logs read --service=ministry-visualizer --limit=50
```

## 💰 成本估算

Cloud Run 定价：
- **CPU**: $0.00002400 每 vCPU 每秒
- **内存**: $0.00000250 每 GB 每秒
- **请求**: $0.40 每百万请求

预估月度成本（中等使用）：$5-20 USD

## 🔐 安全注意事项

1. **服务账户权限**: 确保服务账户只有必需的权限
2. **网络访问**: 考虑是否需要添加认证
3. **数据隐私**: 确保 Google Sheet 数据访问权限合适

## 📞 支持

如遇问题，请检查：
1. Google Cloud Console 中的部署状态
2. Cloud Build 构建日志
3. Cloud Run 服务日志
