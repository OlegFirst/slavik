# 📚 GitHub Pages Documentation Generator

Автоматическая генерация и обновление GitHub Pages документации из исходных каталогов проекта.

## 🎯 Цель

Этот инструмент автоматически:
- ✅ Читает данные из `/catalogs/` (services, subsystems, systems)
- ✅ Обновляет HTML страницы в `/docs/`
- ✅ Генерирует `stats.json` для JavaScript
- ✅ Запускается автоматически при коммитах через GitHub Actions

## 📁 Структура

```
scripts/docs-generator/
├── generate_docs.py                    # Main generator
├── update_service_catalog_page.py      # Service catalog updater
├── requirements.txt                    # Python dependencies
└── README.md                           # This file
```

## 🚀 Использование

### Локально

```bash
# 1. Install dependencies
pip install -r scripts/docs-generator/requirements.txt

# 2. Generate documentation
python scripts/docs-generator/generate_docs.py

# 3. Update service catalog page (optional)
python scripts/docs-generator/update_service_catalog_page.py
```

### Автоматически (GitHub Actions)

Workflow автоматически запускается при:
- Push в `main` или `recovery-7-8-oct` branch
- Изменениях в `catalogs/**` или `infrastructure/**`
- Ручном запуске через GitHub UI

**Workflow**: `.github/workflows/update-docs.yml`

## 📊 Что генерируется

### 1. `docs/assets/stats.json`

Статистика для JavaScript:

```json
{
  "generated_at": "2025-10-14T...",
  "services": {
    "total": 62,
    "platform": 46,
    "applications": 16,
    "by_category": {...}
  },
  "subsystems": {
    "total": 12,
    "list": [...]
  },
  "systems": {
    "total": 19,
    "list": [...]
  },
  "ports": {
    "postgresql": 5432,
    "redis": 6379,
    ...
  }
}
```

### 2. Updated `docs/index.html`

Обновляет статистику:
- Platform Services count
- AI Modules count
- Other dynamic stats

### 3. `docs/service-catalog-comprehensive/`

Полный каталог сервисов:
- `COMPREHENSIVE_SERVICE_CATALOG.md` - Markdown документация
- `service-catalog-full.json` - JSON для API

## 🔄 Workflow Diagram

```
┌─────────────────┐
│ Git Push        │
│ (catalogs/**) │
└────────┬────────┘
         │
         ↓
┌─────────────────────────┐
│ GitHub Actions Trigger  │
└────────┬────────────────┘
         │
         ↓
┌──────────────────────────┐
│ Install Python + deps    │
└────────┬─────────────────┘
         │
         ↓
┌──────────────────────────┐
│ Run generate_docs.py     │
│ - Parse catalogs/*.yaml  │
│ - Generate stats.json    │
│ - Update index.html      │
└────────┬─────────────────┘
         │
         ↓
┌──────────────────────────┐
│ Commit & Push changes    │
│ (if docs/ changed)       │
└────────┬─────────────────┘
         │
         ↓
┌──────────────────────────┐
│ GitHub Pages Deploy      │
│ (automatic)              │
└──────────────────────────┘
```

## 📖 Источники данных

Generator читает:

1. **Service Catalog**
   - Path: `/catalogs/platform-services/SERVICE_CATALOG_DETAILED.yaml`
   - Contains: 46 platform services + metadata

2. **Subsystems Catalog**
   - Path: `/catalogs/subsystems/SUBSYSTEMS_CATALOG.yaml`
   - Contains: 12 subsystems (deployment groups)

3. **Systems Catalog**
   - Path: `/catalogs/systems/SYSTEMS_CATALOG.yaml`
   - Contains: 19 functional systems

4. **User Applications**
   - Path: `/catalogs/business-services/USER_APPLICATIONS_CATALOG.yaml`
   - Contains: 16 user applications

## 🔧 Расширение

### Добавить новую страницу для генерации

1. Создайте новый метод в `DocsGenerator`:

```python
def generate_my_page(self, data: Dict[str, Any]) -> None:
    """Generate my custom page"""
    template = DOCS_DIR / "templates" / "my-page.html"
    output = DOCS_DIR / "my-page.html"

    # Your logic here
    content = self.render_template(template, data)
    output.write_text(content)
```

2. Вызовите в `generate_all()`:

```python
def generate_all(self):
    # ... existing code ...
    self.generate_my_page(data)
```

### Добавить новый каталог

1. Создайте метод парсинга:

```python
def parse_my_catalog(self) -> Dict[str, Any]:
    catalog_path = CATALOGS_DIR / "my-catalog" / "MY_CATALOG.yaml"
    catalog = self.load_yaml(catalog_path)
    return catalog
```

2. Добавьте в `generate_all()`:

```python
my_catalog = self.parse_my_catalog()
data['my_catalog'] = my_catalog
```

## 🎨 HTML Template Updates

Generator использует **string replacement** для обновления HTML:

```python
import re

# Update stat in HTML
content = re.sub(
    r'<h4>\d+</h4>\s*<p>Platform Services</p>',
    f'<h4>{total_services}</h4>\n<p>Platform Services</p>',
    content
)
```

Для более сложных обновлений можно использовать:
- BeautifulSoup4 для DOM manipulation
- Jinja2 для template rendering

## 📝 TODO

- [ ] Add more page generators (architecture.html, modules.html)
- [ ] Generate port allocation table
- [ ] Create service dependency graph
- [ ] Add architecture diagrams from Mermaid
- [ ] Integrate with project-agent for metrics
- [ ] Add changelog generation from git history

## 🐛 Troubleshooting

### Error: "Service catalog not found"

```bash
# Check if catalog exists
ls catalogs/platform-services/SERVICE_CATALOG_DETAILED.yaml

# If not, copy from infrastructure
cp infrastructure/runtime/service-catalog/SERVICE_CATALOG_DETAILED.yaml \
   catalogs/platform-services/
```

### Error: "Module 'yaml' not found"

```bash
pip install PyYAML>=6.0.1
```

### GitHub Actions fails

Check workflow logs:
1. Go to GitHub → Actions
2. Click on failed workflow
3. Check step logs
4. Common issues:
   - Python version mismatch
   - Missing dependencies
   - File permissions

## 📄 License

MIT - Same as main project

## 🤝 Contributing

1. Make changes to generator scripts
2. Test locally: `python scripts/docs-generator/generate_docs.py`
3. Check output in `docs/`
4. Commit and push
5. GitHub Actions will auto-update docs

---

**Last Updated**: 2025-10-14
**Maintainer**: AI Platform Team
