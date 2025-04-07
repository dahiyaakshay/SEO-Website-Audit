import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import validators
from PIL import Image
import io
import base64

# Import analyzers
from analyzers.seo_analyzer import SEOAnalyzer
from analyzers.performance_analyzer import PerformanceAnalyzer
from analyzers.content_analyzer import ContentAnalyzer
from analyzers.accessibility_analyzer import AccessibilityAnalyzer
from analyzers.security_analyzer import SecurityAnalyzer
from analyzers.design_analyzer import DesignAnalyzer
from analyzers.ai_analysis import AIAnalyzer  # Import the new AI analyzer

# Import utils
from utils.scraper import WebScraper
from utils.report_generator import ReportGenerator

# Set page configuration
st.set_page_config(
    page_title="Website Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Page header
    st.title("🔍 Website Analyzer")
    st.markdown("Analyze and improve your website's SEO, performance, content, and more.")
    
    # Sidebar for inputs and controls
    with st.sidebar:
        st.header("Analysis Configuration")
        url = st.text_input("Enter website URL:", placeholder="https://example.com")
        
        # Analysis options
        st.subheader("Analysis Options")
        analyze_seo = st.checkbox("SEO Analysis", value=True)
        analyze_performance = st.checkbox("Performance Analysis", value=True)
        analyze_content = st.checkbox("Content Analysis", value=True)
        analyze_accessibility = st.checkbox("Accessibility Analysis", value=True)
        analyze_security = st.checkbox("Security Analysis", value=True)
        analyze_design = st.checkbox("Design & UX Analysis", value=True)
        
        # Additional options
        st.subheader("Additional Options")
        detailed_report = st.checkbox("Generate Detailed Report", value=False)
        ai_suggestions = st.checkbox("AI-Powered Recommendations", value=True)
        
        # API Keys section
        st.subheader("API Configuration (Optional)")
        with st.expander("Configure API Keys"):
            st.markdown("""
            **Together.ai API Key**: Enables AI-powered content analysis and personalized recommendations.
            **Google PageSpeed API Key**: Provides detailed performance metrics and optimization suggestions.
            
            Both API keys are optional. The tool will use basic analysis methods if keys are not provided.
            """)
            together_api_key = st.text_input("Together.ai API Key:", type="password", help="Enables AI-powered recommendations")
            pagespeed_api_key = st.text_input("Google PageSpeed API Key:", type="password", help="Enhances performance analysis")
            
        # Run analysis button
        analyze_button = st.button("Analyze Website", type="primary")
    
    # Main content area
    if not url:
        # Show introduction when no URL is entered
        display_intro()
    elif analyze_button:
        if not validators.url(url):
            st.error("Please enter a valid URL including http:// or https://")
        else:
            run_analysis(
                url, 
                analyze_seo, 
                analyze_performance,
                analyze_content,
                analyze_accessibility,
                analyze_security,
                analyze_design,
                detailed_report,
                ai_suggestions,
                together_api_key,
                pagespeed_api_key
            )

def display_intro():
    """Display introduction content when no analysis is running"""
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("""
        ## Improve Your Website with AI-Powered Analysis
        
        This tool helps you identify issues and opportunities across:
        
        - **SEO**: Meta tags, headings, keywords, and more
        - **Performance**: Loading time, resource usage, and optimizations
        - **Content Quality**: Readability, engagement, and structure
        - **Accessibility**: WCAG compliance and inclusive design
        - **Security**: Basic security headers and vulnerabilities
        - **Design & UX**: Visual hierarchy, consistency, and usability
        
        ### How to use
        1. Enter your website URL in the sidebar
        2. Select the aspects you want to analyze
        3. Click "Analyze Website" to get started
        """)
    
    with col2:
        st.image("https://via.placeholder.com/400x300?text=Website+Analyzer", use_column_width=True)
    
    # Feature comparison
    st.markdown("### Feature Comparison")
    comparison_data = {
        "Feature": ["SEO Analysis", "Performance Metrics", "Content Quality", "Accessibility", "Security Checks", "Design & UX", "AI Recommendations", "Cost"],
        "This Tool": ["✓", "✓", "✓", "✓", "✓", "✓", "✓", "Free & Open Source"],
        "Commercial Tools": ["✓", "✓", "✓", "✓", "Limited", "Limited", "Limited", "$20-100/month"]
    }
    
    st.table(pd.DataFrame(comparison_data))

def run_analysis(url, analyze_seo, analyze_performance, analyze_content, 
                analyze_accessibility, analyze_security, analyze_design,
                detailed_report, ai_suggestions, together_api_key, pagespeed_api_key):
    """Run the selected analyses on the given URL"""
    
    # Setup progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    results_container = st.container()
    
    try:
        # Initialize scraper
        status_text.text("Initializing web scraper...")
        scraper = WebScraper(url)
        page_content = scraper.scrape()
        progress_bar.progress(10)
        
        # Run selected analyses
        results = {}
        analyzers_to_run = []
        
        # Add enabled analyzers to the list
        if analyze_seo:
            analyzers_to_run.append(("SEO", SEOAnalyzer(page_content, url)))
        if analyze_performance:
            # Use the updated PerformanceAnalyzer with PageSpeed API support
            analyzers_to_run.append(("Performance", PerformanceAnalyzer(url, api_key=pagespeed_api_key)))
        if analyze_content:
            analyzers_to_run.append(("Content", ContentAnalyzer(page_content)))
        if analyze_accessibility:
            analyzers_to_run.append(("Accessibility", AccessibilityAnalyzer(page_content)))
        if analyze_security:
            analyzers_to_run.append(("Security", SecurityAnalyzer(url)))
        if analyze_design:
            analyzers_to_run.append(("Design & UX", DesignAnalyzer(page_content, url)))
        
        # Add AI analyzer if AI suggestions are enabled
        if ai_suggestions:
            analyzers_to_run.append(("AI Insights", AIAnalyzer(page_content, url, together_api_key=together_api_key)))
        
        # Run each analyzer
        progress_increment = 80 / len(analyzers_to_run) if analyzers_to_run else 0
        current_progress = 10
        
        for name, analyzer in analyzers_to_run:
            status_text.text(f"Analyzing {name.lower()}...")
            results[name] = analyzer.analyze()
            current_progress += progress_increment
            progress_bar.progress(int(current_progress))
            time.sleep(0.5)  # Add small delay for visual effect
        
        # Generate report
        status_text.text("Generating report...")
        report_generator = ReportGenerator(results, detailed=detailed_report, ai_enabled=ai_suggestions, together_api_key=together_api_key)
        report = report_generator.generate()
        progress_bar.progress(95)
        
        # Display results
        status_text.text("Analysis complete!")
        display_results(url, results, report)
        progress_bar.progress(100)
        
    except Exception as e:
        st.error(f"An error occurred during analysis: {str(e)}")
        # Display a more detailed error message for debugging
        import traceback
        st.text("Detailed error information:")
        st.code(traceback.format_exc())
        st.info("Please check the URL and try again, or report this issue.")
    finally:
        # Clean up progress indicators
        progress_bar.empty()
        status_text.empty()

def display_results(url, results, report):
    """Display the analysis results in the Streamlit interface"""
    
    st.header(f"Analysis Results for {url}")
    
    # Overall score
    overall_score = calculate_overall_score(results)
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.metric("Overall Score", f"{overall_score}/100")
        
    with col2:
        if overall_score >= 80:
            st.success("Excellent! Your website is performing well in most areas.")
        elif overall_score >= 60:
            st.warning("Good, but there's room for improvement in several areas.")
        else:
            st.error("Your website needs significant improvements in multiple areas.")
    
    # Create tabs for different analysis categories
    tabs = st.tabs(list(results.keys()) + ["Summary"])
    
    # Fill each tab with its respective analysis results
    for i, category in enumerate(results.keys()):
        with tabs[i]:
            try:
                # Display category score
                st.subheader(f"{category} Score: {results[category]['score']}/100")
                
                # Special handling for AI Insights if available
                if category == "AI Insights" and "summary" in results[category]:
                    st.markdown("### AI Summary")
                    st.markdown(results[category].get("summary", ""))
                
                # Display findings
                st.markdown("### Key Findings")
                display_findings(results[category]['findings'])
                
                # Display recommendations
                st.markdown("### Recommendations")
                display_recommendations(results[category]['recommendations'])
            except Exception as e:
                st.error(f"Error displaying {category} results: {str(e)}")
    
    # Summary tab
    with tabs[-1]:
        st.markdown("## Analysis Summary")
        st.markdown(report['summary'])
        
        # Display top recommendations
        st.markdown("### Top Priority Recommendations")
        for rec in report['top_recommendations']:
            try:
                st.markdown(f"- **{rec['category']}**: {rec['recommendation']}")
            except Exception as e:
                st.error(f"Error displaying recommendation: {str(e)}")
        
        # Download detailed report
        if 'detailed_report' in report:
            report_html = report['detailed_report']
            b64 = base64.b64encode(report_html.encode()).decode()
            st.download_button(
                label="Download Detailed Report (HTML)",
                data=report_html,
                file_name=f"website_analysis_report_{int(time.time())}.html",
                mime="text/html"
            )

def display_findings(findings):
    """Display findings in a structured format"""
    for category, items in findings.items():
        with st.expander(f"{category} ({len(items)} items)"):
            for item in items:
                try:
                    # Ensure item['type'] is a string
                    item_type = item.get('type', '')
                    if isinstance(item_type, dict):
                        # If it's a dictionary, use a default type
                        item_type = 'warning'
                    elif not isinstance(item_type, str):
                        # Convert to string if it's another non-string type
                        item_type = str(item_type)
                    
                    if item_type == 'success':
                        st.markdown(f"✅ **{item['title']}**")
                    elif item_type == 'warning':
                        st.markdown(f"⚠️ **{item['title']}**")
                    elif item_type == 'error':
                        st.markdown(f"❌ **{item['title']}**")
                    else:
                        # Default case for unknown types
                        st.markdown(f"ℹ️ **{item['title']}**")
                    
                    st.markdown(f"{item['description']}")
                    if 'details' in item and item['details']:
                        st.code(item['details'])
                    st.markdown("---")
                except Exception as e:
                    st.error(f"Error displaying finding: {str(e)}")
                    st.markdown("---")

def display_recommendations(recommendations):
    """Display recommendations with priority levels"""
    try:
        for priority in ['High', 'Medium', 'Low']:
            # Add type checking for the priority field
            priority_recs = []
            for r in recommendations:
                rec_priority = r.get('priority', '')
                # Handle if priority is not a string
                if isinstance(rec_priority, dict):
                    rec_priority = 'Medium'  # Default if it's a dictionary
                elif not isinstance(rec_priority, str):
                    rec_priority = str(rec_priority)
                
                if rec_priority == priority:
                    priority_recs.append(r)
            
            if priority_recs:
                st.markdown(f"#### {priority} Priority")
                for rec in priority_recs:
                    try:
                        title = rec.get('title', 'Recommendation')
                        description = rec.get('description', '')
                        
                        if isinstance(description, dict):
                            # If description is a dictionary, try to extract useful information
                            description = str(description)
                        
                        st.markdown(f"- **{title}**: {description}")
                        
                        if 'example' in rec and rec['example']:
                            if isinstance(rec['example'], dict):
                                st.code(str(rec['example']))
                            else:
                                st.code(rec['example'])
                    except Exception as e:
                        st.error(f"Error displaying recommendation: {str(e)}")
    except Exception as e:
        st.error(f"Error in recommendations display: {str(e)}")

def calculate_overall_score(results):
    """Calculate the overall score based on individual category scores"""
    if not results:
        return 0
        
    # Assign weights to different categories
    weights = {
        "SEO": 0.2,
        "Performance": 0.2,
        "Content": 0.2,
        "Accessibility": 0.15,
        "Security": 0.15,
        "Design & UX": 0.1,
        "AI Insights": 0.0  # Initially zero weight
    }
    
    # If AI Insights are available, redistribute weights
    if "AI Insights" in results:
        weights["AI Insights"] = 0.1
        # Adjust other weights proportionally
        for key in weights:
            if key != "AI Insights":
                weights[key] = weights[key] * 0.9
    
    # Calculate weighted average
    total_weight = sum(weights.get(category, 0) for category in results.keys())
    if total_weight == 0:
        return 0
        
    weighted_sum = sum(
        results[category]['score'] * weights.get(category, 0) 
        for category in results.keys()
    )
    
    return round(weighted_sum / total_weight)

if __name__ == "__main__":
    main()
