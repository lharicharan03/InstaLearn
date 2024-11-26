from flask import Flask, request, jsonify
from google.cloud import spanner
import uuid
from datetime import datetime
import vertexai
from vertexai.preview.generative_models import GenerativeModel, ChatSession

app = Flask(__name__)

# Initialize Vertex AI
PROJECT_ID = "e-learning-442804"
LOCATION = "us-central1"
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Initialize Cloud Spanner
spanner_client = spanner.Client()
instance = spanner_client.instance("elearning-new")
database = instance.database("elearning_db")

# Root route
@app.route('/', methods=['GET'])
def home():
    return "Welcome to the E-Learning Backend!", 200
#BACKUP
# Generate summary route
@app.route('/generate-summary', methods=['POST'])
def generate_summary():
    try:
        # Parse the JSON request
        data = request.json
        topic = data.get("topic")
        if not topic:
            return jsonify({"error": "Topic is required"}), 400

        # Construct the prompt
        prompt = f"Summarize the following topic for a beginner and ask some quiz questions on this: {topic}"

        # Use Vertex AI Generative Model to generate the summary
        model = GenerativeModel("gemini-1.0-pro")
        chat = model.start_chat()
        response = chat.send_message(prompt)
        summary = response.text

        # Generate a unique ID and current timestamp for the entry
        summary_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()

        # Save the summary to Cloud Spanner
        with database.batch() as batch:
            batch.insert(
                table="summaries",  # The table name
                columns=("id", "topic", "summary", "timestamp"),
                values=[(summary_id, topic, summary, timestamp)]
            )

        return jsonify({"summary": summary})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
