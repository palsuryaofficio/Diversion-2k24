from flask import Flask, render_template, request, redirect, url_for, jsonify ,session
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import json
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

import cv2
import dlib

app = Flask(__name__, template_folder='templates', static_folder='static')
def detect_emotion(image_path):
    # Load the image using OpenCV
    image = cv2.imread(image_path)

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Use the dlib library for face detection
    detector = dlib.get_frontal_face_detector()
    faces = detector(gray)

    # Check if any faces are found
    if faces:
        # Use your logic for face recognition (you can add your logic here)
        # For simplicity, let's just return the number of faces found
        return {'num_faces': len(faces)}
    else:
        return {'error': 'No faces found in the image'}


app = Flask(__name__, template_folder='templates', static_folder='static')

# Spotify API credentials
SPOTIPY_CLIENT_ID = '55f614b2c700475aac20e12d4a149d33'
SPOTIPY_CLIENT_SECRET = '4dd3a5b009564d25ac8a2464b59f557d'
SPOTIPY_REDIRECT_URI = 'http://127.0.0.1:8888'

USER_DATA_FILE = 'user_data.json'
# Set up Spotify authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope='user-library-read user-top-read'))

def analyze_sentiment(text):
    analyzer = SentimentIntensityAnalyzer()
    sentiment_score = analyzer.polarity_scores(text)['compound']
    return sentiment_score

def save_user_data(username, password):
    if not os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'w') as f:
            json.dump({}, f)
    with open(USER_DATA_FILE, 'r') as f:
        users = json.load(f)

    users[username] = {'password': password}

    with open(USER_DATA_FILE, 'w') as f:
        json.dump(users, f)

def authenticate_user(username, password):
    with open(USER_DATA_FILE, 'r') as f:
        users = json.load(f)

    if username in users and users[username]['password'] == password:
        return True
    else:
        return False

def get_recommendations(sentiment_score, genres):
    if sentiment_score > 0.1:
        genres.extend(['happy', 'remix', 'world', 'indian', 'english'])
    elif sentiment_score < -0.1:
        genres.extend(['sad', 'remix', 'world', 'indian', 'english'])
    else:
        genres.extend(['pop', 'remix', 'world', 'indian', 'english'])

    recommendations = sp.recommendations(seed_genres=genres, limit=5)

    for track in recommendations['tracks']:
        audio_features = sp.audio_features(track['id'])
        if audio_features:
            track['audio_features'] = {
                'danceability': audio_features[0]['danceability'],
                'energy': audio_features[0]['energy'],
                'tempo': audio_features[0]['tempo']
            }
        else:
            track['audio_features'] = None

    return recommendations

def get_user_top_tracks():
    top_tracks = sp.current_user_top_tracks(limit=5, time_range='short_term')
    return top_tracks

def generate_ai_message(danceability, energy):
    if danceability > 0.7:
        return "Get ready to hit the dance floor!"
    elif energy < 0.3:
        return "Relax and enjoy the soothing vibes."
    else:
        return "Feel the rhythm and enjoy the music!"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/emotion_recognition', methods=['POST'])
def emotion_recognition():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file:
        file_path = 'static/uploads/' + file.filename
        file.save(file_path)
        result = detect_emotion(file_path)
        return jsonify(result)

@app.route('/recommend', methods=['POST'])
def recommend():
    user_input = request.form['user_input']
    sentiment_score = analyze_sentiment(user_input)

    recommended_genres = []
    recommendations = get_recommendations(sentiment_score, recommended_genres)

    user_top_tracks = get_user_top_tracks()
    sentiment_message = generate_ai_message(sentiment_score, 0.0)

    return render_template('recomendations.html', sentiment_score=sentiment_score, recommendations=recommendations['tracks'], user_top_tracks=user_top_tracks['items'], sentiment_message=sentiment_message)

@app.route('/get_time_of_day_recommendations', methods=['GET'])
def get_time_of_day_recommendations():
    # Your logic to get recommendations based on the time of day
    # For simplicity, let's return hardcoded recommendations
    recommendations = ['Morning Song', 'Afternoon Jam', 'Evening Chill']
    return jsonify({'recommendations': recommendations})

