<template>
  <div class="space-y-6">
    <!-- Top Greeting & Quick Actions -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold tracking-tight text-foreground">经营概览大盘 (Dashboard)</h1>
        <p class="text-xs text-muted-foreground mt-1">
          实时监控跨国商事委托转化、22 国客源分布及 24h 履约时效
        </p>
      </div>
      <div class="flex items-center gap-2">
        <router-link to="/crm">
          <Button size="sm">
            <Users class="mr-1.5 h-4 w-4" />
            处理待跟进线索 ({{ stats.new || 0 }})
          </Button>
        </router-link>
      </div>
    </div>

    <!-- 4 Key Metric Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <Card class="p-5 border-l-4 border-l-primary flex flex-col justify-between">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-muted-foreground uppercase tracking-wider">总涉外咨询案源</span>
          <Users class="h-4 w-4 text-primary" />
        </div>
        <div class="my-2">
          <span class="text-3xl font-extrabold tracking-tight text-foreground">{{ stats.total || 0 }}</span>
          <span class="text-xs text-emerald-600 font-medium ml-2">↑ 活跃增长</span>
        </div>
        <div class="text-[11px] text-muted-foreground">涵盖官网落地页与智能对话接待</div>
      </Card>

      <Card class="p-5 border-l-4 border-l-rose-500 bg-rose-500/5 flex flex-col justify-between">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-rose-700 dark:text-rose-400 uppercase tracking-wider">24h SLA 待跟进</span>
          <Clock class="h-4 w-4 text-rose-600" />
        </div>
        <div class="my-2">
          <span class="text-3xl font-extrabold tracking-tight text-rose-600">{{ stats.new || 0 }}</span>
          <span class="text-xs text-rose-600 font-medium ml-2">需尽快联系</span>
        </div>
        <div class="text-[11px] text-muted-foreground">超时将自动触发企业微信预警</div>
      </Card>

      <Card class="p-5 border-l-4 border-l-amber-500 flex flex-col justify-between">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-muted-foreground uppercase tracking-wider">在办案与方案评估</span>
          <Briefcase class="h-4 w-4 text-amber-600" />
        </div>
        <div class="my-2">
          <span class="text-3xl font-extrabold tracking-tight text-amber-600">
            {{ (stats.contacted || 0) + (stats.processing || 0) }}
          </span>
          <span class="text-xs text-amber-600 font-medium ml-2">方案推进中</span>
        </div>
        <div class="text-[11px] text-muted-foreground">已初联或律师团队正在评估事实证据</div>
      </Card>

      <Card class="p-5 border-l-4 border-l-emerald-500 bg-emerald-500/5 flex flex-col justify-between">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-emerald-700 dark:text-emerald-400 uppercase tracking-wider">成功转化签约 / 结案</span>
          <CheckCircle2 class="h-4 w-4 text-emerald-600" />
        </div>
        <div class="my-2">
          <span class="text-3xl font-extrabold tracking-tight text-emerald-600">{{ stats.closed || 0 }}</span>
          <span class="text-xs text-emerald-600 font-medium ml-2">转化达成</span>
        </div>
        <div class="text-[11px] text-muted-foreground">已完成正式法律服务合同签署</div>
      </Card>
    </div>

    <!-- 22 Global Countries & Business Breakdown -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Left: Geo Distribution (22 Countries) -->
      <Card class="lg:col-span-2 p-5 space-y-4">
        <div class="flex items-center justify-between border-b pb-3">
          <div class="flex items-center gap-2">
            <Globe class="h-4 w-4 text-primary" />
            <h3 class="font-bold text-sm text-foreground">出海客源重点法域分布 (22 重点国家/地区)</h3>
          </div>
          <span class="text-xs text-muted-foreground font-mono">Top Destinations</span>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
          <div
            v-for="country in topCountries"
            :key="country.name"
            class="rounded-lg border p-2.5 bg-muted/20 hover:bg-muted/40 transition-colors flex items-center justify-between"
          >
            <div>
              <div class="font-bold text-xs text-foreground">{{ country.flag }} {{ country.name }}</div>
              <div class="text-[10px] text-muted-foreground">{{ country.tz }}</div>
            </div>
            <Badge variant="outline" class="text-[10px] font-mono">{{ country.weight }}%</Badge>
          </div>
        </div>

        <div class="pt-2 text-xs text-muted-foreground flex items-center gap-1">
          <Info class="h-3.5 w-3.5 text-primary" />
          <span>覆盖北美（美加）、亚太（新马澳日韩）、欧洲（英法德意荷）等主要涉外商事法域。</span>
        </div>
      </Card>

      <!-- Right: Practice Areas & Conversion Funnel -->
      <Card class="p-5 space-y-4">
        <div class="flex items-center justify-between border-b pb-3">
          <div class="flex items-center gap-2">
            <Scale class="h-4 w-4 text-primary" />
            <h3 class="font-bold text-sm text-foreground">涉外业务构成</h3>
          </div>
        </div>

        <div class="space-y-3">
          <div v-for="item in practiceAreas" :key="item.label" class="space-y-1">
            <div class="flex justify-between text-xs font-medium">
              <span>{{ item.label }}</span>
              <span class="font-mono text-muted-foreground">{{ item.pct }}%</span>
            </div>
            <div class="h-2 w-full rounded-full bg-muted overflow-hidden">
              <div :class="cn('h-full rounded-full', item.color)" :style="{ width: `${item.pct}%` }" />
            </div>
          </div>
        </div>

        <div class="pt-4 border-t space-y-2">
          <div class="text-xs font-semibold text-foreground">获客转化工作流</div>
          <div class="text-xs space-y-1 text-muted-foreground">
            <div>1. 官网 / 智能接待采集线索入库 (100%)</div>
            <div>2. 24h SLA 律师响应初审 (92%)</div>
            <div>3. 事实核验与海牙材料审查 (65%)</div>
            <div>4. 正式签订法律服务协议 (38%)</div>
          </div>
        </div>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Card from '../../components/ui/Card.vue'
