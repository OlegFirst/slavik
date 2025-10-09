# 🎨 Quick Visualization - Как посмотреть архитектуру

**Самый быстрый способ визуализировать всю систему**

---

## ⚡ БЫСТРЫЙ СТАРТ (3 минуты)

### 1️⃣ Открыть C4 Diagrams в VS Code/GitHub

```bash
# Открыть в VS Code (рендерит Mermaid автоматически)
code docs/architecture/C4_LEVEL1_SYSTEM_CONTEXT.md

# Или push в GitHub и открыть там
git add docs/architecture/
git commit -m "Add C4 diagrams"
git push
# Открыть на GitHub - диаграммы отрендерятся
```

**Что увидишь:**
- 🎨 Интерактивные диаграммы Mermaid
- 🔄 System Context (вся система + external)
- 📊 Sequence diagrams (user flows)
- 🚀 Deployment view (где что находится)
- 🔒 Security boundaries

---

### 2️⃣ Dependency Matrix (Markdown таблицы)

```bash
# Открыть в любом markdown viewer
cat docs/architecture/DEPENDENCY_MATRIX.md

# Или в VS Code
code docs/architecture/DEPENDENCY_MATRIX.md
```

**Что увидишь:**
- 📋 Таблицы всех зависимостей
- 🔥 Критичные сервисы (SPOF)
- ⚠️ High coupling warnings
- 📊 Impact scores

---

### 3️⃣ Service Catalog (YAML/Table)

```bash
# Посмотреть в terminal
cat docs/architecture/SERVICE_CATALOG.yaml | less

# Или конвертировать в таблицу
cat docs/architecture/SERVICE_CATALOG.yaml | yq -o json | jq -r '
  .ai_foundation |
  to_entries[] |
  "\(.key): port \(.value.port // "N/A"), status \(.value.status)"
'
```

---

## 📊 ADVANCED VISUALIZATION

### Option 1: Mermaid Live Editor (Online)

```bash
# 1. Открыть файл
cat docs/architecture/C4_LEVEL1_SYSTEM_CONTEXT.md | grep -A 100 "```mermaid"

# 2. Скопировать Mermaid код
# 3. Открыть https://mermaid.live
# 4. Вставить код
# 5. Экспортировать PNG/SVG
```

---

### Option 2: GraphViz (если установлен)

```bash
# Установить GraphViz
brew install graphviz

# Создать DOT файл из зависимостей
cat > /tmp/deps.dot << 'EOF'
digraph G {
    rankdir=LR;
    node [shape=box, style=filled, fillcolor=lightblue];

    // AI Foundation
    workflow_intelligence [fillcolor=gold];
    ai_workflow_optimizer;
    workflow_engine;
    expertise_center;

    // Dependencies
    workflow_intelligence -> postgresql;
    workflow_intelligence -> qdrant;
    workflow_intelligence -> eventbus;
    workflow_intelligence -> temporal;

    ai_workflow_optimizer -> postgresql;

    expertise_center -> community_intelligence;
    expertise_center -> collective;
    expertise_center -> learning_system;
    expertise_center -> living_docs;

    // Platform Services
    bia_service -> workflow_intelligence;
    risk_service -> workflow_intelligence;
    compliance_service -> workflow_intelligence;

    // Infrastructure
    postgresql [shape=cylinder, fillcolor=lightgreen];
    qdrant [shape=cylinder, fillcolor=lightcoral];
    eventbus [fillcolor=lightyellow];
    temporal [fillcolor=lavender];
}
EOF

# Сгенерировать PNG
dot -Tpng /tmp/deps.dot -o docs/architecture/dependency_graph.png

# Открыть
open docs/architecture/dependency_graph.png
```

---

### Option 3: Python NetworkX (интерактивный)

```bash
# Создать интерактивный граф
python3 << 'EOF'
import json
import networkx as nx
import matplotlib.pyplot as plt

# Загрузить зависимости
with open('tools/reports/dependencies.json') as f:
    data = json.load(f)

# Создать граф
G = nx.DiGraph()
deps = data.get('dependencies', {})

