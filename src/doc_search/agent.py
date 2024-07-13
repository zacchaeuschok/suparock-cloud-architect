from langchain import hub
from langchain.agents import create_react_agent
from langchain_core.agents import AgentFinish, AgentAction
from langchain_core.runnables import RunnablePassthrough
from langgraph.constants import END
from langgraph.graph import Graph

from src.doc_search.tools import CLI_TOOLS, DOC_TOOLS, TOOLS
from src.model.config import LLM


def construct_agent():
    prompt = hub.pull("hwchase17/react")
    prompt.template = (
        """
        You are an expert AWS Certified Solutions Architect in 2024.
        Your role is to assist the customer with their request and you should always provide a response without waiting.
        Your customer may provide you with a request or question about building on AWS.
        You should always think about the customer's request before deciding the next step.
        You don't have to use all the tools, but you should use the most appropriate tool for the customer's request.
        
        These are the available tools:
        
        1.  You can reference the AWS Well-Architected Framework for best practices.

        2.  You can run AWS CLI commands to retrieve information about the customer's AWS setup.
            You already have the AWS CLI installed on your machine and can run any command.
            You have access to actual AWS CLI commands and can use them to retrieve information.
            Your commands should not include generic variables and must work without expecting user input.
            You should check that your commands are well-formed and correct.
            
            If you see "error", it means your command is incorrect and you should use the error message to correct it.
            If you see "success", it means your command is correct and you can use the output to help the customer.
            
            If you face syntax errors, you should correct them before running the command.
            For example, you should ensure the command you run has closing quotes and brackets.
            
            If you face Access Denied errors, you should let the customer know that you don't have access to the 
            requested information.
        """
        + prompt.template
    )
    return create_react_agent(LLM, TOOLS, prompt)


def create_graph_workflow(agent_runnable):
    agent = RunnablePassthrough.assign(agent_outcome=agent_runnable)
    workflow = Graph()
    workflow.add_node("agent", agent)
    workflow.add_node("doc_tools", execute_doc_tools)
    workflow.add_node("cli_tools", execute_cli_tools)
    workflow.add_node("response_tools", execute_response_tools)

    workflow.set_entry_point("agent")
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "doc_tools": "doc_tools",
            "cli_tools": "cli_tools",
            "response_tools": "response_tools",
            "exit": END,
        },
    )

    # Add edges to loop back to the agent if necessary
    workflow.add_edge("doc_tools", "agent")
    workflow.add_edge("cli_tools", "agent")

    # Add edge to end agent if response tools invoked
    workflow.add_edge("response_tools", END)

    return workflow.compile()


def execute_doc_tools(data):
    print("Executing Well Arch Tool")

    agent_action = data.pop("agent_outcome")
    print(f"Agent action: {agent_action}")

    tool_to_use = {t.name: t for t in DOC_TOOLS}[agent_action.tool]
    print(f"Executing Well Arch Tool: {agent_action.tool_input}")

    observation = tool_to_use.invoke(agent_action.tool_input)
    print(f"Observation: {observation}")

    data["intermediate_steps"].append((agent_action, observation))
    return data


def execute_cli_tools(data):
    print("Executing CLI command")

    agent_action = data.pop("agent_outcome")
    print(f"Agent action: {agent_action}")

    tool_to_use = {t.name: t for t in CLI_TOOLS}[agent_action.tool]
    print(f"Executing CLI command: {agent_action.tool_input}")

    observation = tool_to_use.invoke(agent_action.tool_input)
    print(f"Observation: {observation}")

    data["intermediate_steps"].append((agent_action, observation))
    return data


def execute_response_tools(data):
    print("Executing response tools")

    agent_action = data.pop("agent_outcome")

    data["intermediate_steps"].append((agent_action, agent_action.tool_input))

    print(f"Agent action: {agent_action}")

    return data


def should_continue(data):
    agent_outcome = data.get("agent_outcome")
    if not agent_outcome:
        print("No agent outcome available, defaulting to exit.")
        return "exit"

    if isinstance(agent_outcome, AgentAction):
        tool_name = agent_outcome.tool
        if tool_name == "Well Arch Tool":
            print("Continue to doc_tools")
            return "doc_tools"
        elif tool_name == "AWS CLI Tool":
            print("Continue to cli_tools")
            return "cli_tools"
        elif tool_name == "Response Tool":
            print("Continue to response_tools")
            return "response_tools"
    elif isinstance(agent_outcome, AgentFinish):
        print("Exiting")
        return "exit"
    else:
        print(f"Unexpected type for agent outcome: {type(agent_outcome)}")
    return "exit"
