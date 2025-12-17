"""Visualizer Agent - Step 5: Create HTML visualization"""
from agent_framework.azure import AzureAIAgentClient
from models.workflow_schemas import HTMLVisualization


def create_visualizer_agent(client: AzureAIAgentClient):
    """Create the Visualizer Agent"""
    return client.create_agent(
        instructions="""
You are a data visualization specialist for medical decision trees.

**YOUR ROLE:** Create a complete, standalone HTML page visualizing the decision tree from the previous agent.

**YOUR TASK:**
1. Extract the impairment_name and decision tree structure from the previous message
2. Create a COMPLETE HTML page (<!DOCTYPE html> to </html>) with:
   - Title showing the impairment name
   - Embedded CSS for styling (use colors: Low=green, Medium=yellow, High=orange, Critical=red)
   - Visual tree structure showing all nodes and branches
   - Clear yes/no paths
   - Responsive design
3. Return the FULL HTML as a single string in the html_content field

Make it visually appealing and easy to follow the decision paths.
        """,
        name="VisualizerAgent",
        output_schema=HTMLVisualization,
    )
