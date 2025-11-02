"""
Complete Working Example: End-to-End Train Production AI Agent
This demonstrates the full workflow from query to response
"""

import asyncio
import json
from datetime import datetime

# ============================================================================
# SIMULATED DEMO (No real database needed for testing)
# ============================================================================

class MockDatabase:
    """Mock database for testing without real DB connection"""
    
    def __init__(self):
        self.projects = {
            "TRN-2024-001": {
                "project_id": "TRN-2024-001",
                "project_name": "Metro Series 3000 - City Transit",
                "train_model": "Metro-3000",
                "num_trains": 8,
                "status": "in_progress",
                "total_phases": 6,
                "total_commitments": 15
            },
            "TRN-2023-045": {
                "project_id": "TRN-2023-045",
                "project_name": "Metro Series 3000 - Bay Area",
                "train_model": "Metro-3000",
                "num_trains": 10,
                "status": "completed",
                "total_phases": 6,
                "total_commitments": 18
            }
        }
        
        self.phases = {
            "TRN-2024-001": [
                {
                    "phase_name": "Bogie Assembly",
                    "sequence_order": 1,
                    "estimated_hours": 320,
                    "department": "Mechanical",
                    "status": "in_progress"
                },
                {
                    "phase_name": "Car Body Welding",
                    "sequence_order": 2,
                    "estimated_hours": 480,
                    "department": "Fabrication",
                    "status": "pending"
                },
                {
                    "phase_name": "Interior Fitting",
                    "sequence_order": 3,
                    "estimated_hours": 240,
                    "department": "Interior",
                    "status": "pending"
                },
                {
                    "phase_name": "HVAC Installation",
                    "sequence_order": 4,
                    "estimated_hours": 160,
                    "department": "HVAC",
                    "status": "pending"
                },
                {
                    "phase_name": "Cable Installation",
                    "sequence_order": 5,
                    "estimated_hours": 200,
                    "department": "Electrical",
                    "status": "pending"
                },
                {
                    "phase_name": "Testing and Commissioning",
                    "sequence_order": 6,
                    "estimated_hours": 400,
                    "department": "QA",
                    "status": "pending"
                }
            ]
        }
        
        self.phase_statistics = {
            "Bogie Assembly": {
                "avg_duration_hours": 305,
                "avg_cost": 43500,
                "success_rate": 0.92,
                "occurrences": 25
            },
            "Car Body Welding": {
                "avg_duration_hours": 465,
                "avg_cost": 72000,
                "success_rate": 0.88,
                "occurrences": 28
            },
            "HVAC Installation": {
                "avg_duration_hours": 155,
                "avg_cost": 51000,
                "success_rate": 0.95,
                "occurrences": 22
            }
        }
        
        self.similar_projects = [
            {
                "project_id": "TRN-2023-045",
                "similarity_score": 0.95,
                "matching_phases": 6,
                "train_model": "Metro-3000",
                "num_trains": 10,
                "completion_date": "2023-11-15"
            },
            {
                "project_id": "TRN-2023-012",
                "similarity_score": 0.88,
                "matching_phases": 5,
                "train_model": "Metro-3000",
                "num_trains": 6,
                "completion_date": "2023-08-22"
            }
        ]
    
    def get_project_overview(self, project_id: str):
        return self.projects.get(project_id)
    
    def get_project_phases(self, project_id: str):
        return self.phases.get(project_id, [])
    
    def get_phase_statistics(self, phase_names: list):
        return {
            name: self.phase_statistics.get(name) 
            for name in phase_names 
            if name in self.phase_statistics
        }
    
    def search_similar_projects(self, phase_subset: list, train_model: str):
        # Simple similarity matching
        return self.similar_projects


# ============================================================================
# EXAMPLE 1: Simple Query Workflow
# ============================================================================

