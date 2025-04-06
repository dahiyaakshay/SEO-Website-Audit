import re
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse, urljoin
import time

class SEOAnalyzer:
    """Analyzes SEO aspects of a webpage"""
    
    def __init__(self, page_content, url):
        """
        Initialize the SEO analyzer
        
        Args:
            page_content (BeautifulSoup): The parsed HTML content
            url (str): The URL of the page being analyzed
        """
        self.soup = page_content
        self.url = url
        self.domain = urlparse(url).netloc
        
    def analyze(self):
        """
        Perform comprehensive SEO analysis
        
        Returns:
            dict: Analysis results containing score, findings, and recommendations
        """
        findings = {
            "Meta Tags": [],
            "Headings": [],
            "Content": [],
            "Links": [],
            "Images": [],
            "Technical": []
        }
        
        # Check title
        title_result = self._check_title()
        findings["Meta Tags"].append(title_result)
        
        # Check meta description
        meta_desc_result = self._check_meta_description()
        findings["Meta Tags"].append(meta_desc_result)
        
        # Check meta keywords
        meta_keywords_result = self._check_meta_keywords()
        findings["Meta Tags"].append(meta_keywords_result)
        
        # Check canonical URL
        canonical_result = self._check_canonical()
        findings["Technical"].append(canonical_result)
        
        # Check heading structure
        headings_result = self._check_headings()
        findings["Headings"].extend(headings_result)
        
        # Check content length
        content_length_result = self._check_content_length()
        findings["Content"].append(content_length_result)
        
        # Check keyword density
        keyword_result = self._check_keyword_density()
        findings["Content"].append(keyword_result)
        
        # Check internal and external links
        link_results = self._check_links()
        findings["Links"].extend(link_results)
        
        # Check image alt texts
        image_results = self._check_images()
        findings["Images"].extend(image_results)
        
        # Check URL structure
        url_result = self._check_url_structure()
        findings["Technical"].append(url_result)
        
        # Check mobile friendliness indicators
        mobile_result = self._check_mobile_friendly()
        findings["Technical"].append(mobile_result)
        
        # Generate score
        score = self._calculate_score(findings)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(findings)
        
        return {
            "score": score,
            "findings": findings,
            "recommendations": recommendations
        }
    
    def _check_title(self):
        """Check if the page has a proper title tag"""
        title_tag = self.soup.find('title')
        
        if not title_tag:
            return {
                "type": "error",
                "title": "Missing title tag",
                "description": "Your page doesn't have a title tag, which is crucial for SEO."
            }
        
        title_text = title_tag.get_text().strip()
        
        if not title_text:
            return {
                "type": "error",
                "title": "Empty title tag",
                "description": "Your title tag exists but is empty."
            }
        
        title_length = len(title_text)
        
        if title_length < 10:
            return {
                "type": "warning",
                "title": "Title too short",
                "description": f"Your title is only {title_length} characters long. Search engines typically display 50-60 characters.",
                "details": title_text
            }
        
        if title_length > 70:
            return {
                "type": "warning",
                "title": "Title too long",
                "description": f"Your title is {title_length} characters long. Search engines typically display only 50-60 characters.",
                "details": title_text
            }
        
        return {
            "type": "success",
            "title": "Good title length",
            "description": f"Your title is {title_length} characters long, which is optimal for search engines.",
            "details": title_text
        }
    
    def _check_meta_description(self):
        """Check if the page has a proper meta description"""
        meta_desc = self.soup.find('meta', attrs={'name': 'description'})
        
        if not meta_desc:
            return {
                "type": "warning",
                "title": "Missing meta description",
                "description": "Your page doesn't have a meta description tag, which helps with SEO and click-through rates."
            }
        
        desc_content = meta_desc.get('content', '').strip()
        
        if not desc_content:
            return {
                "type": "warning",
                "title": "Empty meta description",
                "description": "Your meta description tag exists but is empty."
            }
        
        desc_length = len(desc_content)
        
        if desc_length < 50:
            return {
                "type": "warning",
                "title": "Meta description too short",
                "description": f"Your meta description is only {desc_length} characters long. Aim for 120-160 characters.",
                "details": desc_content
            }
        
        if desc_length > 160:
            return {
                "type": "warning",
                "title": "Meta description too long",
                "description": f"Your meta description is {desc_length} characters long. Search engines typically truncate descriptions after 155-160 characters.",
                "details": desc_content[:157] + "..."
            }
        
        return {
            "type": "success",
            "title": "Good meta description length",
            "description": f"Your meta description is {desc_length} characters long, which is optimal for search engines.",
            "details": desc_content
        }
    
    def _check_meta_keywords(self):
        """Check meta keywords (less important for modern SEO but still useful)"""
        meta_keywords = self.soup.find('meta', attrs={'name': 'keywords'})
        
        if not meta_keywords:
            return {
                "type": "success",
                "title": "No meta keywords tag",
                "description": "Your page doesn't use meta keywords, which is fine as they're not important for most search engines today."
            }
        
        keywords_content = meta_keywords.get('content', '').strip()
        
        if not keywords_content:
            return {
                "type": "warning",
                "title": "Empty meta keywords",
                "description": "Your meta keywords tag exists but is empty. Either add keywords or remove the tag."
            }
        
        keywords = [k.strip() for k in keywords_content.split(',')]
        
        if len(keywords) > 10:
            return {
                "type": "warning",
                "title": "Too many meta keywords",
                "description": f"You have {len(keywords)} meta keywords. While meta keywords aren't important for most search engines today, having too many can look spammy.",
                "details": keywords_content
            }
        
        return {
            "type": "success",
            "title": "Meta keywords present",
            "description": f"Your page has {len(keywords)} meta keywords. While not important for most search engines today, they may be used by some smaller search engines.",
            "details": keywords_content
        }
    
    def _check_canonical(self):
        """Check if the page has a canonical URL"""
        canonical = self.soup.find('link', attrs={'rel': 'canonical'})
        
        if not canonical:
            return {
                "type": "warning",
                "title": "No canonical tag",
                "description": "Your page doesn't have a canonical tag, which helps prevent duplicate content issues."
            }
        
        canonical_url = canonical.get('href', '').strip()
        
        if not canonical_url:
            return {
                "type": "warning",
                "title": "Empty canonical URL",
                "description": "Your canonical tag exists but has an empty href attribute."
            }
        
        # Normalize URLs for comparison
        canonical_url = canonical_url.rstrip('/')
        current_url = self.url.rstrip('/')
        
        if canonical_url != current_url:
            return {
                "type": "warning",
                "title": "Canonical URL doesn't match current URL",
                "description": "Your canonical URL points to a different URL, which may be intentional if this is a duplicate page.",
                "details": f"Canonical: {canonical_url}\nCurrent: {current_url}"
            }
        
        return {
            "type": "success",
            "title": "Proper canonical tag",
            "description": "Your page has a proper canonical tag that points to the current URL.",
            "details": canonical_url
        }
    
    def _check_headings(self):
        """Check if the page has proper heading structure"""
        findings = []
        headings = self.soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        if not headings:
            findings.append({
                "type": "error",
                "title": "No headings found",
                "description": "Your page doesn't have any heading tags (h1-h6), which are important for both SEO and accessibility."
            })
            return findings
        
        # Check for h1
        h1_tags = self.soup.find_all('h1')
        if not h1_tags:
            findings.append({
                "type": "error",
                "title": "No H1 heading found",
                "description": "Your page doesn't have an H1 heading, which is the main heading and important for SEO."
            })
        elif len(h1_tags) > 1:
            findings.append({
                "type": "warning",
                "title": f"Multiple H1 headings ({len(h1_tags)})",
                "description": "Your page has multiple H1 headings. It's best practice to have only one H1 per page.",
                "details": "\n".join([h.get_text().strip() for h in h1_tags])
            })
        else:
            findings.append({
                "type": "success",
                "title": "Proper H1 heading",
                "description": "Your page has a single H1 heading.",
                "details": h1_tags[0].get_text().strip()
            })
        
        # Check heading order (should not skip levels)
        heading_levels = [int(h.name[1]) for h in headings]
        for i in range(len(heading_levels) - 1):
            if heading_levels[i+1] > heading_levels[i] + 1:
                findings.append({
                    "type": "warning",
                    "title": "Heading levels skipped",
                    "description": f"Your page skips from h{heading_levels[i]} to h{heading_levels[i+1]}. Headings should follow a logical hierarchy."
                })
                break
        
        # Check heading content length
        short_headings = []
        for h in headings:
            text = h.get_text().strip()
            if len(text) < 3:
                short_headings.append(f"{h.name}: '{text}'")
        
        if short_headings:
            findings.append({
                "type": "warning",
                "title": f"Very short headings ({len(short_headings)})",
                "description": "Some headings are very short (less than 3 characters), which may not be descriptive enough.",
                "details": "\n".join(short_headings)
            })
        
        # If no issues found beyond the h1 check
        if len(findings) == 1:
            findings.append({
                "type": "success",
                "title": "Good heading structure",
                "description": f"Your page has {len(headings)} headings with a logical hierarchy.",
                "details": "Heading count: " + ", ".join([f"h{i+1}: {heading_levels.count(i+1)}" for i in range(6) if i+1 in heading_levels])
            })
        
        return findings
    
    def _check_content_length(self):
        """Check the content length of the page"""
        content = self.soup.get_text(strip=True)
        words = content.split()
        word_count = len(words)
        
        if word_count < 300:
            return {
                "type": "warning",
                "title": "Thin content",
                "description": f"Your page has only approximately {word_count} words. Search engines typically prefer content with at least 300 words."
            }
        elif word_count < 600:
            return {
                "type": "success",
                "title": "Adequate content length",
                "description": f"Your page has approximately {word_count} words, which is adequate for basic content."
            }
        else:
            return {
                "type": "success",
                "title": "Good content length",
                "description": f"Your page has approximately {word_count} words, which is good for in-depth content."
            }
    
    def _check_keyword_density(self):
        """Check keyword density based on most frequently used words"""
        content = self.soup.get_text(" ", strip=True).lower()
        
        # Remove common words and punctuation
        common_words = ['the', 'and', 'in', 'of', 'to', 'a', 'is', 'that', 'for', 'on', 'with', 'as', 'by', 'this', 'you', 'be', 'are', 'or', 'an', 'it', 'so']
        words = re.findall(r'\b[a-z]{3,15}\b', content)
        
        # Filter out common words
        filtered_words = [w for w in words if w not in common_words]
        
        if not filtered_words:
            return {
                "type": "warning",
                "title": "Cannot analyze keyword density",
                "description": "Could not extract meaningful keywords from your content."
            }
        
        # Count word frequencies
        word_counts = {}
        for word in filtered_words:
            if word in word_counts:
                word_counts[word] += 1
            else:
                word_counts[word] = 1
        
        # Get top keywords
        top_keywords = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Calculate densities
        total_words = len(words)
        densities = [(word, count, (count / total_words) * 100) for word, count in top_keywords]
        
        # Check for keyword stuffing
        high_density_keywords = [w for w, c, d in densities if d > 5]
        
        if high_density_keywords:
            return {
                "type": "warning",
                "title": "Possible keyword stuffing",
                "description": f"Some keywords appear too frequently in your content, which might be seen as keyword stuffing.",
                "details": "\n".join([f"'{w}': {d:.1f}% ({c} times)" for w, c, d in densities if w in high_density_keywords])
            }
        
        # Format top keywords for display
        keywords_display = "\n".join([f"'{w}': {d:.1f}% ({c} times)" for w, c, d in densities])
        
        return {
            "type": "success",
            "title": "Good keyword density",
            "description": "Your content has a natural keyword distribution with no signs of keyword stuffing.",
            "details": f"Top keywords:\n{keywords_display}"
        }
    
    def _check_links(self):
        """Check internal and external links"""
        findings = []
        links = self.soup.find_all('a', href=True)
        
        if not links:
            findings.append({
                "type": "warning",
                "title": "No links found",
                "description": "Your page doesn't have any links, which may limit its connectivity to other pages."
            })
            return findings
        
        internal_links = []
        external_links = []
        broken_links = []
        nofollow_links = []
        
        for link in links:
            href = link['href'].strip()
            
            # Skip empty, javascript, and anchor links
            if not href or href.startswith(('javascript:', '#', 'mailto:')):
                continue
            
            # Make URL absolute if it's relative
            if not href.startswith(('http://', 'https://')):
                href = urljoin(self.url, href)
            
            # Check if internal or external
            if self.domain in href:
                internal_links.append(href)
            else:
                external_links.append(href)
            
            # Check for nofollow
            if link.get('rel') and 'nofollow' in link.get('rel'):
                nofollow_links.append(href)
        
        # Check for issues
        if not internal_links:
            findings.append({
                "type": "warning",
                "title": "No internal links",
                "description": "Your page doesn't have any internal links, which is important for site structure and SEO."
            })
        else:
            findings.append({
                "type": "success",
                "title": f"Internal links found ({len(internal_links)})",
                "description": f"Your page has {len(internal_links)} internal links, which helps with site structure and SEO."
            })
        
        if not external_links:
            findings.append({
                "type": "warning",
                "title": "No external links",
                "description": "Your page doesn't have any external links, which can be beneficial for SEO when linking to authority sites."
            })
        else:
            findings.append({
                "type": "success",
                "title": f"External links found ({len(external_links)})",
                "description": f"Your page has {len(external_links)} external links."
            })
        
        # Check for descriptive link text
        non_descriptive_count = 0
        for link in links:
            text = link.get_text().strip().lower()
            if text in ['click here', 'read more', 'link', 'here', 'this', 'more', ''] or len(text) < 3:
                non_descriptive_count += 1
        
        if non_descriptive_count > 0:
            findings.append({
                "type": "warning",
                "title": f"Non-descriptive link text ({non_descriptive_count})",
                "description": f"Found {non_descriptive_count} links with non-descriptive text like 'click here' or 'read more'. Use descriptive link text for better SEO and accessibility."
            })
        
        return findings
    
    def _check_images(self):
        """Check images for alt text and other attributes"""
        findings = []
        images = self.soup.find_all('img')
        
        if not images:
            findings.append({
                "type": "success",
                "title": "No images to check",
                "description": "Your page doesn't contain any images."
            })
            return findings
        
        missing_alt = []
        empty_alt = []
        with_alt = []
        large_images = []
        
        for img in images:
            if not img.has_attr('alt'):
                missing_alt.append(img)
            elif img['alt'].strip() == '':
                empty_alt.append(img)
            else:
                with_alt.append(img)
            
            # Check for image size attributes
            if img.get('width') and img.get('height'):
                try:
                    width = int(img['width'])
                    height = int(img['height'])
                    if width > 1000 or height > 1000:
                        large_images.append(img)
                except ValueError:
                    pass
        
        # Report findings
        if missing_alt:
            findings.append({
                "type": "error",
                "title": f"Images missing alt text ({len(missing_alt)})",
                "description": f"{len(missing_alt)} out of {len(images)} images are missing alt attributes, which are important for SEO and accessibility."
            })
        
        if empty_alt and with_alt:
            findings.append({
                "type": "success",
                "title": "Images with empty alt text",
                "description": f"{len(empty_alt)} images have empty alt attributes, which is appropriate for decorative images."
            })
        
        if with_alt:
            findings.append({
                "type": "success",
                "title": f"Images with alt text ({len(with_alt)})",
                "description": f"{len(with_alt)} out of {len(images)} images have alt text, which is good for SEO and accessibility."
            })
        
        if large_images:
            findings.append({
                "type": "warning",
                "title": f"Large images detected ({len(large_images)})",
                "description": f"Found {len(large_images)} potentially large images. Consider resizing or compressing these images to improve page load speed."
            })
        
        return findings
    
    def _check_url_structure(self):
        """Check if the URL structure is SEO-friendly"""
        url_path = urlparse(self.url).path
        
        if not url_path or url_path == '/':
            return {
                "type": "success",
                "title": "Root URL",
                "description": "This is the root URL of the domain."
            }
        
        # Check for URL issues
        issues = []
        
        # Check for uppercase letters
        if any(c.isupper() for c in url_path):
            issues.append("Contains uppercase letters (URLs should be lowercase)")
        
        # Check for special characters
        special_chars = re.findall(r'[^a-zA-Z0-9/\-_\.]', url_path)
        if special_chars:
            issues.append(f"Contains special characters: {', '.join(set(special_chars))}")
        
        # Check for numbers in the URL representing dates or versions
        if re.search(r'/\d{4}/\d{2}/', url_path):
            issues.append("Contains date in URL (consider evergreen URLs without dates)")
        
        # Check for keywords in URL
        words_in_url = re.findall(r'[a-z0-9]+', url_path.lower())
        if len(words_in_url) < 2:
            issues.append("URL doesn't contain descriptive keywords")
        
        # Check for file extensions
        file_extensions = ['.html', '.php', '.aspx', '.jsp']
        if any(url_path.endswith(ext) for ext in file_extensions):
            issues.append("Contains file extension (consider clean URLs without extensions)")
        
        # Check for query parameters
        query = urlparse(self.url).query
        if query:
            issues.append("Contains query parameters (which can cause duplicate content issues)")
        
        if issues:
            return {
                "type": "warning",
                "title": "URL structure issues",
                "description": "Your URL structure could be improved for SEO:",
                "details": "\n- " + "\n- ".join(issues)
            }
        
        return {
            "type": "success",
            "title": "SEO-friendly URL",
            "description": "Your URL structure is clean and SEO-friendly."
        }
    
    def _check_mobile_friendly(self):
        """Check for mobile-friendly indicators"""
        viewport_meta = self.soup.find('meta', attrs={'name': 'viewport'})
        
        if not viewport_meta:
            return {
                "type": "warning",
                "title": "Missing viewport meta tag",
                "description": "Your page is missing the viewport meta tag, which is essential for mobile-friendly pages."
            }
        
        viewport_content = viewport_meta.get('content', '')
        if 'width=device-width' not in viewport_content:
            return {
                "type": "warning",
                "title": "Incomplete viewport meta tag",
                "description": "Your viewport meta tag should include 'width=device-width' to properly adjust to mobile screens."
            }
        
        # Check for mobile-friendly indicators
        responsive_indicators = []
        
        # Check for common responsive CSS frameworks
        for link in self.soup.find_all('link', rel='stylesheet'):
            href = link.get('href', '')
            if any(fw in href.lower() for fw in ['bootstrap', 'foundation', 'materialize', 'bulma']):
                responsive_indicators.append(f"Uses {next(fw for fw in ['bootstrap', 'foundation', 'materialize', 'bulma'] if fw in href.lower())} CSS framework")
        
        # Check for media queries in style tags
        for style in self.soup.find_all('style'):
            if style.string and '@media' in style.string:
                responsive_indicators.append("Uses CSS media queries")
                break
        
        # Check for responsive class names
        responsive_classes = ['container', 'row', 'col', 'sm-', 'md-', 'lg-', 'xl-', 'flex', 'grid']
        for element in self.soup.find_all(class_=True):
            classes = ' '.join(element.get('class', []))
            if any(cls in classes for cls in responsive_classes):
                responsive_indicators.append("Uses responsive CSS class names")
                break
        
        if responsive_indicators:
            return {
                "type": "success",
                "title": "Mobile-friendly indicators found",
                "description": "Your page appears to be mobile-friendly based on technical indicators.",
                "details": "\n- " + "\n- ".join(responsive_indicators)
            }
        
        return {
            "type": "warning",
            "title": "Limited mobile-friendly indicators",
            "description": "Found viewport meta tag but limited evidence of responsive design. Consider implementing responsive design techniques."
        }
    
    def _calculate_score(self, findings):
        """Calculate overall SEO score based on findings"""
        
        # Define weights for different categories
        weights = {
            "Meta Tags": 0.2,
            "Headings": 0.15,
            "Content": 0.2,
            "Links": 0.15,
            "Images": 0.15,
            "Technical": 0.15
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
        title = finding.get("title", "").lower()
        
        if "missing title tag" in title:
            return "Add a descriptive title tag that includes your main keyword. Keep it between 50-60 characters."
        
        elif "title too short" in title or "title too long" in title:
            return "Optimize your title tag length to be between 50-60 characters to ensure it displays properly in search results."
        
        elif "missing meta description" in title or "meta description too short" in title or "meta description too long" in title:
            return "Add a compelling meta description between 120-160 characters that includes your main keywords and encourages clicks."
        
        elif "no h1 heading found" in title or "multiple h1 headings" in title:
            return "Ensure your page has exactly one H1 heading that clearly describes the main topic and includes your primary keyword."
        
        elif "heading levels skipped" in title:
            return "Fix your heading structure to follow a logical hierarchy (H1 → H2 → H3) without skipping levels."
        
        elif "thin content" in title:
            return "Expand your content to at least 300 words with valuable information for users. More comprehensive content tends to rank better."
        
        elif "images missing alt text" in title:
            return "Add descriptive alt text to all images that explains what they show. Use your keywords naturally where appropriate."
        
        elif "url structure issues" in title:
            return "Improve your URL structure by using lowercase letters, hyphens instead of underscores, and including relevant keywords."
        
        elif "missing viewport meta tag" in title or "incomplete viewport meta tag" in title:
            return "Add a proper viewport meta tag: <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"> to make your page mobile-friendly."
        
        elif "no internal links" in title:
            return "Add internal links to other relevant pages on your site to improve site structure and help search engines discover and understand your content."
        
        elif "non-descriptive link text" in title:
            return "Replace generic link text like 'click here' or 'read more' with descriptive text that includes relevant keywords and clearly indicates the destination."
        
        # Generic recommendations based on finding type
        if finding.get("type") == "error":
            return finding.get("description", "Fix this critical SEO issue to improve your search engine rankings.")
        else:
            return finding.get("description", "Address this issue to enhance your SEO performance.")

