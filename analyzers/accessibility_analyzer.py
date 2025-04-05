import re
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AccessibilityAnalyzer:
    """Analyzes website accessibility compliance"""
    
    def __init__(self, page_content):
        """
        Initialize the accessibility analyzer
        
        Args:
            page_content (BeautifulSoup): The parsed HTML content
        """
        self.soup = page_content
    
    def analyze(self):
        """
        Perform accessibility analysis
        
        Returns:
            dict: Analysis results with score, findings, and recommendations
        """
        findings = {
            "Structure": [],
            "Content": [],
            "Navigation": [],
            "Media": []
        }
        
        # Check for accessibility issues
        
        # 1. Check document structure
        lang_result = self._check_language()
        findings["Structure"].append(lang_result)
        
        title_result = self._check_page_title()
        findings["Structure"].append(title_result)
        
        headings_result = self._check_headings_hierarchy()
        findings["Structure"].append(headings_result)
        
        landmarks_result = self._check_landmarks()
        findings["Structure"].append(landmarks_result)
        
        # 2. Check content accessibility
        images_alt_result = self._check_img_alt_texts()
        findings["Media"].append(images_alt_result)
        
        color_contrast_result = self._check_color_contrast()
        findings["Content"].append(color_contrast_result)
        
        text_size_result = self._check_text_size()
        findings["Content"].append(text_size_result)
        
        form_labels_result = self._check_form_labels()
        findings["Content"].append(form_labels_result)
        
        links_result = self._check_link_text()
        findings["Navigation"].append(links_result)
        
        keyboard_result = self._check_keyboard_accessibility()
        findings["Navigation"].append(keyboard_result)
        
        tables_result = self._check_tables()
        findings["Content"].append(tables_result)
        
        # Calculate score
        score = self._calculate_score(findings)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(findings)
        
        return {
            "score": score,
            "findings": findings,
            "recommendations": recommendations
        }
    
    def _check_language(self):
        """Check if the page has a language attribute"""
        html_tag = self.soup.find('html')
        
        if not html_tag:
            return {
                "type": "error",
                "title": "No HTML tag found",
                "description": "The page doesn't have a proper HTML structure."
            }
        
        lang_attr = html_tag.get('lang')
        
        if not lang_attr:
            return {
                "type": "error",
                "title": "Missing language attribute",
                "description": "The HTML tag doesn't have a lang attribute, which is essential for screen readers."
            }
        
        if len(lang_attr) < 2:
            return {
                "type": "warning",
                "title": "Invalid language code",
                "description": f"The language code '{lang_attr}' is too short to be valid."
            }
        
        return {
            "type": "success",
            "title": f"Language specified: {lang_attr}",
            "description": f"The page correctly specifies '{lang_attr}' as the document language."
        }
    
    def _check_page_title(self):
        """Check if the page has a proper title"""
        title_tag = self.soup.find('title')
        
        if not title_tag:
            return {
                "type": "error",
                "title": "Missing page title",
                "description": "The page doesn't have a title tag, which is essential for accessibility."
            }
        
        title_text = title_tag.get_text().strip()
        
        if not title_text:
            return {
                "type": "error",
                "title": "Empty page title",
                "description": "The page has a title tag but it's empty."
            }
        
        if len(title_text) < 10:
            return {
                "type": "warning",
                "title": "Title too short",
                "description": f"The page title '{title_text}' is very short. It should be descriptive of the page content."
            }
        
        return {
            "type": "success",
            "title": "Page has proper title",
            "description": f"The page has a descriptive title: '{title_text}'."
        }
    
    def _check_headings_hierarchy(self):
        """Check if headings are used correctly and follow a logical hierarchy"""
        headings = self.soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        if not headings:
            return {
                "type": "error",
                "title": "No headings found",
                "description": "The page doesn't use heading tags (h1-h6), which are crucial for screen reader navigation."
            }
        
        # Count headings by level
        heading_counts = {f'h{i}': 0 for i in range(1, 7)}
        for heading in headings:
            heading_counts[heading.name] += 1
        
        # Check for h1
        if heading_counts['h1'] == 0:
            return {
                "type": "error",
                "title": "No main heading (h1) found",
                "description": "Every page should have exactly one main heading (h1) that describes the page content."
            }
        
        if heading_counts['h1'] > 1:
            return {
                "type": "warning",
                "title": f"Multiple h1 headings ({heading_counts['h1']})",
                "description": "Best practice is to have exactly one h1 heading per page."
            }
        
        # Check heading hierarchy
        prev_level = 0
        skipped_levels = False
        for heading in headings:
            current_level = int(heading.name[1])
            
            # Check for skipped levels (e.g., h1 to h3 without h2)
            if current_level > prev_level + 1 and prev_level > 0:
                skipped_levels = True
            
            prev_level = current_level
        
        if skipped_levels:
            return {
                "type": "warning",
                "title": "Heading levels are skipped",
                "description": "Headings should follow a logical hierarchy without skipping levels (e.g., h1 to h3 without h2)."
            }
        
        # If we reached here, headings are fine
        return {
            "type": "success",
            "title": "Good heading structure",
            "description": f"The page uses {len(headings)} headings with a logical hierarchy."
        }
    
    def _check_landmarks(self):
        """Check if the page uses proper ARIA landmarks or HTML5 structural elements"""
        landmarks = []
        
        # Check for HTML5 landmark elements
        landmarks.extend(self.soup.find_all(['header', 'nav', 'main', 'footer', 'aside', 'section', 'article']))
        
        # Check for ARIA landmark roles
        for elem in self.soup.find_all(attrs={'role': True}):
            role = elem.get('role').lower()
            if role in ['banner', 'navigation', 'main', 'contentinfo', 'complementary', 'region', 'search', 'form']:
                landmarks.append(elem)
        
        if not landmarks:
            return {
                "type": "warning",
                "title": "No landmarks found",
                "description": "The page doesn't use HTML5 structural elements or ARIA landmarks, which help screen reader users navigate."
            }
        
        # Check for key landmarks
        landmark_types = {
            'header': 0, 'role=banner': 0,
            'nav': 0, 'role=navigation': 0,
            'main': 0, 'role=main': 0,
            'footer': 0, 'role=contentinfo': 0
        }
        
        for elem in landmarks:
            if elem.name == 'header':
                landmark_types['header'] += 1
            elif elem.name == 'nav':
                landmark_types['nav'] += 1
            elif elem.name == 'main':
                landmark_types['main'] += 1
            elif elem.name == 'footer':
                landmark_types['footer'] += 1
            elif elem.get('role') == 'banner':
                landmark_types['role=banner'] += 1
            elif elem.get('role') == 'navigation':
                landmark_types['role=navigation'] += 1
            elif elem.get('role') == 'main':
                landmark_types['role=main'] += 1
            elif elem.get('role') == 'contentinfo':
                landmark_types['role=contentinfo'] += 1
        
        # Either HTML5 or ARIA landmarks should be used for main structure
        has_header = landmark_types['header'] > 0 or landmark_types['role=banner'] > 0
        has_nav = landmark_types['nav'] > 0 or landmark_types['role=navigation'] > 0
        has_main = landmark_types['main'] > 0 or landmark_types['role=main'] > 0
        has_footer = landmark_types['footer'] > 0 or landmark_types['role=contentinfo'] > 0
        
        missing_landmarks = []
        if not has_header:
            missing_landmarks.append("header")
        if not has_nav:
            missing_landmarks.append("navigation")
        if not has_main:
            missing_landmarks.append("main content")
        if not has_footer:
            missing_landmarks.append("footer")
        
        if missing_landmarks:
            return {
                "type": "warning",
                "title": "Missing key landmarks",
                "description": f"The page is missing the following landmarks: {', '.join(missing_landmarks)}. "
                           "These help screen reader users navigate the page."
            }
        
        return {
            "type": "success",
            "title": "Good landmark structure",
            "description": f"The page uses {len(landmarks)} landmarks to structure content, including all key navigation points."
        }
    
    def _check_img_alt_texts(self):
        """Check if images have proper alt text"""
        images = self.soup.find_all('img')
        
        if not images:
            return {
                "type": "success",
                "title": "No images found",
                "description": "The page doesn't contain any img elements to check."
            }
        
        missing_alt = []
        empty_alt = 0
        has_alt = 0
        
        for img in images:
            if not img.has_attr('alt'):
                missing_alt.append(img)
            elif img['alt'].strip() == '':
                empty_alt += 1
            else:
                has_alt += 1
        
        if missing_alt:
            # Check if these might be decorative images
            potentially_decorative = 0
            for img in missing_alt:
                # Decorative images often have certain class names or are inside certain containers
                classes = img.get('class', [])
                if any(c.lower() in ['decoration', 'bg', 'background', 'icon'] for c in classes):
                    potentially_decorative += 1
                # Check parent elements for hints that this is decorative
                parent = img.parent
                if parent and parent.name in ['span', 'div'] and not parent.get_text(strip=True):
                    potentially_decorative += 1
            
            if potentially_decorative == len(missing_alt):
                # All missing alt might be decorative
                return {
                    "type": "warning",
                    "title": f"Images missing alt text ({len(missing_alt)})",
                    "description": f"Found {len(missing_alt)} images without alt attributes. If these are decorative, use empty alt attributes (alt='') instead of omitting them."
                }
            else:
                return {
                    "type": "error",
                    "title": f"Images missing alt text ({len(missing_alt)})",
                    "description": f"Found {len(missing_alt)} images without alt attributes. All images must have alt text describing their content or empty alt if decorative."
                }
        
        if has_alt == 0 and empty_alt > 0:
            return {
                "type": "warning",
                "title": "All images have empty alt text",
                "description": f"All {empty_alt} images have empty alt text, suggesting they might be decorative. If some are informative, they should have descriptive alt text."
            }
        
        if empty_alt > 0 and has_alt > 0:
            return {
                "type": "success",
                "title": "Images have alt text",
                "description": f"{has_alt} images have descriptive alt text and {empty_alt} have empty alt text (probably decorative)."
            }
        
        return {
            "type": "success",
            "title": "All images have alt text",
            "description": f"All {len(images)} images have alt text attributes."
        }
    
    def _check_color_contrast(self):
        """Basic check for potential color contrast issues (limited without rendering)"""
        # This is a basic implementation that looks for potential indicators of contrast issues
        # Full contrast checking would require rendering the page and calculating color ratios
        
        style_tags = self.soup.find_all('style')
        inline_styles = self.soup.find_all(attrs={'style': True})
        
        # Look for potential low contrast indicators in CSS
        contrast_issues = []
        
        # Check for light colored text or backgrounds
        light_colors = ['#fff', '#ffffff', 'white', 'rgb(255,255,255)', 'rgba(255,255,255',
                       '#eee', '#f0f0f0', '#f5f5f5', '#fafafa', '#fcfcfc',
                       'lightyellow', 'lightgrey', 'lightgray', 'lightpink']
        
        # Check in style tags
        for style in style_tags:
            css_content = style.string if style.string else ""
            for color in light_colors:
                if color in css_content and ('color:' in css_content or 'background' in css_content):
                    contrast_issues.append(f"Light color '{color}' found in CSS")
        
        # Check inline styles
        for elem in inline_styles:
            style_attr = elem.get('style', '')
            for color in light_colors:
                if color in style_attr and ('color:' in style_attr or 'background' in style_attr):
                    contrast_issues.append(f"Light color '{color}' found in inline style")
        
        # Limited check for explicit contrast classes or accessibility attributes
        contrast_classes = self.soup.find_all(class_=lambda c: c and any(x in str(c).lower() for x in ['high-contrast', 'low-contrast', 'a11y']))
        contrast_attrs = self.soup.find_all(attrs={'data-contrast': True})
        
        if contrast_attrs or contrast_classes:
            # Site appears to have explicit contrast controls
            return {
                "type": "success",
                "title": "Contrast controls detected",
                "description": "The page appears to have elements related to contrast control, suggesting accessibility consideration."
            }
        
        if contrast_issues:
            return {
                "type": "warning",
                "title": "Potential contrast issues",
                "description": "Detected potential color contrast issues. Light colors are used that might not provide sufficient contrast with backgrounds or text."
            }
        
        # If we can't find clear indicators, provide a neutral message
        return {
            "type": "warning",
            "title": "Color contrast requires visual inspection",
            "description": "Couldn't automatically determine if there are contrast issues. Manual testing with a contrast checker is recommended."
        }
    
    def _check_text_size(self):
        """Check for problematic text size settings"""
        style_tags = self.soup.find_all('style')
        inline_styles = self.soup.find_all(attrs={'style': True})
        
        # Look for small font sizes
        small_sizes = []
        
        # Check in style tags
        for style in style_tags:
            css_content = style.string if style.string else ""
            # Look for font-size with small values
            font_sizes = re.findall(r'font-size:\s*(\d+)px', css_content)
            small_sizes.extend([int(size) for size in font_sizes if int(size) < 12])
        
        # Check inline styles
        for elem in inline_styles:
            style_attr = elem.get('style', '')
            font_sizes = re.findall(r'font-size:\s*(\d+)px', style_attr)
            small_sizes.extend([int(size) for size in font_sizes if int(size) < 12])
        
        if small_sizes:
            return {
                "type": "warning",
                "title": "Small text detected",
                "description": f"Found {len(small_sizes)} instances of text smaller than 12px. Small text can be difficult to read, especially for users with visual impairments."
            }
        
        # Check if the page uses relative units (better for accessibility)
        uses_relative = False
        
        # Check in style tags
        for style in style_tags:
            css_content = style.string if style.string else ""
            if re.search(r'font-size:\s*[\d.]+\s*(em|rem|%)', css_content):
                uses_relative = True
                break
        
        # Check inline styles if not found yet
        if not uses_relative:
            for elem in inline_styles:
                style_attr = elem.get('style', '')
                if re.search(r'font-size:\s*[\d.]+\s*(em|rem|%)', style_attr):
                    uses_relative = True
                    break
        
        if uses_relative:
            return {
                "type": "success",
                "title": "Relative font sizes detected",
                "description": "The page uses relative font size units (em, rem, %), which is good for accessibility and responsive design."
            }
        
        # If no specific issues found, provide general guidance
        return {
            "type": "warning",
            "title": "Text size needs manual verification",
            "description": "Could not automatically determine if text sizes are accessible. Ensure text is at least 12px and consider using relative units (em, rem) instead of fixed pixels."
        }
    
    def _check_form_labels(self):
        """Check if form elements have proper labels"""
        form_controls = self.soup.find_all(['input', 'select', 'textarea'])
        
        if not form_controls:
            return {
                "type": "success",
                "title": "No form controls found",
                "description": "The page doesn't contain any form controls to check."
            }
        
        # Filter out hidden and submit inputs which don't need labels
        visible_controls = []
        for control in form_controls:
            input_type = control.get('type', '').lower()
            if control.name != 'input' or (input_type not in ['hidden', 'submit', 'button', 'image', 'reset']):
                visible_controls.append(control)
        
        if not visible_controls:
            return {
                "type": "success",
                "title": "No visible form controls found",
                "description": "The page only contains form controls that don't require labels (like hidden or submit inputs)."
            }
        
        # Check for proper labeling
        properly_labeled = 0
        unlabeled = []
        
        for control in visible_controls:
            # Check if control has an ID
            control_id = control.get('id')
            
            if control_id:
                # Check for explicit label
                label = self.soup.find('label', attrs={'for': control_id})
                if label and label.get_text(strip=True):
                    properly_labeled += 1
                    continue
            
            # Check for aria-label or aria-labelledby
            if control.get('aria-label') or control.get('aria-labelledby'):
                properly_labeled += 1
                continue
            
            # Check if it's a child of a label
            parent_label = [p for p in control.parents if p.name == 'label']
            if parent_label:
                properly_labeled += 1
                continue
            
            # Check if it has a title attribute
            if control.get('title'):
                properly_labeled += 1
                continue
            
            # Check if it has placeholder (not ideal, but better than nothing)
            if control.get('placeholder'):
                # Placeholder is not a substitute for a label, but count it as partially labeled
                properly_labeled += 0.5
                continue
            
            # If we get here, the control is unlabeled
            unlabeled.append(control)
        
        # Calculate percentage properly labeled
        total_controls = len(visible_controls)
        labeled_percentage = (properly_labeled / total_controls) * 100 if total_controls > 0 else 0
        
        if unlabeled:
            if labeled_percentage < 50:
                return {
                    "type": "error",
                    "title": f"Most form controls are unlabeled ({len(unlabeled)}/{total_controls})",
                    "description": f"Only {labeled_percentage:.0f}% of form controls have proper labels. All form controls should have associated labels."
                }
            else:
                return {
                    "type": "warning",
                    "title": f"Some form controls are unlabeled ({len(unlabeled)}/{total_controls})",
                    "description": f"{labeled_percentage:.0f}% of form controls have proper labels. Ensure all form controls have associated labels."
                }
        
        return {
            "type": "success",
            "title": "All form controls are properly labeled",
            "description": f"All {total_controls} form controls have proper labels, which is excellent for accessibility."
        }
    
    def _check_link_text(self):
        """Check if links have descriptive text"""
        links = self.soup.find_all('a', href=True)
        
        if not links:
            return {
                "type": "success",
                "title": "No links found",
                "description": "The page doesn't contain any links to check."
            }
        
        # Filter out anchor links, javascript, and mailto
        content_links = []
        for link in links:
            href = link['href'].strip()
            if not href.startswith(('#', 'javascript:', 'mailto:')):
                content_links.append(link)
        
        if not content_links:
            return {
                "type": "success",
                "title": "No content links found",
                "description": "The page only contains non-navigational links (anchors, mailto, javascript)."
            }
        
        # Check for problematic link text
        problematic_links = []
        non_descriptive_count = 0
        
        for link in content_links:
            link_text = link.get_text(strip=True)
            
            # Check for empty link text
            if not link_text:
                # Check if it contains an image with alt text
                img = link.find('img')
                if img and img.get('alt'):
                    continue
                else:
                    problematic_links.append("Empty link text")
                    non_descriptive_count += 1
                    continue
            
            # Check for very short or non-descriptive text
            if link_text.lower() in ['click here', 'here', 'link', 'this', 'more', 'details', 'read more']:
                problematic_links.append(f"Non-descriptive link text: '{link_text}'")
                non_descriptive_count += 1
                continue
            
            # Check if the link text is too short
            if len(link_text) < 4:
                problematic_links.append(f"Very short link text: '{link_text}'")
                non_descriptive_count += 1
        
        # Calculate percentage of problematic links
        total_links = len(content_links)
        problem_percentage = (non_descriptive_count / total_links) * 100 if total_links > 0 else 0
        
        if problem_percentage > 20:
            return {
                "type": "error",
                "title": f"Many non-descriptive links ({non_descriptive_count}/{total_links})",
                "description": f"{problem_percentage:.0f}% of links have non-descriptive text. Link text should clearly describe its destination without surrounding context."
            }
        elif problem_percentage > 0:
            return {
                "type": "warning",
                "title": f"Some non-descriptive links ({non_descriptive_count}/{total_links})",
                "description": f"{problem_percentage:.0f}% of links have non-descriptive text. All links should have text that makes sense out of context."
            }
        
        return {
            "type": "success",
            "title": "All links have descriptive text",
            "description": f"All {total_links} links have descriptive text, which is excellent for accessibility."
        }
    
    def _check_keyboard_accessibility(self):
        """Check for potential keyboard accessibility issues"""
        # Check for tabindex values that might disrupt keyboard navigation
        elements_with_tabindex = self.soup.find_all(attrs={'tabindex': True})
        
        negative_tabindex = []
        high_tabindex = []
        
        for elem in elements_with_tabindex:
            try:
                tabindex = int(elem['tabindex'])
                if tabindex < 0:
                    negative_tabindex.append(elem)
                elif tabindex > 0:
                    high_tabindex.append((elem, tabindex))
            except ValueError:
                continue
        
        # Check for event handlers without keyboard equivalents
        mouse_only_handlers = []
        elements_with_onclick = self.soup.find_all(attrs={'onclick': True})
        
        for elem in elements_with_onclick:
            # Check if element has keyboard event handlers
            has_keyboard = any(elem.has_attr(attr) for attr in ['onkeydown', 'onkeyup', 'onkeypress'])
            
            # Check if it's an interactive element that naturally handles keyboard
            is_interactive = elem.name in ['a', 'button', 'input', 'select', 'textarea']
            
            if not has_keyboard and not is_interactive:
                mouse_only_handlers.append(elem)
        
        # Provide findings based on issues found
        issues = []
        
        if negative_tabindex:
            issues.append(f"Found {len(negative_tabindex)} elements with negative tabindex, which removes them from keyboard navigation.")
        
        if high_tabindex:
            issues.append(f"Found {len(high_tabindex)} elements with explicit tabindex values > 0, which can disrupt the natural tab order.")
        
        if mouse_only_handlers:
            issues.append(f"Found {len(mouse_only_handlers)} elements with click handlers but no keyboard event handlers.")
        
        if issues:
            return {
                "type": "warning",
                "title": "Potential keyboard accessibility issues",
                "description": " ".join(issues)
            }
        
        # Check for skip links
        skip_links = self.soup.find_all('a', href=lambda href: href and '#' in href and (
            'skip' in href.lower() or 
            'jump' in href.lower() or 
            'content' in href.lower()
        ))
        
        if skip_links:
            return {
                "type": "success",
                "title": "Skip links detected",
                "description": f"Found {len(skip_links)} skip navigation links, which are good for keyboard accessibility."
            }
        
        # If we can't find clear indicators, provide a neutral message
        return {
            "type": "warning",
            "title": "Keyboard accessibility needs manual testing",
            "description": "No obvious keyboard accessibility issues found, but thorough testing requires manual verification with a keyboard."
        }
    
    def _check_tables(self):
        """Check if tables are used properly for data and have proper headers"""
        tables = self.soup.find_all('table')
        
        if not tables:
            return {
                "type": "success",
                "title": "No tables found",
                "description": "The page doesn't contain any tables to check."
            }
        
        # Check if tables are used for layout or data
        layout_tables = []
        data_tables = []
        
        for table in tables:
            # Check for layout role
            if table.get('role') == 'presentation':
                layout_tables.append(table)
                continue
            
            # Check for common data table elements
            has_th = len(table.find_all('th')) > 0
            has_caption = table.find('caption') is not None
            has_thead = table.find('thead') is not None
            has_tbody = table.find('tbody') is not None
            
            if has_th or has_caption or has_thead:
                data_tables.append((table, has_th, has_caption))
            else:
                # Check the structure to guess if it's a data table
                rows = table.find_all('tr')
                if len(rows) <= 1:
                    # Single row tables are likely layout
                    layout_tables.append(table)
                elif all(len(row.find_all(['td', 'th'])) <= 1 for row in rows):
                    # Single column tables are likely layout
                    layout_tables.append(table)
                else:
                    # Might be a data table without proper headers
                    data_tables.append((table, False, False))
        
        # Check data tables for proper headers
        tables_without_headers = []
        tables_without_captions = []
        
        for table, has_th, has_caption in data_tables:
            if not has_th:
                tables_without_headers.append(table)
            if not has_caption:
                tables_without_captions.append(table)
        
        # Determine the finding based on the analysis
        if not data_tables and layout_tables:
            return {
                "type": "warning",
                "title": f"Tables used for layout ({len(layout_tables)})",
                "description": "The page uses tables for layout rather than CSS. While not necessarily an accessibility issue, this is outdated practice."
            }
        
        if tables_without_headers and len(tables_without_headers) == len(data_tables):
            return {
                "type": "error",
                "title": f"Data tables without headers ({len(tables_without_headers)})",
                "description": "All data tables should have header cells (th) to help screen reader users understand the data relationships."
            }
        
        if tables_without_headers:
            return {
                "type": "warning",
                "title": f"Some data tables missing headers ({len(tables_without_headers)}/{len(data_tables)})",
                "description": f"{len(tables_without_headers)} out of {len(data_tables)} data tables are missing proper header cells (th)."
            }
        
        if data_tables and all(has_caption for _, _, has_caption in data_tables):
            return {
                "type": "success",
                "title": "Data tables have proper structure",
                "description": f"All {len(data_tables)} data tables have proper headers and captions."
            }
        
        return {
            "type": "success",
            "title": "Data tables have headers",
            "description": f"All {len(data_tables)} data tables have proper headers, but {len(tables_without_captions)} are missing captions."
        }
    
    def _calculate_score(self, findings):
        """Calculate overall accessibility score based on findings"""
        
        # Define weights for different categories
        weights = {
            "Structure": 0.25,
            "Content": 0.25,
            "Navigation": 0
