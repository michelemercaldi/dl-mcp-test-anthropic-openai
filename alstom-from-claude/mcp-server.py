"""
Train Production MCP Server
A Model Context Protocol server for train manufacturing database interactions
"""

from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio
from typing import Any, Sequence
import json
import psycopg2  # or your database driver
from dataclasses import dataclass
from datetime import datetime

# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class ProductionPhase:
    phase_id: str
    phase_name: str
    sequence_order: int
    estimated_hours: float
    department: str
    dependencies: list[str]

@dataclass
class Project:
    project_id: str
    project_name: str
    train_model: str
    num_trains: int
    start_date: datetime
    phases: list[ProductionPhase]

# ============================================================================
# DATABASE CONNECTION (Your actual implementation)
# ============================================================================

class DatabaseConnection:
    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
    
    def execute_query(self, query: str, params: tuple) -> list[dict]:
        """Execute parameterized query safely"""
        with self.conn.cursor() as cursor:
            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

# ============================================================================
# MCP SERVER IMPLEMENTATION
# ============================================================================

class TrainProductionServer:
    def __init__(self, db_connection_string: str):
        self.db = DatabaseConnection(db_connection_string)
        self.server = Server("train-production-server")
        self._register_tools()
    
    def _register_tools(self):
        """Register all available tools"""
        
        # Tool 1: Get Project Overview
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            return [
                Tool(
                    name="get_project_overview",
                    description="Get basic information about a project including phase count, train count, and commitments",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "string",
                                "description": "The unique project identifier"
                            }
                        },
                        "required": ["project_id"]
                    }
                ),
                Tool(
                    name="get_project_phases",
                    description="Retrieve all production phases for a specific project with details",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "string",
                                "description": "The unique project identifier"
                            },
                            "include_dependencies": {
                                "type": "boolean",
                                "description": "Include phase dependencies",
                                "default": True
                            }
                        },
                        "required": ["project_id"]
                    }
                ),
                Tool(
                    name="search_similar_projects",
                    description="Find similar past projects based on phase patterns, train models, or characteristics",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "phase_subset": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of phase names or IDs to match against"
                            },
                            "train_model": {
                                "type": "string",
                                "description": "Train model to filter by (optional)"
                            },
                            "min_similarity_score": {
                                "type": "number",
                                "description": "Minimum similarity threshold (0-1)",
                                "default": 0.7
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results",
                                "default": 10
                            }
                        },
                        "required": ["phase_subset"]
                    }
                ),
                Tool(
                    name="get_phase_statistics",
                    description="Get statistical data for specific phases across multiple projects",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "phase_names": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Phase names to analyze"
                            },
                            "metrics": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": ["avg_duration", "avg_cost", "success_rate", "common_issues"]
                                },
                                "description": "Metrics to retrieve"
                            }
                        },
                        "required": ["phase_names"]
                    }
                ),
                Tool(
                    name="build_project_skeleton",
                    description="Create a prefilled project skeleton based on similar past projects",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "base_phases": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Initial phase list from engineering"
                            },
                            "train_model": {
                                "type": "string",
                                "description": "Target train model"
                            },
                            "num_trains": {
                                "type": "integer",
                                "description": "Number of trains to produce"
                            },
                            "reference_project_ids": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Optional: specific projects to use as reference"
                            }
                        },
                        "required": ["base_phases", "train_model", "num_trains"]
                    }
                ),
                Tool(
                    name="get_commitments_summary",
                    description="Get summary of commitments (resources, materials, personnel) for a project",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "string",
                                "description": "The unique project identifier"
                            },
                            "commitment_type": {
                                "type": "string",
                                "enum": ["all", "personnel", "materials", "equipment"],
                                "description": "Type of commitments to retrieve",
                                "default": "all"
                            }
                        },
                        "required": ["project_id"]
                    }
                )
            ]
        
        # Tool Handlers
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
            if name == "get_project_overview":
                return await self.get_project_overview(arguments)
            elif name == "get_project_phases":
                return await self.get_project_phases(arguments)
            elif name == "search_similar_projects":
                return await self.search_similar_projects(arguments)
            elif name == "get_phase_statistics":
                return await self.get_phase_statistics(arguments)
            elif name == "build_project_skeleton":
                return await self.build_project_skeleton(arguments)
            elif name == "get_commitments_summary":
                return await self.get_commitments_summary(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
    
    # ========================================================================
    # TOOL IMPLEMENTATIONS
    # ========================================================================
    
    async def get_project_overview(self, args: dict) -> Sequence[TextContent]:
        """Get basic project information"""
        project_id = args["project_id"]
        
        # Parameterized query - SAFE from SQL injection
        query = """
            SELECT 
                p.project_id,
                p.project_name,
                p.train_model,
                p.num_trains,
                COUNT(DISTINCT pp.phase_id) as total_phases,
                COUNT(DISTINCT pc.commitment_id) as total_commitments,
                p.start_date,
                p.expected_completion_date,
                p.status
            FROM projects p
            LEFT JOIN project_phases pp ON p.project_id = pp.project_id
            LEFT JOIN project_commitments pc ON p.project_id = pc.project_id
            WHERE p.project_id = %s
            GROUP BY p.project_id
        """
        
        results = self.db.execute_query(query, (project_id,))
        
        if not results:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Project {project_id} not found"})
            )]
        
        return [TextContent(
            type="text",
            text=json.dumps(results[0], default=str, indent=2)
        )]
    
    async def get_project_phases(self, args: dict) -> Sequence[TextContent]:
        """Get detailed phase information"""
        project_id = args["project_id"]
        include_deps = args.get("include_dependencies", True)
        
        query = """
            SELECT 
                pp.phase_id,
                pp.phase_name,
                pp.sequence_order,
                pp.estimated_hours,
                pp.actual_hours,
                pp.department,
                pp.status,
                pd.phase_description,
                pd.required_skills
            FROM project_phases pp
            LEFT JOIN phase_details pd ON pp.phase_id = pd.phase_id
            WHERE pp.project_id = %s
            ORDER BY pp.sequence_order
        """
        
        phases = self.db.execute_query(query, (project_id,))
        
        if include_deps:
            # Get dependencies for each phase
            for phase in phases:
                dep_query = """
                    SELECT dependency_phase_id, dependency_type
                    FROM phase_dependencies
                    WHERE phase_id = %s
                """
                phase["dependencies"] = self.db.execute_query(
                    dep_query, 
                    (phase["phase_id"],)
                )
        
        return [TextContent(
            type="text",
            text=json.dumps({
                "project_id": project_id,
                "total_phases": len(phases),
                "phases": phases
            }, default=str, indent=2)
        )]
    
    async def search_similar_projects(self, args: dict) -> Sequence[TextContent]:
        """Find similar projects based on phase patterns"""
        phase_subset = args["phase_subset"]
        train_model = args.get("train_model")
        min_similarity = args.get("min_similarity_score", 0.7)
        limit = args.get("limit", 10)
        
        # Use PostgreSQL's similarity functions or custom logic
        # This is a simplified version - you'd implement Jaccard similarity or cosine similarity
        query = """
            WITH input_phases AS (
                SELECT unnest(%s::text[]) as phase_name
            ),
            project_phase_matches AS (
                SELECT 
                    p.project_id,
                    p.project_name,
                    p.train_model,
                    p.num_trains,
                    p.completion_date,
                    COUNT(DISTINCT pp.phase_id) as matching_phases,
                    array_agg(DISTINCT pp.phase_name) as project_phases,
                    -- Jaccard similarity: intersection / union
                    COUNT(DISTINCT pp.phase_id)::float / 
                    (SELECT COUNT(*) FROM input_phases)::float as similarity_score
                FROM projects p
                JOIN project_phases pp ON p.project_id = pp.project_id
                WHERE pp.phase_name = ANY(%s::text[])
                    AND p.status = 'completed'
                    AND (%s IS NULL OR p.train_model = %s)
                GROUP BY p.project_id
                HAVING COUNT(DISTINCT pp.phase_id)::float / 
                       (SELECT COUNT(*) FROM input_phases)::float >= %s
            )
            SELECT * FROM project_phase_matches
            ORDER BY similarity_score DESC, completion_date DESC
            LIMIT %s
        """
        
        results = self.db.execute_query(
            query, 
            (phase_subset, phase_subset, train_model, train_model, min_similarity, limit)
        )
        
        return [TextContent(
            type="text",
            text=json.dumps({
                "query_phases": phase_subset,
                "similar_projects_found": len(results),
                "projects": results
            }, default=str, indent=2)
        )]
    
    async def get_phase_statistics(self, args: dict) -> Sequence[TextContent]:
        """Get statistical analysis of phases"""
        phase_names = args["phase_names"]
        metrics = args.get("metrics", ["avg_duration", "avg_cost"])
        
        stats = {}
        
        for phase_name in phase_names:
            query = """
                SELECT 
                    phase_name,
                    COUNT(*) as occurrences,
                    AVG(actual_hours) as avg_duration_hours,
                    STDDEV(actual_hours) as stddev_duration,
                    AVG(actual_cost) as avg_cost,
                    STDDEV(actual_cost) as stddev_cost,
                    AVG(CASE WHEN status = 'completed_on_time' THEN 1 ELSE 0 END) as success_rate,
                    array_agg(DISTINCT issue_type) FILTER (WHERE issue_type IS NOT NULL) as common_issues
                FROM project_phases pp
                LEFT JOIN phase_issues pi ON pp.phase_id = pi.phase_id
                WHERE phase_name = %s
                    AND pp.status IN ('completed', 'completed_on_time', 'completed_delayed')
                GROUP BY phase_name
            """
            
            result = self.db.execute_query(query, (phase_name,))
            if result:
                stats[phase_name] = result[0]
        
        return [TextContent(
            type="text",
            text=json.dumps({
                "statistics": stats,
                "requested_metrics": metrics
            }, default=str, indent=2)
        )]
    
    async def build_project_skeleton(self, args: dict) -> Sequence[TextContent]:
        """Build prefilled project skeleton from historical data"""
        base_phases = args["base_phases"]
        train_model = args["train_model"]
        num_trains = args["num_trains"]
        reference_projects = args.get("reference_project_ids", [])
        
        # Step 1: Find similar projects
        similar_projects_args = {
            "phase_subset": base_phases,
            "train_model": train_model,
            "min_similarity_score": 0.6,
            "limit": 5
        }
        
        if reference_projects:
            # Use specific reference projects
            query = """
                SELECT DISTINCT pp.phase_name, 
                       AVG(pp.estimated_hours) as avg_estimated_hours,
                       AVG(pp.actual_hours) as avg_actual_hours,
                       mode() WITHIN GROUP (ORDER BY pp.department) as typical_department,
                       array_agg(DISTINCT pd.dependency_phase_id) as typical_dependencies
                FROM project_phases pp
                LEFT JOIN phase_dependencies pd ON pp.phase_id = pd.phase_id
                WHERE pp.project_id = ANY(%s::text[])
                    AND pp.phase_name = ANY(%s::text[])
                GROUP BY pp.phase_name
            """
            historical_data = self.db.execute_query(
                query, 
                (reference_projects, base_phases)
            )
        else:
            # Auto-find similar projects
            query = """
                WITH similar_projects AS (
                    SELECT p.project_id
                    FROM projects p
                    JOIN project_phases pp ON p.project_id = pp.project_id
                    WHERE p.train_model = %s
                        AND pp.phase_name = ANY(%s::text[])
                        AND p.status = 'completed'
                    GROUP BY p.project_id
                    ORDER BY COUNT(DISTINCT pp.phase_id) DESC
                    LIMIT 5
                )
                SELECT 
                    pp.phase_name,
                    AVG(pp.estimated_hours * p.num_trains / %s) as scaled_estimated_hours,
                    AVG(pp.actual_hours * p.num_trains / %s) as scaled_actual_hours,
                    mode() WITHIN GROUP (ORDER BY pp.department) as typical_department,
                    mode() WITHIN GROUP (ORDER BY pp.sequence_order) as typical_sequence,
                    json_agg(DISTINCT jsonb_build_object(
                        'project_id', p.project_id,
                        'hours', pp.actual_hours
                    )) as source_data
                FROM similar_projects sp
                JOIN project_phases pp ON sp.project_id = pp.project_id
                JOIN projects p ON sp.project_id = p.project_id
                WHERE pp.phase_name = ANY(%s::text[])
                GROUP BY pp.phase_name
            """
            historical_data = self.db.execute_query(
                query,
                (train_model, base_phases, num_trains, num_trains, base_phases)
            )
        
        # Build skeleton
        skeleton = {
            "train_model": train_model,
            "num_trains": num_trains,
            "estimated_phases": len(base_phases),
            "prefilled_phases": []
        }
        
        for phase_data in historical_data:
            skeleton["prefilled_phases"].append({
                "phase_name": phase_data["phase_name"],
                "estimated_hours": phase_data.get("scaled_estimated_hours") or phase_data.get("avg_estimated_hours"),
                "department": phase_data["typical_department"],
                "sequence_order": phase_data.get("typical_sequence"),
                "confidence_level": "high" if len(phase_data.get("source_data", [])) > 2 else "medium",
                "based_on_projects": phase_data.get("source_data", [])
            })
        
        return [TextContent(
            type="text",
            text=json.dumps(skeleton, default=str, indent=2)
        )]
    
    async def get_commitments_summary(self, args: dict) -> Sequence[TextContent]:
        """Get commitments summary"""
        project_id = args["project_id"]
        commitment_type = args.get("commitment_type", "all")
        
        type_filter = "" if commitment_type == "all" else "AND commitment_type = %s"
        params = (project_id, commitment_type) if commitment_type != "all" else (project_id,)
        
        query = f"""
            SELECT 
                commitment_type,
                COUNT(*) as total_commitments,
                SUM(quantity) as total_quantity,
                SUM(estimated_cost) as total_estimated_cost,
                json_agg(json_build_object(
                    'resource_name', resource_name,
                    'quantity', quantity,
                    'unit', unit,
                    'status', status
                )) as details
            FROM project_commitments
            WHERE project_id = %s
                {type_filter}
            GROUP BY commitment_type
        """
        
        results = self.db.execute_query(query, params)
        
        return [TextContent(
            type="text",
            text=json.dumps({
                "project_id": project_id,
                "commitment_type_filter": commitment_type,
                "summary": results
            }, default=str, indent=2)
        )]
    
    async def run(self):
        """Run the MCP server"""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import asyncio
    
    # Configuration (use environment variables in production)
    DB_CONNECTION = "postgresql://user:password@localhost:5432/train_production"
    
    server = TrainProductionServer(DB_CONNECTION)
    asyncio.run(server.run())