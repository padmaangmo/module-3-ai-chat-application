import os
import streamlit as st
from openai import OpenAI, AuthenticationError, RateLimitError, APIConnectionError, APIStatusError

st.set_page_config(page_title='AI Chat Companion | Module 3', page_icon='💬', layout='centered')
st.title('💬 AI Chat Companion')
st.caption('Module 3 · LLM APIs & Application Development · Padma Angmo')

MODEL = 'gpt-4o-mini'
INPUT_RATE_PER_M = 0.15  # Example pricing only; verify current provider pricing.
OUTPUT_RATE_PER_M = 0.60

if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'usage' not in st.session_state:
    st.session_state.usage = {'input': 0, 'output': 0}

with st.sidebar:
    st.header('⚙️ Chat Settings')
    instructions = st.text_area('Custom instructions', value='You are a helpful assistant. Explain things clearly and accurately.', height=125)
    temperature = st.slider('Creativity (temperature)', 0.0, 1.0, 0.5, 0.1)
    max_tokens = st.slider('Max response tokens', 100, 1000, 400, 50)
    st.divider()
    st.subheader('Usage (this session)')
    st.write(f"Input tokens: {st.session_state.usage['input']}")
    st.write(f"Output tokens: {st.session_state.usage['output']}")
    estimate = (st.session_state.usage['input'] * INPUT_RATE_PER_M + st.session_state.usage['output'] * OUTPUT_RATE_PER_M) / 1_000_000
    st.caption(f'Illustrative cost estimate: ${estimate:.6f} USD (example rates, not a bill)')
    if st.button('🗑️ Clear chat history'):
        st.session_state.messages = []
        st.session_state.usage = {'input': 0, 'output': 0}
        st.rerun()

api_key = os.getenv('OPENAI_API_KEY', '')
try:
    api_key = api_key or st.secrets.get('OPENAI_API_KEY', '')
except (FileNotFoundError, KeyError):
    pass

if not api_key:
    st.info('Demo mode: add OPENAI_API_KEY in Streamlit Cloud secrets or a local environment variable to enable real AI responses. No API key is exposed to visitors.')

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

user_input = st.chat_input('Ask me anything…')
if user_input:
    if len(user_input) > 3000:
        st.warning('Please keep your message under 3,000 characters.')
        st.stop()
    st.session_state.messages.append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.markdown(user_input)
    with st.chat_message('assistant'):
        if not api_key:
            response_text = ('**Demo mode:** Your message was received. To enable a real LLM answer, the app owner must configure the OPENAI_API_KEY secret. ' 'This placeholder is not an AI-generated response.')
            st.info(response_text)
        else:
            try:
                client = OpenAI(api_key=api_key, timeout=25.0, max_retries=1)
                # Limit conversation sent to the API to reduce context size and cost.
                recent = st.session_state.messages[-12:]
                result = client.chat.completions.create(
                    model=MODEL,
                    messages=[{'role': 'system', 'content': instructions}] + recent,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                response_text = result.choices[0].message.content or '(The model returned no text.)'
                st.markdown(response_text)
                if result.usage:
                    st.session_state.usage['input'] += result.usage.prompt_tokens or 0
                    st.session_state.usage['output'] += result.usage.completion_tokens or 0
            except AuthenticationError:
                response_text = 'Authentication failed. The app owner should check the server-side API key.'
                st.error(response_text)
            except RateLimitError:
                response_text = 'API rate limit or quota reached. Please try later.'
                st.error(response_text)
            except APIConnectionError:
                response_text = 'Could not connect to the AI service. Please try again.'
                st.error(response_text)
            except APIStatusError as exc:
                response_text = f'AI service error (HTTP {exc.status_code}). Please try again.'
                st.error(response_text)
            except Exception:
                response_text = 'An unexpected error occurred. Please try again.'
                st.error(response_text)
    st.session_state.messages.append({'role': 'assistant', 'content': response_text})

st.divider()
st.caption('Chat history and usage are kept in the current Streamlit session. Do not enter sensitive personal information. API usage may incur charges.')
