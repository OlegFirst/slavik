#!/usr/bin/env python3
"""
Diagram Generator - Mermaid.js integration for architecture visualization
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class DiagramGenerator:
    """Generates architecture diagrams using Mermaid.js"""

    def __init__(self):
        self.mermaid_themes = {
            "default": "default",
            "dark": "dark",
            "forest": "forest",
            "neutral": "neutral"
        }

    async def generate(self, architecture: Dict[str, Any]) -> str:
        """Generate architecture diagram"""
        try:
            logger.info("Starting diagram generation")

            pattern = architecture.get("primary_pattern", "monolith")
            components = architecture.get("recommended_components", [])

            if pattern == "monolith":
                diagram = self._generate_monolith_diagram(architecture)
            elif pattern == "microservices":
                diagram = self._generate_microservices_diagram(architecture)
            elif pattern == "serverless":
                diagram = self._generate_serverless_diagram(architecture)
            else:
                diagram = self._generate_hybrid_diagram(architecture)

            # Wrap in HTML for rendering
            html_diagram = self._wrap_in_html(diagram)

            logger.info("Diagram generation completed")
            return html_diagram

        except Exception as e:
            logger.error(f"Diagram generation failed: {e}")
            return self._generate_error_diagram(str(e))

    def _generate_monolith_diagram(self, architecture: Dict[str, Any]) -> str:
        """Generate monolith architecture diagram"""
        components = architecture.get("recommended_components", [])

        mermaid = """graph TD
    %% Monolithic Architecture
    subgraph "Monolithic Application"
        A[Web Interface] --> B[Application Layer]
        B --> C[Business Logic]
        C --> D[Data Access Layer]
        D --> E[(Database)]
    end

    %% External interactions
    F[Users] --> A
    G[Admin Panel] --> A

    %% Additional components
"""

        # Add dynamic components
        for i, component in enumerate(components):
            comp_id = f"COMP{i+1}"
            mermaid += f"    {comp_id}[{component}] --> B\n"

        mermaid += """
    %% Styling
    classDef primary fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef secondary fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef database fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px

    class A,B,C primary
    class F,G secondary
    class E database
"""

        return mermaid

    def _generate_microservices_diagram(self, architecture: Dict[str, Any]) -> str:
        """Generate microservices architecture diagram"""
        components = architecture.get("recommended_components", [])

        mermaid = """graph TD
    %% Microservices Architecture
    subgraph "Client Layer"
        UI[Web App]
        MOB[Mobile App]
    end

    subgraph "API Gateway Layer"
        GW[API Gateway]
        LB[Load Balancer]
    end

    subgraph "Microservices"
        US[User Service]
        OS[Order Service]
        PS[Product Service]
        NS[Notification Service]
    end

    subgraph "Data Layer"
        DB1[(User DB)]
        DB2[(Order DB)]
        DB3[(Product DB)]
        CACHE[(Redis Cache)]
    end

    subgraph "Infrastructure"
        MON[Monitoring]
        LOG[Logging]
        CONFIG[Config Service]
    end

    %% Connections
    UI --> LB
    MOB --> LB
    LB --> GW

    GW --> US
    GW --> OS
    GW --> PS
    GW --> NS

    US --> DB1
    OS --> DB2
    PS --> DB3

    US --> CACHE
    OS --> CACHE
    PS --> CACHE

    US --> CONFIG
    OS --> CONFIG
    PS --> CONFIG
    NS --> CONFIG

    US --> MON
    OS --> MON
    PS --> MON
    NS --> MON

    US --> LOG
    OS --> LOG
    PS --> LOG
    NS --> LOG

    %% Service-to-service communication
    OS -.-> US
    OS -.-> PS
    NS -.-> US
    NS -.-> OS

    %% Styling
    classDef client fill:#e3f2fd,stroke:#0277bd,stroke-width:2px
    classDef gateway fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef service fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef database fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef infra fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px

    class UI,MOB client
    class GW,LB gateway
    class US,OS,PS,NS service
    class DB1,DB2,DB3,CACHE database
    class MON,LOG,CONFIG infra
