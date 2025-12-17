""""
You are a medical document retrieval specialist.

**YOUR ROLE:** Based on search queries from the previous agent, return relevant medical documents.

**INPUT:** The previous agent provided search queries for an impairment

**YOUR TASK:**
1. Extract the impairment_name from the previous message
2. Create 3-5 mock documents relevant to the impairment's risk assessment
3. Each document should have:
   - url: A realistic medical source URL (e.g., from WHO, NCCN, CDC, NIH)
   - title: A relevant document title about the impairment
   - summary: 2-3 sentences about risk factors, diagnostic criteria, or complications

Return documents that would be useful for building a risk assessment decision tree.
        name="SearchAgent",
        output_schema=RetrievedDocuments,
    )
"""

# This initializes a search agent to gather articles and and abstracts from the internet.
# import os
# from agent_framework.devui import serve
import logging

from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(message)s")

search_agent = AzureAIAgentClient().create_agent(
    instructions="""
                
                """,
    name="SearchAgent",
    output_schema=RetrievedDocuments
)

# serve(entities=[search_agent], port=8090, auto_open=True, tracing_enabled=True)
