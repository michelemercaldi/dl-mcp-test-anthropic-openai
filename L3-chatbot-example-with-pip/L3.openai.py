import arxiv
import json
import os
from typing import List
from dotenv import load_dotenv
from openai import AzureOpenAI


# Tool Functions

PAPER_DIR = "papers"


# The first tool searches for relevant arXiv papers based on a topic 
# and stores the papers' info in a JSON file 
# (title, authors, summary, paper url and the publication date). 
# The JSON files are organized by topics in the `papers` directory. 
# The tool does not download the papers.  

def search_papers(topic: str, max_results: int = 5) -> List[str]:
    """
    Search for papers on arXiv based on a topic and store their information.

    Args:
        topic: The topic to search for
        max_results: Maximum number of results to retrieve (default: 5)

    Returns:
        List of paper IDs found in the search
    """

    # Use arxiv to find the papers
    client = arxiv.Client()

    # Search for the most relevant articles matching the queried topic
    search = arxiv.Search(
        query = topic,
        max_results = max_results,
        sort_by = arxiv.SortCriterion.Relevance
    )

    papers = client.results(search)

    # Create directory for this topic
    path = os.path.join(PAPER_DIR, topic.lower().replace(" ", "_"))
    os.makedirs(path, exist_ok=True)

    file_path = os.path.join(path, "papers_info.json")

    # Try to load existing papers info
    try:
        with open(file_path, "r") as json_file:
            papers_info = json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError):
        papers_info = {}

    # Process each paper and add to papers_info
    paper_ids = []
    for paper in papers:
        paper_ids.append(paper.get_short_id())
        paper_info = {
            'title': paper.title,
            'authors': [author.name for author in paper.authors],
            'summary': paper.summary,
            'pdf_url': paper.pdf_url,
            'published': str(paper.published.date())
        }
        papers_info[paper.get_short_id()] = paper_info

    # Save updated papers_info to json file
    with open(file_path, "w") as json_file:
        json.dump(papers_info, json_file, indent=2)

    print(f"Results are saved in: {file_path}")

    return paper_ids


# The second tool looks for information about a specific 
# paper across all topic directories inside the `papers` directory.
def extract_info(paper_id: str) -> str:
    """
    Search for information about a specific paper across all topic directories.

    Args:
        paper_id: The ID of the paper to look for

    Returns:
        JSON string with paper information if found, error message if not found
    """

    for item in os.listdir(PAPER_DIR):
        item_path = os.path.join(PAPER_DIR, item)
        if os.path.isdir(item_path):
            file_path = os.path.join(item_path, "papers_info.json")
            if os.path.isfile(file_path):
                try:
                    with open(file_path, "r") as json_file:
                        papers_info = json.load(json_file)
                        if paper_id in papers_info:
                            return json.dumps(papers_info[paper_id], indent=2)
                except (FileNotFoundError, json.JSONDecodeError) as e:
                    print(f"Error reading {file_path}: {str(e)}")
                    continue

    return f"There's no saved information related to paper {paper_id}."



# Tool Schema
# Here are the schema of each tool which you will provide to the LLM.
tools= [
    {
        "type": "function",
        "function": {
            "name": "search_papers",
            "description": "Search for papers on arXiv based on a topic and store their information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "The topic to search for"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to retrieve",
                        "default": 5
                    }
                },
                "required": ["topic"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "extract_info",
            "description": "Search for information about a specific paper across all topic directories.",
            "parameters": {
                "type": "object",
                "properties": {
                    "paper_id": {
                        "type": "string",
                        "description": "The ID of the paper to look for"
                    }
                },
                "required": ["paper_id"]
            }
        }
    }
]


# Tool Mapping
# This code handles tool mapping and execution.
mapping_tool_function = {
    "search_papers": search_papers,
    "extract_info": extract_info
}


def execute_tool(tool_name, tool_args):

    result = mapping_tool_function[tool_name](**tool_args)

    if result is None:
        result = "The operation completed but didn't return any results."

    elif isinstance(result, list):
        result = ', '.join(result)

    elif isinstance(result, dict):
        # Convert dictionaries to formatted JSON strings
        result = json.dumps(result, indent=2)

    else:
        # For any other type, convert using str()
        result = str(result)
    return result



#======================

# Chatbot Code
# The chatbot handles the user's queries one by one, but it does not persist 
# memory across the queries.


# azure openai client
load_dotenv()
api_key = os.environ["AZURE_OPENAI_API_KEY"]
azure_endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
api_version = os.environ["AZURE_OPENAI_API_VERSION"]
client = AzureOpenAI(
    api_key=api_key,
    api_version=api_version,
    azure_endpoint=azure_endpoint,
)



# OpenAi Query Processing
def process_query(query):
    messages = [{'role': 'user', 'content': query}]
    while True:
        resp = client.chat.completions.create(
            model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
            messages=messages,
            max_tokens=2024,
            temperature=0,
            tools=tools,
            tool_choice="auto",
        )

        msg = resp.choices[0].message

        # If the model wants to call tools, msg.content is often None.
        if getattr(msg, "tool_calls", None):
            # Add the assistant message that *requested* the tools
            messages.append({
                "role": "assistant",
                "content": msg.content or "",  # often None when tool_calls exist
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    } for tc in msg.tool_calls
                ]
            })

            # Execute each tool and feed results back
            for tc in msg.tool_calls:
                func_name = tc.function.name
                args = json.loads(tc.function.arguments or "{}")
                result = execute_tool(func_name, args)

                # The critical part: a `tool` role message with the matching id
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })

            # Loop again so the model can use the tool results
            continue

        # No tool calls -> this is the final assistant text
        print(msg.content)
        return msg.content




# Chat Loop
def chat_loop():
    print("Type your queries or 'quit' to exit.")
    while True:
        try:
            query = input("\nQuery: ").strip()
            if query.lower() == 'quit':
                break

            process_query(query)
            print("\n")
        except Exception as e:
            print(f"\nError: {str(e)}")


def main():
    search_papers("computers")
    extract_info('1310.7911v2')
    
    # Here's an example query:
    # - Search for 2 papers on "LLM interpretability"

    chat_loop()

if __name__ == "__main__":
    main()

