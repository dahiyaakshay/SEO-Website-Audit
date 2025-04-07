import re
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse, urljoin
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DesignAnalyzer:
    """Analyzes website design and user experience aspects"""
    
    def __init__(self, page_content, url):
        """
        Initialize the design analyzer
        
        Args:
            page_content (BeautifulSoup): The parsed HTML content
            url (str): The URL of the page being analyzed
        """
        self.soup = page_content
        self.url = url
        self.parsed_url = urlparse(url)
        self.domain = self.parsed_url.netloc
    
    def analyze(self):
        """
        Perform design and UX analysis
        
        Returns:
            dict: Analysis results with score, findings, and recommendations
        """
        findings = {
            "Layout": [],
            "Visual Design": [],
            "Navigation": [],
            "Mobile": [],
            "Branding": []
        }
        
        # Check layout structure
        layout_result = self._check_layout_structure()
        findings["Layout"].append(layout_result)
        
        # Check responsive design
        responsive_result = self._check_responsive_design()
        findings["Mobile"].append(responsive_result)
        
        # Check navigation usability
        nav_result = self._check_navigation()
        findings["Navigation"].append(nav_result)
        
        # Check typography
        typography_result = self._check_typography()
        findings["Visual Design"].append(typography_result)
        
        # Check color usage
        color_result = self._check_colors()
        findings["Visual Design"].append(color_result)
        
        # Check spacing consistency
        spacing_result = self._check_spacing()
        findings["Visual Design"].append(spacing_result)
        
        # Check image quality
        images_result = self._check_images()
        findings["Visual Design"].append(images_result)
        
        # Check call-to-action elements
        cta_result = self._check_cta_elements()
        findings["Layout"].append(cta_result)
        
        # Check branding consistency
        branding_result = self._check_branding()
        findings["Branding"].append(branding_result)
        
        # Check footer usability
        footer_result = self._check_footer()
        findings["Navigation"].append(footer_result)
        
        # Calculate score
        score = self._calculate_score(findings)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(findings)
        
        return {
            "score": score,
            "findings": findings,
            "recommendations": recommendations
        }
    
    def _check_layout_structure(self):
        """Check if the page has a clear structure and layout"""
        
        # Look for main structural elements
        header = self.soup.find(['header', 'div[role="banner"]', '.header', '#header'])
        main_content = self.soup.find(['main', 'div[role="main"]', 'article', '.content', '#content'])
        footer = self.soup.find(['footer', 'div[role="contentinfo"]', '.footer', '#footer'])
        
        # Count the number of structural elements found
        structure_count = sum(1 for elem in [header, main_content, footer] if elem)
        
        # Check for proper HTML5 semantic elements
        semantic_elements = self.soup.find_all(['header', 'nav', 'main', 'section', 'article', 'aside', 'footer'])
        
        # Check for clear visual sections (using divs with classes/IDs suggesting sections)
        section_patterns = [
            'section', 'container', 'wrapper', 'block', 'module', 'panel', 'row', 'group'
        ]
        
        div_sections = self.soup.find_all('div', class_=lambda c: c and any(pattern in str(c).lower() for pattern in section_patterns))
        div_sections += self.soup.find_all('div', id=lambda i: i and any(pattern in str(i).lower() for pattern in section_patterns))
        
        # Combine semantic elements and div sections
        total_sections = len(semantic_elements) + len(div_sections)
        
        if structure_count < 2:
            return {
                "type": "warning",
                "title": "Poor page structure",
                "description": "The page lacks clear structural elements (header, main content, footer), which can confuse users."
            }
        elif total_sections < 3:
            return {
                "type": "warning",
                "title": "Limited content structure",
                "description": "The page has basic structure but lacks clear content sections, which can make content hard to scan."
            }
        elif len(semantic_elements) > 5:
            return {
                "type": "success",
                "title": "Good semantic structure",
                "description": f"The page uses {len(semantic_elements)} semantic HTML5 elements which creates clear structure."
            }
        else:
            return {
                "type": "success",
                "title": "Clear page structure",
                "description": f"The page has a clear structure with {total_sections} identifiable sections."
            }
    
    def _check_responsive_design(self):
        """Check if the page is designed responsively"""
        
        # Check for viewport meta tag
        viewport_meta = self.soup.find('meta', attrs={'name': 'viewport'})
        
        if not viewport_meta:
            return {
                "type": "error",
                "title": "Not mobile-friendly",
                "description": "The page doesn't have a viewport meta tag, which is essential for responsive design."
            }
        
        viewport_content = viewport_meta.get('content', '')
        
        # Check for width=device-width in viewport
        if 'width=device-width' not in viewport_content:
            return {
                "type": "warning",
                "title": "Incomplete responsive setup",
                "description": "The viewport meta tag doesn't include 'width=device-width', which helps adapt to different screen sizes."
            }
        
        # Check for responsive frameworks
        bootstrap_usage = bool(self.soup.find_all(class_=lambda c: c and 'container' in str(c) and ('row' in str(c) or 'col-' in str(c))))
        foundation_usage = bool(self.soup.find_all(class_=lambda c: c and ('grid-' in str(c) or 'small-' in str(c) or 'medium-' in str(c) or 'large-' in str(c))))
        tailwind_usage = bool(self.soup.find_all(class_=lambda c: c and any(p in str(c) for p in ['sm:', 'md:', 'lg:', 'xl:'])))
        other_responsive = bool(self.soup.find_all(class_=lambda c: c and any(p in str(c) for p in ['mobile-', 'tablet-', 'desktop-'])))
        
        # Check for media queries in style tags
        media_queries = False
        for style in self.soup.find_all('style'):
            if style.string and '@media' in style.string:
                media_queries = True
                break
        
        # Determine level of responsive design
        frameworks_used = sum(1 for usage in [bootstrap_usage, foundation_usage, tailwind_usage, other_responsive] if usage)
        
        if frameworks_used > 0 or media_queries:
            return {
                "type": "success",
                "title": "Responsive design implemented",
                "description": f"The page uses responsive design techniques{', including a CSS framework' if frameworks_used else ''}."
            }
        
        # Check for fixed-width elements
        fixed_width_elements = 0
        for elem in self.soup.find_all(['div', 'table', 'section']):
            style = elem.get('style', '')
            if style and ('width:' in style and 'px' in style):
                fixed_width_elements += 1
        
        if fixed_width_elements > 3:
            return {
                "type": "warning",
                "title": "Many fixed-width elements",
                "description": f"Found {fixed_width_elements} elements with fixed pixel widths, which may not adapt well to mobile screens."
            }
        
        return {
            "type": "warning",
            "title": "Basic responsive setup",
            "description": "The page has a viewport meta tag but shows limited evidence of comprehensive responsive design techniques."
        }
    
    def _check_navigation(self):
        """Check navigation usability"""
        
        # Look for navigation elements
        main_nav = self.soup.find(['nav', 'div[role="navigation"]', 'ul.menu', 'ul.nav', '#menu', '#navigation', '.navigation'])
        
        if not main_nav:
            return {
                "type": "warning",
                "title": "Navigation not clearly defined",
                "description": "Could not identify a clear navigation element, which may make the site difficult to explore."
            }
        
        # Count navigation links
        nav_links = main_nav.find_all('a')
        
        if not nav_links:
            return {
                "type": "warning",
                "title": "No navigation links found",
                "description": "The navigation area doesn't contain any links."
            }
        
        # Check number of navigation items
        if len(nav_links) > 9:
            return {
                "type": "warning",
                "title": "Too many navigation items",
                "description": f"The navigation has {len(nav_links)} items, which may overwhelm users. Best practice is 5-7 items."
            }
        
        # Check for active/current page indication
        has_active_indicator = bool(main_nav.find_all(class_=lambda c: c and any(a in str(c).lower() for a in ['active', 'current', 'selected'])))
        
        # Check for dropdown or mobile menu
        has_dropdown = bool(main_nav.find_all(class_=lambda c: c and any(d in str(c).lower() for d in ['dropdown', 'submenu', 'menu-item-has-children'])))
        has_mobile_toggle = bool(self.soup.find_all(class_=lambda c: c and any(m in str(c).lower() for m in ['menu-toggle', 'navbar-toggle', 'hamburger'])))
        
        if has_active_indicator and (has_dropdown or has_mobile_toggle):
            return {
                "type": "success",
                "title": "Good navigation design",
                "description": f"The {len(nav_links)}-item navigation is well-structured with active page indication and dropdown/mobile support."
            }
        elif has_active_indicator:
            return {
                "type": "success",
                "title": "Clear navigation",
                "description": f"The {len(nav_links)}-item navigation clearly indicates the current page."
            }
        else:
            return {
                "type": "warning",
                "title": "Basic navigation",
                "description": f"The {len(nav_links)}-item navigation could be improved with clearer current page indication."
            }
    
    def _check_typography(self):
        """Check typography for readability and consistency"""
        
        # Extract font families from inline styles and style tags
        font_families = set()
        
        # Check inline styles
        for elem in self.soup.find_all(style=True):
            style = elem['style']
            if 'font-family' in style:
                # Extract font family
                match = re.search(r'font-family:\s*([^;]+)', style)
                if match:
                    font_families.add(match.group(1).strip())
        
        # Check style tags
        for style in self.soup.find_all('style'):
            if style.string:
                # Extract font families
                for match in re.findall(r'font-family:\s*([^;]+)', style.string):
                    font_families.add(match.strip())
        
        # Count different font families
        num_fonts = len(font_families)
        
        # Check for common readability issues
        small_text = 0
        for elem in self.soup.find_all(style=True):
            style = elem['style']
            if 'font-size' in style:
                match = re.search(r'font-size:\s*(\d+)px', style)
                if match and int(match.group(1)) < 12:
                    small_text += 1
        
        # Check line height for readability
        poor_line_height = 0
        for elem in self.soup.find_all(style=True):
            style = elem['style']
            if 'line-height' in style:
                match = re.search(r'line-height:\s*([\d\.]+)(px|em|%)?', style)
                if match:
                    value = float(match.group(1))
                    unit = match.group(2) if match.group(2) else ''
                    
                    if unit == 'px' or not unit:
                        # For px or unitless, recommend at least 1.5
                        if value < 1.4:
                            poor_line_height += 1
                    elif unit == 'em' or unit == '%':
                        # For em or %, convert to unitless
                        em_value = value if unit == 'em' else value / 100
                        if em_value < 1.4:
                            poor_line_height += 1
        
        # Make a finding based on the analysis
        issues = []
        
        if num_fonts > 3:
            issues.append(f"Uses {num_fonts} different font families; 2-3 is recommended")
        
        if small_text > 0:
            issues.append(f"Contains {small_text} instances of text smaller than 12px")
        
        if poor_line_height > 0:
            issues.append(f"Contains {poor_line_height} instances of tight line spacing")
        
        if issues:
            return {
                "type": "warning",
                "title": "Typography issues detected",
                "description": ". ".join(issues) + ". These issues can affect readability and user experience."
            }
        
        if num_fonts == 0:
            return {
                "type": "success",
                "title": "Basic typography",
                "description": "The page uses default fonts with no obvious readability issues."
            }
        else:
            return {
                "type": "success",
                "title": "Good typography",
                "description": f"The page uses {num_fonts} font families with no obvious readability issues."
            }
    
    def _check_colors(self):
        """Check color usage for consistency and contrast"""
        
        # This is a basic check without rendering, so we'll focus on color declarations
        
        # Extract colors from inline styles and style tags
        colors = set()
        background_colors = set()
        
        # Check inline styles
        for elem in self.soup.find_all(style=True):
            style = elem['style']
            
            # Extract colors
            if 'color:' in style and 'background-color' not in style:
                match = re.search(r'color:\s*([^;]+)', style)
                if match:
                    colors.add(match.group(1).strip())
            
            # Extract background colors
            if 'background-color' in style:
                match = re.search(r'background-color:\s*([^;]+)', style)
                if match:
                    background_colors.add(match.group(1).strip())
            
            if 'background:' in style:
                match = re.search(r'background:\s*([^;]+)', style)
                if match and any(c in match.group(1) for c in ['#', 'rgb', 'hsl']):
                    background_colors.add(match.group(1).strip())
        
        # Check style tags
        for style in self.soup.find_all('style'):
            if style.string:
                # Extract text colors
                for match in re.findall(r'color:\s*([^;]+)', style.string):
                    if 'background' not in match:
                        colors.add(match.strip())
                
                # Extract background colors
                for match in re.findall(r'background-color:\s*([^;]+)', style.string):
                    background_colors.add(match.strip())
                
                for match in re.findall(r'background:\s*([^;]+)', style.string):
                    if any(c in match for c in ['#', 'rgb', 'hsl']):
                        background_colors.add(match.strip())
        
        # Count different colors
        num_text_colors = len(colors)
        num_bg_colors = len(background_colors)
        total_colors = num_text_colors + num_bg_colors
        
        # Make a finding based on the analysis
        if total_colors > 10:
            return {
                "type": "warning",
                "title": "Inconsistent color usage",
                "description": f"The page uses {total_colors} different colors ({num_text_colors} text, {num_bg_colors} background), which may create visual inconsistency."
            }
        elif total_colors == 0:
            return {
                "type": "warning",
                "title": "Limited color customization",
                "description": "The page appears to use default colors with little customization."
            }
        elif total_colors < 3:
            return {
                "type": "warning",
                "title": "Minimal color palette",
                "description": f"The page uses only {total_colors} colors, which may lack visual interest."
            }
        else:
            return {
                "type": "success",
                "title": "Balanced color usage",
                "description": f"The page uses approximately {total_colors} colors, which is a good range for visual hierarchy while maintaining consistency."
            }
    
    def _check_spacing(self):
        """Check spacing and whitespace usage"""
        
        # This is a simplified check without rendering
        
        # Check inline styles for margin and padding
        inconsistent_spacing = 0
        consistent_units = True
        spacing_values = []
        
        # Track units for consistency check
        margin_units = set()
        padding_units = set()
        
        # Check inline styles
        for elem in self.soup.find_all(style=True):
            style = elem['style']
            
            # Check margins
            if 'margin' in style:
                matches = re.findall(r'margin(?:-(?:top|right|bottom|left))?:\s*(\d+)(px|em|rem|%)', style)
                for match in matches:
                    value, unit = match
                    spacing_values.append(int(value))
                    margin_units.add(unit)
            
            # Check padding
            if 'padding' in style:
                matches = re.findall(r'padding(?:-(?:top|right|bottom|left))?:\s*(\d+)(px|em|rem|%)', style)
                for match in matches:
                    value, unit = match
                    spacing_values.append(int(value))
                    padding_units.add(unit)
        
        # Check if multiple unit types are used
        if len(margin_units) > 1 or len(padding_units) > 1:
            consistent_units = False
        
        # Check for consistent spacing values
        if spacing_values:
            # Convert to set to get unique values
            unique_values = set(spacing_values)
            
            # Check if there are too many different spacing values
            if len(unique_values) > 7:  # more than 7 different spacing values is often inconsistent
                inconsistent_spacing = len(unique_values)
        
        # Check paragraphs for spacing
        paragraphs = self.soup.find_all('p')
        
        # Make a finding based on the analysis
        if not consistent_units:
            return {
                "type": "warning",
                "title": "Inconsistent spacing units",
                "description": "The page uses multiple different units (px, em, rem, %) for spacing, which can lead to inconsistent layout."
            }
        elif inconsistent_spacing > 0:
            return {
                "type": "warning",
                "title": "Inconsistent spacing values",
                "description": f"Found {inconsistent_spacing} different spacing values, suggesting a lack of a consistent spacing system."
            }
        elif not spacing_values and len(paragraphs) > 3:
            return {
                "type": "warning",
                "title": "Default spacing",
                "description": "The page appears to use default browser spacing with minimal customization."
            }
        else:
            return {
                "type": "success",
                "title": "Consistent spacing",
                "description": "The page appears to use a consistent approach to spacing and whitespace."
            }
    
    def _check_images(self):
        """Check image quality and usage"""
        
        # Find all images
        images = self.soup.find_all('img')
        
        if not images:
            return {
                "type": "success",
                "title": "No images to analyze",
                "description": "The page doesn't contain any images to assess."
            }
        
        # Count images with alt text
        with_alt = sum(1 for img in images if img.get('alt'))
        
        # Check for responsive images
        responsive_images = sum(1 for img in images if img.get('srcset') or img.get('sizes'))
        
        # Check for width and height attributes
        with_dimensions = sum(1 for img in images if img.get('width') and img.get('height'))
        
        # Look for lazy loading
        lazy_loaded = sum(1 for img in images if img.get('loading') == 'lazy' or 'lazyload' in img.get('class', []))
        
        # Calculate percentages
        total_images = len(images)
        alt_percentage = (with_alt / total_images) * 100 if total_images > 0 else 0
        responsive_percentage = (responsive_images / total_images) * 100 if total_images > 0 else 0
        dimensions_percentage = (with_dimensions / total_images) * 100 if total_images > 0 else 0
        
        # Build finding based on results
        if alt_percentage < 50:
            return {
                "type": "warning",
                "title": "Poor image accessibility",
                "description": f"Only {alt_percentage:.0f}% of images have alt text. All images should have descriptive alt text for accessibility."
            }
        
        positive_aspects = []
        if alt_percentage > 90:
            positive_aspects.append(f"{alt_percentage:.0f}% have good alt text")
        
        if responsive_percentage > 50:
            positive_aspects.append(f"{responsive_percentage:.0f}% use responsive image techniques")
        
        if dimensions_percentage > 80:
            positive_aspects.append(f"{dimensions_percentage:.0f}% define dimensions to prevent layout shifts")
        
        if lazy_loaded > 0:
            positive_aspects.append(f"{lazy_loaded} images use lazy loading for performance")
        
        if positive_aspects:
            return {
                "type": "success",
                "title": f"Good image implementation",
                "description": f"The page has {total_images} images with good practices: " + ", ".join(positive_aspects) + "."
            }
        
        return {
            "type": "warning",
            "title": "Basic image implementation",
            "description": f"The page has {total_images} images with {alt_percentage:.0f}% alt text coverage, but could improve with responsive images and lazy loading."
        }
    
    def _check_cta_elements(self):
        """Check call-to-action elements for effectiveness"""
        
        # Look for buttons and prominent links
        buttons = self.soup.find_all('button')
        button_links = self.soup.find_all('a', class_=lambda c: c and any(cls in str(c).lower() for cls in ['btn', 'button', 'cta']))
        
        # Also look for links with CTA-like text
        cta_text_patterns = ['sign up', 'subscribe', 'register', 'get started', 'learn more', 'contact us', 'try', 'buy', 'download']
        cta_links = self.soup.find_all('a', string=lambda s: s and any(cta in s.lower() for cta in cta_text_patterns))
        
        # Combine all CTA elements
        all_ctas = buttons + button_links + cta_links
        
        if not all_ctas:
            return {
                "type": "warning",
                "title": "No clear call-to-actions",
                "description": "The page doesn't have clear call-to-action elements, which are important for guiding users."
            }
        
        # Analyze prominence
        above_fold_ctas = []
        for cta in all_ctas:
            # Check if CTA is likely above the fold
            # This is a heuristic - we assume CTAs near the top are above the fold
            if cta.parent and cta.parent.parent:
                parent_components = [p for p in cta.parents if p.name in ['header', 'nav', 'section', 'div'] and p.get('id') or p.get('class')]
                for parent in parent_components:
                    parent_id = parent.get('id', '')
                    parent_class = ' '.join(parent.get('class', []))
                    
                    if any(term in parent_id.lower() + ' ' + parent_class.lower() for term in ['header', 'hero', 'banner', 'top', 'intro']):
                        above_fold_ctas.append(cta)
                        break
        
        # Check for CTA design patterns
        has_primary_secondary = False
        has_color_contrast = False
        
        # Check if there are primary/secondary button distinctions
        primary_indicators = ['primary', 'main', 'cta']
        secondary_indicators = ['secondary', 'outline', 'ghost', 'text']
        
        primary_ctas = [cta for cta in all_ctas if cta.get('class') and any(p in ' '.join(cta.get('class', [])).lower() for p in primary_indicators)]
        secondary_ctas = [cta for cta in all_ctas if cta.get('class') and any(s in ' '.join(cta.get('class', [])).lower() for s in secondary_indicators)]
        
        if primary_ctas and secondary_ctas:
            has_primary_secondary = True
        
        # Check for color contrast
        for cta in all_ctas:
            style = cta.get('style', '')
            if ('background' in style and 'color' in style) or any(c in ' '.join(cta.get('class', [])).lower() for c in ['blue', 'red', 'green', 'orange', 'purple']):
                has_color_contrast = True
                break
        
        # Build finding based on results
        positive_aspects = []
        
        if len(above_fold_ctas) > 0:
            positive_aspects.append(f"{len(above_fold_ctas)} CTAs above the fold")
        
        if has_primary_secondary:
            positive_aspects.append("clear primary/secondary button hierarchy")
        
        if has_color_contrast:
            positive_aspects.append("good color contrast for visibility")
        
        if len(positive_aspects) >= 2:
            return {
                "type": "success",
                "title": "Effective call-to-actions",
                "description": f"The page has {len(all_ctas)} CTAs with " + ", ".join(positive_aspects) + "."
            }
        elif len(all_ctas) > 5:
            return {
                "type": "warning",
                "title": "Too many call-to-actions",
                "description": f"The page has {len(all_ctas)} CTAs, which may overwhelm users. Focus on fewer, more strategic CTAs."
            }
        else:
            return {
                "type": "warning",
                "title": "Basic call-to-actions",
                "description": f"The page has {len(all_ctas)} CTAs but could improve their prominence and hierarchy."
            }
    
    def _check_branding(self):
        """Check for consistent branding elements"""
        
        # Look for logo
        logo = None
        logo_candidates = self.soup.find_all('img', alt=lambda alt: alt and 'logo' in alt.lower())
        
        if not logo_candidates:
            # Look for images in header with likely class names
            header = self.soup.find(['header', '.header', '#header'])
            if header:
                logo_candidates = header.find_all('img')
                logo_candidates += header.find_all('svg')
        
        if not logo_candidates:
            # Look for links with logo in class or ID
            logo_candidates = self.soup.find_all(['a', 'div'], class_=lambda c: c and 'logo' in ' '.join(c).lower())
            logo_candidates += self.soup.find_all(['a', 'div'], id=lambda i: i and 'logo' in i.lower())
        
        has_logo = len(logo_candidates) > 0
        
        # Check for favicon
        favicon = None
        for link in self.soup.find_all('link', rel=lambda r: r and r.lower() in ['icon', 'shortcut icon']):
            favicon = link
            break
        
        has_favicon = favicon is not None
        
        # Check for consistent colors (we've already analyzed colors in _check_colors)
        # This is a simplified check
        
        # Check for brand name mention
        domain_parts = self.domain.split('.')
        if len(domain_parts) > 1:
            brand_name = domain_parts[-2]  # Use the domain name as brand name heuristic
            
            # Count brand name mentions in text
            text_content = self.soup.get_text()
            brand_mentions = len(re.findall(r'\b' + re.escape(brand_name) + r'\b', text_content, re.IGNORECASE))
        else:
            brand_name = None
            brand_mentions = 0
        
        # Build finding based on results
        positive_aspects = []
        negative_aspects = []
        
        if has_logo:
            positive_aspects.append("logo is present")
        else:
            negative_aspects.append("no clear logo found")
        
        if has_favicon:
            positive_aspects.append("favicon is implemented")
        else:
            negative_aspects.append("no favicon found")
        
        if brand_mentions > 3:
            positive_aspects.append(f"brand name mentioned {brand_mentions} times")
        
        if negative_aspects:
            return {
                "type": "warning",
                "title": "Branding issues",
                "description": "The page has branding issues: " + ", ".join(negative_aspects) + "."
            }
        elif positive_aspects:
            return {
                "type": "success",
                "title": "Good branding elements",
                "description": "The page has good branding: " + ", ".join(positive_aspects) + "."
            }
        else:
            return {
                "type": "warning",
                "title": "Limited branding",
                "description": "The page shows limited evidence of consistent branding elements."
            }
    
    def _check_footer(self):
        """Check footer for usability and completeness"""
        
        # Find footer
        footer = self.soup.find(['footer', 'div[role="contentinfo"]', '.footer', '#footer'])
        
        if not footer:
            return {
                "type": "warning",
                "title": "No footer found",
                "description": "The page doesn't have a clear footer section, which is important for secondary navigation and trust signals."
            }
        
        # Check for important footer elements
        footer_links = footer.find_all('a')
        footer_link_count = len(footer_links)

 # Check for important footer elements
        has_contact = any('contact' in link.get_text().lower() for link in footer_links)
        has_privacy = any('privacy' in link.get_text().lower() for link in footer_links)
        has_terms = any(term in ' '.join(link.get_text().lower() for link in footer_links) for term in ['terms', 'conditions'])
        
        # Check for social media links
        social_patterns = ['facebook', 'twitter', 'instagram', 'linkedin', 'youtube', 'pinterest', 'tiktok']
        social_links = [link for link in footer_links if any(pattern in link.get('href', '').lower() for pattern in social_patterns)]
        has_social = len(social_links) > 0
        
        # Check for copyright information
        copyright_text = footer.find(string=lambda text: text and '©' in text or 'copyright' in text.lower())
        has_copyright = copyright_text is not None
        
        # Build finding based on results
        present_elements = []
        if has_contact:
            present_elements.append("contact information")
        if has_privacy:
            present_elements.append("privacy policy")
        if has_terms:
            present_elements.append("terms of service")
        if has_social:
            present_elements.append(f"{len(social_links)} social media links")
        if has_copyright:
            present_elements.append("copyright notice")
        
        if len(present_elements) >= 4:
            return {
                "type": "success",
                "title": "Comprehensive footer",
                "description": f"The footer contains {footer_link_count} links and includes " + ", ".join(present_elements) + "."
            }
        elif len(present_elements) >= 2:
            return {
                "type": "success",
                "title": "Good footer elements",
                "description": f"The footer includes " + ", ".join(present_elements) + "."
            }
        else:
            return {
                "type": "warning",
                "title": "Basic footer",
                "description": f"The footer is minimal and missing important elements like " + ", ".join(["contact information", "privacy policy", "terms of service"][:(3 - len(present_elements))]) + "."
            }
    
    def _calculate_score(self, findings):
        """Calculate overall design score based on findings"""
        
        # Define weights for different categories
        weights = {
            "Layout": 0.2,
            "Visual Design": 0.25,
            "Navigation": 0.25,
            "Mobile": 0.2,
            "Branding": 0.1
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
        
        if "not mobile-friendly" in title:
            return "Add a viewport meta tag with content='width=device-width, initial-scale=1' to enable proper responsive behavior on mobile devices."
        
        elif "poor page structure" in title:
            return "Implement a clear page structure with header, main content, and footer sections using semantic HTML5 elements."
        
        elif "limited content structure" in title:
            return "Divide content into clear sections using semantic elements like <section>, <article>, and <aside> to improve scanability."
        
        elif "many fixed-width elements" in title:
            return "Replace fixed pixel widths with responsive units like percentages, rem, or em, and use CSS media queries for responsive layouts."
        
        elif "navigation not clearly defined" in title:
            return "Create a clear navigation element using the <nav> tag and organize links logically with proper hierarchy."
        
        elif "too many navigation items" in title:
            return "Simplify navigation by grouping related items into dropdown menus or moving less important links to the footer."
        
        elif "typography issues detected" in title:
            return "Improve typography by limiting fonts to 2-3 families, ensuring text is at least 16px, and setting line height to 1.5-1.6 for better readability."
        
        elif "inconsistent color usage" in title:
            return "Create a consistent color palette with 2-3 primary colors, 2-3 secondary colors, and appropriate accent colors for better visual harmony."
        
        elif "inconsistent spacing" in title:
            return "Implement a consistent spacing system using a base unit (like 8px or 1rem) and multiples of that unit for all margins and padding."
        
        elif "poor image accessibility" in title:
            return "Add descriptive alt text to all images to improve accessibility and SEO. Use empty alt text (alt=\"\") for decorative images."
        
        elif "no clear call-to-actions" in title or "basic call-to-actions" in title:
            return "Add prominent call-to-action buttons with clear hierarchy, using color contrast and positioning to guide users toward important actions."
        
        elif "branding issues" in title or "limited branding" in title:
            return "Strengthen branding with a prominent logo, favicon, consistent color scheme, and typography that reflects your brand identity."
        
        elif "no footer found" in title or "basic footer" in title:
            return "Implement a comprehensive footer with contact information, legal links (privacy policy, terms), social media links, and copyright notice."
        
        # Generic recommendations based on finding type
        if finding.get("type") == "error":
            return finding.get("description", "Fix this critical design issue to improve user experience.")
        else:
            return finding.get("description", "Address this design issue to enhance visual appeal and usability.")