async def example_simple_query():
    """
    Example: Simple information retrieval
    Query: "How many phases are in project TRN-2024-001?"
    """
    print("\n" + "="*80)
    print("EXAMPLE 1: Simple Query - Project Phase Count")
    print("="*80 + "\n")
    
    db = MockDatabase()
    
    # Step 1: User asks question
    user_query = "How many phases are in project TRN-2024-001?"
    print(f"👤 User Query: {user_query}\n")
    
    # Step 2: LLM decides to use get_project_overview tool
    print("🤖 Agent Reasoning:")
    print("   - Identified need for project information")
    print("   - Selected tool: get_project_overview")
    print("   - Parameters: project_id='TRN-2024-001'\n")
    
    # Step 3: MCP server executes tool
    print("🔧 Executing Tool...")
    project_data = db.get_project_overview("TRN-2024-001")
    print(f"   Tool Response: {json.dumps(project_data, indent=2)}\n")
    
    # Step 4: LLM synthesizes response
    response = f"""Project TRN-2024-001 ({project_data['project_name']}) has {project_data['total_phases']} production phases. 
The project is currently {project_data['status']} and involves manufacturing {project_data['num_trains']} {project_data['train_model']} trains."""
    
    print("💬 Agent Response:")
    print(f"   {response}\n")
    
    return response


# ============================================================================
# EXAMPLE 2: Multi-Step Query Workflow
# ============================================================================

async def example_multi_step_query():
    """
    Example: Query requiring multiple tool calls
    Query: "What are the phases in TRN-2024-001 and their statistics?"
    """
    print("\n" + "="*80)
    print("EXAMPLE 2: Multi-Step Query - Phases with Statistics")
    print("="*80 + "\n")
    
    db = MockDatabase()
    
    # Step 1: User asks question
    user_query = "What are the phases in TRN-2024-001 and show me statistics for them?"
    print(f"👤 User Query: {user_query}\n")
    
    # Step 2: LLM plans multi-step approach
    print("🤖 Agent Planning:")
    print("   - Need to retrieve project phases first")
    print("   - Then get statistics for those phases")
    print("   - Will make 2 tool calls\n")
    
    # Step 3a: First tool call - get phases
    print("🔧 Tool Call 1: get_project_phases")
    print("   Parameters: project_id='TRN-2024-001'\n")
    
    phases = db.get_project_phases("TRN-2024-001")
    print(f"   Retrieved {len(phases)} phases")
    for p in phases[:3]:  # Show first 3
        print(f"   - {p['phase_name']} ({p['estimated_hours']} hours)")
    print("   ...\n")
    
    # Step 3b: Second tool call - get statistics
    phase_names = [p['phase_name'] for p in phases[:3]]
    print("🔧 Tool Call 2: get_phase_statistics")
    print(f"   Parameters: phase_names={phase_names}\n")
    
    stats = db.get_phase_statistics(phase_names)
    print("   Retrieved statistics:")
    for name, data in stats.items():
        if data:
            print(f"   - {name}: avg {data['avg_duration_hours']}h, success rate {data['success_rate']:.0%}")
    print()
    
    # Step 4: LLM synthesizes comprehensive response
    response = """Project TRN-2024-001 has 6 production phases:

1. **Bogie Assembly** (320h estimated)
   - Historical average: 305 hours
   - Success rate: 92%
   - Based on 25 similar projects

2. **Car Body Welding** (480h estimated)
   - Historical average: 465 hours
   - Success rate: 88%
   - Based on 28 similar projects

3. **Interior Fitting** (240h estimated)
4. **HVAC Installation** (160h estimated)
   - Historical average: 155 hours
   - Success rate: 95%
   - Based on 22 similar projects

5. **Cable Installation** (200h estimated)
6. **Testing and Commissioning** (400h estimated)

The estimates are slightly above historical averages, suggesting a conservative timeline."""
    
    print("💬 Agent Response:")
    print(f"{response}\n")
    
    return response


# ============================================================================
# EXAMPLE 3: Complex Skeleton Building Workflow
# ============================================================================

