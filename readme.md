# Interior Designer Agent

AI-powered Interior Designer Agent — a minimal, open-source MVP for generating interior design images and ideas using LLMs and image models.

This repository contains:

- **Streamlit App** (`app.py`) — a simple UI for generating and viewing interior design images.
- **Agent Core** (`lib/agent.py`) — the main agent logic for generating design suggestions and images.
- **File Management** (`lib/files.py`) — handles file operations for generated images and resources.
- **Output Images** (`output/`) — stores generated images and their low-res versions.
- **Resources** (`resources/`) — example images and floorplans for reference or input.

## 🚀 Features

- Generate interior design images using AI models
- Upload and use reference images or floorplans
- Simple Streamlit interface for easy interaction
- Extensible agent logic for custom design workflows

## 🛠️ Setup

### Prerequisites

- Python 3.11+
- API keys for any external model providers (only OpenAI in this case)

### Installation

1. Clone the repo:

```bash
git clone <repo-url>
cd interior-designer-agent
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create your `.env` file (copy `.env.example`):

```bash
cp .env.example .env
```

4. Set required environment variables in `.env`:

```
OPENAI_API_KEY=sk-...           # for LLM usage
```

Refer to `.env.example` for all available variables. You must provide valid API keys for any model providers you use. **There is no defined budget cap — users will likely incur costs associated with running the models.**

### Running the Project

Start the Streamlit app:

```bash
streamlit run app.py
```

Generated images will be saved in the `output/` directory..

## 💸 Cost Warning

**Important:** This agent does not enforce any budget cap. By default, users will likely incur costs when using external model APIs. Monitor your API usage and set limits with your provider if needed.

## 🏗️ Architecture (high-level)

1. `app.py` — Streamlit UI for generating and viewing images.
2. `lib/agent.py` — agent logic for design suggestions and image generation.
3. `lib/files.py` — file management utilities.
4. `output/` — stores generated images.

## 🤖 Usage Example

- Upload a floorplan or reference image via the Streamlit UI.
- Enter your design prompt (e.g., "1920s modern luxury").
- The agent generates images and saves them to `output/`.
- View and download generated images from the UI.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Run tests and linters
4. Open a pull request with a description of your changes

Please include a short description of how your change was tested.

---

Built with ❤️ by [Tom Shaw](https://tomshaw.dev)
