# Import required modules
import json
import os
from quart import Quart, request, jsonify
from quart_cors import cors

# Create a Quart app and enable CORS
app = Quart(__name__)
app = cors(app)

# Retrieve the service authentication key from the environment variables
SERVICE_AUTH_KEY = os.environ.get("SERVICE_AUTH_KEY")
# Initialize an empty dictionary to store todos
TODOS = {}

# Add a before_request hook to check for authorization header
@app.before_request
def auth_required():
    # Get the authorization header from the request
    auth_header = request.headers.get("Authorization")
    # Check if the header is missing or incorrect, and return an error if needed
    if not auth_header or auth_header != f"Bearer {SERVICE_AUTH_KEY}":
        return jsonify({"error": "Unauthorized"}), 401

# Define a route to get todos for a specific username
@app.route("/todos/<string:username>", methods=["GET"])
async def get_todos(username):
    # Get todos for the given username, or return an empty list if not found
    todos = TODOS.get(username, [])
    return jsonify(todos)

# Define a route to add a todo for a specific username
@app.route("/todos/<string:username>", methods=["POST"])
async def add_todo(username):
    # Get the request data as JSON
    request_data = await request.get_json()
    # Get the todo from the request data, or use an empty string if not found
    todo = request_data.get("todo", "")
    # Add the todo to the todos dictionary
    TODOS.setdefault(username, []).append(todo)
    return jsonify({"status": "success"})

# Define a route to delete a todo for a specific username
@app.route("/todos/<string:username>", methods=["DELETE"])
async def delete_todo(username):
    # Get the request data as JSON
    request_data = await request.get_json()
    # Get the todo index from the request data, or use -1 if not found
    todo_idx = request_data.get("todo_idx", -1)
    # Check if the index is valid, and delete the todo if it is
    if 0 <= todo_idx < len(TODOS.get(username, [])):
        TODOS[username].pop(todo_idx)
    return jsonify({"status": "success"})

# Run the app
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
