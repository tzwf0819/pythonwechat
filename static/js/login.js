$(document).ready(function() {
    const apiUrl = 'http://127.0.0.1:8000';

    // 新增：处理微信扫码登录回调
    function handleWechatCallback() {
        const urlParams = new URLSearchParams(window.location.search);
        const accessToken = urlParams.get('access_token');
        
        if (accessToken) {
            localStorage.setItem('access_token', accessToken);
            window.location.href = '/home';  // 清除URL参数
        }
    }

    // 初始化时检查是否是回调
    handleWechatCallback();

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
                window.location.href = '/home';
            } else {
                const errorData = await response.json();
                alert(`Login failed: ${errorData.detail}`);
            }
        } catch (error) {
            alert(`Login failed: ${error.message}`);
        }
    });
});