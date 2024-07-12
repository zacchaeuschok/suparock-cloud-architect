import base64
import json
import sys

import vecs

from src.model.config import DB_CONNECTION
from src.model.embedding import get_embedding_from_titan_multimodal


def readFileAsBase64(file_path):
    """Encode image as base64 string."""
    try:
        with open(file_path, "rb") as image_file:
            input_image = base64.b64encode(image_file.read()).decode("utf8")
        return input_image
    except:
        print("bad file name")
        sys.exit(0)


def construct_bedrock_image_body(base64_string):
    """Construct the request body.

    https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-titan-embed-mm.html
    """
    return json.dumps(
        {
            "inputImage": base64_string,
            "embeddingConfig": {"outputEmbeddingLength": 1024},
        }
    )


def encode_image(file_path):
    """Generate embedding for the image at file_path."""
    base64_string = readFileAsBase64(file_path)
    body = construct_bedrock_image_body(base64_string)
    emb = get_embedding_from_titan_multimodal(body)
    return emb


def seed():
    # create vector store client
    vx = vecs.create_client(DB_CONNECTION)

    # get or create a collection of vectors with 1024 dimensions
    images = vx.get_or_create_collection(name="image_vectors", dimension=1024)

    # Generate image embeddings with Amazon Titan Model
    img_emb1 = encode_image("./images/one.jpg")
    img_emb2 = encode_image("./images/two.jpg")
    img_emb3 = encode_image("./images/three.jpg")
    img_emb4 = encode_image("./images/four.jpg")

    # add records to the *images* collection
    images.upsert(
        records=[
            (
                "one.jpg",  # the vector's identifier
                img_emb1,  # the vector. list or np.array
                {"type": "jpg"},  # associated  metadata
            ),
            ("two.jpg", img_emb2, {"type": "jpg"}),
            ("three.jpg", img_emb3, {"type": "jpg"}),
            ("four.jpg", img_emb4, {"type": "jpg"}),
        ]
    )
    print("Inserted images")

    # index the collection for fast search performance
    images.create_index()
    print("Created index")
