import json

from langchain_aws import BedrockEmbeddings

from src.model.config import bedrock_runtime, TEXT_EMBEDDING_MODEL_ID


def get_embedding_from_titan_text(body) -> list:
    """Invoke the Amazon Titan Model via API request for text embeddings."""
    encoded_body = json.dumps(body).encode("utf-8")
    response = bedrock_runtime.invoke_model(
        body=encoded_body,
        modelId=TEXT_EMBEDDING_MODEL_ID,
        accept="application/json",
        contentType="application/json",
    )
    response_body = json.loads(response.get("body").read())
    return response_body["embedding"]


def get_embedding_from_titan_multimodal(body):
    """Invoke the Amazon Titan Model via API request."""
    response = bedrock_runtime.invoke_model(
        body=body,
        modelId="amazon.titan-embed-image-v1",
        accept="application/json",
        contentType="application/json",
    )

    response_body = json.loads(response.get("body").read())
    print(response_body)
    return response_body["embedding"]


def get_text_embedding_model():
    return BedrockEmbeddings(model_id=TEXT_EMBEDDING_MODEL_ID)
