import re
from bs4 import BeautifulSoup
import logging

# Configure logging
class AccessibilityAnalyzer:
    def __init__(self, html_content):
        self.soup = BeautifulSoup(html_content, 'html.parser')

    def check_img_alt(self):
        images = self.soup.find_all('img')
        missing_alt = [img for img in images if not img.get('alt')]
        return len(missing_alt), len(images)

    def check_aria_labels(self):
        elements = self.soup.find_all(attrs={"aria-label": True})
        return 0 if elements else 1, 1

    def check_lang_attribute(self):
        html_tag = self.soup.find('html')
        return 0 if html_tag and html_tag.get('lang') else 1, 1

    def check_contrast(self):
        # This is a placeholder – real contrast checks require CSS and rendering context
        return 0, 1

    def _calculate_score(self, issues_found, total_checks):
        if total_checks == 0:
            return 100
        return max(0, round((1 - issues_found / total_checks) * 100))

    def analyze(self):
        results = {}
        total_issues = 0
        total_checks = 0

        checks = {
            "Image alt text missing": self.check_img_alt,
            "ARIA labels missing": self.check_aria_labels,
            "Missing lang attribute": self.check_lang_attribute,
            "Color contrast issues (placeholder)": self.check_contrast,
        }

        for label, check_func in checks.items():
            issues, checks_total = check_func()
            results[label] = {
                "issues_found": issues,
                "checks_total": checks_total
            }
            total_issues += issues
            total_checks += checks_total

        score = self._calculate_score(total_issues, total_checks)
        return {"score": score, "details": results}
