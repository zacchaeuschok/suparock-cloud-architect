from langchain import hub
from langchain.agents import create_react_agent
from langchain_core.agents import AgentFinish
from langchain_core.runnables import RunnablePassthrough
from langgraph.constants import END
from langgraph.graph import Graph

from doc_search.tools import TOOLS
from model.config import LLM


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
