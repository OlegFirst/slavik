# 🤝 BCM Collective Intelligence MCP Server

**Model Context Protocol server providing Claude access to privacy-preserving collective wisdom**

---

## 🎯 WHAT THIS IS

MCP server that connects **Claude** to **Partisia Blockchain** for privacy-preserving collective intelligence.

```
Claude ←→ MCP Server ←→ Partisia Blockchain (MPC) ←→ Encrypted Case Data
```

**Result:** Claude can access collective wisdom from multiple organizations WITHOUT knowing who they are!

---

## 🚀 QUICK START

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Server

```bash
python bcm_collective_mcp.py
```

### 3. Configure Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "bcm-collective": {
      "command": "python3",
      "args": ["/Users/MD/AI-Platform-ISO/infrastructure/mcp-server/bcm_collective_mcp.py"]
    }
  }
}
```

### 4. Restart Claude Desktop

The server will appear in Claude's MCP menu!

---

## 📚 RESOURCES

Resources Claude can access:

### Patterns
- `bcm://collective/patterns/supply_chain_complexity`
- `bcm://collective/patterns/executive_engagement`
- `bcm://collective/patterns/rto_determination`

### Benchmarks
- `bcm://collective/benchmarks/bia_duration`
- `bcm://collective/benchmarks/critical_process_count`
- `bcm://collective/benchmarks/rto_average`

### Best Practices
- `bcm://collective/best-practices/bia_methodology`

---

## 🔧 TOOLS

Tools Claude can use:

### 1. `query_collective_wisdom`

Query privacy-preserving patterns from blockchain.

**Example:**
```python
query_collective_wisdom(
    problem_type="supply_chain_complexity",
    org_context={
        "industry": "healthcare",
        "size": "medium",
        "region": "pacific_northwest"
    }
)
```

**Returns:**
```json
{
    "patterns": {
        "stakeholder_mapping_first": {
            "frequency": "4_out_of_5",
            "confidence": 0.85
        }
    },
    "privacy": {
        "source_count": 5,
        "k_anonymity": 5,
        "mpc_verified": true
    }
}
```

### 2. `get_anonymous_benchmark`

Get aggregate benchmarks from similar organizations.

**Example:**
```python
get_anonymous_benchmark(
    metric="bia_duration_days",
    org_context={
        "industry": "healthcare",
        "size": "medium",
        "current_value": 38
    }
)
```

**Returns:**
```json
{
    "median": 45,
    "mean": 48,
    "p25": 35,
    "p75": 62,
    "org_count": 12,
    "your_estimate": 38,
    "comparison": "faster_than_average"
}
```

### 3. `verify_collective_wisdom`

Verify computation with zero-knowledge proof.

**Example:**
```python
verify_collective_wisdom(
    query_id="query-123",
    result={...}
)
```

**Returns:**
```json
{
    "verified": true,
    "proof_hash": "0x9f8e7d6c...",
    "privacy_preserved": true
}
```

---

## 💭 PROMPTS

Pre-built prompts for common scenarios:

### 1. `ask_collective`

Ask collective wisdom about a challenge.

**Usage in Claude:**
```
Use prompt: ask_collective
Challenge: "How to map Tier 2 supplier dependencies"
```

### 2. `compare_with_peers`

Compare your metrics with similar organizations.

**Usage in Claude:**
```
Use prompt: compare_with_peers
Metric: "BIA duration"
```

### 3. `stuck_on_bcm`

Get help when stuck on a BCM task.

**Usage in Claude:**
```
Use prompt: stuck_on_bcm
Task: "Supply chain dependency mapping"
Days stuck: 10
```

---

## 🎬 EXAMPLE SESSION

**User in Claude Desktop:**
> I'm struggling with supply chain dependency mapping in my BIA. How did other organizations approach this?

**Claude (via MCP):**
> Let me query the collective intelligence for you...

*Claude calls: `query_collective_wisdom(problem_type="supply_chain_complexity")`*

