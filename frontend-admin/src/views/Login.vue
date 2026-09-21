<template>
  <div class="flex min-h-screen w-screen items-center justify-center bg-muted/30 p-4">
    <Card class="w-full max-w-md p-8 shadow-2xl border bg-card">
      <!-- Brand Header -->
      <div class="flex flex-col items-center text-center space-y-2 mb-6">
        <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-primary text-white font-bold text-xl shadow-md">
          申
        </div>
        <h1 class="text-xl font-bold tracking-tight text-foreground">深远涉外律师事务所</h1>
        <p class="text-xs text-muted-foreground">
          Shenyuan Legal · 涉外商事线索中枢与管理后台
        </p>
      </div>

      <!-- Login Form -->
      <form class="space-y-4" @submit.prevent="handleLogin">
        <div class="space-y-1.5">
          <label class="text-xs font-semibold text-foreground">管理访问令牌 (ADMIN TOKEN)</label>
          <div class="relative">
            <Input
              v-model="token"
              type="password"
              placeholder="请输入 ADMIN_TOKEN 或安全访问密钥"
              class="pr-10"
              autofocus
            />
            <div class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none text-muted-foreground">
              <Key class="h-4 w-4" />
            </div>
          </div>
        </div>

        <Button class="w-full" :loading="loading" type="submit">
          安全登录业务中台
        </Button>
      </form>

      <!-- Footer Info -->
      <div class="mt-8 pt-4 border-t text-center text-[11px] text-muted-foreground space-y-1">
        <div>数据直连 Supabase Postgres · 端到端鉴权保护</div>
        <div class="text-muted-foreground/60">© {{ new Date().getFullYear() }} Shenyuan Law Firm. All rights reserved.</div>
      </div>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import Card from '../components/ui/Card.vue'
import Button from '../components/ui/Button.vue'
import Input from '../components/ui/Input.vue'
import { Key } from 'lucide-vue-next'

const router = useRouter()
const token = ref('')
const loading = ref(false)

const handleLogin = () => {
  if (!token.value) {
    alert('请输入管理访问 Token')
    return
  }
  loading.value = true
  localStorage.setItem('shenyuan_admin_token', token.value)
  setTimeout(() => {
    loading.value = false
    router.push('/dashboard')
  }, 400)
}
</script>
