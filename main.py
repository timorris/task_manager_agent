import os
import traceback
from dotenv import load_dotenv

from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.prompts import MessagesPlaceholder
from todoist_api_python.api import TodoistAPI

load_dotenv()

todoist_api_key = os.getenv("TODOIST_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")
todoist = TodoistAPI(todoist_api_key)

@tool
def add_task(task, desc=None):
    """ Add a new task to the user's Todoist task list. Use this when the user wants to add or create a task
    with a description to buy from the closest store, if the task is to buy something.
    """
    try:
        todoist.add_task(content=task,
                         description=desc)
    except Exception as e:
        tb = traceback.format_exc(limit=1)
        return f"Failed to add task '{task}': {e.__class__.__name__} - {e}.\nTrace: {tb}"

@tool
def show_tasks():
    """ Returns a list of all the tasks in the user's Todoist task list. Use this tool when the user wants to see their tasks. """
    try:
        tasks = []
        results_paginated = todoist.get_tasks()
        for task_list in results_paginated:
            for task in task_list:
                tasks.append(task.content)
        return tasks
    except Exception as e:
        tb = traceback.format_exc(limit=1)
        return f"Failed to get tasks: {e.__class__.__name__} - {e}.\nTrace: {tb}"

tools = [add_task, show_tasks]

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=gemini_api_key,
    temperature=0.3
)

system_prompt = """ You are a helpful assistant. 
You will help the user add tasks. 
When adding a task, if the same task already exists, do not add a new one.
You will help the user show existing tasks. If the user asks to show the tasks, for example, "show tasks", print them in a bullet point format.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder("history"),
    ("user", "{input}"),
    MessagesPlaceholder("agent_scratchpad")
])

agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

history = []
while True:
    user_input = input("You: ")

    if user_input == "exit":
        break

    response = agent_executor.invoke({"input": user_input, 'history': history})
    print(response['output'])
    history.append(HumanMessage(content=user_input))
    history.append(AIMessage(content=response['output']))

