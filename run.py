"""项目根目录入口：直接 python run.py 即可"""

from src.main import run_prospecting_task

if __name__ == "__main__":
    result = run_prospecting_task("帮我找重庆的农业科技企业")
    print("最终报告：")
    print(result.get("report", "未生成报告"))
    print(f"\n是否需要人工审批：{result.get('human_review_required')}")