# AI Chat Companion — Module 3

**Student:** Padma Angmo  
**Module:** LLM APIs & Application Development (Day 11–15)  
**Stack:** Python, Streamlit, OpenAI Python SDK

## Features
- Chat UI using Streamlit (`st.chat_input`, `st.chat_message`)
- API integration with server-side authentication
- System, user and assistant roles
- Session-based conversation history and clear-chat button
- Custom instructions, temperature and maximum output tokens
- Recent-message context limit to help control token usage
- Input/output token counters and illustrative cost estimate
- Friendly handling of API authentication, quota, network and server errors
- Explicit **demo mode** when no API key is configured (no fake AI replies)

## Run locally
1. Install Python 3.10 or newer.
2. Download or clone this repository.
3. Run `pip install -r requirements.txt`.
4. Set the environment variable `OPENAI_API_KEY` to your own API key (do not put the key in the code or commit it).
   - Windows PowerShell, for the current session: `$env:OPENAI_API_KEY="your-key"`
   - macOS/Linux: `export OPENAI_API_KEY="your-key"`
5. Run `streamlit run app.py`.
6. Open the localhost URL printed by Streamlit.

Without a key, the interface still runs in explicitly labeled demo mode.

## Deploy to Streamlit Community Cloud
1. Create a **public GitHub repository** and upload `app.py`, `requirements.txt`, `README.md`, `.gitignore`, and `.env.example`.
2. Visit https://share.streamlit.io/ and sign in with GitHub.
3. Select **Create app → Deploy a public app from GitHub** (wording may vary).
4. Choose your repository, branch `main`, and entrypoint `app.py`.
5. If you have an API key, add it in **Advanced settings / Secrets** using TOML:
   ```toml
   OPENAI_API_KEY = "your-actual-key"
   ```
   Never put the real key in GitHub or screenshots.
6. Deploy and copy the resulting `*.streamlit.app` URL.
7. Open the URL in an incognito/private window to confirm it loads. Without an API key, it is a demo UI; with a working key and sufficient quota, it can produce real responses.

## Architecture
User → Streamlit chat interface → Python application → OpenAI API → AI response → session history.

## Concepts practiced
- Authentication via environment variables/secrets
- LLM request parameters and system/user/assistant messages
- Session state, context limits, token accounting
- Error handling and basic API cost awareness

## Security and limitations
- API calls consume the app owner's API quota and may incur costs. Public deployment with a shared owner key can lead to unexpected charges. Consider restricted access, provider budget alerts, and stronger rate limiting before broad sharing.
- Chat history is per browser session and is not a persistent database.
- Token cost estimate uses **illustrative example rates**, not verified live prices; confirm current rates with your provider.
- Model availability and API billing requirements depend on your account.
- For a production app, add per-user authentication, abuse prevention, monitoring, privacy controls and persistent storage.
