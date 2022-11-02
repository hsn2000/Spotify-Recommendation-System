from flask import Flask,request, url_for, redirect, render_template, jsonify
import pandas as pd
import pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
application = Flask(__name__)

data = pd.read_csv("Final_Data1.csv")
orignal_data = pd.read_csv("Data_with_Features.csv")
summarized_playlists_data = pd.read_csv("Summarized_playlists_Data.csv")

unique_tracks = data['track_uri'].unique()
def get_song_recommendations(orig_data,playlists_vector,playlist_id,num_of_recommendations):
  playlists_tracks = orig_data[orig_data['pid'] == playlist_id]['track_uri'].unique()
  tracks_not_in_playlist = set(unique_tracks) - set(playlists_tracks)
  non_playlist_df = orig_data[orig_data['track_uri'].isin(tracks_not_in_playlist)]
  non_playlist_df.drop_duplicates(subset=['track_uri'],inplace=True)
  non_playlist_df['sim'] = cosine_similarity(non_playlist_df.drop(columns=['pid','track_uri']).values, playlists_vector[playlists_vector['pid']==playlist_id].drop(columns=['pid']).values)[:,0]
  non_playlist_df = non_playlist_df.sort_values('sim',ascending = False).head(num_of_recommendations)
  return non_playlist_df['track_uri']

def song_names_to_append_to_playlist(data,summarized_playlists_df,playlist_id,num_of_recommendations):
  recommended_track_uri = get_song_recommendations(data,summarized_playlists_df,playlist_id,num_of_recommendations)
  track_names = orignal_data[orignal_data['track_uri'].isin(recommended_track_uri.values)]['track_name'].unique()
  artist_names = orignal_data[orignal_data['track_uri'].isin(recommended_track_uri.values)]['artist_name'].unique()
  album_names = orignal_data[orignal_data['track_uri'].isin(recommended_track_uri.values)]['album_name'].unique()
  songs = [('"'+song+ '",   by   "' +artist+ '",    Album Name: "' +album+'"') for song,artist,album in zip(track_names,artist_names,album_names)]
  return songs

@application.route('/')
def home():
    return render_template('index.html')

@application.route('/predict',methods=['POST'])
def predict():
    values = [x for x in request.form.values()]
    playlistID = values[0]
    numSongs = values[1]
    songs = song_names_to_append_to_playlist(data,summarized_playlists_data,int(playlistID),int(numSongs))
    return render_template('results.html',pred=songs)

if __name__ == '__main__':
    application.run(debug=True)