<template>
  <div class="space-y-4">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <div>
        <h1 class="text-xl font-bold tracking-tight text-foreground">出海营销获客矩阵 (Marketing Matrix)</h1>
        <p class="text-xs text-muted-foreground mt-0.5">
          为中资出海企业与海外高净值客户定制 7 大传播渠道素材与 UTM 全链路追踪
        </p>
      </div>
      <div class="flex items-center gap-2">
        <Button variant="outline" size="sm" @click="exportMarkdownBundle" :disabled="!bundle">
          <Download class="mr-1.5 h-3.5 w-3.5" />
          下载完整 Markdown 素材包
        </Button>
      </div>
    </div>

    <!-- Generator Control Bar -->
    <Card class="p-4">
      <div class="space-y-3">
        <label class="text-xs font-semibold text-foreground">营销主题 / 核心痛点</label>
        <div class="flex flex-col sm:flex-row gap-2">
          <Input
            v-model="topic"
            placeholder="例如：中国民商事生效判决在加州/纽约州的承认与执行指引、涉外继承海牙认证..."
            class="flex-1"
            @keyup.enter="generate"
          />
          <Button :loading="generating" @click="generate">
            <Sparkles class="mr-1.5 h-4 w-4" />
            一键生成全渠道素材包
          </Button>
        </div>
        <!-- Quick Topic Chips -->
        <div class="flex items-center gap-1.5 flex-wrap pt-1 text-[11px] text-muted-foreground">
          <span>推荐选题：</span>
          <button
            v-for="chip in quickTopics"
            :key="chip"
            class="rounded bg-muted px-2 py-0.5 hover:bg-primary/10 hover:text-primary transition-colors cursor-pointer"
            @click="setTopic(chip)"
          >
            {{ chip }}
          </button>
        </div>
      </div>
    </Card>

    <!-- Marketing Generated Cards Matrix -->
    <div v-if="bundle" class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- 1. WeChat Official Account & Moments -->
      <Card class="p-4 space-y-3">
        <div class="flex items-center justify-between border-b pb-2">
          <div class="flex items-center gap-2">
            <span class="text-emerald-600 font-bold text-sm">🟢 微信公号 / 朋友圈深度文案</span>
            <Badge variant="outline" class="text-[10px]">中企出海法务</Badge>
          </div>
          <Button variant="ghost" size="sm" class="text-xs text-primary" @click="copyText(bundle.wechat_post)">
            <Copy class="mr-1 h-3 w-3" />
            复制
          </Button>
        </div>
        <p class="text-xs text-foreground/90 whitespace-pre-wrap leading-relaxed bg-muted/20 p-3 rounded-lg border font-sans">
          {{ bundle.wechat_post }}
        </p>
      </Card>

      <!-- 2. LinkedIn English Post -->
      <Card class="p-4 space-y-3">
        <div class="flex items-center justify-between border-b pb-2">
          <div class="flex items-center gap-2">
            <span class="text-sky-600 font-bold text-sm">🔵 LinkedIn 领英专栏 (English)</span>
            <Badge variant="outline" class="text-[10px]">跨国投资总监</Badge>
          </div>
          <Button variant="ghost" size="sm" class="text-xs text-primary" @click="copyText(bundle.linkedin_post)">
            <Copy class="mr-1 h-3 w-3" />
            复制
          </Button>
        </div>
        <p class="text-xs text-foreground/90 whitespace-pre-wrap leading-relaxed bg-muted/20 p-3 rounded-lg border font-mono">
          {{ bundle.linkedin_post }}
        </p>
      </Card>

      <!-- 3. Target Audience & Global Tags -->
      <Card class="p-4 space-y-3">
        <div class="flex items-center justify-between border-b pb-2">
          <span class="font-bold text-sm text-foreground">🎯 受众画像与标签体系</span>
        </div>
        <div class="space-y-2 text-xs">
          <div>
            <span class="text-muted-foreground">精准受众群体：</span>
            <span class="font-semibold text-foreground ml-1">{{ bundle.target_audience }}</span>
          </div>
          <div class="pt-2">
            <span class="text-muted-foreground block mb-1.5">出海全网传播标签：</span>
            <div class="flex flex-wrap gap-1.5">
              <Badge v-for="tag in bundle.suggested_tags" :key="tag" variant="secondary">
                {{ tag }}
              </Badge>
            </div>
          </div>
        </div>
      </Card>

      <!-- 4. UTM Tracking Link Generator -->
      <Card class="p-4 space-y-3">
        <div class="flex items-center justify-between border-b pb-2">
          <span class="font-bold text-sm text-foreground">🔗 全渠道 UTM 追踪归因</span>
        </div>
        <div class="space-y-2 text-xs">
          <div class="p-2 rounded bg-muted/40 font-mono text-[11px] truncate">
            https://shenyuanlegal.com/services/recovery?utm_source=linkedin&utm_medium=social&utm_campaign={{ encodeURIComponent(topic || 'marketing') }}
          </div>
          <div class="flex justify-between items-center text-[11px] text-muted-foreground pt-1">
            <span>支持微信、LinkedIn、X、Facebook 多通道统一追踪</span>
            <Button variant="ghost" size="sm" class="text-xs" @click="copyText(`https://shenyuanlegal.com/services/recovery?utm_source=linkedin&utm_medium=social&utm_campaign=${encodeURIComponent(topic || 'marketing')}`)">
              复制 UTM 链接
            </Button>
          </div>
        </div>
      </Card>
    </div>

    <!-- Empty State -->
    <Card v-else class="p-12 text-center text-muted-foreground border-dashed">
      <Sparkles class="mx-auto h-8 w-8 opacity-40 mb-2" />
      <p class="text-xs">输入上方涉外法律主题并点击一键生成，即可获取 7 大海外渠道素材包</p>
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
import { Sparkles, Copy, Download } from 'lucide-vue-next'

const topic = ref('')
const generating = ref(false)
const bundle = ref<any>(null)

const quickTopics = [
  '中美跨境商业欠款追收实操指引',
  '涉外遗嘱与海牙公证附加证明书审查',
  '国际仲裁裁决在中国内地法院的承认与执行',
  '外贸信用证欺诈争议与禁令保全',
]

const setTopic = (t: string) => {
  topic.value = t
  generate()
}

const generate = async () => {
  if (!topic.value) return
  generating.value = true
  try {
    const res: any = await api.get('/admin/api/marketing/generate', { params: { topic: topic.value } })
    bundle.value = res
  } catch (err) {
    console.error(err)
  } finally {
    generating.value = false
  }
}

const copyText = (text: string) => {
  navigator.clipboard.writeText(text)
  alert('已成功复制到剪贴板！')
}

const exportMarkdownBundle = () => {
  if (!bundle.value) return
  const md = `# 深远涉外营销素材包 · ${bundle.value.topic}

## 目标受众画像
${bundle.value.target_audience}

## 微信公众号 / 朋友圈文案
${bundle.value.wechat_post}

## LinkedIn 领英专栏 (English)
${bundle.value.linkedin_post}

## 推荐标签
${bundle.value.suggested_tags.join(' ')}
`
  const blob = new Blob([md], { type: 'text/markdown;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `shenyuan-marketing-${Date.now()}.md`
  a.click()
}
</script>
