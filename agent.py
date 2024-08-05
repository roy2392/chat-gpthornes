from llm import got_chat_model as chat_model
from graph import driver
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain.schema import StrOutputParser
from langchain.tools import Tool
from langchain_community.chat_message_histories import Neo4jChatMessageHistory
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.runnables.history import RunnableWithMessageHistory
from utils import get_session_id
from tools.vector import get_got_text
from tools.cypher import got_cypher_qa

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a wise maester from the Citadel, deeply knowledgeable about the history, lore, and current events of the Seven Kingdoms and beyond. Provide information about Game of Thrones. Use only the information from your previous responses."),
    ("human", "{input}"),
])
got_chat = chat_prompt | chat_model | StrOutputParser()

tools = [
    Tool.from_function(
        name="General Game of Thrones Chat",
        description="For general chat about Game of Thrones not covered by other tools. Relevant when the user asks a question about your previous answers, which do not require retrieving additional information",
        func=got_chat.invoke
    ),
    Tool.from_function(
        name="Game of Thrones Lore Search",
        description="For when you need to find information about Game of Thrones lore, characters, houses, and events based on books and research",
        func=get_got_text
    ),
    Tool.from_function(
        name="Game of Thrones Graph Information",
        description="Provide information about Game of Thrones using Cypher queries on the knowledge graph",
        func=got_cypher_qa
    )
]

def get_memory(session_id):
    return Neo4jChatMessageHistory(session_id=session_id, graph=driver)

agent_prompt = PromptTemplate.from_template("""
You are a wise maester from the Citadel, deeply knowledgeable about the history, lore, and current events of the Seven Kingdoms and beyond.
Be as helpful as possible and return as much information as possible about the world of Game of Thrones.
Do not answer any questions that do not relate to Game of Thrones, its characters, houses, events, or lore.
Do not answer any questions using your pre-trained knowledge, only use the information provided in the context.

TOOLS:
------
You have access to the following tools:
{tools}

To use a tool, please use the following format:
```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
```

When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:
```
Thought: Do I need to use a tool? No
Final Answer: [your response here]
```

Begin!
Previous conversation history:
{chat_history}

New input: {input}
{agent_scratchpad}
""")

agent = create_react_agent(chat_model, tools, agent_prompt)
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

def generate_response(user_input):
    """
    Create a handler that calls the Conversational agent
    and returns a response to be rendered in the UI
    """
    response = chat_agent.invoke(
        {"input": user_input},
        {"configurable": {"session_id": get_session_id()}},
    )
    return response['output']

# Make sure to export the generate_response function
__all__ = ['generate_response']