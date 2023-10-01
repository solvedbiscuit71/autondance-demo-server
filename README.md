# Autondance Demo Server

This is a demo server used for testing the flutter-api interaction
and provides a static overview the api.

```bash
git clone <repo>
cd <repo>
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

## POST /upload

This route expects the request body to be form data with `application/x-www-form-urlencoded`
as its media type. This route expects one parameter which is a file (whose field name is also file)

```bash
curl --request POST \
  --url http://127.0.0.1:8000/upload \
  --header 'Content-Type: multipart/form-data' \
  --form 'file=@<absolute-path-to-file>'
```

Response
```json
{
	"message": "success",
	"data": [
		{
			"roll_no": "…",
			"name": "…",
			"is_present": true
		},
        // and so on...
	]
}
```
