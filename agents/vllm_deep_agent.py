import asyncio
from utils.coloring import print_user, print_assistant, print_environment
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langgraph.checkpoint.memory import MemorySaver  # For persistence
from langgraph.types import Command
from copy import deepcopy
import json
import os
from langchain_openai import ChatOpenAI
from langchain_community.llms import VLLM





workdir = os.getcwd()

def print_message(response):
    # Print the agent's response
    for msg in response["messages"]:
        print(type(msg).__name__)
        if type(msg) == HumanMessage:
            print_user(msg.content)
        elif type(msg) == AIMessage:
            print_assistant(msg.content)
            for elm in msg.tool_calls:
                print("Tool calls:")
                print_assistant(json.dumps(elm, indent=4))
        elif type(msg) == ToolMessage:
            for elm in msg.content:
                if elm["type"] == "text":
                    print_environment(elm["text"])
        print("-" * 50)



def process_interrupts(response):
    interrupts = response["__interrupt__"][0].value
    decisions = []
    for action_request, review_config in zip(interrupts["action_requests"], interrupts["review_configs"]):
        print(f"{len(interrupts["action_requests"])} user decisions are required.\n{'-' * 10}")
        input_str = "\n".join([f"{key}: {val}" for key, val in action_request["args"].items()])
        print(
                f"Tool {review_config["action_name"]} requires a user decision.\nCurrent input:\n{input_str}\n{'-' * 10}\nOptions: {review_config["allowed_decisions"]}\n{'-' * 10}")
        user_input = input("Please enter your decision:\n")
        if "edit" in user_input.lower():
            user_arg = input(f"Which argument of {review_config["action_name"]} do you want to edit?")
            user_value = input("What value do you want to set?")
            initial_args = action_request["args"]
            updated_args = deepcopy(initial_args)
            updated_args.update({user_arg: user_value})

            decisions.append({
                    "type": "edit",
                    "edited_action": {
                        "name": review_config["action_name"],  # Must include the tool name
                        "args": updated_args
                    }
                })
        else:
            decisions.append(
                    {"type": user_input.strip()}
            )
    return decisions


def check_stopcondition(messages: list[dict[str, str]]) -> bool:
    # if the maximum conversation length is exceeded
    if len(messages) > 20:
        return True
    # if the user indicates that they are done
    if messages[-1]["content"].lower() in ["stop", "done", "exit"]:
        return True
    return False


def format_ai_message(message) -> str:
    outstr = message.content

    if type(message) == AIMessage and len(message.tool_calls) > 0:
        outstr += "\nThe following tool calls were executed:\n"
        for tc in message.tool_calls:
            outstr += ("\n")
            outstr += (json.dumps(tc, indent=4))
    return outstr



def format_model_answer(message: dict[str, str]) -> str:
    """
    format the model answer to be displayed to the user
    """

    s = format_ai_message(message)
    s += "\n"
    return s


async def main():
    client = MultiServerMCPClient(
        {
            "simple_server": {
                "transport": "stdio",  # Local subprocess communication
                "command": "python",
                "args": [os.path.join(workdir, "servers/simple_server.py")]
            },
            "mensa_server": {
                "transport": "stdio",  # Local subprocess communication
                "command": "python",
                "args": [os.path.join(workdir, "servers/parse_mensaar.py")]
            }
        }
    )
  
    config = {
        "configurable": {
            "thread_id": "my-session-1"
        }
    }

    tools = await client.get_tools()

    llm = VLLM(
        model="qwen/qwen3.5:0.8b",
        trust_remote_code=True,  # mandatory for hf models
        max_new_tokens=128,
        top_k=10,
        top_p=0.95,
        temperature=0.8
    )

    agent = create_deep_agent(
        #"gpt-4o-mini",
        #"ollama:qwen3.5:0.8b",
        model=llm,
        tools=tools,
        backend=FilesystemBackend(
            root_dir=workdir,  # Absolute path to accessible directory
            virtual_mode=True  # Recommended: Normalize/sanitize paths
        ),
        checkpointer=MemorySaver(),  # Required for multi-turn / persistence
        interrupt_on={  # Optional: Human approval for file ops
            "read_file": True,
            "write_file": True,
            "edit_file": True,
        }
    )

    userfacing_prompt = "Hello, I am your DeepAgent. How may I help you?\n"

    # first turn
    user_message = input(userfacing_prompt)
    messages =  [{"role": "user", "content": user_message.strip()}]
    stopcondition = False

    while not stopcondition:
        response = await agent.ainvoke(
            {"messages": messages},
            config=config
        )


        print_message(response)

        # check for interrupts
        if "__interrupt__" in response:
            decisions = process_interrupts(response)

            # Resume execution with decisions
            response = agent.invoke(
                Command(resume={"decisions": decisions}),
                config=config
            )

        # collect the result
        messages = response["messages"]

        # initiate the new turn
        userfacing_prompt = f"{format_model_answer(messages[-1])}"
        user_message = input(userfacing_prompt)
        messages.append({"role": "user", "content": user_message.strip()})
        stopcondition = check_stopcondition(messages)


if __name__ == "__main__":
    asyncio.run(main())