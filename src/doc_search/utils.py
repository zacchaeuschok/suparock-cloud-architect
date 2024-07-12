import vecs
from pypdf import PdfReader

from src.model.config import DB_CONNECTION
from src.model.embedding import get_embedding_from_titan_text


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
    return [text[i : i + max_length] for i in range(0, len(text), max_length)]


def encode_text(text):
    """Generate text embedding."""
    return get_embedding_from_titan_text(
        {
            "inputText": text,
        }
    )


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
        records.append(
            (f"sample.pdf_chunk{idx}", chunk_emb, {"type": "pdf", "chunk_index": idx})
        )

    # Upsert all chunks at once
    documents.upsert(records=records)
    print("Inserted PDF chunks")

    # Index the collection for fast search performance
    documents.create_index()
    print("Created index")
