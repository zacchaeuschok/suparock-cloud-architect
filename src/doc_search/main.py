import sys
from typing import Optional

from langchain_core.exceptions import OutputParserException

from src.doc_search.agent import construct_agent


def search(query_term: Optional[str] = None, callbacks=None):
    agent_executor = construct_agent()
    config = {"recursion_limit": 10}
    result = agent_executor.invoke(
        {
            "input": query_term,
        },
        config={
            'callbacks': callbacks,
            **config
        }
    )
    return result


def main():
    # sys.argv[1] will be the first command-line argument passed to the script
    query = sys.argv[1] if len(sys.argv) > 1 else None
    search(query)


if __name__ == "__main__":
    main()
