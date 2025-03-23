// app.js
App({
  onLaunch() {
    // 展示本地存储能力
    const logs = wx.getStorageSync('logs') || []
    logs.unshift(Date.now())
    wx.setStorageSync('logs', logs)

    // 登录
    wx.login({
      success: res => {
        // 发送 res.code 到后台换取 openId, sessionKey, unionId
        wx.request({
          url: 'http://your-backend-url/wechat-login',
          method: 'POST',
          data: {
            code: res.code
          },
          success: (response) => {
            if (response.statusCode === 200) {
              const { access_token } = response.data
              // 保存 access_token 到本地存储
              wx.setStorageSync('access_token', access_token)
            } else {
              console.error('微信登录失败:', response.data)
            }
          },
          fail: (error) => {
            console.error('请求失败:', error)
          }
        })
      }
    })
  },
  globalData: {
    userInfo: null
  }
})