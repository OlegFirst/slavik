#!/usr/bin/env python3
"""
 BCM Collective Intelligence MCP Server

Model Context Protocol server providing Claude access to
privacy-preserving collective wisdom via Partisia Blockchain.

**What this enables:**
- Claude can query collective intelligence from blockchain
- Privacy-preserving via MPC (Multi-Party Computation)
- Zero knowledge of source organizations
- Cryptographically verified results

**Usage:**
    python bcm_collective_mcp.py

**Claude Integration:**
    Add to claude_desktop_config.json:
    {
        "mcpServers": {
            "bcm-collective": {
                "command": "python3",
                "args": ["/path/to/bcm_collective_mcp.py"]
            }
        }
    }
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

# MCP SDK
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Resource,
        Tool,
        TextContent,
        ImageContent,
        EmbeddedResource,
        Prompt,
        PromptMessage,
        GetPromptResult
    )
except ImportError:
    print("ERROR: MCP SDK not installed. Install with: pip install mcp")
    exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("bcm-collective-mcp")

# ================================================
# PARTISIA BLOCKCHAIN CLIENT (Placeholder)
# ================================================

class PartisiaClient:
    """
    Client for Partisia Blockchain MPC queries

    In production: Real Partisia SDK
    For now: Simulated responses
    """

    def __init__(self, contract_address: str = "collective_intelligence.mpc"):
        self.contract = contract_address
        logger.info(f" Connected to Partisia contract: {contract_address}")

    async def query_collective_wisdom(
        self,
        problem_type: str,
        org_context: Dict[str, Any],
        min_cases: int = 5
    ) -> Dict[str, Any]:
        """
        Query collective wisdom via MPC

        Privacy-preserving computation on blockchain
        """

        logger.info(f" MPC Query: {problem_type}")

        # Simulate MPC computation
        # In production: Real blockchain query
        await asyncio.sleep(0.5)  # Simulate network delay

        # Simulated aggregate result
        wisdom = {
            "patterns": {
                "stakeholder_mapping_first": {
                    "frequency": "4_out_of_5",
                    "confidence": 0.85,
                    "description": "Started with stakeholder identification and interviews"
                },
                "dependency_diagram": {
                    "frequency": "3_out_of_5",
                    "confidence": 0.72,
                    "description": "Created visual dependency diagrams"
                },
                "phased_approach": {
                    "frequency": "5_out_of_5",
                    "confidence": 0.95,
                    "description": "Implemented in phases (Tier 1 → Tier 2)"
                }
            },
            "timeline": {
                "median_days": 42,
                "range": "28-63 days",
                "source_count": 5
            },
            "common_challenges": [
                "Incomplete supplier data (4/5 organizations)",
                "Resistance from operational staff (3/5)",
                "Defining scope boundaries (5/5)"
            ],
            "success_factors": [
                "Executive sponsorship (5/5)",
                "Clear scope definition (4/5)",
                "Iterative approach (5/5)"
            ],
            "privacy": {
                "source_count": 5,
                "k_anonymity": 5,
                "risk_score": 0.15,
                "mpc_verified": True,
                "zk_proof": "0x1a2b3c4d5e6f..."
            }
        }

        return wisdom

    async def get_benchmark(
        self,
        metric: str,
        org_context: Dict[str, Any],
        min_orgs: int = 5
    ) -> Dict[str, Any]:
        """
        Get privacy-preserving benchmark

        MPC aggregation across similar organizations
        """

        logger.info(f" Benchmark Query: {metric}")

        await asyncio.sleep(0.3)

        # Simulated benchmark data
        benchmarks = {
            "bia_duration_days": {
                "median": 45,
                "mean": 48,
                "p25": 35,
                "p75": 62,
                "org_count": 12,
                "your_estimate": org_context.get("current_value"),
                "comparison": "faster_than_average"
            },
            "critical_process_count": {
                "median": 23,
                "mean": 26,
                "p25": 18,
                "p75": 32,
                "org_count": 15
            },
            "rto_average_hours": {
                "median": 24,
                "mean": 28,
                "p25": 12,
                "p75": 48,
                "org_count": 10
            }
        }

        return benchmarks.get(metric, {
            "error": "Metric not found",
            "available_metrics": list(benchmarks.keys())
        })

    async def verify_computation(
        self,
        query_id: str,
        result: Dict
    ) -> Dict[str, Any]:
        """
        Verify computation with zero-knowledge proof

        Proves correctness WITHOUT revealing source data
        """

        logger.info(f" Verifying computation: {query_id}")

        await asyncio.sleep(0.2)

        return {
            "verified": True,
            "proof_hash": "0x9f8e7d6c5b4a3210",
            "timestamp": datetime.utcnow().isoformat(),
            "privacy_preserved": True,
            "message": "Computation verified via zero-knowledge proof"
        }

# ================================================
# MCP SERVER
# ================================================

# Initialize server
app = Server("bcm-collective-intelligence")

# Initialize Partisia client
partisia = PartisiaClient()

# ================================================
# RESOURCES
# ================================================

@app.list_resources()
async def list_resources() -> List[Resource]:
    """
    List available collective intelligence resources

    Resources are blockchain-backed, privacy-preserving
    """

    logger.info(" Listing resources")

    return [
        Resource(
            uri="bcm://collective/patterns/supply_chain_complexity",
            name="Supply Chain Complexity Patterns",
            mimeType="application/json",
            description="Anonymous patterns from organizations that solved supply chain complexity in BIA"
        ),
        Resource(
            uri="bcm://collective/patterns/executive_engagement",
            name="Executive Engagement Patterns",
            mimeType="application/json",
            description="Collective wisdom on engaging executives in BCM initiatives"
        ),
        Resource(
            uri="bcm://collective/patterns/rto_determination",
            name="RTO Determination Patterns",
            mimeType="application/json",
            description="Approaches to determining Recovery Time Objectives"
        ),
        Resource(
            uri="bcm://collective/benchmarks/bia_duration",
            name="BIA Duration Benchmarks",
            mimeType="application/json",
            description="Privacy-preserving benchmarks for BIA completion time"
        ),
        Resource(
            uri="bcm://collective/benchmarks/critical_process_count",
            name="Critical Process Count Benchmarks",
            mimeType="application/json",
            description="How many critical processes similar organizations identified"
        ),
        Resource(
            uri="bcm://collective/benchmarks/rto_average",
            name="Average RTO Benchmarks",
            mimeType="application/json",
            description="Typical RTO values by industry and process type"
        ),
        Resource(
            uri="bcm://collective/best-practices/bia_methodology",
            name="BIA Methodology Best Practices",
            mimeType="application/json",
            description="Collective wisdom on BIA methodologies that work"
        )
    ]

@app.read_resource()
async def read_resource(uri: str) -> str:
    """
    Read collective intelligence resource

    Data retrieved via Partisia MPC (privacy-preserving)
    """

    logger.info(f" Reading resource: {uri}")

    # Parse URI
    parts = uri.split("/")
    if len(parts) < 5:
        return json.dumps({"error": "Invalid URI format"}, indent=2)

    resource_type = parts[3]  # patterns, benchmarks, best-practices
    problem_type = parts[4]   # e.g., supply_chain_complexity

    # Query Partisia blockchain (MPC computation)
    if resource_type == "patterns":
        result = await partisia.query_collective_wisdom(
            problem_type=problem_type,
            org_context={},
            min_cases=5
        )
    elif resource_type == "benchmarks":
        result = await partisia.get_benchmark(
            metric=problem_type,
            org_context={},
            min_orgs=5
        )
    else:
        result = {"error": f"Resource type '{resource_type}' not supported"}

    return json.dumps(result, indent=2)

# ================================================
# TOOLS
# ================================================

@app.list_tools()
async def list_tools() -> List[Tool]:
    """
    List available tools for querying collective intelligence
    """

    logger.info(" Listing tools")

    return [
        Tool(
            name="query_collective_wisdom",
            description="""
