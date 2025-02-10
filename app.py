import os
import ast

import chainlit.message
import requests
from bs4 import BeautifulSoup
from typing import List

import chainlit as cl
from langchain_openai import ChatOpenAI

from models import LlmModels, SearchResult

GOOGLE_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
GOOGLE_CX = os.getenv("GOOGLE_SEARCH_CX")
BASE_URL = "https://api.deepinfra.com/v1/openai"
get_llm = lambda: ChatOpenAI(
        model=LlmModels.DEEPSEEK_V3.value,
        temperature=0.23,
        base_url=BASE_URL,
        api_key=os.getenv("DEEPINFRA_API_KEY"),
        timeout=None
    )

##########################################
# Agent 0: Search Planner                #
##########################################
def search_planner(prompt: str) -> List[str]:
    """
    Analyzes the user prompt and produces a list of research topics.
    Example output: ["Topic 1", "Topic 2", "Topic 3"]

    This implementation uses an LLM to extract topics.
    """
    llm = get_llm()
    planner_prompt = f"""
    Extract a list of research topics from the following text. Identify what the user wants to search for and return a maximum of 5 topics as a clear Python list.

Rules:
- If the user's intent is unclear or the input is meaningless, return an empty list.
- The research topics must be **searchable on the web**, clearly defined, and useful.
- Topics should be **broad and researchable**, avoiding overly specific or vague phrases.
- Output **only a Python list**—no explanations, no additional text.

Examples:

Input:
"What do you think about the relationship between quantum computers and AI?"
Output:
["Quantum computers and AI relationship", "Quantum AI algorithms", "Fundamentals of quantum computing", "AI optimization techniques", "Quantum hardware and applications"]

Input:
"lsdlsdlfjlsdfj"
Output:
[]

Now, generate a Python list following these rules for the given text:

{prompt}"""
    topics_str = llm.invoke(planner_prompt)
    try:
        topics = ast.literal_eval(topics_str.content)
        if isinstance(topics, list) and topics:
            return topics
        else:
            return [prompt]
    except Exception as e:
        return [prompt]


##########################################
# Agent 1: Search Agent                  #
##########################################
# @cl.step(type="tool")
def search_agent(query: str) -> List[SearchResult]:
    """
    Performs a web search for the given query using the Google Custom Search API.
    Returns a list of dictionaries with keys: 'title', 'url', and 'snippet'.
    """
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CX,
        "q": query,
        "num": 5  # Number of search results to retrieve
    }
    url = "https://www.googleapis.com/customsearch/v1"
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        items = data.get("items", [])
        results = []
        for item in items:
            results.append(
                SearchResult.from_google_result(item)
            )
        return results
    else:
        print(f"Google Search API error: {response.status_code} - {response.text}")
        return []



##########################################
# Pydantic Model for Search Results      #
##########################################



##########################################
# Helper Function: Fetch Content         #
##########################################
# @cl.step(type="tool")
def fetch_content(url: str) -> str:
    """
    Fetches the HTML content from a URL and extracts text using BeautifulSoup.
    """
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            paragraphs = soup.find_all("p")
            text = "\n".join(p.get_text() for p in paragraphs)
            return text
        else:
            return ""
    except Exception as e:
        print(f"Error fetching URL: {url} - {e}")
        return ""


##########################################
# Agent 2: Result Extraction & Relevancy Filter
##########################################
# @cl.step(type="tool")
def result_extraction_and_filter_agent(search_results: List[SearchResult], query: str) -> List[SearchResult]:
    """
    Parses the raw search results and, for each result, fetches the content from its URL.
    Then applies a relevancy filter to select the best results using LLM evaluation.
    """

    llm = get_llm()
    filter_prompt = f"""
    The following are search results for the query: {query}.
    Each result contains a title, URL, snippet, and extracted content.
    Your task is to analyze these results and determine the most relevant ones based on the query.
    Return a Python list of the top 3 most relevant results based on comprehensiveness and accuracy.
    {search_results}
    """
    relevant_results_str = llm.invoke(filter_prompt).content

    import json
    try:
        relevant_results = json.loads(relevant_results_str)
    except Exception as e:
        print(f"Error parsing LLM output: {relevant_results_str}")
        relevant_results = search_results[:3]

    results = []
    for item in relevant_results:
        content = fetch_content(item.url)
        print(content)
        result = item.set_content(content)
        results.append(result)

    return results

