# Архив устаревших модулей

**Дата архивации**: 2025-10-10
**Причина**: Откат вчера (Oct 8) - старые standalone версии

---

## 📦 Содержимое

### 1. knowledge-system-standalone/
**Статус**: 🗑️ Устарел
**Размер**: 112KB
**Причина архивации**: Полностью интегрирован в `ai-foundation/learning-knowledge/knowledge/`

**Что произошло**:
- Модуль был объединен с `learning-system` в единый `learning-knowledge` модуль
- Все функции перенесены в `ai-foundation/learning-knowledge/knowledge/`
- Файлы идентичны, но `ai-foundation` версия НОВЕЕ (Oct 7 vs Oct 8)
- Импорты в `ai-foundation` исправлены на внутренние пути

**Новое расположение**:
```
ai-foundation/learning-knowledge/knowledge/
├── loader/
│   ├── standards_loader.py  # ISO/BCI/WHO/NIST
│   └── case_loader.py        # Workflow cases
├── indexer/
└── updater/
```

**Восстановление** (если нужно):
```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core
mv _archive-deprecated-2025-10-10/knowledge-system-standalone/ knowledge-system/
```

**НО!** Рекомендуется использовать `ai-foundation/learning-knowledge/`

---

### 2. learning-system-standalone/
**Статус**: 🗑️ Устарел
**Размер**: 844KB (28 Python файлов)
**Причина архивации**: Полностью интегрирован в `ai-foundation/learning-knowledge/learning/`

**Что произошло**:
- Модуль был объединен с `knowledge-system` в единый `learning-knowledge` модуль
- Все функции перенесены в `ai-foundation/learning-knowledge/learning/`
- `ai-foundation` версия НОВЕЕ и включает мониторинг (декораторы @track_*)
- Никто не импортирует старый модуль

**Новое расположение**:
```
ai-foundation/learning-knowledge/learning/
├── engines/
│   ├── pattern_detector.py      # Pattern detection
│   ├── ml_predictor.py          # ML predictions
│   ├── competency_tracker.py    # Competency tracking
│   ├── gamification_engine.py   # Gamification
│   └── self_learning_engine.py  # Self-learning
└── ml/
```

**Восстановление** (если нужно):
```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core
mv _archive-deprecated-2025-10-10/learning-system-standalone/ learning-system/
```

**НО!** Рекомендуется использовать `ai-foundation/learning-knowledge/`

---

## 🔍 Как проверить что всё работает

### 1. Проверить импорты в ai-foundation:
```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/ai-foundation
grep -r "from knowledge_system\|from learning_system" --include="*.py" .
# Должно вернуть: ничего (все импорты исправлены)
```

### 2. Запустить тесты:
```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/ai-foundation/learning-knowledge
pytest tests/test_basic.py -v
```

### 3. Проверить что сервисы запускаются:
```bash
cd /Users/MD/AI-Platform-ISO/intelligent-core/ai-foundation
python main.py
# Должен запуститься на порту 8053
```

---

## ⚠️ Важно

**Эти модули - ДУБЛИКАТЫ** откатившиеся вчера (Oct 8)!

Актуальная версия:
- **ai-foundation/learning-knowledge/** (1.5MB, 66 файлов, Oct 7)
  - Включает: knowledge + learning + новые фичи
  - С мониторингом
  - Production-ready

Архивированные версии:
- **knowledge-system** (112KB, Oct 8) - старая, без фич
- **learning-system** (844KB, Oct 8) - старая, без мониторинга

---

## 🚀 Миграция

Если вы использовали старые импорты, обновите:

**БЫЛО**:
```python
from knowledge_system.loader.standards_loader import StandardsLoader
from learning_system.engines.pattern_detector import PatternDetector
```

**СТАЛО**:
```python
from learning_knowledge.knowledge.loader.standards_loader import StandardsLoader
from learning_knowledge.learning.engines.pattern_detector import PatternDetector
```

---

## 📞 Вопросы?

Если что-то сломалось после архивации:
1. Проверьте импорты в вашем коде
2. Убедитесь что используете `ai-foundation/learning-knowledge/`
3. В крайнем случае - восстановите из архива (команды выше)

---

**Архивировано**: 2025-10-10 by Claude
**Статус**: ✅ Безопасно для удаления (после проверки)
