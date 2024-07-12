import json
from typing import Any, Dict

import vecs
from langchain_community.tools import ShellTool
from langchain_core.tools import StructuredTool

from src.model.config import DB_CONNECTION
from src.model.embedding import get_embedding_from_titan_text


def well_arch_tool_function(query: str) -> Dict[str, Any]:
    """Returns similar documents from a Supabase vector store based on the query"""
    # Create vector store client
    vx = vecs.create_client(DB_CONNECTION)
    # Get or create a collection of vectors
    documents = vx.get_or_create_collection(name="document_vectors", dimension=1024)

    query_emb = get_embedding_from_titan_text(
        {
            "inputText": query,
        }
    )

    # Query the collection
    results = documents.query(data=query_emb, limit=5, include_value=True)

    # Format results for output
    resp_json = {"docs": [result for result in results]}
    return resp_json


well_arch_tool = StructuredTool.from_function(
    func=well_arch_tool_function,
    name="Well Arch Tool",
    description="Returns text from AWS Well-Architected Framework related to the query",
)


def aws_cli_tool_function(cli_command: str) -> Dict[str, Any]:
    """
    Executes specified AWS CLI commands and returns the parsed JSON response.

    Args:
    cli_command (str): A valid AWS CLI command formatted as a string.

    Returns:
    Dict[str, Any]: The JSON parsed output of the AWS CLI command.
    """
    print("Running AWS CLI command")

    # Initialize the ShellTool
    shell_tool = ShellTool()

    # Execute the command using ShellTool
    result = shell_tool.run(tool_input={"commands": [cli_command]})

    # Assuming result is returned as a JSON string from the command
    parsed_result = json.loads(result) if type(result) is str else result

    # Return the parsed result directly
    return {"aws_data": parsed_result}


# Create a StructuredTool from the function
aws_cli_tool = StructuredTool.from_function(
    func=aws_cli_tool_function,
    name="Cost Analysis Tool",
    description="Runs AWS CLI commands",
)

TOOLS = [well_arch_tool, aws_cli_tool]
