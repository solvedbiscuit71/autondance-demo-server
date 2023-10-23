# Autondance Demo Server

This is a demo server used for testing the flutter-api interaction
and provides a static overview the api.

```bash
git clone https://github.com/solvedbiscuit71/autondance-demo-server.git
cd autondance-demo-server
```

# Setup

We are using poetry as the package manager and build tool install poetry

Linux, macOS, Windows (WSL)
```sh
curl -sSL https://install.python-poetry.org | python3 -
```

Windows (Powershell)
```sh
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

Don't forget to add poetry to your $PATH,


`$HOME/.local/bin` on Unix.  
`%APPDATA%\Python\Scripts` on Windows.

## Install the dependencies

To install dependency, inside the cloned directory run,
```sh
poetry install
```

## Setup env variables

Create a new file `.env` in the root of the project and add the host and port
```
API_HOST=<ip>
API_PORT=<port-number>
```

## Start the server

To start the server, run
```bash
poetry run python main.py
```

This starts the server at http://127.0.0.1:8000 (by default). For API reference check out http://127.0.0.1:8000/docs and http://127.0.0.1:8000/redoc
