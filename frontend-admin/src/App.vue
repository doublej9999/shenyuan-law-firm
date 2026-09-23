<template>
  <router-view />
  <Toaster position="top-right" richColors closeButton />
</template>

<script setup lang="ts">
import { Toaster } from 'vue-sonner'
</script>
