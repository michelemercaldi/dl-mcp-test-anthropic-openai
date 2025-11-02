

# MCP chatbot test for Anthropic and OpenAI

this exercise is a porting to Azure OpenAI of the short course
**MCP: Build Rich-Context AI Apps with Anthropic**
https://learn.deeplearning.ai/courses/mcp-build-rich-context-ai-apps-with-anthropic/lesson/fkbhh/introduction

for every lesson I reported the original version for Anthropic
and the custom version for Azure OpenAI



------------------------------------


activate environment
```
python -m venv .venv
.\.venv\Scripts\activate

```

install
```
pip install arxiv
pip install dotenv
pip install anthropic
pip install openai
```

run
```
python L3.openai.py
#   > show me firs article about water
```



--------------------------------



### using uv
```
pip install uv
uv init --name dl-mcp-server
uv venv
.venv\Scripts\activate
```

L4
```
uv add mcp arxiv
npx @modelcontextprotocol/inspector uv run .\L4-mcp_server-with-uv\research_server.py
```

L5
```
uv add openai python-dotenv nest_asyncio
uv run L5-mcp_client\mcp_chatbot.py
```

