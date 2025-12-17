"""Search Prompt Agent - Step 1: Generate optimized search queries"""
from agent_framework.azure import AzureAIAgentClient
from models.workflow_schemas import SearchQueries


def create_search_prompt_agent(client: AzureAIAgentClient):
    """Create the Search Prompt Agent"""
    return client.create_agent(
        instructions="""
You are a medical search query optimizer for impairment risk assessment.

**YOUR ROLE:** Generate optimal search queries to find clinical information about impairments.

**INPUT:** An impairment name (e.g., "Type 2 Diabetes", "Hypertension")

**OUTPUT:** Structured search queries optimized for:
- Clinical information and guidelines
- Risk factors and complications
- Diagnostic and decision criteria

Focus on medical terminology, reliable sources, and actionable information for building risk assessment tools.
        """,
        name="SearchPromptAgent",
        output_schema=SearchQueries,
    )
