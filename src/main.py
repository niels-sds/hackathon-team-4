import os
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential
from dotenv import load_dotenv
from agent_framework.devui import serve
import logging

load_dotenv()

def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    
    settings = {
        "project_endpoint": os.environ["AZURE_AI_PROJECT_ENDPOINT"],
        "model_deployment_name": os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        "credential": AzureCliCredential(),
    }
    
    # Create a simple test agent
    test_agent = AzureAIAgentClient(**settings).create_agent(
        instructions="You are a helpful assistant for testing the setup.",
        name="TestAgent",
    ) 
    
    serve(entities=[test_agent], port=8090, auto_open=True, tracing_enabled=True)


if __name__ == "__main__":
    main()