async def example_complex_skeleton_building():
    """
    Example: Complex multi-step analysis and skeleton generation
    Query: "Build a project skeleton for Metro-3000, 8 trains, with these phases..."
    """
    print("\n" + "="*80)
    print("EXAMPLE 3: Complex Query - Skeleton Building")
    print("="*80 + "\n")
    
    db = MockDatabase()
    
    # Step 1: User asks complex question
    user_query = """I need to create a new project for Metro-3000 trains.
We'll produce 8 trains with these phases: Bogie Assembly, Car Body Welding, 
Interior Fitting, HVAC Installation, Cable Installation, Testing.
Can you find similar projects and build me a detailed skeleton?"""
    
    print(f"👤 User Query:\n{user_query}\n")
    
    # Step 2: LLM breaks down into subtasks
    print("🤖 Agent Planning:")
    print("   1. Search for similar Metro-3000 projects")
    print("   2. Get phase statistics for the specified phases")
    print("   3. Build prefilled skeleton with historical data")
    print("   4. Provide recommendations\n")
    
    # Step 3a: Search similar projects
    print("🔧 Step 1: search_similar_projects")
    phase_subset = ["Bogie Assembly", "Car Body Welding", "Interior Fitting", 
                    "HVAC Installation", "Cable Installation", "Testing"]
    print(f"   Searching for: {phase_subset[:3]}...")
    
    similar = db.search_similar_projects(phase_subset, "Metro-3000")
    print(f"\n   Found {len(similar)} similar projects:")
    for proj in similar:
        print(f"   - {proj['project_id']}: {proj['similarity_score']:.0%} match, "
              f"{proj['num_trains']} trains, completed {proj['completion_date']}")
    print()
    
    # Step 3b: Get phase statistics
    print("🔧 Step 2: get_phase_statistics")
    stats = db.get_phase_statistics(phase_subset)
    print(f"   Retrieved statistics for {len(stats)} phases\n")
    
    # Step 3c: Build skeleton (simulated)
    print("🔧 Step 3: build_project_skeleton")
    print("   Analyzing historical data...")
    print("   Scaling estimates for 8 trains...")
    print("   Calculating resource requirements...\n")
    
    skeleton = {
        "project_template": "Metro-3000-8-trains",
        "estimated_duration": "45 weeks",
        "total_estimated_hours": 1800,
        "confidence": "High (based on 2 highly similar projects)",
        "phases": [
            {
                "name": "Bogie Assembly",
                "estimated_hours": 320,
                "scaled_from": "TRN-2023-045 (10 trains, 400h)",
                "department": "Mechanical",
                "typical_cost": 45000,
                "confidence": "High"
            },
            {
                "name": "Car Body Welding",
                "estimated_hours": 480,
                "scaled_from": "TRN-2023-045 (10 trains, 600h)",
                "department": "Fabrication",
                "typical_cost": 75000,
                "confidence": "High"
            },
            {
                "name": "Interior Fitting",
                "estimated_hours": 240,
                "department": "Interior",
                "typical_cost": 38000,
                "confidence": "Medium"
            },
            {
                "name": "HVAC Installation",
                "estimated_hours": 160,
                "scaled_from": "Average of 22 projects",
                "department": "HVAC",
                "typical_cost": 52000,
                "confidence": "High"
            },
            {
                "name": "Cable Installation",
                "estimated_hours": 200,
                "department": "Electrical",
                "typical_cost": 28000,
                "confidence": "Medium"
            },
            {
                "name": "Testing and Commissioning",
                "estimated_hours": 400,
                "department": "QA",
                "typical_cost": 95000,
                "confidence": "Medium"
            }
        ],
        "recommended_resources": {
            "welding_specialists": 12,
            "electrical_engineers": 8,
            "qa_personnel": 6
        }
    }
    
    # Step 4: LLM generates comprehensive response
    print("💬 Agent Response:\n")
    
    response = f"""I've analyzed similar Metro-3000 projects and created a detailed skeleton for your 8-train project.

📊 **PROJECT OVERVIEW**
- Base Template: {skeleton['project_template']}
- Estimated Duration: {skeleton['estimated_duration']}
- Total Hours: {skeleton['total_estimated_hours']}
- Confidence Level: {skeleton['confidence']}

📋 **DETAILED PHASE BREAKDOWN**

1. **Bogie Assembly** - 320 hours
   ├─ Based on: TRN-2023-045 (scaled from 10 to 8 trains)
   ├─ Department: Mechanical
   ├─ Estimated Cost: €45,000
   └─ Confidence: High ⭐⭐⭐

2. **Car Body Welding** - 480 hours
   ├─ Based on: TRN-2023-045 (scaled from 10 to 8 trains)
   ├─ Department: Fabrication
   ├─ Estimated Cost: €75,000
   └─ Confidence: High ⭐⭐⭐

3. **Interior Fitting** - 240 hours
   ├─ Department: Interior
   ├─ Estimated Cost: €38,000
   └─ Confidence: Medium ⭐⭐

4. **HVAC Installation** - 160 hours
   ├─ Based on: 22 historical projects average
   ├─ Department: HVAC
   ├─ Estimated Cost: €52,000
   └─ Confidence: High ⭐⭐⭐

5. **Cable Installation** - 200 hours
   ├─ Department: Electrical
   ├─ Estimated Cost: €28,000
   └─ Confidence: Medium ⭐⭐

6. **Testing and Commissioning** - 400 hours
   ├─ Department: QA
   ├─ Estimated Cost: €95,000
   └─ Confidence: Medium ⭐⭐

💡 **KEY RECOMMENDATIONS**

1. **Resource Allocation**: Based on TRN-2023-045 and TRN-2023-012:
   - Welding Specialists: 12 personnel
   - Electrical Engineers: 8 personnel
   - QA Personnel: 6 personnel

2. **Risk Factors**:
   - Car Body Welding historically has 88% on-time completion
   - Consider adding 10% buffer to this phase

3. **Dependencies**:
   - Interior Fitting cannot start until Car Body Welding is 80% complete
   - Testing requires all other phases completed

4. **Timeline Optimization**:
   - HVAC and Cable Installation can be parallelized
   - Consider starting interior work while mechanical assembly completes

5. **Cost Comparison**:
   - Your estimates: €333,000 total
   - TRN-2023-045 (adjusted): €325,000
   - Within 2.5% variance - reasonable budget

📈 **NEXT STEPS**

1. Review and adjust the skeleton based on your specific requirements
2. Assign department heads to each phase
3. Set up milestone reviews at 25%, 50%, and 75% completion
4. Consider procurement lead times for HVAC and electrical components

Would you like me to:
- Export this skeleton to your project management system?
- Generate a detailed Gantt chart with dependencies?
- Calculate detailed resource loading by week?
"""
    
    print(response)
    print("\n" + "="*80)
    print(f"✅ Skeleton generated successfully!")
    print(f"   Total execution time: ~3.5 seconds")
    print(f"   Tools used: 3")
    print(f"   Confidence: High (95% match with historical data)")
    print("="*80 + "\n")
    
    return skeleton


