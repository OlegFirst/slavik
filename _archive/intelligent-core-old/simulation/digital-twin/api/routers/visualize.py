"""
Visualization Endpoints

API endpoints for generating diagrams and charts
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Request, Query

from storage import PostgreSQLStorage, RedisCache

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================
# DEPENDENCIES
# ============================================

def get_storage(request: Request) -> PostgreSQLStorage:
    """Get storage dependency"""
    return request.app.state.app_state.storage


def get_cache(request: Request) -> RedisCache:
    """Get cache dependency"""
    return request.app.state.app_state.cache


# ============================================
# MERMAID DIAGRAMS
# ============================================

@router.get("/{twin_id}/organization-graph")
async def get_organization_graph(
    twin_id: str,
    storage: PostgreSQLStorage = Depends(get_storage)
):
    """
    Get organization structure as Mermaid diagram
    
    Returns interactive diagram code
    """
    try:
        org = await storage.get_organization(twin_id=twin_id)
        
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        # Generate Mermaid diagram
        mermaid = f"""graph TD
    ORG["{org.name}"]
    
    ORG --> TYPE["Type: {org.org_type}"]
    ORG --> IND["Industry: {org.industry or 'N/A'}"]
    ORG --> EMP["Employees: {org.employee_count or 'N/A'}"]
    ORG --> REV["Revenue: ${org.annual_revenue or 0:,.0f}"]
    
    ORG --> HEALTH["Health Score: {org.health_score:.2f}"]
    ORG --> MAT["Maturity: Level {org.maturity_level}"]
    ORG --> QUAL["Quality: {org.quality_score:.2f}"]
    ORG --> RISK["Risk: {org.risk_score:.2f}"]
    
    style ORG fill:#4299e1,stroke:#2c5282,color:#fff
    style HEALTH fill:#48bb78,stroke:#2f855a
    style RISK fill:#f56565,stroke:#c53030
    style MAT fill:#ed8936,stroke:#c05621
    style QUAL fill:#9f7aea,stroke:#6b46c1"""
        
        return {
            'format': 'mermaid',
            'diagram': mermaid,
            'organization': org.name,
            'twin_id': twin_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate organization graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{twin_id}/simulation-flow")
async def get_simulation_flow(
    twin_id: str,
    storage: PostgreSQLStorage = Depends(get_storage)
):
    """
    Get simulation flow diagram
    
    Shows simulation scenarios and their impact
    """
    try:
        org = await storage.get_organization(twin_id=twin_id)
        
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        # Get simulations
        simulations = await storage.list_simulations(twin_id=twin_id, limit=10)
        
        # Build flow diagram
        mermaid = f"""graph LR
    ORG["{org.name}<br/>Digital Twin"]
    
"""
        
        if simulations:
            for idx, sim in enumerate(simulations):
                status_color = {
                    'completed': '#48bb78',
                    'failed': '#f56565',
                    'running': '#ed8936',
                    'pending': '#cbd5e0'
                }.get(sim.status, '#cbd5e0')
                
                impact = sim.impact_score or 0
                impact_label = 'High' if impact > 0.7 else 'Medium' if impact > 0.4 else 'Low'
                
                sim_node = f"""SIM{idx}["Scenario: {sim.scenario}<br/>Impact: {impact_label} ({impact:.2f})<br/>Status: {sim.status}"]"""
                
                mermaid += f"    ORG --> {sim_node}\n"
                mermaid += f"    style SIM{idx} fill:{status_color}\n"
        else:
            mermaid += "    ORG --> NOSIM[No simulations yet]\n"
        
        mermaid += "\n    style ORG fill:#4299e1,stroke:#2c5282,color:#fff"
        
        return {
            'format': 'mermaid',
            'diagram': mermaid,
            'simulations_count': len(simulations)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate simulation flow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{twin_id}/risk-heatmap")
async def get_risk_heatmap(
    twin_id: str,
    storage: PostgreSQLStorage = Depends(get_storage)
):
    """
    Get risk analysis heatmap data
    
    Returns data for risk visualization
    """
    try:
        org = await storage.get_organization(twin_id=twin_id)
        
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        # Get all completed simulations
        simulations = await storage.list_simulations(
            twin_id=twin_id,
            status='completed',
            limit=100
        )
        
        # Build heatmap data
        scenarios = {}
        
        for sim in simulations:
            if sim.scenario not in scenarios:
                scenarios[sim.scenario] = {
                    'count': 0,
                    'avg_impact': 0,
                    'avg_financial': 0,
                    'avg_operational': 0,
                    'avg_recovery_days': 0,
                    'simulations': []
                }
            
            entry = scenarios[sim.scenario]
            entry['count'] += 1
            entry['avg_impact'] += sim.impact_score or 0
            entry['avg_financial'] += sim.financial_impact or 0
            entry['avg_operational'] += sim.operational_impact or 0
            entry['avg_recovery_days'] += sim.recovery_time_days or 0
            
            entry['simulations'].append({
                'id': sim.id,
                'impact': sim.impact_score,
                'created_at': sim.created_at.isoformat()
            })
        
        # Calculate averages
        for scenario, data in scenarios.items():
            count = data['count']
            data['avg_impact'] = data['avg_impact'] / count if count > 0 else 0
            data['avg_financial'] = data['avg_financial'] / count if count > 0 else 0
            data['avg_operational'] = data['avg_operational'] / count if count > 0 else 0
            data['avg_recovery_days'] = data['avg_recovery_days'] / count if count > 0 else 0
            
            # Determine risk level
            if data['avg_impact'] > 0.7:
                data['risk_level'] = 'high'
            elif data['avg_impact'] > 0.4:
                data['risk_level'] = 'medium'
            else:
                data['risk_level'] = 'low'
        
        return {
            'organization': org.name,
            'twin_id': twin_id,
            'overall_risk': org.risk_score,
            'scenarios': scenarios,
            'total_simulations': len(simulations)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate risk heatmap: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# METRICS CHARTS (Plotly compatible)
# ============================================

@router.get("/{twin_id}/health-trend")
async def get_health_trend(
    twin_id: str,
    limit: int = Query(30, ge=1, le=365),
    storage: PostgreSQLStorage = Depends(get_storage)
):
    """
    Get health score trend over time
    
    Returns Plotly-compatible data
    """
    try:
        # Get health scores
        health_scores = await storage.get_health_scores(twin_id, limit=limit)
        
        if not health_scores:
            return {
                'format': 'plotly',
                'data': [],
                'message': 'No health score history'
            }
        
        # Prepare Plotly data
        x_values = [h.calculated_at.isoformat() for h in health_scores]
        
        traces = [
            {
                'x': x_values,
                'y': [h.overall for h in health_scores],
                'type': 'scatter',
                'mode': 'lines+markers',
                'name': 'Overall Health',
                'line': {'color': '#4299e1'}
            },
            {
                'x': x_values,
                'y': [h.financial for h in health_scores],
                'type': 'scatter',
                'mode': 'lines',
                'name': 'Financial',
                'line': {'color': '#48bb78', 'dash': 'dot'}
            },
            {
                'x': x_values,
                'y': [h.operational for h in health_scores],
                'type': 'scatter',
                'mode': 'lines',
                'name': 'Operational',
                'line': {'color': '#ed8936', 'dash': 'dot'}
            },
            {
                'x': x_values,
                'y': [h.impact for h in health_scores],
                'type': 'scatter',
                'mode': 'lines',
                'name': 'Impact',
                'line': {'color': '#9f7aea', 'dash': 'dot'}
            }
        ]
        
        layout = {
            'title': f'Health Score Trend',
            'xaxis': {'title': 'Date'},
            'yaxis': {'title': 'Score', 'range': [0, 1]},
            'hovermode': 'x unified'
        }
        
        return {
            'format': 'plotly',
            'data': traces,
            'layout': layout
        }
        
    except Exception as e:
        logger.error(f"Failed to generate health trend: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{twin_id}/simulation-impact")
async def get_simulation_impact_chart(
    twin_id: str,
    storage: PostgreSQLStorage = Depends(get_storage)
):
    """
    Get simulation impact comparison chart
    
    Returns bar chart data
    """
    try:
        # Get completed simulations
        simulations = await storage.list_simulations(
            twin_id=twin_id,
            status='completed',
            limit=50
        )
        
        if not simulations:
            return {
                'format': 'plotly',
                'data': [],
                'message': 'No completed simulations'
            }
        
        # Group by scenario
        scenarios = {}
        for sim in simulations:
            if sim.scenario not in scenarios:
                scenarios[sim.scenario] = {
                    'impact': [],
                    'financial': [],
                    'operational': []
                }
            
            scenarios[sim.scenario]['impact'].append(sim.impact_score or 0)
            scenarios[sim.scenario]['financial'].append(sim.financial_impact or 0)
            scenarios[sim.scenario]['operational'].append(sim.operational_impact or 0)
        
        # Calculate averages
        scenario_names = []
        avg_impact = []
        avg_financial = []
        avg_operational = []
        
        for scenario, values in scenarios.items():
            scenario_names.append(scenario)
            avg_impact.append(sum(values['impact']) / len(values['impact']))
            avg_financial.append(sum(values['financial']) / len(values['financial']))
            avg_operational.append(sum(values['operational']) / len(values['operational']))
        
        # Plotly bar chart
        traces = [
            {
                'x': scenario_names,
                'y': avg_impact,
                'type': 'bar',
                'name': 'Overall Impact',
                'marker': {'color': '#4299e1'}
            },
            {
                'x': scenario_names,
                'y': avg_financial,
                'type': 'bar',
                'name': 'Financial Impact',
                'marker': {'color': '#48bb78'}
            },
            {
                'x': scenario_names,
                'y': avg_operational,
                'type': 'bar',
                'name': 'Operational Impact',
                'marker': {'color': '#ed8936'}
            }
        ]
        
        layout = {
            'title': 'Average Impact by Scenario',
            'xaxis': {'title': 'Scenario'},
            'yaxis': {'title': 'Impact Score', 'range': [0, 1]},
            'barmode': 'group'
        }
        
        return {
            'format': 'plotly',
            'data': traces,
            'layout': layout
        }
        
    except Exception as e:
        logger.error(f"Failed to generate impact chart: {e}")
        raise HTTPException(status_code=500, detail=str(e))
