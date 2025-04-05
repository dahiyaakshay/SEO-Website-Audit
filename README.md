Website Analyzer
An open-source, AI-powered website analysis tool that evaluates SEO, performance, content quality, accessibility, and more. Built with Streamlit and Together.ai.

Features

SEO Analysis: Meta tags, headings, keywords, and content structure
Performance Analysis: Loading speed, resource usage, Core Web Vitals metrics
Content Quality: Readability, engagement, formatting, and structure
Accessibility: WCAG compliance checks and accessibility best practices
Security: Basic security headers and vulnerability checks
Design & UX: Visual hierarchy, consistency, and usability analysis
AI-Powered Recommendations: Smart suggestions using Together.ai LLMs

Getting Started
Prerequisites

Python 3.8 or higher
Git

Installation

Clone the repository:
bashCopygit clone https://github.com/yourusername/website-analyzer.git
cd website-analyzer

Create a virtual environment:
bashCopypython -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install the required dependencies:
bashCopypip install -r requirements.txt

Create a .env file in the project root directory:
CopyTOGETHER_API_KEY=your_together_ai_api_key
PAGESPEED_API_KEY=your_google_pagespeed_api_key  # Optional

Note: The Together.ai API key is required for AI-powered content analysis. You can get a free API key at Together.ai.



Running the Application
Start the Streamlit application:
bashCopystreamlit run app.py
The application will be available at http://localhost:8501 in your web browser.
Usage

Enter the URL of the website you want to analyze
Select the types of analysis you want to perform
Click "Analyze Website" to start the analysis
View the results and recommendations across different categories
Download a detailed report for sharing or reference

Deployment Options
Streamlit Cloud
The easiest way to deploy this app is using Streamlit Cloud:

Push your code to a GitHub repository
Sign up for Streamlit Cloud
Create a new app pointing to your repository
Add the required secrets (API keys) in the Streamlit Cloud dashboard

Heroku
To deploy to Heroku:

Create a Procfile with:
Copyweb: streamlit run app.py

Initialize a Heroku app:
bashCopyheroku create your-app-name

Set the environment variables:
bashCopyheroku config:set TOGETHER_API_KEY=your_together_ai_api_key
heroku config:set PAGESPEED_API_KEY=your_google_pagespeed_api_key  # Optional

Deploy your application:
bashCopygit push heroku main


Project Structure
Copyproject_root/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Dependencies
├── README.md                 # Documentation
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
Extending the Project
Adding New Analyzers

Create a new file in the analyzers directory (e.g., new_analyzer.py)
Implement the analyzer class with an analyze() method that returns findings and recommendations
Import and integrate the analyzer in app.py

Customizing the UI
The UI is built with Streamlit, making it easy to customize:

Modify the app.py file to change the layout, inputs, or visualization components
Add new tabs, charts, or interactive elements using Streamlit's components
Customize the styling using Streamlit's theming capabilities

API Integration
Together.ai Integration
The tool uses Together.ai's large language models for content analysis. You can customize the model used by modifying the ContentAnalyzer class in analyzers/content_analyzer.py.
Google PageSpeed Insights API
For detailed performance analysis, the tool can use the Google PageSpeed Insights API. This is optional but provides more accurate metrics.
Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

Fork the repository
Create your feature branch (git checkout -b feature/amazing-feature)
Commit your changes (git commit -m 'Add some amazing feature')
Push to the branch (git push origin feature/amazing-feature)
Open a Pull Request

License
This project is licensed under the MIT License - see the LICENSE file for details.
Acknowledgements

Streamlit - The web framework used
Together.ai - AI model provider
BeautifulSoup - HTML parsing library
PageSpeed Insights - Performance metrics