**Claude's Response:**
> 🤝 **Collective Wisdom: Supply Chain Complexity**
>
> Based on privacy-preserving analysis of 5 similar healthcare organizations:
>
> **Patterns Identified:**
> • **Stakeholder Mapping First** (4 out of 5)
>   Started with stakeholder identification and interviews
>   Confidence: 85%
>
> • **Phased Approach** (5 out of 5)
>   Implemented in phases (Tier 1 → Tier 2)
>   Confidence: 95%
>
> **Timeline:**
> • Median: 42 days
> • Range: 28-63 days
>
> **Common Challenges:**
> • Incomplete supplier data (4/5 organizations)
> • Resistance from operational staff (3/5)
>
> **Success Factors:**
> • Executive sponsorship (5/5)
> • Iterative approach (5/5)
>
> **Privacy Guarantee:**
> • Source Organizations: 5 (identities protected)
> • K-Anonymity: 5
> • MPC Verified: ✅
> • ZK Proof: 0x1a2b3c4d...

---

## 🔒 PRIVACY ARCHITECTURE

### How Privacy Works

```
Organization A (Healthcare, Seattle)
     ↓ Submits case
Partisia Blockchain
     ↓ Secret Sharing (MPC)
[Node 1: Shard 1] [Node 2: Shard 2] [Node 3: Shard 3]
     ↓ MPC Computation (encrypted!)
Aggregate Result (no source info)
     ↓ Via MCP
Claude (sees only aggregate)
     ↓ Response
User (learns from collective, zero knowledge of sources)
```

### Privacy Guarantees

- ✅ **K-Anonymity:** Minimum 5 organizations required
- ✅ **MPC:** Computation on encrypted data
- ✅ **Zero Knowledge:** Source organizations never revealed
- ✅ **ZK Proofs:** Cryptographically verified results
- ✅ **Decentralized:** No single entity can de-anonymize

---

## 🛠️ DEVELOPMENT

### Testing Locally

```bash
# Run server
python bcm_collective_mcp.py

# In another terminal, test with MCP inspector
npx @modelcontextprotocol/inspector python bcm_collective_mcp.py
```

### Connecting to Real Partisia Blockchain

Replace `PartisiaClient` placeholder with real SDK:

```python
from partisia_sdk import PartisiaBlockchain

partisia = PartisiaBlockchain(
    contract_address="0x...",
    node_endpoints=[
        "https://node1.partisiablockchain.com",
        "https://node2.partisiablockchain.com",
        "https://node3.partisiablockchain.com"
    ]
)
```

---

## 📊 METRICS

Track MCP usage:

```python
# Log analytics
logger.info(f"Tool called: {name}")
logger.info(f"Problem type: {problem_type}")
logger.info(f"Results: {source_count} orgs")
```

---

## 🚀 DEPLOYMENT

### Production Setup

1. **Deploy to Cloud**
   ```bash
   docker build -t bcm-mcp-server .
   docker run -d bcm-mcp-server
   ```

2. **Configure for Organization**
   ```json
   {
     "mcpServers": {
       "bcm-collective": {
         "command": "docker",
         "args": ["run", "-i", "bcm-mcp-server"]
       }
     }
   }
   ```

3. **Monitor**
   ```bash
   docker logs -f bcm-mcp-server
   ```

---

## 🎯 USE CASES

### 1. Stuck Detection Integration

When organization detected as stuck:
```python
# Collective Agent uses MCP
wisdom = mcp_client.query_collective_wisdom(
    problem_type=stuck_on,
    org_context=user_org
)

# Create agent with blockchain wisdom
agent = create_collective_agent(wisdom)
```

### 2. Benchmarking

User wants to compare:
```python
benchmark = mcp_client.get_anonymous_benchmark(
    metric="bia_duration_days",
    org_context={"industry": "healthcare", "size": "medium"}
)

# Show: "You're faster than 65% of similar organizations"
```

### 3. Best Practice Discovery

User exploring options:
```python
practices = mcp_client.query_collective_wisdom(
    problem_type="executive_engagement",
    org_context=user_org
)

# Returns patterns from successful organizations
```

---

**Ready to connect Claude to blockchain! 🚀🔐✨**
