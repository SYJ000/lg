"""配置信息：服务器 vLLM 地址与模型映射"""

# 服务器 vLLM API 地址（远程）
VLLM_BASE_URL = "http://服务器IP:8000/v1"  # 部署后替换为实际IP

# 模型映射
LLM_MODEL = "qwen-14b"           # 14B 推理模型（Agent 大脑）
EXTRACT_MODEL = "qwen-lora"      # 7B 微调模型（实体抽取）
EMBEDDING_MODEL = "BAAI/bge-m3"  # 向量模型