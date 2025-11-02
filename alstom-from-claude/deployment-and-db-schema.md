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
   - Consider