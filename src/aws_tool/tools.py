import json
import warnings
from typing import Any, Dict

import vecs
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_aws import BedrockEmbeddings
from langchain_community.tools import ShellTool
from langchain_community.vectorstores import PGVector
from langchain_core.prompts import PromptTemplate
from langchain_experimental.utilities import PythonREPL
from langchain_core.tools import StructuredTool

from src.model.config import DB_CONNECTION, LLM
from src.model.embedding import get_embedding_from_titan_text, get_text_embedding_model

# Ignore all user warnings
warnings.filterwarnings("ignore", category=UserWarning)


def well_arch_tool_function(query: str) -> Dict[str, Any]:
    """Returns similar documents from a Supabase vector store based on the query"""
    # Create vector store client
    vx = vecs.create_client(DB_CONNECTION)
    # Get or create a collection of vectors
    documents = vx.get_or_create_collection(name="aws_documentation_vectors", dimension=1024)

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


def parse_aws_response(command, response):
    """Parses AWS CLI response, looking for JSON data or handling plain text."""
    if isinstance(response, str):
        if "error" in response:
            return {"command": command, "error": response}
        try:
            parsed_response = json.loads(response)
            return {"success": parsed_response}
        except json.JSONDecodeError:
            return {"success": response}
    else:
        return {"success": response}


def ensure_quotes_balanced(cli_command: str) -> str:
    """
    Ensures that all quotes within the command are properly balanced.
    If there is an odd number of quotes, it adds a closing quote at the end.

    Args:
    cli_command (str): The command to check.

    Returns:
    str: The potentially modified command with balanced quotes.
    """
    # Count the number of single and double quotes
    single_quotes = cli_command.count("'")
    double_quotes = cli_command.count('"')

    # If odd, add an extra quote at the end to balance
    if single_quotes % 2 != 0:
        cli_command += "'"
    if double_quotes % 2 != 0:
        cli_command += '"'

    return cli_command


def aws_cli_tool_function(cli_command: str) -> Dict[str, Any]:
    """
    Executes specified AWS CLI commands and returns the parsed JSON response.

    Args:
    cli_command (str): A valid AWS CLI command formatted as a string.

    Returns:
    Dict[str, Any]: The JSON parsed output of the AWS CLI command.
    """
    # Initialize the ShellTool
    shell_tool = ShellTool()

    # Ensure the command is well-formed
    safe_cli_command = ensure_quotes_balanced(cli_command)

    # Execute the command using ShellTool
    result = shell_tool.run(tool_input={"commands": [safe_cli_command]})

    # Assuming result is returned as a JSON string from the command
    parsed_result = parse_aws_response(command=safe_cli_command, response=result)

    return parsed_result


aws_cli_tool = StructuredTool.from_function(
    func=aws_cli_tool_function,
    name="AWS CLI Tool",
    description="Runs AWS CLI commands",
)


def aws_cloud_diagram_code_function(query: str) -> Dict[str, Any]:
    embeddings = get_text_embedding_model()

    vector_store = PGVector(
        embedding_function=embeddings,
        connection_string=DB_CONNECTION,
        collection_name="diagrams_documentation_vectors",
    )

    retriever = vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={'k': 5, 'fetch_k': 50},
    )

    # RAG template
    prompt_RAG = """
        You are a proficient python developer that specialises in generating AWS cloud diagrmas using the diagrams library. 
        
        Respond with the syntactically correct code for to the question below. Make sure you follow these rules:
        1. Your response should only include Python code. Do not include any preamble or postamble in your response.
        2. Use context to understand the diagrams library and how to use it & apply.
        3. Do not add license information to the output code.
        4. Do not include colab code in the output.
        5. Ensure all the requirements in the question are met.
        6. You should always name the diagram as "tmp" in your code.

        Question:
        {question}

        Context:
        {context}

        Generated Python Code :
        """

    prompt_RAG_tempate = PromptTemplate(
        template=prompt_RAG, input_variables=["context", "question"]
    )

    qa_chain = RetrievalQA.from_llm(
        llm=LLM, prompt=prompt_RAG_tempate, retriever=retriever, return_source_documents=True
    )

    response = qa_chain.invoke({"query": query})

    return {"code": response}


aws_cloud_diagram_code_tool = StructuredTool.from_function(
    name="AWS Cloud Diagram Code Generation Tool",
    description="Generates python code for cloud architecture diagrams based on the query",
    func=aws_cloud_diagram_code_function,
)


python_interpeter_tool = StructuredTool.from_function(
    func=PythonREPL().run,
    name="Python Interpreter Tool",
    description="Runs python code",
)

TOOLS = [well_arch_tool, aws_cli_tool, aws_cloud_diagram_code_tool, python_interpeter_tool]
