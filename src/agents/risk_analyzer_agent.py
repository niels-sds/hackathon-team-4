"""Risk Analyzer Agent - Step 3: Extract risk-relevant attributes"""
from agent_framework.azure import AzureAIAgentClient
from models.workflow_schemas import RiskAttributes


def create_risk_analyzer_agent(client: AzureAIAgentClient):
    """Create the Risk Analyzer Agent"""
    return client.create_agent(
        instructions="""
You are a clinical risk assessment specialist.

**YOUR ROLE:** Extract risk-relevant attributes from medical documents.

**INPUT:** Retrieved documents about an impairment

**OUTPUT:** Structured risk attributes including:
- Risk factors that increase likelihood or severity
- Severity indicators (lab values, symptoms, progression markers)
- Potential complications
- Diagnostic criteria
- Key decision points for risk stratification

Focus on measurable, actionable attributes that can inform a decision tree.
        """,
        name="RiskAnalyzerAgent",
        output_schema=RiskAttributes,
    )
