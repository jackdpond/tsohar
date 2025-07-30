# BibleProject Search Setup

This document explains how to set up and use the new semantic search functionality for the BibleProject podcast navigator.

## Overview

The search functionality now uses the Index class from `scribe.py` to perform semantic search on episode content. This provides much more accurate and relevant search results compared to simple text matching.

## Setup Instructions

### 1. Install Dependencies

First, install the required Python packages for the search API:

```bash
cd site
pip install -r requirements_api.txt
```

### 2. Start the Search API Server

The search functionality requires a Flask API server to be running. Start it with:

```bash
cd site
python start_search_server.py
```

Or directly:

```bash
cd site
python search_api.py
```

The server will start on `http://localhost:5000` and load the database files from `../scripts/database/bp_db`.

### 3. Start the Web Server

In a separate terminal, start the web server:

```bash
cd site
python serve_site.py
```

The site will be available at `http://localhost:8000`.

## How It Works

### Backend (search_api.py)
- Uses the Index class from `scribe.py` to load the pre-built FAISS index
- Provides a REST API endpoint at `/search?q=<query>&k=<number_of_results>`
- Returns search results as JSON with series, episode, text, and similarity scores

### Frontend (script.js)
- Modified `searchEpisodes()` function to call the API instead of local text matching
- Updated `renderSidebarSearchResults()` to handle the new result format
- Shows similarity scores and text previews in search results
- Falls back to old search method if API is unavailable

### Search Results Format

The API returns results in this format:
```json
[
  {
    "series": "Series Name",
    "episode": "Episode Title", 
    "text": "The actual text content that matched",
    "start": "00:01:30",
    "end": "00:01:45",
    "similarity_score": 0.85
  }
]
```

## Features

- **Semantic Search**: Uses OpenAI embeddings for context-aware search
- **Similarity Scores**: Shows how well each result matches the query
- **Text Previews**: Displays the actual matching text content
- **Fallback**: Falls back to simple text search if API is unavailable
- **Loading States**: Shows "Searching..." indicator during API calls

## Troubleshooting

### Database Files Not Found
Make sure `bp_db.index` and `bp_db.json` exist in `scripts/database/`.

### API Server Won't Start
- Check that all dependencies are installed
- Verify the database files exist
- Check the console for error messages

### Search Not Working
- Ensure the API server is running on port 5000
- Check browser console for CORS or network errors
- Verify the site is being served from a web server (not file://)

### Performance
- The first search may be slow as the database loads
- Subsequent searches should be faster
- Consider increasing the `k` parameter for more results 