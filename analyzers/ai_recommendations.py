import streamlit as st
import requests

def run_ai_recommendations(html_content):
    key = st.secrets.get("TOGETHER_API_KEY", None)
    if not key:
        st.info("🔑 Add your Together.ai API key to get AI-generated suggestions.")
        return

    st.subheader("🤖 AI SEO Suggestions")
    prompt = f"Suggest SEO improvements for this HTML:\n\n{html_content[:4000]}"
    headers = {"Authorization": f"Bearer {key}"}
    data = {
        "model": "togethercomputer/llama-2-70b-chat",
        "prompt": prompt,
        "max_tokens": 500
    }

    try:
        res = requests.post("https://api.together.xyz/v1/completions", json=data, headers=headers)
        if res.status_code == 200:
            output = res.json()["choices"][0]["text"]
            st.markdown(output)
        else:
            st.warning("Failed to get a response from Together.ai")
    except Exception as e:
        st.warning(f"Error calling Together.ai: {e}")
