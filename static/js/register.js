$(document).ready(function() {
    const apiUrl = 'http://127.0.0.1:8000';

    $('#register-form').on('submit', async function(event) {
        event.preventDefault();
        const registerUsername = $('#register-username').val();
        const registerEmail = $('#register-email').val();
        const registerPassword = $('#register-password').val();

        try {
            const response = await fetch(`${apiUrl}/auth/users/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username: registerUsername,
                    email: registerEmail,
                    password: registerPassword
                })
            });

            if (response.ok) {
                alert('Registration successful! Please login.');
                window.location.href = '/static/login.html';
            } else {
                const errorData = await response.json();
                alert(`Registration failed: ${errorData.detail}`);
            }
        } catch (error) {
            alert(`Registration failed: ${error.message}`);
        }
    });
});