import json
from typing import Any, Dict

import boto3
import vecs
from dotenv import load_dotenv
from pypdf import PdfReader
from langchain import hub
from langchain.agents import create_react_agent
from langchain_aws import BedrockLLM
from langchain_core.agents import AgentFinish
from langchain_core.runnables import RunnablePassthrough
from langchain_core.tools import StructuredTool

from langgraph.graph import END, Graph

load_dotenv()

# Setup bedrock
bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-west-2",
)

DB_CONNECTION = "postgresql://postgres:postgres@localhost:54322/postgres"

# Define Bedrock LLM
LLM = BedrockLLM(client=bedrock_runtime, model_id="meta.llama3-70b-instruct-v1:0")
LLM.model_kwargs = {"temperature": 0.7}


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
    results = documents.query(
        data=query_emb,
        limit=5,
        include_value=True
    )

    # Format results for output
    resp_json = {"docs": [result for result in results]}
    return resp_json


well_arch_tool = StructuredTool.from_function(
    func=well_arch_tool_function,
    name="Well Arch Tool",
    description="Returns text from AWS Well-Architected Framework related to the query",
)

TOOLS = [well_arch_tool]


def get_embedding_from_titan_text(body) -> list:
    """Invoke the Amazon Titan Model via API request for text embeddings."""
    encoded_body = json.dumps(body).encode('utf-8')
    response = bedrock_runtime.invoke_model(
        body=encoded_body,
        modelId="amazon.titan-embed-text-v2:0",
        accept="application/json",
        contentType="application/json",
    )
    response_body = json.loads(response.get("body").read())
    return response_body["embedding"]


def construct_agent():
    prompt = hub.pull("hwchase17/react")
    prompt.template = (
            """
        You are an expert AWS Certified Solutions Architect. Your role is to help customers understand best 
        practices on building on AWS. You will always reference the AWS Well-Architected Framework when customers ask 
        questions on building on AWS.
        """
            + prompt.template
    )
    return create_react_agent(LLM, TOOLS, prompt)


def create_graph_workflow(agent_runnable):
    agent = RunnablePassthrough.assign(agent_outcome=agent_runnable)
    workflow = Graph()
    workflow.add_node("agent", agent)
    workflow.add_node("tools", execute_tools)

    workflow.set_entry_point("agent")
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "continue": "tools",
            "exit": END,
        },
    )
    workflow.add_edge("tools", "agent")

    return workflow.compile()


def execute_tools(data):
    agent_action = data.pop("agent_outcome")
    tool_to_use = {t.name: t for t in TOOLS}[agent_action.tool]
    observation = tool_to_use.invoke(agent_action.tool_input)
    print(f"{agent_action}\n {observation}")
    data["intermediate_steps"].append((agent_action, observation))
    return data


def should_continue(data):
    if isinstance(data["agent_outcome"], AgentFinish):
        return "exit"
    else:
        return "continue"


def extract_text_from_pdf(file_path):
    pdf_reader = PdfReader(file_path)
    text = ""

    for page in pdf_reader.pages:
        extracted_text = page.extract_text()
        if extracted_text:  # Check if text is extracted successfully
            text += extracted_text + "\n"  # Append text of each page

    return text


def chunk_text(text, max_length=1000):
    """Chunk text into segments of up to max_length characters."""
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]


def encode_text(text):
    """Generate text embedding."""
    return get_embedding_from_titan_text({
        "inputText": text,
    })


def seed():
    # Create vector store client
    vx = vecs.create_client(DB_CONNECTION)

    # Get or create a collection of vectors for documents
    documents = vx.get_or_create_collection(name="document_vectors", dimension=1024)

    # Path to the PDF file
    pdf_path = "./docs/AWS_Well-Architected_Framework.pdf"

    # Extract text from the PDF
    pdf_text = extract_text_from_pdf(pdf_path)

    # Chunk the text into smaller parts
    text_chunks = chunk_text(pdf_text)

    # Generate embeddings and store each chunk
    records = []
    for idx, chunk in enumerate(text_chunks):
        print(f"Inserting chunk {idx}")
        chunk_emb = encode_text(chunk)
        records.append((f"sample.pdf_chunk{idx}", chunk_emb, {"type": "pdf", "chunk_index": idx}))

    # Upsert all chunks at once
    documents.upsert(records=records)
    print("Inserted PDF chunks")

    # Index the collection for fast search performance
    documents.create_index()
    print("Created index")


def main():
    agent_runnable = construct_agent()
    chain = create_graph_workflow(agent_runnable)
    config = {
        "recursion_limit": 50
    }
    result = chain.invoke(
        {
            "input": "Should I use a single or multiple AWS accounts?",
            "intermediate_steps": [],
        },
        config=config
    )
    output = result["agent_outcome"].return_values["output"]
    print(output)


if __name__ == "__main__":
    main()
