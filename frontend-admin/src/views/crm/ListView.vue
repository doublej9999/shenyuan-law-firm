<template>
  <div class="space-y-4">
    <!-- Top Stats Row -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <Card class="p-4 flex items-center justify-between">
        <div>
          <div class="text-2xl font-bold tracking-tight text-foreground">{{ stats.total || 0 }}</div>
          <div class="text-xs text-muted-foreground mt-0.5">总涉外咨询案源</div>
        </div>
        <div class="p-2.5 rounded-lg bg-primary/10 text-primary">
          <Users class="h-5 w-5" />
        </div>
      </Card>
      <Card class="p-4 flex items-center justify-between border-rose-500/20 bg-rose-500/5">
        <div>
          <div class="text-2xl font-bold tracking-tight text-rose-600">{{ stats.new || 0 }}</div>
          <div class="text-xs text-muted-foreground mt-0.5">待首次跟进 (24h SLA)</div>
        </div>
        <div class="p-2.5 rounded-lg bg-rose-500/10 text-rose-600">
          <Clock class="h-5 w-5" />
        </div>
      </Card>
      <Card class="p-4 flex items-center justify-between">
        <div>
          <div class="text-2xl font-bold tracking-tight text-amber-600">{{ (stats.contacted || 0) + (stats.processing || 0) }}</div>
          <div class="text-xs text-muted-foreground mt-0.5">已初联 / 推进中</div>
        </div>
        <div class="p-2.5 rounded-lg bg-amber-500/10 text-amber-600">
          <Briefcase class="h-5 w-5" />
        </div>
      </Card>
      <Card class="p-4 flex items-center justify-between border-emerald-500/20 bg-emerald-500/5">
        <div>
          <div class="text-2xl font-bold tracking-tight text-emerald-600">{{ stats.closed || 0 }}</div>
          <div class="text-xs text-muted-foreground mt-0.5">成功转化签约 / 结案</div>
        </div>
        <div class="p-2.5 rounded-lg bg-emerald-500/10 text-emerald-600">
          <CheckCircle2 class="h-5 w-5" />
        </div>
      </Card>
    </div>

    <!-- Toolbar & View Switcher -->
    <Card class="p-3">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-3">
        <!-- Search & Filter Controls -->
        <div class="flex flex-wrap items-center gap-2">
          <div class="w-40">
            <Select v-model="filterStatus" @update:model-value="fetchData">
              <option value="">全部跟进阶段</option>
              <option value="new">新线索 (待初审)</option>
              <option value="contacted">已初审联系</option>
              <option value="processing">方案推进中</option>
              <option value="closed">已结案</option>
            </Select>
          </div>
          <div class="relative w-64">
            <Input
              v-model="searchQuery"
              placeholder="搜索客户、电话、诉求摘要..."
              @keyup.enter="fetchData"
            />
          </div>
          <Button size="sm" @click="fetchData">
            <Search class="mr-1.5 h-3.5 w-3.5" />
            查询
          </Button>
          <Button variant="outline" size="sm" @click="resetFilter">重置</Button>
        </div>

        <!-- View Switcher (Table vs Kanban) & Export -->
        <div class="flex items-center gap-2">
          <div class="flex rounded-md border p-0.5 bg-muted/30">
            <button
              :class="cn('px-2.5 py-1 text-xs font-medium rounded flex items-center gap-1.5 transition-colors cursor-pointer', currentView === 'table' ? 'bg-background shadow-xs text-foreground font-semibold' : 'text-muted-foreground hover:text-foreground')"
              @click="currentView = 'table'"
            >
              <Table2 class="h-3.5 w-3.5" />
              表格列表
            </button>
            <button
              :class="cn('px-2.5 py-1 text-xs font-medium rounded flex items-center gap-1.5 transition-colors cursor-pointer', currentView === 'kanban' ? 'bg-background shadow-xs text-foreground font-semibold' : 'text-muted-foreground hover:text-foreground')"
              @click="currentView = 'kanban'"
            >
              <Columns3 class="h-3.5 w-3.5" />
              阶段看板
            </button>
          </div>

          <Button variant="outline" size="sm" class="text-xs" @click="exportCsv">
            <Download class="mr-1.5 h-3.5 w-3.5" />
            导出 CSV
          </Button>
        </div>
      </div>
    </Card>

    <!-- Content: Table View -->
    <Card v-if="currentView === 'table'" class="overflow-hidden border">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs">
          <thead class="bg-muted/50 border-b text-muted-foreground">
            <tr>
              <th class="py-3 px-4 font-semibold w-16">ID</th>
              <th class="py-3 px-4 font-semibold w-32">客户姓名</th>
              <th class="py-3 px-4 font-semibold w-48">联络方式</th>
              <th class="py-3 px-4 font-semibold w-44">国家 / 事项</th>
              <th class="py-3 px-4 font-semibold">案情事实摘要</th>
              <th class="py-3 px-4 font-semibold w-32">SLA 履约时效</th>
              <th class="py-3 px-4 font-semibold w-36 text-right">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border">
            <tr
              v-for="row in intakes"
              :key="row.id"
              class="hover:bg-muted/30 transition-colors cursor-pointer"
              @click="openDetail(row)"
            >
              <td class="py-3 px-4 font-mono font-medium text-foreground">#{{ row.id }}</td>
              <td class="py-3 px-4">
                <div class="font-bold text-foreground">{{ row.name }}</div>
                <ScoreBadge :score="row.score || 0" class="mt-1" />
              </td>
              <td class="py-3 px-4 space-y-0.5">
                <div class="font-mono text-foreground">{{ row.phone || '-' }}</div>
                <div v-if="row.email" class="text-[11px] text-muted-foreground font-mono truncate max-w-[180px]">
                  {{ row.email }}
                </div>
              </td>
              <td class="py-3 px-4 space-y-1">
                <Badge variant="secondary">{{ row.matter }}</Badge>
                <div v-if="row.country_or_region" class="text-[11px] text-muted-foreground">
                  🌍 {{ row.country_or_region }}
                </div>
              </td>
              <td class="py-3 px-4">
                <div class="line-clamp-2 text-foreground/80 leading-relaxed max-w-md">
                  {{ row.summary }}
                </div>
                <div v-if="row.note" class="text-[11px] text-amber-600 dark:text-amber-400 mt-0.5 truncate max-w-md">
                  📌 跟进备注: {{ row.note }}
                </div>
              </td>
              <td class="py-3 px-4">
                <SlaBadge :created-at="row.created_at" :status="row.status" />
              </td>
              <td class="py-3 px-4 text-right space-x-1" @click.stop>
                <Button variant="ghost" size="sm" class="text-xs text-primary" @click="openDetail(row)">
                  跟进档案 ↗
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  class="text-xs text-destructive hover:text-destructive hover:bg-destructive/10 px-2"
                  title="删除此案源客户"
                  @click="handleDelete(row)"
                >
                  <Trash2 class="h-3.5 w-3.5" />
                </Button>
              </td>
            </tr>
            <tr v-if="intakes.length === 0">
              <td colspan="7" class="py-12 text-center text-muted-foreground">
                未找到符合条件的线索记录
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </Card>

    <!-- Content: Kanban View -->
    <IntakeKanban
      v-else
      :list="intakes"
      @select="openDetail"
    />

    <!-- Customer Detail 360 Sheet -->
    <IntakeDetailSheet
      v-model="detailOpen"
      :intake="selectedIntake"
      @saved="fetchData"
    />

    <!-- Delete Confirm Dialog -->
    <Dialog
      v-model="deleteDialogOpen"
      title="确认删除客户档案"
      description="该操作将彻底移除该涉外商事线索及所有关联记录。"
    >
      <div v-if="intakeToDelete" class="py-2 text-sm text-foreground space-y-2">
        <p>确定要删除以下案源吗？此操作无法撤销：</p>
        <div class="rounded-md border bg-muted/40 p-3 text-xs space-y-1">
          <div><span class="text-muted-foreground">案源编号：</span>#{{ intakeToDelete.id }}</div>
          <div><span class="text-muted-foreground">客户姓名：</span><strong class="text-foreground">{{ intakeToDelete.name }}</strong></div>
          <div><span class="text-muted-foreground">咨询事项：</span>{{ intakeToDelete.matter }}</div>
          <div v-if="intakeToDelete.phone"><span class="text-muted-foreground">联系方式：</span>{{ intakeToDelete.phone }}</div>
        </div>
      </div>
      <div class="flex justify-end gap-2 mt-4">
        <Button variant="outline" size="sm" :disabled="deleting" @click="deleteDialogOpen = false">取消</Button>
        <Button variant="destructive" size="sm" :loading="deleting" @click="confirmDelete">确认删除</Button>
      </div>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Card from '../../components/ui/Card.vue'
