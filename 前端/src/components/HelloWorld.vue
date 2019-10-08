<template>
  <div class="hello">
    <van-tabs @change="activeChange">
        <van-tab title="选择图片">
            <div style="margin: 20px 0">
                <span>请选择图片</span>
                <div class="images-show">
                    <van-uploader :after-read="afterRead" v-model="fileList" multiple :preview-full-image="false">
                    <div class="upload">
                        <van-icon name="plus" />
                    </div>
                    </van-uploader>
                </div>

                <!-- <img :src="imgData" alt="" id="image"> -->
                <canvas id="myCanvas" width="28px" height="28px" style="display:none"></canvas>
            </div>
        </van-tab>
        <van-tab title="手动绘制">
            <div class="shouxie">
                <canvas id="myCanvas2" width="280px" height="280px" style="border: 1px solid gray"></canvas>
                <van-button type="warning" @click="clear">清空</van-button>
            </div>

            <van-popup v-model="shouxieShow" custom-style="padding: 20px;">{{ shouxieTip }}</van-popup>
        </van-tab>
    </van-tabs>

    <van-button type="info" @click="submit">提交</van-button>
    <div class="result">
      <van-circle
        v-model="currentRate"
        :rate="currentRate"
        :speed="1000"
        :text="text"
        layer-color="#f5f5f5"
      />
    </div>

    <van-popup
        v-model="show"
        position="bottom"
        :style="{ height: '80%' }"
    >
        <van-divider :style="{ color: '#1989fa', borderColor: '#1989fa', padding: '0 16px' }">识别结果</van-divider>
        <!-- <van-card
            num="2"
            thumb="https://img.yzcdn.cn/vant/t-thirt.jpg"
        /> -->
        <van-grid :column-num="3">
            <van-grid-item
                v-for="(item, key) in results"
                :key="key"
                :icon="item.image"
                :text="item.result"
            />
        </van-grid>
    </van-popup>
  </div>
</template>

<script>
import Vue from "vue";
import { Uploader, Icon, Button, Divider, Circle, Popup, Grid, GridItem, Tabs, Tab } from "vant";
import axios from 'axios';
import qs from 'qs';

Vue.use(Uploader);
Vue.use(Icon);
Vue.use(Button);
Vue.use(Divider);
Vue.use(Circle);
Vue.use(Popup);
Vue.use(Grid);
Vue.use(GridItem);
Vue.use(Tabs).use(Tab);

const HOST = "http://34.80.197.3:8000";

