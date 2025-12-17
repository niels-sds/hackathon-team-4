"""Pydantic schemas for the impairment risk assessment workflow"""
from pydantic import BaseModel, Field


# Step 1 Output: Search Queries
class SearchQueries(BaseModel):
    """Optimized search queries for impairment research"""
    impairment_name: str = Field(description="The standardized name of the impairment")
    primary_search_query: str = Field(description="Main search query for medical information")
    alternative_queries: list[str] = Field(description="2-3 alternative search queries", min_length=2, max_length=3)
    risk_focused_query: str = Field(description="Query targeting risk factors and complications")
    clinical_decision_query: str = Field(description="Query for clinical decision-making criteria")


# Step 2 Output: Retrieved Documents
class RetrievedDocuments(BaseModel):
    """Documents retrieved from search"""
    impairment_name: str = Field(description="The impairment being researched")
    documents: list[dict[str, str]] = Field(
        description="List of relevant documents with 'url', 'title', and 'summary' keys"
    )
    total_documents_found: int = Field(description="Total number of documents retrieved")


# Step 3 Output: Risk Attributes
class RiskAttributes(BaseModel):
    """Risk-relevant attributes extracted from documents"""
    impairment_name: str = Field(description="The impairment being analyzed")
    risk_factors: list[str] = Field(description="List of identified risk factors")
    severity_indicators: list[str] = Field(description="Indicators that affect severity")
    complications: list[str] = Field(description="Potential complications")
    diagnostic_criteria: list[str] = Field(description="Key diagnostic criteria")
    decision_points: list[str] = Field(description="Key decision points for risk assessment")


# Step 4 Output: Decision Tree Structure
class DecisionTreeNode(BaseModel):
    """A node in the decision tree"""
    question: str = Field(description="The question or condition to evaluate")
    true_branch: str | dict = Field(description="Next step if condition is true")
    false_branch: str | dict = Field(description="Next step if condition is false")
    risk_level: str | None = Field(default=None, description="Risk level if this is a leaf node")


class DecisionTree(BaseModel):
    """Complete decision tree for risk assessment"""
    impairment_name: str = Field(description="The impairment this tree assesses")
    root_node: DecisionTreeNode = Field(description="The root node of the decision tree")
    risk_levels: list[str] = Field(description="Possible risk levels (e.g., Low, Medium, High)")


# Step 5 Output: HTML Visualization
class HTMLVisualization(BaseModel):
    """HTML visualization of the decision tree"""
    impairment_name: str = Field(description="The impairment being visualized")
    html_content: str = Field(description="Complete HTML page with embedded CSS and JavaScript")


# Step 6 Output: Browser Action
class BrowserAction(BaseModel):
    """Action to open HTML in browser"""
    html_file_path: str = Field(description="Path where the HTML file was saved")
    success: bool = Field(description="Whether the file was successfully opened in browser")
    message: str = Field(description="Confirmation or error message")