"""

        return mermaid

    def _generate_serverless_diagram(self, architecture: Dict[str, Any]) -> str:
        """Generate serverless architecture diagram"""

        mermaid = """graph TD
    %% Serverless Architecture
    subgraph "Client"
        WEB[Web App]
        MOB[Mobile App]
    end

    subgraph "CDN & Static"
        CDN[CloudFront CDN]
        S3[S3 Static Assets]
    end

    subgraph "API Layer"
        APIGW[API Gateway]
    end

    subgraph "Serverless Functions"
        AUTH[Auth Lambda]
        USER[User Lambda]
        ORDER[Order Lambda]
        NOTIFY[Notification Lambda]
    end

    subgraph "Data & Storage"
        DYNAMO[(DynamoDB)]
        RDS[(RDS)]
        S3DATA[(S3 Data)]
    end

    subgraph "Event & Messaging"
        SQS[SQS Queue]
        SNS[SNS Topics]
        EVENT[EventBridge]
    end

    subgraph "Monitoring"
        CW[CloudWatch]
        XRAY[X-Ray Tracing]
    end

    %% Connections
    WEB --> CDN
    MOB --> APIGW
    CDN --> S3
    CDN --> APIGW

    APIGW --> AUTH
    APIGW --> USER
    APIGW --> ORDER

    AUTH --> DYNAMO
    USER --> RDS
    ORDER --> DYNAMO
    ORDER --> SQS

    SQS --> NOTIFY
    NOTIFY --> SNS

    EVENT --> NOTIFY

    USER --> S3DATA
    ORDER --> S3DATA

    AUTH --> CW
    USER --> CW
    ORDER --> CW
    NOTIFY --> CW

    AUTH --> XRAY
    USER --> XRAY
    ORDER --> XRAY

    %% Styling
    classDef client fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef cdn fill:#fff8e1,stroke:#f57c00,stroke-width:2px
    classDef gateway fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef lambda fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef database fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef messaging fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef monitoring fill:#e0f2f1,stroke:#00695c,stroke-width:2px

    class WEB,MOB client
    class CDN,S3 cdn
    class APIGW gateway
    class AUTH,USER,ORDER,NOTIFY lambda
    class DYNAMO,RDS,S3DATA database
    class SQS,SNS,EVENT messaging
    class CW,XRAY monitoring
"""

        return mermaid

    def _generate_hybrid_diagram(self, architecture: Dict[str, Any]) -> str:
        """Generate hybrid architecture diagram"""

        mermaid = """graph TD
    %% Hybrid Architecture
    subgraph "Frontend"
        UI[React App]
        ADMIN[Admin Panel]
    end

    subgraph "Core Monolith"
        CORE[Core Application]
        AUTH[Authentication]
        USER[User Management]
    end

    subgraph "Microservices"
        PAY[Payment Service]
        NOTIFY[Notification Service]
        REPORT[Reporting Service]
    end

    subgraph "Serverless Functions"
        LAMBDA1[Image Processing]
        LAMBDA2[Email Service]
        LAMBDA3[Analytics]
    end

    subgraph "Data Layer"
        MAIN_DB[(Main Database)]
        PAY_DB[(Payment DB)]
        CACHE[(Redis)]
        S3[(S3 Storage)]
    end

    subgraph "Infrastructure"
        GW[API Gateway]
        LB[Load Balancer]
        MON[Monitoring]
    end

    %% Connections
    UI --> LB
    ADMIN --> LB
    LB --> GW

    GW --> CORE
    GW --> PAY
    GW --> NOTIFY
    GW --> REPORT

    CORE --> AUTH
    CORE --> USER
    CORE --> MAIN_DB
    CORE --> CACHE

    PAY --> PAY_DB
    NOTIFY --> LAMBDA2
    REPORT --> LAMBDA3

    LAMBDA1 --> S3
    LAMBDA2 --> S3
    LAMBDA3 --> MAIN_DB

    CORE --> MON
    PAY --> MON
    NOTIFY --> MON
    REPORT --> MON

    %% Event flows
    CORE -.-> PAY
    PAY -.-> NOTIFY
    USER -.-> LAMBDA1

    %% Styling
    classDef frontend fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef monolith fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef microservice fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef serverless fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef database fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef infra fill:#e0f2f1,stroke:#00695c,stroke-width:2px

    class UI,ADMIN frontend
    class CORE,AUTH,USER monolith
    class PAY,NOTIFY,REPORT microservice
    class LAMBDA1,LAMBDA2,LAMBDA3 serverless
    class MAIN_DB,PAY_DB,CACHE,S3 database
    class GW,LB,MON infra
