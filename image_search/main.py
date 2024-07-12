import json
import sys
from typing import Optional

import vecs
from matplotlib import image as mpimg
from matplotlib import pyplot as plt

from model.config import DB_CONNECTION
from model.embedding import get_embedding_from_titan_multimodal


def search(query_term: Optional[str] = None):
    if query_term is None:
        query_term = sys.argv[1]

    # create vector store client
    vx = vecs.create_client(DB_CONNECTION)
    images = vx.get_or_create_collection(name="image_vectors", dimension=1024)

    # Encode text query
    text_emb = get_embedding_from_titan_multimodal(
        json.dumps(
            {
                "inputText": query_term,
                "embeddingConfig": {"outputEmbeddingLength": 1024},
            }
        )
    )

    # query the collection filtering metadata for "type" = "jpg"
    results = images.query(
        data=text_emb,  # required
        limit=1,  # number of records to return
        filters={"type": {"$eq": "jpg"}},  # metadata filters
    )
    result = results[0]
    print(result)
    plt.title(result)
    image = mpimg.imread("./images/" + result)
    plt.imshow(image)
    plt.show()


if __name__ == "__main__":
    search("Man wearing shoes")
