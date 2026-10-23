
import time
import requests
import streamlit as st

st.set_page_config(
    page_title="AI Chat Application",
    page_icon="🤖"
)

st.title("🤖 AI Chat Application")
st.caption("Codomax Module 3 - LLM APIs & Application Development")

api_key = st.secrets.get("GEMINI_API_KEY", "")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("Chat Settings")

    instructions = st.text_area(
        "Custom Instructions",
        "You are a helpful AI assistant. Explain in simple language."
    )

    max_tokens = st.slider(
        "Maximum Response Tokens",
        min_value=100,
        max_value=2048,
        value=512
    )

    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input("Ask me anything...")

if user_input:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        if not api_key:
            st.error("Gemini API key is missing in Streamlit Secrets.")
        else:
            try:
                contents = []

                for message in st.session_state.messages:
                    role = (
                        "model"
                        if message["role"] == "assistant"
                        else "user"
                    )

                    contents.append({
                        "role": role,
                        "parts": [{"text": message["content"]}]
                    })

                url = (
                    "https://generativelanguage.googleapis.com/"
                     "v1beta/models/gemini-3.5-flash-lite:generateContent"
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

                response = None

                with st.spinner("AI is thinking..."):
                    for attempt in range(3):
                        try:
                            response = requests.post(
                                url,
                                headers={
                                    "x-goog-api-key": api_key
                                },
                                json=payload,
                                timeout=30
                            )

                            if (
                                response.status_code
                                in (429, 500, 502, 503, 504)
                                and attempt < 2
                            ):
                                time.sleep(2 ** attempt)
                                continue

                            response.raise_for_status()
                            break

                        except requests.exceptions.Timeout:
                            if attempt == 2:
                                raise
                            time.sleep(2 ** attempt)

                data = response.json()

                answer = data["candidates"][0][
                    "content"
                ]["parts"][0]["text"]

                st.write(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except requests.exceptions.HTTPError as e:
                st.error(
                    f"API request failed: {e.response.status_code}"
                )
                st.code(e.response.text[:500])

            except requests.exceptions.Timeout:
                st.error(
                    "The AI server timed out. Please try again."
                )

            except requests.exceptions.RequestException as e:
                st.error(f"Connection error: {e}")

            except (KeyError, IndexError, TypeError):
                st.error(
                    "The AI returned an unexpected response."
                )
