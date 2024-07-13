import json
import warnings
from typing import Any, Dict

from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_community.tools import ShellTool
from langchain_core.prompts import PromptTemplate
from langchain_experimental.utilities import PythonREPL
from langchain_core.tools import StructuredTool

from src.aws.vectorstore import get_diagrams_documentation_vector_store
from src.aws.vectorstore import get_aws_documentation_vector_store
from src.aws.vectorstore import get_web_service_documentation_vector_store
from src.model.config import LLM

# Ignore all user warnings
warnings.filterwarnings("ignore", category=UserWarning)


def well_arch_tool_function(query: str) -> Dict[str, Any]:
    vector_store = get_aws_documentation_vector_store()

    retriever = vector_store.as_retriever(
        search_kwargs={'k': 5},
    )

    # RAG template
    prompt_RAG = """
        You are an expert in the AWS Well-Architected Framework.

        Respond with the most relevant sections of the AWS Well-Architected Framework documentation based on the question below. Ensure your response is accurate and provides best practices.

        Question:
        {question}

        Context:
        {context}

        """

    prompt_RAG_tempate = PromptTemplate(
        template=prompt_RAG, input_variables=["context", "question"]
    )

    qa_chain = RetrievalQA.from_llm(
        llm=LLM, prompt=prompt_RAG_tempate, retriever=retriever, return_source_documents=True
    )

    response = qa_chain.invoke({"query": query})

    return {"code": response}


well_arch_tool = StructuredTool.from_function(
    func=well_arch_tool_function,
    name="Well Arch Tool",
    description="Returns text from AWS Well-Architected Framework related to the query",
)


def web_service_search_function(query: str) -> Dict[str, Any]:
    vector_store = get_web_service_documentation_vector_store()

    retriever = vector_store.as_retriever(
        search_kwargs={'k': 5},
    )

    # RAG template
    prompt_RAG = """
        You are an expert in providing Amazon Web Services based on the AWS Whitepaper Overview of Amazon Web Services.

        Respond with the most relevant sections of the AWS Whitepaper documentation based on the question below. 
        Ensure your response is accurate and provides the most suitable web services for the user.

        Question:
        {question}

        Context:
        {context}

        """

    prompt_RAG_tempate = PromptTemplate(
        template=prompt_RAG, input_variables=["context", "question"]
    )

    qa_chain = RetrievalQA.from_llm(
        llm=LLM, prompt=prompt_RAG_tempate, retriever=retriever, return_source_documents=True
    )

    response = qa_chain.invoke({"query": query})

    return {"code": response}

web_service_search_tool = StructuredTool.from_function(
    func=web_service_search_function,
    name="Web Service Search Tool",
    description="Selects the most suitable AWS web service based on the user input",
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
    vector_store = get_diagrams_documentation_vector_store()

    retriever = vector_store.as_retriever(
        search_kwargs={'k': 5},
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


def python_interpeter_tool_function(code: str) -> Dict[str, Any]:
    """
    Runs the provided Python code in a Python interpreter and returns the output.

    Args:
    code (str): The Python code to be executed.

    Returns:
    Dict[str, Any]: The output of the Python code execution.
    """
    python_repl = PythonREPL()
    python_repl.run(
        """
        import subprocess
        import sys
        import platform
        
        def install_diagrams():
            # Build the pip install command
            command = [sys.executable, "-m", "pip", "install", "diagrams"]
            
            # Run the command
            result = subprocess.run(command, capture_output=True, text=True)
            
            # Print output and error if any
            if result.returncode == 0:
                print("Installation successful:", result.stdout)
            else:
                print("Error during installation:", result.stderr)
                
        def install_graphviz():
        try:
            if platform.system() == "Linux":
                subprocess.run(["sudo", "apt-get", "update"], check=True)
                subprocess.run(["sudo", "apt-get", "install", "-y", "graphviz"], check=True)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["brew", "install", "graphviz"], check=True)
            print("Graphviz installation successful.")
        except subprocess.CalledProcessError as e:
            print("Failed to install Graphviz: ", e)

        # Execute the function
        install_diagrams()
        install_graphviz()
        """
    )
    result = python_repl.run(code)
    return {"output": result}


python_interpeter_tool = StructuredTool.from_function(
    func=python_interpeter_tool_function,
    name="Python Interpreter Tool",
    description="Runs python code",
)

TOOLS = [well_arch_tool, aws_cli_tool, aws_cloud_diagram_code_tool, python_interpeter_tool, web_service_search_tool]
