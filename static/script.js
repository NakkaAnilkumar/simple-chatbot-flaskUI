
// Get HTML elements
const chatBox = document.getElementById("chat-box");

const userInput = document.getElementById("user-input");

const sendButton = document.getElementById("send-btn");


// Display messages
function addMessage(message, sender) {

    const messageDiv = document.createElement("div");

    messageDiv.classList.add("message", sender);

    const avatar = document.createElement("div");

    avatar.classList.add("avatar");

    avatar.textContent = sender === "user" ? "👤" : "🤖";

    const content = document.createElement("div");

    content.classList.add("message-content");

    content.textContent = message;

    messageDiv.appendChild(avatar);

    messageDiv.appendChild(content);

    chatBox.appendChild(messageDiv);

    chatBox.scrollTop = chatBox.scrollHeight;

    return content;
}


// Send message to Flask
async function sendMessage() {

    const message = userInput.value.trim();

    if (!message || sendButton.disabled) {
        return;
    }

    // Display user message
    addMessage(message, "user");

    userInput.value = "";

    sendButton.disabled = true;

    sendButton.textContent = "Thinking...";

    // Loading message
    const loadingMessage = addMessage(
        "Qwen is generating a response...",
        "bot"
    );

    try {

        // Send HTTP POST request
        const response = await fetch("/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: message
            })

        });

        // Convert response into JSON
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.response || "Request failed.");
        }

        // Display AI response
        loadingMessage.textContent = data.response;

    }

    catch (error) {

        loadingMessage.textContent = "Error: " + error.message;

        console.error(error);

    }

    finally {

        sendButton.disabled = false;

        sendButton.textContent = "Send ➤";

        userInput.focus();

        chatBox.scrollTop = chatBox.scrollHeight;

    }

}


// Send message using Enter key
userInput.addEventListener("keydown", function(event) {

    if (event.key === "Enter") {
        sendMessage();
    }

});


// Clear chat history
async function clearChat() {

    try {

        const response = await fetch("/clear", {
            method: "POST"
        });

        if (!response.ok) {
            throw new Error("Unable to clear chat.");
        }

        chatBox.innerHTML = "";

        addMessage(
            "Chat cleared! How can I help you?",
            "bot"
        );

    }

    catch (error) {

        alert(error.message);

    }

}
