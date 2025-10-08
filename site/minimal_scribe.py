#!/usr/bin/env python3
"""
Minimal version of scribe.py for demo deployment.
Only includes the Index class and search functionality.
"""

import json
import os
import faiss
from openai import OpenAI
import numpy as np


class Index:
    def __init__(self, dimension=1536, embedding_model='text-embedding-3-small'):
        """
        Initialize an Index instance for search only
        """
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.utterances = []
        
        # Create OpenAI client
        self.client = OpenAI()
        self.embedding_model = embedding_model

    def load_database(self, filename: str):
        """Load FAISS index and documents from disk"""
        self.index = faiss.read_index(f"{filename}.index")
        with open(f"{filename}.json", 'r') as f:
            self.utterances = json.load(f)
        
        print(f"Loaded database with {len(self.utterances)} entries")

    def search(self, query, k=5, verbose=False):
        """Search for similar content"""
        query_embedding = self.client.embeddings.create(input=query, model=self.embedding_model).data[0].embedding
        query_vector = np.array([query_embedding]).astype('float32')
        distances, indices = self.index.search(query_vector, k)
        
        results = []
        for distance, idx in zip(distances[0], indices[0]):
            result = self.utterances[idx].copy()
            result['similarity_score'] = 1 / (1 + distance)
            result['series'] = result['series'].replace(' Bible Project ', '')
            results.append(result)

            if verbose:
                print(f'{result["series"]}: {result["episode"]} at {result["start"]}')
                print(f'{result["text"]}')
                print(f'Similarity: {result["similarity_score"]}')
                print('-' * 80)

        return results
