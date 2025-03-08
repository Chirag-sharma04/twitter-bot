import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from cosine_sim import calculate_similarity_scores  # Ensure cosine_sim.py exists

# Intent sentences for similarity matching
intent_sentences = [
    "Supabase is an open-source Firebase alternative",
    "Supabase offers Postgres database with real-time subscriptions",
    "Supabase authentication supports OAuth, JWT, and social logins",
    "Supabase storage allows users to manage files and images",
    "Supabase integrates with Edge Functions for serverless computing"
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

# Scrape tweets dynamically and capture metadata
def scrape_tweets_with_metadata(keyword, num_tweets=100):
    driver = setup_driver()
    
    print("Opening Twitter...")
    driver.get("https://x.com")
    time.sleep(5)  # Allow login session to load

    # Navigate to Twitter search page
    search_url = f"https://x.com/search?q={keyword}&src=typed_query&f=live"
    driver.get(search_url)
    time.sleep(5)
    
    tweets_data = []
    body = driver.find_element(By.TAG_NAME, 'body')

    scroll_attempts = 0  # To ensure we scrape 100 tweets
    while len(tweets_data) < num_tweets and scroll_attempts < 50:
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(2)
        
        tweet_elements = driver.find_elements(By.XPATH, "//article[@data-testid='tweet']")
        
        for elem in tweet_elements:
            try:
                # Extract tweet text
                tweet_text = elem.find_element(By.XPATH, ".//div[@data-testid='tweetText']").text
                
                # Extract tweet URL
                tweet_url = elem.find_element(By.XPATH, ".//a[contains(@href, '/status/')]").get_attribute("href")
                
                # Extract timestamp (convert to year)
                timestamp = elem.find_element(By.TAG_NAME, "time").get_attribute("datetime")
                tweet_year = timestamp[:4]  # Extracting year (YYYY)

                if tweet_text and tweet_url:  # Ensure valid data
                    tweets_data.append({
                        "text": tweet_text,
                        "url": tweet_url,
                        "year": tweet_year
                    })

                if len(tweets_data) >= num_tweets:
                    break

            except Exception as e:
                print("Error extracting tweet:", e)
        
        scroll_attempts += 1

    driver.quit()  # Close driver
    print(f"Scraped {len(tweets_data)} tweets.")
    return tweets_data

# Analyze tweets and generate structured data
def analyze_tweets(tweets_data):
    results = []
    tweets_text = [tweet["text"] for tweet in tweets_data]
    similarity_scores = calculate_similarity_scores(tweets_text, intent_sentences)  # Compute similarity

    for i, tweet in enumerate(tweets_data):
        results.append({
            "ticker": "TXG",  # Static or extracted from query context
            "SentenceT": f"[{tweet['year']}]",  # Year from timestamp
            "Target sentence": tweet["text"],
            "upload-da:id": "####",  # Placeholder
            "Page": i + 1,  # Simulated page number
            "DocURL": tweet["url"],  # Actual tweet URL
            "DocTitle": "Twitter Post",  # Generic title
            "Similarity Score": round(similarity_scores[i].item(), 6)  # Convert tensor to float and round
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
