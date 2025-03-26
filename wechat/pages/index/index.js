const defaultAvatarUrl = 'https://mmbiz.qpic.cn/mmbiz/icTdbqWNOwNRna42FI242Lcia07jQodd2FJGIYQfG0LAJGFxM4FbnQP6yfMxBgJ0F3YRqJCJ1aPAK2dQagdusBZg/0';

Page({
  data: {
    motto: 'Hello World',
    userInfo: {
      avatarUrl: defaultAvatarUrl,
      nickName: '',
    },
    hasUserInfo: false,
    canIUseGetUserProfile: wx.canIUse('getUserProfile'),
    canIUseNicknameComp: wx.canIUse('input.type.nickname'),
    access_token: '',
    full_name: '',
    // 新增默认头像和用户名
    defaultAvatarUrl: defaultAvatarUrl,
    defaultNickName: '默认用户名'
  },
  bindViewTap() {
    wx.navigateTo({
      url: '../logs/logs'
    })
  },
  onChooseAvatar(e) {
    const { avatarUrl } = e.detail;
    const { nickName } = this.data.userInfo;
    this.setData({
      "userInfo.avatarUrl": avatarUrl,
      hasUserInfo: nickName && avatarUrl && avatarUrl !== defaultAvatarUrl,
    });
    // 调用更新用户信息接口
    this.updateUserInfo();
  },
  onInputChange(e) {
    const nickName = e.detail.value;
    const { avatarUrl } = this.data.userInfo;
    this.setData({
      "userInfo.nickName": nickName,
      hasUserInfo: nickName && avatarUrl && avatarUrl !== defaultAvatarUrl,
    });
    // 调用更新用户信息接口
    this.updateUserInfo();
  },
  // 新增按钮点击事件处理函数
  onLoginButtonTap() {
    wx.getUserProfile({
      desc: '展示用户信息', 
      success: (res) => {
        this.setData({
          userInfo: res.userInfo,
          hasUserInfo: true
        });

        wx.login({
          success: (loginRes) => {
            if (loginRes.code) {
              const data = {
                nickName: res.userInfo.nickName,
                avatarUrl: res.userInfo.avatarUrl,
                code: loginRes.code
              };

              wx.request({
                url: 'https://yidasoftware.xyz/wechat-login', 
                method: 'POST',
                data: data,
                header: {
                  'content-type': 'application/json'
                },
                success: (res) => {
                  if (res.statusCode === 200) {
                    const { access_token, full_name, avatar_url } = res.data;
                    wx.setStorageSync('access_token', access_token);
                    wx.setStorageSync('full_name', full_name);
                    wx.setStorageSync('avatar_url', avatar_url);
                    this.setData({
                      access_token,
                      "userInfo.nickName": full_name,
                      "userInfo.avatarUrl": avatar_url,
                      hasUserInfo: true
                    });
                    wx.showToast({
                      title: '登录成功',
                      icon: 'success'
                    });
                    wx.navigateBack(); 
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
      fail: (error) => {
        console.error('wx.getUserProfile failed:', error);
        wx.showToast({
          title: '获取用户信息失败',
          icon: 'none'
        });
      }
    });
  },
  // 新增更新用户信息方法
  updateUserInfo() {
    const { userInfo, access_token } = this.data;
    wx.request({
      url: 'https://yidasoftware.xyz/update-profile',
      method: 'POST',
      header: {
        'Authorization': `Bearer ${access_token}`,
        'content-type': 'application/json'
      },
      data: {
        full_name: userInfo.nickName,
        avatar_url: userInfo.avatarUrl
      },
      success: (res) => {
        if (res.statusCode === 200) {
          wx.showToast({
            title: '更新成功',
            icon: 'success'
          });
        } else {
          wx.showToast({
            title: '更新失败',
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
  },
  // 页面加载时检查登录状态
  onLoad() {
    const access_token = wx.getStorageSync('access_token');
    if (access_token) {
      // 已登录，获取用户信息
      wx.request({
        url: 'https://yidasoftware.xyz/users/me/',
        method: 'GET',
        header: {
          'Authorization': `Bearer ${access_token}`
        },
        success: (res) => {
          if (res.statusCode === 200) {
            const { full_name, avatar_url } = res.data;
            this.setData({
              "userInfo.nickName": full_name,
              "userInfo.avatarUrl": avatar_url,
              hasUserInfo: true
            });
          }
        },
        fail: (error) => {
          console.error('获取用户信息失败:', error);
        }
      });
    }
  }
});