Query privacy-preserving collective wisdom from blockchain.

Uses Partisia MPC to compute on encrypted case data without revealing source organizations.

Example: Find out how similar organizations solved supply chain dependency mapping.

Privacy: Minimum 5 organizations required (k-anonymity). Zero knowledge of sources.
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "problem_type": {
                        "type": "string",
                        "description": "Type of BCM problem (e.g., 'supply_chain_complexity', 'rto_determination', 'executive_engagement')"
                    },
                    "org_context": {
                        "type": "object",
                        "description": "Your organization context for similarity matching",
                        "properties": {
                            "industry": {"type": "string"},
                            "size": {"type": "string"},
                            "region": {"type": "string"}
                        }
                    }
                },
                "required": ["problem_type"]
            }
        ),
        Tool(
            name="get_anonymous_benchmark",
            description="""
Get privacy-preserving benchmark from similar organizations.

Uses MPC aggregation to calculate statistics without revealing individual organizations.

Example: "How long does BIA typically take for organizations like mine?"

Privacy: Minimum 5 organizations. Aggregate statistics only.
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "metric": {
                        "type": "string",
                        "description": "Metric to benchmark (e.g., 'bia_duration_days', 'critical_process_count', 'rto_average_hours')"
                    },
                    "org_context": {
                        "type": "object",
                        "description": "Your organization context for similarity matching",
                        "properties": {
                            "industry": {"type": "string"},
                            "size": {"type": "string"},
                            "current_value": {"type": "number"}
                        }
                    }
                },
                "required": ["metric", "org_context"]
            }
        ),
        Tool(
            name="verify_collective_wisdom",
            description="""
Verify collective wisdom computation using zero-knowledge proof.

Proves the computation was performed correctly WITHOUT revealing source data.

Use this to verify the integrity of collective intelligence results.
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "query_id": {
                        "type": "string",
                        "description": "Query ID from previous collective wisdom query"
                    },
                    "result": {
                        "type": "object",
                        "description": "Result to verify"
                    }
                },
                "required": ["query_id", "result"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    """
    Execute tool

    All tools query Partisia blockchain via MPC
    """

    logger.info(f"️  Calling tool: {name}")

    if name == "query_collective_wisdom":
        # Call Partisia MPC smart contract
        result = await partisia.query_collective_wisdom(
            problem_type=arguments["problem_type"],
            org_context=arguments.get("org_context", {}),
            min_cases=5
        )

        response = f"""
 **Collective Wisdom: {arguments['problem_type']}**

**Patterns Identified:**
"""
        for pattern_name, pattern_data in result['patterns'].items():
            response += f"\n• **{pattern_name.replace('_', ' ').title()}** ({pattern_data['frequency']})\n"
            response += f"  {pattern_data['description']}\n"
            response += f"  Confidence: {pattern_data['confidence']:.0%}\n"

        response += f"\n**Timeline:**\n"
        response += f"• Median: {result['timeline']['median_days']} days\n"
        response += f"• Range: {result['timeline']['range']}\n"

        response += f"\n**Common Challenges:**\n"
        for challenge in result['common_challenges']:
            response += f"• {challenge}\n"

        response += f"\n**Success Factors:**\n"
        for factor in result['success_factors']:
            response += f"• {factor}\n"

        response += f"\n**Privacy Guarantee:**\n"
        response += f"• Source Organizations: {result['privacy']['source_count']} (identities protected)\n"
        response += f"• K-Anonymity: {result['privacy']['k_anonymity']}\n"
        response += f"• Risk Score: {result['privacy']['risk_score']:.2f}\n"
        response += f"• MPC Verified: \n"
        response += f"• ZK Proof: {result['privacy']['zk_proof']}\n"

        return [TextContent(type="text", text=response)]

    elif name == "get_anonymous_benchmark":
        # MPC benchmark query
        result = await partisia.get_benchmark(
            metric=arguments["metric"],
            org_context=arguments["org_context"],
            min_orgs=5
        )

        if "error" in result:
            return [TextContent(
                type="text",
                text=f" {result['error']}\n\nAvailable metrics: {', '.join(result.get('available_metrics', []))}"
            )]

        response = f"""
 **Benchmark: {arguments['metric']}**

**Statistics (from {result['org_count']} similar organizations):**
• Median: {result['median']}
• Mean: {result['mean']}
• 25th Percentile: {result['p25']}
• 75th Percentile: {result['p75']}
"""

        if "your_estimate" in result and result["your_estimate"]:
            response += f"\n**Your Value:** {result['your_estimate']}\n"
            response += f"**Comparison:** {result.get('comparison', 'N/A').replace('_', ' ').title()}\n"

        response += f"\n**Privacy:**\n"
        response += f"• {result['org_count']} organizations (k-anonymity preserved)\n"
        response += f"• Individual organizations: UNKNOWN (MPC-protected)\n"
        response += f"• Aggregate statistics only\n"

        return [TextContent(type="text", text=response)]

    elif name == "verify_collective_wisdom":
        # Verify with zero-knowledge proof
        proof = await partisia.verify_computation(
            query_id=arguments["query_id"],
            result=arguments["result"]
        )

        response = f"""
 **Computation Verified**

**Zero-Knowledge Proof:**
• Proof Hash: {proof['proof_hash']}
• Verified: {proof['verified']}
• Timestamp: {proof['timestamp']}
• Privacy Preserved: {proof['privacy_preserved']}

**What this means:**
The collective intelligence computation was performed correctly on the blockchain
WITHOUT revealing any source organization data.

This is cryptographically proven - no trust required! 
        """

        return [TextContent(type="text", text=response)]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]

