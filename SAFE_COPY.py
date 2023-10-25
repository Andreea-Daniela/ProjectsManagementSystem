from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
from bson import json_util
import os
import json

app = Flask(__name__)

#####################################################################
                        # DATABASE 
#####################################################################
# Database connection
mongodb_uri = os.environ.get("MONGODB_URI")

if mongodb_uri is None:
    raise ValueError("MONGODB_URI environment variable is not set")

client = MongoClient(mongodb_uri)
db = client.get_database()

# Collection names
departments_collection = db['departments']
line_managers_collection = db['line_managers']
projects_collection = db['projects']

# Insert departments
def insert_departments():
    # Check if departments already exist
    existing_departments = list(departments_collection.find({}))
    if not existing_departments:
        departments_data = ["Agile Hub", "Cyber Security", "AI"]
        departments = []

        for department_name in departments_data:
            department = {
                "name": department_name
            }
            departments.append(department)

        departments_collection.insert_many(departments)
        print("Departments inserted successfully.")
    else:
        print("Departments already exist in the database.")

# Insert line managers
def insert_line_managers():
    # Check if line managers already exist
    existing_line_managers = list(line_managers_collection.find({}))
    if not existing_line_managers:
        line_managers_data = [
            {"name": "John Smith", "email": "johnsmith@example.com"},
            {"name": "Alicia Reyes", "email": "aliciareyes@example.com"},
            {"name": "Adrian Ionescu", "email": "adrianionescu@example.com"}
        ]

        line_managers = []

        for manager_data in line_managers_data:
            line_manager = {
                "name": manager_data['name'],
                "email": manager_data['email']
            }
            line_managers.append(line_manager)

        line_managers_collection.insert_many(line_managers)
        print("Line managers inserted successfully.")
    else:
        print("Line managers already exist in the database.")


#####################################################################
                        # PROJECT METHODS 
#####################################################################

# Custom JSON encoder
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)  # Convert ObjectId to string
        return super(CustomJSONEncoder, self).default(obj)

app.json_encoder = CustomJSONEncoder

###################### RETRIEVE ALL PROJECTS ########################
# Route to get all projects
@app.route('/projects', methods=['GET'])
def get_all_projects():
    projects = projects_collection.find()

    # Use json_util for serialization
    projects_data = json_util.dumps(list(projects))
    
    return projects_data, 200

###################### RETRIEVE ONE PROJECT #########################
# Route to get a single project by ID
@app.route('/projects/<string:project_id>', methods=['GET'])
def get_project_by_id(project_id):
    project = projects_collection.find_one({'_id': ObjectId(project_id)})

    if project is None:
        return jsonify({'error': 'Project not found'}), 404

    # Use json_util for serialization
    project_data = json_util.dumps(project)

    return project_data, 200

###################### CREATE A PROJECT #############################
# Create and add a project
@app.route('/create_project', methods=['POST'])
def create_project():
    data = request.json

    # Validate project data
    required_fields = ['title', 'line_manager', 'department', 'description', 'has_role_opening']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing field: {field}'}), 400

    # Check if the line manager and department exist
    line_manager_id = data['line_manager']
    department_id = data['department']

    department = departments_collection.find_one({'_id': ObjectId(department_id)})
    line_manager = line_managers_collection.find_one({'_id': ObjectId(line_manager_id)})

    if line_manager is None:
        return jsonify({'error': 'Line manager not found'}), 400

    if department is None:
        return jsonify({'error': 'Department not found'}), 400

    # Generate a new ObjectID for the project
    project_id = ObjectId()

    project = {
        '_id': project_id,
        'title': data['title'],
        'line_manager': line_manager,
        'department': department,
        'description': data['description'],
        'has_role_opening': data['has_role_opening']
    }

    projects_collection.insert_one(project)

    return jsonify({'message': 'Project created successfully', 'project_id': str(project_id)}), 201

###################### DELETE A PROJECT ###############################
# Route to delete a project by its ID
@app.route('/delete_project/<string:project_id>', methods=['DELETE'])
def delete_project(project_id):
    # Check if the project exists
    project = projects_collection.find_one({'_id': ObjectId(project_id)})
    
    if project is None:
        return jsonify({'error': 'Project not found'}), 404

    # Delete the project
    projects_collection.delete_one({'_id': ObjectId(project_id)})

    return jsonify({'message': 'Project deleted successfully'}), 200


###################### UPDATE A PROJECT ################################
# Route to update a project by its ID
@app.route('/update_project/<string:project_id>', methods=['PUT'])
def update_project(project_id):
    # Check if the project exists
    project = projects_collection.find_one({'_id': ObjectId(project_id)})
    
    if project is None:
        return jsonify({'error': 'Project not found'}), 404

    # Get the update data from the request
    data = request.json

    # Update the project fields
    if 'title' in data:
        project['title'] = data['title']
    if 'line_manager' in data:
        project['line_manager'] = data['line_manager']
    if 'department' in data:
        project['department'] = data['department']
    if 'description' in data:
        project['description'] = data['description']
    if 'has_role_opening' in data:
        project['has_role_opening'] = data['has_role_opening']

    # Update the project in the database
    projects_collection.update_one({'_id': ObjectId(project_id)}, {'$set': project})

    return jsonify({'message': 'Project updated successfully'}), 200


# Route to get all projects in a specific department
@app.route('/projects_dep/<department_id>', methods=['GET'])
def get_projects_in_department(department_id):
    department = departments_collection.find_one({'_id': ObjectId(department_id)})

    if department is None:
        return jsonify({'error': 'Department not found'}), 404

    projects = projects_collection.find({'department._id': ObjectId(department_id)})

    # Use json_util for serialization
    projects_data = json_util.dumps(list(projects))
    
    return projects_data, 200

# Route to get all projects with a specific line manager
@app.route('/projetcs_mng/<line_manager_id>', methods=['GET'])
def get_projects_line_manager(line_manager_id):
    line_manager = line_managers_collection.find_one({'_id': ObjectId(line_manager_id)})

    if line_manager is None:
        return jsonify({'error': 'Line manager not found'}), 404
    
    projects = projects_collection.find({'line_manager._id': ObjectId(line_manager_id)})

    # Use json_util for serialization
    projects_data = json_util.dumps(list(projects))

    return projects_data, 200


if __name__ == '__main__':
    insert_departments()
    insert_line_managers()
    app.run(debug=True)
