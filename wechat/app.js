App({
  onLaunch() {
    // 每次启动时清除登录状态
    this.clearLoginStatus();
  },

  onShow() {
    // 可选：每次回到小程序时也检查
    this.checkLoginStatus();
  },

  clearLoginStatus() {
    // 清除所有登录相关存储
    wx.removeStorageSync('access_token');
    wx.removeStorageSync('userInfo');
    console.log('登录状态已重置');
  },

  checkLoginStatus() {
    // 检查当前登录状态
    const token = wx.getStorageSync('access_token');
    if (!token) {
      console.log('当前未登录');
      // 可以在这里添加跳转到登录页的逻辑
      // wx.reLaunch({ url: '/pages/login/login' });
    }
  },

  globalData: {
    userInfo: null
  }
});