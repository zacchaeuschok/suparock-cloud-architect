from typing import Optional

from src.doc_search.agent import construct_agent, create_graph_workflow


def search(query_term: Optional[str] = None):
    agent_runnable = construct_agent()
    chain = create_graph_workflow(agent_runnable)
    config = {"recursion_limit": 50}
    result = chain.invoke(
        {
            "input": query_term,
            "intermediate_steps": [],
        },
        config=config,
    )
    output = result["agent_outcome"].return_values["output"]
    print(output)


if __name__ == "__main__":
    search("Should I use a single or multiple AWS accounts?")
