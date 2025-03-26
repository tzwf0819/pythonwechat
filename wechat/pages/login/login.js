// wechat/pages/login/login.js
Page({
  data: {
    userInfo: null
  },

  onLoad() {
    // Check if the user is already logged in
    const accessToken = wx.getStorageSync('access_token');
    if (accessToken) {
      wx.navigateBack(); // Navigate back to the previous page if already logged in
    }
  },

  bindGetUserInfo(e) {
    const userInfo = e.detail.userInfo;
    if (userInfo) {
      this.setData({ userInfo });

      // Get the code from wx.login
      wx.login({
        success: (loginRes) => {
          if (loginRes.code) {
            // Send user info and code to backend
            wx.request({
              url: 'https://yidasoftware.xyz/wechat-login',
              method: 'POST',
              data: {
                nickName: userInfo.nickName,
                avatarUrl: userInfo.avatarUrl,
                code: loginRes.code
              },
              success: (res) => {
                if (res.statusCode === 200) {
                  const { access_token } = res.data;
                  wx.setStorageSync('access_token', access_token);
                  wx.showToast({
                    title: '登录成功',
                    icon: 'success'
                  });
                  wx.navigateBack(); // Navigate back to the previous page
                } else {
                  wx.showToast({
                    title: '登录失败',
                    icon: 'none'
                  });
                }
              },
              fail: (error) => {
                console.error('请求失败:', error);
                wx.showToast({
                  title: '请求失败',
                  icon: 'none'
                });
              }
            });
          } else {
            wx.showToast({
              title: '获取登录码失败',
              icon: 'none'
            });
          }
        },
        fail: (error) => {
          console.error('wx.login failed:', error);
          wx.showToast({
            title: '登录失败',
            icon: 'none'
          });
        }
      });
    } else {
      wx.showToast({
        title: '获取用户信息失败',
        icon: 'none'
      });
    }
  }
});