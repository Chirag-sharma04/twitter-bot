import time
import psutil
from datetime import datetime
import pandas as pd
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import os

# Text preprocessing function
def preprocess(text):
    if not isinstance(text, str):  # Check if input is not a string
        return ""  # Return an empty string if input is not a string
    
    # Remove URLs
    text = re.sub(r'http\S+', '', text)
    # Remove mentions
    text = re.sub(r'@\w+', '', text)
    # Remove hashtags
    text = re.sub(r'#\w+', '', text)
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    # Convert to lowercase
    text = text.lower()
    
    return text.strip()

# Calculate similarity scores between tweets and intents
def calculate_similarity_scores(tweets, intents):
    print(f"Calculating similarity scores between {len(tweets)} tweets and {len(intents)} intents...")
    
    # Preprocess tweets and intents
    preprocessed_tweets = [preprocess(tweet) for tweet in tweets]
    preprocessed_intents = [preprocess(intent) for intent in intents]
    
    # Combine tweets and intents for vectorization
    all_texts = preprocessed_tweets + preprocessed_intents
    
    # Create TF-IDF vectors
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(all_texts)
    
    # Split the matrix back into tweets and intents
    tweets_tfidf = tfidf_matrix[:len(tweets)]
    intents_tfidf = tfidf_matrix[len(tweets):]
    
    # Calculate cosine similarity
    similarity_matrix = cosine_similarity(tweets_tfidf, intents_tfidf)
    
    # Calculate average similarity for each tweet
    avg_similarities = np.mean(similarity_matrix, axis=1)
    
    return similarity_matrix, avg_similarities

# Initialize database with intent data
def initialize_DB():
    # Define your intents here
    intents = {
        'financial_results': [
            'first quarter 2023 financial results revenue was $134.3 million for the first quarter of 2023, a 17% increase from $114.5 million for the corresponding prior year period.'
        ],
        'building': [
            'What are you working on this weekend?', 
            'are u building today?', 
            'What are you building today?', 
            'Hello builders, it/s Saturday but we/re still building.'
        ],
        'marketing': [
            'market', 
            'marketing strategy', 
            'product launch', 
            'customer acquisition'
        ],
        'database_question': [
            'How do I set up a database with Supabase?',
            'Looking for help with database configuration and setup.',
            'Need assistance with Supabase database integration'
        ],
        'authentication': [
            'Authentication with Supabase',
            'How to implement login and signup with Supabase',
            'User management features in Supabase'
        ],
        'vector_search': [
            'Using vector search with Supabase',
            'AI features with Supabase for semantic search',
            'How to implement embeddings with Supabase'
        ]
    }
    
    # Create a dataframe from the intents
    rows = []
    for intent_name, sentences in intents.items():
        for sentence in sentences:
            rows.append({
                'Intent': intent_name,
                'Target sentence': sentence
            })
    
    return pd.DataFrame(rows)

# Setup and configure the web driver for Twitter scraping
def setup_driver():
    print("Setting up Chrome driver...")
    chrome_options = Options()
    
    # Use existing Chrome profile for a logged-in session
    chrome_options.add_argument(r'--user-data-dir=C:\Users\LENOVO\AppData\Local\Google\Chrome\User Data')
    chrome_options.add_argument(r'--profile-directory=Profile 1')
    
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver


# Scrape tweets for a given keyword
def scrape_tweets(driver, keyword, min_tweets=100):
    print(f"Scraping tweets for keyword: {keyword}")
    url = f"https://x.com/search?q={keyword}&src=typed_query&f=live"
    
    driver.get(url)
    time.sleep(5)  # Wait for page to load
    
    tweets = []
    usernames = []
    timestamps = []
    tweet_urls = []
    
    # Scroll to load more tweets
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_count = 0
    max_scrolls = 30  # Limit scrolling to prevent infinite loops
    
    while len(tweets) < min_tweets and scroll_count < max_scrolls:
        # Scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Wait for content to load
        
        # Get all tweet elements
        tweet_elements = driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')
        
        for tweet_element in tweet_elements:
            try:
                # Extract tweet text
                tweet_text_element = tweet_element.find_element(By.CSS_SELECTOR, 'div[data-testid="tweetText"]')
                tweet_text = tweet_text_element.text
                
                # Extract username
                username_element = tweet_element.find_element(By.CSS_SELECTOR, 'div[data-testid="User-Name"] a')
                username = username_element.get_attribute("href").split("/")[-1]
                
                # Extract timestamp if available
                try:
                    time_element = tweet_element.find_element(By.CSS_SELECTOR, 'time')
                    timestamp = time_element.get_attribute("datetime")
                    tweet_url = time_element.find_element(By.XPATH, "..").get_attribute("href")
                except:
                    timestamp = "Unknown"
                    tweet_url = f"https://x.com/{username}/status/unknown"
                
                # Only add if this tweet is not already in our list
                if tweet_text not in tweets:
                    tweets.append(tweet_text)
                    usernames.append(username)
                    timestamps.append(timestamp)
                    tweet_urls.append(tweet_url)
                    
                    if len(tweets) >= min_tweets:
                        break
            except Exception as e:
                print(f"Error extracting tweet: {e}")
                continue
        
        # Check if we've reached the bottom of the page
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # Try one more time with a longer wait
            time.sleep(3)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
        
        last_height = new_height
        scroll_count += 1
        print(f"Scrolled {scroll_count} times, found {len(tweets)} tweets so far")
    
    # Create a dataframe with the scraped tweets
    tweet_data = {
        'Username': usernames,
        'Tweet': tweets,
        'Timestamp': timestamps,
        'URL': tweet_urls
    }
    
    return pd.DataFrame(tweet_data)

