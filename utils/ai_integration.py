import requests
import json
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TogetherAIClient:
    """Client for interacting with Together.ai API"""
    
    def __init__(self, api_key, model="llama-3-70b-instruct"):
        """
        Initialize the Together.ai client
        
        Args:
            api_key (str): Together.ai API key
            model (str, optional): Model to use. Defaults to "llama-3-70b-instruct".
        """
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.together.xyz/v1"
        
        # Default headers for all requests
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def analyze_text(self, content, max_tokens=500, temperature=0.3, task_type="analysis"):
        """
        Analyze text content using Together.ai LLM
        
        Args:
            content (str): Text content to analyze
            max_tokens (int, optional): Maximum tokens in response
            temperature (float, optional): Temperature for generation
            task_type (str, optional): Type of analysis task
        
        Returns:
            dict or None: Analysis result or None if error occurred
        """
        # Create prompt based on task type
        if task_type == "content_quality":
            prompt = self._create_content_quality_prompt(content)
        elif task_type == "seo_recommendations":
            prompt = self._create_seo_recommendations_prompt(content)
        elif task_type == "ux_feedback":
            prompt = self._create_ux_feedback_prompt(content)
        elif task_type == "audience_analysis":
            prompt = self._create_audience_analysis_prompt(content)
        else:
            # Default general analysis
            prompt = self._create_general_analysis_prompt(content)
        
        # Call the API
        try:
            response = requests.post(
                f"{self.base_url}/completions",
                headers=self.headers,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                completion = result.get("choices", [{}])[0].get("text", "")
                
                # Try to parse JSON response if expected
                if "JSON" in prompt or "json" in prompt:
                    try:
                        # Extract the JSON part from the text
                        json_start = completion.find('{')
                        json_end = completion.rfind('}') + 1
                        
                        if json_start >= 0 and json_end > json_start:
                            json_str = completion[json_start:json_end]
                            return json.loads(json_str)
                        else:
                            return {"text": completion}
                    except json.JSONDecodeError:
                        # Return raw text if JSON parsing fails
                        return {"text": completion}
                else:
                    return {"text": completion}
            else:
                logger.error(f"API error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error calling Together.ai API: {str(e)}")
            return None
    
    def _create_general_analysis_prompt(self, content):
        """Create a general analysis prompt"""
        return f"""
        Analyze the following website content and provide insights and recommendations:
        
        {content[:2000]}
        
        Please include:
        1. Overall impression
        2. Strengths and weaknesses
        3. Key improvement opportunities
        
        Provide your analysis in a concise, professional format.
        """
    
    def _create_content_quality_prompt(self, content):
        """Create a prompt for content quality analysis"""
        return f"""
        Analyze the following website content for quality and engagement potential:
        
        {content[:2000]}
        
        Provide analysis in JSON format with the following structure:
        {{
            "clarity": "rating from 1-5 with brief explanation",
            "engagement": "rating from 1-5 with brief explanation",
            "persuasiveness": "rating from 1-5 with brief explanation",
            "readability": "rating from 1-5 with brief explanation",
            "top_3_strengths": ["strength 1", "strength 2", "strength 3"],
            "top_3_improvements": ["improvement 1", "improvement 2", "improvement 3"]
        }}
        """
    
    def _create_seo_recommendations_prompt(self, content):
        """Create a prompt for SEO recommendations"""
        return f"""
        Analyze this website content for SEO improvement opportunities:
        
        {content[:2000]}
        
        Provide specific SEO recommendations in JSON format:
        {{
            "keyword_opportunities": ["keyword 1", "keyword 2", "keyword 3"],
            "content_improvements": ["improvement 1", "improvement 2", "improvement 3"],
            "structure_recommendations": ["recommendation 1", "recommendation 2", "recommendation 3"],
            "semantic_relevance": "brief analysis of topic relevance and depth"
        }}
        """
    
    def _create_ux_feedback_prompt(self, content):
        """Create a prompt for UX feedback"""
        return f"""
        Review this website content from a user experience perspective:
        
        {content[:2000]}
        
        Provide UX analysis in JSON format:
        {{
            "clarity": "rating and brief explanation",
            "navigation": "rating and brief explanation",
            "call_to_actions": "rating and brief explanation",
            "user_flow": "rating and brief explanation",
            "priority_improvements": ["improvement 1", "improvement 2", "improvement 3"]
        }}
        """
    
    def _create_audience_analysis_prompt(self, content):
        """Create a prompt for audience analysis"""
        return f"""
        Analyze this website content to identify the likely target audience:
        
        {content[:2000]}
        
        Provide audience analysis in JSON format:
        {{
            "primary_audience": "description of likely primary audience",
            "audience_needs": ["need 1", "need 2", "need 3"],
            "engagement_strategies": ["strategy 1", "strategy 2", "strategy 3"],
            "tone_analysis": "analysis of content tone and how it matches audience",
            "recommendations": ["recommendation 1", "recommendation 2", "recommendation 3"]
        }}
        """
    
    def moderate_content(self, content):
        """
        Check content for potential issues using AI moderation
        
        Args:
            content (str): Content to moderate
        
        Returns:
            dict: Moderation results with issue flags
        """
        prompt = f"""
        Analyze the following website content for potential issues:
        
        {content[:2000]}
        
        Check for these potential issues and respond in JSON format:
        {{
            "has_offensive_language": true/false,
            "has_discriminatory_content": true/false,
            "has_misleading_claims": true/false,
            "has_privacy_issues": true/false,
            "has_accessibility_issues": true/false,
            "recommendations": ["recommendation 1", "recommendation 2"]
        }}
        """
        
        try:
            response = requests.post(
                f"{self.base_url}/completions",
                headers=self.headers,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "max_tokens": 500,
                    "temperature": 0.2
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                completion = result.get("choices", [{}])[0].get("text", "")
                
                # Extract the JSON part from the text
                json_start = completion.find('{')
                json_end = completion.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = completion[json_start:json_end]
                    try:
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        logger.error("Failed to parse JSON from moderation response")
                        return {
                            "error": "Failed to parse response",
                            "has_issues": False
                        }
            
            return {
                "error": f"API error: {response.status_code}",
                "has_issues": False
            }
        except Exception as e:
            logger.error(f"Error in content moderation: {str(e)}")
            return {
                "error": str(e),
                "has_issues": False
            }

    def suggest_improvements(self, url, screenshot_description, analysis_results):
        """
        Generate AI-powered improvement suggestions based on analysis results
        
        Args:
            url (str): URL of the analyzed website
            screenshot_description (str): Text description of website appearance
            analysis_results (dict): Combined results from various analyzers
        
        Returns:
            dict: Prioritized improvement suggestions
        """
        # Prepare a summary of analysis results
        categories = []
        issues = []
        
        for category, data in analysis_results.items():
            score = data.get("score", 0)
            categories.append(f"{category}: {score}/100")
            
            # Extract top issues
            findings = data.get("findings", {})
            for section, items in findings.items():
                for item in items:
                    if item.get("type") in ["error", "warning"]:
                        issues.append(f"{category} - {section}: {item.get('title')}")
        
        # Limit issues to top 10 for prompt size
        issues = issues[:10]
        
        prompt = f"""
        As a website optimization expert, provide prioritized recommendations for improving this website:
        
        URL: {url}
        
        Website appearance: {screenshot_description[:500]}
        
        Analysis scores:
        {', '.join(categories)}
        
        Top issues identified:
        {' - ' + 'n - '.join(issues)}
        
        Based on this information, provide:
        1. The 3-5 highest impact improvements that should be prioritized
        2. For each recommendation, explain why it matters and how to implement it
        
        Format your response as JSON:
        {{
            "priority_recommendations": [
                {{
                    "title": "Clear recommendation title",
                    "impact": "high/medium/low",
                    "why_it_matters": "Brief explanation of business impact",
                    "how_to_implement": "Specific implementation steps"
                }},
                ...
            ]
        }}
        """
        
        try:
            response = requests.post(
                f"{self.base_url}/completions",
                headers=self.headers,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "max_tokens": 800,
                    "temperature": 0.3
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                completion = result.get("choices", [{}])[0].get("text", "")
                
                # Extract the JSON part from the text
                json_start = completion.find('{')
                json_end = completion.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = completion[json_start:json_end]
                    try:
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        logger.error("Failed to parse JSON from recommendations response")
                        return {
                            "error": "Failed to parse response",
                            "priority_recommendations": []
                        }
            
            return {
                "error": f"API error: {response.status_code}",
                "priority_recommendations": []
            }
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return {
                "error": str(e),
                "priority_recommendations": []
            }
