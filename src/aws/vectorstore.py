from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_text_splitters import CharacterTextSplitter

from src.model.embedding import get_text_embedding_model
from src.model.supabase_client import supabase_client

embeddings = get_text_embedding_model()


def create_diagrams_documentation_vector_store():
    loader = PyMuPDFLoader("./src/docs/diagrams_documentation.pdf")
    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)

    vector_store = SupabaseVectorStore.from_documents(
        docs,
        embeddings,
        client=supabase_client,
        table_name="diagrams_documents",
        query_name="match_diagrams_documents",
        chunk_size=500,
    )
    return vector_store


def get_diagrams_documentation_vector_store():
    return SupabaseVectorStore(
        embedding=embeddings,
        client=supabase_client,
        table_name="diagrams_documents",
        query_name="match_diagrams_documents",
    )


def create_aws_documentation_vector_store():
    loader = PyMuPDFLoader("./src/docs/aws_documentation.pdf")
    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)

    vector_store = SupabaseVectorStore.from_documents(
        docs,
        embeddings,
        client=supabase_client,
        table_name="aws_documents",
        query_name="match_diagrams_documents",
        chunk_size=500,
    )
    return vector_store


def get_aws_documentation_vector_store():
    return SupabaseVectorStore(
        embedding=embeddings,
        client=supabase_client,
        table_name="aws_documents",
        query_name="match_aws_documents",
    )


if __name__ == "__main__":
    print("Creating vector stores")
    create_diagrams_documentation_vector_store()
    create_aws_documentation_vector_store()
