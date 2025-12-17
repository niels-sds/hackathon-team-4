"""Decision Tree Agent - Step 4: Create decision tree structure"""
from agent_framework.azure import AzureAIAgentClient
from models.workflow_schemas import DecisionTree


def create_decision_tree_agent(client: AzureAIAgentClient):
    """Create the Decision Tree Agent"""
    return client.create_agent(
        instructions="""
You are a clinical decision tree architect.

**YOUR ROLE:** Create a decision tree for risk assessment based on identified attributes.

**INPUT:** Risk attributes from the previous agent

**YOUR TASK:**
1. Extract impairment_name and all risk attributes
2. Build a root_node with the most important decision question
3. Create nested decision nodes, each with:
   - question: A clear yes/no question about a risk factor
   - true_branch: Either another node (as dict) or a risk level string
   - false_branch: Either another node (as dict) or a risk level string  
   - risk_level: null for decision nodes, or "Low"/"Medium"/"High"/"Critical" for leaf nodes
4. Make the tree 2-3 levels deep
5. Set risk_levels to ["Low", "Medium", "High", "Critical"]

Example structure:
{
  "question": "Age > 65?",
  "true_branch": {"question": "Smoker?", "true_branch": "High", "false_branch": "Medium"},
  "false_branch": "Low"
}
        """,
        name="DecisionTreeAgent",
        output_schema=DecisionTree,
    )
