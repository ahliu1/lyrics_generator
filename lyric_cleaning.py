from lyric_scraping import *
import re

def is_russian_character(char):
    """ Helper function to help us get rid of Russian characters. (A lot of Russian song covers for some reason)

    Parameters
    -----------
    char : char

    Returns
    -------
    Bool:
        True: if char is Cyrillic letter
        False: if char is not

    """
    return 'А' <= char <= 'я' or char == 'ё' or char == 'Ё'
    
def clean_data(filename, artist_name):
    """ Takes in filename from lyric_scraping.add_song and cleans the lyric data for cleaner model training. 
    Parameters
    -----------
    filename: str
        Filename, 0th index of lyric_scraping.add_song return value
    
    artist_name: str
        Artist name, 1st index of lyric_scraping.add_song return value

    Returns
    -------
    Bool:
    """
    #with open(filename, "r") as f:
    with open(filename, "r", encoding="UTF-8", errors="ignore") as f:
        file = f.read()
    # Unnecessary Filler Words
    #removal = [artist_name, "Instrumental", " x ", " pt. ", " pt ", "1", "2", "3", "4", "5", "6", "7", "8", "9", "Spotify", "Pre-Chorus", "Post-Chorus", "Variation", "Title: ", "Verse", "Chorus", "Bridge", "Outro", "Intro", "[ ]", "[]", "[", "]", ":", "Lyrics"] + artist_name.split(" ")
    removal = [artist_name.lower(), "instrumental", " x ", " pt. ", " pt ", "1", "2", "3", "4", "5", "6", "7", "8", "9", 
               "spotify", "pre-chorus", "post-chorus", "variation", "title: ", "verse", "chorus", "bridge", "outro", "intro", 
               "[ ]", "[]", "[", "]", ":", "lyrics"] + artist_name.lower().split(" ")
    for remov in removal:
        file = file.lower().replace(remov, "")
    # Replace 2 or more whitespace characters with a single space
    file = re.sub(r'\s{2,}', ' ', file)  
    file = re.sub(r'\n{2,}', ' ', file) 

    # Cracking down on some more characters
    set_remove = {'(', ')', "*", '"', ":" '[', ']', '0', '/7', '❤', '\xa0', '«', '»', '\u205f', '\ufeff', '×', '†', 'Ø', 'à', 'å', 'æ', 'é', 'í', 'ñ', 'ó', 'ø', 'ú', 'œ', 'і', 'ї', '\u2005', '\u200a', '\u200b', '\u200e'}

    # Remove unwanted characters
    file = ''.join([char for char in file if char not in set_remove and not is_russian_character(char)])
    file = file.lower()
    #print(file)
    return file
