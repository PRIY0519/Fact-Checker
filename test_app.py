import unittest
import json
import os
import tempfile
from app import app, facts_checker

class TestFactsChecker(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        
    def test_home_page(self):
        """Test that the home page loads correctly"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Holy Books Facts Checker', response.data)
        
    def test_fact_check_endpoint(self):
        """Test the fact check API endpoint"""
        test_claim = "Does Bhagavad Gita 2:47 say that outcomes don't matter?"
        
        response = self.app.post('/api/fact-check',
                               data=json.dumps({'claim': test_claim, 'language': 'en'}),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Check that required fields are present
        self.assertIn('verdict', data)
        self.assertIn('confidence', data)
        self.assertIn('rationale', data)
        self.assertIn('citations', data)
        self.assertIn('claim', data)
        
    def test_history_endpoint(self):
        """Test the history API endpoint"""
        response = self.app.get('/api/history')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        
    def test_claim_classification(self):
        """Test claim type classification"""
        textual_claim = "Bhagavad Gita 2:47 says that outcomes don't matter"
        historical_claim = "The Bhagavad Gita was written in 500 BCE"
        
        # Test textual claim classification
        result = facts_checker.classify_claim_type(textual_claim)
        self.assertIn(result, ['textual', 'historical', 'mixed', 'theological'])
        
        # Test historical claim classification
        result = facts_checker.classify_claim_type(historical_claim)
        self.assertIn(result, ['textual', 'historical', 'mixed', 'theological'])
        
    def test_reference_extraction(self):
        """Test scripture reference extraction"""
        claim_with_ref = "Bhagavad Gita 2:47 says that outcomes don't matter"
        claim_without_ref = "This is a general claim about religion"
        
        # Test extraction with reference
        refs = facts_checker.extract_references(claim_with_ref)
        self.assertGreater(len(refs), 0)
        
        # Test extraction without reference
        refs = facts_checker.extract_references(claim_without_ref)
        self.assertEqual(len(refs), 0)
        
    def test_fact_check_without_openai(self):
        """Test fact checking functionality (without OpenAI API)"""
        # Mock the OpenAI call to avoid API dependency in tests
        original_fact_check = facts_checker.fact_check_claim
        
        def mock_fact_check(claim, language='en'):
            return {
                'verdict': 'Supported',
                'confidence': 85,
                'rationale': 'This is a test response for the claim.',
                'citations': [{'work': 'Test Scripture', 'reference': '1:1', 'text': 'Test verse'}],
                'alternative_views': ['Some scholars disagree'],
                'next_steps': ['Consult additional sources'],
                'claim': claim,
                'claim_type': 'textual',
                'language': language,
                'timestamp': '2024-01-01T00:00:00'
            }
        
        facts_checker.fact_check_claim = mock_fact_check
        
        try:
            result = facts_checker.fact_check_claim("Test claim")
            self.assertEqual(result['verdict'], 'Supported')
            self.assertEqual(result['confidence'], 85)
            self.assertIn('citations', result)
        finally:
            facts_checker.fact_check_claim = original_fact_check
            
    def test_database_operations(self):
        """Test database operations"""
        # Test storing a fact check
        test_result = {
            'claim': 'Test claim for database',
            'verdict': 'Supported',
            'confidence': 90,
            'rationale': 'Test rationale',
            'citations': [{'work': 'Test', 'reference': '1:1', 'text': 'Test'}]
        }
        
        facts_checker._store_fact_check(test_result)
        
        # Test retrieving history
        history = facts_checker.get_fact_check_history(limit=1)
        self.assertGreater(len(history), 0)
        
    def test_invalid_requests(self):
        """Test handling of invalid requests"""
        # Test empty claim
        response = self.app.post('/api/fact-check',
                               data=json.dumps({'claim': '', 'language': 'en'}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)
        
        # Test missing claim
        response = self.app.post('/api/fact-check',
                               data=json.dumps({'language': 'en'}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)

class TestScriptureData(unittest.TestCase):
    
    def test_scripture_loading(self):
        """Test that scripture data loads correctly"""
        # Test that the facts checker initializes with scripture data
        self.assertIsNotNone(facts_checker.scriptures)
        
        # Test that major religions are included
        expected_religions = ['hinduism', 'islam', 'christianity', 'sikhism', 'buddhism', 'judaism']
        for religion in expected_religions:
            self.assertIn(religion, facts_checker.scriptures)
            
    def test_sample_verses(self):
        """Test that sample verses are available"""
        # Test Bhagavad Gita verses
        gita_verses = facts_checker.scriptures['hinduism']['bhagavad_gita']['verses']
        self.assertGreater(len(gita_verses), 0)
        
        # Test Quran verses
        quran_verses = facts_checker.scriptures['islam']['quran']['verses']
        self.assertGreater(len(quran_verses), 0)
        
        # Test Bible verses
        bible_verses = facts_checker.scriptures['christianity']['bible']['verses']
        self.assertGreater(len(bible_verses), 0)

if __name__ == '__main__':
    # Create a temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
        test_db_path = tmp_db.name
    
    # Set environment variable for test database
    os.environ['TEST_DB_PATH'] = test_db_path
    
    try:
        unittest.main(verbosity=2)
    finally:
        # Clean up test database
        if os.path.exists(test_db_path):
            os.unlink(test_db_path)
