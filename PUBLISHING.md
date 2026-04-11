# Публикация и сопровождение (для автора репозитория)

Этот файл не для пользователей библиотеки. Здесь — чеклист релиза на PyPI и сопутствующие задачи.

## Перед первым релизом

1. **Имя на PyPI** — убедиться, что имя дистрибутива (`dialog-engine` в `pyproject.toml`) свободно или зарезервировано: https://pypi.org/project/dialog-engine/
2. **Метаданные** в `[project]` файла `pyproject.toml`:
   - `authors` (Danila Shubin, Saveliy Khvostov), `license = { file = "LICENSE" }`, `readme`
   - `project.urls` — репозиторий [github.com/ShyDamn/dialog-engine](https://github.com/ShyDamn/dialog-engine) (владелец: ShyDamn)
3. **Версия** — синхронизировать `version` в `pyproject.toml` и при необходимости `__version__` в `src/dialog_engine/__init__.py`.

## Сборка артефактов

Из каталога `DialogEngine` (где лежит `pyproject.toml`):

```bash
pip install build
python -m build --outdir dist .
```

В `dist/` появятся `.tar.gz` (sdist) и `.whl` (wheel).

Проверка установки колёса в чистом окружении:

```bash
pip install dist/dialog_engine-*.whl
python -c "import dialog_engine; print(dialog_engine.__version__)"
```

## TestPyPI (рекомендуется перед боем)

```bash
pip install twine
twine upload --repository testpypi dist/*
```

Установка с тестового индекса:

```bash
pip install -i https://test.pypi.org/simple/ dialog-engine==<версия>
```

## PyPI (production)

```bash
twine upload dist/*
```

Потребуются учётные данные PyPI (API token или логин/пароль). Не коммитьте токены в репозиторий — используйте `~/.pypirc` или переменные окружения / секреты CI.

## Релиз на GitHub

1. Обновить версию и changelog (если ведёте).
2. Создать тег `v0.x.y` и запушить.
3. Прикрепить к релизу файлы из `dist/` или полагаться на автосборку workflow (если настроена).

## CI

В монорепозитории ArrowMediaBot workflow: `.github/workflows/dialog-engine-ci.yml` (пути `DialogEngine/**`). После выноса библиотеки в отдельный репозиторий перенесите workflow в корень и уберите `working-directory: DialogEngine`, либо оставьте структуру с подпапкой — по ситуации.

## После релиза

- Проверить страницу проекта на PyPI (описание, ссылки).
- При необходимости обновить зависимость в приложениях: `dialog-engine = "^0.x.y"` вместо `path = ...`.
