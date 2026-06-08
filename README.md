# Operations Assistant: Multi-Agent Crew on MCP Server

A working example of CrewAI agents connected to a custom MCP (Model Context Protocol) server. The crew searches documents, retrieves records, and writes sourced reports for operational questions.

**📺 [Watch the Visual Demo!](https://drive.google.com/file/d/1NZPFj0Hnf_dyQ03ViPDL3NSTNZPtEyCK/view?usp=sharing)**

## 📋 What This Does

- **MCP Server**: Exposes tools over local data (documents + CSV)
- **CrewAI Agents**: Researcher and Writer agents that collaborate to answer questions
- **Grounded Answers**: Every claim in the report cites its source (document or record ID)

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- uv (Python package manager): `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Ollama (for local models): https://ollama.ai or use Claude API

### Installation

```bash
# Clone and setup
git clone <your-repo>
cd operations_assistant

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install all packages
uv pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env and choose your model
```

### Running the Project

#### 1. Start the MCP Server (in Terminal 1)
```bash
python src/mcp_server.py
```

Expected output:
```
INFO: Starting MCP server on stdio
```

#### 2. Test with MCP Inspector (Terminal 2)
```bash
# Download MCP Inspector from: https://github.com/modelcontextprotocol/inspector
# Or use npx:
npx @modelcontextprotocol/inspector ./src/mcp_server.py
```

#### 3. Run the CrewAI Crew (Terminal 2 or 3)
```bash
# Run a single query
python src/crew_main.py

# Or run tests
python tests/test_crew.py
```

#### 4. Example Questions

The crew can answer:
- "What is our product return policy?"
- "Which customers ordered in the last month?"
- "What are the main features of our premium package?"

---

## 📁 Project Structure

```
operations_assistant/
├── README.md                 # This file
├── .env.example             # Environment variables template
├── requirements.txt         # Python dependencies
├── decision_log.md          # Design decisions made
│
├── src/
│   ├── mcp_server.py        # MCP server with FastMCP
│   ├── crew_main.py         # CrewAI crew definition
│   └── config.py            # Configuration loader
│
├── data/
│   ├── documents/           # Text documents for searching
│   │   ├── return_policy.md
│   │   ├── product_features.md
│   │   ├── support_tickets.md
│   │   └── ...
│   └── orders.csv           # Orders/inventory data
│
├── tests/
│   ├── test_mcp_tools.py    # Unit tests for MCP tools
│   └── test_crew.py         # End-to-end crew tests
│
├── outputs/
│   ├── traces/              # Agent execution traces
│   └── reports/             # Generated reports
│
└── demo/
    └── demo_script.md       # Commands for demo video
```

---

## 🔧 How It Works

### MCP Server (src/mcp_server.py)

Exposes three tools:

1. **search_documents(query: str)**
   - Searches document titles and content
   - Returns list of matching document IDs and snippets

2. **read_record(document_id: str)**
   - Reads the full content of a document
   - Returns complete text with metadata

3. **save_report(title: str, content: str)**
   - Saves a markdown report to outputs/reports/
   - Returns file path and confirmation

### CrewAI Crew (src/crew_main.py)

Two agents working together:

1. **Researcher Agent**
   - Role: Finds evidence in documents and records
   - Task: Search for relevant information and read full records
   - Uses: search_documents and read_record tools

2. **Writer Agent**
   - Role: Creates grounded reports citing sources
   - Task: Synthesize evidence into a sourced report
   - Uses: save_report tool

---

## 🧪 Testing

```bash
# Unit test MCP tools directly
python tests/test_mcp_tools.py

# End-to-end test with crew
python tests/test_crew.py -v

# Run on specific question
python src/crew_main.py --question "What is our return policy?"
```

---

## 🔐 Safety & Security

- ✅ Tool inputs validated with strict schemas
- ✅ No shell command injection (no subprocess calls)
- ✅ File paths constrained to data/ directory
- ✅ max_iter set to prevent infinite loops
- ✅ MCP connection properly closed (context manager)
- ✅ No API keys hardcoded (uses .env)

---

## 📚 References

- [MCP Getting Started](https://modelcontextprotocol.io/docs/getting-started/intro)
- [FastMCP (Python SDK)](https://github.com/modelcontextprotocol/python-sdk)
- [CrewAI Docs](https://docs.crewai.com)
- [CrewAI + MCP Integration](https://docs.crewai.com/en/mcp/overview)

---

## 🎓 Learning Outcomes

After completing this project, you'll understand:
- How to build an MCP server with Python
- How to create multi-agent systems with CrewAI
- How to wire agents to external tools
- How to ground LLM answers in retrieved data
- Production practices: testing, tracing, validation

---

## 📝 License

MIT

---

## 🤝 Support

For issues or questions, check:
1. `.env` is configured with your model choice
2. MCP server is running before starting crew
3. Sample data is in `data/` folder
4. Python 3.11+ installed

