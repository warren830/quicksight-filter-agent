"""配置文件 - AWS 账单数据源和过滤选项"""

# 支持的 AWS Cost Explorer 维度
COST_DIMENSIONS = {
    "SERVICE": "AWS 服务（如 EC2, S3, Lambda）",
    "LINKED_ACCOUNT": "关联账户 ID",
    "REGION": "AWS 区域",
    "USAGE_TYPE": "使用类型",
    "INSTANCE_TYPE": "实例类型（EC2）",
    "OPERATION": "操作类型",
    "PURCHASE_TYPE": "购买类型（按需、预留、Spot）",
    "RECORD_TYPE": "记录类型",
    "RESOURCE_ID": "资源 ID",
    "TAG": "成本分配标签"
}

# 支持的聚合粒度
GRANULARITY_OPTIONS = ["DAILY", "MONTHLY", "HOURLY"]

# 支持的指标
METRICS = {
    "UnblendedCost": "未混合成本（实际支付）",
    "BlendedCost": "混合成本",
    "AmortizedCost": "摊销成本（含预留）",
    "NetUnblendedCost": "净未混合成本",
    "NetAmortizedCost": "净摊销成本",
    "UsageQuantity": "使用量",
    "NormalizedUsageAmount": "标准化使用量"
}

# 常用服务名称映射
SERVICE_NAMES = {
    "ec2": "Amazon Elastic Compute Cloud - Compute",
    "s3": "Amazon Simple Storage Service",
    "rds": "Amazon Relational Database Service",
    "lambda": "AWS Lambda",
    "dynamodb": "Amazon DynamoDB",
    "cloudfront": "Amazon CloudFront",
    "sagemaker": "Amazon SageMaker",
    "bedrock": "Amazon Bedrock",
    "eks": "Amazon Elastic Kubernetes Service",
    "ecs": "Amazon Elastic Container Service"
}
