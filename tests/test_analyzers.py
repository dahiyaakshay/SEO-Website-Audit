import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json
from bs4 import BeautifulSoup

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analyzers.seo_analyzer import SEOAnalyzer
from analyzers.performance_analyzer import PerformanceAnalyzer
from analyzers.content_analyzer import ContentAnalyzer
from analyzers.accessibility_analyzer import AccessibilityAnalyzer
from analyzers.security_analyzer import SecurityAnalyzer
from analyzers.design_analyzer import DesignAnalyzer
from utils.scraper import WebScraper

class TestSEOAnalyzer(unittest.TestCase):
    """Tests for the SEO analyzer module"""
    
    def setUp(self):
        # Create a simple test HTML content
        self.test_html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Test Page Title</title>
            <meta name="description" content="This is a test page description">
            <meta name="keywords" content="test, page, keywords">
            <link rel="canonical" href="https://example.com/test">
        </head>
        <body>
            <h1>Main Heading</h1>
            <p>This is a test paragraph with some content.</p>
            <h2>Secondary Heading</h2>
            <p>Another paragraph with <a href="https://example.com">a link</a>.</p>
            <img src="test.jpg" alt="Test image">
        </body>
        </html>
        """
        self.soup = BeautifulSoup(self.test_html, 'html.parser')
        self.url = "https://example.com/test"
    
    def test_check_title(self):
        """Test the title checking functionality"""
        analyzer = SEOAnalyzer(self.soup, self.url)
        result = analyzer._check_title()
        self.assertEqual(result["type"], "success")
        
        # Test with empty title
        soup_empty_title = BeautifulSoup(self.test_html.replace("<title>Test Page Title</title>", "<title></title>"), 'html.parser')
        analyzer = SEOAnalyzer(soup_empty_title, self.url)
        result = analyzer._check_title()
        self.assertEqual(result["type"], "error")
        
        # Test with missing title
        soup_no_title = BeautifulSoup(self.test_html.replace("<title>Test Page Title</title>", ""), 'html.parser')
        analyzer = SEOAnalyzer(soup_no_title, self.url)
        result = analyzer._check_title()
        self.assertEqual(result["type"], "error")
    
    def test_analyze(self):
        """Test the full analysis process"""
        analyzer = SEOAnalyzer(self.soup, self.url)
        result = analyzer.analyze()
        
        # Check if the result has the expected structure
        self.assertIn("score", result)
        self.assertIn("findings", result)
        self.assertIn("recommendations", result)
        
        # Score should be between 0 and 100
        self.assertTrue(0 <= result["score"] <= 100)
        
        # Check if findings include the categories we expect
        findings = result["findings"]
        self.assertIn("Meta Tags", findings)
        self.assertIn("Headings", findings)
        
        # Check if recommendations are generated
        self.assertTrue(len(result["recommendations"]) > 0)

class TestPerformanceAnalyzer(unittest.TestCase):
    """Tests for the Performance analyzer module"""
    
    def setUp(self):
        self.url = "https://example.com/test"
    
    @patch('requests.get')
    def test_check_response_time(self, mock_get):
        """Test response time checking"""
        # Mock the response
        mock_response = MagicMock()
        mock_get.return_value = mock_response
        
        # Setup the analyzer
        analyzer = PerformanceAnalyzer(self.url)
        
        # Test fast response
        with patch('time.time', side_effect=[0, 0.3]):  # Start time, end time
            result = analyzer._check_response_time()
            self.assertEqual(result["type"], "success")
        
        # Test slow response
        with patch('time.time', side_effect=[0, 3.5]):  # Start time, end time
            result = analyzer._check_response_time()
            self.assertEqual(result["type"], "error")
    
    @patch('requests.get')
    def test_analyze(self, mock_get):
        """Test the full analysis process"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.headers = {'Content-Length': '1024'}
        mock_response.text = "<html><body>Test content</body></html>"
        mock_get.return_value = mock_response
        
        # Setup the analyzer
        analyzer = PerformanceAnalyzer(self.url)
        
        # Mock time to simulate response times
        with patch('time.time', side_effect=[0, 0.5, 0, 0.5]):
            result = analyzer.analyze()
            
            # Check if the result has the expected structure
            self.assertIn("score", result)
            self.assertIn("findings", result)
            self.assertIn("recommendations", result)
            
            # Score should be between 0 and 100
            self.assertTrue(0 <= result["score"] <= 100)

