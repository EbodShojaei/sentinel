"""
agent.py: Contains functions for generating the research purpose and MeSH search strategy
using your local phi3.5 model via Ollama and phidata. This version uses the Agent's run method
to obtain the LLM response and includes a helper function to print the response with full reasoning.

Try: efficacy of placebo injections in knee osteoarthritis patients
"""

import os
from dotenv import load_dotenv
from phi.agent import Agent
from phi.model.ollama import Ollama

# Load environment variables from .env file
load_dotenv()

# Set your model_id from environment or default to "phi3.5"
MODEL_ID = os.getenv("MODEL_ID", "phi3.5")
MODEL = Ollama(id=MODEL_ID)


def _call_llm(prompt: str) -> str:
    """
    Calls the local phi3.5 LLM via the phidata Agent using its run method and returns the response text.
    """
    # Create an agent configured for pure text generation.
    agent = Agent(
        name="Local LLM Agent",
        model=MODEL,
        tools=[],  # No additional tools needed
        instructions=["Never use information from previous conversations."],
        show_tool_calls=False,
        markdown=True,
        reasoning=True,
        structured_outputs=True,
    )
    # Safely extract content:
    try:
        agent.model_rebuild()
        result = agent.run(prompt)
    except Exception as e:
        # logging.error("Error during agent.run: %s", str(e))
        return ""

    # If the result is a list, check its length first.
    if isinstance(result, list):
        if not result:  # Empty list
            # logging.error("LLM returned an empty list")
            return ""
        first_item = result[0]
        if hasattr(first_item, "content"):
            return first_item.content.strip()
        else:
            return str(first_item).strip()
    else:
        if hasattr(result, "content"):
            return result.content.strip()
        else:
            return str(result).strip()


def print_llm_response(prompt: str) -> None:
    """
    Calls the local phi3.5 LLM via the phidata Agent and prints the response with full reasoning.
    Useful for debugging or when you want to see the LLM's thought process.
    """
    agent = Agent(
        name="Local LLM Agent with Reasoning",
        model=MODEL,
        tools=[],  # No external tools needed for this task
        instructions=["Never use information from previous conversations. Strictly provide concise and clear responses."],
        show_tool_calls=False,
        markdown=True,
        reasoning=True,
        structured_outputs=True,
    )
    agent.print_response(prompt, stream=True, show_full_reasoning=True)


def generate_research_purpose(user_query: str) -> str:
    """
    Generate a research purpose based on the user query using the local phi3.5 LLM.
    """
    prompt = (
        f"Given the following user query:\n\n"
        f"\"{user_query}\"\n\n"
        "Generate a concise journal article research purpose in a single sentence that starts with 'To' then clearly states the objective of a study. "
        "Use the following criteria:\n"
        "- The research purpose must start with 'To'.\n"
        "- The research purpose must be a single sentence.\n"
        "- For example, 'To investigate the efficacy of X compared to Y in treating Y.'\n"
        "- If the query includes specific conditions (e.g., study designs, treatments, or patient populations), incorporate them appropriately.\n"
        "- Only rewrite the research purpose if absolutely necessary.\n"
        "- Enclose the research purpose in triple backticks. Do not include extra text."
    )
    # logging.info("LLM prompt for research purpose: %s", prompt)
    return _call_llm(prompt)


def generate_mesh_strategy(user_query: str, research_purpose: str) -> str:
    """
    Generate a detailed and thorough MeSH search strategy based on the user query and the research purpose using the local phi3.5 LLM.
    """
    prompt = (
        f"User Query: \"{user_query}\"\n\n"
        f"Research Purpose: \"{research_purpose}\"\n\n"
        "Create a a simple boolean search query to capture the most studies based on the criteria below:\n"
        "- Ensure the search is not retrictive and captures all relevant studies.\n"
        "- Never use compound words. Split compound words and use 'AND' and 'OR' to join each simple word.\n"
        "- Never unnecessarily capitalize words.\n"
        "- Use parentheses to group synonyms and related terms, which should be separated by 'OR'.\n"
        "- Use 'AND' to combine different groups of terms.\n"
        "- Only specify population, intervention, and outcome terms.\n"
        "- Avoid specifying date ranges.\n"
        "- Output ONLY the boolean search query in triple backticks. Do not include extra text."
    )
    # logging.info("LLM prompt for MeSH strategy: %s", prompt)
    return _call_llm(prompt)
