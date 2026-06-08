# Demo Script (5 Minutes)

## Overview
This script guides what to show in the 5-minute demo video. Time ~1 min per section.

---

## ~1 min: The Pitch

**What to Say (Adapt in Your Own Words):**

> "Hi, I'm [Name]. I built an Operations Assistant that helps teams answer questions about their documents and data.
>
> The problem: Operations teams spend time searching through documents, finding records in spreadsheets, and summarizing findings. 
>
> My solution: A multi-agent crew that connects to an MCP server. The crew can search documents, read records, and write sourced reports automatically.
>
> It's built with:
> - **MCP (Model Context Protocol):** A server that exposes tools
> - **CrewAI:** Agents that collaborate to answer questions
> - **Local data:** Documents and a CSV file, no API keys needed
>
> Why it matters: This shows how to build reliable AI systems where every answer is grounded in evidence."

**Demo Screenshot:**
- Show project folder structure (screenshot of VS Code)
- Quick overview: README visible

---

## ~1 min: Show It Run

**Terminal 1: Start the MCP Server**

```bash
python src/mcp_server.py
```

Expected output:
```
INFO: Starting MCP server on stdio
```

Keep this running.

**Terminal 2: Test with MCP Inspector (Optional, Quick)**

```bash
# Quick test (if you have npx installed)
npx @modelcontextprotocol/inspector ./src/mcp_server.py
```

Or skip this and go straight to crew.

**Terminal 2: Run the Crew**

```bash
# Run a sample question
python src/crew_main.py "What is our product return policy?"
```

**What to Show:**
- Show the agents thinking and working
- Highlight: "Agent 1 is researching..." and "Agent 2 is writing..."
- Show the final answer appears

**Key Visuals:**
- Terminal output showing both agents running
- Final answer with citations like "(Source: return_policy)"

---

## ~1.5 min: One Decision and One Failure

### The Decision

**Show decision_log.md in editor:**

> "One key decision I made: I chose simple text matching for search instead of embeddings.
>
> Why? Because:
> 1. No external dependencies (this project uses only 3 documents - text matching is fine)
> 2. It's transparent - I can easily explain what's happening
> 3. It fails gracefully - returns empty results, doesn't hallucinate
>
> In production, I'd use vector embeddings for 100K+ documents, but for this scope, simple is better.
>
> The tradeoff: Won't scale huge. The upside: It's bulletproof and understandable."

### The Failure

**Show conversation in notes or talk through it:**

> "The first problem was agents weren't citing sources. The crew would answer correctly but wouldn't say WHERE it found the information.
>
> I added to the task description: 'For EVERY claim, cite the source.' 
>
> Now watch the answer - see how it says '(Source: return_policy)' - that citation is the guardrail catching hallucination."

**Show Example:** Run one more question to prove sourcing works

```bash
python src/crew_main.py "What features are in the Premium package?"
```

Point out the sources in the answer.

---

## ~1 min: What You Learned

**Talk Through (Pick Top 3):**

### 1. MCP and CrewAI
> "MCP is a protocol. It lets me wrap Python functions as tools and serve them over stdio. CrewAI connects to those tools using MCPServerAdapter.
>
> The cool part: MCP doesn't care about the LLM. I could swap Claude for Ollama for Llama and the same server works."

### 2. Agent Safety
> "The big risk I took seriously was prompt injection. What if a document contains instructions that trick the LLM?
>
> My guard: I control the documents (they're synthetic), and I validate all inputs with Pydantic schemas. In production, I'd add a security check agent."

### 3. Sources Over Guesses
> "The core lesson: LLMs are great at synthesis but terrible at recalling exact facts. So I made the crew cite sources.
>
> If the answer can't be grounded, the agent says 'I don't know' instead of making something up. That's the real safety win here."

**Key Sources Used:**
- CrewAI docs (the MCP integration guide)
- FastMCP tutorial on YouTube
- ModelContextProtocol.io (the spec)

---

## ~30 sec: What's Next?

> "Before this touched real company data, I'd add:
>
> 1. **Vector search** - Replace text matching with embeddings for scale
> 2. **Approval gates** - Require a human to approve before saving reports
> 3. **Access control** - Only show users documents they have permission to see
> 4. **Audit logging** - Track every query and answer for compliance
>
> But the architecture is solid. The sourced answers work. And it proves the concept: AI agents + tools + grounding = reliable systems."

---

## Recording Tips

- **One take is fine.** No editing needed.
- **Show your face/voice** for credibility. Narrate over screen share.
- **Keep energy:** This is your interview rehearsal. Speak clearly and confidently.
- **Point at the screen:** Use cursor to highlight what you're talking about.
- **Test ahead:** Make sure code runs before recording (pre-run to check for long startup times).

---

## Timing Breakdown

| Time | Section | Notes |
|------|---------|-------|
| 0:00-1:00 | Pitch | What you built and why |
| 1:00-2:00 | Demo | Show it run, highlight sources |
| 2:00-3:30 | Decision & Failure | One design choice, one bug and fix |
| 3:30-4:30 | Learning | MCP, CrewAI, sourcing, safety |
| 4:30-5:00 | What's Next | 3 things you'd add |

**Total: 5:00**

---

## Checklist Before Recording

- [ ] Python 3.11+ installed
- [ ] `pip install -r requirements.txt` done
- [ ] `.env` configured with your model choice
- [ ] `python tests/test_mcp_tools.py` passes
- [ ] `python src/crew_main.py` runs without errors
- [ ] MCP server starts: `python src/mcp_server.py`
- [ ] Sample documents exist in `data/documents/`
- [ ] `outputs/` folder has some example reports
- [ ] Screen resolution: 1920x1080 or better (readable code)
- [ ] Quiet background, clear audio
- [ ] Have decision_log.md open for reference

---

## Commands to Run (Quick Reference)

```bash
# Setup
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
cp .env.example .env
# Edit .env to choose your model

# Terminal 1: MCP Server
python src/mcp_server.py

# Terminal 2: Run tests
python tests/test_mcp_tools.py      # Unit tests
python tests/test_crew.py            # End-to-end tests

# Terminal 2: Run crew on questions
python src/crew_main.py "What is our product return policy?"
python src/crew_main.py "What features are in Premium?"
python src/crew_main.py "How many support tickets were resolved?"
```

---

**Recording Date:** [Insert Date]  
**Duration:** ~5 minutes  
**Format:** MP4 (1920x1080, H.264)  
**Audio:** Your voice narrating + screen audio
