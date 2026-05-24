from llm import llm
from graph import graph
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import Tool
from langchain_core.runnables.history import RunnableWithMessageHistory
from langsmith import Client
from langchain.agents import create_agent
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_neo4j import Neo4jChatMessageHistory
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_core.tools import tool
from llm import llm
from graph import graph
from utils import get_session_id

# Create a movie chat chain
chat_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a movie expert providing information about movies."),
        ("human", "{input}"),
    ]
)
movie_chat = chat_prompt | llm | StrOutputParser()
# Create a set of tools
tools = [
    Tool.from_function(
        name="General Chat",
        description="For general movie chat not covered by other tools",
        func=movie_chat.invoke,
    )
]
# Create chat history callback
def get_memory(session_id):
    return Neo4jChatMessageHistory(session_id=session_id, graph=graph)
# Create the agent
client = Client()
agent_prompt = client.pull_prompt("hwchase17/react-chat", dangerously_pull_public_prompt=True)
agent = create_react_agent(llm, tools, agent_prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True, 
    handle_parsing_errors=True
)

chat_agent = RunnableWithMessageHistory(
    agent_executor,
    get_memory,
    input_messages_key="input",
    history_messages_key="chat_history",
)
# Create a handler to call the agent

def generate_response(user_input):
    """
    Create a handler that calls the Conversational agent
    and returns a response to be rendered in the UI
    """

    response = chat_agent.invoke(
        {"input": user_input},
        {"configurable": {"session_id": get_session_id()}},)

    return response['output']