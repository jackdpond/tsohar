import assemblyai as aai
import json
import os

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph
import faiss
from openai import OpenAI
import numpy as np

from dotenv import load_dotenv

load_dotenv()

def ms2hms(ms):
    seconds = ms // 1000
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02}:{minutes:02}:{secs:02}"

def clean_path_name(filename):
    filename = filename.replace('-', ' ').replace('_', ' ').replace('/', ' ').split('.')[0]
    return filename

def make_path_name(filename):
    filename = filename.replace(' ', '_')
    return filename

class Episode:

    def __init__(self, episode_title, series_title, audio_file, speaker_labels=True, speakers_expected=0, speaker_map={'A': 'A', 'B': 'B', 'C': 'C', 'D': 'D', 'E': 'E', 'F':'F', 'G': 'G'}, verbose=False):
        self.assembly_api_key = 0
        self.episode_title = episode_title
        self.series_title = series_title

        aai.settings.http_timeout = 240.0

        if speakers_expected > 0:
            config = aai.TranscriptionConfig(speech_model=aai.SpeechModel.nano, 
                                            speaker_labels=speaker_labels, 
                                            speakers_expected=speakers_expected)
        else:
            config = aai.TranscriptionConfig(speech_model=aai.SpeechModel.best, 
                                speaker_labels=speaker_labels)


        transcriber = aai.Transcriber(config=config).transcribe(audio_file)

        if transcriber.status == "error":
            raise RuntimeError(f"Transcription failed: {transcriber.error}")
        
        transcript = list()

        # Handle case of transcriber.utterances being None
        if not transcriber.utterances:
            raise ValueError("utterances attribute of transcriber object is None")
        for utterance in transcriber.utterances:
            transcript.append({"speaker": speaker_map[utterance.speaker],
                          "text": utterance.text,
                          "start": ms2hms(utterance.start),
                          "end": ms2hms(utterance.end)})
            
        self.transcript = transcript

        if verbose:
            for utterance in transcriber.utterances:
                print(f"{utterance.speaker}: {utterance.text}")

    def add_speaker_labels(self, speaker_map={'A': 'A', 'B': 'B', 'C': 'C'}):
        for utterance in self.transcript:
            utterance['speaker'] = speaker_map[utterance['speaker']]
        
    def save_as_json(self, destination):    
        directory, _ = os.path.split(destination)
        if not os.path.exists(directory):
            os.makedirs(directory)

        with open(destination, "w") as file:
            json.dump(self.transcript, file, indent=4)

        print("Saved as .json!")


    def save_as_pdf(self, destination):
        # Set up the PDF file
        directory, _ = os.path.split(destination)
        if not os.path.exists(directory):
            os.makedirs(directory)

        filename = destination
        document = SimpleDocTemplate(filename, pagesize=letter)

        # Create a custom style for text
        styles = getSampleStyleSheet()

        style_heading = ParagraphStyle(
            'HeadingStyle',
            parent=styles['Heading2'],
            fontName='Times-Roman',
            fontSize=16,
            alignment=1
        )

        style_title = ParagraphStyle(
            'TitleStyle',
            parent=styles['Title'],
            fontName='Times-Roman',
            fontSize=24,
            alignment=1
        )

        # Custom style for normal text with a serif font (Times New Roman)
        style_normal = ParagraphStyle(
            'NormalStyle', 
            parent=styles['Normal'],
            fontName='Times-Roman',  # Using Times New Roman
            fontSize=12,
            spaceBefore=5,
            spaceAfter=5,
            firstLineIndent=0,  # First line of the paragraph won't be indented
            leftIndent=15  # Indentation for following lines
        )

        # Custom style for speaker names (no bold, same size)
        style_speaker = ParagraphStyle(
            'SpeakerStyle',
            parent=styles['Normal'],
            fontName='Times-Roman',
            fontSize=12,
            spaceBefore=5,
            spaceAfter=5,
            firstLineIndent=0  # Speaker name is on the same line as dialogue
        )

        # Create a list of paragraph objects to add to the PDF
        content = []

        # Title
        content.append(Paragraph(self.episode_title, style_title))
        content.append(Paragraph(self.series_title, style_heading))

        # Loop through each item in the "interview" list
        for entry in self.transcript:
            speaker = entry["speaker"]
            text = entry["text"]
            
            # Add the speaker's name on the same line as the dialogue
            dialog = f"<b>{speaker}:</b> {text}"
            
            # Add the combined speaker and text paragraph
            content.append(Paragraph(dialog, style_normal))
            content.append(Paragraph("", style_normal))

        # Build the PDF
        document.build(content)

        print(f"PDF created: {filename}")


