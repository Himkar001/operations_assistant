"""
CrewAI Crew for Operations Assistant.

Two agents (Researcher and Writer) collaborate to answer questions
by using tools from the MCP server:
- Researcher: searches documents and reads records
- Writer: synthesizes information and saves reports

Run with: python src/crew_main.py
"""

import json
import os
os.environ["PYTHONIOENCODING"] = "utf-8"
import sys
import logging
from datetime import datetime
from pathlib import Path
from crewai import Agent, Task, Crew, Process

from mcp.client.stdio import StdioServerParameters
from crewai_tools import MCPServerAdapter

from config import get_settings, ensure_output_dirs, get_model_config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure output directories exist
ensure_output_dirs()
settings = get_settings()

# Setup LLM Environment for litellm
import os
model_config = get_model_config()
os.environ["OPENAI_MODEL_NAME"] = model_config["model"]
if settings.model_type == "ollama":
    os.environ["OPENAI_API_BASE"] = model_config.get("base_url", "http://localhost:11434")
    os.environ["OPENAI_API_KEY"] = "NA"
elif settings.model_type == "anthropic":
    os.environ["ANTHROPIC_API_KEY"] = model_config["api_key"]
elif settings.model_type == "openai":
    os.environ["OPENAI_API_KEY"] = model_config["api_key"]
elif settings.model_type == "groq":
    os.environ["GROQ_API_KEY"] = model_config["api_key"]



# ============================================================================
# Setup MCP Server Connection
# ============================================================================

def create_mcp_tools():
    """Create MCP tools that connect to the server via stdio."""
    
    # Define MCP server parameters
    mcp_server_params = StdioServerParameters(
        command="python",
        args=["src/mcp_server.py"]
    )
    
    # Create tools connected to MCP server
    tools = []
    
    try:
        # We start the MCP Server via MCPServerAdapter
        # We don't filter tools, exposing everything the server provides.
        mcp_server = MCPServerAdapter(mcp_server_params)
        logger.info("✓ MCP tools loaded")
        return mcp_server.tools
        
    except Exception as e:
        logger.error(f"Error creating MCP tools: {e}")
        logger.error("Make sure the MCP server is available or can be started automatically")
        raise
    
    return tools


# ============================================================================
# Define Agents
# ============================================================================

def create_researcher_agent(tools, llm):
    """Create the Researcher agent that searches and retrieves information."""
    
    return Agent(
        role="Research Analyst",
        goal="Search documents and records to find relevant information that answers the user's question. Always cite the source document.",
        backstory="""You are an expert research analyst for an operations team. 
        You search through documents and data records to find answers.
        You are thorough, careful, and always cite your sources.
        You never make up information - if you can't find evidence, you say so.""",
        tools=tools,
        verbose=settings.crew_verbose,
        max_iter=settings.crew_max_iter,
        allow_delegation=False,
        llm=llm
    )


def create_writer_agent(tools, llm):
    """Create the Writer agent that synthesizes information into reports."""
    
    return Agent(
        role="Report Writer",
        goal="Take the research findings and create a clear, sourced report that directly answers the user's question.",
        backstory="""You are an excellent technical writer. You take research findings and synthesize them
        into clear, well-organized reports. Every claim in your report cites the source document or record.
        You are accurate, concise, and professional.""",
        tools=tools,
        verbose=settings.crew_verbose,
        max_iter=settings.crew_max_iter,
        allow_delegation=False,
        llm=llm
    )


# ============================================================================
# Define Tasks
# ============================================================================

def create_research_task(researcher_agent, user_question):
    """Create the research task for finding evidence."""
    
    return Task(
        description=f"""Research and find evidence to answer this question:
        
        "{user_question}"
        
        Steps:
        1. Search for relevant documents using keywords from the question
        2. Read the full content of relevant documents
        3. Extract key facts and cite their sources
        4. If no information is found, clearly state that
        
        For each fact you find, note:
        - The exact information
        - The source document ID
        - Any relevant record numbers""",
        expected_output="""A summary of findings with:
        - Key facts that answer the question
        - Source document for each fact (document_id)
        - Any relevant record references
        - Note if no evidence was found""",
        agent=researcher_agent
    )


