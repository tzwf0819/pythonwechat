Page({
  data: {
    userInfo: null,
  },

  bindGetUserInfo(e) {
    if (e.detail.userInfo) {
      this.setData({
        userInfo: e.detail.userInfo,
      });
      this.login();
    } else {
      wx.showToast({
        title: '您需要授权登录',
        icon: 'none',
      });
    }
  },

  async login() {
    try {
      const res = await wx.login({
        success: res => {
          if (res.code) {
            // 将 code 发送到后端服务器
            wx.request({
              url: 'https://127.0.0.1:8000/wechat-login', // 替换为你的后端登录接口
              method: 'POST',
              data: {
                code: res.code,
              },
              success: res => {
                if (res.data.access_token) {
                  // 登录成功，保存 token 到本地
                  wx.setStorageSync('token', res.data.access_token);
                  wx.showToast({
                    title: '登录成功',
                  });
                  // 跳转到首页或其他页面
                  wx.navigateTo({
                    url: '/pages/home/home',
                  });
                } else {
                  wx.showToast({
                    title: '登录失败',
                    icon: 'none',
                  });
                }
              },
              fail: err => {
                wx.showToast({
                  title: '请求失败',
                  icon: 'none',
                });
              }
            });
          } else {
            console.log('登录失败！' + res.errMsg);
          }
        }
      });
    } catch (error) {
      console.error('登录过程中发生错误', error);
    }
  }
});