class Index:
    aai.settings.api_key = os.getenv("ASSEMBLY_API_KEY")

    def __init__(self, dimension=1536, embedding_model='text-embedding-3-small'):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.utterances = []

        self.client = OpenAI()
        self.embedding_model = embedding_model

    def add_batch_embeddings(self, texts, batch_size=100):
        for i in range(0, len(texts), batch_size):
            batch = texts[i: i+batch_size]
            response = self.client.embeddings.create(input=batch, model=self.embedding_model)
            batch_embeddings = np.array([item.embedding for item in response.data]).astype('float32')
            self.index.add(batch_embeddings)

        print('Created and added embeddings to index')

    def add_episode(self, episode: Episode, batch_size=100):
        documents = [{'text': utterance['text'],
                            'start': utterance['start'],
                            'end': utterance['end'],
                            'series': episode.series_title,
                            'episode': episode.episode_title}
                            for utterance in episode.transcript]
        self.utterances.extend(documents)

        texts = [doc['text'] for doc in documents]
        self.add_batch_embeddings(texts, batch_size)

        print("Index and utterances initialized.")

        self.save_database('temp')

        print("Checkpoint saved")

    def add_series(self, 
                   download_path, 
                   temp_episodes,
                   batch_size=100, 
                   speaker_map={'A': 'A', 'B': 'B', 'C': 'C', 'D': 'D', 'E': 'E', 'F':'F', 'G': 'G'}, 
                   transcribe=False, 
                   transcription_dir=None):
        if os.path.isdir(download_path):
            series_title = clean_path_name(download_path)
            for root, dirs, files in os.walk(download_path):
                # Do not enter subdirectories
                if dirs:
                    raise ValueError(f"Subdirectories found: {dirs}")
                
                for audio_file in files:
                    print(f'Processing: {audio_file}')
                    if not audio_file.lower().endswith('.mp3'):
                        raise ValueError(f"Non-MP3 file found: {audio_file}")
                    
                    episode_title = clean_path_name(audio_file)
                    if episode_title in temp_episodes:
                        print(f"Episode: {episode_title} already loaded")
                        continue
                    print(f'Series: {series_title}, Episode: {episode_title}')
                    audio_file_path = os.path.join(download_path, audio_file)
                    print(f"Path: {audio_file_path}")
                    new_episode = Episode(episode_title, series_title, audio_file_path, speaker_map=speaker_map)

                    if transcribe:
                        if not transcription_dir:
                            transcription_dir = f'transcripts'
                        transcript_file_path = audio_file_path.replace('mp3', 'pdf')
                        transcript_output_path = os.path.join(transcription_dir, transcript_file_path)
                        new_episode.save_as_pdf(transcript_output_path)

                    self.add_episode(new_episode, batch_size=batch_size)
                break
            
        elif download_path.split('.')[-1] == 'txt':
            series_title = clean_path_name(download_path.split('.')[-2])
            with open(download_path, 'r') as file:
                lines = file.readlines()
            
            for line in lines:
                episode_info = line.split(',')
                if len(episode_info) != 2:
                    raise ValueError(f'lines in the download_info .txt file must have two items each \n Your line is {line}')
                episode_title, download_url = episode_info[0],  episode_info[1]

                if episode_title in temp_episodes:
                    continue

                try:
                    print(f'Series: {series_title}, Episode: {episode_title}')
                    new_episode = Episode(episode_title, series_title, download_url, speaker_map=speaker_map)
                except RuntimeError as e:
                    print(f"{episode_title} failed to load due to Runtime Error")
                    print(e)
                    continue
                
                if transcribe:
                    if not transcription_dir:
                        transcription_dir = f'transcripts'
                    transcript_file_path = make_path_name(episode_title) + '.pdf'
                    transcript_output_path = os.path.join(transcription_dir, transcript_file_path)
                    new_episode.save_as_pdf(transcript_output_path)

                self.add_episode(new_episode, batch_size=batch_size)
        else:
            raise ValueError(f'download_path must be directory or .txt file instead of : {download_path}')

    def add_podcast(self, 
                    source_path, 
                    batch_size=100, 
                    speaker_map={'A': 'A', 'B': 'B', 'C': 'C', 'D': 'D', 'E': 'E', 'F':'F', 'G': 'G'}, 
                    transcribe=False, 
                    transcription_dir=None,
                    temp_filename='temp'):
        
        if os.path.exists(temp_filename + ".json"):
            self.load_database(temp_filename)
            print(f"Initialized database from {temp_filename}")
            temp_episodes = {snippet['episode'] for snippet in self.utterances}
            print("Loaded episodes are: ")
            for episode in temp_episodes:
                print(episode)
        else:
            temp_episodes = set()

        if not transcription_dir:
            transcription_dir = make_path_name(source_path)
        os.makedirs(transcription_dir, exist_ok=True)

        for _, sub_dirs, filenames in os.walk(source_path):
            for sub_dir in sub_dirs:
                sub_dir = make_path_name(sub_dir)
                sub_transcription_dir = f'{transcription_dir}/{sub_dir}'
                self.add_series(sub_dir, 
                                batch_size=batch_size, 
                                speaker_map=speaker_map, 
                                transcribe=transcribe, 
                                transcription_dir=sub_transcription_dir,
                                temp_episodes=temp_episodes)
            for filename in filenames:
                name, extension = filename.split('.')
                if extension == 'txt':
                    name = make_path_name(name)
                    sub_transcription_dir = f'{transcription_dir}/{name}'
                    self.add_series(os.path.join(source_path, filename),
                                    temp_episodes=temp_episodes,
                                    batch_size=batch_size, 
                                    speaker_map=speaker_map,
                                    transcribe=transcribe, 
                                    transcription_dir=sub_transcription_dir)
                else:
                    raise ValueError(f'download_path must be directory or .txt file instead of : {source_path}')
        
    def search(self, query, k=5, verbose=False):
        query_embedding = self.client.embeddings.create(input=query, model=self.embedding_model).data[0].embedding
        print('Query embedding obtained')
        query_vector = np.array([query_embedding]).astype('float32')
        distances, indices = self.index.search(query_vector, k)
        
        print('Search completed')

        results = []
        for distance, idx in zip(distances[0], indices[0]):
            result = self.utterances[idx].copy()
            result['similarity score'] = 1 / (1 + distance)
            result['series'] = result['series'].replace(' Bible Project ', '')
            results.append(result)

            if verbose:
                print(f'{result['series']}: {result['episode']} at {result['start']}')
                print(f'{result['text']}')
                print(f'Similarity: {result['similarity score']}')
                print('-------------------------------------------------------------------------------')

        return results
    
    def save_database(self, filename):
        """Save FAISS index and documents to disk"""
        faiss.write_index(self.index, f"{filename}.index")

        print(f'FAISS index saved to {filename}.index')

        with open(f"{filename}.json", 'w') as f:
            json.dump(self.utterances, f)

        print(f'Text, metadata saved to {filename}.json')

    def load_database(self, filename: str):
        """Load FAISS index and documents from disk"""
        self.index = faiss.read_index(f"{filename}.index")
        with open(f"{filename}.json", 'r') as f:
            self.utterances = json.load(f)

        print(f'Loaded Vector Database from {filename}.index and {filename}.index')