from agents import build_reader_agent, build_search_agent, writer_chain , critic_chain


def run_research_pipeline(topic : str) -> dict:

    state = {}

    # Search Agent working
    print("\n" + "=" * 50)
    print("step 1 - search agent is working ...")
    print("=" * 50)

    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages" : [("user", f"Find recent, reliable and detailed information about: {topic}")]
    })

    state["search_results"] = search_result['messages'][-1].content   # We need to grab the last message from the state dictionary

    print("\n search result ", state['search_results'])




