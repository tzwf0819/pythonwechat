$(document).ready(function() {
    const apiUrl = 'http://127.0.0.1:8080';

    // 处理微信扫码登录回调
    function handleWechatCallback() {
        const urlParams = new URLSearchParams(window.location.search);
        const accessToken = urlParams.get('access_token');
        
        if (accessToken) {
            localStorage.setItem('access_token', accessToken);
            // 清除URL参数并跳转
            window.history.replaceState({}, '', '/login');
            window.location.href = '/home';
        }
    }

    // 初始化微信扫码登录按钮
    function initWechatLogin() {
        $('#wechat-login-btn').click(function() {
            window.open(
                '/auth/wechat/qrcode',
                'wechat-login',
                'width=500,height=600'
            );
        });
    }

    // 监听来自扫码窗口的消息
    window.addEventListener('message', (event) => {
        if (event.data.type === 'wechat-login') {
            localStorage.setItem('access_token', event.data.token);
            window.location.href = '/home';
        }
    });

    // 标准表单登录处理
    $('#login-form').on('submit', async function(event) {
        event.preventDefault();
        const username = $('#login-username').val();
        const password = $('#login-password').val();

        try {
            const response = await fetch(`${apiUrl}/auth/token`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: new URLSearchParams({
                    username: username,
                    password: password
                })
            });

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('access_token', data.access_token);
                window.location.href = '/home';
            } else {
                const error = await response.json();
                alert(`登录失败: ${error.detail}`);
            }
        } catch (error) {
            alert(`网络错误: ${error.message}`);
        }
    });

    // 初始化
    handleWechatCallback();
    initWechatLogin();
});