import Button from '../../components/ui/Button.vue'
import Input from '../../components/ui/Input.vue'
import Select from '../../components/ui/Select.vue'
import Badge from '../../components/ui/Badge.vue'
import Dialog from '../../components/ui/Dialog.vue'
import SlaBadge from '../../components/business/SlaBadge.vue'
import ScoreBadge from '../../components/business/ScoreBadge.vue'
import IntakeKanban from '../../components/business/IntakeKanban.vue'
import IntakeDetailSheet from '../../components/business/IntakeDetailSheet.vue'
import api from '../../api/client'
import { cn } from '../../lib/utils'
import {
  Users,
  Clock,
  Briefcase,
  CheckCircle2,
  Search,
  Table2,
  Columns3,
  Download,
  Trash2,
} from 'lucide-vue-next'

const currentView = ref<'table' | 'kanban'>('table')
const intakes = ref<any[]>([])
const stats = ref<any>({})
const filterStatus = ref('')
const searchQuery = ref('')
const detailOpen = ref(false)
const selectedIntake = ref<any>(null)
const deleteDialogOpen = ref(false)
const intakeToDelete = ref<any>(null)
const deleting = ref(false)

const fetchData = async () => {
  try {
    const params: any = {}
    if (filterStatus.value) params.status = filterStatus.value
    if (searchQuery.value) params.q = searchQuery.value

    const res: any = await api.get('/admin/api/intakes', { params })
    intakes.value = res || []

    const statsRes: any = await api.get('/admin/api/stats')
    stats.value = statsRes || {}
  } catch (err) {
    console.error(err)
  }
}

