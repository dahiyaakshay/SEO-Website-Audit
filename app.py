import os
import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from analyzers.meta_tags import MetaTagsAnalyzer
from analyzers.headings import HeadingsAnalyzer
from analyzers.image_alt import ImageAltAnalyzer
from analyzers.link_analysis import LinkAnalysis
from analyzers.structured_data import StructuredDataAnalyzer
from analyzers.mobile_friendly import MobileFriendlyAnalyzer
from analyzers.page_speed import PageSpeedAnalyzer
from analyzers.security import SecurityAnalyzer
from analyzers.accessibility import AccessibilityAnalyzer
from analyzers.keyword_density import KeywordDensityAnalyzer
from analyzers.performance_audit import PerformanceAudit
from analyzers.ai_recommendations import AIRecommendations


def fetch_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        st.error(f"Error fetching page: {e}")
        return None


def run_analysis(url, options, pagespeed_api_key=None, together_api_key=None):
    html_content = fetch_page(url)
    if not html_content:
        return

    page_content = html_content
    soup = BeautifulSoup(html_content, 'html.parser')

    st.subheader("Audit Summary")
    scores = []

    analyzers_to_run = []

    if options["Meta Tags"]:
        analyzers_to_run.append(("Meta Tags", MetaTagsAnalyzer(soup)))
    if options["Headings"]:
        analyzers_to_run.append(("Headings", HeadingsAnalyzer(soup)))
    if options["Image ALT Attributes"]:
        analyzers_to_run.append(("Image ALT Attributes", ImageAltAnalyzer(soup)))
    if options["Link Analysis"]:
        analyzers_to_run.append(("Link Analysis", LinkAnalysis(soup)))
    if options["Structured Data"]:
        analyzers_to_run.append(("Structured Data", StructuredDataAnalyzer(soup)))
    if options["Mobile Friendly"]:
        analyzers_to_run.append(("Mobile Friendly", MobileFriendlyAnalyzer(soup)))
    if options["Page Speed"]:
        analyzers_to_run.append(("Page Speed", PageSpeedAnalyzer(url)))
    if options["Security"]:
        analyzers_to_run.append(("Security", SecurityAnalyzer(url)))
    if options["Accessibility"]:
        analyzers_to_run.append(("Accessibility", AccessibilityAnalyzer(soup)))
    if options["Keyword Density"]:
        analyzers_to_run.append(("Keyword Density", KeywordDensityAnalyzer(soup)))

    if pagespeed_api_key and options.get("Performance Audit"):
        analyzers_to_run.append(("PageSpeed UX", PerformanceAudit(url, api_key=pagespeed_api_key)))

    if together_api_key and options.get("AI Suggestions"):
        analyzers_to_run.append(("AI Suggestions", AIRecommendations(page_content, together_api_key)))

    tabs = st.tabs([name for name, _ in analyzers_to_run])
    for i, (name, analyzer) in enumerate(analyzers_to_run):
        with tabs[i]:
            result = analyzer.analyze() if hasattr(analyzer, 'analyze') else analyzer.get_recommendations()
            scores.append(result["score"])
            st.write("### Score:", result["score"])
            for section, findings in result["findings"].items():
                st.write(f"#### {section}")
                for finding in findings:
                    if finding["type"] == "error":
                        st.error(f"{finding['title']}: {finding['description']}")
                    elif finding["type"] == "warning":
                        st.warning(f"{finding['title']}: {finding['description']}")
                    elif finding["type"] == "success":
                        st.success(f"{finding['title']}: {finding['description']}")
                    else:
                        st.info(f"{finding['title']}: {finding['description']}")

    if scores:
        avg_score = sum(scores) / len(scores)
        st.metric(label="Overall SEO Health Score", value=f"{avg_score:.1f}/100")


def main():
    st.set_page_config(page_title="SEO Audit Tool", layout="wide")
    st.title("SEO Audit Tool")
    st.write("Enter a URL to analyze its SEO performance.")

    url = st.text_input("Website URL", "https://example.com")
    st.write("---")

    st.sidebar.header("Audit Options")
    audit_options = {
        "Meta Tags": st.sidebar.checkbox("Meta Tags", True),
        "Headings": st.sidebar.checkbox("Headings", True),
        "Image ALT Attributes": st.sidebar.checkbox("Image ALT Attributes", True),
        "Link Analysis": st.sidebar.checkbox("Link Analysis", True),
        "Structured Data": st.sidebar.checkbox("Structured Data", True),
        "Mobile Friendly": st.sidebar.checkbox("Mobile Friendly", True),
        "Page Speed": st.sidebar.checkbox("Page Speed", True),
        "Security": st.sidebar.checkbox("Security", True),
        "Accessibility": st.sidebar.checkbox("Accessibility", True),
        "Keyword Density": st.sidebar.checkbox("Keyword Density", False),
        "Performance Audit": st.sidebar.checkbox("PageSpeed UX (via API)", False),
        "AI Suggestions": st.sidebar.checkbox("AI SEO Suggestions", False),
    }

    pagespeed_api_key = st.sidebar.text_input("Google PageSpeed API Key", type="password")
    together_api_key = st.sidebar.text_input("Together.ai API Key", type="password")

    if st.button("Run Audit"):
        run_analysis(url, audit_options, pagespeed_api_key, together_api_key)


if __name__ == "__main__":
    main()