# @cl.step(type="tool")
async def report_generation_agent(query: str, results: List[SearchResult]):
    """
    Generates a comprehensive Markdown report (styled like a Wikipedia article)
    based on the search query and the extracted results.
    Streams the output gradually to improve responsiveness.
    """
    context = f"**Search Query:** {query}\n\n"
    context += "**Search Results:**\n"
    for res in results:
        context += f"### {res.title}\n"
        context += f"**URL:** {res.url}\n\n"
        context += f"**Snippet:** {res.snippet}\n\n"
        excerpt = (res.content[:200] + "...") if res.content else "Content could not be retrieved."
        context += f"**Content (Excerpt):** {excerpt}\n\n"

    prompt = f"""
Below is a search query along with its search results.
Using the information provided, please generate a comprehensive, fluent, and informative Wikipedia-style article in Markdown format.
Insert references inside the references section
{context}

Article:
"""

    llm = get_llm()
    async for chunk in llm.astream(prompt):
        yield chunk

##########################################
# Chainlit Integration
##########################################
@cl.on_chat_start
async def on_chat_start():
    """
    Sends a welcome message when the chat starts.
    """
    await cl.Message(
        content="Welcome! Your past conversations will be displayed in the left panel."
    ).send()


@cl.on_message
async def handle_message(chainlit_message: chainlit.message.Message):
    """
    Processes the user's message by executing the following steps:

      1. **Search Planner:** Extract research topics from the prompt.
      2. **Search Agent:** Perform web searches for each topic.
      3. **Result Extraction & Relevancy Filter:** Process and filter the results.
      4. **Report Generation:** Create a comprehensive report.
    """
    steps = [
        "Step 1: Received the user's query.",
        "Step 2: Running Search Planner..."
    ]
    # for step in steps:
    #     await cl.Message(content=step).send()

    # Agent 0: Search Planner
    message = chainlit_message.content
    report_msg = cl.Message(content="")
    async with cl.Step(name="Seep Desearch") as parent_step:
        topics = search_planner(message)
        async with cl.Step(name="Search Agent"):
            parent_step.name = "Search Agent"
            await parent_step.update()
            all_results = []
            # Agent 1: Search Agent (for each topic)
            for topic in topics:
                search_results = search_agent(topic)
                all_results.extend(search_results)
                
        async with cl.Step(name="Result Extraction & Relevancy Filter"):
            parent_step.name = "Result Extraction & Relevancy Filter"
            await parent_step.update()
            filtered_results = result_extraction_and_filter_agent(all_results, message)
            

        async with cl.Step(name="Report Generation"):
            parent_step.name = "Report Generation"
            await parent_step.update()
            async for chunk in report_generation_agent(message, filtered_results):
                await report_msg.stream_token(chunk.content)
        parent_step.name = "Seep Desearch – Completed!"
        await parent_step.update()
    await report_msg.send()


##########################################
# Main: Run the Chainlit App
##########################################
if __name__ == "__main__":
    # To run this app, you can either use the Chainlit CLI:
    #     chainlit run app.py --watch
    # or run it directly:
    #     python app.py
    from chainlit.cli import main

    main()
    # SANTORİNİ'DE YAŞAYAN BİR UYGARLIK VARDI MÖ 1700 CİVARLARINDA. O uygarlığın başlangıcı, yükselişini ve düşüşünü anlat.