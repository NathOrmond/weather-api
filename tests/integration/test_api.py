import unittest
import json
from app import app

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_get_items(self):
        response = self.app.get('/items')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
    
    def test_create_item(self):
        item_data = {
            "name": "Test Item",
            "description": "This is a test item"
        }
        response = self.app.post('/items', 
                                 data=json.dumps(item_data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["name"], item_data["name"])

if __name__ == '__main__':
    unittest.main()
