# personal-gemini

## setup

### 1. create environment

```bash
python -m venv .venv

source .venv/bin/activate
```

### 2. install npm

```bash
cd client
npm install
```

### 3. install pip

```bash
cd server
pip install -r server/requirements.txt
```

### 4. create google_key.json

```bash
cd server
touch google_key.json
```

and write google cloud platform service account key json file.<br>
<a href="https://cloud.google.com/vertex-ai/docs/start/cloud-environment?hl=ja" target="_blank">
Please check this URL for details.
</a>

### 5. create .env file or not(not required)

```txt:.env
# google custom search engine id
GOOGLE_CSE_ID = "*****"
# google custom search engine api key
GOOGLE_API_KEY = "*****"
# google cloud platform project id
PROJECT_ID = "*****"
# google cloud platform region
REGION = "*****"
# notino api key
NOTION_API_KEY = "secret_*****"
```

## usage1

```bash
cd server
python main_gradio.py
```

## usage2

open two terminals

### 1. start server

```bash
cd server
python main.py
```

### 2. start client

```bash
cd client
npm run dev
```

### 3. open browser

http://localhost:5173
