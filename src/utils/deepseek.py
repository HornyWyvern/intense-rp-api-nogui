from selenium.webdriver.common.keys import Keys
import re, time, tempfile

def login(driver, email, password):
    try:
        if not email or not password:
            return
        
        driver.type("//input[@type='text']", email, timeout=15)
        driver.type("//input[@type='password']", password, timeout=15)
        driver.click("div[role='button'].ds-sign-up-form__register-button")
    except Exception as e:
        print(f"Error logging in: {e}")

def close_sidebar(driver):
    try:
        sidebar = driver.find_element("class name", "dc04ec1d")
        
        if "a02af2e6" not in sidebar.get_attribute("class"):
            driver.click(".ds-icon-button")
            time.sleep(1)
    except Exception:
        pass

def new_chat(driver):
    try:
        boton = driver.find_element("xpath", "//div[contains(@class, '_217e214')]")
        driver.execute_script("arguments[0].click();", boton)
    except Exception:
        pass

def check_and_reload_page(driver):
    try:
        element = driver.find_elements("css selector", "div.a4380d7b")
        
        if element:
            driver.refresh()
            time.sleep(1)
    except Exception:
        pass

def set_button_state(driver, xpath, activate=False):
    try:
        button = driver.find_element("xpath", xpath)
        style = button.get_attribute("style")
        is_active = "rgba(77, 107, 254, 0.40)" in style
        
        if is_active != activate:
            driver.execute_script("arguments[0].click();", button)
            time.sleep(0.5)
    except Exception as e:
        print(f"Error setting button state: {e}")

def configure_chat(driver, r1, search):
    close_sidebar(driver)
    new_chat(driver)
    check_and_reload_page(driver)
    set_button_state(driver, "//div[@role='button' and contains(@class, '_3172d9f') and contains(., 'R1')]", r1)
    set_button_state(driver, "//div[@role='button' and contains(@class, '_3172d9f') and not(contains(., 'R1'))]", search)

def click_send_message_button(driver):
    try:
        button_xpath = "//div[@role='button' and contains(@class, '_7436101')]"
        driver.wait_for_element_present(button_xpath, by="xpath", timeout=15)
        
        end_time = time.time() + 60
        while time.time() < end_time:
            button = driver.find_element("xpath", button_xpath)
            if button.get_attribute("aria-disabled") == "false":
                driver.execute_script("arguments[0].click();", button)
                return True
            
            time.sleep(1)
        
        return False
    except Exception as e:
        print(f"Error clicking the send message button: {e}")
        return False

def send_chat_file(driver, text):
    try:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode='w', encoding='utf-8')
        tmp.write(text)
        tmp.close()
        
        file_input = driver.wait_for_element_present("input[type='file']", by="css selector", timeout=10)
        file_input.send_keys(tmp.name)
        
        return click_send_message_button(driver)
    except Exception as e:
        print(f"Error when attaching text file: {e}")
        return False

def send_chat_text(driver, text):
    try:
        def attempt_send():
            chat_input = driver.wait_for_element_present("chat-input", by="id", timeout=15)
            
            for _ in range(3):
                chat_input.clear()
                driver.execute_script("arguments[0].value = arguments[1];", chat_input, text)
                chat_input.send_keys(" ")
                chat_input.send_keys(Keys.BACKSPACE)
                
                if chat_input.get_attribute("value") == text:
                    return True
                
                time.sleep(1)
            
            return False
        
        for _ in range(2):
            if attempt_send():
                return click_send_message_button(driver)
            
            driver.refresh()
            time.sleep(1)
        
        return False
    except Exception as e:
        print(f"Error when pasting prompt: {e}")
        return False

def send_chat_message(driver, input_message, text_file):
    if text_file:
        return send_chat_file(driver, input_message)
    else:
        return send_chat_text(driver, input_message)

def active_generate_response(driver):
    try:
        button = driver.wait_for_element_present("//div[@role='button' and contains(@class, '_7436101')]//div[contains(@class, '_480132b')]", by="xpath", timeout=15)
        return button
    except Exception as e:
        print(f"Error generating response: {e}")
        return None

def is_response_generating(driver):
    try:
        button = driver.find_element("xpath", "//div[@role='button' and contains(@class, '_7436101')]")
        return button.get_attribute("aria-disabled") == "false"
    except Exception:
        return False

def get_last_message(driver):
    try:
        messages = driver.find_elements("xpath", "//div[contains(@class, 'ds-markdown ds-markdown--block')]")
        
        if messages:
            last_message = messages[-1].get_attribute("innerHTML")
            
            # Preserve XML tags during processing
            last_message = re.sub(r'(<think>.*?</think>|<infobox>.*?</infobox>)', 
                                lambda m: m.group(0).replace('<', '\x00').replace('>', '\x01'), 
                                last_message, 
                                flags=re.DOTALL)

            # Remove HTML tags while handling formatting
            last_message = re.sub(r'<p class="ds-markdown-paragraph">', '\n', last_message)  # New paragraph handling
            last_message = re.sub(r'</?p[^>]*>', '\n\n', last_message)  # All other p tags
            last_message = re.sub(r'<br\s*/?>', '\n', last_message)  # Line breaks
            last_message = re.sub(r'</?em>', '*', last_message)  # Italics
            last_message = re.sub(r'</?strong>', '', last_message)  # Remove bold
            last_message = re.sub(r'<[^>]+>', '', last_message)  # Remove remaining HTML

            # Restore XML tags
            last_message = last_message.replace('\x00', '<').replace('\x01', '>')

            # Clean up markdown artifacts
            last_message = re.sub(r'\n{3,}', '\n\n', last_message)  # Reduce multiple newlines
            last_message = re.sub(r'(\S)\n(\S)', r'\1\n\n\2', last_message)  # Add spacing between paragraphs
            last_message = re.sub(r'\*{2,}', '*', last_message)  # Fix asterisks
            last_message = re.sub(r'"{2,}', '"', last_message)  # Fix quotes
            
            return last_message.strip()
        else:
            return None
    
    except Exception as e:
        print(f"Error getting last response: {e}")
        return None

def closing_symbol(text):
    if not text:
        return ""
    
    text = text.strip()
    analysis_text = text.split("\n")[-1].strip()
    
    if re.search(r'(?:"\.?$|\*\.?$|”\.?$)', text):
        return ""

    current_symbol = None
    equal_chars = {
        '"': ['"'],
        '*': ['*'],
        '“': ['“', '”'],
        '”': ['“', '”']
        }
    opposite_chars = {
        '"': ['*', '“'],
        '*': ['"', '“'],
        '“': ['"', '*'],
        '”': ['"', '*']
        }
    
    for char in analysis_text:
        if not current_symbol:
            if char in equal_chars:
                current_symbol = char
        else:
            if char in equal_chars[current_symbol]:
                current_symbol = None
            elif char in opposite_chars[current_symbol]:
                current_symbol = char
    
    return current_symbol if current_symbol else ""