"""

        return mermaid

    def _wrap_in_html(self, mermaid_code: str) -> str:
        """Wrap Mermaid code in HTML for rendering"""

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Architecture Diagram</title>
    <script src="https://unpkg.com/mermaid@10.6.1/dist/mermaid.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 30px;
            text-align: center;
        }}

        .header h1 {{
            margin: 0;
            font-size: 2.5rem;
            font-weight: 300;
        }}

        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.1rem;
        }}

        .diagram-container {{
            padding: 40px;
            text-align: center;
            background: #fafafa;
        }}

        .mermaid {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.05);
            margin: 20px auto;
            max-width: 100%;
            overflow-x: auto;
        }}

        .controls {{
            margin: 20px 0;
            text-align: center;
        }}

        .btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            margin: 0 10px;
            font-size: 14px;
            transition: all 0.3s ease;
        }}

        .btn:hover {{
            background: #5a67d8;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}

        .legend {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            text-align: left;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        }}

        .legend h3 {{
            color: #333;
            margin-top: 0;
        }}

        .legend-item {{
            display: inline-block;
            margin: 5px 15px;
            font-size: 14px;
        }}

        .legend-color {{
            display: inline-block;
            width: 16px;
            height: 16px;
            border-radius: 3px;
            margin-right: 8px;
            vertical-align: middle;
        }}

        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 2rem;
            }}
            .diagram-container {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏗️ Architecture Diagram</h1>
            <p>Generated by Universal Orchestration Platform</p>
        </div>

        <div class="diagram-container">
            <div class="controls">
                <button class="btn" onclick="downloadSVG()">📥 Download SVG</button>
                <button class="btn" onclick="downloadPNG()">🖼️ Download PNG</button>
                <button class="btn" onclick="toggleTheme()">🎨 Toggle Theme</button>
            </div>

            <div class="mermaid" id="diagram">
{mermaid_code}
            </div>

            <div class="legend">
                <h3>🎨 Legend</h3>
                <div class="legend-item">
                    <span class="legend-color" style="background: #e3f2fd;"></span>
                    Client Layer
                </div>
                <div class="legend-item">
                    <span class="legend-color" style="background: #e8f5e8;"></span>
                    Services
                </div>
                <div class="legend-item">
                    <span class="legend-color" style="background: #fce4ec;"></span>
                    Data Layer
                </div>
                <div class="legend-item">
                    <span class="legend-color" style="background: #f3e5f5;"></span>
                    Infrastructure
                </div>
            </div>
        </div>
    </div>

    <script>
        // Initialize Mermaid
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'default',
            flowchart: {{
                useMaxWidth: true,
                htmlLabels: true,
                curve: 'cardinal'
            }},
            securityLevel: 'loose'
        }});

        // Download SVG
        function downloadSVG() {{
            const svg = document.querySelector('.mermaid svg');
            if (svg) {{
                const svgData = new XMLSerializer().serializeToString(svg);
                const svgBlob = new Blob([svgData], {{type: 'image/svg+xml;charset=utf-8'}});
                const svgUrl = URL.createObjectURL(svgBlob);
                const downloadLink = document.createElement('a');
                downloadLink.href = svgUrl;
                downloadLink.download = 'architecture-diagram.svg';
                document.body.appendChild(downloadLink);
                downloadLink.click();
                document.body.removeChild(downloadLink);
            }}
        }}

        // Download PNG
        function downloadPNG() {{
            const svg = document.querySelector('.mermaid svg');
            if (svg) {{
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                const img = new Image();

                const svgData = new XMLSerializer().serializeToString(svg);
                const svgBlob = new Blob([svgData], {{type: 'image/svg+xml;charset=utf-8'}});
                const url = URL.createObjectURL(svgBlob);

                img.onload = function() {{
                    canvas.width = img.width;
                    canvas.height = img.height;
                    ctx.drawImage(img, 0, 0);

                    canvas.toBlob(function(blob) {{
                        const url = URL.createObjectURL(blob);
                        const downloadLink = document.createElement('a');
                        downloadLink.href = url;
                        downloadLink.download = 'architecture-diagram.png';
                        document.body.appendChild(downloadLink);
                        downloadLink.click();
                        document.body.removeChild(downloadLink);
                    }});
                }};

                img.src = url;
            }}
        }}

        // Toggle theme
        let currentTheme = 'default';
        function toggleTheme() {{
            currentTheme = currentTheme === 'default' ? 'dark' : 'default';
            mermaid.initialize({{
                startOnLoad: true,
                theme: currentTheme,
                flowchart: {{
                    useMaxWidth: true,
                    htmlLabels: true,
                    curve: 'cardinal'
                }}
            }});

            // Re-render the diagram
            const diagramDiv = document.getElementById('diagram');
            const mermaidCode = `{mermaid_code}`;
            diagramDiv.innerHTML = mermaidCode;
            mermaid.init(undefined, diagramDiv);
        }}
    </script>
</body>
</html>
"""
        return html

    def _generate_error_diagram(self, error_message: str) -> str:
        """Generate error diagram when generation fails"""

        error_mermaid = f"""graph TD
    A[❌ Diagram Generation Failed] --> B[Error: {error_message[:50]}...]
    B --> C[Please check your architecture data]

    classDef error fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    class A,B,C error
"""

        return self._wrap_in_html(error_mermaid)

    def generate_c4_diagram(self, architecture: Dict[str, Any], level: str = "context") -> str:
        """Generate C4 model diagrams"""

        if level == "context":
            return self._generate_c4_context(architecture)
        elif level == "container":
            return self._generate_c4_container(architecture)
        elif level == "component":
            return self._generate_c4_component(architecture)
        else:
            return self._generate_c4_context(architecture)

    def _generate_c4_context(self, architecture: Dict[str, Any]) -> str:
        """Generate C4 Context diagram"""

        mermaid = """C4Context
    title System Context Diagram

    Person(user, "User", "Application user")
    Person(admin, "Administrator", "System administrator")

    System(app, "Application System", "Main application system")

    System_Ext(email, "Email System", "External email service")
    System_Ext(payment, "Payment Gateway", "External payment processing")
    System_Ext(analytics, "Analytics", "External analytics service")

    Rel(user, app, "Uses", "HTTPS")
    Rel(admin, app, "Administers", "HTTPS")

    Rel(app, email, "Sends emails", "SMTP")
    Rel(app, payment, "Processes payments", "API")
    Rel(app, analytics, "Sends events", "API")

    UpdateLayoutConfig($c4ShapeInRow="2", $c4BoundaryInRow="1")
"""

        return self._wrap_in_html(mermaid)

    def _generate_c4_container(self, architecture: Dict[str, Any]) -> str:
        """Generate C4 Container diagram"""

        pattern = architecture.get("primary_pattern", "monolith")

        if pattern == "microservices":
            mermaid = """C4Container
    title Container Diagram

    Person(user, "User")

    Container_Boundary(c1, "Application System") {
        Container(web, "Web Application", "React", "Delivers content and handles user interactions")
        Container(api, "API Gateway", "Node.js", "Routes requests to microservices")
        Container(auth, "Auth Service", "Python", "Handles authentication and authorization")
        Container(business, "Business Service", "Python", "Handles core business logic")
        Container(data, "Data Service", "Python", "Manages data operations")
    }

    ContainerDb(db, "Database", "PostgreSQL", "Stores application data")
    ContainerDb(cache, "Cache", "Redis", "Stores cached data")

    Rel(user, web, "Uses", "HTTPS")
    Rel(web, api, "Makes API calls", "JSON/HTTP")
    Rel(api, auth, "Authenticates", "JSON/HTTP")
    Rel(api, business, "Processes requests", "JSON/HTTP")
    Rel(business, data, "Reads/writes data", "JSON/HTTP")
    Rel(data, db, "Reads/writes", "SQL")
    Rel(data, cache, "Caches data", "Redis Protocol")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
"""
        else:
            mermaid = """C4Container
    title Container Diagram

    Person(user, "User")

    Container_Boundary(c1, "Application System") {
        Container(web, "Web Application", "React", "Single page application")
        Container(app, "Application Server", "Python", "Provides application logic and API")
    }

    ContainerDb(db, "Database", "PostgreSQL", "Stores all application data")

    Rel(user, web, "Uses", "HTTPS")
    Rel(web, app, "Makes API calls", "JSON/HTTPS")
    Rel(app, db, "Reads from and writes to", "SQL/TCP")

    UpdateLayoutConfig($c4ShapeInRow="2", $c4BoundaryInRow="1")
"""

        return self._wrap_in_html(mermaid)