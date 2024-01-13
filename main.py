import tweepy
import dotenv
import os
from langchain_openai import ChatOpenAI
from pytrends.request import TrendReq
import pandas as pd
import requests
from langchain_core.prompts import ChatPromptTemplate


# Create Twython instance and today trends
def get_trend() -> pd.DataFrame:
    pytrend = TrendReq()
    trendingtoday = pytrend.today_searches(pn='US')
    trendingtoday = trendingtoday.apply(lambda x: x.split('=')[1].split('&')[0].replace('+', ' '))
    return trendingtoday

# get information about the trend
def get_trends_info(trend : str) -> list:
    url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={trend} latest news&start={1}"
    response = requests.get(url)
    items = response.json().get("items",[])
    return [item["snippets"] for item in items]

# Post a tweet
def post_message(text : str) -> None:
    client = tweepy.Client(bearer_token=bearer_token,consumer_key=consumer_key,consumer_secret=consumer_secret,access_token=access_token,access_token_secret=access_token_secret)
    client.create_tweet(text=text)

# Generate a tweet using langchain and openai
def generate_tweet(topic : str,resource : str) -> str:
    llm = ChatOpenAI(api_key=os.getenv('openai_api'))
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a regular twitter user who like to tweet about trending topics."),
        ("user", "generate a tweet about this topic {topic} using these resources {resource}")
    ])
    chain = prompt | llm
    tweet = chain.invoke({"topic": topic, "resource": resource})
    return tweet


if __name__ == "__main__":
    # Load environment variables
    dotenv.load_dotenv()
    consumer_key = os.getenv('consumer_key')
    consumer_secret = os.getenv('consumer_secret')
    access_token = os.getenv('access_token')
    access_token_secret = os.getenv('access_token_secret')
    bearer_token = os.getenv('bearer_token')
    API_KEY = os.getenv('google_search')
    SEARCH_ENGINE_ID = os.getenv("search_engin_id")
    # execute
    trends = get_trend()
    topic = trends[0]
    resources = get_trends_info(topic)
    tweet = generate_tweet(topic,resources)
    #post_message(tweet)