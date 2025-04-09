import time
import pytest
import allure
import os
import tempfile
from allure_commons.types import AttachmentType, Severity
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Fixture to set up and tear down the WebDriver
@pytest.fixture(scope="function")
def setup():
    chrome_options = Options()
    # Use a temporary directory for Chrome user data to avoid conflicts
    temp_dir = tempfile.mkdtemp()
    chrome_options.add_argument(f"--user-data-dir={temp_dir}")
    chrome_options.add_argument("--no-sandbox")  # Required for CI environments
    chrome_options.add_argument("--disable-dev-shm-usage")  # Avoid shared memory issues in CI
    chrome_options.add_argument("--headless")  # Run in headless mode for CI (optional)
    chrome_options.add_argument("--disable-gpu")  # Helps with headless stability
    chrome_options.add_argument("--window-size=1920,1080")  # Ensure proper rendering
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 40)
    yield driver, wait
    driver.quit()

# Step 1: Open the Website
@allure.step("Open the website")
def open_website(driver, wait):
    driver.get("https://dfperformance.azurewebsites.net/")
    driver.maximize_window()
    # Wait for the title to be present or a specific element to load
    wait.until(EC.title_contains("Datafortune Performance Accelerator-Stage"))
    allure.attach(driver.get_screenshot_as_png(), name="website_opened", attachment_type=AttachmentType.PNG)
    return "Website opened successfully"

@allure.step("Verify website title")
def verify_title(driver, expected_title="Datafortune Performance Accelerator-Stage"):
    # Wait for the exact title to match
    wait.until(EC.title_is(expected_title))
    actual_title = driver.title
    assert actual_title == expected_title, f"Title mismatch. Expected: {expected_title}, Got: {actual_title}"
    allure.attach(driver.get_screenshot_as_png(), name="title_verified", attachment_type=AttachmentType.PNG)
    return f"Title verified: {actual_title}"

# Step 2: Navigate to Microsoft Login
@allure.step("Navigate to Microsoft login page")
def navigate_to_microsoft_login_page(driver, wait):
    original_window = driver.current_window_handle
    sign_in_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btn loginButton')]"))
    )
    sign_in_button.click()
    wait.until(lambda d: len(d.window_handles) > 1)
    new_window_handles = [window for window in driver.window_handles if window != original_window]
    driver.switch_to.window(new_window_handles[0])
    allure.attach(driver.get_screenshot_as_png(), name="microsoft_login_page", attachment_type=AttachmentType.PNG)
    return "Navigated to Microsoft login page"

# Step 3: Enter Credentials
@allure.step("Enter username")
def enter_username(driver, wait, test_username="pratik.wavhal@datafortune.com"):
    username_field = wait.until(EC.presence_of_element_located((By.ID, "i0116")))
    username_field.clear()
    username_field.send_keys(test_username)
    next_button = wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
    next_button.click()
    allure.attach(driver.get_screenshot_as_png(), name="username_entered", attachment_type=AttachmentType.PNG)
    return f"Username entered: {test_username}"

@allure.step("Enter password")
def enter_password(driver, wait, password="Production@2024"):
    print("Current URL before password:", driver.current_url)
    allure.attach(driver.get_screenshot_as_png(), name="pre_password_page", attachment_type=AttachmentType.PNG)
    password_field = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='password']")))
    password_field.clear()
    password_field.send_keys(password)
    sign_in_button = wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
    sign_in_button.click()
    allure.attach(driver.get_screenshot_as_png(), name="password_entered", attachment_type=AttachmentType.PNG)
    return "Password entered successfully"

# Step 4: OTP Verification
@allure.step("Enter and verify OTP")
def enter_otp(driver, wait, otp="123456"):
    # Handle "Stay signed in?" prompt if it appears
    try:
        yes_button = wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
        yes_button.click()
        print("Clicked 'Yes' on 'Stay signed in?' prompt")
        allure.attach(driver.get_screenshot_as_png(), name="stay_signed_in", attachment_type=AttachmentType.PNG)
    except:
        print("No 'Stay signed in?' prompt detected")

    otp_field = wait.until(EC.visibility_of_element_located((By.NAME, "otc")))
    otp_field.clear()
    otp_field.send_keys(otp)
    verify_button = wait.until(EC.element_to_be_clickable((By.ID, "idSubmit_SAOTCC_Continue")))
    verify_button.click()
    allure.attach(driver.get_screenshot_as_png(), name="otp_verified", attachment_type=AttachmentType.PNG)
    return f"OTP {otp} entered and verified"

# Test Cases
@allure.title("Test 1: Open the website")
@allure.description("Verifies that the website opens successfully.")
@allure.severity(Severity.BLOCKER)
def test_open_website(setup):
    driver, wait = setup
    result = open_website(driver, wait)
    print(result)

@allure.title("Test 2: Verify website title")
@allure.description("Checks if the website title matches the expected value.")
@allure.severity(Severity.MAJOR)
def test_verify_title(setup):
    driver, wait = setup
    result = verify_title(driver)
    print(result)

@allure.title("Test 3: Navigate to Microsoft login page")
@allure.description("Ensures navigation to the Microsoft login page works.")
@allure.severity(Severity.BLOCKER)
def test_navigate_to_microsoft_login(setup):
    driver, wait = setup
    open_website(driver, wait)
    result = navigate_to_microsoft_login_page(driver, wait)
    print(result)

@allure.title("Test 4: Enter username")
@allure.description("Tests entering the username on the Microsoft login page.")
@allure.severity(Severity.CRITICAL)
def test_enter_username(setup):
    driver, wait = setup
    open_website(driver, wait)
    navigate_to_microsoft_login_page(driver, wait)
    result = enter_username(driver, wait)
    print(result)

@allure.title("Test 5: Enter password")
@allure.description("Tests entering the password on the Microsoft login page.")
@allure.severity(Severity.CRITICAL)
def test_enter_password(setup):
    driver, wait = setup
    open_website(driver, wait)
    navigate_to_microsoft_login_page(driver, wait)
    enter_username(driver, wait)
    result = enter_password(driver, wait)
    print(result)

@allure.title("Test 6: Enter and verify OTP")
@allure.description("Tests entering and verifying the OTP for login.")
@allure.severity(Severity.CRITICAL)
def test_enter_otp(setup):
    driver, wait = setup
    open_website(driver, wait)
    navigate_to_microsoft_login_page(driver, wait)
    enter_username(driver, wait)
    enter_password(driver, wait)
    result = enter_otp(driver, wait)
    print(result)

if __name__ == "__main__":
    pytest.main(["-q", "--tb=line", "--alluredir=./allure-results"])
