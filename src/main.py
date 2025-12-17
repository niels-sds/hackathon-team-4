import os
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential
from dotenv import load_dotenv
from agent_framework.devui import serve
from agent_framework import SequentialBuilder
from agents.search_prompt_agent import create_search_prompt_agent
from agents.search_agent import create_search_agent
from agents.risk_analyzer_agent import create_risk_analyzer_agent
from agents.decision_tree_agent import create_decision_tree_agent
from agents.visualizer_agent import create_visualizer_agent
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
    visualizer_agent = create_visualizer_agent(client)
    
    # Create Sequential Workflow
    workflow = (
        SequentialBuilder()
        .participants([
            search_prompt_agent,
            search_agent,
            risk_analyzer_agent,
            decision_tree_agent,
            visualizer_agent,
        ])
        .build()
    )
    
    serve(entities=[workflow], port=8090, auto_open=True, tracing_enabled=True)


if __name__ == "__main__":
    main()