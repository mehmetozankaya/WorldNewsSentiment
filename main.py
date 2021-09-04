# -*- coding: utf-8 -*-
"""
Created on Fri Mar 19 00:28:00 2021

@author: kelvin
"""
#import required libraries
from flask import Flask, render_template, json, jsonify, Response, request, redirect
import requests
from bs4 import BeautifulSoup  
from textblob import TextBlob
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path
from db import Mongo
import re
import string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.probability import FreqDist
import nltk
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')

app = Flask(__name__)


env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


#route for home page
@app.route('/index')
@app.route('/')
def index():
    return render_template('index.html')

#Route for scrape.html 
@app.route('/scrape')
def add():
    return render_template('scrape.html')

#Route for about.html page
@app.route("/about")
def about():
  return render_template("about.html")


#Route for getbooks api
@app.route('/getData-nyt')
def get_data_nyt():
    'fetches the records from the database to display it in the frontend plugin'
    # empty array to store data
    output = []
    
    for s in Mongo.nyTimesCol.find():
        del s['_id'] #delete the default ID created by mongoDB
        output.append(s)
    #create json object to pass to template
    data = {
        "data": output
    }
    return jsonify(data)

@app.route('/getData-cbs')
def get_data_cbs():
    'fetches the records from the database to display it in the frontend plugin'
    # empty array to store data
    output = []
    
    for s in Mongo.cbsNewsCol.find():
        del s['_id'] #delete the default ID created by mongoDB
        output.append(s)
    #create json object to pass to template
    data = {
        "data": output
    }
    return jsonify(data)
    
@app.route('/api/scrape-nyt')
def scrape_Data_nyt():
    newYorkTimes()
    return redirect('/scrape')



@app.route('/api/scrape-cbs')
def scrape_Data_cbs():
    cbsNews()
    return redirect('/scrape')


def newYorkTimes():
    URL = 'https://rss.nytimes.com/services/xml/rss/nyt/World.xml'
    data_col = Mongo.nyTimesCol
    wc_col = Mongo.nyWcCol
    scrapeArticles(URL, data_col, wc_col)

def cbsNews():
    URL = 'https://www.cbsnews.com/latest/rss/world'
    data_col = Mongo.cbsNewsCol
    wc_col = Mongo.cbsWcCol
    scrapeArticles(URL, data_col, wc_col)

def scrapeArticles(URL,data_col, wc_col):
    newsURL = URL
    col = data_col
    col.drop()
    wcCol = wc_col
    wcCol.drop()
    
    newsGet = requests.get(newsURL)
    newsSoup = BeautifulSoup(newsGet.content, features='xml')
    news = newsSoup.findAll('item')
    totalDescription = ''

    newsArticles = []
    for article in news:
        newsArticle = {}
        newsArticle['title'] = article.title.text
        newsArticle['description'] = article.description.text
        newsArticle['link'] = article.link.text
        newsArticle['date'] = article.pubDate.text
        

        useBlob = article.title.text
        blob = TextBlob(useBlob) 
        newsArticle['polarity'] = blob.sentiment.polarity
        
        if newsArticle['polarity'] > 0:
            newsArticle['sentiment'] = 'Positive'
        elif newsArticle['polarity'] < 0:
            newsArticle['sentiment'] = 'Negative'
        else:
            newsArticle['sentiment'] = 'Neutral'

        newsArticles.append(newsArticle)
        totalDescription += newsArticle['description']

    df = pd.DataFrame(newsArticles,columns=['title','description','link','date','polarity','sentiment'])
    col.insert_many(df.to_dict('records'))
    rDict = wordCount(totalDescription)
    wcCol.insert_many(rDict)

def wordCount(tdesc):
    text = re.sub('<[^<]+?>', '', tdesc)
    text = text.lower()
    text = text.replace('"','')
    text = text.replace('“','')
    text = text.replace('”','')
    text = text.replace("’",'')

    strip = str.maketrans('','', string.punctuation)
    text = text.translate(strip)

    tokenized_word=word_tokenize(text)
    tokenized_word = [word.lower() for word in tokenized_word]

    stop_words = set(stopwords.words('english'))
    filtered_word = []

    for word in tokenized_word:
        if word not in stop_words:
            filtered_word.append(word)

    lem = WordNetLemmatizer()
    lem_words = []
    for w in filtered_word:
        lem_words.append(lem.lemmatize(w,'v'))

    fdist = FreqDist(lem_words)
    most_common = fdist.most_common(100)
    wcDict = []
    for item in most_common:
        res = {'word' : item[0], 'count': item[1]}
        wcDict.append(res)
    return wcDict





if __name__ == '__main__':
    app.run()