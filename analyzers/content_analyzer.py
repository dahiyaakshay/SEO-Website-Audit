import requests
import json
import re
from bs4 import BeautifulSoup
import time
import textwrap

class ContentAnalyzer:
    """Analyzes content quality, readability, and engagement potential"""
    
    def __init__(self, page_content, together_api_key=None, model="llama-3-70b-instruct"):
        """
        Initialize the content analyzer
        
        Args:
            page_content (BeautifulSoup): The parsed HTML content
            together_api_key (str, optional): Together.ai API key
            model (str, optional): Together.ai model to use
        """
        self.soup = page_content
        self.together_api_key = together_api_key
        self.model = model
        
        # Strip scripts, styles and other non-content elements
        for script in self.soup(["script", "style", "nav", "footer", "header"]):
            script.extract()
    
    def analyze(self):
        """
        Analyze the content quality, readability, and engagement
        
        Returns:
            dict: Analysis results with score, findings, and recommendations
        """
        findings = {
            "Readability": [],
            "Content Quality": [],
            "Engagement": [],
            "SEO Content": []
        }
        
        # Extract main content
        main_content = self._extract_main_content()
        
        # Check readability
        readability_result = self._check_readability(main_content)
        findings["Readability"].append(readability_result)
        
        # Check content length
        content_length_result = self._check_content_length(main_content)
        findings["Content Quality"].append(content_length_result)
        
        # Check paragraph structure
        paragraph_result = self._check_paragraph_structure()
        findings["Content Quality"].append(paragraph_result)
        
        # Check heading-to-content ratio
        heading_content_result = self._check_heading_content_ratio()
        findings["SEO Content"].append(heading_content_result)
        
        # Check for thin content sections
        thin_content_result = self._check_thin_content()
        findings["SEO Content"].append(thin_content_result)
        
        # Check formatting variety
        formatting_result = self._check_formatting_variety()
        findings["Engagement"].append(formatting_result)
        
        # Check call to actions
        cta_result = self._check_call_to_actions()
        findings["Engagement"].append(cta_result)
        
        # Use AI for content quality analysis if API key is provided
        if self.together_api_key:
            ai_analysis = self._analyze_with_ai(main_content)
            for category, items in ai_analysis.items():
                if category in findings:
                    findings[category].extend(items)
        
        # Calculate score
        score = self._calculate_score(findings)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(findings)
        
        return {
            "score": score,
            "findings": findings,
            "recommendations": recommendations
        }
    
    def _extract_main_content(self):
        """Extract the main content from the page"""
        # Try to find main content containers
        main_tags = ['article', 'main', 'div[role="main"]', '.content', '#content', '.main-content']
        
        for tag in main_tags:
            if '[' in tag:
                # Handle attribute selectors
                tag_name, attr = tag.split('[', 1)
                attr_name, attr_value = attr.split('=', 1)
                attr_value = attr_value.strip('"]')
                
                elements = self.soup.find_all(tag_name, {attr_name.strip(): attr_value})
                if elements:
                    return " ".join([elem.get_text(strip=True) for elem in elements])
            elif tag.startswith('.'):
                # Handle class selectors
                elements = self.soup.find_all(class_=tag[1:])
                if elements:
                    return " ".join([elem.get_text(strip=True) for elem in elements])
            elif tag.startswith('#'):
                # Handle ID selectors
                element = self.soup.find(id=tag[1:])
                if element:
                    return element.get_text(strip=True)
            else:
                # Handle regular tags
                elements = self.soup.find_all(tag)
                if elements:
                    return " ".join([elem.get_text(strip=True) for elem in elements])
        
        # Fallback to body if no main content container found
        body = self.soup.find('body')
        if body:
            return body.get_text(strip=True)
        
        # Last resort - use all text
        return self.soup.get_text(strip=True)
    
    def _check_readability(self, content):
        """Check the readability of the content"""
        if not content:
            return {
                "type": "error",
                "title": "No readable content found",
                "description": "No readable text content was found on the page."
            }
        
        # Count sentences
        sentences = re.split(r'[.!?]+', content)
        sentences = [s for s in sentences if len(s.strip()) > 0]
        
        # Count words
        words = re.findall(r'\w+', content)
        
        # Count syllables (simplified approach)
        def count_syllables(word):
            word = word.lower()
            if len(word) <= 3:
                return 1
            count = 0
            vowels = "aeiouy"
            if word[0] in vowels:
                count += 1
            for index in range(1, len(word)):
                if word[index] in vowels and word[index - 1] not in vowels:
                    count += 1
            if word.endswith("e"):
                count -= 1
            if count == 0:
                count = 1
            return count
        
        syllable_count = sum(count_syllables(word) for word in words)
        
        # Calculate Flesch Reading Ease Score
        if len(sentences) == 0 or len(words) == 0:
            flesch_score = 0
        else:
            flesch_score = 206.835 - 1.015 * (len(words) / len(sentences)) - 84.6 * (syllable_count / len(words))
        
        if flesch_score < 30:
            readability_level = "Very difficult"
            readability_type = "error"
        elif flesch_score < 50:
            readability_level = "Difficult"
            readability_type = "warning"
        elif flesch_score < 60:
            readability_level = "Fairly difficult"
            readability_type = "warning"
        elif flesch_score < 70:
            readability_level = "Standard"
            readability_type = "success"
        elif flesch_score < 80:
            readability_level = "Fairly easy"
            readability_type = "success"
        elif flesch_score < 90:
            readability_level = "Easy"
            readability_type = "success"
        else:
            readability_level = "Very easy"
            readability_type = "success"
        
        return {
            "type": readability_type,
            "title": f"Readability: {readability_level}",
            "description": f"The content has a Flesch Reading Ease score of {flesch_score:.1f}. " +
                       f"Average sentences have {len(words) / max(len(sentences), 1):.1f} words. " +
                       f"Average words have {syllable_count / max(len(words), 1):.1f} syllables."
        }
    
    def _check_content_length(self, content):
        """Check if the content has sufficient length"""
        word_count = len(re.findall(r'\w+', content))
        
        if word_count < 300:
            return {
                "type": "error",
                "title": "Content too short",
                "description": f"The page has only approximately {word_count} words. " +
                           "Search engines typically prefer content with 300+ words for most pages."
            }
        elif word_count < 600:
            return {
                "type": "warning",
                "title": "Content could be more comprehensive",
                "description": f"The page has approximately {word_count} words. " +
                           "For many topics, 600+ words may provide better depth and SEO value."
            }
        else:
            return {
                "type": "success",
                "title": "Good content length",
                "description": f"The page has approximately {word_count} words, " +
                           "which is a good length for most web pages."
            }
    
    def _check_paragraph_structure(self):
        """Check paragraph structure and length"""
        paragraphs = self.soup.find_all('p')
        
        if not paragraphs:
            return {
                "type": "warning",
                "title": "No paragraph tags found",
                "description": "The page does not use <p> tags for paragraphs, which can affect readability and SEO."
            }
        
        paragraph_lengths = [len(p.get_text().strip()) for p in paragraphs if p.get_text().strip()]
        
        if not paragraph_lengths:
            return {
                "type": "warning",
                "title": "Empty paragraph tags",
                "description": "The page has paragraph tags but they appear to be empty."
            }
        
        avg_paragraph_length = sum(paragraph_lengths) / len(paragraph_lengths)
        
        long_paragraphs = sum(1 for length in paragraph_lengths if length > 300)
        long_paragraph_ratio = long_paragraphs / len(paragraph_lengths) if paragraph_lengths else 0
        
        if avg_paragraph_length > 200:
            return {
                "type": "warning",
                "title": "Paragraphs too long",
                "description": f"The average paragraph length is {avg_paragraph_length:.0f} characters. " +
                           f"{long_paragraph_ratio*100:.0f}% of paragraphs are over 300 characters. " +
                           "Consider breaking long paragraphs into smaller, more digestible chunks."
            }
        else:
            return {
                "type": "success",
                "title": "Good paragraph structure",
                "description": f"The page has {len(paragraphs)} paragraphs with an average length of " +
                           f"{avg_paragraph_length:.0f} characters, which is good for readability."
            }
    
    def _check_heading_content_ratio(self):
        """Check the ratio of headings to content"""
        headings = self.soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        paragraphs = self.soup.find_all('p')
        
        if not headings:
            return {
                "type": "warning",
                "title": "No headings found",
                "description": "The page does not use heading tags (h1-h6), which are important for structure and SEO."
            }
        
        if not paragraphs:
            return {
                "type": "warning",
                "title": "No paragraphs found",
                "description": "The page does not use paragraph tags, which makes it difficult to analyze content structure."
            }
        
        headings_count = len(headings)
        paragraphs_count = len(paragraphs)
        
        if paragraphs_count == 0:
            ratio = 0
        else:
            ratio = headings_count / paragraphs_count
        
        if ratio < 0.1:
            return {
                "type": "warning",
                "title": "Too few headings",
                "description": f"The page has only {headings_count} headings for {paragraphs_count} paragraphs. " +
                           "Consider adding more headings to break up content and improve readability."
            }
        elif ratio > 0.5:
            return {
                "type": "warning",
                "title": "Too many headings",
                "description": f"The page has {headings_count} headings for {paragraphs_count} paragraphs. " +
                           "Too many headings might fragment content too much."
            }
        else:
            return {
                "type": "success",
                "title": "Good heading-to-content ratio",
                "description": f"The page has a good balance of {headings_count} headings for {paragraphs_count} paragraphs."
            }
    
    def _check_thin_content(self):
        """Check for sections with thin content"""
        sections = []
        
        # Try to identify content sections via headings
        for heading in self.soup.find_all(['h2', 'h3']):
            # Get all content until the next heading
            content = ""
            for sibling in heading.find_next_siblings():
                if sibling.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    break
                content += sibling.get_text(" ", strip=True) + " "
            
            sections.append({
                "heading": heading.get_text(strip=True),
                "content": content.strip(),
                "word_count": len(re.findall(r'\w+', content))
            })
        
        # If no sections found via headings, try other containers
        if not sections:
            for div in self.soup.find_all(['div', 'section']):
                if div.get('id') or div.get('class'):
                    content = div.get_text(" ", strip=True)
                    word_count = len(re.findall(r'\w+', content))
                    
                    if word_count < 50 and word_count > 10:
                        sections.append({
                            "heading": f"Section {len(sections) + 1}",
                            "content": content,
                            "word_count": word_count
                        })
        
        # Check for thin sections
        thin_sections = [s for s in sections if s["word_count"] < 50]
        
        if thin_sections and len(thin_sections) > 1:
            return {
                "type": "warning",
                "title": "Thin content sections detected",
                "description": f"Found {len(thin_sections)} sections with less than 50 words each. " +
                           "Consider expanding these sections with more detailed content."
            }
        elif sections and len(sections) > 0:
            return {
                "type": "success",
                "title": "Content sections have adequate depth",
                "description": f"The page has {len(sections)} content sections with good content depth."
            }
        else:
            return {
                "type": "warning",
                "title": "Content structure unclear",
                "description": "Unable to identify clear content sections. Consider using heading tags to structure content."
            }
    
    def _check_formatting_variety(self):
        """Check for variety in text formatting"""
        
        # Check for formatting elements
        formatting_elements = {
            "bold": len(self.soup.find_all(['b', 'strong'])),
            "italic": len(self.soup.find_all(['i', 'em'])),
            "lists": len(self.soup.find_all(['ul', 'ol'])),
            "blockquotes": len(self.soup.find_all('blockquote')),
            "tables": len(self.soup.find_all('table')),
            "images": len(self.soup.find_all('img')),
            "links": len(self.soup.find_all('a'))
        }
        
        # Count total formatting elements
        total_formatting = sum(formatting_elements.values())
        
        # Get content elements to compare against
        content_elements = len(self.soup.find_all(['p', 'div', 'section', 'article']))
        
        if content_elements == 0:
            content_elements = 1  # Avoid division by zero
        
        formatting_ratio = total_formatting / content_elements
        
        formatting_types = sum(1 for count in formatting_elements.values() if count > 0)
        
        if formatting_ratio < 0.2:
            return {
                "type": "warning",
                "title": "Limited content formatting",
                "description": f"The page uses very little formatting ({total_formatting} formatting elements found). " +
                           "Consider adding more bold text, lists, images, etc. to improve readability and engagement."
            }
        elif formatting_types < 3:
            return {
                "type": "warning",
                "title": "Limited formatting variety",
                "description": f"The page only uses {formatting_types} types of formatting elements. " +
                           "Consider using more varied formatting (bold, lists, images, tables, etc.)"
            }
        else:
            return {
                "type": "success",
                "title": "Good formatting variety",
                "description": f"The page uses {formatting_types} different types of formatting elements " +
                           f"({total_formatting} total formatting elements), which helps with readability and engagement."
            }
    
    def _check_call_to_actions(self):
        """Check for call to action elements"""
        # Look for common CTA elements
        buttons = self.soup.find_all(['button', 'a'], class_=lambda c: c and any(cta in c.lower() for cta in ['btn', 'button', 'cta']))
        
        # Also look for links with CTA-like text
        cta_text_patterns = ['sign up', 'subscribe', 'register', 'get started', 'learn more', 'contact us', 'try', 'buy']
        cta_links = self.soup.find_all('a', string=lambda s: s and any(cta in s.lower() for cta in cta_text_patterns))
        
        all_ctas = buttons + cta_links
        
        if not all_ctas:
            return {
                "type": "warning",
                "title": "No clear call-to-actions found",
                "description": "The page doesn't appear to have clear call-to-action elements, which are important for user engagement and conversion."
            }
        elif len(all_ctas) > 5:
            return {
                "type": "warning",
                "title": "Too many call-to-actions",
                "description": f"The page has {len(all_ctas)} potential call-to-action elements, which might overwhelm users."
            }
        else:
            return {
                "type": "success",
                "title": "Good call-to-action presence",
                "description": f"The page has {len(all_ctas)} clear call-to-action elements, which is good for user engagement."
            }
    
    def _analyze_with_ai(self, content):
        """Use Together.ai API to analyze content quality"""
        
        # Limit content length to avoid excessive API usage
        content_excerpt = content[:2000] if len(content) > 2000 else content
        
        prompt = f"""
        Analyze the following website content for quality, engagement, and readability. 
        Provide specific observations about:
        
        1. Content quality and depth
        2. Tone and style
        3. Target audience alignment
        4. Persuasiveness
        5. Readability issues
        
        Website content:
        {content_excerpt}
        
        Return your analysis in JSON format with the following structure:
        {{
            "Content Quality": [
                {{
                    "type": "success|warning|error",
                    "title": "Observation title",
                    "description": "Detailed observation"
                }}
            ],
            "Engagement": [
                {{
                    "type": "success|warning|error",
                    "title": "Observation title",
                    "description": "Detailed observation"
                }}
            ],
            "Readability": [
                {{
                    "type": "success|warning|error",
                    "title": "Observation title",
                    "description": "Detailed observation"
                }}
            ]
        }}
        """
        
        try:
            response = requests.post(
                "https://api.together.xyz/v1/completions",
                headers={
                    "Authorization": f"Bearer {self.together_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "max_tokens": 1000,
                    "temperature": 0.2,
                    "stop": ["}}}"]  # Stop at the end of the JSON
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_text = result.get("choices", [{}])[0].get("text", "")
                
                # Clean up the response to ensure it's valid JSON
                ai_text = re.sub(r'^[^{]*', '', ai_text)  # Remove any text before first {
                ai_text = re.sub(r'[^}]*$', '', ai_text)  # Remove any text after last }
                
                try:
                    ai_analysis = json.loads(ai_text)
                    # Validate the structure
                    valid_categories = ["Content Quality", "Engagement", "Readability"]
                    for category in valid_categories:
                        if category not in ai_analysis:
                            ai_analysis[category] = []
                    return ai_analysis
                except json.JSONDecodeError:
                    # Fallback response if JSON parsing fails
                    return {
                        "Content Quality": [{
                            "type": "warning",
                            "title": "AI analysis unavailable",
                            "description": "Could not parse AI analysis results."
                        }],
                        "Engagement": [],
                        "Readability": []
                    }
            else:
                return {
                    "Content Quality": [{
                        "type": "warning",
                        "title": "AI analysis unavailable",
                        "description": f"API error: {response.status_code}"
                    }],
                    "Engagement": [],
                    "Readability": []
                }
        except Exception as e:
            return {
                "Content Quality": [{
                    "type": "warning",
                    "title": "AI analysis unavailable",
                    "description": f"Error: {str(e)}"
                }],
                "Engagement": [],
                "Readability": []
            }
    
    def _calculate_score(self, findings):
        """Calculate overall content score based on findings"""
        
        # Define weights for different categories
        weights = {
            "Readability": 0.25,
            "Content Quality": 0.3,
            "Engagement": 0.25,
            "SEO Content": 0.2
        }
        
        # Calculate scores for each category
        category_scores = {}
        
        for category, items in findings.items():
            if not items:
                category_scores[category] = 50  # Default score for empty categories
                continue
                
            # Count types
            type_counts = {"success": 0, "warning": 0, "error": 0}
            for item in items:
                if "type" in item:
                    type_counts[item["type"]] += 1
            
            # Calculate category score
            total_items = sum(type_counts.values())
            if total_items == 0:
                category_scores[category] = 50
            else:
                # Success: 100 points, Warning: 50 points, Error: 0 points
                category_score = (type_counts["success"] * 100 + type_counts["warning"] * 50) / total_items
                category_scores[category] = category_score
        
        # Calculate weighted total score
        total_weight = sum(weights.get(category, 0) for category in category_scores.keys())
        if total_weight == 0:
            return 50  # Default score
            
        weighted_sum = sum(
            category_scores[category] * weights.get(category, 0) 
            for category in category_scores.keys()
        )
        
        return round(weighted_sum / total_weight)
    
    def _generate_recommendations(self, findings):
        """Generate prioritized recommendations based on findings"""
        recommendations = []
        
        # Process all error findings first (high priority)
        for category, items in findings.items():
            for item in items:
                if item.get("type") == "error":
                    recommendations.append({
                        "priority": "High",
                        "category": category,
                        "title": item.get("title", "Fix issue"),
                        "description": self._generate_recommendation_text(category, item)
                    })
        
        # Process warning findings (medium priority)
        for category, items in findings.items():
            for item in items:
                if item.get("type") == "warning":
                    recommendations.append({
                        "priority": "Medium",
                        "category": category,
                        "title": item.get("title", "Improve aspect"),
                        "description": self._generate_recommendation_text(category, item)
                    })
        
        # Limit to top 5 recommendations
        return sorted(recommendations, key=lambda x: {"High": 0, "Medium": 1, "Low": 2}[x["priority"]])[:5]
    
    def _generate_recommendation_text(self, category, finding):
        """Generate specific recommendation text based on the finding"""
        if category == "Readability" and "Readability: " in finding.get("title", ""):
            if "Very difficult" in finding.get("title", ""):
                return "Simplify your content by using shorter sentences and less complex vocabulary. Aim for shorter paragraphs and more straightforward explanations."
            elif "Difficult" in finding.get("title", ""):
                return "Make your content more accessible by reducing sentence length and using simpler words where possible."
        
        elif category == "Content Quality" and "Content too short" in finding.get("title", ""):
            return "Expand your content with more detailed information, examples, and explanations to provide better value to users and improve search rankings."
        
        elif category == "Readability" and "paragraphs too long" in finding.get("title", "").lower():
            return "Break long paragraphs into smaller, more digestible chunks of 2-3 sentences each to improve readability and engagement."
        
        elif category == "Engagement" and "No clear call-to-actions" in finding.get("title", ""):
            return "Add clear call-to-action buttons or links to guide users toward conversion goals such as signing up, purchasing, or contacting you."
        
        elif category == "SEO Content" and "No headings found" in finding.get("title", ""):
            return "Add headings (H1, H2, H3) to structure your content, make it more scannable, and improve SEO."
        
        # Generic recommendations based on finding type
        if finding.get("type") == "error":
            return finding.get("description", "Fix this critical issue to improve content effectiveness.")
        else:
            return finding.get("description", "Address this issue to enhance content quality.")