class TestContentAnalyzer(unittest.TestCase):
    """Tests for the Content analyzer module"""
    
    def setUp(self):
        # Create a simple test HTML content
        self.test_html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <title>Test Content</title>
        </head>
        <body>
            <h1>Main Heading</h1>
            <p>This is a test paragraph with some content. It contains enough words to test the readability algorithms.
            We need to make sure it has several sentences with varying structures. This will help test the analyzer properly.</p>
            <h2>Secondary Heading</h2>
            <p>Another paragraph with <a href="https://example.com">a link</a>. This paragraph also needs some content to adequately test the content analyzer.</p>
            <ul>
                <li>List item one</li>
                <li>List item two</li>
            </ul>
            <p>A third paragraph to ensure we have enough content for the analyzer to work with.</p>
        </body>
        </html>
        """
        self.soup = BeautifulSoup(self.test_html, 'html.parser')
    
    def test_check_readability(self):
        """Test the readability checking functionality"""
        analyzer = ContentAnalyzer(self.soup)
        content = analyzer._extract_main_content()
        result = analyzer._check_readability(content)
        
        # Check that we get a valid result
        self.assertIn("type", result)
        self.assertIn("title", result)
        self.assertIn("description", result)
    
    def test_analyze(self):
        """Test the full analysis process"""
        analyzer = ContentAnalyzer(self.soup)
        result = analyzer.analyze()
        
        # Check if the result has the expected structure
        self.assertIn("score", result)
        self.assertIn("findings", result)
        self.assertIn("recommendations", result)
        
        # Score should be between a 0 and 100
        self.assertTrue(0 <= result["score"] <= 100)
        
        # Check if findings include the categories we expect
        findings = result["findings"]
        self.assertIn("Readability", findings)
        self.assertIn("Content Quality", findings)

class TestAccessibilityAnalyzer(unittest.TestCase):
    """Tests for the Accessibility analyzer module"""
    
    def setUp(self):
        # Create a simple test HTML content with accessibility issues
        self.test_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Accessibility</title>
        </head>
        <body>
            <h1>Main Heading</h1>
            <img src="test.jpg">
            <div class="button" onclick="doSomething()">Click me</div>
            <form>
                <input type="text" placeholder="Enter your name">
                <input type="submit" value="Submit">
            </form>
        </body>
        </html>
        """
        self.soup = BeautifulSoup(self.test_html, 'html.parser')
    
    def test_check_img_alt_texts(self):
        """Test the image alt text checking functionality"""
        analyzer = AccessibilityAnalyzer(self.soup)
        result = analyzer._check_img_alt_texts()
        
        # Should detect missing alt attributes
        self.assertEqual(result["type"], "error")
        
        # Fix the issue and test again
        soup_fixed = BeautifulSoup(self.test_html.replace('<img src="test.jpg">', '<img src="test.jpg" alt="Test image">'), 'html.parser')
        analyzer = AccessibilityAnalyzer(soup_fixed)
        result = analyzer._check_img_alt_texts()
        
        # Should now pass
        self.assertEqual(result["type"], "success")
    
    def test_analyze(self):
        """Test the full analysis process"""
        analyzer = AccessibilityAnalyzer(self.soup)
        result = analyzer.analyze()
        
        # Check if the result has the expected structure
        self.assertIn("score", result)
        self.assertIn("findings", result)
        self.assertIn("recommendations", result)
        
        # Score should be between 0 and 100
        self.assertTrue(0 <= result["score"] <= 100)
        
        # Check if findings include the categories we expect
        findings = result["findings"]
        self.assertIn("Structure", findings)
        self.assertIn("Media", findings)

