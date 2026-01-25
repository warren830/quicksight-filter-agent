"""Lambda Handler - QuickSight 调用入口"""

import json
from agent import query, process_quicksight_event


def lambda_handler(event, context):
    """
    请求格式:
    1. 自然语言: {"query": "查询本月 EC2 成本"}
    2. QuickSight 事件: {"quicksight_event": {...}}
    """
    try:
        body = json.loads(event.get("body", "{}")) if isinstance(event.get("body"), str) else event
        
        if "query" in body:
            result = query(body["query"])
        elif "quicksight_event" in body:
            result = process_quicksight_event(body["quicksight_event"])
        else:
            return {"statusCode": 400, "body": json.dumps({"error": "需要 query 或 quicksight_event"})}
        
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"success": True, "result": result}, ensure_ascii=False)
        }
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
