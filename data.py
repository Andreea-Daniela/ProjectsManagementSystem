from bson import ObjectId
from pymongo import MongoClient

def insert_departments_and_line_managers(mongodb_uri):
    client = MongoClient(mongodb_uri)
    db = client.get_database()
    
    # Create a collection for departments if it doesn't exist
    departments_collection = db['departments']
    
    # Define the list of departments
    departments_data = ["Agile Hub", "Cyber Security", "AI"]
    
    # Insert departments into the collection
    for department_name in departments_data:
        department = {
            "_id": ObjectId(),
            "name": department_name
        }
        departments_collection.insert_one(department)
    
    # Create a collection for line managers if it doesn't exist
    line_managers_collection = db['line_managers']
    
    # Define the list of line managers
    line_managers_data = ["John Smith", "Alicia Reyes", "Adrian Ionescu"]
    
    # Insert line managers into the collection with unique email addresses
    for manager_name in line_managers_data:
        manager = {
            "_id": ObjectId(),
            "name": manager_name,
            "email": manager_name.replace(" ", "").lower() + "@example.com"
        }
        line_managers_collection.insert_one(manager)
