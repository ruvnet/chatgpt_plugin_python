In this tutorial, we will create a simple to-do list plugin using OpenAI's new plugin system. We will be using Python and deploying the plugin on Replit. The plugin will be authenticated using a service level authentication token and will allow users to create, view, and delete to-do items. We will also be defining an OpenAPI specification to match the endpoints defined in our plugin.

## ChatGPT Plugins

The ChatGPT plugin system enables language models to interact with external tools and services, providing access to information and enabling safe, constrained actions. Plugins can address challenges associated with large language models, including keeping up with recent events, accessing up-to-date information, and providing evidence-based references to enhance the model's responses.

Plugins also enable users to assess the trustworthiness of the model's output and double-check its accuracy. However, there are also risks associated with plugins, including the potential for harmful or unintended actions.

The development of the ChatGPT plugin platform has included several safeguards and red-teaming exercises to identify potential risks and inform safety-by-design mitigations. The deployment of access to plugins is being rolled out gradually, and researchers are encouraged to study safety risks and mitigations in this area. The ChatGPT plugin system has wide-ranging societal implications and may have a significant economic impact.

Learn more or signup here: [https://openai.com/blog/chatgpt-plugins](https://openai.com/blog/chatgpt-plugins)

## Prerequisites

To complete this tutorial, you will need the following:

* A basic understanding of Python
* A Replit account (you can sign up for free at replit.com)
* An OpenAI API key (you can sign up for free at openai.com)
* A text editor or the Replit IDE

## Replit

[Replit](https://replit.com/) is an online integrated development environment (IDE) that allows you to code in many programming languages, collaborate with others in real-time, and host and run your applications in the cloud. It's a great platform for beginners, educators, and professionals who want to quickly spin up a new project or prototype, or for teams who want to work together on code.

## Plugin Flow:

1. **Create a manifest file**: Host a manifest file at yourdomain.com/.well-known/manifest.json, containing metadata about the plugin, authentication details, and an OpenAPI spec for the exposed endpoints.
2. **Register the plugin in ChatGPT UI**: Install the plugin using the ChatGPT UI, providing the necessary OAuth 2 client\_id and client\_secret or API key for authentication.
3. **Users activate the plugin**: Users manually activate the plugin in the ChatGPT UI. During the alpha phase, developers can share their plugins with 15 additional users.
4. **Authentication**: If needed, users are redirected via OAuth to your plugin for authentication, and new accounts can be created.
5. **Users begin a conversation**: OpenAI injects a compact description of the plugin into the ChatGPT conversation, which remains invisible to users. The model may invoke an API call from the plugin if relevant, and the API results are incorporated into its response.
6. **API responses**: The model may include links from API calls in its response, displaying them as rich previews using the OpenGraph protocol.
7. **User location data**: The user's country and state are sent in the Plugin conversation header for relevant use cases like shopping, restaurants, or weather. Additional data sources require user opt-in via a consent screen.

## Step 1: Setting up the Plugin Manifest

The first step in creating a plugin is to define a manifest file. The manifest file provides information about the plugin, such as its name, description, and authentication method. The authentication method we will be using is a service level authentication token.

Create a new file named manifest.json in your project directory and add the following code:

    {
    #manifest.json
      "schema_version": "v1",
      "name_for_human": "TODO Plugin (service http)",
      "name_for_model": "todo",
      "description_for_human": "Plugin for managing a TODO list, you can add, remove and view your TODOs.",
      "description_for_model": "Plugin for managing a TODO list, you can add, remove and view your TODOs.",
      "auth": {
        "type": "service_http",
        "authorization_type": "bearer",
        "verification_tokens": {
          "openai": "<your-openai-token>"
        }
      },
       "api": {
        "type": "openapi",
        "url": "https://<your-replit-app-name>.<your-replit-username>.repl.co/openapi.yaml",
        "is_user_authenticated": false
      },
      "logo_url": "https://example.com/logo.png",
      "contact_email": "<your-email-address>",
      "legal_info_url": "http://www.example.com/legal"
    }

In this manifest file, we have specified the plugin's name and description, along with the authentication method and verification token. We have also specified the API type as OpenAPI and provided the URL for the OpenAPI specification. Replace the

    <your-openai-token>

placeholder with your OpenAI API key, and replace

    <your-replit-app-name>

and

    <your-replit-username>

placeholders with the name of your Replit app and your Replit username respectively. Finally, replace

    <your-email-address>

with your email address.

## Step 2. Update your pyproject.toml

    [tool.poetry]
    name = "chatgpt-plugin"
    version = "0.1.0"
    description = ""
    authors = ["@rUv"]
    
    [tool.poetry.dependencies]
    python = ">=3.10.0,<3.11"
    numpy = "^1.22.2"
    replit = "^3.2.4"
    Flask = "^2.2.0"
    urllib3 = "^1.26.12"
    openai = "^0.10.2"
    quart = "^0.14.1"
    quart-cors = "^0.3.1"
    
    [tool.poetry.dev-dependencies]
    debugpy = "^1.6.2"
    replit-python-lsp-server = {extras = ["yapf", "rope", "pyflakes"], version = "^1.5.9"}
    
    [build-system]
    requires = ["poetry-core>=1.0.0"]
    build-backend = "poetry.core.masonry.api"

## Install Quart &  Quart_cors

Go to the shell in Replit and run the following.

    pip install quart

Next install pip install quart-cors

    pip install quart-cors

## Step your OpenAi Keys in the secrets area.

Here are the instructions to set up these secrets variables in Replit:

1. Open your Replit project.
2. Click on the "Lock" icon on the left-hand sidebar to open the secrets panel.
3. Click the "New secret" button to create a new secret.
4. Enter a name for your secret (e.g. SERVICE\_AUTH\_KEY) and the value for the key.
5. Click "Add secret" to save the secret.

Example:

    import os
    
    SERVICE_AUTH_KEY = os.environ.get('SERVICE_AUTH_KEY')

Make sure to use the exact name you gave the secret when calling os.environ.get()

## Step 4: Creating the Python Endpoints

The next step is to create the Python endpoints that will handle requests from the user. We will be using the Quart web framework for this.

Create/edit a new file named main.py in your project directory and add the following code:

    
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
    

Now we can start our plugin server on Replit by clicking on the "Run" button. Once the server is running, we can test it out by sending requests to the plugin's endpoints using ChatGPT.

Congratulations, you have successfully built and deployed a Python based to-do plugin using OpenAI's new plugin system!