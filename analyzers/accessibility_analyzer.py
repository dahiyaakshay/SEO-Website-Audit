import re
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AccessibilityAnalyzer:
    def __init__(self, html_content):
        self.soup = BeautifulSoup(html_content, 'html.parser')

    def check_img_alt(self):
        try:
            images = self.soup.find_all('img')
            missing_alt = [img for img in images if not img.get('alt')]
            return len(missing_alt), len(images)
        except Exception as e:
            logger.error(f"Error in check_img_alt: {e}")
            return 1, 1

    def check_aria_labels(self):
        try:
            elements = self.soup.find_all(attrs={"aria-label": True})
            return 0 if elements else 1, 1
        except Exception as e:
            logger.error(f"Error in check_aria_labels: {e}")
            return 1, 1

    def check_lang_attribute(self):
        try:
            html_tag = self.soup.find('html')
            return 0 if html_tag and html_tag.get('lang') else 1, 1
        except Exception as e:
            logger.error(f"Error in check_lang_attribute: {e}")
            return 1, 1

    def check_contrast(self):
        try:
            # Placeholder logic for color contrast
            return 0, 1
        except Exception as e:
            logger.error(f"Error in check_contrast: {e}")
            return 1, 1

    def _calculate_score(self, issues_found, total_checks):
        try:
            if total_checks == 0:
                return 100
            return max(0, round((1 - issues_found / total_checks) * 100))
        except Exception as e:
            logger.error(f"Error in _calculate_score: {e}")
            return 0

    def analyze(self):
        logger.info("AccessibilityAnalyzer: Starting analysis...")
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
            try:
                issues, checks_total = check_func()
                results[label] = {
                    "issues_found": issues,
                    "checks_total": checks_total
                }
                total_issues += issues
                total_checks += checks_total
                logger.info(f"{label}: {issues} issues out of {checks_total}")
            except Exception as e:
                logger.error(f"Error running check '{label}': {e}")
                results[label] = {
                    "issues_found": 1,
                    "checks_total": 1,
                    "error": str(e)
                }
                total_issues += 1
                total_checks += 1

        score = self._calculate_score(total_issues, total_checks)
        logger.info(f"Accessibility Score: {score}")
        return {"score": score, "details": results}
