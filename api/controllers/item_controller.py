def get_items():
    """Get all items"""
    # Implementation placeholder
    return [
        {"id": 1, "name": "Example Item 1", "description": "This is an example"},
        {"id": 2, "name": "Example Item 2", "description": "This is another example"}
    ], 200

def create_item(body):
    """Create a new item"""
    # Implementation placeholder - in a real application, would save to database
    # Just echo back the received item with an ID for demonstration
    return {**body, "id": 999}, 201

def get_item(item_id):
    """Get an item by ID"""
    # Implementation placeholder - would normally fetch from database
    if item_id == 999:
        return {"id": 999, "name": "Example Item", "description": "This is an example"}, 200
    return {"error": "Resource not found", "detail": "Item not found"}, 404
