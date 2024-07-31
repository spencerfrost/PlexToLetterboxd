# Plex to Letterboxd CSV Export

This script fetches your Plex watch history and exports it to a CSV file compatible with Letterboxd import format. It also retrieves additional movie details from The Movie Database (TMDb) API.

## Features

- Fetches watch history from your Plex server
- Retrieves additional movie details from TMDb
- Exports data in Letterboxd-compatible CSV format
- Includes error handling and progress indicators

## Requirements

- Python 3.6+
- `plexapi` library
- `requests` library
- `tqdm` library

## Setup

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/plex-to-letterboxd.git
   cd plex-to-letterboxd
   ```

2. Install required packages:
   ```
   pip install plexapi requests tqdm
   ```

3. Copy `config_template.py` to `config.py`:
   ```
   cp config_template.py config.py
   ```

4. Edit `config.py` and fill in your Plex credentials and TMDb API key:
   ```python
   PLEX_USERNAME = 'your_plex_username'
   PLEX_PASSWORD = 'your_plex_password'
   PLEX_SERVER_NAME = 'your_plex_server_name'
   TMDB_API_KEY = 'your_tmdb_api_key'
   ```

## Usage

Run the script:

```
python plex_to_letterboxd.py
```

The script will connect to your Plex server, fetch your watch history, and create a file named `plex_watch_history.csv` in the same directory.

## Importing to Letterboxd

1. Go to your Letterboxd profile settings
2. Navigate to the "Import & Export" section
3. Under "Import your data", select the CSV file option
4. Upload the `plex_watch_history.csv` file

## Notes

- The script may take some time to run, depending on the size of your watch history and your internet connection speed.
- Some items may have incomplete information due to retrieval errors. These will be noted in the console output.
- Make sure not to share your `config.py` file, as it contains sensitive information.
