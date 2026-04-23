#!/usr/bin/env python3
"""
GitHub Trending AI Fetcher — fetch trending AI projects from OSSInsight API.

数据源：https://api.ossinsight.io/v1/trends/repos/?period=past_week

Usage:
    python fetch_github.py --max 10 --output github_news.json
"""

import argparse
import json
import os
import sys
from datetime import datetime

import requests

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OSSINSIGHT_API_URL = "https://api.ossinsight.io/v1/trends/repos/"

# AI 相关关键词（用于判断项目是否与 AI 相关）
AI_KEYWORDS = {
    # 核心 AI/ML 词汇
    "ai", "artificial intelligence", "machine learning", "ml", "deep learning",
    "neural network", "neural", "transformer", "diffusion", "llm",
    "large language model", "foundation model", "generative ai", "genai",

    # 大模型名称
    "gpt", "claude", "gemini", "llama", "mistral", "deepseek", "qwen",
    "chatglm", "baichuan", "internlm", "pangu", "ernie", "wenxin",
    "falcon", "phi", "orca", "vicuna", "alpaca", "koala", "mpt",
    "bloom", "gpt2", "gpt-3", "gpt-4", "gpt4", "gpt3", "t5", "bart",

    # 技术框架/库
    "pytorch", "tensorflow", "jax", "paddlepaddle", "mindspore",
    "huggingface", "transformers", "tokenizers", "accelerate",
    "langchain", "llamaindex", "autogpt", "autogen", "crewai",
    "openai", "anthropic", "cohere", "ai21", "replicate",

    # AI 应用领域
    "nlp", "natural language processing", "computer vision", "cv",
    "speech recognition", "tts", "text to speech", "text-to-speech",
    "image generation", "text to image", "text-to-image", "image-to-text",
    "multimodal", "vision language model", "vlm", "lmm",
    "rag", "retrieval augmented generation", "agent", "ai agent",
    "fine-tuning", "finetuning", "lora", "qlora", "peft",
    "embedding", "vector", "semantic search", "similarity",
    "stable diffusion", "sdxl", "midjourney", "dalle", "dall-e",
    "whisper", "wav2vec", "bert", "roberta", "electra", "deberta",

    # 模型优化/部署
    "quantization", "onnx", "tensorrt", "vllm", "text generation inference",
    "model serving", "model deployment", "inference", "optimization",

    # 数据集/评测
    "dataset", "benchmark", "evaluation", "eval",
}


def is_ai_related(repo_name: str, description: str) -> bool:
    """判断项目是否与 AI 相关（基于 repo_name 和 description）"""
    text = f"{repo_name} {description or ''}".lower()

    for keyword in AI_KEYWORDS:
        if keyword in text:
            return True
    return False


def fetch_github(max_items: int = 10, token: str = "") -> list[dict]:
    """
    从 OSSInsight API 获取 GitHub 趋势项目，筛选 AI 相关项目

    数据源：
        URL: https://api.ossinsight.io/v1/trends/repos/
        参数: period=past_week
        请求头: User-Agent=AI-News-Skill, Accept=application/json

    Args:
        max_items: 返回的最大项目数量（默认 10）
        token: GitHub token (kept for compatibility, not used by OSSInsight API)

    Returns:
        AI 相关项目的列表，每个项目包含 stars、forks、total_score 等字段
    """
    headers = {
        "User-Agent": "AI-News-Skill",
        "Accept": "application/json",
    }

    params = {
        "period": "past_week"
    }

    print(f"  [INFO] Fetching from OSSInsight API...", file=sys.stderr)
    print(f"  [INFO] URL: {OSSINSIGHT_API_URL}?period=past_week", file=sys.stderr)

    try:
        resp = requests.get(
            OSSINSIGHT_API_URL,
            params=params,
            headers=headers,
            timeout=30
        )

        if resp.status_code != 200:
            print(f"  [WARN] OSSInsight API returned status {resp.status_code}", file=sys.stderr)
            return []

        data = resp.json()

        # OSSInsight API 返回格式：{ "data": { "rows": [...] } }
        rows = data.get("data", {}).get("rows", [])

        if not rows:
            print(f"  [WARN] No data returned from OSSInsight API", file=sys.stderr)
            return []

        print(f"  [INFO] Got {len(rows)} total repos, filtering AI-related...", file=sys.stderr)

        # 筛选 AI 相关项目
        ai_projects = []
        for item in rows:
            repo_name = item.get("repo_name", "")
            description = item.get("description", "") or ""

            if is_ai_related(repo_name, description):
                ai_projects.append(item)

        print(f"  [INFO] Found {len(ai_projects)} AI-related projects", file=sys.stderr)

        # 取前 max_items 个
        selected = ai_projects[:max_items]

        # 构建输出格式
        items = []
        for item in selected:
            repo_name = item.get("repo_name", "")
            description = item.get("description", "") or ""
            language = item.get("primary_language", "") or "Unknown"

            # 构建 GitHub URL
            github_url = f"https://github.com/{repo_name}"

            # 获取字段：stars, forks, total_score
            stars = item.get("stars", 0)
            forks = item.get("forks", 0)
            total_score = item.get("total_score", 0)

            # 构建标题：仅使用 repo_name，不包含 description
            title = repo_name

            items.append({
                "title": title,
                "url": github_url,
                "source": "GitHub Trending",
                "region": "global",
                "summary": description or "AI项目",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "news_type": "github",
                # 核心展示字段
                "stars": stars,
                "forks": forks,
                "total_score": total_score,
                "primary_language": language,
                "description": description,
                # 额外信息
                "repo_name": repo_name,
            })

        return items

    except requests.exceptions.Timeout:
        print(f"  [WARN] OSSInsight API request timed out", file=sys.stderr)
        return []
    except requests.exceptions.RequestException as e:
        print(f"  [WARN] OSSInsight API request failed: {e}", file=sys.stderr)
        return []
    except json.JSONDecodeError as e:
        print(f"  [WARN] Failed to parse OSSInsight API response: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"  [WARN] Unexpected error: {e}", file=sys.stderr)
        return []


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Fetch GitHub Trending AI projects from OSSInsight")
    parser.add_argument("--max", type=int, default=10, help="Max projects to return (default: 10)")
    parser.add_argument("--token", default="", help="GitHub token (kept for compatibility, not used)")
    parser.add_argument("--output", help="Output JSON file (default: stdout)")
    args = parser.parse_args()

    print(f"Fetching GitHub Trending AI projects from OSSInsight (max: {args.max})...", file=sys.stderr)
    items = fetch_github(max_items=args.max)
    print(f"Got {len(items)} AI projects", file=sys.stderr)

    output = json.dumps(items, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Saved to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()