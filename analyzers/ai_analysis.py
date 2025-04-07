import os
import pandas as pd
import openai
from time import sleep
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AIAnalyzer:
    def __init__(self):
        # Initialize OpenAI API key from environment variables
        self.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.api_key

    def analyze_seo_with_ai(self, data):
        """
        Use OpenAI's GPT to analyze SEO data and provide recommendations.
        
        Args:
            data: Dictionary containing scraped website data and analysis results
            
        Returns:
            Dictionary containing AI-generated SEO analysis and recommendations
        """
        try:
            # Extract relevant data for AI analysis
            page_title = data.get("meta_tags", {}).get("title", "")
            meta_description = data.get("meta_tags", {}).get("description", "")
            headings = data.get("headings", {})
            content_length = data.get("content_length", 0)
            keyword_density = data.get("keyword_density", {})
            
            # Extract top 5 keywords by density
            top_keywords = dict(sorted(keyword_density.items(), key=lambda x: x[1], reverse=True)[:5])
            
            # Create prompt for GPT
            prompt = f"""
            You are an expert SEO consultant. Analyze the following website data and provide actionable recommendations:
            
            Page Title: {page_title}
            Meta Description: {meta_description}
            Content Length: {content_length} characters
            
            Headings Structure:
            {self._format_headings_for_prompt(headings)}
            
            Top Keywords by Density:
            {self._format_keywords_for_prompt(top_keywords)}
            
            Provide a comprehensive SEO analysis with the following sections:
            1. Title & Meta Description Analysis
            2. Content Quality Assessment
            3. Heading Structure Evaluation
            4. Keyword Usage Analysis
            5. Top 3 Most Important Recommendations
            
            Focus on actionable insights that would improve search rankings.
            """
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert SEO consultant providing website analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1500
            )
            
            # Extract and process the response
            ai_analysis = response.choices[0].message.content
            
            # Structure the results
            analysis_sections = self._parse_ai_response(ai_analysis)
            
            return {
                "ai_seo_analysis": analysis_sections,
                "raw_analysis": ai_analysis
            }
            
        except Exception as e:
            print(f"Error in AI SEO analysis: {str(e)}")
            return {
                "ai_seo_analysis": {
                    "error": f"Failed to complete AI analysis: {str(e)}",
                    "sections": {}
                },
                "raw_analysis": ""
            }
    
    def _format_headings_for_prompt(self, headings):
        """Format headings data for inclusion in the prompt."""
        result = []
        for level, heading_list in headings.items():
            if heading_list:
                result.append(f"{level}: {' | '.join(heading_list)}")
        return "\n".join(result) if result else "No headings found"
    
    def _format_keywords_for_prompt(self, keywords):
        """Format keyword density data for inclusion in the prompt."""
        result = []
        for keyword, density in keywords.items():
            result.append(f"'{keyword}': {density:.2%}")
        return "\n".join(result) if result else "No significant keywords found"
    
    def _parse_ai_response(self, response_text):
        """Parse the AI response into structured sections."""
        # Define the sections we expect
        sections = {
            "title_meta_analysis": "",
            "content_quality": "",
            "heading_structure": "",
            "keyword_usage": "",
            "top_recommendations": ""
        }
        
        # Simple pattern matching to identify sections
        current_section = None
        lines = response_text.split("\n")
        
        for line in lines:
            # Check if this line starts a new section
            lower_line = line.lower()
            
            if "title" in lower_line and "meta" in lower_line and "description" in lower_line:
                current_section = "title_meta_analysis"
                sections[current_section] += line + "\n"
            elif "content" in lower_line and "quality" in lower_line:
                current_section = "content_quality"
                sections[current_section] += line + "\n"
            elif "heading" in lower_line and "structure" in lower_line:
                current_section = "heading_structure"
                sections[current_section] += line + "\n"
            elif "keyword" in lower_line and "usage" in lower_line:
                current_section = "keyword_usage"
                sections[current_section] += line + "\n"
            elif "recommendation" in lower_line or "important" in lower_line:
                current_section = "top_recommendations"
                sections[current_section] += line + "\n"
            elif current_section:  # If we're in a section, add the line to it
                sections[current_section] += line + "\n"
        
        # Clean up any trailing newlines
        for section in sections:
            sections[section] = sections[section].strip()
            
        return sections
