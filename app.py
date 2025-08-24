from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
import json
import sqlite3
from datetime import datetime
import openai
from dotenv import load_dotenv
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import re
from typing import Dict, List, Optional, Tuple
import logging
import google.generativeai as genai

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai.api_key = os.getenv('OPENAI_API_KEY')

# Initialize sentence transformer for embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')



class HolyBooksFactsChecker:
    def __init__(self):
        self.scriptures = {}
        data_dir = 'data'
        for fname in os.listdir(data_dir):
            name, ext = os.path.splitext(fname)
            if ext.lower() in ['.json', '.csv']:
                self.scriptures[name.lower()] = self._load_scripture_data(name)
        
        # Initialize vector database
        self.vector_db = self._initialize_vector_db()
        
        # Initialize database
        self._init_database()

    def _load_scripture_data(self, scripture_name: str) -> List[Dict]:
        """
        Load scripture data from any JSON or CSV file in the data/ directory
        that matches the scripture_name (case-insensitive, partial match allowed).
        """
        data_dir = 'data'
        scripture_files = os.listdir(data_dir)
        scripture_name_lower = scripture_name.lower()
        for fname in scripture_files:
            name, ext = os.path.splitext(fname)
            if scripture_name_lower in name.lower() and ext.lower() in ['.json', '.csv']:
                fpath = os.path.join(data_dir, fname)
                try:
                    if ext.lower() == '.json':
                        with open(fpath, 'r', encoding='utf-8') as f:
                            return json.load(f)
                    elif ext.lower() == '.csv':
                        df = pd.read_csv(fpath)
                        # Handle CSV structure for Bhagavad Gita
                        if 'EngMeaning' in df.columns and 'Shloka' in df.columns:
                            records = []
                            for idx, row in df.iterrows():
                                records.append({
                                    'text': row['EngMeaning'],
                                    'original': row['Shloka'],
                                    'chapter': idx // 20 + 1,  # Estimate chapter
                                    'verse': idx % 20 + 1,     # Estimate verse
                                    'work': scripture_name
                                })
                            return records
                        return df.to_dict(orient='records')
                except Exception as e:
                    logger.error(f"Error loading {fpath}: {e}")
                    continue
        # If nothing found, return sample data
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

    def _initialize_vector_db(self) -> Optional[faiss.Index]:
        """Initialize FAISS vector database with scripture embeddings"""
        all_texts = []
        self.verse_index_map = []
        for scripture_name, verses in self.scriptures.items():
            for verse in verses:
                all_texts.append(verse.get('text', ''))
                self.verse_index_map.append((scripture_name, verse))
        if all_texts:
            embeddings = model.encode(all_texts)
            dimension = embeddings.shape[1]
            index = faiss.IndexFlatL2(dimension)
            index.add(embeddings.astype('float32'))
            return index
        return None

    def _init_database(self):
        """Initialize SQLite database for storing fact checks"""
        conn = sqlite3.connect('facts_checker.db')
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
        """Classify the type of claim (textual, historical, mixed, theological)"""
        prompt = f"""
        Classify the following claim about religious texts into one of these categories:
        - textual: Claims about what a specific text says
        - historical: Claims about historical events or contexts
        - mixed: Claims that combine textual and historical elements
        - theological: Claims about matters of faith or belief that cannot be empirically verified
        
        Claim: "{claim}"
        
        Respond with only the category name.
        """
        
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0
            )
            return response.choices[0].message.content.strip().lower()
        except Exception as e:
            logger.error(f"Error classifying claim: {e}")
            # Check if it's a quota error and provide a default classification
            if "quota" in str(e).lower() or "429" in str(e):
                logger.warning("OpenAI quota exceeded during claim classification, using default")
            return "mixed"

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
        """Search scriptures using vector similarity or keyword match"""
        results = []
        if self.vector_db:
            query_embedding = model.encode([query])
            D, I = self.vector_db.search(query_embedding.astype('float32'), top_k)
            for idx in I[0]:
                scripture_name, verse = self.verse_index_map[idx]
                result = verse.copy()
                result['work'] = scripture_name
                results.append(result)
        else:
            # Fallback: keyword search
            for scripture_name, verses in self.scriptures.items():
                for verse in verses:
                    if query.lower() in verse.get('text', '').lower():
                        result = verse.copy()
                        result['work'] = scripture_name
                        results.append(result)
            results = results[:top_k]
        return results

    def fact_check_claim(self, claim: str, language: str = 'en') -> Dict:
        """Main fact checking function"""
        try:
            # Classify claim type
            claim_type = self.classify_claim_type(claim)
            
            # Extract references
            references = self.extract_references(claim)
            
            # Search relevant scriptures
            search_results = self.search_scriptures(claim)
            
            # Generate fact check using OpenAI
            prompt = f"""
            You are an impartial, respectful, and academically rigorous assistant that checks factual claims related to holy books.
            
            Claim: "{claim}"
            Claim Type: {claim_type}
            Language: {language}
            
            Please provide a fact check report with the following structure:
            1. Verdict: Supported/Contradicted/Partially supported/Unclear/Theological
            2. Confidence: 0-100%
            3. Rationale: Clear explanation of the verdict
            4. Citations: Relevant scripture passages with book/chapter/verse
            5. Alternative Views: If applicable, mention different scholarly interpretations
            
            Be respectful, neutral, and academic in your response. If this is a theological matter, 
            present different viewpoints rather than a true/false verdict.
            
            Respond in JSON format:
            {{
                "verdict": "string",
                "confidence": number,
                "rationale": "string",
                "citations": [{{"work": "string", "reference": "string", "text": "string"}}],
                "alternative_views": ["string"],
                "next_steps": ["string"]
            }}
            """
            
            try:
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000,
                    temperature=0.3
                )
                try:
                    result = json.loads(response.choices[0].message.content)
                except json.JSONDecodeError as json_error:
                    logger.error(f"Failed to parse OpenAI response as JSON: {json_error}")
                    logger.error(f"Raw response: {response.choices[0].message.content}")
                    # Fall back to Gemini
                    result = self._gemini_fact_check(claim, claim_type, language)
                    if not result:
                        # Fall back to local search
                        result = self._generate_fallback_response(claim, claim_type, references, search_results)
            except Exception as api_error:
                logger.error(f"OpenAI API error: {api_error}")
                # Try Gemini if OpenAI fails
                result = self._gemini_fact_check(claim, claim_type, language)
                if not result:
                    # Provide a fallback response based on local scripture search
                    result = self._generate_fallback_response(claim, claim_type, references, search_results)
            
            # Add metadata
            result.update({
                'claim': claim,
                'claim_type': claim_type,
                'language': language,
                'timestamp': datetime.now().isoformat(),
                'references_found': references
            })
            
            # Store in database
            self._store_fact_check(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in fact checking: {e}")
            return {
                'verdict': 'Unclear',
                'confidence': 0,
                'rationale': 'Unable to process the claim at this time. Please check your OpenAI or Gemini API quota or try again later.',
                'citations': [],
                'alternative_views': [],
                'next_steps': ['Please try rephrasing your claim or contact support if the issue persists.'],
                'claim': claim,
                'claim_type': 'unknown',
                'language': language,
                'timestamp': datetime.now().isoformat()
            }

    def _generate_fallback_response(self, claim: str, claim_type: str, references: List[Dict], search_results: List[Dict]) -> Dict:
        """Generate a fallback response when OpenAI API is unavailable"""
        # Try to find relevant verses in our local data
        relevant_verses = []
        for ref in references:
            for scripture_name, verses in self.scriptures.items():
                for verse in verses:
                    if any(keyword.lower() in verse.get('text', '').lower() for keyword in claim.split()):
                        relevant_verses.append({
                            'work': scripture_name,
                            'reference': f"{verse.get('chapter', verse.get('surah', verse.get('book', '')))}:{verse.get('verse', verse.get('ayah', ''))}",
                            'text': verse.get('text', '')
                        })
        if relevant_verses:
            return {
                'verdict': 'Partially supported',
                'confidence': 60,
                'rationale': f'Found relevant scripture passages that may relate to your claim: "{claim}". However, a full AI analysis is currently unavailable due to API quota limitations.',
                'citations': relevant_verses[:3],
                'alternative_views': ['Consider consulting multiple translations and scholarly commentaries for a complete understanding.'],
                'next_steps': [
                    'Review the cited passages in their full context',
                    'Consult multiple translations for better understanding',
                    'Check scholarly commentaries for detailed analysis'
                ]
            }
        # Generic fallback response
        return {
            'verdict': 'Unclear',
            'confidence': 30,
            'rationale': f'Unable to perform a complete fact check for claim: "{claim}" due to API quota limitations. The system can only provide basic scripture search without AI analysis.',
            'citations': [],
            'alternative_views': ['Consider consulting primary religious texts and scholarly sources directly.'],
            'next_steps': [
                'Consult primary religious texts and commentaries directly'
            ]
        }

    def _store_fact_check(self, result: Dict):
        """Store fact check result in database"""
        try:
            conn = sqlite3.connect('facts_checker.db')
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
            conn = sqlite3.connect('facts_checker.db')
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

    def _gemini_fact_check(self, claim, claim_type, language):
        """Fact check using Google Gemini as fallback with enhanced accuracy"""
        try:
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            # Enhanced prompt for better accuracy
            prompt = f"""
            You are an expert religious scholar and fact-checker with deep knowledge of holy books including the Bible, Quran, Bhagavad Gita, Torah, and other sacred texts. Your task is to provide accurate, scholarly analysis of religious claims.

            CLAIM TO ANALYZE: "{claim}"
            CLAIM TYPE: {claim_type}
            RESPONSE LANGUAGE: {language}

            INSTRUCTIONS:
            1. Analyze the claim against authentic religious sources
            2. Consider historical context and scholarly interpretations
            3. Be respectful of all religious traditions
            4. Provide specific scripture references when possible
            5. Acknowledge when claims involve matters of faith vs. factual content

            REQUIRED RESPONSE FORMAT (JSON):
            {{
                "verdict": "Supported|Contradicted|Partially supported|Unclear|Theological",
                "confidence": 85,
                "rationale": "Detailed explanation with reasoning and context",
                "citations": [
                    {{
                        "work": "Scripture name",
                        "reference": "Book/Chapter:Verse or Surah:Ayah",
                        "text": "Relevant passage text"
                    }}
                ],
                "alternative_views": ["Different scholarly interpretations if applicable"],
                "next_steps": ["Recommendations for further study"]
            }}

            Ensure your response is valid JSON and academically rigorous.
            """
            
            # Configure generation parameters for better accuracy
            generation_config = genai.types.GenerationConfig(
                temperature=0.1,  # Lower temperature for more consistent responses
                max_output_tokens=2000,
                top_p=0.8,
                top_k=40
            )
            
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Clean and parse response
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3].strip()
            elif response_text.startswith('```'):
                response_text = response_text[3:-3].strip()
                
            return json.loads(response_text)
            
        except json.JSONDecodeError as e:
            logger.error(f"Gemini returned invalid JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Error with Gemini API: {e}")
            return None

    def fact_check_claim(self, claim: str, language: str = 'en') -> dict:
        """Main fact checking function with OpenAI and Gemini fallback"""
        try:
            claim_type = self.classify_claim_type(claim)
            references = self.extract_references(claim)
            search_results = self.search_scriptures(claim)

            # Try OpenAI
            prompt = f"""
            You are an impartial, respectful, and academically rigorous assistant that checks factual claims related to holy books.

            Claim: "{claim}"
            Claim Type: {claim_type}
            Language: {language}

            Please provide a fact check report with the following structure:
            1. Verdict: Supported/Contradicted/Partially supported/Unclear/Theological
            2. Confidence: 0-100%
            3. Rationale: Clear explanation of the verdict
            4. Citations: Relevant scripture passages with book/chapter/verse
            5. Alternative Views: If applicable, mention different scholarly interpretations

            Respond in JSON format:
            {{
                "verdict": "string",
                "confidence": number,
                "rationale": "string",
                "citations": [{{"work": "string", "reference": "string", "text": "string"}}],
                "alternative_views": ["string"],
                "next_steps": ["string"]
            }}
            """
            try:
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000,
                    temperature=0.3
                )
                try:
                    result = json.loads(response.choices[0].message.content)
                except json.JSONDecodeError:
                    # If OpenAI returns non-JSON, try Gemini
                    result = self._gemini_fact_check(claim, claim_type, language)
                    if not result:
                        result = self._detailed_local_fallback(claim, claim_type, references, search_results)
            except Exception as api_error:
                # If OpenAI fails, try Gemini
                result = self._gemini_fact_check(claim, claim_type, language)
                if not result:
                    result = self._detailed_local_fallback(claim, claim_type, references, search_results)

            # Add metadata
            result.update({
                'claim': claim,
                'claim_type': claim_type,
                'language': language,
                'timestamp': datetime.now().isoformat(),
                'references_found': references
            })
            self._store_fact_check(result)
            return result

        except Exception as e:
            logging.error(f"Error in fact checking: {e}")
            return {
                'verdict': 'Unclear',
                'confidence': 0,
                'rationale': 'Unable to process the claim at this time. Please check your API quota or try again later.',
                'citations': [],
                'alternative_views': [],
                'next_steps': ['Please try rephrasing your claim or contact support if the issue persists.'],
                'claim': claim,
                'claim_type': 'unknown',
                'language': language,
                'timestamp': datetime.now().isoformat()
            }

    def _detailed_local_fallback(self, claim, claim_type, references, search_results):
        """Provide a more detailed local fallback using scripture search"""
        citations = []
        
        # Build proper citations from search results
        for result in search_results[:3]:
            if result.get("text"):
                citations.append({
                    "work": result.get("work", "Unknown Scripture").replace("_", " ").title(),
                    "reference": f"Chapter {result.get('chapter', result.get('surah', result.get('book', '')))}:{result.get('verse', result.get('ayah', result.get('verse_number', '')))}",
                    "text": result.get("text", "")[:200] + "..." if len(result.get("text", "")) > 200 else result.get("text", "")
                })
        
        # If no good citations found, try to use Gemini anyway
        if not citations:
            try:
                gemini_result = self._gemini_fact_check(claim, claim_type, "en")
                if gemini_result:
                    return gemini_result
            except Exception as e:
                logger.error(f"Gemini fallback failed: {e}")
        
        rationale = f"Based on local scripture search for '{claim}', " + (
            f"found {len(citations)} relevant passages. " if citations 
            else "no specific passages found in local data. "
        ) + "For comprehensive analysis, AI fact-checking with OpenAI or Gemini is recommended."
        
        return {
            "verdict": "Partially supported" if citations else "Unclear",
            "confidence": 65 if citations else 30,
            "rationale": rationale,
            "citations": citations,
            "alternative_views": ["Consult multiple translations and commentaries for deeper understanding.", "Consider the historical and cultural context of the passages."],
            "next_steps": [
                "Add OpenAI API key for enhanced fact-checking accuracy",
                "Review the cited passages in their full context",
                "Consult multiple translations for better understanding",
                "Check scholarly commentaries for detailed analysis"
            ]
        }

# Initialize the facts checker
facts_checker = HolyBooksFactsChecker()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/fact-check', methods=['POST'])
def fact_check():
    """Fact check endpoint"""
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

@app.route('/api/export/<int:check_id>')
def export_fact_check(check_id):
    """Export fact check as JSON"""
    try:
        conn = sqlite3.connect('facts_checker.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT claim, verdict, confidence, rationale, citations, timestamp
            FROM fact_checks
            WHERE id = ?
        ''', (check_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return jsonify({'error': 'Fact check not found'}), 404
        result = {
            'claim': row[0],
            'verdict': row[1],
            'confidence': row[2],
            'rationale': row[3],
            'citations': json.loads(row[4]) if row[4] else [],
            'timestamp': row[5]
        }
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error exporting fact check: {e}")
        return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
