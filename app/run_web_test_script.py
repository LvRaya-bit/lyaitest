# app/run_web_test_script.py
import sys
import json
import time
from playwright.sync_api import sync_playwright

def main():
    # 从命令行参数获取 URL
    if len(sys.argv) < 2:
        print(json.dumps({"error": "请提供 URL"}))
        return
    
    url = sys.argv[1]
    result = {"status": None, "title": None, "screenshot": None, "error": None}
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            response = page.goto(url, wait_until="networkidle", timeout=30000)
            result["status"] = response.status if response else "无响应"
            result["title"] = page.title()
            
            timestamp = int(time.time())
            screenshot_path = f"screenshot_{timestamp}.png"
            page.screenshot(path=screenshot_path, full_page=True)
            result["screenshot"] = screenshot_path
            
            browser.close()
    except Exception as e:
        result["error"] = str(e)
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()