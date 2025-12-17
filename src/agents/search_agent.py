"""Search Agent - Step 2: Retrieve and filter medical documents"""
from agent_framework.azure import AzureAIAgentClient
from models.workflow_schemas import RetrievedDocuments


def create_search_agent(client: AzureAIAgentClient):
    """Create the Search Agent"""
    return client.create_agent(
        instructions="""
You are a medical document retrieval specialist.

**YOUR ROLE:** Based on search queries, retrieve and filter relevant medical documents.

**INPUT:** Search queries from the previous agent

**OUTPUT:** List of relevant documents (the user will provide source URLs)
For now, acknowledge the queries and prepare to receive document links.

Format each document with:
- url: The document URL
- title: Document title
- summary: Brief 2-3 sentence summary of relevance

Keep only documents directly relevant to the impairment's risk assessment.
        """,
        name="SearchAgent",
        output_schema=RetrievedDocuments,
    )
