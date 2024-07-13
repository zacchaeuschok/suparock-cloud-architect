import sys
from typing import Optional

from langchain_core.exceptions import OutputParserException

from src.doc_search.agent import construct_agent, create_graph_workflow


def search(query_term: Optional[str] = None):
    agent_runnable = construct_agent()
    chain = create_graph_workflow(agent_runnable)
    config = {"recursion_limit": 50}
    try:
        result = chain.invoke(
            {
                "input": query_term,
                "intermediate_steps": [],
            },
            config=config,
        )
    except OutputParserException as e:
        print(f"Error parsing output: {e}")
        return
    try:
        output = result["agent_outcome"].return_values["output"]
    except AttributeError:
        print(result["agent_outcome"])
        output = "No output found."
    print(output)


def main():
    # sys.argv[1] will be the first command-line argument passed to the script
    query = sys.argv[1] if len(sys.argv) > 1 else None
    search(query)


if __name__ == "__main__":
    main()
