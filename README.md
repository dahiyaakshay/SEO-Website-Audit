# Website Analyzer

An open-source, AI-powered website analysis tool that evaluates SEO, performance, content quality, accessibility, and more. Built with Streamlit and Together.ai.

# Features
- SEO Analysis: Meta tags, headings, keywords, and content structure
- Performance Analysis: Loading speed, resource usage, Core Web Vitals metrics
- Content Quality: Readability, engagement, formatting, and structure
- Accessibility: WCAG compliance checks and accessibility best practices
- Security: Basic security headers and vulnerability checks
- Design & UX: Visual hierarchy, consistency, and usability analysis
- AI-Powered Recommendations: Smart suggestions using Together.ai LLMs

# Getting Started
-> Prerequisites
- Python 3.8 or higher
- Git

# Installation
1. Clone the repository:
   git clone https://github.com/yourusername/website-analyzer.git
   cd website-analyzer

2. Create a virtual environment:
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install the required dependencies:
   pip install -r requirements.txt

4. Create a .env file in the project root directory:
   TOGETHER_API_KEY=your_together_ai_api_key
   PAGESPEED_API_KEY=your_google_pagespeed_api_key  # Optional

# Running the Application

Start the Streamlit application:

streamlit run app.py

The application will be available at http://localhost:8501 in your web browser.

# Usage
- Enter the URL of the website you want to analyze
- Select the types of analysis you want to perform
- Click "Analyze Website" to start the analysis
- View the results and recommendations across different categories
- Download a detailed report for sharing or reference

# Deployment Options
-> Streamlit Cloud

The easiest way to deploy this app is using Streamlit Cloud:
- Push your code to a GitHub repository
- Sign up for Streamlit Cloud
- Create a new app pointing to your repository
- Add the required secrets (API keys) in the Streamlit Cloud dashboard

# Heroku
To deploy to Heroku:

1. Create a Procfile with:
- web: streamlit run app.py

2. Initialize a Heroku app:
- heroku create your-app-name

3. Set the environment variables:
- heroku config:set TOGETHER_API_KEY=your_together_ai_api_key
  heroku config:set PAGESPEED_API_KEY=your_google_pagespeed_api_key  # Optional

4. Deploy your application:
- git push heroku main


# Project Structure

project_root/

├── app.py     # Main Streamlit application

├── requirements.txt  # Dependencies

├── README.md         # Documentation

├── .gitignore                # Git ignore file

├── analyzers/

│   ├── __init__.py

│   ├── seo_analyzer.py       # SEO analysis module

│   ├── performance_analyzer.py  # Performance analysis

│   ├── content_analyzer.py   # Content quality analysis

│   ├── accessibility_analyzer.py  # Accessibility checks

│   ├── security_analyzer.py  # Security analysis

│   └── design_analyzer.py    # Design and UX analysis

├── utils/

│   ├── __init__.py

│   ├── scraper.py            # Web scraping utilities

│   ├── ai_integration.py     # AI model integration

│   └── report_generator.py   # Report formatting and generation

└── tests/

    ├── __init__.py

    └── test_analyzers.py     # Unit tests



# Extending the Project

-> Adding New Analyzers

1. Create a new file in the analyzers directory (e.g., new_analyzer.py)
2. Implement the analyzer class with an analyze() method that returns findings and recommendations
3. Import and integrate the analyzer in app.py

# Customizing the UI

The UI is built with Streamlit, making it easy to customize:
1. Modify the app.py file to change the layout, inputs, or visualization components
2. Add new tabs, charts, or interactive elements using Streamlit's components
3. Customize the styling using Streamlit's theming capabilities

# API Integration
-> Together.ai Integration

The tool uses Together.ai's large language models for content analysis. You can customize the model used by modifying the ContentAnalyzer class in analyzers/content_analyzer.py.

# Google PageSpeed Insights API
For detailed performance analysis, the tool can use the Google PageSpeed Insights API. This is optional but provides more accurate metrics.

# Contributing
-> Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (git checkout -b feature/amazing-feature)
3. Commit your changes (git commit -m 'Add some amazing feature')
4. Push to the branch (git push origin feature/amazing-feature)
5. Open a Pull Request

# License
This project is licensed under the MIT License - see the LICENSE file for details.

# Acknowledgements

- Streamlit - The web framework used
- Together.ai - AI model provider
- BeautifulSoup - HTML parsing library
- PageSpeed Insights - Performance metrics


