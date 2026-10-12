
import streamlit as st
import requests
import os

st.set_page_config(page_title="AI Chat Companion", page_icon="🤖")

st.title("🤖 AI Chat Companion")
st.caption("Module 3 | LLM APIs & Application Development | Padma Angmo")

# Gemini API key from Streamlit Secrets
try:
    API_KEY = st.secrets.get("GEMINI_API_KEY", "")
except Exception:
    API_KEY = os.getenv("GEMINI_API_KEY", "")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar settings
with st.sidebar:
    st.header("Chat Settings")

    instructions = st.text_area(
        "Custom Instructions",
        value="You are a helpful AI assistant. Explain clearly and simply."
    )

    temperature = st.slider(
        "Creativity",
        min_value=0.0,
        max_value=1.0,
        value=0.7
    )

    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
user_input = st.chat_input("Ask me anything...")

if user_input:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        if not API_KEY:
            response = "Please configure GEMINI_API_KEY in Streamlit Secrets."
        else:
            try:
                url = (
                    "https://generativelanguage.googleapis.com/v1beta/"
                    "models/gemini-2.5-flash:generateContent"
                )

                contents = []
                for msg in st.session_state.messages:
                    role = "model" if msg["role"] == "assistant" else "user"
                    contents.append({
                        "role": role,
                        "parts": [{"text": msg["content"]}]
                    })

                payload = {
                    "systemInstruction": {
                        "parts": [{"text": instructions}]
                    },
                    "contents": contents,
                    "generationConfig": {
                        "temperature": temperature,
                        "maxOutputTokens": 1024
                    }
                }

                result = requests.post(
                    url,
                    headers={
                        "x-goog-api-key": API_KEY,
                        "Content-Type": "application/json"
                    },
                    json=payload,
                    timeout=60
                )

                result.raise_for_status()
                data = result.json()

                parts = data["candidates"][0]["content"]["parts"]
                response = "".join(
                    part.get("text", "") for part in parts
                )

                if not response.strip():
                    response = "No text response was returned."

            except requests.exceptions.HTTPError as error:
                status = error.response.status_code

                if status == 429:
                    response = "API rate limit reached. Please try later."
                elif status in (401, 403):
                    response = "API authentication or permission error."
                elif status == 404:
                    response = "Model not available. Check the Gemini model name."
                else:
                   response = f"API request failed (HTTP {status}): {error.response.text}"

            except requests.exceptions.RequestException:
                response = "Network error. Please try again."

            except (KeyError, IndexError, TypeError):
                response = "Unexpected API response. Please try again."

        st.markdown(response)

    if API_KEY and "data" in locals() and response and result.ok:
        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })
