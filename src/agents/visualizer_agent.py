"""Visualizer Agent - Step 5: Create HTML visualization"""
from agent_framework.azure import AzureAIAgentClient
from models.workflow_schemas import HTMLVisualization


def create_visualizer_agent(client: AzureAIAgentClient):
    """Create the Visualizer Agent"""
    return client.create_agent(
        instructions="""
You are a data visualization specialist for medical decision trees.

**YOUR ROLE:** Create an interactive HTML visualization of the decision tree.

**INPUT:** Decision tree structure from previous agent

**OUTPUT:** Complete HTML page with:
- Embedded CSS for styling
- JavaScript for interactivity (if needed)
- Clear visual representation of the decision tree
- Color coding for risk levels

User will provide HTML example format.
        """,
        name="VisualizerAgent",
        output_schema=HTMLVisualization,
    )
