import json
from typing import Any, Dict

import vecs
from langchain_core.tools import StructuredTool

from model.config import DB_CONNECTION


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


def cost_analysis_tool_function(query: str) -> Dict[str, Any]:
    print("Running cost analysis tool")
    """Executes AWS CLI commands to fetch and analyze AWS cost data based on the specified query."""
    # Initialize the ShellTool
    shell_tool = ShellTool()

    # Define the AWS CLI command to fetch cost data
    aws_cli_command = """
    aws ce get-cost-and-usage --time-period Start=2024-07-01,End=2024-07-31 --granularity MONTHLY --metrics "BlendedCost" "UsageQuantity"
    """

    # Execute the command using ShellTool
    result = shell_tool.run(tool_input={"commands": [aws_cli_command]})

    # Assuming result is returned as a JSON string from the command
    parsed_result = json.loads(result) if type(result) is str else result

    # Format the result for output
    resp_json = {"cost_data": parsed_result}  # Use the parsed result directly

    return resp_json


# Create a StructuredTool from the function
cost_analysis_tool = StructuredTool.from_function(
    func=cost_analysis_tool_function,
    name="Cost Analysis Tool",
    description="Analyzes AWS costs and usage to provide insights and recommendations.",
)

TOOLS = [well_arch_tool, cost_analysis_tool]
