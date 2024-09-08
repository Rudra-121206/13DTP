document.addEventListener('DOMContentLoaded', function() {
    // Get the notification container
    const notificationContainer = document.querySelector('.notification-container');

    if (notificationContainer) {
        // Add 'show' class to trigger the fade-in effect
        setTimeout(() => {
            notificationContainer.classList.add('show');
        }, 100); // Small delay to trigger the transition

        // Automatically hide notifications after 5 seconds
        setTimeout(() => {
            notificationContainer.classList.remove('show');
        }, 5000); // 5 seconds

        // Close button logic (if you want to add a close button to the notifications)
        const closeBtn = document.querySelector('.close-btn');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                notificationContainer.classList.remove('show');
            });
        }
    }
});