# Main function to run the Twitter bot
def main():
    start_time = datetime.now()
    print(f"Starting Twitter bot at {start_time}")
    
    # Initialize database with intent data
    df_intents = initialize_DB()
    print(f"Loaded {len(df_intents)} intent sentences")
    
    # Setup web driver
    driver = setup_driver()
    
    try:
        # Scrape tweets
        keyword = "supabase"  # Change this to your desired keyword
        df_tweets = scrape_tweets(driver, keyword, min_tweets=100)
        print(f"Scraped {len(df_tweets)} tweets")
        
        if len(df_tweets) == 0:
            print("No tweets found. Exiting.")
            return
        
        # Calculate similarity scores
        intent_sentences = df_intents['Target sentence'].tolist()
        tweet_texts = df_tweets['Tweet'].tolist()
        
        similarity_matrix, avg_similarities = calculate_similarity_scores(tweet_texts, intent_sentences)
        df_tweets['Similarity Score'] = avg_similarities.tolist()
        
        # Find the best matching intent for each tweet
        best_intents = []
        best_intent_scores = []
        
        for i, tweet in enumerate(tweet_texts):
            # Get the similarity scores for this tweet against all intents
            tweet_similarities = similarity_matrix[i]
            
            # Find the index of the intent with the highest similarity
            best_intent_idx = np.argmax(tweet_similarities)
            best_intent_score = tweet_similarities[best_intent_idx]
            
            # Get the intent name from the dataframe
            best_intent_row = df_intents.iloc[best_intent_idx]
            best_intent = best_intent_row['Intent']
            
            best_intents.append(best_intent)
            best_intent_scores.append(best_intent_score)
        
        df_tweets['Best Intent'] = best_intents
        df_tweets['Best Intent Score'] = best_intent_scores
        
        # Sort by similarity score
        df_tweets = df_tweets.sort_values(by='Similarity Score', ascending=False)
        
        # Save results to CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"{keyword}_tweet_analysis_{timestamp}.csv"
        df_tweets.to_csv(output_file, index=False)
        print(f"Results saved to {output_file}")
        
        # Display top 10 tweets by similarity score
        print("\nTop 10 tweets by similarity score:")
        for i, row in df_tweets.head(10).iterrows():
            print(f"Username: @{row['Username']}")
            print(f"Tweet: {row['Tweet'][:100]}...")
            print(f"Best Intent: {row['Best Intent']}")
            print(f"Similarity Score: {row['Similarity Score']:.4f}")
            print("-" * 80)
        
        # Simulate engagement with users
        print("\nSimulating engagement with users:")
        engagement_threshold = 0.3  # Adjust this threshold as needed
        engagement_count = 0
        
        for i, row in df_tweets[df_tweets['Best Intent Score'] > engagement_threshold].iterrows():
            engagement_count += 1
            print(f"Would engage with @{row['Username']} (score: {row['Best Intent Score']:.4f})")
            print(f"Tweet: {row['Tweet'][:100]}...")
            print(f"Best Intent: {row['Best Intent']}")
            
            # Generate a response based on the intent
            if row['Best Intent'] == 'database_question':
                response = "Thanks for your interest in Supabase databases! Have you checked out our documentation? Happy to help if you have specific questions."
            elif row['Best Intent'] == 'authentication':
                response = "Supabase auth is super easy to implement! Let me know if you need any help with your authentication setup."
            elif row['Best Intent'] == 'vector_search':
                response = "Vector search in Supabase is powerful for AI applications! Are you building something with embeddings?"
            elif row['Best Intent'] == 'building':
                response = "Exciting to see what you're building! Would love to hear more about your project with Supabase."
            else:
                response = "Thanks for mentioning Supabase! Let me know if you have any questions."
                
            print(f"Response: {response}")
            print("-" * 80)
            
            if engagement_count >= 10:  # Limit example output
                break
    
    except Exception as e:
        print(f"Error in main function: {e}")
    
    finally:
        # Close the driver
        driver.quit()
        
        # Calculate and print execution time
        stop_time = datetime.now()
        time_difference = stop_time - start_time
        time_difference_seconds = time_difference.total_seconds()
        print(f"Total execution time: {time_difference_seconds} seconds")
        
        # Get CPU and memory usage
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        print(f"CPU Usage: {cpu_usage}%")
        print(f"Memory Usage: {memory_usage}%")

if __name__ == "__main__":
    main()