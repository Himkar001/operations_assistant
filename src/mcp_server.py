"""
MCP Server for Operations Assistant.

Exposes three tools:
1. search_documents(query) - Search document titles and content
2. read_record(document_id) - Read full document content
3. save_report(title, content) - Save markdown report

Run with: python src/mcp_server.py
Test with: npx @modelcontextprotocol/inspector ./src/mcp_server.py
"""

import json
import csv
from pathlib import Path
from typing import Optional
from datetime import datetime
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
server = FastMCP("operations-assistant")

# Configuration
DATA_DIR = Path(__file__).parent.parent / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
OUTPUTS_DIR = Path(__file__).parent.parent / "outputs" / "reports"
ORDERS_FILE = DATA_DIR / "orders.csv"

# Create directories if needed
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# Tool Schemas (Input Validation)
# ============================================================================

class SearchDocumentsInput(BaseModel):
    """Input for search_documents tool."""
    query: str = Field(..., min_length=1, max_length=500, description="Search query")


class ReadRecordInput(BaseModel):
    """Input for read_record tool."""
    document_id: str = Field(..., min_length=1, max_length=100, description="Document filename without extension")


class SaveReportInput(BaseModel):
    """Input for save_report tool."""
    title: str = Field(..., min_length=1, max_length=200, description="Report title")
    content: str = Field(..., min_length=1, description="Report content in markdown")


# ============================================================================
# Tool: Search Documents
# ============================================================================

@server.tool()
def search_documents(query: str) -> str:
    """
    Search documents by query.
    
    Returns a list of matching document IDs with snippets.
    Uses simple text matching on document filenames and content.
    """
    logger.info(f"Searching documents for: {query}")
    
    # Validate input
    try:
        validated = SearchDocumentsInput(query=query)
        search_query = validated.query.lower()
    except Exception as e:
        return json.dumps({"error": f"Invalid input: {str(e)}", "results": []})
    
    results = []
    
    # Check if documents directory exists
    if not DOCUMENTS_DIR.exists():
        return json.dumps({"error": f"Documents directory not found: {DOCUMENTS_DIR}", "results": []})
    
    # Search through markdown files
    for doc_file in DOCUMENTS_DIR.glob("*.md"):
        try:
            content = doc_file.read_text(encoding='utf-8')
            filename_lower = doc_file.stem.lower()
            content_lower = content.lower()
            
            # Check if query matches filename or content
            if search_query in filename_lower or search_query in content_lower:
                # Get first 200 chars as snippet
                snippet = content[:200].replace("\n", " ")
                results.append({
                    "id": doc_file.stem,
                    "title": doc_file.stem.replace("_", " ").title(),
                    "snippet": snippet + "..." if len(content) > 200 else snippet,
                    "matched_query": True
                })
        except Exception as e:
            logger.error(f"Error reading {doc_file}: {e}")
    
    logger.info(f"Found {len(results)} matching documents")
    
    return json.dumps({
        "query": query,
        "results": results,
        "total": len(results)
    })


# ============================================================================
# Tool: Read Record
# ============================================================================

@server.tool()
def read_record(document_id: str) -> str:
    """
    Read the full content of a document by ID.
    
    Returns the complete text of the document.
    Can also read CSV records if format is "csv:row_number".
    """
    logger.info(f"Reading record: {document_id}")
    
    # Validate input
    try:
        validated = ReadRecordInput(document_id=document_id)
        doc_id = validated.document_id
    except Exception as e:
        return json.dumps({"error": f"Invalid input: {str(e)}", "content": ""})
    
    # Check if it's a CSV record request (format: "csv:0" for first row)
    if doc_id.startswith("csv:"):
        try:
            row_num = int(doc_id.split(":")[1])
            if ORDERS_FILE.exists():
                with open(ORDERS_FILE, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for i, row in enumerate(reader):
                        if i == row_num:
                            return json.dumps({
                                "id": doc_id,
                                "type": "csv_record",
                                "content": json.dumps(row),
                                "found": True
                            })
                return json.dumps({"error": f"CSV record {row_num} not found", "content": ""})
            else:
                return json.dumps({"error": f"Orders file not found: {ORDERS_FILE}", "content": ""})
        except Exception as e:
            return json.dumps({"error": f"Error reading CSV: {str(e)}", "content": ""})
    
    # Read markdown document
    doc_path = DOCUMENTS_DIR / f"{doc_id}.md"
    
    if not doc_path.exists():
        available = list(DOCUMENTS_DIR.glob("*.md"))
        return json.dumps({
            "error": f"Document '{doc_id}' not found",
            "available_documents": [f.stem for f in available],
            "content": ""
        })
    
    try:
        content = doc_path.read_text(encoding='utf-8')
        return json.dumps({
            "id": doc_id,
            "type": "markdown",
            "content": content,
            "found": True
        })
    except Exception as e:
        return json.dumps({"error": f"Error reading document: {str(e)}", "content": ""})


# ============================================================================
# Tool: Save Report
# ============================================================================

@server.tool()
def save_report(title: str, content: str) -> str:
    """
    Save a markdown report to the outputs/reports directory.
    
    Returns the file path and confirmation.
    """
    logger.info(f"Saving report: {title}")
    
    # Validate input
    try:
        validated = SaveReportInput(title=title, content=content)
        safe_title = validated.title
        safe_content = validated.content
    except Exception as e:
        return json.dumps({"error": f"Invalid input: {str(e)}", "file_path": ""})
    
    # Create safe filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = safe_title.replace(" ", "_").replace("/", "_")[:50]
    filename = f"{timestamp}_{safe_filename}.md"
    file_path = OUTPUTS_DIR / filename
    
    try:
        # Add header to report
        full_content = f"# {safe_title}\n\nGenerated: {datetime.now().isoformat()}\n\n{safe_content}"
        file_path.write_text(full_content, encoding='utf-8')
        
        logger.info(f"Report saved to: {file_path}")
        
        return json.dumps({
            "success": True,
            "title": safe_title,
            "file_path": str(file_path),
            "filename": filename,
            "message": f"Report saved successfully to {filename}"
        })
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Error saving report: {str(e)}",
            "file_path": ""
        })


# ============================================================================
# Resource: List Available Documents
# ============================================================================

@server.resource("documents://list")
def list_documents() -> str:
    """Resource that lists all available documents."""
    docs = []
    if DOCUMENTS_DIR.exists():
        docs = [f.stem for f in DOCUMENTS_DIR.glob("*.md")]
    return json.dumps({"documents": sorted(docs)})


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    logger.info("Starting Operations Assistant MCP Server")
    logger.info(f"Documents directory: {DOCUMENTS_DIR}")
    logger.info(f"Outputs directory: {OUTPUTS_DIR}")
    logger.info(f"Orders file: {ORDERS_FILE}")
    logger.info("Available tools: search_documents, read_record, save_report")
    logger.info("Run 'npx @modelcontextprotocol/inspector ./src/mcp_server.py' to test")
    
    # Run the server
    server.run(transport="stdio")
