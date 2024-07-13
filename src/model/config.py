import boto3
from dotenv import load_dotenv
from langchain_aws import ChatBedrock

load_dotenv()

# AWS Setup
bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-west-2",
)


# Database Connection String
DB_CONNECTION = "postgresql://postgres:postgres@localhost:54322/postgres"

# LangChain Model Identifier
LLM_MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"
TEXT_EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v2:0"

# Define Bedrock LLM
LLM = ChatBedrock(client=bedrock_runtime, model_id=LLM_MODEL_ID)
LLM.model_kwargs = {"temperature": 0.7}
