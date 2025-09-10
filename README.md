# Agentic Task Manager

This project is an agentic task manager that uses Langchain and Todoist to help you manage your tasks. The agent is powered by Google's Gemini model and can understand natural language to add tasks to your Todoist.

## Features

*   Add tasks to your Todoist using natural language.
*   Powered by Google's Gemini model for natural language understanding.
*   Easily extensible with new tools and capabilities.

## Getting Started

### Prerequisites

*   Python 3.8+
*   Todoist account and API key
*   Google Gemini API key

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/agentic-task-manager.git
    ```
2.  Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Create a `.env` file in the root of the project and add your API keys:
    ```
    TODOIST_API_KEY=your_todoist_api_key
    GEMINI_API_KEY=your_gemini_api_key
    ```

## Usage

To run the agent, simply execute the `main.py` file:

```bash
python main.py
```

The agent will then prompt you to add a task. For example, you can say:

```
"add a new task to buy dinner for tonight, and dog food for the week."
```

The agent will then add the task to your Todoist.

## Configuration

The agent is configured in the `main.py` file. You can change the following parameters:

*   `model`: The Gemini model to use.
*   `temperature`: The temperature of the model.
*   `system_prompt`: The system prompt for the agent.
