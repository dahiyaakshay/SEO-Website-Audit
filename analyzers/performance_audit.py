import streamlit as st
import requests

def run_performance_audit(url):
    key = st.secrets.get("PAGESPEED_API_KEY", None)
    if not key:
        st.info("🔑 Add your Google PageSpeed API key to get performance analysis.")
        return

    st.subheader("🚀 PageSpeed Performance Insights")
    try:
        response = requests.get(
            f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&key={key}&strategy=desktop"
        )
        data = response.json()

        perf_score = data['lighthouseResult']['categories']['performance']['score'] * 100
        accessibility = data['lighthouseResult']['categories']['accessibility']['score'] * 100
        best_practices = data['lighthouseResult']['categories']['best-practices']['score'] * 100
        seo_score = data['lighthouseResult']['categories']['seo']['score'] * 100

        st.metric("Performance Score", f"{perf_score}")
        st.metric("Accessibility", f"{accessibility}")
        st.metric("Best Practices", f"{best_practices}")
        st.metric("SEO Score (PageSpeed)", f"{seo_score}")

    except Exception as e:
        st.warning(f"Error fetching PageSpeed data: {e}")
