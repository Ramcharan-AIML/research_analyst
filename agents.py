# pyrefly: ignore [missing-import]
from langchain.agents import create_agent
# pyrefly: ignore [missing-import]
from langchain_mistralai import ChatMistralAI
# pyrefly: ignore [missing-import]
from langchain_core.prompts import ChatPromptTemplate
# pyrefly: ignore [missing-import]
from langchain_core.output_parsers import StrOutputParser
from tools import web_search, scrape_url
import os
from dotenv import load_dotenv

load_dotenv()

# LLM Model setup
llm = ChatMistralAI(
    model = "mistral-medium-latest",
    temperature = 0.1
)


# 1st Agent - this agent is for searching the urls in web(internet)
def build_search_agent():
    return create_agent(
        model = llm,
        tools = [web_search]
    )


# 2nd Agent - this agent is for scraping those urls from web
def build_reader_agent():
    return create_agent(
        model = llm,
        tools = [scrape_url]
    )


# Maintaing the chains

# Writer Chain

writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reports"),
    ("human", """Write a detailed research report on the topic below.
    
    Topic : {topic}

    Research Gathered: {research}

    Structure the report as:
    - Introduction
    - Key findings (minimum 3 well-explained points)
    - conclusion
    - Sources (list all URLs found in the research)

    Be detailed , factual and professioanl.
    """),
])

writer_chain = writer_prompt | llm | StrOutputParser()   #LCEL pipline syntax for chaining the things


# Critic Chain - this chain is for structure the gathered report from the writer chain
critic_prompt = ChatPromptTemplate([
    ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

    Report:{report}

    Respond in this exact format:

    Score: X/10
    Strengths:
    - ....
    - ....

    Areas to Improve:
    - ....
    - ....

    One line verdict:
    ....
    """),
])


critic_chain = critic_prompt | llm | StrOutputParser()



