from langchain.tools import tool
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.prompts import MessagesPlaceholder
from pydantic_core.core_schema import model_field

from dotenv import load_dotenv
import os

load_dotenv()

todoist_api_key = os.getenv("TODOIST_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")

@tool
def add_task():
    """ Add a new task to the user's task list. Use this when the user wants to add or create a task. """
    print("Adding task to Todoist...")
    print("Task added successfully!")

tools = [add_task]

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=gemini_api_key,
    temperature=0.3
)

system_prompt = "You are a helpful assistant. You will help the user add tasks."
user_prompt = "add a new task to buy dinner for tonight, and dog food for the week."

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("user", user_prompt),
    MessagesPlaceholder("agent_scratchpad")
])

agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)
response = agent_executor.invoke({"input": user_prompt})

#chain = prompt | llm | StrOutputParser()
#response = chain.invoke({"system": system_prompt, "human": user_prompt})

print(response)