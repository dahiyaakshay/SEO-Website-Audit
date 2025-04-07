import requests
import logging
from urllib.parse import quote_plus
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PerformanceAnalyzer:
    """Analyzes website performance using Google PageSpeed API with fallback to basic analysis"""
    
    def __init__(self, url, api_key=None):
        """
        Initialize the performance analyzer
        
        Args:
            url (str): The URL to analyze
            api_key (str, optional): Google PageSpeed API key
        """
        self.url = url
        self.api_key = api_key
        
    def analyze(self):
        """
        Perform performance analysis using PageSpeed API if available, otherwise use basic analysis
        
        Returns:
            dict: Analysis results with score, findings, and recommendations
        """
        if self.api_key:
            try:
                # Use Google PageSpeed API
                return self._analyze_with_api()
            except Exception as e:
                logger.error(f"PageSpeed API error: {str(e)}")
                logger.info("Falling back to basic performance analysis")
                # Fallback to basic analysis if API fails
                return self._analyze_basic()
        else:
            # No API key provided, use basic analysis
            return self._analyze_basic()
    
    def _analyze_with_api(self):
        """Analyze performance using Google PageSpeed API"""
        # URL encode the target URL and build the API request URL
        encoded_url = quote_plus(self.url)
        api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={encoded_url}&strategy=mobile&category=performance&key={self.api_key}"
        
        # Make the API request
        response = requests.get(api_url)
        
        # Check if the request was successful
        if response.status_code != 200:
            logger.error(f"PageSpeed API returned status code {response.status_code}: {response.text}")
            raise Exception(f"PageSpeed API error: {response.status_code}")
        
        # Parse the JSON response
        data = response.json()
        
        # Extract key metrics from the API response
        lighthouse_result = data.get("lighthouseResult", {})
        audits = lighthouse_result.get("audits", {})
        
        # Extract performance score (0-1, convert to 0-100)
        categories = lighthouse_result.get("categories", {})
        performance_score = int(categories.get("performance", {}).get("score", 0) * 100)
        
        # Initialize findings structure
        findings = {
            "Loading Speed": [],
            "Resources": [],
            "Optimization": [],
        }
        
        # Extract core web vitals metrics
        core_web_vitals = [
            ("first-contentful-paint", "First Contentful Paint (FCP)", "Loading Speed"),
            ("largest-contentful-paint", "Largest Contentful Paint (LCP)", "Loading Speed"),
            ("first-meaningful-paint", "First Meaningful Paint (FMP)", "Loading Speed"),
            ("speed-index", "Speed Index", "Loading Speed"),
            ("interactive", "Time to Interactive (TTI)", "Loading Speed"),
            ("max-potential-fid", "Max Potential First Input Delay", "Loading Speed"),
            ("cumulative-layout-shift", "Cumulative Layout Shift (CLS)", "Loading Speed"),
            ("server-response-time", "Server Response Time (TTFB)", "Loading Speed"),
            ("total-blocking-time", "Total Blocking Time (TBT)", "Loading Speed"),
        ]
        
        # Process core web vitals
        for audit_id, title, category in core_web_vitals:
            if audit_id in audits:
                audit = audits[audit_id]
                score = audit.get("score", 0)
                
                # Determine finding type based on score
                if score >= 0.9:
                    finding_type = "success"
                elif score >= 0.5:
                    finding_type = "warning"
                else:
                    finding_type = "error"
                
                findings[category].append({
                    "type": finding_type,
                    "title": title,
                    "description": f"{audit.get('displayValue', 'N/A')} - {audit.get('description', '')}"
                })
        
        # Resource optimization metrics
        resource_audits = [
            ("render-blocking-resources", "Render-Blocking Resources", "Resources"),
            ("uses-optimized-images", "Optimized Images", "Resources"),
            ("unused-css-rules", "Unused CSS Rules", "Resources"),
            ("uses-webp-images", "WebP Image Format", "Optimization"),
            ("uses-text-compression", "Text Compression", "Optimization"),
            ("uses-responsive-images", "Responsive Images", "Resources"),
            ("efficient-animated-content", "Efficient Animated Content", "Resources"),
            ("unminified-css", "CSS Minification", "Optimization"),
            ("unminified-javascript", "JavaScript Minification", "Optimization"),
            ("unused-javascript", "Unused JavaScript", "Resources"),
        ]
        
        # Process resource audits
        for audit_id, title, category in resource_audits:
            if audit_id in audits:
                audit = audits[audit_id]
                score = audit.get("score", 0)
                
                # Determine finding type based on score
                if score >= 0.9:
                    finding_type = "success"
                elif score >= 0.5:
                    finding_type = "warning"
                else:
                    finding_type = "error"
                
                findings[category].append({
                    "type": finding_type,
                    "title": title,
                    "description": f"{audit.get('displayValue', 'N/A')} - {audit.get('description', '')}"
                })
        
        # Generate recommendations based on failed or partially failed audits
        recommendations = []
        for audit_id, audit in audits.items():
            # Focus on low-scoring audits that have details
            if audit.get("score", 1) < 0.7 and "details" in audit:
                priority = "High" if audit.get("score", 0) < 0.5 else "Medium"
                
                # Create a recommendation
                rec = {
                    "priority": priority,
                    "title": audit.get("title", "Improve performance issue"),
                    "description": audit.get("description", "")
                }
                
                # Add example for certain audit types
                if audit_id == "render-blocking-resources":
                    rec["example"] = "Use 'async' or 'defer' attributes on script tags or move CSS inline for critical content."
                elif audit_id == "uses-optimized-images":
                    rec["example"] = "Compress images and consider using WebP format."
                elif audit_id == "unused-css-rules":
                    rec["example"] = "Remove or defer loading of unused CSS."
                
                recommendations.append(rec)
        
        # Sort recommendations by priority
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))
        
        return {
            "score": performance_score,
            "findings": findings,
            "recommendations": recommendations[:10]  # Limit to top 10
        }
    
    def _analyze_basic(self):
        """Basic performance analysis without API"""
        # Perform basic checks on the website's loading speed
        start_time = time.time()
        try:
            response = requests.get(self.url, timeout=10)
            page_load_time = time.time() - start_time
            page_size = len(response.content) / 1024  # in KB
            
            # Initialize findings
            findings = {
                "Loading Speed": [],
                "Resources": [],
                "Optimization": [],
            }
            
            # Assess loading time
            if page_load_time < 1:
                loading_type = "success"
                loading_desc = "Excellent! The page loads very quickly."
            elif page_load_time < 3:
                loading_type = "success"
                loading_desc = "Good. The page loads reasonably fast."
            elif page_load_time < 5:
                loading_type = "warning"
                loading_desc = "Fair. The page load time could be improved."
            else:
                loading_type = "error"
                loading_desc = "Poor. The page takes too long to load."
            
            findings["Loading Speed"].append({
                "type": loading_type,
                "title": "Page Load Time",
                "description": f"{page_load_time:.2f} seconds - {loading_desc}"
            })
            
            # Assess page size
            if page_size < 500:
                size_type = "success"
                size_desc = "The page size is small and efficient."
            elif page_size < 1500:
                size_type = "success"
                size_desc = "The page size is reasonable."
            elif page_size < 3000:
                size_type = "warning"
                size_desc = "The page size is somewhat large."
            else:
                size_type = "error"
                size_desc = "The page size is too large, which may slow down loading."
            
            findings["Resources"].append({
                "type": size_type,
                "title": "Page Size",
                "description": f"{page_size:.2f} KB - {size_desc}"
            })
            
            # Check for basic HTTP headers
            cache_control = response.headers.get('Cache-Control')
            if cache_control:
                findings["Optimization"].append({
                    "type": "success",
                    "title": "Cache Control",
                    "description": f"The page uses cache control: {cache_control}"
                })
            else:
                findings["Optimization"].append({
                    "type": "warning",
                    "title": "Cache Control",
                    "description": "No Cache-Control header found. This may affect page load performance on repeat visits."
                })
            
            # Calculate score based on loading time and page size
            if loading_type == "success" and size_type == "success":
                score = 85
            elif loading_type == "success" or size_type == "success":
                score = 70
            elif loading_type == "warning" and size_type == "warning":
                score = 50
            else:
                score = 30
            
            # Generate recommendations
            recommendations = []
            
            if loading_type == "warning" or loading_type == "error":
                recommendations.append({
                    "priority": "High" if loading_type == "error" else "Medium",
                    "title": "Improve page load time",
                    "description": "Optimize resources, reduce server response time, and implement browser caching."
                })
            
            if size_type == "warning" or size_type == "error":
                recommendations.append({
                    "priority": "High" if size_type == "error" else "Medium",
                    "title": "Reduce page size",
                    "description": "Compress images, minify CSS/JS, and remove unnecessary resources."
                })
                
            if not cache_control:
                recommendations.append({
                    "priority": "Medium",
                    "title": "Implement browser caching",
                    "description": "Add Cache-Control headers to improve loading speed for returning visitors."
                })
            
            # Add general performance recommendations
            recommendations.append({
                "priority": "Medium",
                "title": "Use a Content Delivery Network (CDN)",
                "description": "Consider using a CDN to deliver static assets faster to users worldwide."
            })
            
            recommendations.append({
                "priority": "Medium",
                "title": "Optimize images",
                "description": "Compress images and use modern formats like WebP to reduce load times."
            })
            
            return {
                "score": score,
                "findings": findings,
                "recommendations": recommendations
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error during basic performance analysis: {str(e)}")
            
            # Return a default response with error information
            return {
                "score": 0,
                "findings": {
                    "Loading Speed": [{
                        "type": "error",
                        "title": "Connection Error",
                        "description": f"Could not connect to the website: {str(e)}"
                    }],
                    "Resources": [],
                    "Optimization": []
                },
                "recommendations": [{
                    "priority": "High",
                    "title": "Fix connection issues",
                    "description": "Make sure the website is accessible and properly configured."
                }]
            }
