Page({
  data: {
    isLoggedIn: false,
    userInfo: {
      nickName: '',
      avatarUrl: 'https://yida-wechat.obs.cn-north-4.myhuaweicloud.com/avatar/default.png',
      phone: '',
      address: ''
    },
    // 新增独立输入状态
    inputValues: {
      nickName: '',
      phone: '',
      address: ''
    }
  },

  onLoad() {
    this.checkLoginStatus();
  },

  checkLoginStatus() {
    const token = wx.getStorageSync('access_token');
    const userInfo = wx.getStorageSync('userInfo') || {};
    
    this.setData({
      isLoggedIn: !!token,
      'userInfo.nickName': userInfo.nickName || '',
      'userInfo.avatarUrl': userInfo.avatarUrl || 'https://yida-wechat.obs.cn-north-4.myhuaweicloud.com/avatar/default.png',
      'userInfo.phone': userInfo.phone || '',
      'userInfo.address': userInfo.address || ''
    });
  },

  onGetUserInfo(e) {
    if (e.detail.userInfo) {
      wx.showLoading({ title: '登录中...', mask: true });
      
      wx.login({
        success: (loginRes) => {
          wx.request({
            url: 'https://yidasoftware.xyz/auth/wechat-login',
            method: 'POST',
            data: {
              code: loginRes.code,
              encryptedData: e.detail.encryptedData,
              iv: e.detail.iv
            },
            success: (res) => {
              wx.hideLoading();
              if (res.data?.code === 200) {
                const serverData = res.data.data;
                const userInfo = {
                  nickName: serverData.nickName || e.detail.userInfo.nickName,
                  avatarUrl: serverData.avatarUrl || e.detail.userInfo.avatarUrl,
                  phone: serverData.phone || '',
                  address: serverData.address || ''
                };
                
                wx.setStorageSync('access_token', serverData.access_token);
                wx.setStorageSync('userInfo', userInfo);
                
                this.setData({
                  isLoggedIn: true,
                  userInfo: userInfo
                });
              }
            }
          });
        }
      });
    }
  },

  // 获取用户资料
  fetchUserProfile() {
    wx.request({
      url: 'https://yidasoftware.xyz/auth/users/me',
      method: 'GET',
      header: {
        'Authorization': 'Bearer ' + wx.getStorageSync('access_token')
      },
      success: (res) => {
        if (res.data) {
          this.setData({
            nickName: res.data.full_name || '',
            phoneNumber: res.data.phone || '',
            address: res.data.address || '',
            avatarUrl: res.data.avatar_url || '',
            userInfo: {
              nickName: res.data.full_name,
              avatarUrl: res.data.avatar_url
            }
          });
          wx.setStorageSync('userInfo', res.data);
        }
      }
    });
  },

  // 微信登录
  

  // 手机号处理（微信授权或手动输入）
  getPhoneNumber(e) {
    if (e.detail.code) {
      wx.request({
        url: 'https://yidasoftware.xyz/auth/decrypt-phone',
        method: 'POST',
        data: { code: e.detail.code },
        header: {
          'Authorization': 'Bearer ' + wx.getStorageSync('access_token')
        },
        success: (res) => {
          if (res.data.phone) {
            this.setData({ phoneNumber: res.data.phone });
          }
        }
      });
    }
  },

  // 地址选择（微信或手动输入）
  chooseAddress() {
    wx.chooseAddress({
      success: (res) => {
        const address = `${res.provinceName}${res.cityName}${res.countyName}${res.detailInfo}`;
        this.setData({ address });
      },
      fail: () => {
        // 用户拒绝或取消，可以手动输入
        wx.showToast({ title: '请在下方手动输入地址', icon: 'none' });
      }
    });
  },

  // 保存资料到后端
  saveProfile() {
    const { nickName, phone, address } = this.data.inputValues;
    const postData = {
      nickName: nickName || this.data.userInfo.nickName,
      phone: phone || this.data.userInfo.phone,
      address: address || this.data.userInfo.address
    };
    
    console.log('提交数据:', JSON.stringify(postData));
    
    wx.request({
      url: 'https://yidasoftware.xyz/auth/update-profile',
      method: 'POST',
      data: postData,
      header: {
        'Authorization': 'Bearer ' + wx.getStorageSync('access_token')
      },
      success: (res) => {
        console.log('完整响应:', JSON.stringify(res.data));
        if (res.data?.success) {
          // 强制刷新本地数据
          const newData = {
            nickName: res.data.user_info.nickName,
            phone: res.data.user_info.phone,
            address: res.data.user_info.address,
            avatarUrl: this.data.userInfo.avatarUrl
          };
          
          wx.setStorageSync('userInfo', newData);
          this.setData({
            userInfo: newData,
            'inputValues.nickName': '',
            'inputValues.phone': '',
            'inputValues.address': ''
          });
          
          wx.showToast({ title: '更新成功' });
        }
      }
    });
  },

  // 手动输入处理
  updateNickName(e) {
    this.setData({
      'inputValues.nickName': e.detail.value
    });
    console.log('当前输入的用户名:', e.detail.value);
  },

  updatePhoneNumber(e) {
    this.setData({
      'inputValues.phone': e.detail.value
    });
  },
});