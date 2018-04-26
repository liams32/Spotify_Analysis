import numpy as np
import pandas as pd 
import spotipy
import spotipy.oauth2
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
import statistics
from scipy.stats import kurtosis
from scipy.stats import skew

from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_curve, auc
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import normalize
from sklearn.externals import joblib

import pygal
from pygal.maps.world import World #if this doesn't work run pip install pygal_maps_world

import os
from json.decoder import JSONDecodeError

from flask import render_template, Flask, request, send_file

	
'----- OUTPUT OF SEARCH PORTION BEGINS -----'
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
	###funcs for features later
	def f_mean(row):
		return(np.mean(row))
	def f_median(row):
		return(np.median(row))
	def f_std(row):
		return(np.std(row))
	def f_min(row):
		return(np.min(row))
	def f_max(row):
		return(np.max(row))
	def f_80Percentile(row):
		return(np.percentile(row, 80))
	def f_kurtosis(row):
		return(kurtosis(row))
	def f_skew(row):
		return(skew(row))
	
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
	
	#track_popularity = results['tracks']['items'][0]['popularity'] #get popularity of track
	track_genre = sp.artist(artist_uri)['genres'] #get genre of artist
	track_name = results['tracks']['items'][0]['name'] #get name of track

	if not track_genre:
		track_genre = 'Unknown'
	else:
		track_genre = track_genre[0] #to prevent index error for genre selection

	track_features = sp.audio_features(track_uri) #grab dict of audio features
	new_track_df = generate_df(track_features) #now have pandas df with relevant columns, this will be used for output

	#new_track_df['popularity'] = track_popularity
	new_track_df['genre'] = track_genre
	new_track_df['song'] = track_name
	new_track_df['uri'] = track_uri

	"Following part to produce map"
	timbre_features = ['timbre_all_1', 'timbre_all_2', 'timbre_all_3', 'timbre_all_4', 'timbre_all_5', 'timbre_all_6', 'timbre_all_7', 'timbre_all_8', 'timbre_all_9', 'timbre_all_10', 'timbre_all_11', 'timbre_all_12']

	timbre_all_df = pd.DataFrame(index = range(len(new_track_df)), columns = timbre_features)

	curr_uri = new_track_df['uri'][0]
	curr_song = sp.audio_analysis(curr_uri)
	curr_segments = curr_song['segments'] #get into segments (time intervals). Each song diff length

	init_timbres_all = [[] for _ in range(12)] #initialize 12 lists for median (find median each list)

	for j in range(0, len(curr_segments)):
		curr_timbres_list = curr_segments[j]['timbre'] #grab timbres as list
		init_timbres_all[0].append(curr_timbres_list[0])
		init_timbres_all[1].append(curr_timbres_list[1])
		init_timbres_all[2].append(curr_timbres_list[2])
		init_timbres_all[3].append(curr_timbres_list[3])
		init_timbres_all[4].append(curr_timbres_list[4])
		init_timbres_all[5].append(curr_timbres_list[5])
		init_timbres_all[6].append(curr_timbres_list[6])
		init_timbres_all[7].append(curr_timbres_list[7])
		init_timbres_all[8].append(curr_timbres_list[8])
		init_timbres_all[9].append(curr_timbres_list[9])
		init_timbres_all[10].append(curr_timbres_list[10])
		init_timbres_all[11].append(curr_timbres_list[11])

	timbre_all_df['timbre_all_1'][0] = init_timbres_all[0]
	timbre_all_df['timbre_all_2'][0] = init_timbres_all[1]
	timbre_all_df['timbre_all_3'][0] = init_timbres_all[2]
	timbre_all_df['timbre_all_4'][0] = init_timbres_all[3]
	timbre_all_df['timbre_all_5'][0] = init_timbres_all[4]
	timbre_all_df['timbre_all_6'][0] = init_timbres_all[5]
	timbre_all_df['timbre_all_7'][0] = init_timbres_all[6]
	timbre_all_df['timbre_all_8'][0] = init_timbres_all[7]
	timbre_all_df['timbre_all_9'][0] = init_timbres_all[8]
	timbre_all_df['timbre_all_10'][0] = init_timbres_all[9]
	timbre_all_df['timbre_all_11'][0] = init_timbres_all[10]
	timbre_all_df['timbre_all_12'][0] = init_timbres_all[11]

	new_track_df = pd.concat([new_track_df, timbre_all_df], axis=1)
	j = 0
	for i in range(15, len(new_track_df.columns)):
		current_column  = new_track_df.iloc[:,i]
		new_track_df['mean_timbre{}'.format(j+1)] = current_column.apply(f_mean)
		new_track_df['median_timbre{}'.format(j+1)] = current_column.apply(f_median)
		new_track_df['std_timbre{}'.format(j+1)] = current_column.apply(f_std)
		new_track_df['min_timbre{}'.format(j+1)] = current_column.apply(f_min)
		new_track_df['max_timbre{}'.format(j+1)] = current_column.apply(f_max)
		new_track_df['range_timbre{}'.format(j+1)] = new_track_df['max_timbre{}'.format(j+1)]-new_track_df['min_timbre{}'.format(j+1)]
		new_track_df['80Percentile_timbre{}'.format(j+1)] = current_column.apply(f_80Percentile)
		new_track_df['kurtosis_timbre{}'.format(j+1)] = current_column.apply(f_kurtosis)
		new_track_df['skewness_timbre{}'.format(j+1)] = current_column.apply(f_skew)
		j += 1
	local_output = ['ee', 'br', 'my', 'cz', 'pe', 'gb', 'ie', 'se', 'sk', 'co', 'sg', 'ec', 'es', 'no', 'dk', 'be', 'lu', 'do', 'nz', 'de', 'hu', 'cr', 'jp', 'hk', 'lt', 'pl','it', 'hn', 'mx', 'ph', 'cl', 'is', 'ca', 'ar', 'at', 'ch', 'tr', 'py', 'tw', 'gt', 'sv', 'us', 'fr', 'global', 'nl', 'bo', 'lv', 'gr', 'pa', 'uy', 'au', 'pt', 'fi']

	model_list = []
	for i in local_output:
		model_list.append(joblib.load('{}_model.pkl'.format(i)))

	new_track_df = new_track_df[new_track_df.columns.difference(['timbre_all_1', 'timbre_all_2', 'timbre_all_3', 'timbre_all_4', 'timbre_all_5', 'timbre_all_6', 'timbre_all_7', 'timbre_all_8', 'timbre_all_9', 'timbre_all_10', 'timbre_all_11', 'timbre_all_12', 'song', 'uri', 'genre'])]
	X_norm = normalize(new_track_df)
	region_dict = {}
	for i in range(0, len(local_output)):
		curr_country = local_output[i]
		curr_model = model_list[i]
		region_dict[curr_country] = curr_model.predict(X_norm)[0]

	worldmap_chart = World()
	worldmap_chart.title = 'testing world map'
	worldmap_chart.add('regions', region_dict)
	del region_dict['global'] 
	map_output = worldmap_chart.render_data_uri()

	return(map_output)
"TO DO: CALL ML MODEL ON TRACK_FEATURES. THIS INCLUDES: GENERATING COLUMNS FOR TOP ALL TIME, TOP 100, etc FOR EACH COUNTRY"
"ALSO: NEED TO GENERATE MAPS AFTER PREDICTIONS FROM ML MODEL, CONSIDER SEPARATE HTML PAGE?"

'----- FINISHED OUTPUT PORTION -----'