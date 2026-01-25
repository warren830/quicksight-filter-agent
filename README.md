# QuickSight 智能账单查询 Agent

基于 Strands Agent SDK 构建的 AWS 账单智能查询系统。用户在 QuickSight 仪表板上点击数据点时，Agent 自动分析意图并调用合适的 AWS Cost Explorer API 返回 JSON 数据。

## 架构

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   QuickSight    │────▶│   前端应用       │────▶│   Agent API     │────▶│  AWS Cost       │
│   (用户点击)    │     │   (捕获事件)     │     │   (LLM 分析)    │     │  Explorer API   │
└─────────────────┘     └──────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
                                                 ┌─────────────────┐
                                                 │  LLM 决策:      │
                                                 │  1. 用哪个 API  │
                                                 │  2. 什么参数    │
                                                 │  3. 如何过滤    │
                                                 └─────────────────┘
```

## 工作流程

1. 用户在 QuickSight 仪表板点击某个数据点（如 EC2 柱状图）
2. 前端捕获点击事件，构造 JSON 发送给 Agent
3. LLM 分析用户意图，决定调用哪个 AWS API 及参数
4. Agent 执行 API 调用
5. 返回 JSON 格式的账单数据

## 安装

```bash
pip install strands-agents boto3
```

## 配置

### AWS 凭证
需要有 Cost Explorer 权限的 AWS 凭证：

```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_REGION=us-east-1
```

### Bedrock API Key（用于 LLM）
```bash
export AWS_BEDROCK_API_KEY=your_bedrock_api_key
```

### 所需 IAM 权限
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ce:GetCostAndUsage",
        "ce:GetCostForecast",
        "ce:GetDimensionValues",
        "ce:GetTags",
        "ce:GetReservationUtilization",
        "ce:GetSavingsPlansUtilization"
      ],
      "Resource": "*"
    }
  ]
}
```

## 使用方式

### 方式 1: 自然语言查询

```python
from agent import query

result = query("查询本月各个服务的成本")
print(result)
```

### 方式 2: QuickSight 事件

```python
from agent import process_quicksight_event

event = {
    "action": "drill_down",
    "visual_type": "bar_chart",
    "clicked_element": {
        "dimension": "SERVICE",
        "value": "Amazon EC2"
    },
    "current_filters": {
        "date_range": {"start": "2025-01-01", "end": "2025-01-25"}
    }
}

result = process_quicksight_event(event)
print(result)
```

### 方式 3: Lambda API

```bash
curl -X POST https://your-api/agent \
  -H "Content-Type: application/json" \
  -d '{"query": "查询本月 EC2 成本明细"}'
```

## QuickSight 集成

### 方案 A: Custom Actions（推荐）

1. 在 QuickSight 中创建 Custom Action
2. 配置 Action 触发 URL 或 iframe 通信
3. 在前端监听事件

```javascript
// QuickSight Embedding SDK
const dashboard = await embedDashboard({
    url: dashboardUrl,
    container: document.getElementById("dashboard"),
});

dashboard.on('CUSTOM_ACTION', async (event) => {
    const clickedData = {
        action: event.actionName,
        clicked_element: {
            dimension: event.dataPointSelection.columns[0].columnName,
            value: event.dataPointSelection.columns[0].value
        },
        current_filters: extractFilters(event.filterGroups)
    };
    
    const response = await fetch('/api/agent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quicksight_event: clickedData })
    });
    
    const result = await response.json();
    displayResult(result);
});
```

### 方案 B: Data Point Click 监听

```javascript
dashboard.on('DATA_POINT_CLICK', async (event) => {
    const clickedData = {
        visual_type: event.visualId,
        clicked_element: {
            dimension: event.dataPoint.column,
            value: event.dataPoint.value
        }
    };
    
    const result = await callAgent(clickedData);
    showDetailPanel(result);
});
```

## Agent 支持的 AWS API

| API | 用途 |
|-----|------|
| `get_cost_and_usage` | 查询成本和使用量 |
| `get_cost_forecast` | 成本预测 |
| `get_dimension_values` | 获取维度可用值 |
| `get_tags` | 获取可用标签 |
| `get_reservation_utilization` | 预留实例利用率 |
| `get_savings_plans_utilization` | Savings Plans 利用率 |

## 示例查询

### 按服务查询成本
```
用户: "查询本月各服务成本"

Agent 分析后调用:
- API: get_cost_and_usage
- GroupBy: SERVICE
- Granularity: MONTHLY
```

### 特定服务详情
```
用户点击: EC2 柱状图

Agent 分析后调用:
- API: get_cost_and_usage
- Filter: SERVICE = "Amazon EC2"
- GroupBy: USAGE_TYPE
- Granularity: DAILY
```

### 区域成本对比
```
用户: "对比各区域的成本"

Agent 分析后调用:
- API: get_cost_and_usage
- GroupBy: REGION
- Metrics: UnblendedCost
```

## 部署

### Lambda 部署

```python
# api_handler.py 作为 Lambda 入口
# Handler: api_handler.lambda_handler
```

### 环境变量
```
AWS_BEDROCK_API_KEY=xxx
```

## 文件结构

```
quicksight-filter-agent/
├── agent.py          # Agent 定义和主逻辑
├── tools.py          # AWS API 执行工具
├── api_handler.py    # Lambda 入口
├── config.py         # 配置
└── requirements.txt  # 依赖
```
