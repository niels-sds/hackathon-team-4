"""Visualizer Agent - Step 5: Create HTML visualization"""
from agent_framework.azure import AzureAIAgentClient
from models.workflow_schemas import HTMLVisualization


def create_visualizer_agent(client: AzureAIAgentClient):
    """Create the Visualizer Agent"""
    return client.create_agent(
        instructions="""
You are a data visualization specialist for medical decision trees.

**YOUR ROLE:** Convert a decision tree into a diagram JSON format and embed it in HTML.

**INPUT:** Decision tree structure and source_documents from the previous agent

**YOUR TASK:**

1. Transform the decision tree into this JSON format:
   - Create "nodes" array where each decision point and outcome is a node:
     * id: unique number (1, 2, 3...)
     * title: "Rule / Decision Point" for questions, "Assignment" for outcomes
     * content: The question text or risk level assignment
     * type: "code" for outcomes, omit for questions
   
   - Create "connections" array linking nodes:
     * source: id of parent node
     * target: id of child node
     * label: "True" or "False"

2. Generate the complete HTML using this EXACT template:

<!DOCTYPE html>
<html lang="en">
  <head>
    <title>{{IMPAIRMENT_NAME}} Risk Assessment</title>
    <script
      src="https://cdn.scordigital.solutions/components/latest/themes/brms-119d236af7cd.js"
      data-turbo-track="reload"
    ></script>
    <script
      src="https://cdn.scordigital.solutions/components/latest/index.js"
      defer
      data-turbo-track="reload"
    ></script>
    <style>
      body { font-family: Arial, sans-serif; margin: 20px; }
      .sources { background: #f5f5f5; padding: 15px; margin-bottom: 20px; border-radius: 8px; }
      .sources h2 { margin-top: 0; }
      .sources a { display: block; margin: 5px 0; color: #0066cc; }
    </style>
  </head>
  <body>
    <h1>{{IMPAIRMENT_NAME}} Risk Assessment Decision Tree</h1>
    
    <div class="sources">
      <h2>Sources</h2>
      {{SOURCE_LINKS}}
    </div>

    <rmv-styles
      asset-path="https://cdn.scordigital.solutions/assets"
    ></rmv-styles>
    <rmv-diagram readonly><template></template></rmv-diagram>

    <script>
      document.addEventListener("DOMContentLoaded", function () {
        const diagram = document.querySelector("rmv-diagram");
        diagram.data = {{DIAGRAM_JSON}};
      });
    </script>
  </body>
</html>

3. Replace placeholders:
   - {{IMPAIRMENT_NAME}}: the impairment name
   - {{SOURCE_LINKS}}: HTML <a> tags for each source document
   - {{DIAGRAM_JSON}}: the complete JSON object with nodes and connections

Return the complete HTML as a single string in html_content field.
        """,
        name="VisualizerAgent",
        output_schema=HTMLVisualization,
    )
