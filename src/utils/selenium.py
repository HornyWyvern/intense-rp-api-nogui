from seleniumbase import Driver

def initialize_webdriver(custom_browser="chrome", url=None, headless=True, grid_host=None, grid_port=None):
    try:
        custom_browser = custom_browser.lower()
        chromium_arg = None
        selenium_options = {}
        
        if custom_browser in ["chrome", "edge"]:
            chromium_arg = f"--app={url}"

        # Если указан Selenium Grid, используем Remote WebDriver
        if grid_host and grid_port:
            from selenium.webdriver import Remote
            from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
            capabilities = getattr(DesiredCapabilities, custom_browser.upper(), DesiredCapabilities.CHROME)
            driver = Remote(
                command_executor=f"http://{grid_host}:{grid_port}/wd/hub",
                desired_capabilities=capabilities
            )
            if url:
                driver.get(url)
            return driver

        driver = Driver(
            browser=custom_browser,
            chromium_arg=chromium_arg,
            uc=(custom_browser == "chrome"),
            headless=headless
        )

        if custom_browser in ["firefox", "safari"] and url:
            driver.get(url)

        return driver

    except Exception as e:
        print(f"Error starting Selenium: {e}")
        return None

def is_browser_open(driver):
    try:
        _ = driver.title
        return True
    except Exception:
        return False
    
def current_page(driver, url):
    try:
        return driver.get_current_url().startswith(url)
    except Exception:
        return False