class TestSecurityAnalyzer(unittest.TestCase):
    """Tests for the Security analyzer module"""
    
    def setUp(self):
        self.url = "https://example.com/test"
    
    @patch('requests.get')
    def test_check_https(self, mock_get):
        """Test the HTTPS checking functionality"""
        # Mock the response for HTTP URL
        mock_response = MagicMock()
        mock_response.url = "https://example.com/test"  # Simulates a redirect to HTTPS
        mock_get.return_value = mock_response
        
        # Test with HTTPS URL
        analyzer = SecurityAnalyzer("https://example.com/test")
        result = analyzer._check_https()
        self.assertEqual(result["type"], "success")
        
        # Test with HTTP URL (should detect the redirect to HTTPS)
        analyzer = SecurityAnalyzer("http://example.com/test")
        result = analyzer._check_https()
        self.assertEqual(result["type"], "success")
        
        # Test with HTTP URL that doesn't redirect
        mock_response.url = "http://example.com/test"  # No redirect
        analyzer = SecurityAnalyzer("http://example.com/test")
        result = analyzer._check_https()
        self.assertEqual(result["type"], "warning")
    
    @patch('requests.get')
    def test_analyze(self, mock_get):
        """Test the full analysis process"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.url = "https://example.com/test"
        mock_response.headers = {
            'Strict-Transport-Security': 'max-age=31536000',
            'Content-Security-Policy': "default-src 'self'",
            'X-Content-Type-Options': 'nosniff'
        }
        mock_response.text = "<html><body>Test content</body></html>"
        mock_get.return_value = mock_response
        
        # Setup the analyzer with mocked SSL check
        analyzer = SecurityAnalyzer("https://example.com/test")
        with patch.object(analyzer, '_check_ssl_configuration', return_value={
            "type": "success",
            "title": "Strong SSL/TLS configuration",
            "description": "The website uses TLSv1.3, which provides strong security."
        }):
            result = analyzer.analyze()
            
            # Check if the result has the expected structure
            self.assertIn("score", result)
            self.assertIn("findings", result)
            self.assertIn("recommendations", result)
            
            # Score should be between 0 and 100
            self.assertTrue(0 <= result["score"] <= 100)
            
            # Check if findings include the categories we expect
            findings = result["findings"]
            self.assertIn("HTTPS", findings)
            self.assertIn("Headers", findings)

class TestDesignAnalyzer(unittest.TestCase):
    """Tests for the Design analyzer module"""
    
    def setUp(self):
        # Create a simple test HTML content
        self.test_html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Test Design</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; }
                .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
                @media (max-width: 768px) { .container { padding: 10px; } }
            </style>
        </head>
        <body>
            <header>
                <img src="logo.png" alt="Logo">
                <nav>
                    <ul>
                        <li><a href="#" class="active">Home</a></li>
                        <li><a href="#">About</a></li>
                        <li><a href="#">Services</a></li>
                        <li><a href="#">Contact</a></li>
                    </ul>
                </nav>
            </header>
            <main>
                <section class="hero">
                    <h1>Welcome to our website</h1>
                    <p>This is a hero section with a call to action.</p>
                    <a href="#" class="btn">Get Started</a>
                </section>
                <section class="features">
                    <h2>Our Features</h2>
                    <div class="feature-grid">
                        <div class="feature">
                            <h3>Feature 1</h3>
                            <p>Description of feature 1.</p>
                        </div>
                        <div class="feature">
                            <h3>Feature 2</h3>
                            <p>Description of feature 2.</p>
                        </div>
                    </div>
                </section>
            </main>
            <footer>
                <div class="footer-links">
                    <a href="#">Privacy Policy</a>
                    <a href="#">Terms of Service</a>
                    <a href="#">Contact Us</a>
                </div>
                <div class="social-links">
                    <a href="https://facebook.com">Facebook</a>
                    <a href="https://twitter.com">Twitter</a>
                </div>
                <p>&copy; 2023 Example Company</p>
            </footer>
        </body>
        </html>
        """
        self.soup = BeautifulSoup(self.test_html, 'html.parser')
        self.url = "https://example.com/test"
    
    def test_check_layout_structure(self):
        """Test the layout structure checking functionality"""
        analyzer = DesignAnalyzer(self.soup, self.url)
        result = analyzer._check_layout_structure()
        
        # Should detect good semantic structure
        self.assertEqual(result["type"], "success")
        
        # Test with poor structure
        soup_poor = BeautifulSoup("<html><body><div>Content</div></body></html>", 'html.parser')
        analyzer = DesignAnalyzer(soup_poor, self.url)
        result = analyzer._check_layout_structure()
        
        # Should detect poor structure
        self.assertEqual(result["type"], "warning")
    
    def test_check_responsive_design(self):
        """Test the responsive design checking functionality"""
        analyzer = DesignAnalyzer(self.soup, self.url)
        result = analyzer._check_responsive_design()
        
        # Should detect responsive design
        self.assertEqual(result["type"], "success")
        
        # Test without viewport meta
        soup_not_responsive = BeautifulSoup(self.test_html.replace('<meta name="viewport" content="width=device-width, initial-scale=1.0">', ''), 'html.parser')
        analyzer = DesignAnalyzer(soup_not_responsive, self.url)
        result = analyzer._check_responsive_design()
        
        # Should detect missing responsive design
        self.assertEqual(result["type"], "error")
    
    def test_analyze(self):
        """Test the full analysis process"""
        analyzer = DesignAnalyzer(self.soup, self.url)
        result = analyzer.analyze()
        
        # Check if the result has the expected structure
        self.assertIn("score", result)
        self.assertIn("findings", result)
        self.assertIn("recommendations", result)
        
        # Score should be between 0 and 100
        self.assertTrue(0 <= result["score"] <= 100)
        
        # Check if findings include the categories we expect
        findings = result["findings"]
        self.assertIn("Layout", findings)
        self.assertIn("Visual Design", findings)
        self.assertIn("Navigation", findings)

