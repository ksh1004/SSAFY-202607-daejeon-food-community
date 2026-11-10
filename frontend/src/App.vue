<script setup>
import { RouterView } from 'vue-router'
import AppHeader from '@/components/common/AppHeader.vue'
import ChatWidget from '@/components/chat/ChatWidget.vue'
</script>

<template>
  <div class="app-layout">
    <AppHeader />

    <RouterView />

    <ChatWidget />
  </div>
</template>

<style scoped>
.app-layout {
  min-height: 100vh;
}
</style>
