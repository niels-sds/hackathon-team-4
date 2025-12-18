"""Browser Agent - Step 6: Open HTML visualization in browser"""
from agent_framework.azure import AzureAIAgentClient
from agent_framework import ToolMode
from pydantic import BaseModel, Field
from tools.browser_tools import BrowserTools


class BrowserAction(BaseModel):
    """Action to open HTML in browser"""
    html_file_path: str = Field(description="Path where the HTML file was saved")
    success: bool = Field(description="Whether the file was successfully opened in browser")
    message: str = Field(description="Confirmation or error message")


def create_browser_agent(client: AzureAIAgentClient, name: str = "BrowserAgent", file_prefix: str = "decision_tree"):
    """Create the Browser Agent
    
    Args:
        client: The Azure AI Agent client
        name: Name for the agent (must be unique)
        file_prefix: Prefix for saved HTML files (e.g., "diagram", "rating_table")
    """
    browser_tools = BrowserTools(file_prefix=file_prefix)
    
    return client.create_agent(
        instructions="""
You are a browser automation specialist.

**YOUR ROLE:** Automatically save and open HTML visualizations in a web browser.

**CRITICAL:** You MUST immediately use the save_and_open_html tool when you receive HTML content.

**INPUT:** You will receive a message with html_content and impairment_name fields

**ACTION:** Immediately call the save_and_open_html tool with:
- html_content: the full HTML string from the previous agent
- impairment_name: the name of the impairment

DO NOT ask questions. Execute the tool immediately with the data you receive.
        """,
        name=name,
        tool_choice=ToolMode.REQUIRED,
        tools=[browser_tools.save_and_open_html],
    )