# Endpoint for inviting friends and updating collaborative playlist
@app.route('/invite_friends', methods=['GET'])
def invite_friends():
    # Your logic to invite friends and update the collaborative playlist
    # For simplicity, let's return hardcoded playlist information
    playlist_info = {'playlist_name': 'My Collaborative Playlist', 'contributors': ['Friend 1', 'Friend 2']}
    return jsonify(playlist_info)


@app.route('/search', methods=['POST'])
def search():
    search_query = request.form['search_query']
    search_results = sp.search(q=search_query, type='track', limit=5)

    return render_template('search_results.html', search_results=search_results['tracks']['items'])

@app.route('/ai_recommendation/<track_id>', methods=['GET'])
def ai_recommendation_route(track_id):
    audio_features = sp.audio_features(track_id)

    if audio_features:
        danceability = audio_features[0]['danceability']
        energy = audio_features[0]['energy']

        if danceability > 0.7 and energy > 0.7:
            return "This track is energetic and great for parties!"
        elif danceability < 0.5 and energy < 0.5:
            return "This track has a chill vibe, perfect for relaxing."
        else:
            return "This track has a balanced energy level."
    else:
        return "Audio features not available for the track."


@app.route('/get_location_recommendations')
def get_location_recommendations():
    # Simulate getting user location (replace this with actual geolocation logic)
    user_location = 'WestBengal'

    if user_location in location_recommendations:
        recommendations = location_recommendations[user_location]
    else:
        recommendations = location_recommendations['Other']

    return jsonify({'recommendations': recommendations})


@app.route('/get_location', methods=['POST'])
def get_location():
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')

    # Example: Determine the user's location based on coordinates
    user_location = determine_location(float(latitude), float(longitude))

    # Adjust your music recommendation logic based on the user's location
    # ...

    return jsonify({'location': user_location})


# Example function to determine location (customize based on your needs)
def determine_location(latitude, longitude):
    if 21.5721 <= latitude <= 27.0996 and 85.9870 <= longitude <= 89.8761:
        return 'West Bengal'
    else:
        return 'Other'

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        save_user_data(username, password)
        return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if authenticate_user(username, password):
            return redirect(url_for('landing_page'))
        return redirect(url_for('index'))

@app.route('/landing_page')
def landing_page():
    return render_template('landing_page.html')


location_recommendations = {
    'WestBengal': ['Bengali Song 1', 'Bengali Song 2', 'Hindi Song 1', 'Hindi Song 2'],
    'Other': ['English Song 1', 'English Song 2', 'Other Language Song 1', 'Other Language Song 2']
}


def index():
    return render_template('index.html')





def generate_personalized_recommendations():
    user_top_tracks = get_user_top_tracks()

    audio_features_list = []
    for track in user_top_tracks['items']:
        audio_features = sp.audio_features(track['id'])
        if audio_features:
            audio_features_list.append({
                'track_name': track['name'],
                'artist_name': track['artists'][0]['name'],
                'audio_features': {
                    'danceability': audio_features[0]['danceability'],
                    'energy': audio_features[0]['energy'],
                    'tempo': audio_features[0]['tempo']
                }
            })

    personalized_recommendations = []
    for audio_features in audio_features_list:
        recommendations = sp.recommendations(
            seed_tracks=[audio_features['track_name']],
            limit=2
        )
        personalized_recommendations.extend(recommendations['tracks'])

    return personalized_recommendations

@app.route('/personalized_recommendations')
def personalized_recommendations():
    recommendations = generate_personalized_recommendations()
    return render_template('personalized_recommendations.html', recommendations=recommendations)


@app.route('/get_updated_playlist', methods=['GET'])
def get_updated_playlist():
    # Implement your logic to provide the updated playlist
    # This could involve fetching data from a database or another source
    updated_playlist = [
        {'song_name': 'Updated Song 1', 'artist_name': 'Updated Artist 1'},
        {'song_name': 'Updated Song 2', 'artist_name': 'Updated Artist 2'},
        # ... (add more songs as needed)
    ]
    return jsonify({'playlist': updated_playlist})





if __name__ == '__main__':
    app.run(debug=True, port=8888)
