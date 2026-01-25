"""AWS 账单 API 执行工具 - Agent 分析后调用"""

import json
import boto3
from strands import tool


@tool
def execute_cost_explorer_api(api_name: str, parameters: str) -> str:
    """执行 AWS Cost Explorer API 调用。
    
    根据 Agent 分析的结果，调用对应的 Cost Explorer API。
    
    Args:
        api_name: API 名称，支持:
            - get_cost_and_usage: 获取成本和使用量
            - get_cost_forecast: 获取成本预测
            - get_dimension_values: 获取维度可用值
            - get_tags: 获取可用标签
            - get_reservation_utilization: 获取预留实例利用率
            - get_savings_plans_utilization: 获取 Savings Plans 利用率
        parameters: JSON 格式的 API 参数
    
    Returns:
        JSON 格式的 API 响应
    """
    try:
        ce = boto3.client('ce', region_name='us-east-1')
        params = json.loads(parameters)
        
        api_map = {
            'get_cost_and_usage': ce.get_cost_and_usage,
            'get_cost_forecast': ce.get_cost_forecast,
            'get_dimension_values': ce.get_dimension_values,
            'get_tags': ce.get_tags,
            'get_reservation_utilization': ce.get_reservation_utilization,
            'get_savings_plans_utilization': ce.get_savings_plans_utilization,
        }
        
        if api_name not in api_map:
            return json.dumps({"error": f"不支持的 API: {api_name}"}, ensure_ascii=False)
        
        response = api_map[api_name](**params)
        
        # 移除不可序列化的元数据
        if 'ResponseMetadata' in response:
            del response['ResponseMetadata']
        
        return json.dumps(response, ensure_ascii=False, default=str, indent=2)
    
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@tool  
def execute_cloudwatch_api(api_name: str, parameters: str) -> str:
    """执行 AWS CloudWatch API 调用（用于获取使用量指标）。
    
    Args:
        api_name: API 名称，支持:
            - get_metric_statistics: 获取指标统计
            - list_metrics: 列出可用指标
        parameters: JSON 格式的 API 参数
    
    Returns:
        JSON 格式的 API 响应
    """
    try:
        cw = boto3.client('cloudwatch')
        params = json.loads(parameters)
        
        api_map = {
            'get_metric_statistics': cw.get_metric_statistics,
            'list_metrics': cw.list_metrics,
        }
        
        if api_name not in api_map:
            return json.dumps({"error": f"不支持的 API: {api_name}"}, ensure_ascii=False)
        
        response = api_map[api_name](**params)
        
        if 'ResponseMetadata' in response:
            del response['ResponseMetadata']
        
        return json.dumps(response, ensure_ascii=False, default=str, indent=2)
    
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@tool
def execute_organizations_api(api_name: str, parameters: str) -> str:
    """执行 AWS Organizations API 调用（用于获取账户信息）。
    
    Args:
        api_name: API 名称，支持:
            - list_accounts: 列出所有账户
            - describe_account: 获取账户详情
        parameters: JSON 格式的 API 参数
    
    Returns:
        JSON 格式的 API 响应
    """
    try:
        org = boto3.client('organizations')
        params = json.loads(parameters) if parameters else {}
        
        api_map = {
            'list_accounts': org.list_accounts,
            'describe_account': org.describe_account,
        }
        
        if api_name not in api_map:
            return json.dumps({"error": f"不支持的 API: {api_name}"}, ensure_ascii=False)
        
        response = api_map[api_name](**params)
        
        if 'ResponseMetadata' in response:
            del response['ResponseMetadata']
        
        return json.dumps(response, ensure_ascii=False, default=str, indent=2)
    
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
