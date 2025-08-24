#!/usr/bin/env python3
"""
Offline Holy Books Facts Checker - Works without OpenAI API
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import json
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import re
from typing import Dict, List, Optional, Tuple
import logging

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize sentence transformer for embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')

class OfflineHolyBooksFactsChecker:
    def __init__(self):
        self.scriptures = {
            'hinduism': {
                'bhagavad_gita': {
                    'name': 'Bhagavad Gita',
                    'translations': ['Swami Prabhupada', 'Eknath Easwaran', 'Juan Mascaro'],
                    'verses': self._load_scripture_data('bhagavad_gita')
                },
                'vedas': {
                    'name': 'Vedas',
                    'translations': ['Ralph T.H. Griffith', 'Arthur Anthony Macdonell'],
                    'verses': self._load_scripture_data('vedas')
                }
            },
            'islam': {
                'quran': {
                    'name': 'Quran',
                    'translations': ['Sahih International', 'Pickthall', 'Yusuf Ali'],
                    'verses': self._load_scripture_data('quran')
                }
            },
            'christianity': {
                'bible': {
                    'name': 'Bible',
                    'translations': ['King James Version', 'New International Version', 'English Standard Version'],
                    'verses': self._load_scripture_data('bible')
                }
            },
            'sikhism': {
                'guru_granth_sahib': {
                    'name': 'Guru Granth Sahib',
                    'translations': ['Gurbachan Singh Talib', 'Sant Singh Khalsa'],
                    'verses': self._load_scripture_data('guru_granth_sahib')
                }
            },
            'buddhism': {
                'tripitaka': {
                    'name': 'Tripitaka',
                    'translations': ['Bhikkhu Bodhi', 'Thanissaro Bhikkhu'],
                    'verses': self._load_scripture_data('tripitaka')
                }
            },
            'judaism': {
                'tanakh': {
                    'name': 'Tanakh',
                    'translations': ['Jewish Publication Society', 'Robert Alter'],
                    'verses': self._load_scripture_data('tanakh')
                }
            }
        }
        
        # Initialize vector database
        self.vector_db = self._initialize_vector_db()
        
        # Initialize database
        self._init_database()

    def _load_scripture_data(self, scripture_name: str) -> List[Dict]:
        """Load scripture data from JSON files or create sample data"""
        try:
            with open(f'data/{scripture_name}.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Return sample data if file doesn't exist
            return self._get_sample_verses(scripture_name)

    def _get_sample_verses(self, scripture_name: str) -> List[Dict]:
        """Generate sample verses for demonstration"""
        sample_verses = {
            'bhagavad_gita': [
                {
                    'chapter': 2,
                    'verse': 47,
                    'text': 'You have the right to work, but never to the fruit of work.',
                    'translation': 'Swami Prabhupada',
                    'original': 'कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।'
                },
                {
                    'chapter': 18,
                    'verse': 66,
                    'text': 'Abandon all varieties of religion and just surrender unto Me.',
                    'translation': 'Swami Prabhupada',
                    'original': 'सर्वधर्मान्परित्यज्य मामेकं शरणं व्रज।'
                }
            ],
            'quran': [
                {
                    'surah': 1,
                    'ayah': 1,
                    'text': 'In the name of Allah, the Entirely Merciful, the Especially Merciful.',
                    'translation': 'Sahih International',
                    'original': 'بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ'
                },
                {
                    'surah': 2,
                    'ayah': 255,
                    'text': 'Allah - there is no deity except Him, the Ever-Living, the Self-Sustaining.',
                    'translation': 'Sahih International',
                    'original': 'اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ'
                }
            ],
            'bible': [
                {
                    'book': 'Matthew',
                    'chapter': 5,
                    'verse': 9,
                    'text': 'Blessed are the peacemakers, for they will be called children of God.',
                    'translation': 'NIV',
                    'original': 'μακάριοι οἱ εἰρηνοποιοί, ὅτι αὐτοὶ υἱοὶ θεοῦ κληθήσονται.'
                }
            ]
        }
        return sample_verses.get(scripture_name, [])

    def _initialize_vector_db(self) -> faiss.Index:
        """Initialize FAISS vector database with scripture embeddings"""
        all_texts = []
        for religion, texts in self.scriptures.items():
            for text_name, text_data in texts.items():
                for verse in text_data['verses']:
                    all_texts.append(verse['text'])
        
        if all_texts:
            embeddings = model.encode(all_texts)
            dimension = embeddings.shape[1]
            index = faiss.IndexFlatL2(dimension)
            index.add(embeddings.astype('float32'))
            return index
        return None

    def _init_database(self):
        """Initialize SQLite database for storing fact checks"""
        conn = sqlite3.connect('facts_checker_offline.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fact_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                claim TEXT NOT NULL,
                verdict TEXT NOT NULL,
                confidence REAL NOT NULL,
                rationale TEXT,
                citations TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()

    def classify_claim_type(self, claim: str) -> str:
        """Simple rule-based claim classification"""
        claim_lower = claim.lower()
        
        # Keywords for different claim types
        textual_keywords = ['says', 'states', 'mentions', 'writes', 'teaches', 'verse', 'chapter', 'book']
        historical_keywords = ['history', 'historical', 'event', 'occurred', 'happened', 'time', 'period']
        theological_keywords = ['belief', 'faith', 'divine', 'god', 'spiritual', 'sacred', 'holy']
        
        if any(keyword in claim_lower for keyword in textual_keywords):
            return 'textual'
        elif any(keyword in claim_lower for keyword in historical_keywords):
            return 'historical'
        elif any(keyword in claim_lower for keyword in theological_keywords):
            return 'theological'
        else:
            return 'mixed'

    def extract_references(self, claim: str) -> List[Dict]:
        """Extract scripture references from the claim"""
        references = []
        
        # Pattern for various scripture references
        patterns = [
            r'(\w+)\s+(\d+):(\d+)',  # Book 1:1
            r'(\w+)\s+(\d+)\s+verse\s+(\d+)',  # Book 1 verse 1
            r'surah\s+(\d+)\s+ayah\s+(\d+)',  # surah 1 ayah 1
            r'chapter\s+(\d+)\s+verse\s+(\d+)',  # chapter 1 verse 1
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, claim, re.IGNORECASE)
            for match in matches:
                references.append({
                    'type': 'scripture_reference',
                    'match': match.group(0),
                    'groups': match.groups()
                })
        
        return references

    def search_scriptures(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search scriptures using vector similarity"""
        if not self.vector_db:
            return []
        
        query_embedding = model.encode([query])
        D, I = self.vector_db.search(query_embedding.astype('float32'), top_k)
        
        results = []
        for idx in I[0]:
            # This is a simplified version - in practice you'd maintain a mapping
            # between vector indices and actual scripture verses
            results.append({
                'text': f"Scripture verse {idx}",
                'similarity_score': float(D[0][list(I[0]).index(idx)])
            })
        
        return results

    def fact_check_claim(self, claim: str, language: str = 'en') -> Dict:
        """Main fact checking function using local analysis only"""
        try:
            # Classify claim type
            claim_type = self.classify_claim_type(claim)
            
            # Extract references
            references = self.extract_references(claim)
            
            # Search relevant scriptures
            search_results = self.search_scriptures(claim)
            
            # Generate fact check using local analysis
            result = self._generate_local_response(claim, claim_type, references, search_results)
            
            # Add metadata
            result.update({
                'claim': claim,
                'claim_type': claim_type,
                'language': language,
                'timestamp': datetime.now().isoformat(),
                'references_found': references,
                'mode': 'offline'
            })
            
            # Store in database
            self._store_fact_check(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in fact checking: {e}")
            return {
                'verdict': 'Unclear',
                'confidence': 0,
                'rationale': 'Unable to process the claim at this time.',
                'citations': [],
                'alternative_views': [],
                'next_steps': ['Please try rephrasing your claim or contact support if the issue persists.'],
                'claim': claim,
                'claim_type': 'unknown',
                'language': language,
                'timestamp': datetime.now().isoformat(),
                'mode': 'offline'
            }

    def _generate_local_response(self, claim: str, claim_type: str, references: List[Dict], search_results: List[Dict]) -> Dict:
        """Generate a response using local analysis only"""
        
        # Check if we have any scripture references
        if references:
            # Try to find relevant verses in our local data
            relevant_verses = []
            for ref in references:
                for religion, texts in self.scriptures.items():
                    for text_name, text_data in texts.items():
                        for verse in text_data['verses']:
                            # Simple keyword matching
                            if any(keyword.lower() in verse['text'].lower() for keyword in claim.split()):
                                relevant_verses.append({
                                    'work': text_data['name'],
                                    'reference': f"{verse.get('chapter', verse.get('surah', verse.get('book', '')))}:{verse.get('verse', verse.get('ayah', ''))}",
                                    'text': verse['text']
                                })
            
            if relevant_verses:
                return {
                    'verdict': 'Partially supported',
                    'confidence': 70,
                    'rationale': f'Found relevant scripture passages that relate to your claim: "{claim}". This analysis is based on local scripture search and keyword matching.',
                    'citations': relevant_verses[:3],  # Limit to 3 citations
                    'alternative_views': ['Consider consulting multiple translations and scholarly commentaries for a complete understanding.'],
                    'next_steps': [
                        'Review the cited passages in their full context',
                        'Consult multiple translations for better understanding',
                        'Check scholarly commentaries for detailed analysis',
                        'Enable OpenAI API for more advanced AI analysis'
                    ]
                }
        
        # Generic response for claims without direct matches
        return {
            'verdict': 'Unclear',
            'confidence': 40,
            'rationale': f'Unable to find direct scripture references for claim: "{claim}". This analysis is based on local scripture search only. For more comprehensive analysis, consider enabling OpenAI API.',
            'citations': [],
            'alternative_views': ['Consider consulting primary religious texts and scholarly sources directly.'],
            'next_steps': [
                'Try rephrasing your claim with more specific scripture references',
                'Consult primary religious texts and commentaries directly',
                'Enable OpenAI API for advanced AI-powered analysis'
            ]
        }

    def _store_fact_check(self, result: Dict):
        """Store fact check result in database"""
        try:
            conn = sqlite3.connect('facts_checker_offline.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO fact_checks (claim, verdict, confidence, rationale, citations)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                result['claim'],
                result['verdict'],
                result['confidence'],
                result['rationale'],
                json.dumps(result.get('citations', []))
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error storing fact check: {e}")

    def get_fact_check_history(self, limit: int = 10) -> List[Dict]:
        """Get recent fact check history"""
        try:
            conn = sqlite3.connect('facts_checker_offline.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT claim, verdict, confidence, rationale, citations, timestamp
                FROM fact_checks
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'claim': row[0],
                    'verdict': row[1],
                    'confidence': row[2],
                    'rationale': row[3],
                    'citations': json.loads(row[4]) if row[4] else [],
                    'timestamp': row[5]
                })
            
            conn.close()
            return results
        except Exception as e:
            logger.error(f"Error getting history: {e}")
            return []

# Initialize the facts checker
facts_checker = OfflineHolyBooksFactsChecker()

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/fact-check', methods=['POST'])
def fact_check():
    """API endpoint for fact checking"""
    try:
        data = request.get_json()
        claim = data.get('claim', '').strip()
        language = data.get('language', 'en')
        
        if not claim:
            return jsonify({'error': 'Claim is required'}), 400
        
        result = facts_checker.fact_check_claim(claim, language)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in fact-check endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/history')
def get_history():
    """Get fact check history"""
    try:
        limit = request.args.get('limit', 10, type=int)
        history = facts_checker.get_fact_check_history(limit)
        return jsonify(history)
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Starting Offline Holy Books Facts Checker...")
    print("📝 This version works without OpenAI API")
    print("🌐 Open your browser and go to: http://localhost:5001")
    app.run(debug=True, host='0.0.0.0', port=5001)
