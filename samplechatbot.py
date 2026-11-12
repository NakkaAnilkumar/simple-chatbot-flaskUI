
from flask import Flask, render_template, request, jsonify
import requests
import webbrowser
from threading import Timer

app = Flask(__name__)

# Ollama API URL
OLLAMA_URL = "http://localhost:11434/api/chat"

# Qwen LLM model
MODEL_NAME = "qwen2.5:3b"

# Conversation history
messages = [
    {
        "role": "system",
        "content": "You are a helpful AI assistant. Answer questions clearly and in simple English."
    }
]


# Home page
@app.route("/")
def home():
    return render_template("index.html")


# Chat API
@app.route("/chat", methods=["POST"])
def chat():

    try:

        # Get user message
        data = request.get_json(silent=True) or {}
        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({
                "response": "Please enter a message."
            }), 400

        # Add user message
        messages.append({
            "role": "user",
            "content": user_message
        })

        # Prepare Ollama payload
        payload = {
            "model": MODEL_NAME,
            "messages": messages,
            "stream": False
        }

        # Send request to Ollama
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=180
        )

        response.raise_for_status()

        # Extract AI response
        ai_response = response.json()["message"]["content"]

        # Add assistant response
        messages.append({
            "role": "assistant",
            "content": ai_response
        })

        # Maintain recent conversation history
        if len(messages) > 13:
            messages[:] = [messages[0]] + messages[-12:]

        return jsonify({
            "response": ai_response
        })

    except requests.exceptions.ConnectionError:

        # Remove unanswered user message
        if len(messages) > 1 and messages[-1]["role"] == "user":
            messages.pop()

        return jsonify({
            "response": "Ollama is not running. Please start Ollama."
        }), 503

    except requests.exceptions.Timeout:

        if len(messages) > 1 and messages[-1]["role"] == "user":
            messages.pop()

        return jsonify({
            "response": "Request timed out. Please try again."
        }), 504

    except requests.exceptions.RequestException as e:

        if len(messages) > 1 and messages[-1]["role"] == "user":
            messages.pop()

        return jsonify({
            "response": f"Ollama API error: {str(e)}"
        }), 500

    except Exception as e:

        return jsonify({
            "response": f"Something went wrong: {str(e)}"
        }), 500


# Clear chat
@app.route("/clear", methods=["POST"])
def clear_chat():

    messages.clear()

    messages.append({
        "role": "system",
        "content": "You are a helpful AI assistant. Answer questions clearly and in simple English."
    })

    return jsonify({
        "message": "Chat history cleared successfully!"
    })


# Run Flask application
if __name__ == "__main__":

    # Automatically open browser
    Timer(
        2,
        lambda: webbrowser.open("http://127.0.0.1:5000")
    ).start()

    # Start Flask server
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
        use_reloader=False
    )
