
import streamlit as st
import requests

st.set_page_config(page_title="AI Chat Application", page_icon="🤖")

st.title("🤖 AI Chat Application")
st.write("Module 3 - LLM APIs & Application Development")

api_key = st.secrets.get("GEMINI_API_KEY", "")

if "messages" not in st.session_state:
    st.session_state.messages = []

instructions = st.sidebar.text_area(
    "Custom Instructions",
    "You are a helpful AI assistant. Explain things in simple language."
)

max_tokens = st.sidebar.slider(
    "Maximum Response Tokens", 100, 2048, 512
)

if st.sidebar.button("Clear Chat History"):
    st.session_state.messages = []
    st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input("Ask me anything...")

if user_input:
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        if not api_key:
            st.error("GEMINI_API_KEY is missing in Streamlit Secrets.")
        else:
            try:
                contents = []

                for message in st.session_state.messages:
                    role = "model" if message["role"] == "assistant" else "user"
                    contents.append({
                        "role": role,
                        "parts": [{"text": message["content"]}]
                    })

                url = (
                    "https://generativelanguage.googleapis.com/"
                    "v1beta/models/gemini-3.8-flash:generateContent"
                )

                payload = {
                    "systemInstruction": {
                        "parts": [{"text": instructions}]
                    },
                    "contents": contents,
                    "generationConfig": {
                        "maxOutputTokens": max_tokens
                    }
                }

                
import time

for attempt in range(3):
    try:
        response = requests.post(
            url,
            headers={"x-goog-api-key": api_key},
            json=payload,
            timeout=30
        )

        if response.status_code in (429, 500, 502, 503, 504):
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue

        response.raise_for_status()
        break

    except requests.exceptions.Timeout:
        if attempt == 2:
            raise
        time.sleep(2 ** attempt)


                data = response.json()
                answer = data["candidates"][0]["content"]["parts"][0]["text"]

                st.write(answer)

                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )

            except requests.exceptions.HTTPError:
                st.error(
                    f"API request failed (HTTP {response.status_code}): "
                    f"{response.text[:500]}"
                )
            except requests.exceptions.RequestException as e:
                st.error(f"Connection error: {e}")
            except (KeyError, IndexError):
                st.error("The AI returned an unexpected or empty response.")
