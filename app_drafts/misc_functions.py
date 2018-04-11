import spotipy
import spotipy.oauth2
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import numpy as np

import os
from json.decoder import JSONDecodeError

from flask import render_template, Flask, request

	
'----- OUTPUT OF SEARCH PORTION BEGINS -----'
#SEARCH_ENDPOINT = 'https://api.spotify.com/v1/search'

#@app.route('/output/<Artist><Track>', methods = ('GET', 'POST')) #output map at the end? RECEIVES DATA FROM homepage.html
def generate_df(sp_feature_dict):
	df = pd.DataFrame.from_dict(sp_feature_dict) #convert dict to pandas table

	df = df.loc[:,['acousticness', 'danceability', 'duration_ms', 'energy', 'instrumentalness', 'key', 'liveness', 'loudness', 'mode', 'speechiness', 'tempo', 'valence']] #clean up table (extract columns we need)
	return(df)

def output(Artist, Track):

	'----- Grab authentication -----'
	CLIENT_ID = '23888f5deee6452db5d78bd2d1091da5'
	CLIENT_SECRET = 'f6ecea7a89d24b02b2c969745b88a9db'

	client_credentials_manager = SpotifyClientCredentials(CLIENT_ID, CLIENT_SECRET)
	sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

	q = 'artist:{} track:{}'.format(Artist, Track) #get artist_name and track_name from html 
	results = sp.search(q, type='track')
	#print('aaaaaa') used for debugging purposes
	#print(results)
	track_uri = results['tracks']['items'][0]['uri'] #nested dict: get tracks, items of tracks, 1st item, and then uri of the 1st item
	artist_uri = results['tracks']['items'][0]['artists'][0]['uri'] #gets artist info, needed to grab the genre

	#except IndexError:
	#	print('This song does not exist') #consider sending user to a does not exist page we need to make an exception case
	
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

	world = pd.read_csv('data.csv')
	w_no_na = world.dropna()
	region_names = list(set(w_no_na.Region))
	region_dict = {} #consider making a cached version of this dictionary to expedite process?
	
	for i in range(0, len(region_names)):
		relevant_data = w_no_na[w_no_na.Region == region_names[i]] #subset data where region == relevant region
		relevant_artists = list(set(relevant_data['Track Name'])) #set of artists for region
		region_dict[region_names[i]] = relevant_artists #populate dictionaries
	
	for i in list(region_dict.keys()):
		new_track_df[i] = new_track_df.song.isin(list(region_dict[i])) #makes the columns of each country

	for i in list(region_dict.keys()):
		new_col = i + '_top' #each country now has column to state if song was ever the top ranked song in that country
		col_values = []
		pos_1_ever = set(world[(world['Position'] == 1) & (world['Region'] == i)]['Track Name']) # 'i' is region 
		
		for j in range(0, len(new_track_df)):
			if new_track_df.song[j] in pos_1_ever:
				col_values.append(True)
			else:
				col_values.append(False)
		new_track_df[new_col] = col_values

	for i in list(region_dict.keys()):
		new_col = i + '_100' #each country now has column to state if song was 100 days popular in that country
		col_values = []
		ever_show = set(world[world['Region'] == i]['Track Name'])
		song_frequencies = world[world['Region'] == i]['Track Name'].value_counts() #get frequencies of each song in this region
		days_100 = set(song_frequencies[song_frequencies > 100].index) # 'i' is region, get all songs >= 100 frequencies 

		for j in range(0, len(new_track_df)):
			if new_track_df.song[j] not in ever_show:
				col_values.append(False) #it looks redundant now, was using for testing
			elif copy2.song[j] in days_100:
				col_values.append(True)
			else:
				col_values.append(False)
		new_track_df[new_col] = col_values

	print('BLAJDSDKSDK KSDKSDL dskdskds ``` ~~~~~') #for debugging purposes
	print(new_track_df.columns[0:len(new_track_df.columns)])

	return(new_track_df) #new_track_df is the fully cleaned dataframe
"TO DO: CALL ML MODEL ON TRACK_FEATURES. THIS INCLUDES: GENERATING COLUMNS FOR TOP ALL TIME, TOP 100, etc FOR EACH COUNTRY"
"ALSO: NEED TO GENERATE MAPS AFTER PREDICTIONS FROM ML MODEL, CONSIDER SEPARATE HTML PAGE?"

'----- FINISHED OUTPUT PORTION -----'