import requests
import csv
from plexapi.myplex import MyPlexAccount
from plexapi.exceptions import NotFound
from tqdm import tqdm
from config import PLEX_USERNAME, PLEX_PASSWORD, PLEX_SERVER_NAME, TMDB_API_KEY

def get_tmdb_details(title, year):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}&year={year}"
    response = requests.get(url)
    if response.status_code == 200:
        results = response.json().get('results', [])
        if results:
            return results[0]
    return None

def get_imdb_id(tmdb_id):
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={TMDB_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get('imdb_id', '')
    return ''

def main():
    print(f"Connecting to Plex server: {PLEX_SERVER_NAME}...")
    account = MyPlexAccount(PLEX_USERNAME, PLEX_PASSWORD)
    
    try:
        plex = account.resource(PLEX_SERVER_NAME).connect()
    except Exception as e:
        print(f"Error connecting to server '{PLEX_SERVER_NAME}': {str(e)}")
        print("Available servers:")
        for resource in account.resources():
            if resource.product == 'Plex Media Server':
                print(f"- {resource.name}")
        return

    print("Fetching watch history...")
    movie_section = None
    for section in plex.library.sections():
        if section.type == 'movie':
            movie_section = section
            break
    
    if not movie_section:
        print(f"No movie library found on server '{PLEX_SERVER_NAME}'.")
        return

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
                # Try to fetch the full movie object
                full_item = movie_section.get(item.title)
                
                title = full_item.title
                year = full_item.year
                watched_date = item.viewedAt if hasattr(item, 'viewedAt') else None
                
                tmdb_details = get_tmdb_details(title, year)
                tmdb_id = tmdb_details['id'] if tmdb_details else ''
                imdb_id = get_imdb_id(tmdb_id) if tmdb_id else ''
                
                row = {
                    'Title': title,
                    'Year': year,
                    'WatchedDate': watched_date.strftime('%Y-%m-%d') if watched_date else '',
                    'tmdbID': tmdb_id,
                    'imdbID': imdb_id,
                    'LetterboxdURI': f'https://boxd.it/{imdb_id[2:]}' if imdb_id else ''
                }
                writer.writerow(row)
            except NotFound as e:
                print(f"\nWarning: Unable to find item with rating key {item.ratingKey}. Error: {str(e)}")
                # Try to write a row with available information
                title = getattr(item, 'title', 'Unknown')
                year = getattr(item, 'year', '')
                watched_date = item.viewedAt if hasattr(item, 'viewedAt') else None
                
                tmdb_details = get_tmdb_details(title, year)
                tmdb_id = tmdb_details['id'] if tmdb_details else ''
                imdb_id = get_imdb_id(tmdb_id) if tmdb_id else ''
                
                row = {
                    'Title': title,
                    'Year': year,
                    'WatchedDate': watched_date.strftime('%Y-%m-%d') if watched_date else '',
                    'tmdbID': tmdb_id,
                    'imdbID': imdb_id,
                    'LetterboxdURI': f'https://boxd.it/{imdb_id[2:]}' if imdb_id else ''
                }
                writer.writerow(row)
            except Exception as e:
                print(f"\nError processing item: {str(e)}")
    
    print("\nCSV file 'plex_watch_history.csv' has been created successfully.")
    print("Note: Some items may have incomplete information due to retrieval errors.")

if __name__ == "__main__":
    main()
