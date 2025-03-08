import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from cosine_sim import calculate_similarity_scores  # Ensure cosine_sim.py exists

# Predefined intent sentences for comparison
intent_data = [
    "Looking for alternatives to Firebase",
    "Need a scalable database solution",
    "Trying to migrate my backend to Supabase",
    "Looking for an open-source authentication provider",
    "What are the benefits of Supabase?",
    "Best NoSQL database options for my project",
    "How does Supabase compare to Firebase?"
]

# Setup Selenium WebDriver with logged-in Chrome session
def setup_driver():
    print("Setting up Chrome driver...")
    chrome_options = Options()
    
    # Use existing Chrome profile for login persistence
    chrome_options.add_argument(r'--user-data-dir=C:\Users\LENOVO\AppData\Local\Google\Chrome\User Data')
    chrome_options.add_argument(r'--profile-directory=Profile 1')
    
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

# Scrape at least 100 tweets dynamically
def scrape_tweets_with_metadata(keyword, num_tweets=100):
    driver = setup_driver()
    
    print("Opening Twitter...")
    driver.get("https://x.com")
    time.sleep(5)  # Allow login session to load

    # Navigate to Twitter search page
    search_url = f"https://x.com/search?q={keyword}&src=typed_query&f=live"
    driver.get(search_url)
    time.sleep(5)
    
    divxpath = '//div[@data-testid="cellInnerDiv"]'
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, divxpath)))
    
    row = driver.find_element(By.XPATH, divxpath)
    action = ActionChains(driver)
    
    x, y = 0, 0  # Iteration controls
    tweets_data = []
    
    while len(tweets_data) < num_tweets:
        try:
            nexts = driver.execute_script("return arguments[0].nextSibling;", row)
            
            try:
                action.move_to_element(nexts).perform()
            except Exception:
                pass
            
            tweet_info = {}

            # Extract profile handle and profile link
            try:
                profile = row.find_element(By.XPATH, './/div[@data-testid="User-Name"]')
                tweet_info["Profile Link"] = profile.find_elements(By.XPATH, './/a')[1].get_attribute('href')
                tweet_info["Profile Handle"] = profile.find_elements(By.XPATH, './/a')[1].text
            except Exception:
                pass

            # Extract tweet text
            try:
                tweet_info["Post"] = row.find_element(By.XPATH, ".//div[@data-testid='tweetText']").text
            except Exception:
                pass

            # Extract tweet URL
            try:
                tweet_info["DocURL"] = row.find_elements(By.XPATH, './/a[contains(@href,"status")]')[0].get_attribute('href')
            except Exception:
                pass

            # Extract timestamp (Date & Time)
            try:
                dt=row.find_element(By.XPATH,'.//time').get_attribute('datetime').split("T")
                df.at[y,"Date"]=dt[0]
                df.at[y,"Time"]=dt[1]
                #print(dt[1])
            except Exception as e:
                pass
            
            if "Post" in tweet_info and "DocURL" in tweet_info:
                tweets_data.append(tweet_info)

            nexts = driver.execute_script("return arguments[0].nextSibling;", row)
            row = nexts
            x += 1

            # Scroll down after every 10 tweets to ensure new ones load
            if x % 10 == 0:
                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
                time.sleep(3)

        except Exception:
            try:
                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
                time.sleep(2)
                row = driver.find_element(By.XPATH, divxpath)
                nexts = driver.execute_script("return arguments[0].nextSibling;", row)
            except Exception:
                pass

    driver.quit()  # Close driver
    print(f"Scraped {len(tweets_data)} tweets.")
    return tweets_data

# Analyze tweets by comparing against predefined intent data
def analyze_tweets(tweets_data):
    results = []
    tweets_text = [tweet["Post"] for tweet in tweets_data]

    # Compare each tweet against predefined intents
    similarity_scores = calculate_similarity_scores(tweets_text, intent_data)  

    for i, tweet in enumerate(tweets_data):
        # Get the highest similarity score for the tweet
        best_match_index = similarity_scores[i].argmax()
        best_match_score = similarity_scores[i, best_match_index].item()
        best_match_intent = intent_data[best_match_index]

        results.append({
            "Profile Handle": tweet.get("Profile Handle", ""),
            "Profile Link": tweet.get("Profile Link", ""),
            "DocURL": tweet.get("DocURL", ""),
            "Date": tweet.get("Date", ""),
            "Time": tweet.get("Time", ""),
            "Target Sentence": tweets_text[i],  
            "Best Matched Intent": best_match_intent,  # Most relevant intent
            "Similarity Score": round(best_match_score, 6)  # Convert tensor to float and round
        })

    df = pd.DataFrame(results)
    return df

# Main execution
if __name__ == "__main__":
    keyword = "supabase"
    tweets_data = scrape_tweets_with_metadata(keyword, num_tweets=100)
    
    df = analyze_tweets(tweets_data)

    # Save CSV file with correct formatting
    csv_filename = "Test_result.csv"
    df.to_csv(csv_filename, index=False)
    print(f"Analysis complete! Saved to {csv_filename}")
