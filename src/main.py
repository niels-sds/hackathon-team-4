import os
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential
from dotenv import load_dotenv
from agent_framework.devui import serve
from agent_framework import WorkflowBuilder
from agents.search_prompt_agent import create_search_prompt_agent
from agents.search_agent import create_search_agent
from agents.risk_analyzer_agent import create_risk_analyzer_agent
from agents.decision_tree_agent import create_decision_tree_agent
from agents.visualizer_agent import create_visualizer_agent
from agents.rating_table_agent import create_rating_table_agent
from agents.browser_agent import create_browser_agent
import logging

load_dotenv()


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    
    settings = {
        "project_endpoint": os.environ["AZURE_AI_PROJECT_ENDPOINT"],
        "model_deployment_name": os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        "credential": AzureCliCredential(),
    }
    
    client = AzureAIAgentClient(**settings)
    
    # Create all agents
    search_prompt_agent = create_search_prompt_agent(client)
    search_agent = create_search_agent(client)
    risk_analyzer_agent = create_risk_analyzer_agent(client)
    decision_tree_agent = create_decision_tree_agent(client)
    
    # Two visualizer agents
    visualizer_agent = create_visualizer_agent(client)
    rating_table_agent = create_rating_table_agent(client)
    
    # Two browser agents (one for each visualizer)
    diagram_browser_agent = create_browser_agent(client, name="DiagramBrowserAgent", file_prefix="diagram")
    table_browser_agent = create_browser_agent(client, name="TableBrowserAgent", file_prefix="rating_table")
    
    # Build workflow with parallel visualization branches
    workflow = (
        WorkflowBuilder()
        # Register all agents
        .add_agent(search_prompt_agent)
        .add_agent(search_agent)
        .add_agent(risk_analyzer_agent)
        .add_agent(decision_tree_agent)
        .add_agent(visualizer_agent)
        .add_agent(rating_table_agent)
        .add_agent(diagram_browser_agent)
        .add_agent(table_browser_agent)
        # Sequential chain: search -> analyze -> decision tree
        .add_edge(search_prompt_agent, search_agent)
        .add_edge(search_agent, risk_analyzer_agent)
        .add_edge(risk_analyzer_agent, decision_tree_agent)
        # Fan out: decision tree -> both visualizers in parallel
        .add_fan_out_edges(decision_tree_agent, [visualizer_agent, rating_table_agent])
        # Each visualizer -> its own browser
        .add_edge(visualizer_agent, diagram_browser_agent)
        .add_edge(rating_table_agent, table_browser_agent)
        # Set the starting point
        .set_start_executor(search_prompt_agent)
        .build()
    )
    
    serve(entities=[workflow], port=8090, auto_open=True, tracing_enabled=True)


if __name__ == "__main__":
    main()