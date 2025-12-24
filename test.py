from datapizza.tools.duckduckgo import DuckDuckGoSearchTool
from datapizza.clients.openai import OpenAIClient
from datapizza.tracing import ContextTracing
from datapizza.agents.agent import Agent
from datapizza.tools import tool




@tool
def get_weather(news: str, category: str) -> str:
    
    return f""" Category: {category} 
                News: {news}"""


news_agent = Agent(
    name="news_expert",
    client=client,
    system_prompt="""You are a news expert specialized in funny and absurd news stories.

                    When providing news, you must classify each story into ONE of these categories:
                        - National Funny: Funny news from Italy
                        - International Funny: Funny news from around the world
                        - National Absurd: Absurd/bizarre news from Italy  
                        - International Absurd: Absurd/bizarre news from around the world

                    Always specify the category when using the tool.""",
    tools=[get_weather]
)

web_search_agent = Agent(
    name="web_search_expert",
    client=client,
    system_prompt="You are a web search expert. You can search the web for information.",
    tools=[DuckDuckGoSearchTool()]
)

# Orchestrator Agent
report_agent = Agent(
    name="report",
    client=client,
    system_prompt="You are a report planner. You should provide a report for the user with the latest news. Make sure to provide a detailed report with the funniest and more absurd news from all over the world."
)

report_agent.can_call([news_agent, web_search_agent])

with ContextTracing().trace("AI_news_tracing"):
    response = report_agent.run(
        "I need the latest funny and absurd news report."
    )


# print(response.text)