const resetFilter = () => {
  filterStatus.value = ''
  searchQuery.value = ''
  fetchData()
}

const openDetail = (item: any) => {
  selectedIntake.value = item
  detailOpen.value = true
}

const handleDelete = (row: any) => {
  intakeToDelete.value = row
  deleteDialogOpen.value = true
}

const confirmDelete = async () => {
  if (!intakeToDelete.value) return
  deleting.value = true
  try {
    await api.delete(`/admin/api/intakes/${intakeToDelete.value.id}`)
    deleteDialogOpen.value = false
    intakeToDelete.value = null
    await fetchData()
  } catch (err) {
    console.error('删除线索失败:', err)
  } finally {
    deleting.value = false
  }
}

const exportCsv = () => {
  if (intakes.value.length === 0) return
  const headers = ['ID', '客户姓名', '电话', '邮箱', '事项类型', '国家地区', '案情事实', '状态', '意向分', '跟进备注', '提交时间']
  const rows = intakes.value.map((i) => [
    i.id,
    `"${i.name || ''}"`,
    `"${i.phone || ''}"`,
    `"${i.email || ''}"`,
    `"${i.matter || ''}"`,
    `"${i.country_or_region || ''}"`,
    `"${(i.summary || '').replace(/"/g, '""')}"`,
    i.status,
    i.score || 0,
    `"${(i.note || '').replace(/"/g, '""')}"`,
    i.created_at,
  ])
  const csvContent = '\uFEFF' + [headers.join(','), ...rows.map((r) => r.join(','))].join('\n')
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `shenyuan-intakes-${new Date().toISOString().slice(0, 10)}.csv`
  a.click()
}

onMounted(() => {
  fetchData()
})
</script>