# ============================================================================
# EXAMPLE 4: Interactive Conversation Flow
# ============================================================================

async def example_interactive_conversation():
    """
    Example: Multi-turn conversation with context
    """
    print("\n" + "="*80)
    print("EXAMPLE 4: Interactive Conversation with Context")
    print("="*80 + "\n")
    
    db = MockDatabase()
    conversation_context = []
    
    # Turn 1
    print("👤 User: Tell me about project TRN-2024-001\n")
    
    project = db.get_project_overview("TRN-2024-001")
    response1 = f"""Project TRN-2024-001 is the {project['project_name']} project. 
It's currently {project['status']} and involves {project['num_trains']} {project['train_model']} trains 
with {project['total_phases']} production phases and {project['total_commitments']} resource commitments."""
    
    print(f"🤖 Agent: {response1}\n")
    conversation_context.append({"project_id": "TRN-2024-001"})
    
    # Turn 2 - Uses context
    print("👤 User: What phases does it have?\n")
    print("🤖 Agent: (Using context: TRN-2024-001 from previous question)\n")
    
    phases = db.get_project_phases("TRN-2024-001")
    response2 = f"""The project has {len(phases)} phases:

1. Bogie Assembly (320h) - Currently in progress
2. Car Body Welding (480h) - Pending
3. Interior Fitting (240h) - Pending
4. HVAC Installation (160h) - Pending
5. Cable Installation (200h) - Pending
6. Testing and Commissioning (400h) - Pending

Total estimated: 1,800 hours across all phases."""
    
    print(f"🤖 Agent: {response2}\n")
    
    # Turn 3 - Follow-up with specifics
    print("👤 User: How does Bogie Assembly compare to similar projects?\n")
    print("🤖 Agent: (Retrieving statistics for Bogie Assembly phase)\n")
    
    stats = db.get_phase_statistics(["Bogie Assembly"])
    response3 = f"""For Bogie Assembly in this project (320 hours estimated):

📊 Historical Comparison (based on {stats['Bogie Assembly']['occurrences']} projects):
- Your estimate: 320 hours
- Historical average: {stats['Bogie Assembly']['avg_duration_hours']} hours
- Difference: +{320 - stats['Bogie Assembly']['avg_duration_hours']} hours (+4.9%)

✅ Success Rate: {stats['Bogie Assembly']['success_rate']:.0%}
💰 Typical Cost: €{stats['Bogie Assembly']['avg_cost']:,}

Your estimate is slightly above average, which provides a good buffer. 
The 92% success rate indicates this phase is generally predictable."""
    
    print(f"🤖 Agent: {response3}\n")
    
    print("="*80)
    print("✅ Multi-turn conversation demonstrates:")
    print("   - Context retention across turns")
    print("   - Natural follow-up question handling")
    print("   - Progressive information disclosure")
    print("="*80 + "\n")


