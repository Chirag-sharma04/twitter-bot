# Twitter Tweet Scraper and Intent Analyzer

This Python script scrapes tweets from Twitter (X) based on a specified keyword, extracts metadata, and analyzes the tweets' content by comparing them against predefined intent sentences using cosine similarity. The script leverages Selenium to automate browser interactions and pandas for data manipulation.

## Prerequisites

* Python 3.x
* Chrome browser installed
* Selenium library (`pip install selenium`)
* webdriver-manager (`pip install webdriver-manager`)
* pandas library (`pip install pandas`)
* cosine_sim.py file (a python file that contains the calculate_similarity_scores function)

## Setup

1.  **Install Dependencies:**

    ```bash
    pip install selenium webdriver-manager pandas
    ```

2.  **Chrome User Data Directory:**
    * The script uses a specific Chrome user data directory (`C:\Users\LENOVO\AppData\Local\Google\Chrome\User Data`) and profile (`Profile 1`).
    * **Important:** You need to replace this path with the actual path to your Chrome user data directory and profile. This allows the script to use your logged-in Chrome session for persistent login.
    * To find your Chrome user data directory:
        * Open Chrome.
        * Go to `chrome://version/`.
        * Look for "Profile Path". The parent directory of this path is your user data directory.
        * To find your profile name, examine the folder names under the user data directory.
3.  **`cosine_sim.py`:**
    * Create a file named `cosine_sim.py` in the same directory as your script.
    * This file should contain a function named `calculate_similarity_scores` that takes a list of tweet texts and a list of intent sentences as input and returns a matrix of cosine similarity scores.
4.  **Predefined Intent Sentences:**
    * The `intent_data` list in the script contains predefined intent sentences for comparison. You can modify this list to suit your specific analysis needs.

## Usage

1.  **Run the Script:**

    ```bash
    python your_script_name.py
    ```

2.  **Keyword Input:**
    * The script uses the keyword "supabase" by default. You can change the `keyword` variable in the `if __name__ == "__main__":` block to scrape tweets related to a different keyword.
3.  **Tweet Scraping:**
    * The script will open a Chrome browser window, navigate to Twitter (X), and perform a search for the specified keyword.
    * It will dynamically scroll and load tweets until it has scraped at least 100 tweets (or the number specified by `num_tweets`).
    * The script will extract metadata such as profile handle, profile link, tweet text, tweet URL, and timestamp.
4.  **Intent Analysis:**
    * The script will analyze the scraped tweets by comparing their text against the predefined intent sentences using cosine similarity.
    * For each tweet, it will identify the most relevant intent sentence and calculate the similarity score.
5.  **Output:**
    * The script will save the analysis results to a CSV file named `Test_result.csv` in the same directory.
    * The CSV file will contain columns such as "Profile Handle", "Profile Link", "DocURL", "Date", "Time", "Target Sentence" (tweet text), "Best Matched Intent", and "Similarity Score".

## Code Explanation

* **`setup_driver()`:**
    * Initializes the Selenium WebDriver with Chrome options, including the user data directory and profile.
    * Uses `webdriver_manager` to automatically download the correct ChromeDriver.
* **`scrape_tweets_with_metadata()`:**
    * Navigates to the Twitter search page for the specified keyword.
    * Dynamically scrolls and loads tweets using Selenium.
    * Extracts tweet metadata using XPath selectors.
    * Handles dynamic content loading and potential errors.
* **`analyze_tweets()`:**
    * Compares tweet texts against predefined intent sentences using cosine similarity.
    * Identifies the most relevant intent and calculates the similarity score.
    * Creates a pandas DataFrame with the analysis results.
* **`if __name__ == "__main__":`:**
    * Sets the keyword and number of tweets to scrape.
    * Calls the scraping and analysis functions.
    * Saves the results to a CSV file.

## Notes

* This script relies on the HTML structure of the Twitter page. If Twitter changes its HTML, the script may need to be updated.
* The refresh interval and wait times can be adjusted in the script.
* Make sure that your Chrome user data directory and profile are correctly specified.
* The quality of the intent analysis depends on the accuracy of the `cosine_sim.py` function and the relevance of the predefined intent sentences.
* Due to changes to X.com, this script may need to have the xpath updated frequently.
