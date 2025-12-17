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

# from azure.identity.aio import AzureCliCredential
from dotenv import load_dotenv

from models.workflow_schemas import RetrievedDocuments

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(message)s")

search_agent = AzureAIAgentClient().create_agent(
    instructions="""
                You are a medical document retrieval specialist.

                **YOUR ROLE:** Based on search queries from the previous agent, return relevant medical documents.

                **INPUT:** The previous agent provided search queries for an impairment

                **SEARCH CRITERIA:**
                    - Search only in reputable sources of medical information: medical journals, universities and health organizations.
                    - Your search is worldwide.
                    - Search for documents with information on mortality risk, permanent or temporary disability and morbidity risk.
                      For morbidity, only look into the following medical conditions:
                      cancer, dementia,diabetes, heart attack,Parkinson's, stroke, organ transplant (MOT) and renal failure.
                    - Documents do not need to be disease specific.
                
                **YOUR TASK:**
                1. Extract the impairment_name from the previous message
                2. Use the SEARCH CRITERIA to retrieve maximum 20 relevant documents 
                3. For each document provide:
                - url: A realistic medical source URL (e.g., from WHO, NCCN, CDC, NIH)
                - title: A relevant document title
                - summary: 2-3 sentences about risk factors, diagnostic criteria, or complications
                
                Return results that would be useful for building a risk assessment decision tree
                """,
    name="SearchAgent",
    output_schema=RetrievedDocuments
)

# serve(entities=[search_agent], port=8090, auto_open=True, tracing_enabled=True)
