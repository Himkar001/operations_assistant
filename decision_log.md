# Decision Log

## Project: Operations Assistant (MCP + CrewAI)

### Decision 1: MCP Server Transport (stdio vs HTTP)

**Options Considered:**
1. **stdio** (chosen) - Simpler for local development, no port binding
2. HTTP/SSE - More flexible for remote deployment
3. TCP socket - Standard but more complex setup

**Choice:** stdio
**Reason:** 
- Keeps the project simple and free
- Perfect for local development with CrewAI
- No need for port management or networking setup
- Student-friendly (no extra services needed)

**Tradeoff:** Less flexible for distributed systems, but that's not a requirement for this project.

---

### Decision 2: Agent Architecture (Sequential vs Hierarchical)

**Options Considered:**
1. **Sequential** (chosen) - Researcher → Writer pipeline
2. Hierarchical - Manager orchestrates research and writing
3. Parallel - Both agents work simultaneously
4. Custom agentic loop

**Choice:** Sequential
**Reason:**
- Clear, understandable workflow
- Easy to debug and trace
- Natural task dependency (research must come first)
- Simpler for demonstration

**What Broke:** Initial attempt had agents looping. Added max_iter=10 to prevent infinite loops.

**Tradeoff:** Less flexible for complex multi-path investigations, but clearer for sourced reporting.

---

### Decision 3: Data Source Size (8-15 docs vs larger corpus)

**Options Considered:**
1. **Tiny corpus** (chosen) - 3 markdown docs + 1 CSV
2. Start with 20+ documents
3. Realistic company documentation

**Choice:** Tiny (3 docs, 1 CSV)
**Reason:**
- Easy to read and verify by hand
- Fast tests and demos
- No external data dependencies
- Follows project spec (8-15 items, but minimal is better)
- Student can scale easily

---

### Decision 4: Search Algorithm (Simple text matching vs embeddings)

**Options Considered:**
1. **Simple text matching** (chosen) - Substring search
2. Vector embeddings (FAISS, Chroma)
3. Full-text search (Elasticsearch)
4. LLM-based semantic search

**Choice:** Simple text matching
**Reason:**
- No external dependencies needed
- Transparent behavior (easy to debug)
- Fast enough for 3 documents
- Clear what the tool is doing
- Follows "keep it simple" principle

**Tradeoff:** Won't scale to thousands of documents. But for the scope, it's perfect.

---

### Decision 5: Validation Approach

**Options Considered:**
1. **Pydantic models** (chosen) - Input validation before tool execution
2. Direct function arguments with type hints
3. JSON schema in MCP definitions
4. No validation (trust the LLM)

**Choice:** Pydantic + JSON
**Reason:**
- Explicit validation catches injection attempts
- Clear error messages back to agents
- Follows security best practices
- Easy to test validation separately

---

### Decision 6: Source Attribution (Automatic vs Manual)

**Options Considered:**
1. **Agent responsibility** (chosen) - Agents must cite sources
2. Automatic wrapping of results with source tags
3. Separate source-tracking layer
4. Trace-based attribution only

**Choice:** Agent responsibility
**Reason:**
- Agents must reason about sources
- Natural language attribution is more readable
- Teaches LLM safety best practice
- Easier for human verification

**What Broke:** Initially, agents would answer without citing sources. Added explicit instructions to require citations.

---

### Decision 7: Environment & Model Access

**Options Considered:**
1. **Local model (Ollama) with fallback to Claude** (chosen)
2. Require Claude API key
3. Require local model only
4. Support multiple model providers

**Choice:** Ollama preferred, Claude fallback
**Reason:**
- Free tier friendly
- No API key needed for Ollama
- Still supports commercial model if available
- Reproducible from a fresh clone
- Education-friendly

---

### Decision 8: Error Handling

**Options Considered:**
1. **Graceful degradation** (chosen) - Return errors as JSON, let agents handle
2. Raise exceptions and crash
3. Silent failures
4. Logging-only failures

**Choice:** Graceful + clear messages
**Reason:**
- Agents can recover and retry
- Easy to debug from logs
- Follows "fail openly" principle

---

## Testing Strategy

### Unit Tests (test_mcp_tools.py)
- **Why:** Verify tools work independently of crew
- **What:** search, read, save each tested separately
- **Coverage:** Happy path + edge cases (not found, invalid input)

### End-to-End Tests (test_crew.py)
- **Why:** Verify crew can answer real questions
- **What:** 3 sample questions covering documents and CSV
- **Coverage:** Full workflow from question to report

### Manual Testing
- **Why:** Verify grounding and source attribution
- **What:** Run crew and check sources are cited
- **Coverage:** Check answer quality and evidence

---

## What Would Change for Production

1. **Search:** Replace text matching with embeddings + vector DB
2. **Scale:** Support 100K+ documents with proper indexing
3. **Auth:** Add user authentication and data isolation
4. **Audit:** Comprehensive logging and action tracking
5. **Approval:** Human approval before save_report (stretch goal)
6. **Validation:** Stricter input validation and sandboxing
7. **Caching:** Cache search results and document reads
8. **Monitoring:** Alerts for tool failures and slow queries
9. **Recovery:** Proper error recovery and retry logic
10. **Testing:** Property-based testing and fuzzing

---

### Decision 11: Free-Tier Rate Limit Handling

**Options Considered:**
1. Default CrewAI behavior (run at maximum speed)
2. Handle litellm rate limit exceptions dynamically
3. **Throttling via max_rpm=1** (chosen)

**Choice:** Throttling via max_rpm=1
**Reason:** 
- The Groq free tier imposes extremely tight Tokens Per Minute (TPM) limits (6,000 TPM).
- CrewAI sends significant context (agent prompts, tool descriptions, execution history) back and forth with every interaction.
- A fast execution strategy reliably exceeds the 6,000 TPM limit within seconds.
- Enforcing `max_rpm=1` strictly paces the requests, naturally bypassing the rate limits entirely without creating complex retry logic or risking permanent IP rate limiting.

**Tradeoff:** Execution takes notably longer (~3-4 minutes) compared to raw speed, but ensures absolute reliability for free-tier users.

---

## References Used

1. **MCP Docs:** https://modelcontextprotocol.io/
2. **CrewAI Docs:** https://docs.crewai.com
3. **CrewAI + MCP:** https://docs.crewai.com/en/mcp/overview
4. **FastMCP Tutorial:** https://gofastmcp.com/
5. **YouTube: Build MCP Server:** https://www.youtube.com/watch?v=_mUuhOwv9PY
6. **YouTube: Build CrewAI:** https://www.youtube.com/watch?v=K2UAE1OlC8s

---

## Security Decisions

### Input Validation
- Pydantic schemas validate all tool inputs
- Path traversal prevented (no .. in document IDs)
- Command injection prevented (no subprocess calls)

### Data Isolation
- All data in ./data/ directory
- Output only to ./outputs/ directory
- No system file access

### LLM Injection
- Test included to catch malicious prompts in documents
- Tool output is plain text/JSON, not code

### Keys & Secrets
- NO hardcoded API keys
- .env.example guides setup without exposing secrets
- API keys only loaded at runtime from environment

---

Generated: 2024-06-08
