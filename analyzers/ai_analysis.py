import requests
import logging
from bs4 import BeautifulSoup
import re
import time
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIAnalyzer:
    """Provides AI-powered analysis and recommendations for websites using Together.ai API"""
    
    def __init__(self, page_content, url, together_api_key=None):
        """
        Initialize the AI analyzer
        
        Args:
            page_content (BeautifulSoup): The parsed HTML content
            url (str): The URL being analyzed
            together_api_key (str, optional): API key for Together.ai
        """
        self.soup = page_content
        self.url = url
        self.together_api_key = together_api_key
        
    def analyze(self):
        """
        Perform AI analysis if API key is available, otherwise fall back to heuristic analysis
        
        Returns:
            dict: Analysis results with score, findings, and recommendations
        """
        if self.together_api_key:
            try:
                # Use Together.ai API for analysis
                return self._analyze_with_ai()
            except Exception as e:
                logger.error(f"Together.ai API error: {str(e)}")
                logger.info("Falling back to basic AI analysis")
                return self._analyze_basic()
        else:
            # No API key provided, use basic analysis
            return self._analyze_basic()
    
    def _analyze_with_ai(self):
        """Analyze website content using Together.ai LLM API"""
        # Extract key content from the page
        analysis_data = self._extract_page_data()
        
        # Prepare a structured prompt for the AI
        prompt = self._build_ai_prompt(analysis_data)
        
        # Call the Together.ai API
        headers = {
            "Authorization": f"Bearer {self.together_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
    "model": "meta-llama-3-70b-instruct-turbo-free",
    "prompt": prompt,
    "max_tokens": 1024,
    "temperature": 0.2,
    "top_p": 0.7
}
        
        response = requests.post(
            "https://api.together.xyz/v1/completions",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            logger.error(f"Together.ai API returned status code {response.status_code}: {response.text}")
            raise Exception(f"Together.ai API error: {response.status_code}")
        
        # Parse the AI response
        result = response.json()
        ai_analysis_text = result.get("choices", [{}])[0].get("text", "")
        
        # Process AI output into structured findings and recommendations
        return self._process_ai_output(ai_analysis_text)
    
    def _extract_page_data(self):
        """Extract relevant data from the page for AI analysis"""
        data = {
            "url": self.url,
            "title": self._get_title(),
            "meta_description": self._get_meta_description(),
            "headings": self._get_headings_structure(),
            "content_sample": self._get_content_sample(),
            "keywords": self._extract_potential_keywords(),
            "links": self._analyze_links(),
            "images": self._analyze_images(),
        }
        return data
    
    def _build_ai_prompt(self, data):
        """Build a structured prompt for the AI model"""
        prompt = f"""<instruction>
You are a professional website analyzer that provides expert SEO, content, and user experience recommendations.

Please analyze this website data and provide structured feedback with specific, actionable recommendations:

URL: {data['url']}
Page Title: {data['title']}
Meta Description: {data['meta_description']}

HEADINGS STRUCTURE:
{data['headings']}

CONTENT SAMPLE:
{data['content_sample']}

POTENTIAL KEYWORDS:
{', '.join(data['keywords'][:20])}

LINK ANALYSIS:
- Internal links: {data['links']['internal']}
- External links: {data['links']['external']}
- Social media links: {data['links']['social']}

IMAGE ANALYSIS:
- Total images: {data['images']['count']}
- Images with alt text: {data['images']['with_alt']}
- Images without alt text: {data['images']['without_alt']}

ANALYSIS INSTRUCTIONS:
1. Evaluate the website data provided above.
2. Identify key strengths and issues across 5 categories: SEO, Content Quality, User Experience, Technical Aspects, and Marketing Potential.
3. For each category, provide specific findings with a classification of "strength", "opportunity", or "issue".
4. Suggest specific, actionable recommendations prioritized as "High", "Medium", or "Low".
5. Structure your response in JSON format with these exact keys:
   - "findings": Object with category keys, each containing an array of finding objects with "type", "title", and "description"
   - "recommendations": Array of recommendation objects with "priority", "title", and "description"
   - "score": Numerical score from 0-100 representing overall website quality
   - "summary": Brief textual summary of the analysis

Format your response as a valid JSON object that can be parsed. Do not include any explanations or text outside of the JSON structure.
</instruction>"""
        return prompt
    
    def _process_ai_output(self, ai_output):
        """Process the AI's output text into structured data"""
        try:
            # Try to extract JSON from the response
            json_str = ai_output
            
            # Clean up the response if it contains text outside the JSON
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            analysis_data = json.loads(json_str)
            
            # Validate required keys
            required_keys = ["findings", "recommendations", "score", "summary"]
            for key in required_keys:
                if key not in analysis_data:
                    analysis_data[key] = {} if key == "findings" else [] if key == "recommendations" else "Not provided" if key == "summary" else 50
            
            # Ensure recommendations have priority
            for rec in analysis_data["recommendations"]:
                if "priority" not in rec:
                    rec["priority"] = "Medium"
            
            return {
                "score": analysis_data["score"],
                "findings": analysis_data["findings"],
                "recommendations": analysis_data["recommendations"],
                "summary": analysis_data.get("summary", "Analysis complete")
            }
            
        except Exception as e:
            logger.error(f"Error processing AI output: {str(e)}")
            logger.debug(f"Raw AI output: {ai_output}")
            
            # Return a basic structure if parsing fails
            return {
                "score": 50,
                "findings": {
                    "AI Analysis": [{
                        "type": "warning",
                        "title": "AI Analysis Partial Results",
                        "description": "The AI provided analysis but in a format that couldn't be fully processed."
                    }]
                },
                "recommendations": [
                    {
                        "priority": "Medium",
                        "title": "Review AI findings manually",
                        "description": "The AI analysis should be reviewed manually for insights."
                    }
                ]
            }
    
    def _analyze_basic(self):
        """Perform basic analysis without AI API using heuristics"""
        findings = {
            "Content": [],
            "SEO": [],
            "Technical": [],
            "User Experience": [],
        }
        
        # Check content length and quality
        content_text = self._get_content_sample()
        word_count = len(content_text.split())
        
        if word_count < 300:
            findings["Content"].append({
                "type": "warning",
                "title": "Low content volume",
                "description": f"The page has only approximately {word_count} words. Search engines typically favor pages with substantial, valuable content (500+ words)."
            })
        elif word_count > 1500:
            findings["Content"].append({
                "type": "success",
                "title": "Substantial content volume",
                "description": f"The page has approximately {word_count} words, which is good for SEO and user engagement."
            })
        else:
            findings["Content"].append({
                "type": "success",
                "title": "Adequate content volume",
                "description": f"The page has approximately {word_count} words, which is acceptable for most purposes."
            })
        
        # Check readability (basic approximation)
        sentences = self._count_sentences(content_text)
        if sentences > 0:
            avg_words_per_sentence = word_count / sentences
            if avg_words_per_sentence > 25:
                findings["Content"].append({
                    "type": "warning",
                    "title": "Complex sentence structure",
                    "description": f"Average of {avg_words_per_sentence:.1f} words per sentence. Consider simplifying for better readability."
                })
            elif avg_words_per_sentence < 10:
                findings["Content"].append({
                    "type": "warning",
                    "title": "Very short sentences",
                    "description": f"Average of {avg_words_per_sentence:.1f} words per sentence. The content may be overly simplified."
                })
            else:
                findings["Content"].append({
                    "type": "success",
                    "title": "Good sentence length",
                    "description": f"Average of {avg_words_per_sentence:.1f} words per sentence, which is good for readability."
                })
        
        # Check keyword density
        keywords = self._extract_potential_keywords()
        if len(keywords) > 0:
            findings["SEO"].append({
                "type": "success",
                "title": "Keyword presence",
                "description": f"Detected potential keywords: {', '.join(keywords[:5])}."
            })
        
        # Check title and meta description
        title = self._get_title()
        meta_description = self._get_meta_description()
        
        if title:
            if len(title) < 30:
                findings["SEO"].append({
                    "type": "warning",
                    "title": "Title too short",
                    "description": f"The page title is only {len(title)} characters. Aim for 50-60 characters to maximize SEO impact."
                })
            elif len(title) > 70:
                findings["SEO"].append({
                    "type": "warning",
                    "title": "Title too long",
                    "description": f"The page title is {len(title)} characters, which may get truncated in search results. Aim for 50-60 characters."
                })
            else:
                findings["SEO"].append({
                    "type": "success",
                    "title": "Good title length",
                    "description": f"The page title is {len(title)} characters, which is within the optimal range for search engines."
                })
        else:
            findings["SEO"].append({
                "type": "error",
                "title": "Missing title",
                "description": "The page does not have a title tag, which is crucial for SEO."
            })
        
        if meta_description:
            if len(meta_description) < 70:
                findings["SEO"].append({
                    "type": "warning",
                    "title": "Meta description too short",
                    "description": f"The meta description is only {len(meta_description)} characters. Aim for 150-160 characters to maximize click-through rates."
                })
            elif len(meta_description) > 160:
                findings["SEO"].append({
                    "type": "warning",
                    "title": "Meta description too long",
                    "description": f"The meta description is {len(meta_description)} characters, which may get truncated in search results. Aim for 150-160 characters."
                })
            else:
                findings["SEO"].append({
                    "type": "success",
                    "title": "Good meta description length",
                    "description": f"The meta description is {len(meta_description)} characters, which is within the optimal range."
                })
        else:
            findings["SEO"].append({
                "type": "error",
                "title": "Missing meta description",
                "description": "The page does not have a meta description, which is important for SEO and click-through rates."
            })
        
        # Check heading structure
        headings = self._get_headings_count()
        if headings["h1"] == 0:
            findings["SEO"].append({
                "type": "error",
                "title": "Missing H1 heading",
                "description": "The page does not have an H1 heading, which is important for search engines to understand the main topic."
            })
        elif headings["h1"] > 1:
            findings["SEO"].append({
                "type": "warning",
                "title": "Multiple H1 headings",
                "description": f"The page has {headings['h1']} H1 headings. It's best practice to have only one H1 per page."
            })
        else:
            findings["SEO"].append({
                "type": "success",
                "title": "Good H1 usage",
                "description": "The page has exactly one H1 heading, which is optimal for SEO."
            })
        
        # Check images
        image_data = self._analyze_images()
        if image_data["without_alt"] > 0:
            findings["SEO"].append({
                "type": "warning",
                "title": "Images missing alt text",
                "description": f"{image_data['without_alt']} out of {image_data['count']} images are missing alt text, which is important for SEO and accessibility."
            })
        elif image_data["count"] > 0:
            findings["SEO"].append({
                "type": "success",
                "title": "All images have alt text",
                "description": f"All {image_data['count']} images have alt text, which is excellent for SEO and accessibility."
            })
        
        # Check links
        link_data = self._analyze_links()
        if link_data["internal"] == 0 and link_data["external"] == 0:
            findings["SEO"].append({
                "type": "warning",
                "title": "No links detected",
                "description": "The page doesn't have any links, which may limit its SEO value and user navigation."
            })
        else:
            if link_data["internal"] > 0:
                findings["SEO"].append({
                    "type": "success",
                    "title": "Internal linking",
                    "description": f"The page has {link_data['internal']} internal links, which helps with site structure and user navigation."
                })
            
            if link_data["external"] > 0:
                findings["SEO"].append({
                    "type": "success",
                    "title": "External linking",
                    "description": f"The page has {link_data['external']} external links, which can add credibility and context."
                })
        
        # Check mobile responsiveness (basic check)
        viewport_meta = self.soup.find("meta", attrs={"name": "viewport"})
        if viewport_meta:
            findings["Technical"].append({
                "type": "success",
                "title": "Mobile viewport configured",
                "description": "The page has a viewport meta tag, which is essential for mobile responsiveness."
            })
        else:
            findings["Technical"].append({
                "type": "error",
                "title": "Missing viewport meta tag",
                "description": "The page is missing a viewport meta tag, which is crucial for proper display on mobile devices."
            })
        
        # Generate score based on findings
        score = self._calculate_score(findings)
        
        # Generate recommendations based on findings
        recommendations = self._generate_recommendations(findings)
        
        return {
            "score": score,
            "findings": findings,
            "recommendations": recommendations
        }
    
    def _get_title(self):
        """Extract page title"""
        title_tag = self.soup.find("title")
        return title_tag.get_text().strip() if title_tag else ""
    
    def _get_meta_description(self):
        """Extract meta description"""
        meta_desc = self.soup.find("meta", attrs={"name": "description"})
        return meta_desc["content"].strip() if meta_desc and "content" in meta_desc.attrs else ""
    
    def _get_headings_structure(self):
        """Get hierarchical structure of headings"""
        headings = []
        for level in range(1, 7):
            for h in self.soup.find_all(f"h{level}"):
                text = h.get_text().strip()
                if text:
                    headings.append(f"H{level}: {text}")
        
        return "\n".join(headings[:10]) + ("\n..." if len(headings) > 10 else "")
    
    def _get_headings_count(self):
        """Count headings by level"""
        counts = {}
        for level in range(1, 7):
            tag = f"h{level}"
            counts[tag] = len(self.soup.find_all(tag))
        return counts
    
    def _get_content_sample(self):
        """Extract a representative sample of the page's main content"""
        # Try to find main content containers
        main_content = self.soup.find("main") or self.soup.find("article") or self.soup.find(id=re.compile("content|main", re.I))
        
        if not main_content:
            # Fall back to body content, excluding navigation, header, footer, etc.
            main_content = self.soup.find("body")
            if main_content:
                for tag in main_content.find_all(["nav", "header", "footer", "aside"]):
                    tag.decompose()
        
        if main_content:
            text = main_content.get_text(separator=" ", strip=True)
        else:
            # If no specific container found, use all text
            text = self.soup.get_text(separator=" ", strip=True)
        
        # Clean up the text
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Limit to a reasonable size
        max_chars = 2000
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
            
        return text
    
    def _extract_potential_keywords(self):
        """Extract potential keywords from the content"""
        text = self._get_content_sample()
        
        # Split into words and normalize
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Count word frequencies
        word_counts = {}
        for word in words:
            if word not in word_counts:
                word_counts[word] = 0
            word_counts[word] += 1
        
        # Filter out common stop words
        stop_words = {"the", "and", "for", "that", "this", "with", "you", "not", "but", "are", "from", "have", "was", "all", "can", "will", "your", "one", "has", "they", "what", "who", "when", "where", "why", "how"}
        filtered_words = {word: count for word, count in word_counts.items() if word not in stop_words}
        
        # Sort by frequency
        sorted_words = sorted(filtered_words.items(), key=lambda x: x[1], reverse=True)
        
        # Return the top words
        return [word for word, count in sorted_words[:30]]
    
    def _analyze_links(self):
        """Analyze links on the page"""
        links = self.soup.find_all("a", href=True)
        
        internal_count = 0
        external_count = 0
        social_count = 0
        
        domain = self._extract_domain(self.url)
        
        for link in links:
            href = link["href"].strip()
            
            # Skip empty, javascript, anchor links
            if not href or href.startswith(("javascript:", "#", "mailto:", "tel:")):
                continue
                
            # Check if it's an internal or external link
            if href.startswith("/") or domain in href:
                internal_count += 1
            else:
                external_count += 1
                
                # Check if it's a social media link
                social_domains = ["facebook.com", "twitter.com", "instagram.com", "linkedin.com", "youtube.com", "pinterest.com", "tiktok.com"]
                if any(social in href for social in social_domains):
                    social_count += 1
        
        return {
            "internal": internal_count,
            "external": external_count,
            "social": social_count
        }
    
    def _analyze_images(self):
        """Analyze images on the page"""
        images = self.soup.find_all("img")
        
        with_alt = 0
        without_alt = 0
        
        for img in images:
            if img.get("alt") is not None:
                with_alt += 1
            else:
                without_alt += 1
                
        return {
            "count": len(images),
            "with_alt": with_alt,
            "without_alt": without_alt
        }
    
    def _count_sentences(self, text):
        """Roughly count the number of sentences in text"""
        # This is a simple approximation
        sentences = re.split(r'[.!?]+', text)
        return len([s for s in sentences if len(s.strip()) > 0])
    
    def _extract_domain(self, url):
        """Extract domain from URL"""
        match = re.search(r'https?://(?:www\.)?([^/]+)', url)
        if match:
            return match.group(1)
        return ""
    
    def _calculate_score(self, findings):
        """Calculate a score based on findings"""
        score = 70  # Start with a base score
        
        # Count types
        success_count = 0
        warning_count = 0
        error_count = 0
        
        for category, items in findings.items():
            for item in items:
                if item["type"] == "success":
                    success_count += 1
                elif item["type"] == "warning":
                    warning_count += 1
                elif item["type"] == "error":
                    error_count += 1
        
        # Adjust score
        score += success_count * 2
        score -= warning_count * 1
        score -= error_count * 5
        
        # Ensure score is in range 0-100
        return max(0, min(100, score))
    
    def _generate_recommendations(self, findings):
        """Generate recommendations based on findings"""
        recommendations = []
        
        # Process findings to generate recommendations
        for category, items in findings.items():
            for item in items:
                if item["type"] == "error" or item["type"] == "warning":
                    priority = "High" if item["type"] == "error" else "Medium"
                    
                    # Generate recommendation based on finding title
                    if "title" in item.lower():
                        recommendations.append({
                            "priority": priority,
                            "title": "Optimize page title",
                            "description": "Create a descriptive title between 50-60 characters that includes your primary keyword."
                        })
                    elif "meta description" in item["title"].lower():
                        recommendations.append({
                            "priority": priority,
                            "title": "Improve meta description",
                            "description": "Write a compelling meta description between 150-160 characters that summarizes the page content and includes a call to action."
                        })
                    elif "heading" in item["title"].lower() and "h1" in item["title"].lower():
                        recommendations.append({
                            "priority": priority,
                            "title": "Fix H1 heading",
                            "description": "Ensure the page has exactly one H1 heading that clearly describes the main topic and includes your primary keyword."
                        })
                    elif "alt text" in item["title"].lower():
                        recommendations.append({
                            "priority": priority,
                            "title": "Add alt text to images",
                            "description": "Add descriptive alt text to all images, describing their content and incorporating relevant keywords where appropriate."
                        })
                    elif "content volume" in item["title"].lower():
                        recommendations.append({
                            "priority": priority,
                            "title": "Increase content volume",
                            "description": "Add more high-quality, relevant content to reach at least 500-700 words, focusing on providing value to users."
                        })
                    elif "sentence" in item["title"].lower():
                        recommendations.append({
                            "priority": priority,
                            "title": "Improve readability",
                            "description": "Aim for a mix of sentence lengths, with an average of 15-20 words per sentence. Break up complex sentences and use active voice."
                        })
                    elif "viewport" in item["title"].lower():
                        recommendations.append({
                            "priority": priority,
                            "title": "Add viewport meta tag",
                            "description": "Add <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"> to the head section for better mobile responsiveness."
                        })
        
        # Deduplicate recommendations
        unique_recs = []
        titles_added = set()
        
        for rec in recommendations:
            if rec["title"] not in titles_added:
                unique_recs.append(rec)
                titles_added.add(rec["title"])
        
        # Add general recommendations if few specific ones
        if len(unique_recs) < 3:
            general_recs = [
                {
                    "priority": "Medium",
                    "title": "Implement schema markup",
                    "description": "Add structured data markup to help search engines better understand your content and potentially enhance search results with rich snippets."
                },
                {
                    "priority": "Medium",
                    "title": "Improve internal linking",
                    "description": "Create a logical internal linking structure that guides users to related content and distributes page authority throughout the site."
                },
                {
                    "priority": "Medium",
                    "title": "Optimize for page speed",
                    "description": "Compress images, minify CSS/JS, leverage browser caching, and reduce server response time to improve page loading speed."
                }
            ]
            
            for rec in general_recs:
                if rec["title"] not in titles_added:
                    unique_recs.append(rec)
                    titles_added.add(rec["title"])
        
        # Sort by priority
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        unique_recs.sort(key=lambda x: priority_order.get(x["priority"], 3))
        
        return unique_recs[:7]  # Limit to top 7 recommendations
