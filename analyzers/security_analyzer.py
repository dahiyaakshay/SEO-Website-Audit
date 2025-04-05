import requests
import re
from urllib.parse import urlparse
import socket
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SecurityAnalyzer:
    """Analyzes website security aspects"""
    
    def __init__(self, url):
        """
        Initialize the security analyzer
        
        Args:
            url (str): The URL to analyze
        """
        self.url = url
        self.parsed_url = urlparse(url)
        self.domain = self.parsed_url.netloc
    
    def analyze(self):
        """
        Perform security analysis
        
        Returns:
            dict: Analysis results with score, findings, and recommendations
        """
        findings = {
            "HTTPS": [],
            "Headers": [],
            "Content": [],
            "Configuration": []
        }
        
        # Check HTTPS
        https_result = self._check_https()
        findings["HTTPS"].append(https_result)
        
        # Check SSL/TLS configuration
        ssl_result = self._check_ssl_configuration()
        findings["HTTPS"].append(ssl_result)
        
        # Check security headers
        headers_result = self._check_security_headers()
        findings["Headers"].extend(headers_result)
        
        # Check for information disclosure
        info_disclosure_result = self._check_information_disclosure()
        findings["Content"].append(info_disclosure_result)
        
        # Check for forms security
        forms_result = self._check_forms_security()
        findings["Content"].append(forms_result)
        
        # Check for common security misconfigurations
        config_result = self._check_security_configs()
        findings["Configuration"].extend(config_result)
        
        # Calculate score
        score = self._calculate_score(findings)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(findings)
        
        return {
            "score": score,
            "findings": findings,
            "recommendations": recommendations
        }
    
    def _check_https(self):
        """Check if the website uses HTTPS"""
        if self.parsed_url.scheme != 'https':
            return {
                "type": "error",
                "title": "HTTPS not implemented",
                "description": "The website does not use HTTPS encryption, which puts user data at risk."
            }
        
        try:
            # Try to connect to HTTP version and check if it redirects to HTTPS
            http_url = f"http://{self.domain}"
            response = requests.get(http_url, timeout=10, allow_redirects=True)
            
            final_url = response.url
            
            if final_url.startswith('https://'):
                return {
                    "type": "success",
                    "title": "HTTPS properly implemented with redirect",
                    "description": "The website uses HTTPS and correctly redirects HTTP requests to HTTPS."
                }
            else:
                return {
                    "type": "warning",
                    "title": "HTTPS implemented but without redirect",
                    "description": "The website supports HTTPS but does not redirect HTTP requests to HTTPS."
                }
        except requests.exceptions.RequestException:
            # If HTTP request fails, at least HTTPS is working
            return {
                "type": "success",
                "title": "HTTPS implemented",
                "description": "The website uses HTTPS encryption to protect user data."
            }
    
    def _check_ssl_configuration(self):
        """Check SSL/TLS configuration security"""
        if self.parsed_url.scheme != 'https':
            return {
                "type": "error",
                "title": "No SSL/TLS",
                "description": "The website does not use SSL/TLS encryption."
            }
        
        try:
            import ssl
            import socket
            
            hostname = self.domain
            context = ssl.create_default_context()
            
            with socket.create_connection((hostname, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    # Get the certificate
                    cert = ssock.getpeercert()
                    
                    # Check expiration
                    from datetime import datetime
                    import time
                    
                    not_after = cert.get('notAfter')
                    if not_after:
                        # Parse the date in the format provided by getpeercert()
                        expire_date = ssl.cert_time_to_seconds(not_after)
                        current_time = time.time()
                        days_left = (expire_date - current_time) / (60 * 60 * 24)
                        
                        if days_left <= 0:
                            return {
                                "type": "error",
                                "title": "SSL certificate expired",
                                "description": f"The SSL certificate has expired."
                            }
                        elif days_left < 30:
                            return {
                                "type": "warning",
                                "title": "SSL certificate expiring soon",
                                "description": f"The SSL certificate will expire in {days_left:.0f} days."
                            }
                    
                    # Check protocol version
                    protocol_version = ssock.version()
                    
                    if protocol_version in ['TLSv1.3']:
                        return {
                            "type": "success",
                            "title": "Strong SSL/TLS configuration",
                            "description": f"The website uses {protocol_version}, which provides strong security."
                        }
                    elif protocol_version in ['TLSv1.2']:
                        return {
                            "type": "success",
                            "title": "Good SSL/TLS configuration",
                            "description": f"The website uses {protocol_version}, which is currently secure."
                        }
                    elif protocol_version in ['TLSv1.1', 'TLSv1']:
                        return {
                            "type": "warning",
                            "title": "Outdated SSL/TLS version",
                            "description": f"The website uses {protocol_version}, which is outdated and less secure."
                        }
                    else:
                        return {
                            "type": "error",
                            "title": "Insecure SSL/TLS version",
                            "description": f"The website uses {protocol_version}, which is considered insecure."
                        }
        except (socket.error, ssl.SSLError, ConnectionRefusedError) as e:
            return {
                "type": "warning",
                "title": "Could not verify SSL/TLS configuration",
                "description": f"Unable to check SSL/TLS configuration: {str(e)}"
            }
        except Exception as e:
            # If we got this far, at least HTTPS is working
            return {
                "type": "success",
                "title": "HTTPS implemented",
                "description": "The website uses HTTPS encryption, but detailed SSL/TLS configuration could not be checked."
            }
    
    def _check_security_headers(self):
        """Check important security headers"""
        try:
            response = requests.get(self.url, timeout=10)
            headers = response.headers
            
            # Define security headers to check
            security_headers = {
                'Strict-Transport-Security': {
                    'title': 'HTTP Strict Transport Security (HSTS)',
                    'description': 'Ensures the browser always uses HTTPS connections to the site',
                    'recommended': 'max-age=31536000; includeSubDomains'
                },
                'Content-Security-Policy': {
                    'title': 'Content Security Policy (CSP)',
                    'description': 'Prevents Cross-Site Scripting (XSS) and other code injection attacks',
                    'recommended': 'Customized per site needs'
                },
                'X-Content-Type-Options': {
                    'title': 'X-Content-Type-Options',
                    'description': 'Prevents MIME type sniffing',
                    'recommended': 'nosniff'
                },
                'X-Frame-Options': {
                    'title': 'X-Frame-Options',
                    'description': 'Prevents clickjacking attacks',
                    'recommended': 'DENY or SAMEORIGIN'
                },
                'X-XSS-Protection': {
                    'title': 'X-XSS-Protection',
                    'description': 'Provides some XSS protection in older browsers',
                    'recommended': '1; mode=block'
                },
                'Referrer-Policy': {
                    'title': 'Referrer-Policy',
                    'description': 'Controls what information is sent in the Referer header',
                    'recommended': 'strict-origin-when-cross-origin or no-referrer'
                },
                'Permissions-Policy': {
                    'title': 'Permissions-Policy',
                    'description': 'Controls which browser features can be used (formerly Feature-Policy)',
                    'recommended': 'Customized per site needs'
                }
            }
            
            findings = []
            
            # Check each security header
            for header, details in security_headers.items():
                header_value = headers.get(header)
                
                if not header_value:
                    # Also check for renamed/alternative headers
                    if header == 'Permissions-Policy' and headers.get('Feature-Policy'):
                        header_value = headers.get('Feature-Policy')
                
                if header_value:
                    findings.append({
                        "type": "success",
                        "title": f"{details['title']} implemented",
                        "description": f"{details['description']}. Current value: {header_value}"
                    })
                else:
                    # Prioritize headers differently
                    if header in ['Strict-Transport-Security', 'Content-Security-Policy']:
                        finding_type = "warning"
                    else:
                        finding_type = "warning"
                    
                    findings.append({
                        "type": finding_type,
                        "title": f"Missing {details['title']}",
                        "description": f"{details['description']}. Recommended value: {details['recommended']}"
                    })
            
            return findings
            
        except requests.exceptions.RequestException as e:
            return [{
                "type": "warning",
                "title": "Could not check security headers",
                "description": f"Unable to retrieve headers: {str(e)}"
            }]
    
    def _check_information_disclosure(self):
        """Check for sensitive information disclosure in HTML source"""
        try:
            response = requests.get(self.url, timeout=10)
            html_content = response.text.lower()
            
            # Patterns for potentially sensitive information
            patterns = {
                'Email addresses': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
                'Server information': r'server:\s*([^\r\n]+)',
                'Database errors': r'(sql syntax|mysql error|pg_query|db_query)',
                'Internal paths': r'(\/var\/www\/|c:\\inetpub|\\\\server)',
                'API keys': r'(api[_-]key|apikey|access[_-]key|auth[_-]token)["\']?\s*[:=]\s*["\']([\w\d_\.\-]+)["\']',
                'Debug information': r'(debug|trace|error|exception|stack trace|stacktrace)',
                'Version numbers': r'(version|v)[=:]["\']?(\d+\.\d+\.\d+)'
            }
            
            disclosures = []
            
            # Check response headers for server info
            if 'Server' in response.headers:
                server_info = response.headers['Server']
                if len(server_info) > 3:  # Not a minimal value like "nginx"
                    disclosures.append(f"Server header reveals: {server_info}")
            
            # Check HTML content for patterns
            for desc, pattern in patterns.items():
                matches = re.findall(pattern, html_content)
                if matches:
                    # For email patterns, we need to filter out common patterns like example@example.com
                    if desc == 'Email addresses':
                        matches = [m for m in matches if not ('example' in m or 'user' in m or 'domain' in m)]
                    
                    if matches and len(matches) > 0:
                        # Limit the number of examples to show
                        if isinstance(matches[0], tuple):
                            # Some regex patterns return tuples
                            sample = [m[0] for m in matches[:3]]
                        else:
                            sample = matches[:3]
                        
                        disclosures.append(f"{desc} found: {', '.join(sample)}")
            
            if disclosures:
                return {
                    "type": "warning",
                    "title": "Information disclosure detected",
                    "description": f"Found {len(disclosures)} potential information leaks: " + "; ".join(disclosures)
                }
            else:
                return {
                    "type": "success",
                    "title": "No information disclosure detected",
                    "description": "No obvious sensitive information found in the HTML source or headers."
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "type": "warning",
                "title": "Could not check for information disclosure",
                "description": f"Unable to analyze page content: {str(e)}"
            }
    
    def _check_forms_security(self):
        """Check forms for secure implementation"""
        try:
            response = requests.get(self.url, timeout=10)
            html_content = response.text
            
            # Simple check for forms with sensitive actions
            login_forms = re.findall(r'<form[^>]*(?:login|signin|auth)[^>]*>', html_content, re.IGNORECASE)
            signup_forms = re.findall(r'<form[^>]*(?:register|signup|join)[^>]*>', html_content, re.IGNORECASE)
            payment_forms = re.findall(r'<form[^>]*(?:payment|checkout|billing)[^>]*>', html_content, re.IGNORECASE)
            
            sensitive_forms = login_forms + signup_forms + payment_forms
            
            if not sensitive_forms:
                return {
                    "type": "success",
                    "title": "No sensitive forms detected",
                    "description": "No login, registration, or payment forms were found to check."
                }
            
            # Check for insecure attributes
            insecure_http_forms = []
            missing_csrf = []
            
            for form in sensitive_forms:
                # Check for HTTP action
                action_match = re.search(r'action=["\']([^"\']+)["\']', form)
                if action_match:
                    action = action_match.group(1)
                    if action.startswith('http:'):
                        insecure_http_forms.append(action)
                
                # Basic check for CSRF protection (this is a simple heuristic)
                has_token = re.search(r'csrf|token|nonce', form, re.IGNORECASE)
                if not has_token:
                    missing_csrf.append(form[:50] + "...")
            
            issues = []
            
            if insecure_http_forms:
                issues.append(f"Found {len(insecure_http_forms)} forms submitting data over insecure HTTP")
            
            if missing_csrf:
                issues.append(f"Found {len(missing_csrf)} forms without obvious CSRF protection")
            
            if issues:
                return {
                    "type": "warning",
                    "title": "Potential form security issues",
                    "description": ". ".join(issues)
                }
            else:
                return {
                    "type": "success",
                    "title": "Forms appear to be secure",
                    "description": f"Found {len(sensitive_forms)} sensitive forms with no obvious security issues."
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "type": "warning",
                "title": "Could not check form security",
                "description": f"Unable to analyze page forms: {str(e)}"
            }
    
    def _check_security_configs(self):
        """Check for common security configurations and issues"""
        findings = []
        
        # Check for robots.txt
        try:
            robots_url = f"{self.parsed_url.scheme}://{self.domain}/robots.txt"
            robots_response = requests.get(robots_url, timeout=5)
            
            if robots_response.status_code == 200:
                # Check for sensitive paths
                robots_content = robots_response.text
                sensitive_paths = re.findall(r'Disallow:\s*(/[^\s]+)', robots_content)
                
                if sensitive_paths:
                    findings.append({
                        "type": "warning",
                        "title": "Sensitive paths in robots.txt",
                        "description": f"Found {len(sensitive_paths)} potentially sensitive paths in robots.txt, " +
                                    f"including: {', '.join(sensitive_paths[:3])}"
                    })
                else:
                    findings.append({
                        "type": "success",
                        "title": "robots.txt properly configured",
                        "description": "The robots.txt file exists and doesn't expose sensitive paths."
                    })
        except requests.exceptions.RequestException:
            # Not having robots.txt is not a security issue
            pass
        
        # Check for security.txt
        try:
            # Check in both locations as per RFC
            security_urls = [
                f"{self.parsed_url.scheme}://{self.domain}/.well-known/security.txt",
                f"{self.parsed_url.scheme}://{self.domain}/security.txt"
            ]
            
            security_found = False
            for security_url in security_urls:
                try:
                    security_response = requests.get(security_url, timeout=5)
                    if security_response.status_code == 200:
                        security_found = True
                        findings.append({
                            "type": "success",
                            "title": "security.txt implemented",
                            "description": "The website has a security.txt file for responsible disclosure of security vulnerabilities."
                        })
                        break
                except:
                    continue
            
            if not security_found:
                findings.append({
                    "type": "warning",
                    "title": "No security.txt file",
                    "description": "The website doesn't have a security.txt file for vulnerability disclosure."
                })
        except Exception:
            # Ignore errors here
            pass
        
        # Check for exposed git/svn directories
        try:
            git_url = f"{self.parsed_url.scheme}://{self.domain}/.git/HEAD"
            git_response = requests.get(git_url, timeout=5)
            
            if git_response.status_code == 200 and "ref:" in git_response.text:
                findings.append({
                    "type": "error",
                    "title": "Exposed Git repository",
                    "description": "The website has an exposed Git repository, which could leak source code and sensitive information."
                })
        except requests.exceptions.RequestException:
            # No exposed git repository is good
            pass
        
        # Check for directory listing
        common_dirs = ['images', 'js', 'css', 'uploads', 'assets', 'includes']
        exposed_dirs = []
        
        for directory in common_dirs:
            try:
                dir_url = f"{self.parsed_url.scheme}://{self.domain}/{directory}/"
                dir_response = requests.get(dir_url, timeout=5)
                
                # Check if directory listing is enabled
                if dir_response.status_code == 200:
                    if "Index of /" in dir_response.text or "<title>Index of" in dir_response.text:
                        exposed_dirs.append(directory)
            except requests.exceptions.RequestException:
                continue
        
        if exposed_dirs:
            findings.append({
                "type": "warning",
                "title": "Directory listing enabled",
                "description": f"Directory listing is enabled for these directories: {', '.join(exposed_dirs)}. " +
                           "This may expose sensitive files."
            })
        
        return findings
    
    def _calculate_score(self, findings):
        """Calculate overall security score based on findings"""
        
        # Define weights for different categories
        weights = {
            "HTTPS": 0.4,
            "Headers": 0.3,
            "Content": 0.15,
            "Configuration": 0.15
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
        
        if "https not implemented" in title:
            return "Implement HTTPS encryption by obtaining an SSL/TLS certificate from a trusted CA and configuring your web server to use it."
        
        elif "https implemented but without redirect" in title:
            return "Configure your web server to redirect all HTTP traffic to HTTPS using a 301 redirect."
        
        elif "ssl certificate expired" in title or "ssl certificate expiring soon" in title:
            return "Renew your SSL/TLS certificate as soon as possible and set up automated renewal reminders."
        
        elif "outdated ssl/tls version" in title:
            return "Update your server configuration to use TLS 1.2 or 1.3 and disable older protocols (SSL 3.0, TLS 1.0, TLS 1.1)."
        
        elif "missing http strict transport security" in title:
            return "Implement HSTS by adding the 'Strict-Transport-Security' header with a value of 'max-age=31536000; includeSubDomains'."
        
        elif "missing content security policy" in title:
            return "Implement a Content Security Policy to prevent XSS attacks by adding the 'Content-Security-Policy' header with appropriate directives."
        
        elif "missing x-content-type-options" in title:
            return "Add the 'X-Content-Type-Options: nosniff' header to prevent MIME type sniffing."
        
        elif "missing x-frame-options" in title:
            return "Add the 'X-Frame-Options: DENY' header to prevent clickjacking attacks."
        
        elif "information disclosure detected" in title:
            return "Remove sensitive information such as server details, internal paths, and debug information from your HTML source and HTTP headers."
        
        elif "potential form security issues" in title:
            return "Ensure all forms use HTTPS, implement CSRF protection, and validate input on both client and server side."
        
        elif "exposed git repository" in title:
            return "Immediately restrict access to your .git directory by configuring your web server to deny access to these paths."
        
        elif "directory listing enabled" in title:
            return "Disable directory listing in your web server configuration to prevent exposure of file structures."
        
        # Generic recommendations based on finding type
        if finding.get("type") == "error":
            return finding.get("description", "Fix this critical security issue to protect your website and users.")
        else:
            return finding.get("description", "Address this security issue to improve your website's protection.")