# ============================================================================
# EXAMPLE 5: Error Handling and Edge Cases
# ============================================================================

async def example_error_handling():
    """
    Example: How the system handles errors and edge cases
    """
    print("\n" + "="*80)
    print("EXAMPLE 5: Error Handling and Edge Cases")
    print("="*80 + "\n")
    
    db = MockDatabase()
    
    # Case 1: Non-existent project
    print("📝 Case 1: Non-existent Project\n")
    print("👤 User: Show me details for project TRN-9999-999\n")
    
    project = db.get_project_overview("TRN-9999-999")
    if not project:
        response = """I couldn't find a project with ID TRN-9999-999 in the database. 

Some suggestions:
- Verify the project ID is correct
- Check if the project might be archived
- Try searching by project name instead

Would you like me to:
1. List all active projects?
2. Search for projects by train model?
3. Show recently completed projects?"""
        
        print(f"🤖 Agent: {response}\n")
    
    # Case 2: Ambiguous query
    print("📝 Case 2: Ambiguous Query\n")
    print("👤 User: What about the welding?\n")
    
    response = """I'd be happy to help with welding information, but I need a bit more context:

- Are you asking about the **Car Body Welding** phase?
- Do you want statistics across all welding phases?
- Are you referring to a specific project?

Could you clarify which aspect you're interested in?"""
    
    print(f"🤖 Agent: {response}\n")
    
    # Case 3: Data quality issues
    print("📝 Case 3: Insufficient Historical Data\n")
    print("👤 User: Build a skeleton for a new Hyperloop-X1 model\n")
    
    response = """I attempted to search for similar Hyperloop-X1 projects, but found:
- 0 completed projects
- 1 project in planning stage
- No historical phase data

⚠️ **Limited Data Warning**: Without historical data, I can only provide:

1. **Generic Phase Template**: Based on train projects in general
2. **Industry Benchmarks**: Average hours per train manufacturing phase
3. **Expert Estimates**: Would need manual input from engineering team

**Recommendation**: For this new model, I suggest:
- Start with engineering department's detailed estimates
- Use similar train model (Metro-3000?) as a rough baseline
- Plan for higher uncertainty margins (30-40% buffer)
- Schedule frequent reviews to update estimates

Would you like me to provide a generic template based on Metro-series projects?"""
    
    print(f"🤖 Agent: {response}\n")
    
    print("="*80)
    print("✅ Error handling demonstrates:")
    print("   - Graceful degradation when data missing")
    print("   - Helpful suggestions for user")
    print("   - Transparency about limitations")
    print("="*80 + "\n")


# ============================================================================
# EXAMPLE 6: Performance Comparison - MCP vs Traditional
# ============================================================================

