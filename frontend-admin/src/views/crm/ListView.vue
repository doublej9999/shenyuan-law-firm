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

      <!-- Batch Actions Bar (when items selected) -->
      <transition name="fade">
        <div
          v-if="selectedIds.length > 0"
          class="mt-3 pt-3 border-t flex items-center justify-between bg-destructive/5 -mx-3 -mb-3 p-3 rounded-b-lg border-destructive/20"
        >
          <div class="flex items-center gap-2 text-xs">
            <span class="inline-flex items-center justify-center bg-destructive text-destructive-foreground font-semibold px-2 py-0.5 rounded-full text-[11px]">
              {{ selectedIds.length }}
            </span>
            <span class="text-foreground font-medium">已选择 {{ selectedIds.length }} 项案源客户</span>
          </div>
          <div class="flex items-center gap-2">
            <Button variant="outline" size="sm" class="text-xs h-7" @click="selectedIds = []">
              取消全选
            </Button>
            <Button
              variant="destructive"
              size="sm"
              class="text-xs h-7"
              :loading="batchDeleting"
              @click="batchDeleteDialogOpen = true"
            >
              <Trash2 class="mr-1.5 h-3.5 w-3.5" />
              批量删除
            </Button>
          </div>
        </div>
      </transition>
    </Card>

    <!-- Content: Table View -->
    <Card v-if="currentView === 'table'" class="overflow-hidden border relative">
      <div v-if="loading" class="absolute inset-0 bg-background/60 backdrop-blur-[1px] z-10 flex items-center justify-center">
        <div class="flex items-center gap-2 text-xs text-muted-foreground bg-background border px-3 py-1.5 rounded-md shadow-xs">
          <span class="inline-block h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent" />
          正在同步案源数据...
        </div>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs">
          <thead class="bg-muted/50 border-b text-muted-foreground">
            <tr>
              <th class="py-3 px-3 w-10 text-center">
                <input
                  type="checkbox"
                  class="rounded border-input text-primary focus:ring-primary h-3.5 w-3.5 cursor-pointer"
                  :checked="isAllSelected"
                  :indeterminate="isIndeterminate"
                  @change="toggleSelectAll"
                />
              </th>
              <th class="py-3 px-3 font-semibold w-16">ID</th>
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
              :class="cn('hover:bg-muted/30 transition-colors cursor-pointer', selectedIds.includes(row.id) ? 'bg-primary/5' : '')"
              @click="openDetail(row)"
            >
              <td class="py-3 px-3 text-center" @click.stop>
                <input
                  type="checkbox"
                  class="rounded border-input text-primary focus:ring-primary h-3.5 w-3.5 cursor-pointer"
                  :checked="selectedIds.includes(row.id)"
                  @change="toggleSelectRow(row.id)"
                />
              </td>
              <td class="py-3 px-3 font-mono font-medium text-foreground">#{{ row.id }}</td>
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
              <td colspan="8" class="py-12 text-center text-muted-foreground">
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
      @deleted="onSheetDeleted"
    />

    <!-- Single Delete Confirm Dialog -->
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

    <!-- Batch Delete Confirm Dialog -->
    <Dialog
      v-model="batchDeleteDialogOpen"
      title="确认批量删除客户档案"
      description="该操作将同时清理所有选中的涉外案源线索，不可恢复。"
    >
      <div class="py-2 text-sm text-foreground space-y-2">
        <p>确定要彻底删除已选中的 <strong class="text-destructive font-bold">{{ selectedIds.length }}</strong> 条客户案源吗？</p>
        <div class="rounded-md border bg-destructive/5 p-3 text-xs space-y-1 border-destructive/20 text-muted-foreground">
          ⚠️ 注意：关联的所有证据材料登记、跟进备注将同步清除，无法撤销。
        </div>
      </div>
      <div class="flex justify-end gap-2 mt-4">
        <Button variant="outline" size="sm" :disabled="batchDeleting" @click="batchDeleteDialogOpen = false">取消</Button>
        <Button variant="destructive" size="sm" :loading="batchDeleting" @click="confirmBatchDelete">确认批量删除</Button>
      </div>
    </Dialog>

    <!-- Delete Success Result Dialog -->
    <Dialog v-model="successDialogOpen">
      <div v-if="deleteResult" class="flex flex-col items-center text-center py-2 space-y-3">
        <div class="flex h-14 w-14 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-600">
          <CheckCircle2 class="h-7 w-7" />
        </div>
        <div class="space-y-1">
          <h3 class="text-base font-semibold text-foreground">删除成功</h3>
          <p class="text-xs text-muted-foreground">该客户档案已从线索中枢中彻底移除。</p>
        </div>
        <div class="w-full rounded-md border bg-muted/40 p-3 text-xs text-left space-y-1">
          <div v-if="deleteResult.count === 1">
            <span class="text-muted-foreground">客户姓名：</span>
            <strong class="text-foreground">{{ deleteResult.names[0] }}</strong>
          </div>
          <div v-else class="text-muted-foreground">
            共删除 <strong class="text-foreground">{{ deleteResult.count }}</strong> 条案源：
            <span class="text-foreground">{{ deleteResult.names.join('、') }}</span>
          </div>
        </div>
      </div>
      <div class="flex justify-center mt-2">
        <Button size="sm" class="w-full" @click="successDialogOpen = false">知道了</Button>
      </div>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
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
import { describeDeleteError } from '../../lib/apiError'
import { toast } from 'vue-sonner'
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
const loading = ref(false)
const detailOpen = ref(false)
const selectedIntake = ref<any>(null)
const deleteDialogOpen = ref(false)
const intakeToDelete = ref<any>(null)
const deleting = ref(false)

