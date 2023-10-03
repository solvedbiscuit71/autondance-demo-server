# Autondance Demo Server

This is a demo server used for testing the flutter-api interaction
and provides a static overview the api.

```bash
git clone https://github.com/solvedbiscuit71/autondence-demo-server.git
cd autondence-demo-server
```

# Setup

Create a new python virtual environment and install the dependencies
```bash
python -m venv venv
```

To activate your virtual environment

On windows
```bash
vevn\Scripts\activate
```

On macOS and Linux
```bash
source venv/bin/activate
```

## Install the dependencies

After activate your virtual environment, run
```bash
pip install -r requirements.txt
```


## Start the server

To start the server, run
```bash
uvicorn main:app
```

This starts the server at http://127.0.0.1:8000

# API Reference

Check out http://127.0.0.1:8000/doc
