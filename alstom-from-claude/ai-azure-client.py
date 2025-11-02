"""
AI Agent Client for Train Production
Integrates MCP tools with Azure OpenAI (or local LLM)
"""

import asyncio
from typing import List, Dict, Any
from openai import AsyncAzureOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import json

# ============================================================================
# AGENT CONFIGURATION
# ============================================================================

class AgentConfig:
    """Configuration for the AI agent"""
    
    # Azure OpenAI settings
    AZURE_ENDPOINT = "https://your-resource.openai.azure.com/"
    AZURE_API_KEY = "your-api-key"
    AZURE_DEPLOYMENT = "gpt-4"  # or your deployment name
    AZURE_API_VERSION = "2024-02-15-preview"
    
    # Alternative: Local LLM settings (e.g., Ollama, LM Studio)
    LOCAL_LLM_URL = "http://localhost:11434"
    LOCAL_MODEL = "llama2"
    
    # MCP Server settings
    MCP_SERVER_SCRIPT = "train_production_server.py"
    MCP_SERVER_ARGS = []


# ============================================================================
# AGENT ORCHESTRATOR
# ============================================================================

class TrainProductionAgent:
    """Main agent that orchestrates between LLM and MCP tools"""
    
    def __init__(self, use_azure: bool = True):
        self.use_azure = use_azure
        self.llm_client = None
        self.mcp_session = None
        self.available_tools = []
        self.conversation_history = []
    
    async def initialize(self):
        """Initialize LLM and MCP connections"""
        
        # Initialize LLM
        if self.use_azure:
            self.llm_client = AsyncAzureOpenAI(
                azure_endpoint=AgentConfig.AZURE_ENDPOINT,
                api_key=AgentConfig.AZURE_API_KEY,
                api_version=AgentConfig.AZURE_API_VERSION
            )
        else:
            # For local LLM, you'd use a different client
            # e.g., LiteLLM, Ollama client, etc.
            from openai import AsyncOpenAI
            self.llm_client = AsyncOpenAI(
                base_url=AgentConfig.LOCAL_LLM_URL,
                api_key="not-needed"  # local models don't need keys
            )
        
        # Initialize MCP connection
        server_params = StdioServerParameters(
            command="python",
            args=[AgentConfig.MCP_SERVER_SCRIPT] + AgentConfig.MCP_SERVER_ARGS
        )
        
        stdio_transport = await stdio_client(server_params)
        self.read_stream, self.write_stream = stdio_transport
        
        self.mcp_session = ClientSession(self.read_stream, self.write_stream)
        await self.mcp_session.initialize()
        
        # Get available tools from MCP server
        tools_response = await self.mcp_session.list_tools()
        self.available_tools = tools_response.tools
        
        print(f"✓ Initialized with {len(self.available_tools)} MCP tools")
    
    def _convert_tools_to_openai_format(self) -> List[Dict]:
        """Convert MCP tools to OpenAI function calling format"""
        openai_tools = []
        
        for tool in self.available_tools:
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            })
        
        return openai_tools
    
    async def _execute_tool(self, tool_name: str, tool_args: Dict) -> str:
        """Execute an MCP tool and return results"""
        try:
            result = await self.mcp_session.call_tool(tool_name, tool_args)
            
            # Extract text content from result
            if result.content:
                return "\n".join([
                    item.text for item in result.content 
                    if hasattr(item, 'text')
                ])
            return "Tool executed but returned no content"
            
        except Exception as e:
            return f"Error executing tool {tool_name}: {str(e)}"
    
    async def chat(self, user_message: str) -> str:
        """Main chat method that handles the conversation"""
        
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # System prompt with context
        system_message = {
            "role": "system",
            "content": """You are an AI assistant specialized in train manufacturing project management.
You have access to tools that can query the production database. 

Your capabilities:
1. Answer questions about project phases, commitments, and statistics
2. Find similar past projects based on phase patterns
3. Build project skeletons by learning from historical data
4. Provide insights and recommendations based on data

When a user asks a complex question:
- Break it down into smaller queries if needed
- Use multiple tools in sequence to gather complete information
- Synthesize results into clear, actionable insights
- Always cite which projects or data your recommendations come from

Be conversational but precise. Always verify your understanding of technical terms related to train production."""
        }
        
        # Prepare messages for LLM
        messages = [system_message] + self.conversation_history
        
        # Convert tools to OpenAI format
        tools = self._convert_tools_to_openai_format()
        
        # Call LLM with function calling
        response = await self.llm_client.chat.completions.create(
            model=AgentConfig.AZURE_DEPLOYMENT if self.use_azure else AgentConfig.LOCAL_MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        assistant_message = response.choices[0].message
        
        # Handle tool calls
        if assistant_message.tool_calls:
            # Add assistant's tool call message to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in assistant_message.tool_calls
                ]
            })
            
            # Execute each tool call
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                print(f"🔧 Executing: {function_name}")
                print(f"   Args: {json.dumps(function_args, indent=2)}")
                
                # Execute tool via MCP
                function_response = await self._execute_tool(function_name, function_args)
                
                # Add tool response to conversation
                self.conversation_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": function_response
                })
            
            # Get final response from LLM after tool execution
            final_response = await self.llm_client.chat.completions.create(
                model=AgentConfig.AZURE_DEPLOYMENT if self.use_azure else AgentConfig.LOCAL_MODEL,
                messages=[system_message] + self.conversation_history
            )
            
            final_message = final_response.choices[0].message.content
            self.conversation_history.append({
                "role": "assistant",
                "content": final_message
            })
            
            return final_message
        
        else:
            # No tool calls, just a direct response
            response_content = assistant_message.content
            self.conversation_history.append({
                "role": "assistant",
                "content": response_content
            })
            
            return response_content
    
    async def handle_complex_query(self, query: str) -> str:
        """
        Handle complex multi-step queries like finding similar projects
        and building skeletons
        """
        
        # Let the LLM orchestrate the multi-step process
        decomposition_prompt = f"""
The user has asked: "{query}"

This appears to be a complex query that may require multiple steps. 
Please analyze what needs to be done and execute the necessary tools in sequence.

For building project skeletons based on similar projects, follow this pattern:
1. First, use search_similar_projects to find relevant past projects
2. Then, use get_phase_statistics to understand typical durations and costs
3. Finally, use build_project_skeleton to create the prefilled skeleton
4. Synthesize the results into actionable recommendations

Break down the query and execute each step thoughtfully.
"""
        
        return await self.chat(decomposition_prompt)
    
    async def cleanup(self):
        """Clean up connections"""
        if self.mcp_session:
            await self.mcp_session.__aexit__(None, None, None)


