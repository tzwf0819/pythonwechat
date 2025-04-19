// wechat/pages/login/login.js
Page({
  data: {
    userInfo: null
  },

  onLoad(options) {
    if (options.scene === 'web_login') {
        this.handleWebLogin();
    } else {
        // 小程序内直接登录
        this.handleMiniProgramLogin();
    }
  },
handleWebLogin() {
  wx.login({
      success: (loginRes) => {
          if (loginRes.code) {
              wx.request({
                  url: 'https://yidasoftware.xyz/auth/wechat-login-for-web',
                  method: 'POST',
                  data: {
                      code: loginRes.code
                  },
                  success: (res) => {
                      if (res.statusCode === 200) {
                          const { access_token } = res.data;
                          wx.setStorageSync('access_token', access_token);
                          window.parent.postMessage({ type: 'wechat-login', token: access_token }, '*');
                          wx.showToast({
                              title: '登录成功',
                              icon: 'success'
                          });
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
},

// 处理小程序内直接登录
handleMiniProgramLogin() {
  wx.login({
      success: (loginRes) => {
          if (loginRes.code) {
              wx.request({
                  url: 'https://yidasoftware.xyz/auth/wechat-login-in-miniprogram',
                  method: 'POST',
                  data: {
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
                          // 跳转到小程序内主页等操作
                          wx.switchTab({
                              url: '/pages/home/home'
                          });
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
}

// 根据不同场景调用不同登录方法


});
