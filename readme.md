

# MCP chatbot test for Anthropic and OpenAI

this exercise is a porting to Azure OpenAI of the short course
**MCP: Build Rich-Context AI Apps with Anthropic**
https://learn.deeplearning.ai/courses/mcp-build-rich-context-ai-apps-with-anthropic/lesson/fkbhh/introduction

for every lesson I reported the original version for Anthropic
and the custom version for Azure OpenAI


see mcp
https://github.com/modelcontextprotocol

mcp servers
https://github.com/modelcontextprotocol/servers



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

### L4
```
uv add mcp arxiv
npx @modelcontextprotocol/inspector uv run .\L4-mcp_server-with-uv\research_server.py
```

### L5
```
uv add openai python-dotenv nest_asyncio
uv run L5-mcp-client\mcp_chatbot.py
```

### L6
see mcp servers list  https://github.com/modelcontextprotocol/servers
    we use fetch server and filesystem server
```
uv run .\L6-multi-client-server\mcp_chatbot.py
```
sample prompts:
- list files in current dir

- fetch the website https://fubardevelopment.github.io/WebDavServer/articles/getting-started.html ,  create a visual summary and save it in a summary.md


### L7
```
uv run .\L7-prompt-resources\mcp_chatbot.py
```
- prompts:
/prompts
/prompt generate_search_prompt topic=math
@folders