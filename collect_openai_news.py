import requests
import xml.etree.ElementTree as ET
import datetime

RSS_FEED_URL = "https://openai.com/news/rss.xml"

def get_openai_news_from_rss():
    """
    Fetches recent news articles about OpenAI from the official RSS feed.
    """
    try:
        response = requests.get(RSS_FEED_URL)
        response.raise_for_status()  # Raise an exception for bad status codes
        root = ET.fromstring(response.content)

        articles = []
        for item in root.findall(".//item"):
            title = item.find("title").text
            pub_date_str = item.find("pubDate").text
            # Parse the date and check if it's within the last 30 days
            # Example pubDate: Tue, 15 Oct 2025 10:00:00 GMT
            pub_date = datetime.datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S %Z")
            if pub_date.date() > (datetime.date.today() - datetime.timedelta(days=30)):
                articles.append(title)

        if articles:
            print(f"Found {len(articles)} articles from the OpenAI RSS feed in the last month:")
            for i, title in enumerate(articles[:20]):
                print(f"{i+1}. {title}")
        else:
            print("No articles found in the OpenAI RSS feed in the last month.")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the RSS feed: {e}")
    except ET.ParseError as e:
        print(f"An error occurred while parsing the RSS feed: {e}")

if __name__ == "__main__":
    get_openai_news_from_rss()