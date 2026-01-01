<template>
  <div class="face-capture">
    <div class="action-row">
      <button type="button" class="btn" @click="toggleCamera">{{ streaming ? '取消扫描' : '开启人脸识别' }}</button>
      <button type="button" v-if="allowUpload" class="btn" @click="triggerFile">上传照片</button>
      <input ref="fileInput" type="file" accept="image/*" @change="onFileChange" style="display:none" />
    </div>

    <!-- 人脸识别弹窗/遮罩 -->
    <div v-if="streaming" class="face-modal-overlay">
      <div class="face-modal-content">
        <div class="camera-container">
          <video ref="video" autoplay playsinline class="video-stream"></video>
          <!-- 扫描动画层 -->
          <div class="scan-overlay">
            <div class="scan-line"></div>
            <div class="face-guide"></div>
          </div>
          <div class="scan-tips">请将面部置于框内</div>
        </div>
        <div class="modal-actions">
          <button type="button" class="btn primary large" @click="capture">立即识别</button>
          <button type="button" class="btn" @click="stopCamera">取消</button>
        </div>
      </div>
    </div>

    <div v-if="preview" class="preview-wrap">
      <img :src="preview" class="preview-img" />
      <div class="controls">
        <button type="button" class="btn" @click="reset">重拍/重选</button>
        <button type="button" class="btn primary" @click="confirmPreview">使用此照片</button>
      </div>
    </div>
    <canvas ref="canvas" style="display:none"></canvas>
  </div>
</template>

<script setup>
import { ref, onBeforeUnmount, nextTick } from 'vue'

const props = defineProps({
  allowUpload: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['capture'])

const video = ref(null)
const canvas = ref(null)
const fileInput = ref(null)
const streaming = ref(false)
const preview = ref(null)
let stream = null

const toggleCamera = async () => { if (streaming.value) stopCamera(); else await startCamera() }

const startCamera = async () => {
  try {
    if (stream) stopCamera()
    stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } })
    streaming.value = true
    await nextTick()
    if (video.value) { 
      video.value.srcObject = stream
      await video.value.play().catch(()=>{})
    }
  } catch (err) { 
    console.error('无法打开摄像头', err)
    streaming.value = false
  }
}

const stopCamera = () => {
  if (stream && stream.getTracks) stream.getTracks().forEach(t=>t.stop())
  stream = null; streaming.value = false; if (video.value) video.value.srcObject = null
}

const capture = () => {
  const v = video.value, c = canvas.value
  if (!v || !c) return
  const w = v.videoWidth || 320, h = v.videoHeight || 240
  if (w===0 || h===0) return
  c.width = w; c.height = h
  c.getContext('2d').drawImage(v,0,0,w,h)
  c.toBlob(blob => {
    if (!blob) return
    if (preview.value) URL.revokeObjectURL(preview.value)
    preview.value = URL.createObjectURL(blob)
    stopCamera()
  }, 'image/jpeg', 0.9)
}

const triggerFile = () => { if (fileInput.value) fileInput.value.click() }

const onFileChange = (e) => {
  const file = e.target.files && e.target.files[0]; if (!file) return
  if (preview.value) URL.revokeObjectURL(preview.value)
  preview.value = URL.createObjectURL(file); e.target.value = ''
  if (streaming.value) stopCamera()
}

const reset = () => { if (preview.value) { URL.revokeObjectURL(preview.value); preview.value = null } }

const confirmPreview = async () => {
  if (!preview.value) return
  try {
    const res = await fetch(preview.value)
    const blob = await res.blob()
    emit('capture', blob)
  } catch (err) { console.error(err) }
}

onBeforeUnmount(()=>{ stopCamera(); if (preview.value) URL.revokeObjectURL(preview.value) })
</script>

<style scoped>
.face-capture { padding: 6px 2px; background: transparent; }
.action-row{display:flex;gap:8px;justify-content:center;margin-bottom:8px}
.btn{padding:8px 12px;border-radius:6px;border:1px solid #d7d7d7;background:#fff;cursor:pointer}
.btn.primary{background:#1e90ff;color:#fff;border-color:#1e90ff}
.btn.large{padding:12px 30px;font-weight:bold;font-size:1.1rem}

/* 人脸识别弹窗样式 */
.face-modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.face-modal-content {
  background: #1a1a1a;
  padding: 2rem;
  border-radius: 20px;
  text-align: center;
  box-shadow: 0 0 30px rgba(30,144,255,0.3);
}

.camera-container {
  position: relative;
  width: 400px;
  height: 400px;
  border-radius: 50%;
  overflow: hidden;
  border: 4px solid #1e90ff;
  margin-bottom: 2rem;
  background: #000;
}

.video-stream {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.scan-overlay {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  pointer-events: none;
}

.scan-line {
  position: absolute;
  width: 100%;
  height: 4px;
  background: linear-gradient(to bottom, transparent, #1e90ff, transparent);
  box-shadow: 0 0 15px #1e90ff;
  animation: scan 3s infinite linear;
}

.face-guide {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  width: 260px;
  height: 320px;
  border: 2px dashed rgba(30,144,255,0.5);
  border-radius: 50% 50% 45% 45%;
}

.scan-tips {
  position: absolute;
  bottom: 40px;
  width: 100%;
  color: #1e90ff;
  font-weight: bold;
  text-shadow: 0 2px 4px rgba(0,0,0,0.5);
}

@keyframes scan {
  0% { top: 0; }
  100% { top: 100%; }
}

.modal-actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.preview-wrap{display:flex;flex-direction:column;align-items:center;gap:8px}
.preview-img{width:320px;height:auto;border-radius:6px;object-fit:cover}
.controls{display:flex;gap:8px}
</style>