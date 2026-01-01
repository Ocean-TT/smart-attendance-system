<template>
  <div class="clock-widget">
    <div class="time">{{ currentTime }}</div>
    <div class="date">{{ currentDate }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const currentTime = ref('')
const currentDate = ref('')

const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('zh-CN', { hour12: false })
  currentDate.value = now.toLocaleDateString('zh-CN', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric', 
    weekday: 'long' 
  })
}

let timer = null
onMounted(() => {
  updateTime()
  timer = setInterval(updateTime, 1000)
})

onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.clock-widget {
  text-align: right;
  color: #2c3e50;
}
.time {
  font-size: 1.8rem;
  font-weight: bold;
  font-family: 'Courier New', Courier, monospace;
  line-height: 1;
}
.date {
  font-size: 0.9rem;
  opacity: 0.7;
  margin-top: 4px;
}
</style>
