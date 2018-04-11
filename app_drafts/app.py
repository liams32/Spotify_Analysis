import spotipy
import spotipy.oauth2
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import numpy as np
import os
from json.decoder import JSONDecodeError

from flask import render_template, Flask, request

import misc_functions #functions we write

app = Flask(__name__) #create app

@app.route('/')
def main(): #make homepage
    html = render_template('homepage.html')
    return(html)

@app.route('/homepage')
def homepage():
    html = render_template('homepage.html')
    return(html)

@app.route('/search', methods = ('GET', 'POST'))
def search():
	if request.method == 'POST':
		artist_name = request.form['Artist'] #request Artist name from search.html
		track_name = request.form['Track'] #request Track name from search.html
		searched_features = misc_functions.output(Artist = artist_name, Track = track_name) #generate uri for searched song
		return(render_template('test.html', searched_features = searched_features))
	html = render_template('search.html')
	return(html)

@app.route('/test', methods=('GET', 'POST'))
#def get_features():
#	v = request.values.get('Artist', 'Track')
#	return(v)
def test():
	if request.method == 'POST':
		return(redirect(test.html))

	return(render_template(search.html))

if __name__ == '__main__':
	app.run(host='127.0.0.1',port=8080,debug=True) #run app