import Button from '../../components/ui/Button.vue'
import Badge from '../../components/ui/Badge.vue'
import api from '../../api/client'
import { cn } from '../../lib/utils'
import {
  Users,
  Clock,
  Briefcase,
  CheckCircle2,
  Globe,
  Scale,
  Info,
} from 'lucide-vue-next'

const stats = ref<any>({})

const topCountries = [
  { flag: '🇺🇸', name: '美国 (US)', tz: 'UTC-5/-8', weight: 32 },
  { flag: '🇸🇬', name: '新加坡 (SG)', tz: 'UTC+8', weight: 18 },
  { flag: '🇦🇺', name: '澳大利亚 (AU)', tz: 'UTC+10', weight: 14 },
  { flag: '🇬🇧', name: '英国 (UK)', tz: 'UTC+0', weight: 11 },
  { flag: '🇨🇦', name: '加拿大 (CA)', tz: 'UTC-5', weight: 8 },
  { flag: '🇭🇰', name: '中国香港 (HK)', tz: 'UTC+8', weight: 7 },
  { flag: '🇦🇪', name: '阿联酋 (UAE)', tz: 'UTC+4', weight: 5 },
  { flag: '🇩🇪', name: '德国 (DE)', tz: 'UTC+1', weight: 5 },
]

const practiceAreas = [
  { label: '跨境商业欠款追索 (Recovery)', pct: 45, color: 'bg-primary' },
  { label: '国际贸易仲裁与诉讼 (Trade)', pct: 30, color: 'bg-amber-500' },
  { label: '涉外遗产继承与家事 (Legacy)', pct: 25, color: 'bg-sky-500' },
]

onMounted(async () => {
  try {
    const res: any = await api.get('/admin/api/stats')
    stats.value = res || {}
  } catch (err) {
    console.error(err)
  }
})
</script>
