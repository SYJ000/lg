"""15+ 原子化工具定义"""

import json, httpx
from src.config import VLLM_BASE_URL, EXTRACT_MODEL, LLM_MODEL

# ============================================================
# 工具基类：统一调用 vLLM API
# ============================================================

def _call_vllm(model: str, prompt: str, temperature: float = 0) -> str:
    """调用远程 vLLM API（部署在服务器 GPU 7 上）"""
    resp = httpx.post(
        f"{VLLM_BASE_URL}/chat/completions",
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": 1024,
        },
        timeout=60,
    )
    return resp.json()["choices"][0]["message"]["content"]


# ============================================================
# 数据采集工具
# ============================================================

def crawl_procurement(keyword: str, region: str) -> list[dict]:
    """采集招标公告（模拟/预留接口，实际对接具体网站）"""
    # 实际项目中这里用 requests/Scrapy
    return [{"title": f"{region}{keyword}招标公告", "url": "https://..."}]


def crawl_company_detail(company_name: str) -> str:
    """采集公司详情页"""
    return f"{company_name}的工商公开信息"


# ============================================================
# 实体抽取工具（调 7B 微调模型）
# ============================================================

INSTRUCTION = "从以下政企文本中提取公司全称、注册资本、法定代表人、成立日期、经营范围、主体类型、风险等级、资产规模、是否获得政策支持。以JSON格式输出。"

def extract_entities(raw_text: str) -> dict:
    """调 7B 微调模型做结构化抽取"""
    result = _call_vllm(EXTRACT_MODEL, f"{INSTRUCTION}\n{raw_text}")
    return json.loads(result)


def extract_query_structured(question: str) -> dict:
    """调 7B 微调模型将自然语言问题结构化"""
    result = _call_vllm(EXTRACT_MODEL, f"将以下问题转为结构化查询格式：{question}")
    return json.loads(result)


# ============================================================
# 规则引擎工具
# ============================================================

def apply_rule_engine(company: dict) -> dict:
    """规则引擎打标"""
    tags = {}
    capital = company.get("registered_capital", "0")

    # 资产规模
    cap_num = float(capital.replace("万元", "").replace(",", ""))
    if cap_num > 10000:
        tags["asset_scale"] = "大"
    elif cap_num > 500:
        tags["asset_scale"] = "中"
    else:
        tags["asset_scale"] = "小"

    return tags


def entity_alignment(entities: list) -> list:
    """多源数据实体对齐"""
    return entities  # 简化：实际需要模糊匹配


# ============================================================
# RAG 检索工具
# ============================================================

def rag_search(query: str, top_k: int = 3) -> list[dict]:
    """RAG 政策知识库检索（调远程 Milvus 或 API）"""
    # 实际项目中调 Milvus + BGE-Reranker
    return [{"title": "农村土地承包法第三十三条", "content": "...", "score": 0.92}]


def rag_precheck(company: dict) -> str:
    """合规预检"""
    results = rag_search(f"{company.get('company_name','')} 合规审查")
    return results[0]["content"] if results else "无明显红线"


# ============================================================
# 审核工具
# ============================================================

def assess_risk_level(company: dict) -> str:
    """风险等级判定"""
    if company.get("risk_level") == "高":
        return "high"
    return "low"


def generate_report(state: dict) -> str:
    """14B 模型生成审核报告"""
    prompt = f"""
根据以下数据生成审核报告：
任务：{state['task']}
实体：{json.dumps(state['extracted_entities'], ensure_ascii=False)}
标签：{json.dumps(state['tags'], ensure_ascii=False)}
风险等级：{state['risk_level']}

请输出结构化报告，包含：基本信息、标签结果、合规状态、风险备注、推荐操作。
"""
    return _call_vllm(LLM_MODEL, prompt)