import asyncio
from langchain_ollama import ChatOllama 
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

# async since some operations are async
async def main():
    # The LLM layer - we can change the model over here and can be extended to use a different config
    llm = ChatOllama(model="mistral", temperature=0)

    # The tool layer - we create a clent side MCP connection
    client = MultiServerMCPClient({
        "agent-zero": {
            "url": "http://localhost:8000/sse", 
            "transport": "sse"
        }
    })
    # await allows the connection to be alive for the agent to interact with the mcp server
    # client queries the mcp server for the available tools
    tools = await client.get_tools()

    # creates an orchestrator that wraps the model and tools
    # internally decides whether it needs to call a tool to answer 
    # the query and also execute the tool
    agent = create_agent(llm, tools)

    print("\n Agent Zero is online. Type `quit` to exi.\n")

    while True:

        # handling user input
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit"):
            print("Shutting down Agent Zero.")
            break
        if not user_input: continue

        print("\nAgent Zero thinking...\n")
        # this is the input to the agent - a state of object messages
        response = await agent.ainvoke({
            "messages": [HumanMessage(content=user_input)]
        })
        final = response["messages"][-1].content
        print(f"Agent Zero: {final}\n")

if __name__ == "__main__":
    asyncio.run(main())
