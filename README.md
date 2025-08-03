# About this repo
This repo houses the code for both a personal project I did to provide a service I wanted, and a website that serves that project cleanly on the web. 

The project itself is called pod-search (for now at least), and the code for it is found in [scripts](scripts). It is essentially two classes that wrap AssemblyAI, ChatGPT embeddings, and the FAISS vector index package to transcribe podcasts and make them semantically searchable. I wrote it without the use of AI.

The code for the website that uses pod-search in its backend is located in [site](site). It includes two servers, one for the API for searching, and one for the site that displays podcast transcripts. I created this in order to be able to search for passages and ideas from the BibleProject podcast, and I created this proof of concept with its content.

Below I will include what I hope is helpful documentation for the simple pod-search classes and then I will describe briefly how to serve the site on local servers.


# Introducing pod-search 
### A tool to automatically transcribe, index, and semantic-search your favorite podcast.
This project was born from a specific frustration I had with *my* favorite podcast, from The BibleProject. While they have begun to transcribe their podcasts, I still struggled to find the lines and ideas that I wanted to revisit or share. pod-search uses Assembly AI's automatic transcription API and Facebook's faiss-cpu package to transcribe, embed, and index podcast episodes in order to be able to easily search semantically for the moments you want to revisit.

## Disclaimer
This project is very much still in development, and I am actively adding methods and documentation to make this project easier to use. Also, I have no affiliation with the BibleProject. Incredible podcasts, classes, videos, articles and more can be found for free at [their website](https://bibleproject.com)

## Using pod-search
I am planning to turn this into an easier-to-use package, but for now users will need to clone this repo in order to use it.

### Installation
#### MacOS / Unix
```bash
cd Documents                                              # Navigate to Documents folder
mkdir pod-search                                          # Make a new folder called WordTree_Game
cd pod-search                                             # Navigate into the new folder
git clone git@github.com:jackdpond/pod-search.git         # Clone this git repository
python3 -m venv venv                                      # Create a virtual environment
source venv/bin/activate                                  # Activate virtual environment
pip install -r requirements.txt                           # Install dependencies
```
#### Windows
```bash
cd Documents                                              # Navigate to Documents folder
mkdir pod-search                                          # Make a new folder called WordTree_Game
cd pod-search                                             # Navigate into the new folder
git clone git@github.com:jackdpond/pod-search.git         # Clone this git repository
python3 -m venv venv                                      # Create a virtual environment
.\venv\Scripts\activate                                   # Activate virtual environment
pip install -r requirements.txt                           # Install dependencies
```
### Creating a searchable index
The `Index()` object will be created using `Episode()` objects, each of which will have attributes `series_name` and `episode_name`. That way, when we search, the results appear with a series/season name, episode name, and a time stamp.

The `Index()` object has a method `.add_episode()` which can be used to add individual episodes via file path or url. This can be used as follows:
```python
from scribe import Index

index = Index()
index.add_episode(episode_title: str, series_title: str, audio_file_path: str)
# or
index.add_episode(episode_title: str, series_title: str, audio_url: str)
```

However, the easier method is to use `Index.add_series()`, which allows the user to add an entire podcast series or season by setting up the file tree in a particular way. `.add_series()` accepts either a file directory or a .txt file listing urls.
##### Directory method
```
pod-search/
├── README.md
├── requirements.txt
├── .gitignore
├── scripts/
│ └── transcripts/
│ └── database/
│ └── <Podcast_Title_Here>/
│   ├── <Episode_1_Title>.mp3
│   ├── <Episode_2_Title>.mp3
│   ├── <Episode_3_Title>.mp3
│ ├── search.py
│ ├── experiment.py
│ ├── scribe.py
```

##### Urls list method
```
pod-search/
├── README.md
├── requirements.txt
├── .gitignore
├── scripts/
│ └── transcripts/
│ └── database/
│ ├── <Podcast_Title_Here>.txt
│ ├── search.py
│ ├── experiment.py
│ ├── scribe.py
```
Where the <Podcast_Title_Here>.txt contains one podcast episode title along with its corresponding url per line, separated by a comma, like so:
```txt
Episode 1,https://episode1.url-ish-text-here.112233
Episode 2,https://episode2.url-ish-text-here.445566
Episode 3,https://episode3.url-ish-text-here.778899
```

Once the file tree is set up after the preferred manner, the `Index.add_series()` method is used like so:
```python
from scribe import Index

index = Index()

index.add_series(directory_path: str)
# or
index.add_series(urls_list_path: str)
```
This will take a few minutes to run. Once it is finished, you will have a vector database that is ready to search!

### Search
The search.py script is for searching the index. Because it is an index of sentence embeddings, you will be able to search semantically, not using keywords.

```bash
cd scripts/
python3 search.py 'Type your own query here!' --filename <path/to/vector/database> --k-nearest-neighbors <how many results to display>
```

For example, running the following command in the right directory returns the search results printed below the command.  
**Command**
```bash
python3 search.py 'When God allies himself with humans who are imperfect, things can get messy.' --filename Exodus --k-nearest-neighbors 5
```
**Results**
```
Loaded Vector Database from database/exodus_way_db.index and database/exodus_way_db.index
Query embedding obtained
Search completed
The Exodus Way: How Did Israel End Up in Egypt? at 00:51:24
But then when you make the Exodus story the big narrative and you realize that God's working with humans that are just compromised, then there is no hero and there is no bad guy. Everyone is kind of in on it.
Similarity: 0.4978547692298889
-------------------------------------------------------------------------------
The Exodus Way: The New Pharaohs of Joshua and Judges at 00:36:17
But Israel is such an imperfect, flawed tool themselves. And that's when you hear the other main theme of these stories, which is with Rahab and the Achan story, which.
Similarity: 0.49064210057258606
-------------------------------------------------------------------------------
The Exodus Way: How Did Israel End Up in Egypt? at 00:49:46
Of their just oppression and bad decisions and scheming. And then there's this kind of underlying theme that you're showing us, which is the complication of God attaching himself to a family who's not going to always make the right decisions.
Similarity: 0.4745718538761139
-------------------------------------------------------------------------------
The Exodus Way: Israel’s Deliverance and the Song of the Sea at 00:00:45
God will accept a blameless representative who stands over a house and look on that house as a group of people that are right with me in the midst of a land that's full of people who are not right with me. So that's the first rescue, rescue from death.
Similarity: 0.4680551588535309
-------------------------------------------------------------------------------
The Exodus Way: How Did Israel End Up in Egypt? at 00:01:51
The story of Abraham is extremely nuanced in portraying the relationship that God has with his people. Look at the moral complexity of even God's involvement in human history. If God makes promises to people, then he has to work with the people as he finds them.
Similarity: 0.4671679437160492
-------------------------------------------------------------------------------
```

## Use of AI in this project
While I am not opposed to using AI to code and develop, I decided to use AI minimally to build this tool. I used ChatGPT for advice while choosing to use an AI transcription service and a vector database package, ultimately deciding on Assembly AI and FAISS, respectively.

For the code itself, I wrote and organized without AI, with the exception of the function `Episode.save_as_pdf()`, which uses a somewhat complicated package with which I am unfamiliar. I looked up documentation and consulted Stack Overflow when I had questions--which was often.

I am both grateful and excited for the opportunities AI-coding or vibe-coding has created and will create, I still plan to develop my own coding skills, which include a rote knowledge of syntax, but also critical thinking, reasoning, and creativity. I am aware that I could have created a better, neater, more functional tool more quickly using Cursor or ChatGPT, but a neat, functional tool was not my primary object in building pod-search. 

Perhaps pod-search marks a fork in my time spent coding from here on out. Perhaps from now on, I will code with one of two objects, or two mindesets. First, with a neat, functional final product in mind, or second, with the building of my brain and my character in mind. Maybe I will do the first in my profession, and the second as a hobby. 

I don't know how AI will change programming and I don't know how AI will change me. However, building pod-search has been both stimulating, frustrating, and relaxing for me, and I have enjoyed it immensely. 

# About BibleProject Pod-Search, the website
Hosting this site on a local server is very simple. First, clone this repo, as I demonstrated above in the [Installation section](#installation). Then, in order to serve the search API, run the following.
```bash
cd site
python3 start_search_server.py
```

Then, in another terminal tab, navigate to the pod-search directory and run the following commands.
```bash
cd site
python3 serve_site.py
```

Then visit the link printed to the terminal (http://localhost:8000) to see the website!

Using the sidebar, you can either navigate through the BibleProject series and episodes and read the transcripts, or you can semantically search all of BibleProject's podcast content. That the search is semantic means it isn't word for word, but rather idea for idea. Searching for a concept or something you remember hearing will point you towards parts of the podcast where Tim and John talk about the same concept. An example of a search and its results can be found [above](#search).

You may notice that the transcripts do not include speaker labels. That is for the very simple reason that I forgot to include them and did not realize until it would be difficult and expensive to add them back in. Sorry about that.


