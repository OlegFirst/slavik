#!/usr/bin/env python3
"""
Interactive Module Dashboard - Интерактивная визуализация модулей
"""

import json
from pathlib import Path
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px


class ModuleDashboard:
    def __init__(self, reports_dir: str = "tools/reports"):
        self.reports_dir = Path(reports_dir)
        self.ast_data = None
        self.deps_data = None

        # Загрузить данные
        self._load_data()

    def _load_data(self):
        """Загрузить результаты анализа"""
        ast_file = self.reports_dir / "ast_analysis.json"
        deps_file = self.reports_dir / "dependencies.json"

        if ast_file.exists():
            with open(ast_file) as f:
                self.ast_data = json.load(f)
            print(f"✅ Loaded AST data: {len(self.ast_data['functions'])} functions")

        if deps_file.exists():
            with open(deps_file) as f:
                self.deps_data = json.load(f)
            print(f"✅ Loaded dependency data: {len(self.deps_data['dependencies'])} modules")

    def create_dashboard(self):
        """Создать интерактивный dashboard"""
        if not self.ast_data or not self.deps_data:
            print("❌ No data found. Run analyzers first!")
            return

        # Создать subplot фигуру
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Endpoints by Method',
                'Top 10 Modules by Dependencies',
                'Functions vs Classes Distribution',
                'Async vs Sync Functions'
            ),
            specs=[
                [{'type': 'bar'}, {'type': 'bar'}],
                [{'type': 'pie'}, {'type': 'pie'}]
            ]
        )

        # 1. Endpoints by method
        endpoints_by_method = {}
        for endpoint in self.ast_data['endpoints']:
            method = endpoint['method']
            endpoints_by_method[method] = endpoints_by_method.get(method, 0) + 1

        fig.add_trace(
            go.Bar(
                x=list(endpoints_by_method.keys()),
                y=list(endpoints_by_method.values()),
                name='Endpoints',
                marker_color='lightblue'
            ),
            row=1, col=1
        )

        # 2. Top modules by dependencies
        top_deps = self.deps_data['statistics']['most_dependencies'][:10]
        fig.add_trace(
            go.Bar(
                x=[item['module'].split('.')[-1] for item in top_deps],
                y=[item['count'] for item in top_deps],
                name='Dependencies',
                marker_color='lightcoral'
            ),
            row=1, col=2
        )

        # 3. Functions vs Classes
        fig.add_trace(
            go.Pie(
                labels=['Functions', 'Classes'],
                values=[
                    self.ast_data['summary']['total_functions'],
                    self.ast_data['summary']['total_classes']
                ],
                name='Code Structure'
            ),
            row=2, col=1
        )

        # 4. Async vs Sync
        async_count = self.ast_data['summary']['async_functions']
        sync_count = self.ast_data['summary']['total_functions'] - async_count

        fig.add_trace(
            go.Pie(
                labels=['Async', 'Sync'],
                values=[async_count, sync_count],
                name='Function Types'
            ),
            row=2, col=2
        )

        # Обновить layout
        fig.update_layout(
            title_text="AI-Platform-ISO Module Analysis Dashboard",
            showlegend=True,
            height=800
        )

        # Сохранить HTML
        output_file = self.reports_dir / "dashboard.html"
        fig.write_html(str(output_file))
        print(f"\n✅ Dashboard saved: {output_file}")
        print(f"   Open in browser: file://{output_file.absolute()}")

        return fig

    def create_endpoint_map(self):
        """Создать интерактивную карту эндпоинтов"""
        if not self.ast_data:
            return

        endpoints = self.ast_data['endpoints']

        # Группировать по файлам
        file_groups = {}
        for endpoint in endpoints:
            file_name = Path(endpoint['file']).parts[-2:]  # service/file.py
            file_key = '/'.join(file_name)
            if file_key not in file_groups:
                file_groups[file_key] = []
            file_groups[file_key].append(endpoint)

        # Создать Sunburst диаграмму
        labels = ['API']
        parents = ['']
        values = [len(endpoints)]
        colors = ['lightgray']

        for file_name, file_endpoints in file_groups.items():
            # Добавить файл
            labels.append(file_name)
            parents.append('API')
            values.append(len(file_endpoints))
            colors.append('lightblue')

            # Добавить эндпоинты
            for endpoint in file_endpoints[:10]:  # Первые 10
                label = f"{endpoint['method']} {endpoint['path']}"
                labels.append(label)
                parents.append(file_name)
                values.append(1)
                colors.append('lightgreen')

        fig = go.Figure(go.Sunburst(
            labels=labels,
            parents=parents,
            values=values,
            marker=dict(colors=colors),
            branchvalues="total"
        ))

        fig.update_layout(
            title="API Endpoints Structure",
            width=1000,
            height=1000
        )

        output_file = self.reports_dir / "endpoint_map.html"
        fig.write_html(str(output_file))
        print(f"✅ Endpoint map: {output_file}")

        return fig

    def create_dependency_network(self):
        """Создать интерактивную сеть зависимостей"""
        if not self.deps_data:
            return

        # Подготовить данные для сетевого графа
        edge_x = []
        edge_y = []
        node_x = []
        node_y = []
        node_text = []

        # Использовать простую компоновку
        modules = list(self.deps_data['dependencies'].keys())
        n = len(modules)

        import math
        radius = 5

        # Расположить узлы по кругу
        positions = {}
        for i, module in enumerate(modules):
            angle = 2 * math.pi * i / n
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            positions[module] = (x, y)
            node_x.append(x)
            node_y.append(y)
            node_text.append(module.split('.')[-1])  # Только имя файла

        # Создать ребра
        for module, deps in self.deps_data['dependencies'].items():
            if module not in positions:
                continue
            x0, y0 = positions[module]
            for dep in deps:
                if dep in positions:
                    x1, y1 = positions[dep]
                    edge_x.extend([x0, x1, None])
                    edge_y.extend([y0, y1, None])

        # Создать граф
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        )

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=node_text,
            textposition="top center",
            marker=dict(
                showscale=True,
                colorscale='YlGnBu',
                size=10,
                colorbar=dict(
                    thickness=15,
                    title='Dependencies',
                    xanchor='left',
                    titleside='right'
                )
            )
        )

        # Установить цвет узлов по количеству зависимостей
        node_adjacencies = []
        for module in modules:
            node_adjacencies.append(len(self.deps_data['dependencies'].get(module, [])))

        node_trace.marker.color = node_adjacencies

        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                           title='Module Dependency Network',
                           showlegend=False,
                           hovermode='closest',
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           width=1200,
                           height=1200
                       ))

        output_file = self.reports_dir / "dependency_network.html"
        fig.write_html(str(output_file))
        print(f"✅ Dependency network: {output_file}")

        return fig

    def generate_all(self):
        """Генерировать все визуализации"""
        print("🎨 Generating interactive visualizations...\n")

        self.create_dashboard()
        self.create_endpoint_map()
        self.create_dependency_network()

        print("\n🎉 All visualizations created!")
        print(f"\nOpen in browser:")
        print(f"   Dashboard: file://{(self.reports_dir / 'dashboard.html').absolute()}")
        print(f"   Endpoint Map: file://{(self.reports_dir / 'endpoint_map.html').absolute()}")
        print(f"   Dependency Network: file://{(self.reports_dir / 'dependency_network.html').absolute()}")


if __name__ == "__main__":
    dashboard = ModuleDashboard()
    dashboard.generate_all()
