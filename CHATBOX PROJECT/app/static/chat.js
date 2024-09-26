
    // Function to check for new messages
    function checkForNewMessages() {
        fetch('{{ url_for("check_new_messages", course_id=course_id, last_chat_id=chats[-1].chat_id if chats else 0) }}')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.new_messages) {
                    location.reload();  // Reload the page if new messages are found
                }
            })
            .catch(error => {
                console.error('Error fetching new messages:', error);
            });
    }

    // Set an interval to check for new messages every 5 seconds
    setInterval(checkForNewMessages, 5000);  // Changed to 5 seconds

    document.addEventListener('DOMContentLoaded', function () {
        var chatWindow = document.getElementById('chat-window');
        if (chatWindow) {
            chatWindow.scrollTop = chatWindow.scrollHeight;  // Scroll to the bottom
        }
    });
