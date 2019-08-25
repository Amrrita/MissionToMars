# import all dependencies
# if __name__ == "__main__":
from bs4 import BeautifulSoup
import re
from splinter import Browser
import pandas as pd
import requests

def init_browser():
    executable_path = {"executable_path": "chromedriver.exe"}
    return Browser("chrome", **executable_path, headless=True)

def scrape ():
    """Scrapes various websites for information about Mars, and returns data in a dictionary"""
    
    browser = init_browser()
    mars_data = {}

    #text splinter
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    #HTML, then parse with BeautifulSoup
    html = browser.html
    bsoup = BeautifulSoup(html, 'html.parser')

    #most recent news title and paragraph
    news_title = bsoup.find('div', class_ = 'content_title').find('a')
    news_p = bsoup.find('div', class_= 'article_teaser_body').text

    # Add the news title and summary to the dictionary
    mars_data["news_title"] = news_title
    mars_data["summary"] = news_p

    #JPL Mars Space Images
    #Images splinter
    image_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(image_url)
    #getting images
    page = requests.get('https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars')
    soup = BeautifulSoup(page.content, 'html.parser')
    x = soup.find('div', attrs={'class':"carousel_items"}).article['style']

    # use RegEx to extract url between the ' '
    image_url = (re.findall(r"'(.*?)'",x,re.DOTALL)[0])

    #full url
    featured_image_url = 'https://www.jpl.nasa.gov/spaceimages/' + image_url

    # Add the featured image url to the dictionary
    mars_data["featured_image_url"] = featured_image_url

    #Mars Weather
    # Visit Mars Weather Twitter through splinter module
    weather_url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(weather_url)

    # HTML Object 
    html_weather = browser.html

    # Parse HTML with Beautiful Soup
    soup = BeautifulSoup(html_weather, 'html.parser')

    # Find all elements that contain tweets
    latest_tweets = soup.find_all('div', class_='js-tweet-text-container')

    # Retrieve all elements that contain news title in the specified range
    # Look for entries that display weather related words to exclude non weather related tweets 
    for tweet in latest_tweets: 
        weather_tweet = tweet.find('p').text
        if 'Sol' and 'pressure' in weather_tweet:
            print(weather_tweet)
            break
        else: 
            pass

    # Add the weather to the dictionary
    mars_data["mars_weather"] = weather_tweet

    #Mars Facts
    url = "https://space-facts.com/mars/"
    table = pd.read_html(url) 

    df = table[0]
    df1 = df.iloc[:,0:2]
    new_df = df1.rename(columns={"Mars-Earth Comparison": "Property", "Mars": "Value"})

    new_df.columns = ['Property', 'Value']
    #Add mars facts table to the dictionary
    mars_data["mars_table"] = new_df

    #hemisphere
    # Visit hemispheres website through splinter module 
    hemispheres_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hemispheres_url)
    # HTML Object
    html_hemispheres = browser.html

    # Parse HTML with Beautiful Soup
    soup = BeautifulSoup(html_hemispheres, 'html.parser')

    # Retreive all items that contain mars hemispheres information
    items = soup.find_all('div', class_='item')

    # Create empty list for hemisphere urls 
    hemisphere_image_urls = []

    #  Store the main_ul 
    hemispheres_main_url = 'https://astrogeology.usgs.gov'

    # Loop through the items previously stored
    for i in items: 
    # Store title
        title = i.find('h3').text
    
    # Store link that leads to full image website
    partial_img_url = i.find('a', class_='itemLink product-item')['href']
    # Visit the link that contains the full image website 
    browser.visit(hemispheres_main_url + partial_img_url)
    
    # HTML Object of individual hemisphere information website 
    partial_img_html = browser.html
    
    # Parse HTML with Beautiful Soup for every individual hemisphere information website 
    soup = BeautifulSoup( partial_img_html, 'html.parser')
    
    # Retrieve full image source 
    img_url = hemispheres_main_url + soup.find('img', class_='wide-image')['src']
    
    # Append the retreived information into a list of dictionaries 
    hemisphere_image_urls.append({"title" : title, "img_url" : img_url})
    

    # Appens
    mars_data['mars_hemi'] =hemisphere_image_urls


    browser.back()

    #return dictionary
    return mars_data

