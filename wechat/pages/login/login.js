// pages/login/login.js
Page({
  data: {
    userInfo: null
  },

  onLoad() {
    // 页面加载时可以进行一些初始化操作
  },

  bindGetUserInfo(e) {
    if (e.detail.userInfo) {
      this.setData({
        userInfo: e.detail.userInfo
      });
      this.loginWithWechat(e.detail.encryptedData, e.detail.iv);
    } else {
      wx.showToast({
        title: '您需要授权登录',
        icon: 'none'
      });
    }
  },

  async loginWithWechat(encryptedData, iv) {
    try {
        const res = await wx.login();
        if (res.code) {
            const x = "your_x_value"; // 这里填入你需要的 x 的值
            wx.request({
                url: `https://yidasoftware.xyz/wechat-login?x=${x}`, // 添加 x 参数到 URL
                method: 'POST',
                data: {
                    code: res.code,
                    encrypted_data: encryptedData,
                    iv: iv
                },
                header: {
                    'content-type': 'application/json'
                },
                success: (response) => {
                    if (response.statusCode === 200) {
                        const { access_token } = response.data;
                        // 保存 access_token 到本地存储
                        wx.setStorageSync('access_token', access_token);
                        // 登录成功后跳转到首页
                        wx.switchTab({
                            url: '/pages/index/index'
                        });
                    } else {
                        console.error('微信登录失败:', response.data);
                    }
                },
                fail: (error) => {
                    console.error('请求失败:', error);
                }
            });
        }
    } catch (error) {
        console.error('登录失败:', error);
    }
}
});