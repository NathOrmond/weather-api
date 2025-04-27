import unittest
from unittest.mock import patch
import uuid
from dataclasses import dataclass
from api.repositories.memory_repository import InMemoryRepository

import pytest  

@dataclass
class EntityForTesting:
    """Simple test entity for repository testing."""
    name: str
    value: int
    id: uuid.UUID = None

    def __post_init__(self):
        # Auto-generate uuid if not provided
        if self.id is None:
            self.id = uuid.uuid4()


class TestInMemoryRepository(unittest.TestCase):
    """Test the generic InMemoryRepository implementation."""

    def setUp(self):
        """Set up a test repository and some test entities."""
        self.repo = InMemoryRepository[EntityForTesting]()
        self.entity1 = EntityForTesting(name="Test1", value=42)
        self.entity2 = EntityForTesting(name="Test2", value=99)
        
    def test_add_entity(self):
        """Test adding an entity to the repository."""
        # Test adding an entity returns the same entity
        result = self.repo.add(self.entity1)
        self.assertEqual(result.id, self.entity1.id)
        self.assertEqual(result.name, "Test1")
        self.assertEqual(result.value, 42)
        # Verify entity was added by getting it directly
        stored_entity = self.repo._data[self.entity1.id]
        self.assertEqual(stored_entity.id, self.entity1.id)
        self.assertEqual(stored_entity.name, "Test1")
        # Test adding duplicate ID raises an error
        with self.assertRaises(ValueError):
            self.repo.add(self.entity1)
        # Test adding entity without ID raises an error
        with self.assertRaises(ValueError):
            # Create an entity without ID
            bad_entity = EntityForTesting.__new__(EntityForTesting)
            bad_entity.name = "BadEntity"
            bad_entity.value = 0
            # No ID attribute
            self.repo.add(bad_entity)
    
    def test_get_by_id(self):
        """Test retrieving an entity by its ID."""
        # Add an entity
        self.repo.add(self.entity1)
        
        result = self.repo.get_by_id(self.entity1.id)
        self.assertEqual(result.id, self.entity1.id)
        self.assertEqual(result.name, "Test1")
        # Verify deep copy: changes to the result don't affect the stored entity
        result.name = "Modified"
        stored_entity = self.repo._data[self.entity1.id]
        self.assertEqual(stored_entity.name, "Test1")  
        
        # Test getting non-existent ID returns None
        non_existent_id = uuid.uuid4()
        self.assertIsNone(self.repo.get_by_id(non_existent_id))
    
    def test_get_all(self):
        """Test getting all entities from the repository."""
        self.assertEqual(len(self.repo.get_all()), 0)
        self.repo.add(self.entity1)
        self.repo.add(self.entity2)
        results = self.repo.get_all()
        self.assertEqual(len(results), 2)
        ids = {e.id for e in results}
        self.assertEqual(ids, {self.entity1.id, self.entity2.id})
        for e in results:
            e.name = "Modified"
        self.assertEqual(self.repo._data[self.entity1.id].name, "Test1")
        self.assertEqual(self.repo._data[self.entity2.id].name, "Test2")
    
    def test_update(self):
        """Test updating an entity in the repository."""
        self.repo.add(self.entity1)
        modified_entity = EntityForTesting(name="Modified", value=100, id=self.entity1.id)
        # Update entity
        result = self.repo.update(modified_entity)
        self.assertEqual(result.name, "Modified")
        self.assertEqual(result.value, 100)
        # Verify stored entity was updated
        stored_entity = self.repo._data[self.entity1.id]
        self.assertEqual(stored_entity.name, "Modified")
        self.assertEqual(stored_entity.value, 100)
        # Test updating non-existent entity returns None
        nonexistent = EntityForTesting(name="Nonexistent", value=0, id=uuid.uuid4())
        self.assertIsNone(self.repo.update(nonexistent))
        # Test updating entity without ID raises error
        with self.assertRaises(ValueError):
            # Create an entity without ID
            bad_entity = EntityForTesting.__new__(EntityForTesting)
            bad_entity.name = "BadEntity"
            bad_entity.value = 0
            # No ID attribute
            self.repo.update(bad_entity)
    
    def test_delete(self):
        """Test deleting an entity from the repository."""
        self.repo.add(self.entity1)
        result = self.repo.delete(self.entity1.id)
        self.assertTrue(result)
        self.assertNotIn(self.entity1.id, self.repo._data)
        self.assertFalse(self.repo.delete(uuid.uuid4()))
    
    def test_clear(self):
        """Test clearing all entities from the repository."""
        self.repo.add(self.entity1)
        self.repo.add(self.entity2)
        self.assertEqual(len(self.repo._data), 2)
        self.repo.clear()
        self.assertEqual(len(self.repo._data), 0)
        
    @patch('logging.Logger.debug')
    def test_logging(self, mock_debug):
        """Test that operations are properly logged."""
        self.repo.add(self.entity1)
        self.assertTrue(mock_debug.called)
        self.repo.get_all()
        self.repo.get_by_id(self.entity1.id)
        self.assertGreater(mock_debug.call_count, 2)


if __name__ == '__main__':
    unittest.main() 