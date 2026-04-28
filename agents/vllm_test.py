import argparse
from langchain.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI



def main(args):
    llm = ChatOpenAI(
        model=args.model,
        base_url=args.base_url,
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


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base_url", type=str, default="http://localhost:8080/v1")
    parser.add_argument("--model", type=str, default="/scratch/common_models/Qwen3-8B")
    args = parser.parse_args()

    main(args)
