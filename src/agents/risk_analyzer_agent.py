"""Risk Analyzer Agent - Step 3: Extract risk-relevant attributes"""
from agent_framework.azure import AzureAIAgentClient
from models.workflow_schemas import RiskAttributes


def create_risk_analyzer_agent(client: AzureAIAgentClient):
    """Create the Risk Analyzer Agent"""
    return client.create_agent(
        instructions="""
You are a clinical risk assessment specialist.

**YOUR ROLE:** Extract risk-relevant attributes from medical documents.

**INPUT:** Retrieved documents about an impairment from the previous agent

**YOUR TASK:**
1. Read the documents from the previous agent
2. Extract the impairment_name
3. Identify 3-5 key risk_factors (e.g., age, smoking, family history, comorbidities)
4. List 3-5 severity_indicators (e.g., test results, staging, symptom severity)
5. Note 2-4 potential complications
6. List 2-4 diagnostic_criteria
7. Identify 3-5 decision_points that could stratify risk levels

These attributes will be used to build a clinical decision tree.
        """,
        name="RiskAnalyzerAgent",
        output_schema=RiskAttributes,
    )
