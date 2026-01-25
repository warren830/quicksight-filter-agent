"""AWS 账单智能查询 Agent - LLM 分析意图并决定调用哪个 API"""

from strands import Agent
from tools import execute_cost_explorer_api, execute_cloudwatch_api, execute_organizations_api

SYSTEM_PROMPT = """你是一个 AWS 账单分析专家。你的任务是：

1. 分析用户的查询意图（可能来自 QuickSight 点击事件或自然语言）
2. 决定需要调用哪个 AWS API
3. 构造正确的 API 参数
4. 执行 API 调用并返回 JSON 结果

## 可用的 AWS API

### Cost Explorer API (execute_cost_explorer_api)
- get_cost_and_usage: 查询成本和使用量
  参数示例:
  {
    "TimePeriod": {"Start": "2025-01-01", "End": "2025-01-31"},
    "Granularity": "MONTHLY",  // DAILY, MONTHLY, HOURLY
    "Metrics": ["UnblendedCost", "UsageQuantity"],
    "GroupBy": [{"Type": "DIMENSION", "Key": "SERVICE"}],  // 可选
    "Filter": {...}  // 可选
  }

- get_cost_forecast: 成本预测
  参数示例:
  {
    "TimePeriod": {"Start": "2025-02-01", "End": "2025-03-01"},
    "Metric": "UNBLENDED_COST",
    "Granularity": "MONTHLY"
  }

- get_dimension_values: 获取维度可用值
  参数示例:
  {
    "TimePeriod": {"Start": "2025-01-01", "End": "2025-01-31"},
    "Dimension": "SERVICE"  // SERVICE, REGION, LINKED_ACCOUNT, USAGE_TYPE 等
  }

- get_reservation_utilization: 预留实例利用率
- get_savings_plans_utilization: Savings Plans 利用率

### CloudWatch API (execute_cloudwatch_api)
- get_metric_statistics: 获取指标统计（如 EC2 CPU 使用率）
- list_metrics: 列出可用指标

### Organizations API (execute_organizations_api)
- list_accounts: 列出所有账户
- describe_account: 获取账户详情

## 常用 GroupBy 维度
- SERVICE: 按服务分组
- REGION: 按区域分组
- LINKED_ACCOUNT: 按账户分组
- USAGE_TYPE: 按使用类型分组
- INSTANCE_TYPE: 按实例类型分组
- OPERATION: 按操作类型分组

## 常用 Filter 示例
按服务过滤:
{
  "Dimensions": {
    "Key": "SERVICE",
    "Values": ["Amazon Elastic Compute Cloud - Compute"]
  }
}

按区域过滤:
{
  "Dimensions": {
    "Key": "REGION",
    "Values": ["us-east-1", "us-west-2"]
  }
}

组合过滤:
{
  "And": [
    {"Dimensions": {"Key": "SERVICE", "Values": ["Amazon EC2"]}},
    {"Dimensions": {"Key": "REGION", "Values": ["us-east-1"]}}
  ]
}

## 工作流程
1. 理解用户想要什么数据
2. 选择合适的 API
3. 构造正确的参数（日期格式: YYYY-MM-DD）
4. 调用工具执行 API
5. 返回 JSON 结果

始终返回 JSON 格式的数据。如果用户没有指定日期，使用最近 30 天。
"""


def create_agent():
    """创建账单分析 Agent"""
    return Agent(
        tools=[
            execute_cost_explorer_api,
            execute_cloudwatch_api,
            execute_organizations_api
        ],
        system_prompt=SYSTEM_PROMPT,
    )


def query(user_input: str) -> str:
    """处理用户查询"""
    agent = create_agent()
    response = agent(user_input)
    return str(response)


def process_quicksight_event(event: dict) -> str:
    """
    处理 QuickSight 点击事件
    
    event 示例:
    {
        "action": "drill_down",  # 用户动作
        "visual_type": "bar_chart",  # 图表类型
        "clicked_element": {
            "dimension": "SERVICE",
            "value": "Amazon EC2"
        },
        "current_filters": {
            "date_range": {"start": "2025-01-01", "end": "2025-01-25"},
            "region": "us-east-1"
        },
        "context": "月度成本概览仪表板"
    }
    """
    agent = create_agent()
    
    prompt = f"""
用户在 QuickSight 仪表板上进行了以下操作：

动作: {event.get('action', 'click')}
图表类型: {event.get('visual_type', 'unknown')}
点击元素: {event.get('clicked_element', {})}
当前过滤器: {event.get('current_filters', {})}
上下文: {event.get('context', '')}

请分析用户意图，决定需要调用哪个 AWS API 来获取相关数据，然后执行调用并返回 JSON 结果。
"""
    
    response = agent(prompt)
    return str(response)


if __name__ == "__main__":
    # 示例 1: 自然语言查询
    print("=" * 60)
    print("示例 1: 自然语言查询")
    print("=" * 60)
    result = query("查询本月各个服务的成本，按成本从高到低排序")
    print(result)
    
    # 示例 2: QuickSight 点击事件
    print("\n" + "=" * 60)
    print("示例 2: QuickSight 点击事件")
    print("=" * 60)
    event = {
        "action": "drill_down",
        "visual_type": "bar_chart",
        "clicked_element": {
            "dimension": "SERVICE",
            "value": "Amazon EC2"
        },
        "current_filters": {
            "date_range": {"start": "2025-01-01", "end": "2025-01-25"}
        },
        "context": "想看 EC2 的详细成本分解"
    }
    result = process_quicksight_event(event)
    print(result)
