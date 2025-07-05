#!/usr/bin/env python3
"""
NIC.IR Nameserver Change Script
This script automates changing nameservers for domains registered with nic.ir
"""

import time
import csv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NICIRNameserverChanger:
    def __init__(self, headless=False):
        self.setup_driver(headless)
        self.wait = WebDriverWait(self.driver, 10)
        
    def setup_driver(self, headless):
        """Setup Chrome WebDriver with appropriate options"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            # Try to use webdriver-manager for automatic ChromeDriver management
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            
            # Detect if we're using Chromium (ARM64) or Chrome (AMD64)
            import platform
            arch = platform.machine().lower()
            
            if arch in ['aarch64', 'arm64']:
                # Use system chromium driver for ARM64
                chrome_options.binary_location = "/usr/bin/chromium"
                service = Service("/usr/bin/chromedriver")
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                # Use webdriver-manager for AMD64
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                
        except ImportError:
            # Fallback to system ChromeDriver
            self.driver = webdriver.Chrome(options=chrome_options)
        
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def login(self, username, password):
        """Login to NIC.IR panel"""
        try:
            logger.info("Navigating to NIC.IR login page...")
            self.driver.get("https://www.nic.ir/login")
            
            # Wait for login form to load
            username_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_field = self.driver.find_element(By.NAME, "password")
            
            # Enter credentials
            username_field.clear()
            username_field.send_keys(username)
            password_field.clear()
            password_field.send_keys(password)
            
            # Submit login form
            login_button = self.driver.find_element(By.XPATH, "//input[@type='submit']")
            login_button.click()
            
            # Wait for dashboard to load
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "dashboard"))
            )
            
            logger.info("Successfully logged in to NIC.IR")
            return True
            
        except TimeoutException:
            logger.error("Login failed - timeout waiting for elements")
            return False
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False
    
    def navigate_to_domain(self, domain):
        """Navigate to domain management page"""
        try:
            logger.info(f"Navigating to domain: {domain}")
            
            # Go to domain list
            self.driver.get("https://www.nic.ir/domains")
            
            # Search for the domain
            search_box = self.wait.until(
                EC.presence_of_element_located((By.NAME, "domain_search"))
            )
            search_box.clear()
            search_box.send_keys(domain)
            
            # Submit search
            search_button = self.driver.find_element(By.XPATH, "//input[@value='Search']")
            search_button.click()
            
            # Click on domain management link
            domain_link = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, f"//a[contains(text(), '{domain}')]"))
            )
            domain_link.click()
            
            logger.info(f"Successfully navigated to {domain} management page")
            return True
            
        except TimeoutException:
            logger.error(f"Failed to navigate to domain {domain} - timeout")
            return False
        except Exception as e:
            logger.error(f"Failed to navigate to domain {domain}: {str(e)}")
            return False
    
    def change_nameservers(self, domain, nameservers):
        """Change nameservers for a domain"""
        try:
            logger.info(f"Changing nameservers for {domain}")
            
            # Navigate to domain
            if not self.navigate_to_domain(domain):
                return False
            
            # Find DNS/Nameserver section
            dns_section = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'DNS') or contains(text(), 'Name Server')]"))
            )
            dns_section.click()
            
            # Wait for nameserver form to load
            time.sleep(2)
            
            # Clear existing nameservers and enter new ones
            for i, ns in enumerate(nameservers[:4]):  # NIC.IR typically allows up to 4 nameservers
                ns_field = self.driver.find_element(By.NAME, f"ns{i+1}")
                ns_field.clear()
                ns_field.send_keys(ns)
                logger.info(f"Set NS{i+1} to {ns}")
            
            # Clear any remaining nameserver fields
            for i in range(len(nameservers), 4):
                try:
                    ns_field = self.driver.find_element(By.NAME, f"ns{i+1}")
                    ns_field.clear()
                except NoSuchElementException:
                    break
            
            # Submit changes
            submit_button = self.driver.find_element(By.XPATH, "//input[@type='submit' and @value='Update']")
            submit_button.click()
            
            # Wait for confirmation
            time.sleep(3)
            
            # Check for success message
            try:
                success_message = self.driver.find_element(By.CLASS_NAME, "success-message")
                logger.info(f"Successfully changed nameservers for {domain}")
                return True
            except NoSuchElementException:
                logger.warning(f"No success message found for {domain}, but changes may have been applied")
                return True
                
        except Exception as e:
            logger.error(f"Failed to change nameservers for {domain}: {str(e)}")
            return False
    
    def process_domains_from_csv(self, csv_file, username, password):
        """Process multiple domains from CSV file"""
        if not self.login(username, password):
            logger.error("Failed to login, aborting...")
            return
        
        results = []
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    domain = row['domain'].strip()
                    nameservers = [
                        row.get('ns1', '').strip(),
                        row.get('ns2', '').strip(),
                        row.get('ns3', '').strip(),
                        row.get('ns4', '').strip()
                    ]
                    
                    # Filter out empty nameservers
                    nameservers = [ns for ns in nameservers if ns]
                    
                    if not nameservers:
                        logger.warning(f"No nameservers specified for {domain}, skipping...")
                        continue
                    
                    success = self.change_nameservers(domain, nameservers)
                    results.append({
                        'domain': domain,
                        'success': success,
                        'nameservers': nameservers
                    })
                    
                    # Add delay between domains to avoid being rate-limited
                    time.sleep(2)
                    
        except FileNotFoundError:
            logger.error(f"CSV file {csv_file} not found")
        except Exception as e:
            logger.error(f"Error processing CSV file: {str(e)}")
        
        # Print results summary
        successful = sum(1 for r in results if r['success'])
        total = len(results)
        logger.info(f"Completed: {successful}/{total} domains processed successfully")
        
        return results
    
    def close(self):
        """Close the webdriver"""
        if self.driver:
            self.driver.quit()

def main():
    """Main function to run the script"""
    # Configuration - use environment variables if available
    USERNAME = os.getenv('NIC_IR_USERNAME', 'your_nic_ir_username')
    PASSWORD = os.getenv('NIC_IR_PASSWORD', 'your_nic_ir_password')
    CSV_FILE = "domains.csv"
    HEADLESS_MODE = os.getenv('HEADLESS_MODE', 'true').lower() == 'true'
    
    # Initialize the changer
    changer = NICIRNameserverChanger(headless=HEADLESS_MODE)
    
    try:
        # Process domains from CSV
        results = changer.process_domains_from_csv(CSV_FILE, USERNAME, PASSWORD)
        
        # Save results to file
        results_dir = "/app/results" if os.path.exists("/app/results") else "."
        results_file = os.path.join(results_dir, 'nameserver_change_results.csv')
        
        with open(results_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Domain', 'Success', 'Nameservers'])
            
            for result in results:
                writer.writerow([
                    result['domain'],
                    'Yes' if result['success'] else 'No',
                    ', '.join(result['nameservers'])
                ])
        
        logger.info(f"Results saved to {results_file}")
        
    finally:
        changer.close()

if __name__ == "__main__":
    main()