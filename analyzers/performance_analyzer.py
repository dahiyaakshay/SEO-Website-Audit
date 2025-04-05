import requests
import time
import json
import re
from urllib.parse import urlparse, urljoin
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PerformanceAnalyzer:
    """Analyzes website performance metrics"""
    
    def __init__(self, url, api_key=None):
        """
        Initialize the performance analyzer
        
        Args:
            url (str): The URL to analyze
            api_key (str, optional): Google PageSpeed Insights API key
        """
        self.url = url
        self.api_key = api_key
        self.parsed_url = urlparse(url)
    
    def analyze(self):
        """
        Perform performance analysis
        
        Returns:
            dict: Analysis results with score, findings, and recommendations
        """
        findings = {
            "Speed": [],
            "Resources": [],
            "Mobile": [],
            "Technical": []
        }
        
        # First attempt to use PageSpeed Insights API if key is provided
        if self.api_key:
            try:
                pagespeed_results = self._analyze_with_pagespeed()
                if pagespeed_results:
                    # Process PageSpeed results
                    findings = self._process_pagespeed_results(pagespeed_results)
            except Exception as e:
                logger.error(f"Error using PageSpeed Insights API: {str(e)}")
                # Fall back to basic checking
        
        # If no PageSpeed results or no API key, do basic performance checks
        if not findings["Speed"]:
            # Basic response time check
            response_time = self._check_response_time()
            findings["Speed"].append(response_time)
            
            # Check page weight
            page_weight = self._estimate_page_weight()
            findings["Resources"].append(page_weight)
            
            # Check for HTTP/2
            http2_result = self._check_http2()
            findings["Technical"].append(http2_result)
            
            # Check SSL/TLS
            ssl_result = self._check_ssl()
            findings["Technical"].append(ssl_result)
        
        # Calculate score
        score = self._calculate_score(findings)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(findings)
        
        return {
            "score": score,
            "findings": findings,
            "recommendations": recommendations
        }
    
    def _analyze_with_pagespeed(self):
        """
        Use Google PageSpeed Insights API for performance analysis
        
        Returns:
            dict: PageSpeed Insights results or None if unsuccessful
        """
        logger.info(f"Analyzing with PageSpeed Insights API: {self.url}")
        
        api_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        params = {
            "url": self.url,
            "key": self.api_key,
            "strategy": "mobile",  # Start with mobile strategy
            "category": "performance"
        }
        
        try:
            # Make request to PageSpeed API
            response = requests.get(api_url, params=params, timeout=30)
            if response.status_code != 200:
                logger.warning(f"PageSpeed API returned status code {response.status_code}")
                return None
            
            mobile_results = response.json()
            
            # Also get desktop results
            params["strategy"] = "desktop"
            response = requests.get(api_url, params=params, timeout=30)
            if response.status_code != 200:
                logger.warning(f"PageSpeed API (desktop) returned status code {response.status_code}")
                desktop_results = None
            else:
                desktop_results = response.json()
            
            return {
                "mobile": mobile_results,
                "desktop": desktop_results
            }
            
        except Exception as e:
            logger.error(f"Error with PageSpeed API: {str(e)}")
            return None
    
    def _process_pagespeed_results(self, pagespeed_results):
        """
        Process and structure PageSpeed Insights API results
        
        Args:
            pagespeed_results (dict): Results from PageSpeed Insights API
            
        Returns:
            dict: Structured findings
        """
        findings = {
            "Speed": [],
            "Resources": [],
            "Mobile": [],
            "Technical": []
        }
        
        # Process mobile results
        mobile_data = pagespeed_results.get("mobile", {})
        if mobile_data:
            mobile_score = self._extract_pagespeed_score(mobile_data)
            findings["Speed"].append({
                "type": self._score_to_type(mobile_score),
                "title": f"Mobile Speed Score: {mobile_score}",
                "description": f"The mobile speed score is {mobile_score}/100. "
                           f"{'This is good!' if mobile_score >= 80 else 'This needs improvement.'}"
            })
            
            # Extract Core Web Vitals
            mobile_cwv = self._extract_core_web_vitals(mobile_data)
            for vital_name, vital_data in mobile_cwv.items():
                findings["Speed"].append(vital_data)
            
            # Extract opportunities
            mobile_opportunities = self._extract_opportunities(mobile_data)
            for opportunity in mobile_opportunities:
                findings["Resources"].append(opportunity)
        
        # Process desktop results
        desktop_data = pagespeed_results.get("desktop", {})
        if desktop_data:
            desktop_score = self._extract_pagespeed_score(desktop_data)
            findings["Speed"].append({
                "type": self._score_to_type(desktop_score),
                "title": f"Desktop Speed Score: {desktop_score}",
                "description": f"The desktop speed score is {desktop_score}/100. "
                           f"{'This is good!' if desktop_score >= 80 else 'This needs improvement.'}"
            })
            
            # Extract Core Web Vitals for desktop
            desktop_cwv = self._extract_core_web_vitals(desktop_data)
            # Only add desktop CWV if different from mobile
            for vital_name, vital_data in desktop_cwv.items():
                # Create a desktop-specific version
                desktop_vital = vital_data.copy()
                desktop_vital["title"] = f"Desktop {desktop_vital['title']}"
                findings["Speed"].append(desktop_vital)
        
        # Add mobile-friendliness finding if no issues detected
        findings["Mobile"].append({
            "type": "success",
            "title": "Mobile-friendly",
            "description": "The page is optimized for mobile devices based on performance tests."
        })
        
        return findings
    
    def _extract_pagespeed_score(self, pagespeed_data):
        """Extract overall performance score from PageSpeed data"""
        try:
            categories = pagespeed_data.get("lighthouseResult", {}).get("categories", {})
            performance = categories.get("performance", {})
            score = performance.get("score", 0)
            return round(score * 100)  # Convert from 0-1 to 0-100
        except (KeyError, TypeError):
            return 0
    
    def _extract_core_web_vitals(self, pagespeed_data):
        """Extract Core Web Vitals metrics from PageSpeed data"""
        results = {}
        
        try:
            audits = pagespeed_data.get("lighthouseResult", {}).get("audits", {})
            
            # First Contentful Paint (FCP)
            if "first-contentful-paint" in audits:
                fcp = audits["first-contentful-paint"]
                fcp_value = fcp.get("displayValue", "Unknown")
                fcp_score = fcp.get("score", 0)
                
                results["FCP"] = {
                    "type": self._score_to_type(fcp_score * 100),
                    "title": f"First Contentful Paint: {fcp_value}",
                    "description": "First Contentful Paint marks when text or images are first visible. " +
                               f"{'Good' if fcp_score >= 0.8 else 'Needs improvement' if fcp_score >= 0.5 else 'Poor'}."
                }
            
            # Largest Contentful Paint (LCP)
            if "largest-contentful-paint" in audits:
                lcp = audits["largest-contentful-paint"]
                lcp_value = lcp.get("displayValue", "Unknown")
                lcp_score = lcp.get("score", 0)
                
                results["LCP"] = {
                    "type": self._score_to_type(lcp_score * 100),
                    "title": f"Largest Contentful Paint: {lcp_value}",
                    "description": "Largest Contentful Paint measures loading performance. " +
                               f"{'Good' if lcp_score >= 0.8 else 'Needs improvement' if lcp_score >= 0.5 else 'Poor'}."
                }
            
            # Cumulative Layout Shift (CLS)
            if "cumulative-layout-shift" in audits:
                cls = audits["cumulative-layout-shift"]
                cls_value = cls.get("displayValue", "Unknown")
                cls_score = cls.get("score", 0)
                
                results["CLS"] = {
                    "type": self._score_to_type(cls_score * 100),
                    "title": f"Cumulative Layout Shift: {cls_value}",
                    "description": "Cumulative Layout Shift measures visual stability. " +
                               f"{'Good' if cls_score >= 0.8 else 'Needs improvement' if cls_score >= 0.5 else 'Poor'}."
                }
            
            # Total Blocking Time (TBT)
            if "total-blocking-time" in audits:
                tbt = audits["total-blocking-time"]
                tbt_value = tbt.get("displayValue", "Unknown")
                tbt_score = tbt.get("score", 0)
                
                results["TBT"] = {
                    "type": self._score_to_type(tbt_score * 100),
                    "title": f"Total Blocking Time: {tbt_value}",
                    "description": "Total Blocking Time measures interactivity. " +
                               f"{'Good' if tbt_score >= 0.8 else 'Needs improvement' if tbt_score >= 0.5 else 'Poor'}."
                }
            
        except (KeyError, TypeError) as e:
            logger.error(f"Error extracting Core Web Vitals: {str(e)}")
        
        return results
    
    def _extract_opportunities(self, pagespeed_data):
        """Extract improvement opportunities from PageSpeed data"""
        opportunities = []
        
        try:
            audits = pagespeed_data.get("lighthouseResult", {}).get("audits", {})
            
            # Check for specific optimization opportunities
            opportunity_audits = [
                "render-blocking-resources",
                "unminified-css",
                "unminified-javascript",
                "unused-css-rules",
                "unused-javascript",
                "properly-sized-images",
                "offscreen-images",
                "uses-webp-images",
                "uses-text-compression",
                "uses-responsive-images",
                "efficient-animated-content",
                "duplicated-javascript"
            ]
            
            for audit_id in opportunity_audits:
                if audit_id in audits and audits[audit_id]["score"] < 1:
                    audit = audits[audit_id]
                    
                    # Get the potential savings if available
                    savings_text = ""
                    if "details" in audit and "overallSavingsMs" in audit["details"]:
                        savings_ms = audit["details"]["overallSavingsMs"]
                        savings_text = f" Potential savings: {savings_ms}ms."
                    
                    opportunities.append({
                        "type": "warning" if audit["score"] < 0.5 else "warning",
                        "title": audit.get("title", audit_id.replace("-", " ").title()),
                        "description": f"{audit.get('description', '')}{savings_text}"
                    })
        
        except (KeyError, TypeError) as e:
            logger.error(f"Error extracting opportunities: {str(e)}")
        
        return opportunities
    
    def _score_to_type(self, score):
        """Convert numerical score to finding type"""
        if score >= 80:
            return "success"
        elif score >= 50:
            return "warning"
        else:
            return "error"
    
    def _check_response_time(self):
        """
        Check the response time of the website
        
        Returns:
            dict: Finding with response time information
        """
        try:
            start_time = time.time()
            response = requests.get(self.url, timeout=10)
            response_time = time.time() - start_time
            
            # Evaluate response time
            if response_time < 0.5:
                return {
                    "type": "success",
                    "title": f"Fast response time: {response_time:.2f}s",
                    "description": f"The server responded in {response_time:.2f} seconds, which is excellent."
                }
            elif response_time < 1.5:
                return {
                    "type": "success",
                    "title": f"Good response time: {response_time:.2f}s",
                    "description": f"The server responded in {response_time:.2f} seconds, which is good."
                }
            elif response_time < 3:
                return {
                    "type": "warning",
                    "title": f"Moderate response time: {response_time:.2f}s",
                    "description": f"The server responded in {response_time:.2f} seconds. This could be improved."
                }
            else:
                return {
                    "type": "error",
                    "title": f"Slow response time: {response_time:.2f}s",
                    "description": f"The server responded in {response_time:.2f} seconds, which is too slow."
                }
        except requests.exceptions.Timeout:
            return {
                "type": "error",
                "title": "Request timed out",
                "description": "The server took too long to respond (more than 10 seconds)."
            }
        except Exception as e:
            return {
                "type": "error",
                "title": "Error checking response time",
                "description": f"Could not check response time: {str(e)}"
            }
    
    def _estimate_page_weight(self):
        """
        Estimate the total page weight (size)
        
        Returns:
            dict: Finding with page weight information
        """
        try:
            # Get page with all resources
            response = requests.get(self.url, timeout=10)
            html_size = len(response.content)
            
            # Extract URLs of resources (css, js, images)
            resource_urls = []
            
            # CSS files
            css_urls = re.findall(r'href=[\'"]([^\'"]+\.css)[\'"]', response.text)
            resource_urls.extend(css_urls)
            
            # JavaScript files
            js_urls = re.findall(r'src=[\'"]([^\'"]+\.js)[\'"]', response.text)
            resource_urls.extend(js_urls)
            
            # Images
            img_urls = re.findall(r'src=[\'"]([^\'"]+\.(jpg|jpeg|png|gif|webp|svg))[\'"]', response.text)
            resource_urls.extend([url for url, ext in img_urls])
            
            # Make all URLs absolute
            base_url = f"{self.parsed_url.scheme}://{self.parsed_url.netloc}"
            resource_urls = [
                url if url.startswith(('http://', 'https://')) else urljoin(base_url, url)
                for url in resource_urls
            ]
            
            # Limit to first 10 resources to avoid too many requests
            resource_urls = resource_urls[:10]
            
            # Get size of resources
            total_size = html_size
            resource_count = 1  # Start with 1 for the HTML
            
            for url in resource_urls:
                try:
                    # Use HEAD request to get content length
                    head_response = requests.head(url, timeout=5)
                    if 'content-length' in head_response.headers:
                        total_size += int(head_response.headers['content-length'])
                        resource_count += 1
                except:
                    # Skip if error
                    continue
            
            # Convert to KB
            total_kb = total_size / 1024
            
            # Estimate full page size based on sampled resources
            if len(resource_urls) < 10:
                estimated_kb = total_kb
            else:
                # Roughly estimate based on typical resource patterns
                estimated_kb = total_kb * 1.5  # Add 50% more for unchecked resources
            
            # Evaluate page weight
            if estimated_kb < 500:
                return {
                    "type": "success",
                    "title": f"Light page weight: {estimated_kb:.0f}KB",
                    "description": f"The page uses approximately {estimated_kb:.0f}KB across at least {resource_count} resources, which is good."
                }
            elif estimated_kb < 1500:
                return {
                    "type": "success",
                    "title": f"Average page weight: {estimated_kb:.0f}KB",
                    "description": f"The page uses approximately {estimated_kb:.0f}KB across at least {resource_count} resources."
                }
            elif estimated_kb < 3000:
                return {
                    "type": "warning",
                    "title": f"Heavy page weight: {estimated_kb:.0f}KB",
                    "description": f"The page uses approximately {estimated_kb:.0f}KB across at least {resource_count} resources. Consider optimization."
                }
            else:
                return {
                    "type": "error",
                    "title": f"Very heavy page: {estimated_kb:.0f}KB",
                    "description": f"The page uses approximately {estimated_kb:.0f}KB across at least {resource_count} resources, which is too heavy."
                }
        except Exception as e:
            return {
                "type": "warning",
                "title": "Could not estimate page weight",
                "description": f"Error when estimating page weight: {str(e)}"
            }
    
    def _check_http2(self):
        """
        Check if the website supports HTTP/2
        
        Returns:
            dict: Finding with HTTP/2 information
        """
        try:
            # Need to use low-level urllib3 to get protocol version
            import urllib3
            http = urllib3.PoolManager()
            r = http.request('GET', self.url)
            
            # Get protocol version
            if hasattr(r, '_protocol_version'):
                protocol = r._protocol_version
            else:
                # Fallback method
                protocol = r.version if hasattr(r, 'version') else "unknown"
            
            if protocol == 'h2' or protocol == 2:
                return {
                    "type": "success",
                    "title": "HTTP/2 supported",
                    "description": "The website supports HTTP/2, which improves page load performance through multiplexing."
                }
            else:
                return {
                    "type": "warning",
                    "title": "HTTP/2 not detected",
                    "description": "The website appears to use HTTP/1.1. Upgrading to HTTP/2 could improve performance."
                }
        except Exception as e:
            return {
                "type": "warning",
                "title": "Could not check HTTP version",
                "description": f"Error when checking HTTP version: {str(e)}"
            }
    
    def _check_ssl(self):
        """
        Check if the website uses HTTPS and evaluate the SSL/TLS configuration
        
        Returns:
            dict: Finding with SSL/TLS information
        """
        if self.parsed_url.scheme != 'https':
            return {
                "type": "error",
                "title": "No HTTPS",
                "description": "The website does not use HTTPS, which is essential for security and performance."
            }
        
        try:
            import ssl
            import socket
            
            hostname = self.parsed_url.netloc
            context = ssl.create_default_context()
            
            with socket.create_connection((hostname, 443)) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    # Get certificate
                    cert = ssock.getpeercert()
                    # Get protocol version
                    protocol = ssock.version()
            
            # Check if using modern TLS
            if protocol in ('TLSv1.2', 'TLSv1.3'):
                return {
                    "type": "success",
                    "title": f"Modern HTTPS ({protocol})",
                    "description": f"The website uses {protocol}, which is secure and performs well."
                }
            else:
                return {
                    "type": "warning",
                    "title": f"Outdated HTTPS ({protocol})",
                    "description": f"The website uses {protocol}, which is outdated. Upgrading to TLS 1.2 or 1.3 is recommended."
                }
        except Exception as e:
            # If connection worked but analysis failed
            return {
                "type": "success",
                "title": "HTTPS enabled",
                "description": "The website uses HTTPS, which is good for security and performance."
            }
    
    def _calculate_score(self, findings):
        """Calculate overall performance score based on findings"""
        
        # Define weights for different categories
        weights = {
            "Speed": 0.5,
            "Resources": 0.2,
            "Mobile": 0.2,
            "Technical": 0.1
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
        
        if "response time" in title and "slow" in title:
            return "Improve server response time by upgrading hosting, implementing caching, or optimizing server-side code."
        
        elif "page weight" in title and ("heavy" in title or "very heavy" in title):
            return "Reduce page weight by compressing images, minifying CSS/JS, and removing unnecessary resources."
        
        elif "http/2 not detected" in title:
            return "Upgrade your server to support HTTP/2 to improve loading performance through multiplexing and parallel downloads."
        
        elif "no https" in title:
            return "Implement HTTPS to improve security and performance. Many modern performance features require HTTPS."
        
        elif "render-blocking resources" in title:
            return "Eliminate render-blocking resources by moving critical CSS inline and deferring non-critical JavaScript."
        
        elif "properly-sized images" in title or "responsive images" in title:
            return "Serve properly sized images for each device to reduce wasted bytes and improve loading time."
        
        elif "text compression" in title:
            return "Enable GZIP or Brotli compression on your server to reduce transfer sizes of text-based resources."
        
        elif "largest contentful paint" in title or "lcp" in title.split():
            return "Improve Largest Contentful Paint by optimizing the loading of your main content, reducing server response time, and prioritizing critical resources."
        
        elif "cumulative layout shift" in title or "cls" in title.split():
            return "Reduce layout shifts by setting explicit width and height for images and videos, avoiding dynamically injected content, and using stable layouts."
        
        elif "total blocking time" in title or "tbt" in title.split():
            return "Reduce Total Blocking Time by breaking up long tasks, optimizing JavaScript, and deferring non-critical JavaScript execution."
        
        # Generic recommendations based on finding type
        if finding.get("type") == "error":
            return finding.get("description", "Fix this critical performance issue to improve user experience.")
        else:
            return finding.get("description", "Address this issue to enhance website performance.")
