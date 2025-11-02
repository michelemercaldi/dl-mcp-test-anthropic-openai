Lesson 4: Creating an MCP Server
💻   To Access the mcp_project folder : 1) click on the "File" option on the top menu of the notebook and then 2) click on "Open" and finally 3) click on L4.

To create your MCP server using FastMCP, you will initialize a FastMCP server labeled as mcp and decorating the functions with @mcp.tool(). FastMCP automatically generates the necessary MCP schema based on type hints and docstrings.

Note: The magic function %%writefile mcp_project/research_server.py will not execute the code but it will save the content of the cell to the server file research_server.py in the directory: mcp_project. If you remove the magic function and run the cell, the code won't run in Jupyter notebook. You will run the server from the terminal in the next section.


see research_server.py



- To open the terminal, run the cell below.
- Navigate to the project directory and initiate it with `uv`:
    - `cd L4/mcp_project`  or  in paret dir of the project
    - `uv init`
-  Create virtual environment and activate it:
    - `uv venv`
    - `source .venv/bin/activate`
- Install dependencies:
    - `uv add mcp arxiv`
- Launch the inspector:
    - `npx @modelcontextprotocol/inspector uv run research_server.py`
    - If you get a message asking "need to install the following packages", type: `y`
- You will get a message saying that the inspector is up and running at a specific address. To open the inspector, click on that given address. The inspector will open in another tab.
- In the inspector UI, make sure to follow the video. You would need to specify under configuration the `Inspector Proxy Address`. Please check the "Inspector UI Instructions" below and run the last cell (after the terminal) to get the `Inspector Proxy Address` for your configurations. 
- If you tested the tool and would like to access the `papers` folder: 1) click on the `File` option on the top menu of the notebook and 2) click on `Open` and then 3) click on `L4` -> `mcp_project`.
- Once you're done with the inspector UI, make sure to close the inspector by typing `Ctrl+C` in the terminal below.
