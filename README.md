# Настройка проекта

Должны быть установлены pyenv и poetry.
Для корректной работы pyenv необходимо установить библиотеки для сборки версий python.

## Linux-окружение

pyenv под Linux может сразу не заработать. В этом случае нужно доустановить пакеты:

```bash
sudo apt update
sudo apt install \
    build-essential \
    curl \
    libbz2-dev \
    libffi-dev \
    liblzma-dev \
    libncursesw5-dev \
    libreadline-dev \
    libsqlite3-dev \
    libssl-dev \
    libxml2-dev \
    libxmlsec1-dev \
    llvm \
    make \
    tk-dev \
    wget \
    xz-utils \
    zlib1g-dev
```

## Инициализация проекта

Установить нужную версию Python на локальную систему:

```bash
pyenv install 3.11.8
```

Указать версию Python для бэкенда. Для этого в папке `src/backend` выполнить:

```bash
pyenv local 3.11.8
```

Установить зависимости:

```bash
pyenv shell 3.11.8
python -m venv .venv
poetry config virtualenvs.in-project true
poetry install
poetry shell
python -V
```

Установить переменную PYTHONPATH в настройках запуска и среде разработки. Ниже приведён пример для Visual Studion Code
для Windows (settings.json):

```json
    "python.analysis.extraPaths": [
"${workspaceFolder}"
],
"terminal.integrated.env.windows": {
"PYTHONPATH": "${workspaceFolder}"
}
```
