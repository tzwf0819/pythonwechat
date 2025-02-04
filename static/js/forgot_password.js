$(document).ready(function() {
    const apiUrl = 'http://127.0.0.1:8000';

    $('#forgot-password-form').on('submit', async function(event) {
        event.preventDefault();
        const username = $('#forgot-password-username').val();
        const fullname = $('#forgot-password-fullname').val();
        const email = $('#forgot-password-email').val();
        const newPassword = $('#forgot-password-newpassword').val();
        const confirmNewPassword = $('#forgot-password-confirmnewpassword').val();

        if (newPassword !== confirmNewPassword) {
            alert("New Password and Confirm New Password do not match!");
            return;
        }

        try {
            const response = await fetch(`${apiUrl}/auth/forgot-password`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username: username,
                    full_name: fullname,
                    email: email,
                    new_password: newPassword
                })
            });

            if (response.ok) {
                alert('Password reset successful! Please login with your new password.');
                window.location.href = '/login';
            } else {
                const errorData = await response.json();
                alert(`Password reset failed: ${errorData.detail}`);
            }
        } catch (error) {
            alert(`Password reset failed: ${error.message}`);
        }
    });
});