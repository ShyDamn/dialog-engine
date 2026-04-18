# dialog-engine

Библиотека для описания **пошаговых диалогов** (мастеров, анкет, визардов) в JSON или YAML. Вы задаёте список шагов и тип каждого шага; при необходимости шаги можно **показывать или пропускать** в зависимости от уже собранных данных (**контекста**). Ядро не привязано к Telegram — его можно использовать в веб-приложениях, CLI и т.д. Дополнительно есть интеграция с **aiogram 3** (готовые inline-клавиатуры под типичные сценарии).

**Лицензия:** исходный код открыт для просмотра (**source-available**), но **изменение и распространение изменённой версии запрещены**; в своих проектах вы можете **устанавливать пакет и использовать его как библиотеку** без переписывания кода библиотеки. Это **не** «open source» в смысле [Open Source Initiative](https://opensource.org/osd): по определению OSD право на модификацию и производные работы обязательно. Подробности — в [LICENSE](LICENSE).

**Требования:** Python 3.10+.

---

## Установка

Минимальная установка (только ядро, без зависимостей):

```bash
pip install dialog-engine
```

Дополнительные возможности подключаются **extras** (установите только то, что нужно):

| Extra | Назначение |
|-------|------------|
| `validation` | Строгая проверка структуры JSON через Pydantic |
| `yaml` | Загрузка диалогов из YAML-файлов (PyYAML) |
| `aiogram` | Хелперы для inline-клавиатур под aiogram 3 |

Примеры:

```bash
pip install dialog-engine[validation]
pip install dialog-engine[yaml,aiogram]
pip install dialog-engine[validation,yaml,aiogram]
```

Разработка пакета из клонированного репозитория:

```bash
pip install -e ".[dev]"
```

---

## Идея в двух словах

1. В файле описывается массив **шагов** (`steps`). У каждого шага есть `id`, `type` и поле `text` (часто это ключ для i18n или просто текст вопроса).
2. Во время работы приложение хранит **контекст** — обычный словарь (например ответы пользователя: `{"email": "...", "plan": "pro"}`). Ключи в условиях совпадают с ключами контекста.
3. Движок **`DialogEngine`** умеет по контексту определить, какие шаги **видимы**, и вычислить **следующий/предыдущий** видимый шаг — без ручных `if` в коде для каждого сценария.

---

## Формат JSON

Корень файла — либо объект с полем `steps`, либо сразу массив шагов:

```json
{
  "steps": [
    { "id": "name", "type": "text", "text": "question-name", "required": true },
    { "id": "plan", "type": "choice", "text": "question-plan", "required": true,
      "choices": { "free": "plan-free", "pro": "plan-pro" } }
  ]
}
```

### Поля шага

| Поле | Обязательно | Описание |
|------|-------------|----------|
| `id` | да | Уникальный идентификатор шага; по нему удобно сохранять ответ в контексте (`context[id] = ...`). |
| `type` | да | Логический тип шага. В ядре допустимы произвольные строки; типичные: `text`, `choice`, `photo` — интерпретация на стороне вашего UI. |
| `text` | да | Текст вопроса или ключ локализации (библиотека его не переводит). |
| `required` | нет, по умолчанию `true` | Обязательность шага (для вашей логики и extras aiogram — кнопка «Пропустить»). |
| `choices` | для `choice` | Объект `"значение_ответа": "ключ_подписи"` — подписи снова передаются в `translate()` в aiogram-extra. |
| `min`, `max` | для шагов с вложениями | Для типа `photo` в примерах это минимальное и максимальное число файлов; в объекте `DialogStep` они хранятся как `min_photos` / `max_photos`. |
| `skip_when` | нет | Условие: если выполняется — шаг **не показывается** (пропускается при навигации). |
| `show_when` | нет | Если задано — шаг показывается **только** когда условие выполняется. Если не задано и `skip_when` не срабатывает — шаг виден. |

### Условия `skip_when` и `show_when`

Задаются одним объектом или списком объектов верхнего уровня (логика **И** между элементами списка).

**Листовое условие** (один объект с полем `field`):

- `equals`, `in`, `not_in` — как раньше;
- `exists: true` — в контексте есть ключ и значение не `None`; `exists: false` — ключа нет или значение `None`;
- `lt`, `gt`, `lte`, `gte` — сравнение значения в поле с числом или строкой (через обычные операторы Python).

**Составные правила** (без обязательного `field` у корня):

- `any_of: [ {...}, {...} ]` — достаточно одного из вложенных правил (логика **ИЛИ**);
- `all_of: [ {...}, {...} ]` — должны выполняться все вложенные правила (эквивалент списка на верхнем уровне).

Пример: не показывать шаг загрузки фото карты, если владелец карты — третье лицо (значение в контексте заранее записано, например после шага `choice`):

```json
{
  "id": "bank_card_photo",
  "type": "photo",
  "text": "upload-card",
  "required": false,
  "min": 1,
  "max": 1,
  "skip_when": { "field": "card_owner", "equals": "third" }
}
```

Если поля `field` в контексте нет, сравнение идёт с `None` (например `equals` с конкретной строкой не сработает).

---

## Python API: ядро

### Загрузка

```python
from pathlib import Path
from dialog_engine import DialogEngine

engine = DialogEngine.from_file(Path("wizard.json"))
# или из строки JSON:
engine = DialogEngine.from_json_string('{"steps": [...]}')
# или из списка dict (например после своего парсера):
engine = DialogEngine.from_list([{...}, {...}])
```

### Объект шага `DialogStep`

Поля соответствуют JSON; у фото-диапазона в коде имена `min_photos` / `max_photos`.

### Навигация и прогресс

Контекст — любой `Mapping` (часто обычный `dict` с ответами пользователя).

```python
ctx = {"card_owner": "self"}

# Индексы шагов в конфиге — «сырые» (0 .. len-1). Видимость зависит от ctx.
engine.get_step(0)                    # шаг по индексу или None
engine.get_step_by_id("email")        # (index, DialogStep) или None

engine.total()                        # число шагов в файле (все подряд)
engine.effective_total(ctx)           # сколько шагов видно при данном контексте
engine.effective_position(3, ctx)   # номер среди видимых (1-based) или None, если индекс скрыт

engine.next_index(2, ctx)           # следующий видимый индекс после 2, или None — конец
engine.previous_index(5, ctx)       # предыдущий видимый, или None
engine.visible_indices(ctx)         # список сырых индексов видимых шагов по порядку
engine.first_visible_index(ctx)
engine.iter_visible_steps(ctx)      # итератор (index, DialogStep) только по видимым

engine.is_last(4)                   # последний ли индекс в конфиге (без учёта скрытых)
engine.is_last_visible(4, ctx)      # последний ли среди видимых

engine.validation_errors()          # список ошибок конфигурации (дубликаты id, пустой список шагов)
```

Функция `validate_engine(engine)` в модуле `dialog_engine` возвращает то же, что и `DialogEngine.validation_errors()`.

### Снимок сессии (индекс + контекст)

Для сохранения в БД или сессии удобен `DialogSessionState`:

```python
from dialog_engine import DialogSessionState

state = DialogSessionState(index=2, context={"name": "Ann"})
raw = state.to_json()
restored = DialogSessionState.from_json(raw)
```

### JSON Schema и Mermaid

- `get_dialog_json_schema()` и константа `DIALOG_FILE_SCHEMA` — черновая JSON Schema корня файла (для редакторов и `dialog-engine schema`).
- `engine_to_mermaid(engine)` — текст диаграммы Mermaid: линейная цепочка шагов по порядку в файле (видимость в рантайме не отображается).

### Проверка видимости одного шага

```python
from dialog_engine import step_is_visible

if step_is_visible(step, ctx):
    ...
```

Полезно при фильтрации обязательных полей или при построении сводки только по актуальным шагам.

---

## Дополнения (extras)

### Pydantic (`validation`)

После `pip install dialog-engine[validation]` можно проверять структуру данных до загрузки в движок:

```python
from dialog_engine.pydantic_schema import validate_dialog_data
import json

with open("wizard.json", encoding="utf-8") as f:
    data = json.load(f)
validate_dialog_data(data)   # при ошибке — ValidationError
```

Имеет смысл в CI и в редакторах конфигов.

### YAML (`yaml`)

```python
from dialog_engine.loaders import from_yaml_file

engine = from_yaml_file("wizard.yaml")
```

Корень YAML — как в JSON: `steps: [...]` или список шагов.

### aiogram 3 (`aiogram`)

```python
from dialog_engine.integrations.aiogram import (
    KeyboardCallbacks,
    build_step_keyboard,
    build_photo_keyboard,
)

# translate — функция вида lambda key: str, возвращающая подпись кнопки/строки
kb = build_step_keyboard(
    step,
    translate,
    show_back=True,
    current_value=context.get(step.id),
    keep_button_text=...,  # опционально, готовая строка для «оставить»
)

kb = build_photo_keyboard(
    translate,
    show_done=True,
    show_keep=False,
    keep_button_text=None,
    show_clear=True,
    show_skip=True,
)
```

По умолчанию `callback_data` совместимы с префиксами вроде `dialog_choice:field_id:key`, `dialog_skip`, `dialog_back` и т.д. Свои значения можно задать через **`KeyboardCallbacks`** (поля `skip`, `back`, `keep`, `photo_done`, `photo_clear`, `choice_prefix` и метод `choice_data(step_id, key)`).

Для разбора нажатий:

```python
from dialog_engine.integrations.aiogram import KeyboardCallbacks, parse_choice_callback, is_named_callback

cb = KeyboardCallbacks()
pair = parse_choice_callback(callback.data, cb)  # ("step_id", "choice_key") или None
if pair:
    step_id, key = pair
...
if is_named_callback(callback.data, cb.skip):
    ...
```

---

## Командная строка

После установки пакета доступны **`dialog-engine`** (подкоманды) и алиас **`dialog-engine-validate`** (только проверка файла, как в 0.1.0).

Проверка JSON и целостности графа (дубликаты `id` и т.д.):

```bash
dialog-engine validate путь/к/диалог.json
dialog-engine-validate путь/к/диалог.json
```

Строгая проверка через Pydantic (extra `validation`):

```bash
dialog-engine validate --strict путь/к/диалог.json
```

Вывод JSON Schema в stdout:

```bash
dialog-engine schema > dialog.schema.json
```

Mermaid (порядок шагов в файле):

```bash
dialog-engine mermaid путь/к/диалог.json
```

Шаблон минимального диалога:

```bash
dialog-engine init -o my-dialog.json
```

Через модуль можно по-прежнему передать только путь к файлу — он будет обработан как `validate`:

```bash
python -m dialog_engine путь/к/диалог.json
```

Коды выхода: `0` — успех, иначе ошибка (в т.ч. отсутствие файла или `--strict` без Pydantic).

### Сопровождение релиза (для авторов)

Краткий чеклист: синхронизировать `version` в `pyproject.toml` и `dialog_engine.__version__`, собрать артефакты (`pip install build && python -m build`), при необходимости проверить на TestPyPI (`twine upload --repository testpypi dist/*`), затем `twine upload dist/*`. Не храните в репозитории токены PyPI. Файл `PUBLISHING.md` в пакет не входит и в git не отслеживается (см. `.gitignore`).

---

## Как встроить в приложение

1. Загрузите диалог один раз (или при смене файла) через `DialogEngine.from_file`.
2. В состоянии сессии храните **текущий индекс** шага (сырой индекс в массиве `steps`) и **контекст** (ответы).
3. После каждого ответа обновляйте контекст, например `context[step.id] = value`.
4. Для перехода вперёд используйте `next_index(current_index, context)`; если вернулось `None` — диалог закончен (или нужно перейти на экран подтверждения).
5. Для «Назад» — `previous_index(current_index, context)`.
6. Для индикатора «Шаг 2 из 5» используйте `effective_position` и `effective_total`, чтобы число шагов учитывало скрытые по `skip_when` / `show_when`.

Типы `text` / `choice` / `photo` в JSON — соглашение; библиотека не отправляет сообщения и не качает файлы. Реализацию ввода-вывода делаете вы (Telegram, HTTP, TUI и т.д.).

---

## Авторы

| | GitHub | Email |
|---|--------|-------|
| **Данила Шубин** | [@ShyDamn](https://github.com/ShyDamn) | [den03062003@gmail.com](mailto:den03062003@gmail.com) |
| **Савелий Хвостов** | [@k0te1ch](https://github.com/k0te1ch) | [khvostov40@gmail.com](mailto:khvostov40@gmail.com) |

---

## Лицензия

Текст лицензии — в файле [LICENSE](LICENSE) (англ.). Кратко:

- можно **устанавливать**, **запускать** и **подключать** пакет в своих приложениях;
- можно **распространять неизменённые** копии (в т.ч. через PyPI), с сохранением уведомления об авторских правах и текста лицензии;
- **нельзя** изменять исходники библиотеки, создавать производные работы на их основе и распространять изменённые версии;
- отчёты об ошибках и предложения по улучшению приветствуются через репозиторий, но это **не** разрешение на форк с правками.

Для сравнения: лицензии Creative Commons с условием **NoDerivatives** (например [CC BY-ND](https://creativecommons.org/licenses/by-nd/4.0/)) близки по духу («не переделывать и не распространять переделки»), но CC **не рекомендует** применять свои лицензии к ПО; поэтому здесь используется отдельный текст, заточенный под программное обеспечение.
