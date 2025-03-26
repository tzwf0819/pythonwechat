App({
  onLaunch() {
      // 检查是否已经登录
      const accessToken = wx.getStorageSync('access_token');
      if (accessToken) {
          // 已经登录，可以在这里添加一些逻辑，比如跳转到主页等
      }
  },
  globalData: {
      userInfo: null
  }
});