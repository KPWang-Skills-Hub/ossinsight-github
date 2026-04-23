# ossinsight-github — GitHub AI 项目趋势数据

通过 OSSInsight API 获取 GitHub 趋势项目中的 AI 相关热门仓库。

**数据源：** OSSInsight API
**API 地址：** `https://api.ossinsight.io/v1/trends/repos/`
**查询参数：** `?period=past_week`
**请求头：**
```
User-Agent: AI-News-Skill
Accept: application/json
```

## 核心逻辑

1. 调用 OSSInsight `/v1/trends/repos/?period=past_week` 获取过去一周所有 GitHub 趋势
2. 用 80+ 个 AI 关键词过滤出 AI 相关项目（匹配 repo_name + description）
3. 返回趋势分（total_score）最高的项目

## AI 关键词示例

- 核心：`ai`, `machine learning`, `deep learning`, `llm`, `transformer`, `diffusion`, `generative ai`
- 大模型：`gpt`, `llama`, `deepseek`, `qwen`, `chatglm`, `mistral`, `claude`, `gemini`
- 框架：`pytorch`, `tensorflow`, `huggingface`, `langchain`, `vllm`, `autogen`
- 应用：`rag`, `agent`, `nlp`, `cv`, `multimodal`, `text-to-image`, `tts`
- 技术：`lora`, `quantization`, `embedding`, `onnx`

## 输出字段

```json
{
  "title": "owner/repo-name",
  "url": "https://github.com/owner/repo-name",
  "source": "GitHub Trending",
  "region": "global",
  "summary": "项目描述",
  "date": "2026-03-29",
  "news_type": "github",
  "stars": 1234,
  "forks": 567,
  "total_score": 9999.99,
  "primary_language": "Python",
  "description": "项目描述",
  "repo_name": "owner/repo-name"
}
```

## 快速测试

```bash
cd ~/.openclaw/workspace/skills/ossinsight-github
python scripts/fetch_github.py --max 10 --output /tmp/github_ai.json
cat /tmp/github_ai.json
```

## 更新关键词

编辑 `config/keywords.json` 调整 AI 关键词列表。