import spotipy
import spotipy.oauth2
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import numpy as np
import os
from json.decoder import JSONDecodeError
import pygal
from pygal.maps.world import World #if this doesn't work run pip install pygal_maps_world

from flask import render_template, Flask, request, send_file

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
		searched_features = misc_functions.output_map(Artist = artist_name, Track = track_name) 
		album_image = misc_functions.output_album_image(Artist = artist_name, Track = track_name)
		return(render_template('charts.html', chart = searched_features, album_image = album_image, artist_name = artist_name, track_name = track_name))
	html = render_template('search.html')
	return(html)

@app.route('/charts', methods=('GET', 'POST'))

def image():
	if request.method == 'POST':
		album_image = misc_functions.output_album_image(Artist = artist_name, Track = track_name)
		return(render_template('charts.html', album_image = album_image))

if __name__ == '__main__':
	app.run(host='127.0.0.1',port=8080,debug=True) #run app