async def example_performance_comparison():
    """
    Comparison: MCP Architecture vs Traditional Approach
    """
    print("\n" + "="*80)
    print("EXAMPLE 6: Architecture Comparison")
    print("="*80 + "\n")
    
    print("🔧 TRADITIONAL APPROACH (Without MCP):\n")
    print("""
    ┌─────────────┐
    │  LLM Agent  │ ← Directly writes SQL queries
    └──────┬──────┘
           │ "SELECT * FROM projects WHERE..."
           ↓
    ┌──────────────┐
    │   Database   │ ← SQL Injection risk!
    └──────────────┘
    
    Issues:
    ❌ LLM generates raw SQL - security risk
    ❌ Tight coupling between AI and database
    ❌ Hard to change database schema
    ❌ No abstraction layer for business logic
    ❌ Difficult to audit/log queries
    ❌ Can't easily switch LLM providers
    """)
    
    print("\n🚀 MCP APPROACH (Recommended):\n")
    print("""
    ┌─────────────┐
    │  LLM Agent  │ ← Calls semantic tools
    └──────┬──────┘
           │ get_project_overview("TRN-001")
           ↓
    ┌──────────────┐
    │  MCP Server  │ ← Validated, parameterized queries
    │   (Tools)    │ ← Business logic enforcement
    └──────┬───────┘
           │ Parameterized SQL
           ↓
    ┌──────────────┐
    │   Database   │ ← Protected!
    └──────────────┘
    
    Benefits:
    ✅ LLM never sees raw SQL
    ✅ Tools enforce business rules
    ✅ Easy to change implementation
    ✅ Full audit trail of tool usage
    ✅ Provider-agnostic (Azure/Local/Claude)
    ✅ Reusable tools across applications
    ✅ Rate limiting and access control
    """)
    
    print("\n📊 PERFORMANCE METRICS:\n")
    
    metrics = {
        "Security": {
            "Traditional": "⚠️  Medium Risk (SQL injection possible)",
            "MCP": "✅ High Security (parameterized queries only)"
        },
        "Latency": {
            "Traditional": "~800ms (single query)",
            "MCP": "~950ms (tool overhead ~150ms)"
        },
        "Maintainability": {
            "Traditional": "❌ Low (SQL scattered in prompts)",
            "MCP": "✅ High (centralized tool definitions)"
        },
        "Flexibility": {
            "Traditional": "⚠️  Difficult to change DB schema",
            "MCP": "✅ Easy (tools abstract DB structure)"
        },
        "Auditability": {
            "Traditional": "❌ Poor (LLM logs only)",
            "MCP": "✅ Excellent (structured tool logs)"
        },
        "Multi-Provider": {
            "Traditional": "❌ Vendor lock-in",
            "MCP": "✅ Works with any LLM"
        }
    }
    
    for category, comparison in metrics.items():
        print(f"  {category}:")
        print(f"    Traditional: {comparison['Traditional']}")
        print(f"    MCP:         {comparison['MCP']}")
        print()
    
    print("="*80)
    print("💡 RECOMMENDATION: Use MCP for production systems")
    print("="*80 + "\n")


# ============================================================================
# EXAMPLE 7: Real-World Query Patterns
# ============================================================================

async def example_real_world_queries():
    """
    Common real-world queries and how they're handled
    """
    print("\n" + "="*80)
    print("EXAMPLE 7: Real-World Query Patterns")
    print("="*80 + "\n")
    
    queries = [
        {
            "category": "Quick Facts",
            "query": "How many trains in TRN-2024-001?",
            "tools_needed": ["get_project_overview"],
            "complexity": "Low",
            "response_time": "< 1s"
        },
        {
            "category": "Comparative Analysis",
            "query": "Compare TRN-2024-001 with similar past projects",
            "tools_needed": ["get_project_overview", "search_similar_projects"],
            "complexity": "Medium",
            "response_time": "1-2s"
        },
        {
            "category": "Statistical Insights",
            "query": "What's the typical success rate for HVAC installation?",
            "tools_needed": ["get_phase_statistics"],
            "complexity": "Low",
            "response_time": "< 1s"
        },
        {
            "category": "Project Planning",
            "query": "Build skeleton for 12 Metro-3000 trains with custom phases",
            "tools_needed": [
                "search_similar_projects",
                "get_phase_statistics",
                "build_project_skeleton"
            ],
            "complexity": "High",
            "response_time": "3-5s"
        },
        {
            "category": "Resource Planning",
            "query": "What commitments needed for welding phase across all active projects?",
            "tools_needed": [
                "list_active_projects",
                "get_project_phases",
                "get_commitments_summary"
            ],
            "complexity": "Medium-High",
            "response_time": "2-3s"
        },
        {
            "category": "Trend Analysis",
            "query": "Show me how Bogie Assembly duration has changed over the last 3 years",
            "tools_needed": [
                "get_phase_statistics",
                "get_historical_trends"
            ],
            "complexity": "Medium",
            "response_time": "2-3s"
        }
    ]
    
    for i, q in enumerate(queries, 1):
        print(f"{i}. {q['category'].upper()}")
        print(f"   Query: \"{q['query']}\"")
        print(f"   Tools: {' → '.join(q['tools_needed'])}")
        print(f"   Complexity: {q['complexity']}")
        print(f"   Response Time: {q['response_time']}")
        print()
    
    print("="*80)
    print("📈 Query Distribution (typical usage):")
    print("   - Quick Facts: 45%")
    print("   - Comparative Analysis: 25%")
    print("   - Project Planning: 15%")
    print("   - Resource Planning: 10%")
    print("   - Trend Analysis: 5%")
    print("="*80 + "\n")


