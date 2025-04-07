import json
import time
import markdown
from jinja2 import Template
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generates detailed reports from analysis results"""
    
    def __init__(self, results, detailed=False, ai_enabled=False, together_api_key=None):
        """
        Initialize the report generator
        
        Args:
            results (dict): Analysis results from various analyzers
            detailed (bool): Whether to generate a detailed report
            ai_enabled (bool): Whether to use AI for report enhancement
            together_api_key (str, optional): Together.ai API key for AI summaries
        """
        self.results = results
        self.detailed = detailed
        self.ai_enabled = ai_enabled
        self.together_api_key = together_api_key
        self.timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    
    def generate(self):
        """
        Generate a report from the analysis results
        
        Returns:
            dict: Report data with summary and recommendations
        """
        # Generate summary
        summary = self._generate_summary()
        
        # Extract top recommendations
        top_recommendations = self._extract_top_recommendations()
        
        # Prioritize AI recommendations if available
        if self.ai_enabled and "AI Insights" in self.results:
            ai_recommendations = self.results["AI Insights"].get("recommendations", [])
            if ai_recommendations:
                # Combine AI recommendations with other high priority recommendations
                ai_recs = [{"category": "AI Insights", "priority": rec["priority"], 
                            "title": rec["title"],
                            "recommendation": rec["description"]} 
                           for rec in ai_recommendations if rec["priority"] == "High"]
                
                other_top_recs = [rec for rec in top_recommendations if rec["category"] != "AI Insights"]
                
                # Ensure we have a good mix of AI and standard recommendations
                combined_recs = ai_recs[:3] + other_top_recs[:2]
                top_recommendations = combined_recs
        
        report = {
            "summary": summary,
            "top_recommendations": top_recommendations,
            "timestamp": self.timestamp
        }
        
        # Generate detailed HTML report if requested
        if self.detailed:
            detailed_html = self._generate_detailed_html()
            report["detailed_report"] = detailed_html
        
        return report
    
    def _generate_summary(self):
        """Generate a summary of the analysis results"""
        # If AI Insights has its own summary, use that instead
        if self.ai_enabled and "AI Insights" in self.results:
            ai_summary = self.results["AI Insights"].get("summary", None)
            if ai_summary:
                return ai_summary
        
        # Calculate overall scores
        overall_scores = {}
        for category, data in self.results.items():
            overall_scores[category] = data.get("score", 0)
        
        # Calculate average score
        avg_score = sum(overall_scores.values()) / len(overall_scores) if overall_scores else 0
        
        # Count issues by severity
        errors = 0
        warnings = 0
        successes = 0
        
        for category, data in self.results.items():
            findings = data.get("findings", {})
            for section in findings.values():
                for item in section:
                    if item.get("type") == "error":
                        errors += 1
                    elif item.get("type") == "warning":
                        warnings += 1
                    elif item.get("type") == "success":
                        successes += 1
        
        # Generate summary text
        if self.ai_enabled and self.together_api_key:
            return self._generate_ai_summary(overall_scores, avg_score, errors, warnings, successes)
        else:
            return self._generate_standard_summary(overall_scores, avg_score, errors, warnings, successes)
    
    def _generate_standard_summary(self, overall_scores, avg_score, errors, warnings, successes):
        """Generate a standard text summary without AI"""
        
        # Determine overall assessment
        if avg_score >= 80:
            assessment = "excellent"
        elif avg_score >= 70:
            assessment = "good"
        elif avg_score >= 50:
            assessment = "fair"
        else:
            assessment = "poor"
        
        # Generate summary text
        summary = f"## Website Analysis Summary\n\n"
        summary += f"Overall score: **{avg_score:.0f}/100** ({assessment})\n\n"
        
        # Add category scores
        summary += "### Category Scores\n\n"
        for category, score in overall_scores.items():
            summary += f"- **{category}**: {score}/100\n"
        
        summary += f"\n### Issues Found\n\n"
        summary += f"- {errors} critical issues requiring attention\n"
        summary += f"- {warnings} warnings that could be improved\n"
        summary += f"- {successes} checks passed successfully\n\n"
        
        # Highlight best and worst areas
        if overall_scores:
            best_category = max(overall_scores.items(), key=lambda x: x[1])[0]
            worst_category = min(overall_scores.items(), key=lambda x: x[1])[0]
            
            summary += f"Your website performs best in **{best_category}** and needs the most improvement in **{worst_category}**.\n\n"
        
        # Add next steps
        summary += "### Next Steps\n\n"
        summary += "1. Address critical issues first to improve user experience\n"
        summary += "2. Work through warnings to enhance overall performance\n"
        summary += "3. Focus on the lowest-scoring categories for greatest impact\n"
        
        return summary
    
    def _generate_ai_summary(self, overall_scores, avg_score, errors, warnings, successes):
        """Generate an AI-enhanced summary using Together.ai"""
        try:
            # Extract key findings from each category for better AI context
            key_findings = self._extract_key_findings_for_ai()
            
            # Prepare data for AI
            context = {
                "overall_score": f"{avg_score:.0f}",
                "category_scores": overall_scores,
                "errors": errors,
                "warnings": warnings,
                "successes": successes,
                "key_findings": key_findings
            }
            
            # Best and worst categories
            if overall_scores:
                context["best_category"] = max(overall_scores.items(), key=lambda x: x[1])[0]
                context["worst_category"] = min(overall_scores.items(), key=lambda x: x[1])[0]
            
            # Create a prompt for the AI
            prompt = f"""
            You are an expert website analyst. Based on the following analysis results, write a professional, helpful summary of the findings.
            
            Analysis data:
            {json.dumps(context, indent=2)}
            
            Write a concise but informative website analysis summary. Include:
            1. A headline assessment of the overall score
            2. Brief explanation of what each score category represents
            3. Highlight of strengths and weaknesses
            4. A general next steps section with 3 prioritized recommendations
            
            Format the response in Markdown with appropriate headers and emphasis.
            """
            
            # Log that we're making an API call
            logger.info("Making API call to Together.ai for AI summary generation")
            
            # Call Together.ai API with improved error handling
            try:
                response = requests.post(
                    "https://api.together.xyz/v1/completions",
                    headers={
                        "Authorization": f"Bearer {self.together_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "meta-llama-3-8b-instruct",
                        "prompt": prompt,
                        "max_tokens": 800,
                        "temperature": 0.3
                    },
                    timeout=60  # Increase timeout to 60 seconds
                )
                
                # Log the API response status code
                logger.info(f"Together.ai API response status code: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    ai_text = result.get("choices", [{}])[0].get("text", "")
                    if ai_text:
                        logger.info("Successfully generated AI summary")
                        return ai_text
                    else:
                        logger.warning("API returned 200 but no text in the response")
                else:
                    # Log the error response
                    logger.error(f"API error: {response.text}")
            except requests.exceptions.RequestException as e:
                logger.error(f"Request exception during API call: {str(e)}")
            
            # Fallback to standard summary if API call fails
            logger.warning("Falling back to standard summary generation")
            return self._generate_standard_summary(overall_scores, avg_score, errors, warnings, successes)
            
        except Exception as e:
            logger.error(f"Error generating AI summary: {str(e)}")
            return self._generate_standard_summary(overall_scores, avg_score, errors, warnings, successes)
    
    def _extract_key_findings_for_ai(self):
        """Extract important findings to include in AI context"""
        key_findings = []
        
        for category, data in self.results.items():
            findings = data.get("findings", {})
            for section, items in findings.items():
                for item in items:
                    if item.get("type") in ["error", "warning"]:
                        key_findings.append({
                            "category": category,
                            "section": section,
                            "type": item.get("type"),
                            "title": item.get("title"),
                            "description": item.get("description")
                        })
                        
                        # Limit to most important findings to avoid token limits
                        if len(key_findings) >= 15:
                            break
        
        # Sort by importance (errors first)
        return sorted(key_findings, key=lambda x: 0 if x["type"] == "error" else 1)
    
    def _extract_top_recommendations(self):
        """Extract and prioritize top recommendations from all categories"""
        all_recommendations = []
        
        # Collect all recommendations
        for category, data in self.results.items():
            recommendations = data.get("recommendations", [])
            for rec in recommendations:
                all_recommendations.append({
                    "category": category,
                    "priority": rec.get("priority", "Medium"),
                    "title": rec.get("title", ""),
                    "recommendation": rec.get("description", "")
                })
        
        # Sort by priority (High > Medium > Low)
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        sorted_recommendations = sorted(
            all_recommendations, 
            key=lambda x: priority_order.get(x.get("priority"), 3)
        )
        
        # Return top 5 recommendations
        return sorted_recommendations[:5]
    
    def _generate_detailed_html(self):
        """Generate a detailed HTML report"""
        # HTML template for the report
        template_str = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Website Analysis Report</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }
                .header {
                    text-align: center;
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 1px solid #eee;
                }
                .summary {
                    margin-bottom: 30px;
                    padding: 20px;
                    background-color: #f9f9f9;
                    border-radius: 5px;
                }
                .score-card {
                    display: flex;
                    justify-content: space-between;
                    flex-wrap: wrap;
                    margin-bottom: 30px;
                }
                .score-item {
                    width: 30%;
                    min-width: 200px;
                    margin-bottom: 20px;
                    padding: 15px;
                    border-radius: 5px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }
                .score-item h3 {
                    margin-top: 0;
                }
                .recommendations {
                    margin-bottom: 30px;
                }
                .recommendation {
                    margin-bottom: 15px;
                    padding: 15px;
                    border-left: 4px solid #4CAF50;
                    background-color: #f9f9f9;
                }
                .high-priority {
                    border-left-color: #f44336;
                }
                .medium-priority {
                    border-left-color: #FFC107;
                }
                .category-section {
                    margin-bottom: 40px;
                }
                .finding {
                    margin-bottom: 15px;
                    padding: 15px;
                    border-radius: 5px;
                    background-color: #f9f9f9;
                }
                .finding-success {
                    border-left: 4px solid #4CAF50;
                }
                .finding-warning {
                    border-left: 4px solid #FFC107;
                }
                .finding-error {
                    border-left: 4px solid #f44336;
                }
                .footer {
                    text-align: center;
                    margin-top: 50px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    font-size: 0.8em;
                    color: #999;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Website Analysis Report</h1>
                <p>Generated on {{ timestamp }}</p>
            </div>
            
            <div class="summary">
                {{ summary_html | safe }}
            </div>
            
            <h2>Overall Scores</h2>
            <div class="score-card">
                {% for category, data in results.items() %}
                <div class="score-item">
                    <h3>{{ category }}</h3>
                    <div class="score">{{ data.score }}/100</div>
                </div>
                {% endfor %}
            </div>
            
            <h2>Top Recommendations</h2>
            <div class="recommendations">
                {% for rec in top_recommendations %}
                <div class="recommendation {{ rec.priority | lower }}-priority">
                    <h3>{{ rec.title }}</h3>
                    <p><strong>Category:</strong> {{ rec.category }}</p>
                    <p><strong>Priority:</strong> {{ rec.priority }}</p>
                    <p>{{ rec.recommendation }}</p>
                </div>
                {% endfor %}
            </div>
            
            <h2>Detailed Findings</h2>
            {% for category, data in results.items() %}
            <div class="category-section">
                <h2>{{ category }} Analysis</h2>
                
                {% for section, items in data.findings.items() %}
                <h3>{{ section }}</h3>
                
                {% for item in items %}
                <div class="finding finding-{{ item.type }}">
                    <h4>{{ item.title }}</h4>
                    <p>{{ item.description }}</p>
                    {% if item.details %}
                    <pre>{{ item.details }}</pre>
                    {% endif %}
                </div>
                {% endfor %}
                
                {% endfor %}
            </div>
            {% endfor %}
            
            <div class="footer">
                <p>Generated by Website Analyzer - A Web Gremlin Alternative</p>
            </div>
        </body>
        </html>
        """
        
        # Create template and render
        template = Template(template_str)
        
        # Convert markdown summary to HTML
        summary_html = markdown.markdown(self._generate_summary())
        
        # Render the template
        html_report = template.render(
            results=self.results,
            summary_html=summary_html,
            top_recommendations=self._extract_top_recommendations(),
            timestamp=self.timestamp
        )
        
        return html_report
