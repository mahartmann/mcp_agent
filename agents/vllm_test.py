from langchain.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

if __name__=="__main__":

    inference_server_url = "http://localhost:8080/v1"

    llm = ChatOpenAI(
        model="Gwen/Gwen3-8B",
        base_url=inference_server_url,
        max_tokens=5,
        temperature=0
    )
    messages = [
        SystemMessage(
            content="You are a helpful assistant that translates English to Italian."
        ),
        HumanMessage(
            content="Translate the following sentence from English to Italian: I love programming."
        ),
    ]
    response = llm.invoke(messages)
    print(response)
    