# ============================================================================
# EXAMPLE USAGE & QUERY PATTERNS
# ============================================================================

async def demo_simple_queries():
    """Demonstrate simple queries"""
    
    agent = TrainProductionAgent(use_azure=True)
    await agent.initialize()
    
    print("\n" + "="*80)
    print("DEMO: Simple Queries")
    print("="*80 + "\n")
    
    # Simple query 1
    query1 = "How many phases are involved in project TRN-2024-001?"
    print(f"User: {query1}")
    response = await agent.chat(query1)
    print(f"Agent: {response}\n")
    
    # Simple query 2
    query2 = "What commitments does project TRN-2024-001 have? How many trains?"
    print(f"User: {query2}")
    response = await agent.chat(query2)
    print(f"Agent: {response}\n")
    
    # Simple query 3
    query3 = "Show me statistics for the 'Bogie Assembly' and 'Cable Installation' phases"
    print(f"User: {query3}")
    response = await agent.chat(query3)
    print(f"Agent: {response}\n")
    
    await agent.cleanup()


async def demo_complex_query():
    """Demonstrate complex skeleton building query"""
    
    agent = TrainProductionAgent(use_azure=True)
    await agent.initialize()
    
    print("\n" + "="*80)
    print("DEMO: Complex Skeleton Building Query")
    print("="*80 + "\n")
    
    query = """
    I have a new project for a Metro Series 3000 train model. 
    We need to produce 8 trains. The engineering department has provided these phases:
    - Bogie Assembly
    - Car Body Welding
    - Interior Fitting
    - HVAC Installation
    - Cable Installation
    - Testing and Commissioning
    
    Can you find similar past projects and build me a project skeleton with 
    estimated hours and resources based on historical data?
    """
    
    print(f"User: {query}")
    response = await agent.handle_complex_query(query)
    print(f"\nAgent: {response}\n")
    
    await agent.cleanup()


async def interactive_chat():
    """Interactive chat session"""
    
    agent = TrainProductionAgent(use_azure=True)
    await agent.initialize()
    
    print("\n" + "="*80)
    print("Train Production AI Assistant - Interactive Mode")
    print("="*80)
    print("Type 'exit' or 'quit' to end the session\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("\nGoodbye! Closing connections...")
                break
            
            if not user_input:
                continue
            
            response = await agent.chat(user_input)
            print(f"\nAssistant: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\nInterrupted. Closing connections...")
            break
        except Exception as e:
            print(f"\nError: {e}\n")
    
    await agent.cleanup()


# ============================================================================
# WEB API WRAPPER (Optional - for REST API integration)
# ============================================================================

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Train Production AI API")

# Global agent instance
global_agent = None

class QueryRequest(BaseModel):
    query: str
    session_id: str = None

class QueryResponse(BaseModel):
    response: str
    session_id: str

@app.on_event("startup")
async def startup_event():
    """Initialize agent on startup"""
    global global_agent
    global_agent = TrainProductionAgent(use_azure=True)
    await global_agent.initialize()
    print("✓ API ready - Agent initialized")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global global_agent
    if global_agent:
        await global_agent.cleanup()

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process a user query"""
    try:
        response = await global_agent.chat(request.query)
        return QueryResponse(
            response=response,
            session_id=request.session_id or "default"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/complex-query", response_model=QueryResponse)
async def process_complex_query(request: QueryRequest):
    """Process a complex multi-step query"""
    try:
        response = await global_agent.handle_complex_query(request.query)
        return QueryResponse(
            response=response,
            session_id=request.session_id or "default"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "tools_available": len(global_agent.available_tools)}


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        
        if mode == "demo-simple":
            asyncio.run(demo_simple_queries())
        elif mode == "demo-complex":
            asyncio.run(demo_complex_query())
        elif mode == "interactive":
            asyncio.run(interactive_chat())
        elif mode == "api":
            import uvicorn
            uvicorn.run(app, host="0.0.0.0", port=8000)
        else:
            print("Usage: python train_agent_client.py [demo-simple|demo-complex|interactive|api]")
    else:
        # Default: interactive mode
        asyncio.run(interactive_chat())