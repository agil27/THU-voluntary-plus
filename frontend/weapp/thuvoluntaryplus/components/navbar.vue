<template>
  <view class="cu-bar">
    <view class="cu-bar tabbar shadow bg-white foot">
      <view :class="{action: true, 'text-mauve': isIndex, 'text-gray': !isIndex}"
            @click="naviTo('index')">
        <view class="cuIcon-homefill"></view> 志愿广场
      </view>
      <view class="action text-gray add-action">
        <view class="cu-avatar round shadow add"
              :style="{'background-image': avatarUrl}"></view>
        {{personalinfo.name}}
      </view>
      <view :class="{action: true, 'text-mauve': isUserCenter, 'text-gray': !isUserCenter}">
        <view class="cuIcon-my"
              @click="naviTo('userCenter')">
          <view class="cu-tag badge"></view>
        </view>
        个人中心
      </view>
    </view>
  </view>
</template>

<script>
import {
  mapState,
  mapMutations
} from 'vuex'

export default {
  name: 'NavBar',
  props: {

  },

  data () {
    return {
      title: 'Hello',
    }
  },
  computed: {
    ...mapState(['curpage', 'personalinfo']),
    isIndex: function () {
      return (this.curpage === 'index')
    },
    isUserCenter: function () {
      return (this.curpage === 'userCenter')
    },
    avatarUrl: function () {
      //return 'url(' + this.personalinfo.avatarurl + ')'
      return 'url(https://overwatch.nosdn.127.net/1/assets/img/pages/heroes/list/roadhog.png)'
    },
  },
  onLoad () {

  },
  methods: {
    ...mapMutations(['changePageTo', 'setTitle']),
    naviTo: function (page) {
      this.changePageTo(page)
      if (page === 'index') {
        this.setTitle('志愿广场')
      }
      if (page === 'userCenter') {
        this.setTitle('个人中心')
      }
    }
  }
}
</script>

<style>
.box {
  margin: 20upx 0;
}

.box view.cu-bar {
  margin-top: 20upx;
}
</style>