class TestWebScraper(unittest.TestCase):
    """Tests for the WebScraper utility"""
    
    def setUp(self):
        self.url = "https://example.com/test"
    
    @patch('requests.get')
    def test_scrape(self, mock_get):
        """Test the basic scraping functionality"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.text = """
        <!DOCTYPE html>
        <html>
        <head><title>Test Page</title></head>
        <body><h1>Hello World</h1></body>
        </html>
        """
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_get.return_value = mock_response
        
        # Test scraping
        scraper = WebScraper(self.url)
        result = scraper.scrape()
        
        # Check that we got a BeautifulSoup object
        self.assertIsInstance(result, BeautifulSoup)
        
        # Check that content was parsed properly
        self.assertEqual(result.title.text, "Test Page")
        self.assertEqual(result.h1.text, "Hello World")
    
    @patch('requests.get')
    def test_get_all_links(self, mock_get):
        """Test the link extraction functionality"""
        # Mock the response with various links
        mock_response = MagicMock()
        mock_response.text = """
        <!DOCTYPE html>
        <html>
        <body>
            <a href="https://example.com/page1">Internal Link 1</a>
            <a href="/page2">Internal Link 2</a>
            <a href="https://external.com">External Link</a>
            <a href="#section">Anchor Link</a>
            <a href="mailto:info@example.com">Email Link</a>
        </body>
        </html>
        """
        mock_get.return_value = mock_response
        
        # Test link extraction
        scraper = WebScraper(self.url)
        result = scraper.get_all_links(BeautifulSoup(mock_response.text, 'html.parser'))
        
        # Check the extracted links
        self.assertEqual(len(result['internal']), 2)  # Two internal links
        self.assertEqual(len(result['external']), 1)  # One external link
        
        # The anchor and mailto links should be filtered out

if __name__ == '__main__':
    unittest.main()
