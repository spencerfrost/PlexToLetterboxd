import requests
import csv
from datetime import datetime
from plexapi.myplex import MyPlexAccount
from plexapi.exceptions import NotFound
from tqdm import tqdm
from config import PLEX_USERNAME, PLEX_PASSWORD, PLEX_SERVER_NAME, TMDB_API_KEY

def get_tmdb_details(title, year):
    url = f"https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": title,
        "year": year
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        results = response.json().get('results', [])
        return results[0] if results else None
    return None

def get_imdb_id(tmdb_id):
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
    params = {"api_key": TMDB_API_KEY}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get('imdb_id', '')
    return ''

def connect_to_plex():
    print(f"Connecting to Plex server: {PLEX_SERVER_NAME}...")
    account = MyPlexAccount(PLEX_USERNAME, PLEX_PASSWORD)
    try:
        return account.resource(PLEX_SERVER_NAME).connect()
    except Exception as e:
        print(f"Error connecting to server '{PLEX_SERVER_NAME}': {str(e)}")
        print("Available servers:")
        for resource in account.resources():
            if resource.product == 'Plex Media Server':
                print(f"- {resource.name}")
        return None

def get_movie_section(plex):
    for section in plex.library.sections():
        if section.type == 'movie':
            return section
    print(f"No movie library found on server '{PLEX_SERVER_NAME}'.")
    return None

def process_item(item, movie_section):
    try:
        full_item = movie_section.get(item.title)
        title = full_item.title
        year = full_item.year
    except NotFound:
        print(f"\nWarning: Unable to find item with rating key {item.ratingKey}.")
        title = getattr(item, 'title', 'Unknown')
        year = getattr(item, 'year', '')
    
    watched_date = item.viewedAt if hasattr(item, 'viewedAt') else None
    tmdb_details = get_tmdb_details(title, year)
    tmdb_id = tmdb_details['id'] if tmdb_details else ''
    imdb_id = get_imdb_id(tmdb_id) if tmdb_id else ''
    
    return {
        'Title': title,
        'Year': year,
        'WatchedDate': watched_date.strftime('%Y-%m-%d') if watched_date else '',
        'tmdbID': tmdb_id,
        'imdbID': imdb_id,
        'LetterboxdURI': f'https://boxd.it/{imdb_id[2:]}' if imdb_id else ''
    }

def main():
    plex = connect_to_plex()
    if not plex:
        return

    movie_section = get_movie_section(plex)
    if not movie_section:
        return

    print("Fetching watch history...")
    history = movie_section.history()
    total_items = len(history)
    print(f"Found {total_items} items in watch history.")
    print("Processing items and writing to CSV...")
    
    with open('plex_watch_history.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Title', 'Year', 'WatchedDate', 'tmdbID', 'imdbID', 'LetterboxdURI']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for item in tqdm(history, total=total_items, desc="Processing", unit="item"):
            try:
                row = process_item(item, movie_section)
                writer.writerow(row)
            except Exception as e:
                print(f"\nError processing item: {str(e)}")
    
    print("\nCSV file 'plex_watch_history.csv' has been created successfully.")
    print("Note: Some items may have incomplete information due to retrieval errors.")

if __name__ == "__main__":
    main()