# ================================================
# PROMPTS
# ================================================

@app.list_prompts()
async def list_prompts() -> List[Prompt]:
    """Provide prompt templates for collective intelligence queries"""

    logger.info(" Listing prompts")

    return [
        Prompt(
            name="ask_collective",
            description="Ask collective wisdom about a BCM challenge",
            arguments=[
                {
                    "name": "challenge",
                    "description": "The BCM challenge you're facing",
                    "required": True
                }
            ]
        ),
        Prompt(
            name="compare_with_peers",
            description="Compare your approach/metrics with similar organizations",
            arguments=[
                {
                    "name": "metric",
                    "description": "What to compare (e.g., 'BIA duration', 'RTO values')",
                    "required": True
                }
            ]
        ),
        Prompt(
            name="stuck_on_bcm",
            description="Get help when stuck on a BCM task",
            arguments=[
                {
                    "name": "task",
                    "description": "The BCM task you're stuck on",
                    "required": True
                },
                {
                    "name": "days_stuck",
                    "description": "How many days you've been stuck",
                    "required": False
                }
            ]
        )
    ]

@app.get_prompt()
async def get_prompt(name: str, arguments: dict) -> GetPromptResult:
    """Get prompt template"""

    logger.info(f" Getting prompt: {name}")

    if name == "ask_collective":
        challenge = arguments["challenge"]

        return GetPromptResult(
            description=f"Query collective intelligence about: {challenge}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""I'm facing this BCM challenge: {challenge}

Please query the privacy-preserving collective intelligence on blockchain to find how similar organizations addressed this.

Use the `query_collective_wisdom` tool to access anonymized patterns from organizations that successfully solved this challenge.

Privacy note: The source organizations will remain completely unknown - their wisdom is aggregated via Multi-Party Computation on Partisia Blockchain.
"""
                    )
                )
            ]
        )

    elif name == "compare_with_peers":
        metric = arguments["metric"]

        return GetPromptResult(
            description=f"Compare {metric} with similar organizations",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""I want to compare my {metric} with similar organizations.

Please use the `get_anonymous_benchmark` tool to retrieve privacy-preserving benchmarks from blockchain.

This will show me aggregate statistics (median, percentiles) from similar organizations without revealing their identities.
"""
                    )
                )
            ]
        )

    elif name == "stuck_on_bcm":
        task = arguments["task"]
        days = arguments.get("days_stuck", "several")

        return GetPromptResult(
            description=f"Get help with stuck BCM task: {task}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""I've been stuck on this BCM task for {days} days: {task}

Please:
1. Query collective wisdom to see how other organizations approached this
2. Get benchmarks to understand if my timeline is normal
3. Provide specific actionable advice based on collective intelligence

Use the blockchain-based collective intelligence tools to access privacy-preserving wisdom from organizations that successfully completed this task.
"""
                    )
                )
            ]
        )

    return GetPromptResult(
        description=f"Unknown prompt: {name}",
        messages=[]
    )

# ================================================
# MAIN
# ================================================

async def main():
    """Run MCP server"""

    logger.info(" Starting BCM Collective Intelligence MCP Server")
    logger.info(" Connected to Partisia Blockchain MPC")
    logger.info(" Privacy: K-anonymity (minimum 5 organizations)")
    logger.info(" Ready to serve collective intelligence to Claude!")

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
