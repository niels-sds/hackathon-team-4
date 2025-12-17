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

**OUTPUT:** A structured decision tree with:
- Root node asking the most important risk question
- Branch nodes with yes/no decision points
- Leaf nodes with risk level classifications

The tree should be logical, clinically sound, and use the most significant risk factors.
User will provide format example.
        """,
        name="DecisionTreeAgent",
        output_schema=DecisionTree,
    )
