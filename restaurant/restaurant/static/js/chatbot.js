// JavaScript for Chatbot Widget

function toggleChat() {
    var widget = document.getElementById('chat-widget');
    widget.style.display = widget.style.display === 'none' ? 'block' : 'none';
}

function sendMessage() {
    var userInput = document.getElementById('user-input').value;
    document.getElementById('chat-container').innerHTML += '<p>You: ' + userInput + '</p>';

    fetch('http://localhost:5005/model/parse', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: userInput })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Rasa Response:', data);
        if (data && data.length > 0 && data[0].text) {
            document.getElementById('chat-container').innerHTML += '<p>Bot: ' + data[0].text + '</p>';
        } else {
            document.getElementById('chat-container').innerHTML += '<p>Bot: No response from Rasa</p>';
        }
    })
    .catch(error => {
        console.error('Error sending message to Rasa:', error);
        document.getElementById('chat-container').innerHTML += '<p>Bot: Error sending message to Rasa</p>';
    });
}
