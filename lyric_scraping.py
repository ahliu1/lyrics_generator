import time
import lyricsgenius
from access_token import * # Please note that you need your own Genius Access Token to run this code.

genius = lyricsgenius.Genius(client_access_token, timeout=15)

def is_original_version(song_title):
    """
    Helper function that omits songs with these keywords in the song title. Removes duplicates and interviews scraped from Genius.
    
    Examples: song_title = "I Knew You Were Trouble" -> True,
    song_title = "I Knew You Were Trouble (Remix)" -> False
    
    Parameters
    ----------
    song_title: 
        String, title of the song.
    
    Returns
    -------
    Bool
       True if original, false if not.
    """
    keywords = ['remix', 'version', 'demo', 'cover', 'mix', 'edit', 'live', 'feat', 'ft', 'acoustic', 'Artist Archive', '-20grad', 'Setlist',
               'Dates', 'Outfits', 'Live', 'Mash Up', 'Speech', '30 Things I Learned', 'Breakdown', 'Speeches', 'Commentary', 'Remix', 
               'Interview', 'Behind the Song', 'Mixed', 'Notes', 'Cover', 'Note', 'Acoustic', 'thank', 'quotes', 'Mash']
    return not any(keyword.lower() in song_title.lower() for keyword in keywords)

def get_all_songs_and_lyrics(artist_name, total_songs, retries=3, delay=5):
    """
    Scrapes # (total_songs) songs and lyrics of artist (artist_name) from Genius using LyricsGenius. 
    Successfully avoids scraping warnings with retries and delays.
    
    Parameters
    ----------
    artist_name: 
        String, name of the artist, i.e. "Troye Sivan"
    
    total_songs:
        int, number of songs to retrieve
    
    Returns
    -------
    List of tuples: 
        [(song, lyrics), (song, lyrics), ...]
        i.e.: [("Fools", "I am tired of this place, ..."), ("Youth", "What if, what if...")]
    """
    artist = genius.search_artist(artist_name, max_songs=0)  # Initialize the artist object 
    song_titles = {}  # To keep track of unique song titles
    songs_with_lyrics = [] # initializes return object

    songs_fetched = 0
    page = 1

    while songs_fetched < total_songs:
        # Retries until an exception is thrown
        for attempt in range(retries):
            try:
                # fetch songs in batches of 20
                response = genius.artist_songs(artist.id, per_page=20, page=page)
                if 'songs' in response: # check if response has songs key
                    for song in response['songs']:
                        if len(song_titles) >= total_songs: # differentiates # songs being explored and # songs being retrieved b/c dupes are excluded
                            break
                        title = song['title']
                        original_title = title.split('(')[0].strip()  # Extract the base title without version info
                        if is_original_version(title) and original_title not in song_titles: # checks for original version status
                            # Fetch song details to get lyrics
                            song_details = genius.song(song['id'])
                            if 'lyrics' in song_details:
                                song_lyrics = song_details['lyrics']
                            else:
                                song_lyrics = genius.lyrics(song_url=song['url'])
                            songs_with_lyrics.append((title, song_lyrics))
                            song_titles[original_title] = title
                            songs_fetched += 1
                page += 1
                break  # Break out of the retry loop on success
            # to avoid this exception, make sure that your total_songs don't exceed the number of original songs the artist has! (try half of the artists' count on Genius to be safe)
            except (lyricsgenius.GeniusAPIError, TimeoutError) as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    time.sleep(delay)  # Wait before retrying
                else:
                    raise  # Raise the exception if all retries fail

    return songs_with_lyrics

def add_song(artist_name, total_songs):
    """
    Makes new local file and adds all song lyrics.
    
    Parameters
    ----------
    artist_name: 
        String, name of the artist, i.e. "Troye Sivan"
    
    total_songs:
        int, number of songs to retrieve
    
    Returns
    -------
    filename:
        String, name of the file (for easy access)
    artist_name:
        String, name of the artist (for easy access)
    """
    filename = artist_name.lower().replace(" ", "") + "_lyrics.txt"
    print(filename)
    songs_with_lyrics = get_all_songs_and_lyrics(artist_name, total_songs)
    with open(filename, 'w', encoding='utf-8') as file:
        for title, lyrics in songs_with_lyrics:
            print(title)
            file.write(f"Title: {title}\n\nLyrics:\n{lyrics}\n\n\n")
    return filename, artist_name