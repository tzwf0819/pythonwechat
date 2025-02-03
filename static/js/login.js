$(document).ready(function() {
    const apiUrl = 'http://127.0.0.1:8000';

    $('#login-form').on('submit', async function(event) {
        event.preventDefault();
        const loginUsername = $('#login-username').val();
        const loginPassword = $('#login-password').val();

        try {
            const response = await fetch(`${apiUrl}/auth/token`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: new URLSearchParams({
                    username: loginUsername,
                    password: loginPassword
                })
            });

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('access_token', data.access_token);
                window.location.href = '/static/home.html';
            } else {
                alert('Login failed: Incorrect username or password');
            }
        } catch (error) {
            alert(`Login failed: ${error.message}`);
        }
    });
});