from flask import Flask, request, jsonify, render_template_string
import requests
import json

app = Flask(__name__)

# Replace with your OpenRouter API Key
OPENROUTER_API_KEY = "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"

# HTML + JavaScript UI for Chatbot
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NAFON AI</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script defer src="https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"></script>
    <style>
        body.dark { background: #343541; color: #eaeaea; transition: background 0.3s, color 0.3s; }
        body { background: #f7f7f8; color: #333; transition: background 0.3s, color 0.3s; }
        .chat-container { max-width: 700px; width: 100%; padding: 20px; background: white; border-radius: 10px; box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.1); }
        .message-box { background: #ececf1; padding: 12px; border-radius: 8px; margin-bottom: 10px; }
        .user-message { background: #007bff; color: white; align-self: flex-end; }
        .ai-message { background: #f3f4f6; color: black; align-self: flex-start; }
        .button-glow { transition: all 0.3s ease-in-out; }
        .button-glow:hover { box-shadow: 0px 0px 15px rgba(59, 130, 246, 0.7); transform: scale(1.05); }
    </style>
</head>
<body class="flex flex-col items-center justify-center min-h-screen transition-all px-4">
    
    <button onclick="toggleDarkMode()" class="absolute top-5 right-5 px-4 py-2 bg-gray-700 text-white rounded-lg shadow-lg hover:bg-gray-600 transition button-glow">🌙 Toggle Dark Mode</button>
    
    <h1 class="text-3xl font-bold mb-6">🤖 NAFON AI</h1>
    
    <div id="chatbox" class="chat-container flex flex-col">
        <div id="chatOutput" class="flex flex-col space-y-2 mb-4"></div>
        <div class="flex items-center gap-2">
            <textarea id="userInput" class="flex-grow p-3 border rounded-xl dark:bg-gray-700 dark:text-white focus:ring-2 focus:ring-blue-500" placeholder="Type your questions NAFON is waiting..."></textarea>
            <button onclick="getAIResponse()" class="p-3 bg-blue-600 text-white rounded-lg shadow-md hover:bg-blue-700 transition button-glow">🚀 Send</button>
        </div>
    </div>
    
    <script>
        function toggleDarkMode() {
            document.body.classList.toggle("dark");
        }
        
        async function getAIResponse() {
            const userInput = document.getElementById("userInput").value;
            if (!userInput.trim()) return;
            
            const chatOutput = document.getElementById("chatOutput");
            
            const userMessage = document.createElement("div");
            userMessage.className = "message-box user-message";
            userMessage.innerText = userInput;
            chatOutput.appendChild(userMessage);
            
            document.getElementById("userInput").value = "";
            
            const aiMessage = document.createElement("div");
            aiMessage.className = "message-box ai-message";
            aiMessage.innerText = "Thinking...";
            chatOutput.appendChild(aiMessage);
            
            try {
                const response = await fetch("/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ message: userInput })
                });
                const data = await response.json();
                aiMessage.innerText = data.response || "Error!";
            } catch (error) {
                aiMessage.innerText = "Error fetching response!";
            }
        }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_PAGE)

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "").strip()

    if not user_message:
        return jsonify({"response": "Please enter a message."})

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "model": "openai/gpt-4o",
                "messages": [{"role": "user", "content": user_message}]
            })
        )

        api_response = response.json()

        if response.status_code == 200 and "choices" in api_response:
            ai_reply = api_response["choices"][0]["message"]["content"]
        else:
            ai_reply = "Error processing the response."

    except Exception as e:
        ai_reply = f"Request failed: {str(e)}"

    return jsonify({"response": ai_reply})

if __name__ == "__main__":
    app.run(debug=True)
