<template>
  <div class="face-capture">
    <div v-if="!preview">
      <video ref="video" class="video-box" v-show="streaming"></video>
      <div class="controls">
        <button type="button" v-if="!streaming" @click="startCamera">开启摄像头拍照</button>
        <button type="button" v-else @click="capture">拍照</button>
      </div>
    </div>
    <div v-else>
      <img :src="preview" class="preview-img" />
      <br />
      <button type="button" @click="reset">重拍</button>
    </div>
    <div class="upload-box">
      <label>或上传照片: </label>
      <input type="file" accept="image/*" @change="onFileChange" />
    </div>
    <canvas ref="canvas" style="display: none;"></canvas>
  </div>
</template>

<script setup>
import { ref, onBeforeUnmount } from 'vue'

const emit = defineEmits(['capture'])
const video = ref(null)
const canvas = ref(null)
const streaming = ref(false)
const preview = ref(null)
let stream = null

const startCamera = async () => {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: true })
    video.value.srcObject = stream
    video.value.play()
    streaming.value = true
  } catch (err) {
    alert("无法打开摄像头: " + err.message)
  }
}

const capture = () => {
  const c = canvas.value
  const v = video.value
  c.width = v.videoWidth
  c.height = v.videoHeight
  c.getContext('2d').drawImage(v, 0, 0)
  
  c.toBlob((blob) => {
    emit('capture', blob)
    preview.value = URL.createObjectURL(blob)
    stopCamera()
  }, 'image/jpeg')
}

const stopCamera = () => {
  if (stream) {
    stream.getTracks().forEach(track => track.stop())
  }
  streaming.value = false
}

const reset = () => {
  preview.value = null
  startCamera()
}

const onFileChange = (e) => {
  const file = e.target.files[0]
  if (file) {
    emit('capture', file)
    preview.value = URL.createObjectURL(file)
  }
}

onBeforeUnmount(() => {
  stopCamera()
})
</script>

<style scoped>
.face-capture { border: 1px solid #ddd; padding: 10px; border-radius: 8px; text-align: center; }
.video-box { width: 100%; max-width: 320px; margin: 0 auto; display: block; }
.preview-img { width: 100%; max-width: 200px; }
.upload-box { margin-top: 10px; }
.controls { margin: 10px 0; }
</style>
