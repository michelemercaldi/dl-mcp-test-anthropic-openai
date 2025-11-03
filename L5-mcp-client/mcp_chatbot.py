import os
from dotenv import load_dotenv
from openai import AzureOpenAI
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from typing import List, Dict, Any
import json
import asyncio
import nest_asyncio

nest_asyncio.apply()
load_dotenv()

# we use Azure OpenAI in this chatbot

class MCP_ChatBot:
    def __init__(self):
        self.session: ClientSession = None
        api_key = os.environ["AZURE_OPENAI_API_KEY"]
        azure_endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
        api_version = os.environ["AZURE_OPENAI_API_VERSION"]
        self.llm = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=azure_endpoint,
        )
        self.available_tools: List[Dict[str, Any]] = []

    async def process_query(self, query: str):
        messages = [{"role": "user", "content": query}]

        response = self.llm.chat.completions.create(
            model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
            messages=messages,
            tools=self.available_tools,
        )

        process_query = True
        while process_query:
            message = response.choices[0].message
            assistant_content = message.content
            print(assistant_content)

            if message.tool_calls:
                messages.append({"role": "assistant", "content": assistant_content, "tool_calls": message.tool_calls})
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = tool_call.function.arguments
                    tool_id = tool_call.id

                    print(f"Calling tool {tool_name} with args {tool_args}")
                    tool_args_dict = json.loads(tool_args)

                    # Call the tool
                    result = await self.session.call_tool(tool_name, arguments=tool_args_dict)

                    messages.append(
                        {
                            "role": "tool",
                            "content": str(result.content),
                            "tool_call_id": tool_id,
                        }
                    )

                response = self.llm.chat.completions.create(
                    model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
                    messages=messages,
                    tools=self.available_tools,
                )
            else:
                process_query = False

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Chatbot Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()
                if query.lower() == "quit":
                    break
                await self.process_query(query)
            except Exception as e:
                print(f"\nError: {str(e)}")

    async def connect_to_server_and_run(self):
        server_params = StdioServerParameters(
            command="uv",
            args=["run", "L5-mcp-client\\research_server.py"],
            env=None,
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                self.session = session
                await session.initialize()
                response = await session.list_tools()
                tools = response.tools
                print("\nConnected to server with tools:", [tool.name for tool in tools])

                self.available_tools = [
                    {
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.inputSchema,
                        },
                    }
                    for tool in response.tools
                ]

                await self.chat_loop()

async def main():
    chatbot = MCP_ChatBot()
    await chatbot.connect_to_server_and_run()

if __name__ == "__main__":
    asyncio.run(main())