export default {
  name: "HelloWorld",
  data() {
    return {
      currentRate: 0,
      rate: 0,
      fileList: [],
      imgDatas: [],
      results: [],
      show: false,
      shouxieShow: false,
      shouxieTip: '',
      active: 0,
      firstActive: true
    };
  },

  computed: {
    text() {
      return this.currentRate.toFixed(0) + "%";
    }
  },

  mounted() {
      
  },

  methods: {
    afterRead() {
      console.log(this.fileList);
    },

    activeChange (index) {
        if (this.firstActive) {
            this.$nextTick(()=> {
                setTimeout(() => {
                    this.canvasInit();
                });
            });
        }
        this.firstActive = false;
        this.active = index;
    },

    submit () {
        this.currentRate = 0;
        this.imgDatas = [];
        this.results = [];

        if (this.active == 0) this.analyse();
        else this.analyse1();
        
    },

    // 分析图片内容
    analyse() {
      let percent = 80.0 / this.fileList.length;

      let c = document.getElementById("myCanvas");
      let ctx = c.getContext("2d");

      for (let i = 0; i < this.fileList.length; i++) {
        let image = new Image();
        image.src = this.fileList[i].content;

        // 清空画布
        c.height = c.height;
        ctx.drawImage(image, 0, 0);
        let imgData = ctx.getImageData(0, 0, c.width, c.height).data;

        let res = [];

        for (let i = 0; i < 28; i++) {
          for (let j = 0; j < 28; j++) {
            let index = i * image.width * 4 + j * 4;

            // 灰度转换
            let gray =
              imgData[index] * 0.299 +
              imgData[index + 1] * 0.587 +
              imgData[index + 2] * 0.114;
            gray /= 255.0;
            res.push(gray);
          }
        }

        this.imgDatas.push(res.join());
        this.currentRate += percent;
      }

     let params = {
         array: this.imgDatas
     };
      axios.post(HOST + '/analyse', qs.stringify(params)).then((res) => {
          res = res.data;
          for (let i = 0;i < res.data.length;i++) {
              this.results.push({
                image: this.fileList[i].content,
                result: String(res.data[i])
              });
          }

          this.show = true;
          this.currentRate = 100;
      }).catch((err) => { 
          alert("网络请求失败");
          console.log(err);
      });
    },

    /**
     * 分析2
     */
    analyse1 () {
        let canvas = document.getElementById("myCanvas2");
        let ctx = canvas.getContext("2d");

        let data = canvas.toDataURL("image/jpeg");
        console.log(data);
        data = data.substring(data.indexOf(",") + 1);
        data = {
            image: data,
            words_type: 'number'
        };

        this.currentRate = 50;
        // 
        axios.post(HOST + '/bd', qs.stringify(data), {headers: {
            'content-type': 'application/x-www-form-urlencoded'
        }}).then((res) => {
            res = res.data;
            let word = res.words_result[0].words;
            if (res.words_result_num == 0 || isNaN(word)) {
                this.shouxieTip = "暂未识别到数字";
            } else {
                this.shouxieTip = `识别为: ${word}`;
            }

            this.currentRate = 100;
            this.shouxieShow = true;
        }).catch((err) => {
            alert("网络请求失败");
            console.log(err);
        });
    },

    /**
     * 手写
     */
    canvasInit () {
        let c = document.getElementById("myCanvas2");
        let ctx = c.getContext("2d");
        
        this.clear();

        let bounding = c.getBoundingClientRect();

        document.addEventListener("touchstart", (e) => {
            ctx.beginPath();
            
            ctx.moveTo(e.targetTouches[0].clientX - bounding.left, e.targetTouches[0].clientY - bounding.top);
        });

        c.addEventListener("touchmove", (e) => {
            ctx.lineTo(e.targetTouches[0].clientX - bounding.left, e.targetTouches[0].clientY - bounding.top);
            ctx.stroke();
        }, false);

        c.addEventListener("touchend", (e) => {
            ctx.closePath();
        });
    },

    /**
     * 清空手写板
     */
    clear () {
        let c = document.getElementById("myCanvas2");
        let ctx = c.getContext("2d");
        c.width = c.width;
        ctx.fillStyle = "#fff";
        ctx.fillRect(0, 0, c.width, c.height);
        ctx.strokeStyle = "#000";
    }
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.hello {
  display: flex;
  flex-direction: column;
  justify-content: space-around;
  align-items: center;

  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
}

.result {
  display: block;
  width: 80%;
  /* flex-direction: column;
    justify-content: space-around;
    align-items: flex-start; */
}

.images-show {
  margin-top: 20px;
  width: 270px;

  display: flex;
  justify-content: center;
  align-items: center;
}

h1,
h2 {
  font-weight: normal;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}

.upload {
  position: relative;
  display: -webkit-box;
  display: -webkit-flex;
  display: flex;
  -webkit-box-orient: vertical;
  -webkit-box-direction: normal;
  -webkit-flex-direction: column;
  flex-direction: column;
  -webkit-box-align: center;
  -webkit-align-items: center;
  align-items: center;
  -webkit-box-pack: center;
  -webkit-justify-content: center;
  justify-content: center;
  box-sizing: border-box;
  width: 80px;
  height: 80px;
  margin: 0 8px 8px 0;
  background-color: #fff;
  border: 1px dashed #e5e5e5;
}

.shouxie {
    display: flex;
    flex-direction: column;
}

.shouxie-style {
    padding: 20px;
}
</style>