# Добавить edges (показать только top 20 модулей)
top_modules = list(deps.keys())[:20]
for module in top_modules:
    for dep in deps.get(module, [])[:5]:  # Top 5 deps
        if dep in top_modules:
            G.add_edge(module, dep)

# Визуализировать
plt.figure(figsize=(15, 10))
pos = nx.spring_layout(G, k=2, iterations=50)
nx.draw(G, pos,
        with_labels=True,
        node_color='lightblue',
        node_size=1500,
        font_size=8,
        font_weight='bold',
        arrows=True,
        edge_color='gray',
        arrowsize=20)

plt.title('AI Platform Dependencies (Top 20 Modules)')
plt.savefig('docs/architecture/networkx_graph.png', dpi=150, bbox_inches='tight')
print('✅ Saved to docs/architecture/networkx_graph.png')
plt.show()
EOF

open docs/architecture/networkx_graph.png
```

---

### Option 4: Excalidraw (ручная красота)

1. Открыть https://excalidraw.com
2. Использовать данные из `SERVICE_CATALOG.yaml` и `DEPENDENCY_MATRIX.md`
3. Нарисовать boxes для каждого сервиса
4. Соединить стрелками по зависимостям
5. Экспортировать PNG/SVG

**Плюсы:**
- 🎨 Красиво выглядит
- 🖱️ Интерактивно
- 📤 Легко шарить

---

## 📋 ЧТО ДОСТУПНО ПРЯМО СЕЙЧАС

### ✅ Готовые визуализации:

1. **C4_LEVEL1_SYSTEM_CONTEXT.md**
   - Mermaid diagrams
   - System context
   - User interactions
   - External systems
   - Security boundaries

2. **DEPENDENCY_MATRIX.md**
   - Markdown tables
   - Impact scores
   - SPOF analysis
   - Top 5 critical services

3. **SERVICE_CATALOG.yaml**
   - YAML structure
   - All 38 services
   - Ports, dependencies, endpoints

4. **tools/reports/dependencies.json**
   - JSON data
   - 8016 dependencies
   - 1430 modules

5. **WORK_COMPLETED.md**
   - Summary всего проекта
   - Статистика
   - Next steps

---

## 🎯 РЕКОМЕНДАЦИЯ

**Для тебя лучше всего:**

```bash
# 1. Открыть C4 diagram в VS Code
code docs/architecture/C4_LEVEL1_SYSTEM_CONTEXT.md

# 2. Если VS Code не рендерит Mermaid, установить extension:
# Name: Markdown Preview Mermaid Support
# ID: bierner.markdown-mermaid

# 3. Press Cmd+Shift+V для preview
```

**Или push в GitHub:**
```bash
git add docs/architecture/
git commit -m "Add architecture diagrams"
git push
# Открыть на GitHub - автоматически отрендерится
```

---

## 📊 Сравнение методов

| Метод | Время | Качество | Интерактивность |
|-------|-------|----------|-----------------|
| **Mermaid в VS Code/GitHub** | 0 мин | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Markdown tables** | 0 мин | ⭐⭐⭐⭐ | ⭐ |
| **GraphViz** | 5 мин | ⭐⭐⭐⭐ | ⭐ |
| **NetworkX** | 10 мин | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Excalidraw** | 30 мин | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **tools/dashboards/** | 2 мин | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## ✅ ИТОГО

**Самый быстрый способ:**

```bash
# В VS Code (с Mermaid extension)
code docs/architecture/C4_LEVEL1_SYSTEM_CONTEXT.md
# Cmd+Shift+V для preview
```

**Или в браузере:**
```bash
# Push в GitHub
git add docs/ && git commit -m "docs" && git push
# Открыть на GitHub
```

**Все диаграммы отрендерятся автоматически! 🎉**

---

## 📝 Summary

Все что создано:
1. ✅ `C4_LEVEL1_SYSTEM_CONTEXT.md` - Mermaid diagrams
2. ✅ `DEPENDENCY_MATRIX.md` - Markdown tables
3. ✅ `SERVICE_CATALOG.yaml` - YAML data
4. ✅ `WORK_COMPLETED.md` - Full summary
5. ✅ `tools/reports/` - JSON data для программной обработки

**Открывай в VS Code с Mermaid extension - и все увидишь! 🚀**
