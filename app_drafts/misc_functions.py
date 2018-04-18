import spotipy
import spotipy.oauth2
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import numpy as np
import pygal
from pygal.maps.world import World #if this doesn't work run pip install pygal_maps_world

import os
from json.decoder import JSONDecodeError

from flask import render_template, Flask, request, send_file

	
'----- OUTPUT OF SEARCH PORTION BEGINS -----'
#SEARCH_ENDPOINT = 'https://api.spotify.com/v1/search'

#@app.route('/output/<Artist><Track>', methods = ('GET', 'POST')) #output map at the end? RECEIVES DATA FROM homepage.html
def generate_df(sp_feature_dict):
	df = pd.DataFrame.from_dict(sp_feature_dict) #convert dict to pandas table

	df = df.loc[:,['acousticness', 'danceability', 'duration_ms', 'energy', 'instrumentalness', 'key', 'liveness', 'loudness', 'mode', 'speechiness', 'tempo', 'valence']] #clean up table (extract columns we need)
	return(df)

def search_spotify(Artist, Track):
	
	'----- Grab authentication -----'
	CLIENT_ID = '23888f5deee6452db5d78bd2d1091da5'
	CLIENT_SECRET = 'f6ecea7a89d24b02b2c969745b88a9db'

	client_credentials_manager = SpotifyClientCredentials(CLIENT_ID, CLIENT_SECRET)
	sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

	q = 'artist:{} track:{}'.format(Artist, Track) #get artist_name and track_name from html 
	results = sp.search(q, type='track')
	#print('aaaaaa') used for debugging purposes
	#print(results)
	return(results)

def output_album_image(Artist, Track):
	results = search_spotify(Artist, Track)
	album_cover_url = results['tracks']['items'][0]['album']['images'][1]['url'] #album cover image url
	return(album_cover_url)

def output_map(Artist, Track):

	results = search_spotify(Artist, Track)

	#except IndexError:
	#	print('This song does not exist') #consider sending user to a does not exist page we need to make an exception case
	
	CLIENT_ID = '23888f5deee6452db5d78bd2d1091da5'
	CLIENT_SECRET = 'f6ecea7a89d24b02b2c969745b88a9db'

	client_credentials_manager = SpotifyClientCredentials(CLIENT_ID, CLIENT_SECRET)
	sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

	track_uri = results['tracks']['items'][0]['uri'] #nested dict: get tracks, items of tracks, 1st item, and then uri of the 1st item
	artist_uri = results['tracks']['items'][0]['artists'][0]['uri'] #gets artist info, needed to grab the genre

	#except IndexError:
	#	print('This song does not exist') #consider sending user to a does not exist page we need to make an exception case
	
	track_popularity = results['tracks']['items'][0]['popularity'] #get popularity of track
	track_genre = sp.artist(artist_uri)['genres'] #get genre of artist
	track_name = results['tracks']['items'][0]['name'] #get name of track

	track_popularity = results['tracks']['items'][0]['popularity'] #get popularity of track
	track_genre = sp.artist(artist_uri)['genres'] #get genre of artist
	track_name = results['tracks']['items'][0]['name'] #get name of track


	if not track_genre:
		track_genre = 'Unknown'
	else:
		track_genre = track_genre[0] #to prevent index error for genre selection

	track_features = sp.audio_features(track_uri) #grab dict of audio features
	new_track_df = generate_df(track_features) #now have pandas df with relevant columns, this will be used for output

	new_track_df['popularity'] = track_popularity
	new_track_df['genre'] = track_genre
	new_track_df['song'] = track_name

	"Following part to produce map"
	world = pd.read_csv('data.csv')
	w_no_na = world.dropna()
	region_names = list(set(w_no_na.Region))
	region_dict = {} #consider making a cached version of this dictionary to expedite process?
	
	for i in range(0, len(region_names)):
		region_dict[region_names[i]] = np.random.randint(low=0, high=5) #this is for example output

	worldmap_chart = World()
	worldmap_chart.title = 'testing world map'
	worldmap_chart.add('this is a test label', region_dict)
	map_output = worldmap_chart.render_data_uri()



	print('BLAJDSDKSDK KSDKSDL dskdskds ``` ~~~~~') #for debugging purposes

	#return(new_track_df) #new_track_df is the fully cleaned dataframe
	return(map_output)
"TO DO: CALL ML MODEL ON TRACK_FEATURES. THIS INCLUDES: GENERATING COLUMNS FOR TOP ALL TIME, TOP 100, etc FOR EACH COUNTRY"
"ALSO: NEED TO GENERATE MAPS AFTER PREDICTIONS FROM ML MODEL, CONSIDER SEPARATE HTML PAGE?"

'----- FINISHED OUTPUT PORTION -----'