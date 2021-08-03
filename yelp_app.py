#!/usr/bin/env python

#import libraries
import flask
from flask import Flask, json, render_template, redirect
import requests
import os
from bs4 import BeautifulSoup as bs
from lxml import html

#create instance of app
app = flask.Flask(__name__)

#greeting page
@app.route('/', methods = ['GET'])
def home():
    return '''<h1>Top 50 Local Restaurants</h1>
    <p>This site is an API for retrieval of information about the top 50 local restaurants to Benton Park, MO.</p>
    <p>In order to access a scraping tool to retrieve urls for the top 50 restaurants visit: http://127.0.0.1:5000/api/v1/top50/urls<p>
    <p>In order to access a scraping tool to retrieve this information: http://127.0.0.1:5000/api/v1/top50/scrape<p>
    <p>In order to access a list of the top 50 restaurants and their details: http://127.0.0.1:5000/api/v1/top50/all<p>'''

@app.route('/api/v1/top50/urls', methods=['GET'])
def get_urls():
    all_urls = []
    for i in range(0, 50, 10):
        url = f'https://www.yelp.com/search?find_desc=&find_loc=Saint%20Louis%2C%20MO%2063104&start={i}'
        response = requests.get(url)
        soup = bs(response.text, 'html.parser')
        for item in soup.select('h4'): 
            try:  
                if item.find('a'):
                    href = item.find('a', href = True)
                    all_urls.append(href['href'])
            except Exception as e: 
                raise e 
                print('')
    with open('all_urls.json', 'w') as fout:
        json.dump(all_urls, fout)                
    return '''<h1>all_urls have been received</h1>'''
@app.route('/api/v1/top50/scrape', methods=['GET'])                
def yelp_scraped():
    rest_dict={}
    top_50=[]
    all_urls = os.path.join('all_urls.json')
    data_json_file = json.load(open(all_urls))
    all_urls=data_json_file
    #return render_template('index.html',data=data_json)  
    for url in all_urls:  
        path = "https://www.yelp.com" + url
        response=requests.get(path)
        soup = bs(response.text, 'html.parser')
        tree = html.fromstring(response.content)
        try:  
            restaurant=tree.xpath('//*[@id="wrap"]/div[2]/yelp-react-root/div[1]/div[3]/div[1]/div[1]/div/div/div[1]/h1/text()')
            restaurant_location=tree.xpath('//*[@id="wrap"]/div[2]/yelp-react-root/div[1]/div[4]/div/div/div[2]/div/div[2]/div/div/section[1]/div/div[3]/div/div[1]/p[2]/text()')
            phone = tree.xpath('//*[@id="wrap"]/div[2]/yelp-react-root/div[1]/div[4]/div/div/div[2]/div/div[2]/div/div/section[1]/div/div[2]/div/div[1]/p[2]/text()')
            restaurant_website = tree.xpath('//*[@id="wrap"]/div[2]/yelp-react-root/div[1]/div[4]/div/div/div[2]/div/div[2]/div/div/section[1]/div/div[1]/div/div[1]/p[2]/a/text()')
            price = tree.xpath('//*[@id="wrap"]/div[2]/yelp-react-root/div[1]/div[3]/div[1]/div[1]/div/div/span[2]/span/text()')
            rest_dict={'name': restaurant, 'location': restaurant_location, 'phone_number': phone, 'website': restaurant_website, 'price_range': price}
            top_50.append(rest_dict)
        except Exception as e: 
            raise e 
            print('')
    with open('outputfile.json', 'w') as fout:
        json.dump(top_50, fout)        
    return redirect ('/api/v1/top50/all')

@app.route('/api/v1/top50/all', methods=['GET'])
#def api_all():
def home2():
    json_url = os.path.join('outputfile.json')
    data_json = json.load(open(json_url))
    return render_template('index.html',data=data_json)  

if __name__ == "__main__":
    app.run(debug=True)    