"""Lightweight web interface with agent flow visualization"""
import os
import warnings
import logging
import json

# Suppress everything before imports
os.environ["AZURE_LOG_LEVEL"] = "error"
os.environ["AZURE_HTTP_LOGGING_ENABLED"] = "false"
os.environ["OTEL_SDK_DISABLED"] = "true"
warnings.filterwarnings("ignore")
logging.disable(logging.CRITICAL)

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
import uvicorn
from dotenv import load_dotenv
from azure.identity.aio import AzureCliCredential
from agent_framework.azure import AzureAIAgentClient
from agent_framework import WorkflowBuilder

from agents.search_prompt_agent import create_search_prompt_agent
from agents.search_agent import create_search_agent
from agents.risk_analyzer_agent import create_risk_analyzer_agent
from agents.decision_tree_agent import create_decision_tree_agent
from agents.visualizer_agent import create_visualizer_agent
from agents.rating_table_agent import create_rating_table_agent
from agents.browser_agent import create_browser_agent

load_dotenv()

app = FastAPI()

# Agent flow visualization UI
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Risk Assessment Workflow</title>
    <style>
        * { box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 900px; margin: 40px auto; padding: 20px; background: #f5f5f5; }
        h1 { color: #1a1a2e; margin-bottom: 10px; }
        .subtitle { color: #666; margin-bottom: 30px; }
        .input-section { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 30px; }
        input { width: calc(100% - 150px); padding: 14px 18px; font-size: 16px; border: 2px solid #e0e0e0; border-radius: 8px; outline: none; }
        input:focus { border-color: #007bff; }
        button { padding: 14px 28px; font-size: 16px; background: #007bff; color: white; border: none; border-radius: 8px; cursor: pointer; margin-left: 10px; transition: all 0.2s; }
        button:hover { background: #0056b3; transform: translateY(-1px); }
        button:disabled { background: #ccc; cursor: not-allowed; transform: none; }
        
        .workflow-container { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .workflow-title { font-size: 14px; color: #666; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 20px; }
        
        .agent-flow { display: flex; flex-direction: column; gap: 8px; }
        .agent-row { display: flex; align-items: flex-start; gap: 10px; }
        .agent { display: flex; align-items: flex-start; padding: 12px 18px; border-radius: 8px; background: #f8f9fa; border: 2px solid #e9ecef; transition: all 0.3s; flex: 1; min-width: 0; }
        .agent-icon { width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 12px; font-size: 16px; flex-shrink: 0; margin-top: 2px; }
        .agent-info { flex: 1; min-width: 0; }
        .agent-name { font-weight: 600; color: #333; font-size: 14px; }
        .agent-status { font-size: 12px; color: #888; margin-top: 2px; }
        .agent-output { font-size: 11px; color: #555; margin-top: 6px; max-height: 200px; overflow-y: auto; font-family: monospace; background: rgba(0,0,0,0.05); padding: 8px; border-radius: 4px; display: none; line-height: 1.4; }
        .agent-output.visible { display: block; }
        
        /* Markdown styling for agent output */
        .agent-output h1, .agent-output h2, .agent-output h3 { margin: 8px 0 4px; font-size: 1.1em; color: #333; }
        .agent-output ul, .agent-output ol { margin: 4px 0; padding-left: 20px; }
        .agent-output li { margin: 2px 0; }
        .agent-output p { margin: 4px 0; }
        .agent-output code { padding: 2px 4px; border-radius: 3px; background: #e0e0e0; }
        .agent-output pre { padding: 8px; border-radius: 4px; overflow-x: auto; border: 1px solid #ddd; }
        .agent-output pre code { background: transparent; padding: 0; }
        .agent-output blockquote { border-left: 3px solid #ccc; margin: 4px 0; padding-left: 8px; color: #666; }
        
        .agent.waiting { background: #f8f9fa; border-color: #e9ecef; }
        .agent.waiting .agent-icon { background: #e9ecef; color: #aaa; }
        
        .agent.running { background: #fff8e6; border-color: #ffc107; animation: pulse 1.5s infinite; }
        .agent.running .agent-icon { background: #ffc107; color: white; }
        .agent.running .agent-status { color: #856404; }
        
        .agent.completed { background: #e8f5e9; border-color: #4caf50; }
        .agent.completed .agent-icon { background: #4caf50; color: white; }
        .agent.completed .agent-status { color: #2e7d32; }
        
        .agent.error { background: #ffebee; border-color: #f44336; }
        .agent.error .agent-icon { background: #f44336; color: white; }
        
        .connector { width: 2px; height: 20px; background: #888; margin: auto; }
        .connector.active { background: #4caf50; }
        
        .parallel-group { display: flex; gap: 15px; margin-left: 0; }
        .parallel-group .agent { flex: 1; }
        .parallel-indicator { font-size: 11px; color: #888; margin: auto; }
				.connector-group { display: flex; gap: 15px; justify-content: space-between; }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        
        .result-message { margin-top: 20px; padding: 15px; border-radius: 8px; display: none; }
        .result-message.success { background: #e8f5e9; border: 1px solid #4caf50; color: #2e7d32; display: block; }
        .result-message.error { background: #ffebee; border: 1px solid #f44336; color: #c62828; display: block; }
				#details-log:not(:empty) { margin-top: 10px; padding: 15px; background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px; max-height: 300px; overflow-y: auto; font-family: monospace; font-size: 12px; line-height: 1.5; color: #333; }
    </style>
    <!-- Add marked.js for markdown rendering -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
</head>
<body>
    <h1>🏥 Medical Risk Assessment</h1>
    <p class="subtitle">Generate a risk assessment decision tree for medical impairments</p>
    
    <div class="input-section">
        <input type="text" id="impairment" placeholder="Enter impairment (e.g., Diabetes, Asthma, Cancer...)" />
        <button id="submit" onclick="runWorkflow()">Generate</button>
    </div>
    
    <div class="workflow-container">
        <div class="workflow-title">Agent Workflow</div>
        <div class="agent-flow">
            <div class="agent waiting" id="agent-search-prompt">
                <div class="agent-icon">🔍</div>
                <div class="agent-info">
                    <div class="agent-name">Search Prompt Agent</div>
                    <div class="agent-status">Waiting</div>
                    <div class="agent-output" id="output-search-prompt"></div>
                </div>
            </div>
            <div class="connector" id="conn-1"></div>
            
            <div class="agent waiting" id="agent-search">
                <div class="agent-icon">📚</div>
                <div class="agent-info">
                    <div class="agent-name">Search Agent</div>
                    <div class="agent-status">Waiting</div>
                    <div class="agent-output" id="output-search"></div>
                </div>
            </div>
            <div class="connector" id="conn-2"></div>
            
            <div class="agent waiting" id="agent-risk">
                <div class="agent-icon">⚠️</div>
                <div class="agent-info">
                    <div class="agent-name">Risk Analyzer Agent</div>
                    <div class="agent-status">Waiting</div>
                    <div class="agent-output" id="output-risk"></div>
                </div>
            </div>
            <div class="connector" id="conn-3"></div>
            
            <div class="agent waiting" id="agent-decision">
                <div class="agent-icon">🌳</div>
                <div class="agent-info">
                    <div class="agent-name">Decision Tree Agent</div>
                    <div class="agent-status">Waiting</div>
                    <div class="agent-output" id="output-decision"></div>
                </div>
            </div>
            <div class="connector" id="conn-4"></div>
            
            <div class="parallel-indicator">↓ Parallel Execution ↓</div>
            <div class="parallel-group">
                <div class="agent waiting" id="agent-visualizer">
                    <div class="agent-icon">📊</div>
                    <div class="agent-info">
                        <div class="agent-name">Visualizer Agent</div>
                        <div class="agent-status">Waiting</div>
                        <div class="agent-output" id="output-visualizer"></div>
                    </div>
                </div>
                <div class="agent waiting" id="agent-rating">
                    <div class="agent-icon">📋</div>
                    <div class="agent-info">
                        <div class="agent-name">Rating Table Agent</div>
                        <div class="agent-status">Waiting</div>
                        <div class="agent-output" id="output-rating"></div>
                    </div>
                </div>
            </div>
						<div class="connector-group">
            	<div class="connector" id="conn-5"></div>
            	<div class="connector" id="conn-6"></div>
						</div>
            
            <div class="parallel-group">
                <div class="agent waiting" id="agent-browser-diagram">
                    <div class="agent-icon">🌐</div>
                    <div class="agent-info">
                        <div class="agent-name">Diagram Browser</div>
                        <div class="agent-status">Waiting</div>
                        <div class="agent-output" id="output-browser-diagram"></div>
                    </div>
                </div>
                <div class="agent waiting" id="agent-browser-table">
                    <div class="agent-icon">🌐</div>
                    <div class="agent-info">
                        <div class="agent-name">Table Browser</div>
                        <div class="agent-status">Waiting</div>
                        <div class="agent-output" id="output-browser-table"></div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="result-message" id="result"></div>
        
        <!-- Collapsible Details Panel -->
        <details style="margin-top: 20px;" open>
            <summary style="cursor: pointer; padding: 12px; background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px; user-select: none; font-weight: 600;">📋 Processing Details</summary>
            <div id="details-log"></div>
        </details>
    </div>
    
    <script>
        const agentMap = {
            'SearchPromptAgent': 'agent-search-prompt',
            'SearchAgent': 'agent-search',
            'RiskAnalyzerAgent': 'agent-risk',
            'DecisionTreeAgent': 'agent-decision',
            'VisualizerAgent': 'agent-visualizer',
            'RatingTableAgent': 'agent-rating',
            'DiagramBrowserAgent': 'agent-browser-diagram',
            'TableBrowserAgent': 'agent-browser-table'
        };
        
        const outputMap = {
            'SearchPromptAgent': 'output-search-prompt',
            'SearchAgent': 'output-search',
            'RiskAnalyzerAgent': 'output-risk',
            'DecisionTreeAgent': 'output-decision',
            'VisualizerAgent': 'output-visualizer',
            'RatingTableAgent': 'output-rating',
            'DiagramBrowserAgent': 'output-browser-diagram',
            'TableBrowserAgent': 'output-browser-table'
        };
        
        function resetAgents() {
            document.querySelectorAll('.agent').forEach(el => {
                el.className = 'agent waiting';
                el.querySelector('.agent-status').textContent = 'Waiting';
            });
            document.querySelectorAll('.agent-output').forEach(el => {
                el.textContent = '';
                el.classList.remove('visible');
            });
            document.querySelectorAll('.connector').forEach(el => el.classList.remove('active'));
            document.getElementById('result').className = 'result-message';
            document.getElementById('result').style.display = 'none';
        }
        
        function updateAgent(name, status, message, output) {
            const elementId = agentMap[name];
            if (!elementId) return;
            
            const el = document.getElementById(elementId);
            if (!el) return;
            
            el.className = 'agent ' + status;
            el.querySelector('.agent-status').textContent = message || status;
            
            // Update output if provided
            if (output) {
                const outputId = outputMap[name];
                const outputEl = document.getElementById(outputId);
                if (outputEl) {
                    // Use marked library if available, otherwise simple text
                    if (window.marked) {
                        outputEl.innerHTML = marked.parse(output);
                    } else {
                        outputEl.textContent = output;
                    }
                    outputEl.classList.add('visible');
                }
            }
            
            // Log to details panel - agent status changes get a new line
            const timestamp = new Date().toLocaleTimeString();
            const log = document.getElementById('details-log');
            const entry = document.createElement('div');
            entry.textContent = `[${timestamp}] ${name}: ${message || status}`;
            log.appendChild(entry);
            
            // Remove old progress line and create new one after this entry
            let progressEl = document.getElementById('progress-line');
            if (progressEl) progressEl.remove();
            progressEl = document.createElement('div');
            progressEl.id = 'progress-line';
            progressEl.style.color = '#666';
            log.appendChild(progressEl);
            
            log.scrollTop = log.scrollHeight;
        }
        
        function addDetailLog(message) {
            const timestamp = new Date().toLocaleTimeString();
            const log = document.getElementById('details-log');
            
            // Remove progress line before adding new entry
            let progressEl = document.getElementById('progress-line');
            if (progressEl) progressEl.remove();
            
            const entry = document.createElement('div');
            entry.textContent = `[${timestamp}] ${message}`;
            log.appendChild(entry);
            log.scrollTop = log.scrollHeight;
        }
        
        async function runWorkflow() {
            const input = document.getElementById('impairment').value.trim();
            if (!input) { alert('Please enter an impairment name'); return; }
            
            const btn = document.getElementById('submit');
            btn.disabled = true;
            resetAgents();
            
            // Clear and show details
            const log = document.getElementById('details-log');
            log.innerHTML = '';
            addDetailLog('Starting workflow for: ' + input);
            
            try {
                const eventSource = new EventSource('/run-stream?impairment=' + encodeURIComponent(input));
                
                eventSource.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    
                    if (data.type === 'agent_status') {
                        updateAgent(data.agent, data.status, data.message, data.output);
                    } else if (data.type === 'progress') {
                        // Update progress in details panel (overwrite last progress line)
                        const log = document.getElementById('details-log');
                        // Find or create progress element
                        let progressEl = document.getElementById('progress-line');
                        if (!progressEl) {
                            progressEl = document.createElement('div');
                            progressEl.id = 'progress-line';
                            progressEl.style.color = '#666';
                            log.appendChild(progressEl);
                        }
                        progressEl.textContent = `[${new Date().toLocaleTimeString()}] ${data.message}`;
                        log.scrollTop = log.scrollHeight;
                    } else if (data.type === 'complete') {
                        eventSource.close();
                        // Remove progress line and add completion
                        const progressEl = document.getElementById('progress-line');
                        if (progressEl) progressEl.remove();
                        addDetailLog('✓ Workflow completed successfully');
                        const result = document.getElementById('result');
                        result.className = 'result-message success';
                        result.innerHTML = '✅ ' + data.message;
                        result.style.display = 'block';
                        btn.disabled = false;
                    } else if (data.type === 'error') {
                        eventSource.close();
                        const progressEl = document.getElementById('progress-line');
                        if (progressEl) progressEl.remove();
                        addDetailLog('✗ Error: ' + data.message);
                        const result = document.getElementById('result');
                        result.className = 'result-message error';
                        result.innerHTML = '❌ ' + data.message;
                        result.style.display = 'block';
                        btn.disabled = false;
                    }
                };
                
                eventSource.onerror = () => {
                    eventSource.close();
                    btn.disabled = false;
                    addDetailLog('✗ Connection error');
                };
                
            } catch (e) {
                addDetailLog('✗ Error: ' + e.message);
                const result = document.getElementById('result');
                result.className = 'result-message error';
                result.innerHTML = '❌ Error: ' + e.message;
                result.style.display = 'block';
                btn.disabled = false;
            }
        }

        // Add Enter key listener
        document.getElementById('impairment').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const btn = document.getElementById('submit');
                if (!btn.disabled) {
                    runWorkflow();
                }
            }
        });
    </script>
</body>
</html>
"""

# Global client instance (reusable)
client = None


def get_client():
    global client
    if client is None:
        settings = {
            "project_endpoint": os.environ["AZURE_AI_PROJECT_ENDPOINT"],
            "model_deployment_name": os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
            "credential": AzureCliCredential(),
            "logging_enable": False,
        }
        client = AzureAIAgentClient(**settings)
    return client


def create_workflow():
    """Create a fresh workflow instance for each run"""
    c = get_client()
    
    search_prompt_agent = create_search_prompt_agent(c)
    search_agent = create_search_agent(c)
    risk_analyzer_agent = create_risk_analyzer_agent(c)
    decision_tree_agent = create_decision_tree_agent(c)
    visualizer_agent = create_visualizer_agent(c)
    rating_table_agent = create_rating_table_agent(c)
    diagram_browser_agent = create_browser_agent(c, name="DiagramBrowserAgent", file_prefix="diagram")
    table_browser_agent = create_browser_agent(c, name="TableBrowserAgent", file_prefix="rating_table")
    
    return (
        WorkflowBuilder()
        .add_agent(search_prompt_agent)
        .add_agent(search_agent)
        .add_agent(risk_analyzer_agent)
        .add_agent(decision_tree_agent)
        .add_agent(visualizer_agent)
        .add_agent(rating_table_agent)
        .add_agent(diagram_browser_agent)
        .add_agent(table_browser_agent)
        .add_edge(search_prompt_agent, search_agent)
        .add_edge(search_agent, risk_analyzer_agent)
        .add_edge(risk_analyzer_agent, decision_tree_agent)
        .add_fan_out_edges(decision_tree_agent, [visualizer_agent, rating_table_agent])
        .add_edge(visualizer_agent, diagram_browser_agent)
        .add_edge(rating_table_agent, table_browser_agent)
        .set_start_executor(search_prompt_agent)
        .build()
    )


@app.on_event("startup")
async def startup():
    # Initialize client on startup
    get_client()


@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_PAGE


@app.get("/run-stream")
async def run_workflow_stream(impairment: str):
    """Stream agent status updates using Server-Sent Events"""
    
    async def event_generator():
        import asyncio
        import time
        
        try:
            if not impairment:
                yield f"data: {json.dumps({'type': 'error', 'message': 'No impairment provided'})}\n\n"
                return
            
            # Create a fresh workflow for this run
            workflow = create_workflow()
            
            # Start workflow in background task
            workflow_done = False
            workflow_error = None
            workflow_result = None
            
            async def run_workflow_task():
                nonlocal workflow_done, workflow_error, workflow_result
                try:
                    print(f"[DEBUG] Starting workflow for: {impairment}")
                    workflow_result = await workflow.run(impairment)
                    print(f"[DEBUG] Workflow completed. Result type: {type(workflow_result)}")
                    print(f"[DEBUG] Result length: {len(workflow_result) if workflow_result else 0}")
                    workflow_done = True
                except Exception as e:
                    print(f"[DEBUG] Workflow error: {e}")
                    workflow_error = str(e)
                    workflow_done = True
                    workflow_error = str(e)
                    workflow_done = True
            
            # Start the workflow
            task = asyncio.create_task(run_workflow_task())
            
            # Now send UI updates while the workflow runs
            start_time = time.time()
            
            # Example outputs to show (will be replaced by real data when available)
            stage_outputs = {
                'SearchPromptAgent': f'Optimizing search query for "{impairment}"...',
                'SearchAgent': 'Searching medical databases...',
                'RiskAnalyzerAgent': 'Analyzing risk factors and complications...',
                'DecisionTreeAgent': 'Building decision tree structure...',
                'VisualizerAgent': 'Generating HTML visualization...',
                'RatingTableAgent': 'Creating rating table HTML...',
                'DiagramBrowserAgent': 'Opening diagram in browser...',
                'TableBrowserAgent': 'Opening table in browser...',
            }
            
            # Define agent dependencies and durations
            # Each agent has: duration, and list of agents it depends on
            agent_config = {
                'SearchPromptAgent': {'duration': 5, 'depends_on': []},
                'SearchAgent': {'duration': 15, 'depends_on': ['SearchPromptAgent']},
                'RiskAnalyzerAgent': {'duration': 20, 'depends_on': ['SearchAgent']},
                'DecisionTreeAgent': {'duration': 25, 'depends_on': ['RiskAnalyzerAgent']},
                'VisualizerAgent': {'duration': 12, 'depends_on': ['DecisionTreeAgent']},
                'RatingTableAgent': {'duration': 18, 'depends_on': ['DecisionTreeAgent']},
                'DiagramBrowserAgent': {'duration': 3, 'depends_on': ['VisualizerAgent']},
                'TableBrowserAgent': {'duration': 8, 'depends_on': ['RatingTableAgent']},
            }
            
            # Calculate when each agent starts and completes
            agent_start_times = {}
            agent_completion_times = {}
            
            def calc_start_time(agent_name):
                if agent_name in agent_start_times:
                    return agent_start_times[agent_name]
                deps = agent_config[agent_name]['depends_on']
                if not deps:
                    agent_start_times[agent_name] = 0
                else:
                    # Start when all dependencies complete
                    agent_start_times[agent_name] = max(
                        calc_start_time(d) + agent_config[d]['duration'] for d in deps
                    )
                agent_completion_times[agent_name] = agent_start_times[agent_name] + agent_config[agent_name]['duration']
                return agent_start_times[agent_name]
            
            for agent_name in agent_config:
                calc_start_time(agent_name)
            
            total_estimated_time = max(agent_completion_times.values())
            
            # Track agent states: 'waiting', 'running', 'completed'
            agent_states = {name: 'waiting' for name in agent_config}
            
            # Mark first agents as running (those with no dependencies)
            for agent_name, config in agent_config.items():
                if not config['depends_on']:
                    agent_states[agent_name] = 'running'
                    output = stage_outputs.get(agent_name, '')
                    yield f"data: {json.dumps({'type': 'agent_status', 'agent': agent_name, 'status': 'running', 'message': 'Processing...', 'output': output})}\n\n"
            
            # Send updates until workflow is done
            while not workflow_done:
                elapsed = time.time() - start_time
                
                # Check each agent for state transitions
                for agent_name, config in agent_config.items():
                    current_state = agent_states[agent_name]
                    
                    if current_state == 'waiting':
                        # Check if all dependencies are completed
                        deps = config['depends_on']
                        if all(agent_states.get(d) == 'completed' for d in deps):
                            # Start this agent
                            agent_states[agent_name] = 'running'
                            output = stage_outputs.get(agent_name, '')
                            yield f"data: {json.dumps({'type': 'agent_status', 'agent': agent_name, 'status': 'running', 'message': 'Processing...', 'output': output})}\n\n"
                    
                    elif current_state == 'running':
                        # Check if agent should complete based on estimated time
                        if elapsed >= agent_completion_times[agent_name]:
                            agent_states[agent_name] = 'completed'
                            yield f"data: {json.dumps({'type': 'agent_status', 'agent': agent_name, 'status': 'completed', 'message': 'Completed', 'output': '✓ Processing complete'})}\n\n"
                
                # Calculate progress info
                running_agents = [a for a, s in agent_states.items() if s == 'running']
                completed_count = sum(1 for s in agent_states.values() if s == 'completed')
                total_agents = len(agent_config)
                
                if running_agents:
                    current_agents_str = " + ".join(running_agents)
                else:
                    current_agents_str = "Finishing..."
                
                estimated_remaining = max(0, total_estimated_time - int(elapsed))
                progress_pct = min(100, int((completed_count / total_agents) * 100))
                
                # Send detailed heartbeat
                parallel_indicator = " (parallel)" if len(running_agents) > 1 else ""
                progress_msg = f"{current_agents_str}{parallel_indicator} | {int(elapsed)}s elapsed | ~{estimated_remaining}s remaining | {progress_pct}%"
                yield f"data: {json.dumps({'type': 'progress', 'message': progress_msg})}\n\n"
                
                # Wait a bit before next update
                await asyncio.sleep(1)
            
            # Workflow is done - ensure task is cleaned up
            try:
                await task
            except:
                pass
            
            # Check for error
            if workflow_error:
                yield f"data: {json.dumps({'type': 'error', 'message': workflow_error})}\n\n"
                return
            
            # Agent names for output mapping
            agent_names_list = [
                'SearchPromptAgent',
                'SearchAgent',
                'RiskAnalyzerAgent',
                'DecisionTreeAgent',
                'VisualizerAgent',
                'RatingTableAgent',
                'DiagramBrowserAgent',
                'TableBrowserAgent',
            ]
            
            def extract_text_from_event(event):
                """Extract readable text from workflow event"""
                # print(f"[DEBUG] Extracting from event type: {type(event)}")
                
                # Check event.data
                if hasattr(event, 'data'):
                    data = event.data
                    # print(f"[DEBUG] Event data type: {type(data)}")
                    
                    # If data is AgentRunResponse or similar object
                    if hasattr(data, 'output'):
                        return str(data.output)
                    if hasattr(data, 'content'):
                        return str(data.content)
                    if hasattr(data, 'text'):
                        return str(data.text)
                    if hasattr(data, 'message'):
                        return str(data.message)
                        
                    # If data is a dict
                    if isinstance(data, dict):
                        if 'output' in data: return str(data['output'])
                        if 'content' in data: return str(data['content'])
                        if 'text' in data: return str(data['text'])
                        if 'message' in data: return str(data['message'])
                
                # Try to get agent_run_response content (legacy check)
                if hasattr(event, 'agent_run_response'):
                    resp = event.agent_run_response
                    if hasattr(resp, 'output'):
                        return str(resp.output)
                    if hasattr(resp, 'content'):
                        return str(resp.content)
                
                return None
            
            # Extract real outputs from workflow result
            real_outputs = {}
            if workflow_result:
                try:
                    print(f"[DEBUG] Processing workflow result of length: {len(workflow_result)}")
                    # WorkflowRunResult is a list of events
                    for event in workflow_result:
                        # Get executor_id to identify agent
                        executor_id = getattr(event, 'executor_id', None)
                        print(f"[DEBUG] Event executor_id: {executor_id}")
                        
                        if executor_id and executor_id in agent_names_list:
                            text = extract_text_from_event(event)
                            if text:
                                # For HTML content, wrap in code block or keep as is
                                if '<html' in text.lower() or '<!doctype' in text.lower():
                                    # Keep HTML but maybe indicate it
                                    pass
                                
                                real_outputs[executor_id] = text
                                print(f"[DEBUG] Extracted output for {executor_id}: {len(text)} chars")
                    
                    # Also try get_outputs() as fallback
                    try:
                        outputs = workflow_result.get_outputs()
                        print(f"[DEBUG] get_outputs() returned {len(outputs)} items")
                        for i, output in enumerate(outputs):
                            if i < len(agent_names_list):
                                agent_name = agent_names_list[i]
                                if agent_name not in real_outputs and output:
                                    output_text = str(output)
                                    real_outputs[agent_name] = output_text
                                    print(f"[DEBUG] Extracted output from get_outputs for {agent_name}")
                    except Exception as e:
                        print(f"[DEBUG] get_outputs failed: {e}")
                                
                except Exception as e:
                    print(f"Error extracting outputs: {e}")
            
            # Mark all agents as completed with real outputs
            for agent_name in agent_config.keys():
                output = real_outputs.get(agent_name, '')
                if output:
                    # Send real output
                    yield f"data: {json.dumps({'type': 'agent_status', 'agent': agent_name, 'status': 'completed', 'message': 'Completed', 'output': output})}\n\n"
                elif agent_states.get(agent_name) != 'completed':
                    # Not yet completed, mark now
                    if 'Browser' in agent_name:
                        output = '✓ Opened in browser'
                    else:
                        output = '✓ Completed'
                    yield f"data: {json.dumps({'type': 'agent_status', 'agent': agent_name, 'status': 'completed', 'message': 'Completed', 'output': output})}\n\n"
            
            yield f"data: {json.dumps({'type': 'complete', 'message': f'Risk assessment for {impairment} completed! Check browser tabs for results.'})}\n\n"
            
        except Exception as e:
            error_msg = str(e)
            yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )


@app.post("/run")
async def run_workflow_post(request: Request):
    try:
        data = await request.json()
        impairment = data.get("impairment", "")
        
        if not impairment:
            return JSONResponse({"success": False, "message": "No impairment provided"})
        
        # Create a fresh workflow for this run
        workflow = create_workflow()
        
        # Run the workflow
        result = await workflow.run(impairment)
        
        return JSONResponse({
            "success": True, 
            "message": f"Risk assessment for '{impairment}' completed! Check browser tabs for results."
        })
        
    except Exception as e:
        return JSONResponse({"success": False, "message": str(e)})


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    print("Starting lightweight server on http://127.0.0.1:8091")
    uvicorn.run(app, host="127.0.0.1", port=8091, log_level="error")
