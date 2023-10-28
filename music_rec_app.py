# Import libraries
import streamlit as st
st.set_page_config(page_title="Song Recommendation", layout="wide")

import pandas as pd
from sklearn.neighbors import NearestNeighbors
import streamlit.components.v1 as components

# Define function to load & expand data so that each row contains 1 genre of each track
@st.cache_data()
def load_data():
    df = pd.read_csv("data/filtered_track_df.csv")
    df['genres'] = df.genres.apply(lambda x: [i[1:-1] for i in str(x)[1:-1].split(", ")])
    exploded_track_df = df.explode("genres")
    return exploded_track_df

# Define list of genres and audio features of songs for audience to choose from
genre_names = ['Dance Pop', 'Electronic', 'Electropop', 'Hip Hop', 'Jazz', 'K-pop', 'Latin', 
               'Pop', 'Pop Rap', 'R&B', 'Rock']
audio_feats = ["acousticness", "danceability", "energy", "instrumentalness", "valence", "tempo"]

# Load data
exploded_track_df = load_data()

                           #############################################
                           
## Build KNN model to retrieve top songs that are 
## closest in distance with the set of feature inputs selected by users


# Define function to return Spotify URIs and audio feature values of top neighbors (ascending)
def n_neighbors_uri_audio(genre, start_year, end_year, test_feat):
    genre = genre.lower()
    genre_data = exploded_track_df[(exploded_track_df["genres"]==genre) & (exploded_track_df["release_year"]>=start_year) & (exploded_track_df["release_year"]<=end_year)]
    genre_data = genre_data.sort_values(by='popularity', ascending=False)[:500] # use only top 500 most popular songs
    
    neigh = NearestNeighbors()
    neigh.fit(genre_data[audio_feats].to_numpy())
    
    n_neighbors = neigh.kneighbors([test_feat], n_neighbors=len(genre_data), return_distance=False)[0]
    
    uris = genre_data.iloc[n_neighbors]["uri"].tolist()
    audios = genre_data.iloc[n_neighbors][audio_feats].to_numpy()
    return uris, audios


                           #############################################

## Build frontend app layout - a dashboard that allows users to customize songs they want to listen to

# Design dashboard layout with customizeable sliders

def main():
    st.title("Personalized Song Recommendations")
    
    st.sidebar.title("Music Recommender App")
    st.sidebar.header("Welcome!")
    st.sidebar.markdown("Discover your soon-to-be favorite songs by selecting genres and audio features.")
    st.sidebar.markdown("Tips: Play around with different settings and listen to song previews to test the system!")
    
    
    # Add buttons to the sidebar
    if st.sidebar.button("Check out my other projects"):
        st.sidebar.markdown("[https://hahoangpro.wixsite.com/datascience]")
    if st.sidebar.button("Connect with me on LinkedIn"):
        st.sidebar.markdown("[https://www.linkedin.com/in/ha-hoang-86a80814a/]")
   
    
    
    with st.container():
        col1, col2, col3, col4 = st.columns((2,0.5,1,0.5))
        with col3:
            st.markdown("***Select genre:***")
            genre = st.radio(
                "",
                genre_names, index=genre_names.index("Pop"))
        with col1:
            st.markdown("***Select features to customize:***")
            start_year, end_year = st.slider('Select year range', 1990, 2019, (2015, 2019))
            acousticness = st.slider('Acousticness', 0.0, 1.0, 0.5)
            danceability = st.slider('Danceability', 0.0, 1.0, 0.5)
            energy = st.slider('Energy', 0.0, 1.0, 0.5)
            valence = st.slider('Positiveness (Valence)', 0.0, 1.0, 0.45)
            instrumentalness = st.slider('Instrumentalness', 0.0, 1.0, 0.0)
            tempo = st.slider('Tempo', 0.0, 244.0, 118.0)
    
    ## Display 6 top songs (closest neighbors) to recommend based on selected features
    tracks_per_page = 6
    test_feat = [acousticness, danceability, energy, instrumentalness, valence, tempo]
    uris, audios = n_neighbors_uri_audio(genre, start_year, end_year, test_feat)
    
    # Use Spotify Developer Widget to display iframe with classic HTML
    tracks = []
    for uri in uris:
        track = """<iframe src="https://open.spotify.com/embed/track/{}" width="260" height="380" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>""".format(uri)
        tracks.append(track) 
        

    # Add "Recommend More Songs" button to have more options
    
    ## Use Streamlit's session_state to check if users alter any inputs between sessions
    ## If users alter any inputs, the recommendation starts from the 1st track of top 'neighbors'
    ## If users continue to press "Recommend More Songs" without changing inputs, the top neighbors 
    ## will be traversed till the end of the top neighbors list

    current_inputs = [genre, start_year, end_year] + test_feat
    
    try: 
        previous_inputs = st.session_state['previous_inputs']
    except KeyError:
        previous_inputs = None
        
    if current_inputs != previous_inputs:
        st.session_state['start_track_i'] = 0
        st.session_state['previous_inputs'] = current_inputs
    
    
    
    ## Design layout of the "Recommend More Songs" button    
    
    # Initialize start_track_i if not present in session state
    if 'start_track_i' not in st.session_state:
        st.session_state['start_track_i'] = 0
        st.write("start_track_i initialized:", st.session_state['start_track_i'])

    # Add "Recommend More Songs" button
    if st.button("Recommend More Songs"):
        if st.session_state['start_track_i'] < len(tracks):
            st.session_state['start_track_i'] += tracks_per_page  # Show 6 more songs
            

    with st.container():
        col1, col2, col3 = st.columns(3)  # Create 3 columns for a 3x3 grid

    current_tracks = tracks[st.session_state['start_track_i']: st.session_state['start_track_i'] + tracks_per_page]
    current_audios = audios[st.session_state['start_track_i']: st.session_state['start_track_i'] + tracks_per_page]

    for i, (track, audio) in enumerate(zip(current_tracks, current_audios)):
        if i % 3 == 0:
            with col1:
                components.html(
                    track, 
                    height=400, 
                )
        elif i % 3 == 1:
            with col2:
                components.html(
                    track,
                    height=400,
                )
        else:
            with col3:
                components.html(
                    track,
                    height=400,
                )

    if st.session_state['start_track_i'] >= len(tracks):
        st.write("No more songs to recommend")
        
            
if __name__ == "__main__":
    main()

# Note: Install streamlit by typing in the command line "conda install -c conda-forge streamlit" to install latest version
# Test if streamlit is operable by typing "streamlit hello" 

