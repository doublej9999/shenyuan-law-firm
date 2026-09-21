<template>
  <div class="space-y-4">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <div>
        <h1 class="text-xl font-bold tracking-tight text-foreground">涉外法律智能调研 (Legal Research Studio)</h1>
        <p class="text-xs text-muted-foreground mt-0.5">
          深度检索涉外商事法规与实务要点库，一键生成当事人案情评估备忘录 (AI Legal Memo)
        </p>
      </div>
    </div>

    <!-- Search Section -->
    <Card class="p-4 space-y-3">
      <div class="text-xs font-semibold text-foreground">涉外法务知识库语义检索 (Legal KB)</div>
      <div class="flex flex-col sm:flex-row gap-2">
        <Input
          v-model="searchQ"
          placeholder="检索关键词，例如：涉外继承 海牙认证、美国判决执行时效、提单电放欺诈..."
          class="flex-1"
          @keyup.enter="handleSearch"
        />
        <Button :loading="searching" @click="handleSearch">
          <Search class="mr-1.5 h-4 w-4" />
          检索知识库
        </Button>
      </div>

      <!-- Search Results -->
      <div v-if="searchResults.length > 0" class="pt-3 space-y-3 border-t">
        <div class="text-xs font-medium text-muted-foreground">找到 {{ searchResults.length }} 条关联法条与实务要点：</div>
        <div
          v-for="(item, idx) in searchResults"
          :key="idx"
          class="p-3 rounded-lg border bg-muted/20 hover:bg-muted/40 transition-colors space-y-1.5"
        >
          <div class="flex items-center justify-between">
            <span class="font-bold text-xs text-primary flex items-center gap-1.5">
              <FileText class="h-3.5 w-3.5" />
              {{ item.title }}
            </span>
            <Badge variant="outline" class="text-[10px]">{{ item.category }}</Badge>
          </div>
          <p class="text-xs text-foreground/80 leading-relaxed font-sans">
            {{ item.snippet }}
          </p>
          <div class="text-[10px] text-muted-foreground font-mono">
            知识库原文件: {{ item.file_path }}
          </div>
        </div>
      </div>
    </Card>

    <!-- AI Legal Memo Generator -->
    <Card class="p-4 space-y-4">
      <div class="flex items-center justify-between border-b pb-2">
        <div>
          <div class="text-sm font-bold text-foreground">生成涉外法律评估备忘录 (AI Legal Memo)</div>
          <div class="text-xs text-muted-foreground">基于当事人事实快速产出涉外管辖权、准据法与执行策略意见</div>
        </div>
        <Button v-if="memoResult" variant="outline" size="sm" class="text-xs" @click="copyMemo">
          <Copy class="mr-1 h-3 w-3" />
          复制备忘录草稿
        </Button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Input Form -->
        <div class="space-y-3">
          <div>
            <label class="text-xs font-semibold text-muted-foreground mb-1 block">争议法律事项</label>
            <Input v-model="memoForm.matter" placeholder="例如: 中美跨境商事借款追偿 / 涉外不动产继承" />
          </div>
          <div>
            <label class="text-xs font-semibold text-muted-foreground mb-1 block">案件事实与当事人陈述摘要</label>
            <textarea
              v-model="memoForm.facts"
              rows="6"
              placeholder="录入当事人诉求、争议主体国籍、交易履行地、主要证据等事实..."
              class="w-full rounded-md border border-input bg-background p-2.5 text-xs outline-none focus:ring-1 focus:ring-primary leading-relaxed"
            />
          </div>
          <Button :loading="generatingMemo" class="w-full" @click="handleGenerateMemo">
            <Sparkles class="mr-1.5 h-4 w-4" />
            生成涉外法律意见备忘录
          </Button>
        </div>

        <!-- Result Display -->
        <div class="rounded-lg border bg-muted/15 p-4 flex flex-col justify-between">
          <div v-if="memoResult" class="space-y-3">
            <div class="font-bold text-sm text-primary">{{ memoResult.title }}</div>
            <div class="space-y-2 text-xs">
              <div class="font-semibold text-foreground">一、 涉外管辖权与法律适用评估：</div>
              <p class="text-foreground/80 whitespace-pre-wrap leading-relaxed bg-background p-3 rounded border">
                {{ memoResult.analysis }}
              </p>
              <div class="font-semibold text-foreground pt-1">二、 律师推荐维权策略与步骤：</div>
              <p class="text-foreground/80 whitespace-pre-wrap leading-relaxed bg-background p-3 rounded border">
                {{ memoResult.strategy }}
              </p>
            </div>
          </div>
          <div v-else class="flex flex-col items-center justify-center h-full text-center text-muted-foreground/60 text-xs py-12">
            <BookOpen class="h-8 w-8 opacity-30 mb-2" />
            <span>在左侧录入案件要素，系统将规范化生成涉外法律评估备忘录</span>
          </div>
        </div>
      </div>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Card from '../../components/ui/Card.vue'
import Button from '../../components/ui/Button.vue'
import Input from '../../components/ui/Input.vue'
import Badge from '../../components/ui/Badge.vue'
import api from '../../api/client'
import { Search, FileText, Sparkles, Copy, BookOpen } from 'lucide-vue-next'

const searchQ = ref('')
const searching = ref(false)
const searchResults = ref<any[]>([])

const memoForm = ref({ matter: '', facts: '' })
const generatingMemo = ref(false)
const memoResult = ref<any>(null)

const handleSearch = async () => {
  if (!searchQ.value) return
  searching.value = true
  try {
    const res: any = await api.get('/admin/api/research/search', { params: { q: searchQ.value } })
    searchResults.value = res || []
  } catch (err) {
    console.error(err)
  } finally {
    searching.value = false
  }
}

const handleGenerateMemo = async () => {
  if (!memoForm.value.matter) return
  generatingMemo.value = true
  try {
    const res: any = await api.post('/admin/api/research/memo', memoForm.value)
    memoResult.value = res
  } catch (err) {
    console.error(err)
  } finally {
    generatingMemo.value = false
  }
}

const copyMemo = () => {
  if (!memoResult.value) return
  const text = `${memoResult.value.title}\n\n${memoResult.value.analysis}\n\n${memoResult.value.strategy}`
  navigator.clipboard.writeText(text)
  alert('备忘录已复制到剪贴板！')
}
</script>
