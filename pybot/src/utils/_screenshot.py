import time
from playwright.sync_api import sync_playwright
import os

def take_screenshot(browser_type, url, output_path):
    start_time = time.time()
    
    page = browser_type.new_page()
    page.goto(url, wait_until='domcontentloaded')
    # Wait for the page to load
    page.wait_for_timeout(10000)
    page.screenshot(path=output_path)
    page.close()
    
    end_time = time.time()
    return end_time - start_time

def test_browsers(urls):
    results = {
        'firefox': [],
        'chromium': []
    }
    
    with sync_playwright() as p:
        #firefox = p.firefox.launch(headless=True)
        chromium = p.chromium.launch(headless=True)
        
        for i, url in enumerate(urls):
            # Ensure the output directory exists
            os.makedirs('screenshots', exist_ok=True)
            
            # Test Firefox
            #firefox_time = take_screenshot(firefox, url, f'screenshots/firefox_{i}.png')
            #results['firefox'].append(firefox_time)
            
            # Test Chromium
            chromium_time = take_screenshot(chromium, url, f'screenshots/chromium_{i}.png')
            results['chromium'].append(chromium_time)
            
            print(f"URL {i+1}: Chromium - {chromium_time:.4f}s")
        
        #firefox.close()
        chromium.close()
    
    return results

def print_summary(results):
    for browser, times in results.items():
        avg_time = sum(times) / len(times)
        print(f"\n{browser.capitalize()} Summary:")
        print(f"  Total time: {sum(times):.4f}s")
        print(f"  Average time: {avg_time:.4f}s")

# List of URLs to test
urls = [
    "https://www.leetcode.cn/problems/two-sum",
]

print("Starting browser performance test...")
results = test_browsers(urls)
print("\nTest completed. Results summary:")