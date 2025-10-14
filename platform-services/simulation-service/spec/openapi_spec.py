"""
OpenAPI Specification for Simulation Service

Full OpenAPI 3.0 specification for all API endpoints.
"""

from typing import Dict, Any


def get_openapi_schema() -> Dict[str, Any]:
    """
    Get OpenAPI 3.0 specification for Simulation Service

    Returns:
        OpenAPI schema dictionary
    """
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "Simulation Service API",
            "version": "2.0.0",
            "description": "Unified simulation service for BCM exercises, scenario testing, and business impact analysis",
            "contact": {
                "name": "AI Platform Team",
                "email": "platform@example.com"
            }
        },
        "servers": [
            {
                "url": "http://localhost:8095/api/v1",
                "description": "Development server"
            },
            {
                "url": "https://api.example.com/simulation/v1",
                "description": "Production server"
            }
        ],
        "tags": [
            {"name": "health", "description": "Service health and status"},
            {"name": "simulations", "description": "Simulation management"},
            {"name": "scenarios", "description": "BCM scenario management"},
            {"name": "library", "description": "Scenario library browsing"},
            {"name": "executions", "description": "Simulation execution"},
            {"name": "engines", "description": "Simulation engines"}
        ],
        "paths": {
            "/health": {
                "get": {
                    "tags": ["health"],
                    "summary": "Health check",
                    "description": "Check service health and status",
                    "operationId": "health_check",
                    "responses": {
                        "200": {
                            "description": "Service is healthy",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/HealthResponse"}
                                }
                            }
                        }
                    }
                }
            },
            "/simulations": {
                "get": {
                    "tags": ["simulations"],
                    "summary": "List simulations",
                    "description": "Get list of simulations for current tenant",
                    "operationId": "list_simulations",
                    "parameters": [
                        {
                            "name": "simulation_type",
                            "in": "query",
                            "schema": {"type": "string"},
                            "description": "Filter by simulation type"
                        },
                        {
                            "name": "status",
                            "in": "query",
                            "schema": {"type": "string"},
                            "description": "Filter by status"
                        },
                        {
                            "name": "limit",
                            "in": "query",
                            "schema": {"type": "integer", "default": 50},
                            "description": "Maximum number of results"
                        },
                        {
                            "name": "offset",
                            "in": "query",
                            "schema": {"type": "integer", "default": 0},
                            "description": "Offset for pagination"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "List of simulations",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/SimulationResponse"}
                                    }
                                }
                            }
                        }
                    }
                },
                "post": {
                    "tags": ["simulations"],
                    "summary": "Create simulation",
                    "description": "Create a new simulation",
                    "operationId": "create_simulation",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/SimulationCreateRequest"}
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Simulation created",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/SimulationResponse"}
                                }
                            }
                        },
                        "400": {"description": "Invalid request"}
                    }
                }
            },
            "/simulations/{id}": {
                "get": {
                    "tags": ["simulations"],
                    "summary": "Get simulation",
                    "description": "Get simulation details by ID",
                    "operationId": "get_simulation",
                    "parameters": [
                        {
                            "name": "id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"},
                            "description": "Simulation ID"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Simulation details",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/SimulationResponse"}
                                }
                            }
                        },
                        "404": {"description": "Simulation not found"}
                    }
                }
            },
            "/simulations/{id}/execute": {
                "post": {
                    "tags": ["executions"],
                    "summary": "Execute simulation",
                    "description": "Start simulation execution",
                    "operationId": "execute_simulation",
                    "parameters": [
                        {
                            "name": "id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"},
                            "description": "Simulation ID"
                        }
                    ],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/SimulationExecuteRequest"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Execution started",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ExecutionResponse"}
                                }
                            }
                        },
                        "404": {"description": "Simulation not found"},
                        "400": {"description": "Invalid request"}
                    }
                }
            },
            "/scenarios": {
                "get": {
                    "tags": ["scenarios"],
                    "summary": "List scenarios",
                    "description": "Get list of BCM scenarios",
                    "operationId": "list_scenarios",
                    "parameters": [
                        {
                            "name": "category",
                            "in": "query",
                            "schema": {"type": "string"},
                            "description": "Filter by category"
                        },
                        {
                            "name": "complexity",
                            "in": "query",
                            "schema": {"type": "integer"},
                            "description": "Filter by complexity (1-5)"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "List of scenarios",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/ScenarioResponse"}
                                    }
                                }
                            }
                        }
                    }
                },
                "post": {
                    "tags": ["scenarios"],
                    "summary": "Create scenario",
                    "description": "Create a new BCM scenario",
                    "operationId": "create_scenario",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ScenarioCreateRequest"}
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Scenario created",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ScenarioResponse"}
                                }
                            }
                        }
                    }
                }
            },
            "/scenarios/generate": {
                "post": {
                    "tags": ["scenarios"],
                    "summary": "Generate AI scenario",
                    "description": "Generate BCM scenario using AI",
                    "operationId": "generate_scenario",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ScenarioGenerateRequest"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Scenario generated",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ScenarioResponse"}
                                }
                            }
                        }
                    }
                }
            },
            "/library/scenarios": {
                "get": {
                    "tags": ["library"],
                    "summary": "Browse scenario library",
                    "description": "Browse public and tenant-specific scenarios",
                    "operationId": "browse_library",
                    "parameters": [
                        {
                            "name": "category",
                            "in": "query",
                            "schema": {"type": "string"}
                        },
                        {
                            "name": "search",
                            "in": "query",
                            "schema": {"type": "string"},
                            "description": "Search query"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Library scenarios",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/ScenarioResponse"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "HealthResponse": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "example": "healthy"},
                        "version": {"type": "string", "example": "2.0.0"},
                        "engines": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "uptime_seconds": {"type": "number"}
                    }
                },
                "SimulationCreateRequest": {
                    "type": "object",
                    "required": ["name", "simulation_type", "parameters"],
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "simulation_type": {
                            "type": "string",
                            "enum": ["what_if", "monte_carlo", "scenario", "bia", "jaamsim"]
                        },
                        "parameters": {"type": "object"},
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    }
                },
                "SimulationExecuteRequest": {
                    "type": "object",
                    "properties": {
                        "parameters_override": {"type": "object"},
                        "async_execution": {"type": "boolean", "default": False}
                    }
                },
                "ScenarioCreateRequest": {
                    "type": "object",
                    "required": ["title", "category"],
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "category": {
                            "type": "string",
                            "enum": ["cyber", "pandemic", "disaster", "supply_chain"]
                        },
                        "complexity": {"type": "integer", "minimum": 1, "maximum": 5},
                        "content": {"type": "string"}
                    }
                },
                "ScenarioGenerateRequest": {
                    "type": "object",
                    "required": ["category", "complexity"],
                    "properties": {
                        "category": {"type": "string"},
                        "complexity": {"type": "integer", "minimum": 1, "maximum": 5},
                        "industry": {"type": "string"},
                        "organization_size": {"type": "string"}
                    }
                },
                "SimulationResponse": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
                        "simulation_type": {"type": "string"},
                        "status": {"type": "string"},
                        "parameters": {"type": "object"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "updated_at": {"type": "string", "format": "date-time"}
                    }
                },
                "ScenarioResponse": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "title": {"type": "string"},
                        "category": {"type": "string"},
                        "complexity": {"type": "integer"},
                        "is_ai_generated": {"type": "boolean"},
                        "created_at": {"type": "string", "format": "date-time"}
                    }
                },
                "ExecutionResponse": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "simulation_id": {"type": "integer"},
                        "status": {"type": "string"},
                        "progress": {"type": "number"},
                        "started_at": {"type": "string", "format": "date-time"}
                    }
                }
            },
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            }
        },
        "security": [
            {"bearerAuth": []}
        ]
    }
