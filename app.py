#! python3


import requests
import tqdm
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from dateutil import parser, tz
import sqlite3
from flask import Flask, render_template, jsonify

app = Flask(__name__)

def initiate_database():
    conn = sqlite3.connect('./db/output.sqlite')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS techcrunch_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            title TEXT,
            url TEXT,
            timestamp TEXT,
            image_url TEXT,
            authors TEXT
        )
    ''')
    conn.commit()


scraped_dict = {}


def store_in_db(category, title, url, timestamp, image_url, authors):
    conn = sqlite3.connect('./db/output.sqlite')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO techcrunch_articles (category, title, url, timestamp, image_url, authors)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (category, title, url, timestamp, image_url, authors))
    conn.commit()

scraped_dict={}

def get_data():
    categories = ['https://techcrunch.com/category/artificial-intelligence/', 'https://techcrunch.com/category/apps/', 'https://techcrunch.com/category/biotech-health/', 'https://techcrunch.com/category/climate/', 'https://techcrunch.com/category/commerce/', 'https://techcrunch.com/category/cryptocurrency/', 'https://techcrunch.com/category/enterprise/', 'https://techcrunch.com/category/fintech/', 'https://techcrunch.com/category/gadgets/', 'https://techcrunch.com/category/gaming/', 'https://techcrunch.com/category/government-policy/', 'https://techcrunch.com/category/hardware/', 'https://techcrunch.com/category/media-entertainment/', 'https://techcrunch.com/category/privacy/', 'https://techcrunch.com/category/robotics/', 'https://techcrunch.com/category/security/', 'https://techcrunch.com/category/social/', 'https://techcrunch.com/category/space/', 'https://techcrunch.com/category/startups/', 'https://techcrunch.com/category/tc/', 'https://techcrunch.com/category/transportation/', 'https://techcrunch.com/category/venture/']
    counter= 0
    for category in tqdm.tqdm(categories):
        category_name = category.split('/')[-2].capitalize()

        res = requests.get(category)
        soup=BeautifulSoup(res.content, "html.parser")

        latest=soup.find(class_='river')

        no_of_articles=0
        articles=latest.find_all('div',class_='post-block')
        for _ in articles:
            no_of_articles+=1

        article_time_stamp=latest.find_all('time', class_="river-byline__time")

        article_title=latest.find_all('h2', class_='post-block__title')

        article_image_url=latest.find_all('footer',class_="post-block__footer")

        article_authors=latest.find_all('span', class_="river-byline__authors")


        for article in range(no_of_articles):
            each_article=[]
            each_article.append(category_name)
            each_article.append(article_title[article].find('a').get_text().strip())
            each_article.append(article_title[article].find('a').get('href'))

            scraped_dict[counter]=each_article

            raw_datetime=article_time_stamp[article]['datetime']
            raw_datetime=datetime.strptime(raw_datetime, '%Y-%m-%dT%H:%M:%S%z').astimezone()
            final_datetime=raw_datetime.strftime('%I:%M %p %Z %B %d, %Y')
            scraped_dict[counter].append(final_datetime)



            scraped_dict[counter].append(article_image_url[article].findChildren('img')[0]['src'])

            authors_list=[]
            for author in article_authors[article].find_all('a'):
                authors_list.append(author.get_text().strip())
            scraped_dict[counter].append(", ".join(authors_list))
            counter += 1
            store_in_db(each_article[0], each_article[1], each_article[2], each_article[3], each_article[4], each_article[5])


    return scraped_dict



@app.route("/")
def home():
    conn = sqlite3.connect('./db/output.sqlite')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM techcrunch_articles')
    data = cursor.fetchall()

    conn.close()

    html_response = render_template('homepage.html', data=data)

    json_response = jsonify(articles=[{
        'id': row[0],
        'category': row[1],
        'title': row[2],
        'url': row[3],
        'timestamp': row[4],
        'image_url': row[5],
        'authors': row[6]
    } for row in data])

    return html_response, 200, {'Content-Type': 'text/html'}


def fetch_data():
    conn = sqlite3.connect('./db/output.sqlite')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM techcrunch_articles')
    data = cursor.fetchall()
    conn.close()
    return data


@app.route('/json')
def json_data():
    data = fetch_data()

    # Convert data to JSON format
    json_response = jsonify(articles=[{
        'id': row[0],
        'category': row[1],
        'title': row[2],
        'url': row[3],
        'timestamp': row[4],
        'image_url': row[5],
        'authors': row[6]
    } for row in data])

    return json_response

flag = False
@app.before_request
def f():
    global flag
    if not flag:
        initiate_database()
        get_data()
        flag = True

        

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)



