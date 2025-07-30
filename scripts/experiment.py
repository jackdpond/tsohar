import importlib
import scribe

importlib.reload(scribe)
from scribe import Index

from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

if __name__ == "__main__":
    # episode_title = 'Episode 1: An Exodus Shaped Reality'
    # series_title = 'The Exodus Way'
    # bp = Episode(episode_title, series_title)
    speaker_map = {'A': 'John Collins',
                   'B': 'Tim Mackie',
                   'C': 'C',
                   'D': 'D',
                   'E': 'E',
                   'F': 'F',
                   'G': 'G',
                   'H': 'H'}
    for char in "IJKLMNOPQRSTUVWXYZ":
        speaker_map[char] = char
        
    bp = Index()
    bp.add_podcast('../Bible_Project/', speaker_map=speaker_map, transcription_dir="../Bible_Project_transcription")


    # bp.transcribe('audio_files/BP_An_Exodus_Shaped_Reality.mp3', verbose=True)
    # bp.add_speaker_labels(speaker_map)
    # bp.save_as_pdf('transcripts/Episode1.pdf')
    # bp.save_as_json('transcripts/Episode1.json')

    # db = Index()
    # # db.add_episode(bp)
    # # db.save_database('database/vector_db')
    # db.load_database('database/vector_db')
    # results = db.search('The way through the desert is the way to God')

    bp.save_database('database/bp_db')