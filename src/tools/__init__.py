"""15+ 原子化工具定义"""

import json, httpx
from src.config import VLLM_URL, LLM_MODEL


def _call_llm(prompt: str, temperature: float = 0) -> str:
    """统一调 14B API"""
    resp = httpx.post(
        f"{VLLM_URL}/chat/completions",
        json={
            "model": LLM_MODEL,
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
    return [{"title": f"{region}{keyword}招标公告", "url": "https://..."}]


def crawl_company_detail(company_name: str) -> str:
    return f"{company_name}的工商公开信息"


# ============================================================
# 实体抽取 & 问题结构化（统统走 14B）
# ============================================================

INSTRUCTION = "从以下政企文本中提取公司全称、注册资本、法定代表人、成立日期、经营范围、主体类型、风险等级、资产规模、是否获得政策支持。以JSON格式输出。"

def extract_entities(raw_text: str) -> dict:
    result = _call_llm(f"{INSTRUCTION}\n{raw_text}")
    return json.loads(result)


def extract_query_structured(question: str) -> dict:
    result = _call_llm(f"将以下问题转为结构化查询格式：{question}")
    return json.loads(result)


# ============================================================
# 规则引擎
# ============================================================

def apply_rule_engine(company: dict) -> dict:
    tags = {}
    capital = company.get("registered_capital", "0")
    cap_num = float(capital.replace("万元", "").replace(",", ""))
    if cap_num > 10000:
        tags["asset_scale"] = "大"
    elif cap_num > 500:
        tags["asset_scale"] = "中"
    else:
        tags["asset_scale"] = "小"
    return tags


# ============================================================
# RAG 检索
# ============================================================

def rag_search(query: str, top_k: int = 3) -> list[dict]:
    return [{"title": "农村土地承包法第三十三条", "content": "土地经营权流转应当依法、自愿、有偿...", "score": 0.92}]


def rag_precheck(company: dict) -> str:
    return "无明显红线"


# ============================================================
# 审核 & 报告
# ============================================================

def generate_report(state: dict) -> str:
    prompt = f"""
根据以下数据生成审核报告：
任务：{state['task']}
实体：{json.dumps(state['extracted_entities'], ensure_ascii=False)}
标签：{json.dumps(state['tags'], ensure_ascii=False)}
风险等级：{state['risk_level']}

请输出结构化报告，包含：基本信息、标签结果、合规状态、风险备注、推荐操作。
"""
    return _call_llm(prompt)