# ============================================================================
# MAIN DEMO RUNNER
# ============================================================================

async def run_all_examples():
    """Run all examples in sequence"""
    
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "  TRAIN PRODUCTION AI AGENT - COMPLETE DEMO".center(78) + "║")
    print("║" + "  MCP-Based Architecture for Database Interaction".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    
    examples = [
        ("Simple Query", example_simple_query),
        ("Multi-Step Query", example_multi_step_query),
        ("Complex Skeleton Building", example_complex_skeleton_building),
        ("Interactive Conversation", example_interactive_conversation),
        ("Error Handling", example_error_handling),
        ("Performance Comparison", example_performance_comparison),
        ("Real-World Patterns", example_real_world_queries),
    ]
    
    for name, func in examples:
        await func()
        input(f"\n⏸️  Press Enter to continue to next example ({name})...\n")
    
    print("\n" + "="*80)
    print("✅ ALL EXAMPLES COMPLETED!")
    print("="*80)
    print("\n📚 SUMMARY:\n")
    print("This demo showed:")
    print("  1. ✅ Simple information retrieval")
    print("  2. ✅ Multi-step tool orchestration")
    print("  3. ✅ Complex project skeleton generation")
    print("  4. ✅ Contextual conversation handling")
    print("  5. ✅ Graceful error management")
    print("  6. ✅ MCP architecture benefits")
    print("  7. ✅ Real-world query patterns")
    print("\n🚀 Ready to implement in your production environment!")
    print("\nNext steps:")
    print("  1. Set up your PostgreSQL database with the provided schema")
    print("  2. Configure Azure OpenAI or local LLM credentials")
    print("  3. Deploy the MCP server")
    print("  4. Run the client application")
    print("  5. Start querying your train production data!\n")


# ============================================================================
# QUICK START MENU
# ============================================================================

async def quick_start_menu():
    """Interactive menu for running specific examples"""
    
    print("\n╔" + "="*78 + "╗")
    print("║  TRAIN PRODUCTION AI AGENT - DEMO MENU".center(80) + "║")
    print("╚" + "="*78 + "╝\n")
    
    print("Select an example to run:\n")
    print("  1. Simple Query Demo")
    print("  2. Multi-Step Query Demo")
    print("  3. Complex Skeleton Building Demo")
    print("  4. Interactive Conversation Demo")
    print("  5. Error Handling Demo")
    print("  6. Performance Comparison")
    print("  7. Real-World Query Patterns")
    print("  8. Run ALL Examples")
    print("  0. Exit\n")
    
    examples_map = {
        "1": example_simple_query,
        "2": example_multi_step_query,
        "3": example_complex_skeleton_building,
        "4": example_interactive_conversation,
        "5": example_error_handling,
        "6": example_performance_comparison,
        "7": example_real_world_queries,
        "8": run_all_examples,
    }
    
    while True:
        choice = input("Enter your choice (0-8): ").strip()
        
        if choice == "0":
            print("\n👋 Goodbye!\n")
            break
        
        if choice in examples_map:
            await examples_map[choice]()
            input("\n⏸️  Press Enter to return to menu...\n")
        else:
            print("❌ Invalid choice. Please try again.\n")


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "all":
        # Run all examples without interaction
        asyncio.run(run_all_examples())
    else:
        # Interactive menu
        asyncio.run(quick_start_menu())