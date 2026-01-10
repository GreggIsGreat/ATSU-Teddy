from freeflow_llm import FreeFlowClient

with FreeFlowClient() as client:
    response =client.chat(
        messages=[{"role": "user", "content": "Name and List the most popular algorithms used to trade some of the least popular currencies and why they are used"}]
    )
    print(response.content)