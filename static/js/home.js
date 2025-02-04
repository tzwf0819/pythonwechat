$(document).ready(function() {
    const apiUrl = 'http://127.0.0.1:8000';

    // 检查是否有 token
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/login';
        return;
    }

    // 获取用户信息
    async function getUserInfo() {
        try {
            const response = await fetch(`${apiUrl}/auth/users/me/`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error('Token expired or invalid');
            }

            const data = await response.json();
            console.log(data);
            // 可以在页面上显示用户信息，例如：
            $('body').append(`<p>Welcome, ${data.username}!</p>`);
        } catch (error) {
            console.error(error);
            localStorage.removeItem('access_token');
            window.location.href = '/login';
        }
    }

    getUserInfo();

    // 注销按钮事件处理
    $('#logout-btn').on('click', function() {
        localStorage.removeItem('access_token');
        window.location.href = '/login';
    });
});