// 批量选择
const selectedIds = ref<number[]>([])
const batchDeleteDialogOpen = ref(false)
const batchDeleting = ref(false)

// 删除成功结果弹窗
const successDialogOpen = ref(false)
const deleteResult = ref<{ count: number; names: string[] } | null>(null)

const showDeleteSuccess = (items: any[] | any) => {
  const list = Array.isArray(items) ? items : [items]
  deleteResult.value = {
    count: list.length,
    names: list.map((i) => i?.name || `#${i?.id ?? '-'}`),
  }
  successDialogOpen.value = true
}

// 详情抽屉内删除成功后：先刷新列表，再弹出结果提示
const onSheetDeleted = async (item: any) => {
  selectedIntake.value = null
  await fetchData()
  showDeleteSuccess(item)
}

const isAllSelected = computed(() => {
  return intakes.value.length > 0 && selectedIds.value.length === intakes.value.length
})

const isIndeterminate = computed(() => {
  return selectedIds.value.length > 0 && selectedIds.value.length < intakes.value.length
})

const toggleSelectAll = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.checked) {
    selectedIds.value = intakes.value.map((i) => i.id)
  } else {
    selectedIds.value = []
  }
}

const toggleSelectRow = (id: number) => {
  const idx = selectedIds.value.indexOf(id)
  if (idx > -1) {
    selectedIds.value.splice(idx, 1)
  } else {
    selectedIds.value.push(id)
  }
}

const fetchData = async () => {
  loading.value = true
  try {
    const params: any = {}
    if (filterStatus.value) params.status = filterStatus.value
    if (searchQuery.value) params.q = searchQuery.value

    const res: any = await api.get('/admin/api/intakes', { params })
    intakes.value = res || []

    // 过滤掉不再存在于当前列表中的选中项
    const currentIdSet = new Set(intakes.value.map((i) => i.id))
    selectedIds.value = selectedIds.value.filter((id) => currentIdSet.has(id))

    const statsRes: any = await api.get('/admin/api/stats')
    stats.value = statsRes || {}
  } catch (err: any) {
    console.error(err)
    toast.error('拉取案源列表失败')
  } finally {
    loading.value = false
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
  const target = intakeToDelete.value
  deleting.value = true
  try {
    await api.delete(`/admin/api/intakes/${target.id}`)
    deleteDialogOpen.value = false
    intakeToDelete.value = null
    await fetchData()
    showDeleteSuccess(target)
  } catch (err: any) {
    console.error('删除线索失败:', err)
    toast.error(describeDeleteError(err))
  } finally {
    deleting.value = false
  }
}

const confirmBatchDelete = async () => {
  if (selectedIds.value.length === 0) return
  const targets = intakes.value.filter((i) => selectedIds.value.includes(i.id))
  batchDeleting.value = true
  try {
    await api.post('/admin/api/intakes/batch-delete', {
      ids: selectedIds.value,
    })
    batchDeleteDialogOpen.value = false
    selectedIds.value = []
    await fetchData()
    showDeleteSuccess(targets)
  } catch (err: any) {
    console.error('批量删除失败:', err)
    toast.error(describeDeleteError(err))
  } finally {
    batchDeleting.value = false
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