def create_writing_task(writer_agent, user_question):
    """Create the task for writing the final report."""
    
    return Task(
        description=f"""Based on the research findings, create a clear report that answers:
        
        "{user_question}"
        
        Report requirements:
        1. Start with a clear answer to the question
        2. Break down the answer into logical sections
        3. For EVERY claim, cite the source:
           - If from a document: "(Source: document_id)"
           - If from data: "(Source: orders.csv, row X)"
        4. Use markdown formatting
        5. End with a "Sources" section listing all documents used
        6. If answer cannot be found, clearly explain why""",
        expected_output="""A markdown report with:
        - Clear answer to the question
        - Well-organized sections
        - Every claim cited with source
        - Professional formatting
        - Sources section at the end""",
        agent=writer_agent
    )


# ============================================================================
# Create and Run Crew
# ============================================================================

def create_crew(tools, user_question):
    """Create the crew with agents and tasks."""
    
    # Create LLM instance
    from crewai import LLM
    from config import get_model_config
    mc = get_model_config()
    kwargs = {"model": mc["model"]}
    if "api_key" in mc:
        kwargs["api_key"] = mc["api_key"]
    if "base_url" in mc:
        kwargs["base_url"] = mc["base_url"]
    
    llm = LLM(**kwargs)
    
    # Create agents
    researcher = create_researcher_agent(tools, llm)
    writer = create_writer_agent(tools, llm)
    
    # Create tasks
    research_task = create_research_task(researcher, user_question)
    writing_task = create_writing_task(writer, user_question)
    
    # Create crew
    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, writing_task],
        process=Process.sequential,  # Tasks run one after another
        verbose=settings.crew_verbose,
        memory=False,
        cache=False,
        max_rpm=1  # Limit to 1 request per minute to stay under Groq 6000 TPM free tier
    )
    
    return crew


def save_trace(question, result, timestamp):
    """Save the crew's trace to a file."""
    
    trace_dir = settings.output_dir / "traces"
    trace_dir.mkdir(parents=True, exist_ok=True)
    
    # Clean question for filename
    import re
    safe_question = re.sub(r'[<>:"/\\|?*]', '_', question.replace(" ", "_")[:50])
    filename = f"{timestamp}_{safe_question}_trace.json"
    trace_file = trace_dir / filename
    
    trace_data = {
        "timestamp": timestamp,
        "question": question,
        "result": result,
        "status": "completed"
    }
    
    try:
        trace_file.write_text(json.dumps(trace_data, indent=2), encoding='utf-8')
        logger.info(f"Trace saved to: {trace_file}")
        return str(trace_file)
    except Exception as e:
        logger.error(f"Error saving trace: {e}")
        return None


def run_crew(question: str):
    """Run the crew on a question and return the answer."""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    logger.info(f"\n{'='*70}")
    logger.info(f"Operations Assistant Query")
    logger.info(f"{'='*70}")
    logger.info(f"Question: {question}")
    logger.info(f"Timestamp: {timestamp}")
    logger.info(f"{'='*70}\n")
    
    try:
        # Create MCP tools
        logger.info("Connecting to MCP server...")
        tools = create_mcp_tools()
        logger.info(f"✓ Connected. {len(tools)} tools available\n")
        
        # Create crew
        logger.info("Initializing crew...")
        crew = create_crew(tools, question)
        logger.info("✓ Crew ready\n")
        
        # Run crew
        logger.info("Running crew...\n")
        result = crew.kickoff(inputs={"question": question})
        
        # Save trace
        trace_file = save_trace(question, str(result), timestamp)
        
        # Print results
        logger.info(f"\n{'='*70}")
        logger.info("ANSWER")
        logger.info(f"{'='*70}")
        print(result)
        logger.info(f"{'='*70}\n")
        
        if trace_file:
            logger.info(f"Trace saved to: {trace_file}\n")
        
        return result
        
    except Exception as e:
        logger.error(f"Error running crew: {e}", exc_info=True)
        raise


# ============================================================================
# CLI Entry Point
# ============================================================================

def main():
    """Main entry point for the crew."""
    
    print("======================================================================")
    print("🤖 Operations Assistant")
    print("======================================================================")
    
    # Get question from interactive input
    try:
        question = input("\nEnter your question (or 'exit' to quit): ").strip()
        if not question or question.lower() in ('exit', 'quit'):
            sys.exit(0)
    except EOFError:
        sys.exit(0)
    
    # Run the crew
    try:
        run_crew(question)
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
