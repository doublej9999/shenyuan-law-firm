<template>
  <Sheet :model-value="modelValue" :title="intake ? `案源档案 #${intake.id} · ${intake.name}` : '案源详情'" size="lg" @update:model-value="$emit('update:modelValue', $event)">
    <div v-if="intake" class="space-y-6">
      <!-- Top Meta Cards -->
      <div class="grid grid-cols-2 gap-3">
        <div class="rounded-lg border bg-muted/20 p-3 space-y-1">
          <div class="text-[11px] text-muted-foreground">客源国家与时区</div>
          <TimezoneTip :country="intake.country_or_region" />
        </div>
        <div class="rounded-lg border bg-muted/20 p-3 space-y-1">
          <div class="text-[11px] text-muted-foreground">SLA 履约时效</div>
          <SlaBadge :created-at="intake.created_at" :status="intake.status" />
        </div>
      </div>

      <!-- Contact Info -->
      <div class="rounded-lg border p-4 space-y-3">
        <div class="text-xs font-semibold text-muted-foreground uppercase tracking-wider">当事人联系方式</div>
        <div class="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span class="text-xs text-muted-foreground">电话：</span>
            <span class="font-medium font-mono ml-1">{{ intake.phone || '未留存' }}</span>
          </div>
          <div>
            <span class="text-xs text-muted-foreground">邮箱：</span>
            <span class="font-medium font-mono ml-1">{{ intake.email || '未留存' }}</span>
          </div>
          <div>
            <span class="text-xs text-muted-foreground">业务类型：</span>
            <Badge variant="secondary" class="ml-1">{{ intake.matter }}</Badge>
          </div>
          <div>
            <span class="text-xs text-muted-foreground">意向分级：</span>
            <ScoreBadge :score="intake.score || 0" class="ml-1" />
          </div>
        </div>
      </div>

      <!-- Facts Summary -->
      <div class="rounded-lg border p-4 space-y-2 bg-card">
        <div class="text-xs font-semibold text-muted-foreground uppercase tracking-wider">当事人陈述案情事实</div>
        <p class="text-xs leading-relaxed text-foreground/90 whitespace-pre-wrap bg-muted/30 p-3 rounded-md border font-sans">
          {{ intake.summary }}
        </p>
      </div>

      <!-- Material & Evidence Checklist -->
      <div class="rounded-lg border p-4 space-y-3">
        <div class="flex items-center justify-between">
          <div class="text-xs font-semibold text-muted-foreground uppercase tracking-wider">涉外案件事实与证据核验 (Evidence Checklist)</div>
          <span class="text-xs font-semibold text-primary">完备度: {{ evidenceScore }}%</span>
        </div>
        <div class="space-y-2">
          <label
            v-for="item in checklist"
            :key="item.id"
            class="flex items-center gap-2 text-xs text-foreground/80 cursor-pointer hover:text-foreground"
          >
            <input type="checkbox" v-model="item.checked" class="rounded border-input text-primary focus:ring-primary h-4 w-4" />
            <span :class="item.checked ? 'text-foreground font-medium' : 'text-muted-foreground'">{{ item.title }}</span>
          </label>
        </div>
      </div>

      <!-- Follow-up Timeline & Case Notes -->
      <div class="rounded-lg border p-4 space-y-4 bg-muted/10">
        <div class="flex items-center justify-between">
          <div class="text-xs font-semibold text-muted-foreground uppercase tracking-wider">案件跟进记录时间线 (Timeline Notes)</div>
          <div class="w-36">
            <Select v-model="form.status">
              <option value="new">新线索 (待初审)</option>
              <option value="contacted">已初审联系</option>
              <option value="processing">方案评估推进中</option>
              <option value="closed">已签约/已结案</option>
            </Select>
          </div>
        </div>

        <!-- Add Note Input Form -->
        <div class="border rounded-md p-3 bg-background space-y-2.5">
          <div class="flex items-center gap-2">
            <div class="w-32">
              <Select v-model="newEntryType">
                <option value="电话沟通">📞 电话沟通</option>
                <option value="微信沟通">💬 微信沟通</option>
                <option value="邮件发函">✉️ 邮件发函</option>
                <option value="线下会见">🤝 线下会见</option>
                <option value="方案讨论">📋 内部讨论</option>
              </Select>
            </div>
            <div class="w-32">
              <Input v-model="newEntryAuthor" placeholder="跟进律师姓名" />
            </div>
            <Button size="sm" variant="outline" class="ml-auto text-xs" @click="addTimelineEntry">
              + 添加沟通记录
            </Button>
          </div>
          <textarea
            v-model="newEntryContent"
            rows="2"
            placeholder="录入本次与当事人沟通详情（如：债务人加州房产线索、已提示签署涉外委托书、诉讼时效截止日等）..."
            class="w-full rounded-md border border-input bg-background p-2 text-xs outline-none focus:ring-1 focus:ring-primary"
          />
        </div>

        <!-- Chronological Timeline Display -->
        <div class="space-y-2 pt-1">
          <div class="text-[11px] text-muted-foreground font-medium">历史跟进脉络 ({{ timelineEntries.length }} 次跟进)：</div>
          <div v-if="timelineEntries.length === 0" class="text-xs text-muted-foreground py-2 text-center border border-dashed rounded-md">
            暂无跟进记录，请在上方添加首次沟通备忘
          </div>
          <div
            v-for="entry in timelineEntries"
            :key="entry.id"
            class="p-2.5 rounded-md border bg-background text-xs space-y-1 shadow-2xs"
          >
            <div class="flex items-center justify-between text-[11px]">
              <div class="flex items-center gap-1.5 font-semibold text-foreground">
                <Badge variant="secondary" class="text-[10px] px-1.5 py-0">{{ entry.type }}</Badge>
                <span>{{ entry.author }}</span>
              </div>
              <span class="text-muted-foreground font-mono text-[10px]">{{ entry.time }}</span>
            </div>
            <p class="text-foreground/90 whitespace-pre-wrap leading-relaxed font-sans text-xs">
              {{ entry.content }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="flex items-center justify-between w-full">
        <Button
          variant="destructive"
          size="sm"
          :loading="deleting"
          @click="openDeleteDialog"
        >
          <Trash2 class="w-3.5 h-3.5 mr-1" />
          删除客户档案
        </Button>
        <div class="flex items-center gap-2">
          <Button variant="outline" size="sm" @click="$emit('update:modelValue', false)">取消</Button>
          <Button size="sm" :loading="saving" @click="handleSave">保存跟进档案</Button>
        </div>
      </div>
    </template>
  </Sheet>

  <!-- Delete Confirm Dialog -->
  <Dialog
    v-model="deleteDialogOpen"
    title="确认删除客户档案"
    description="该操作将彻底移除该涉外商事线索及所有关联记录。"
  >
    <div v-if="intake" class="py-2 text-sm text-foreground space-y-2">
      <p>确定要删除以下案源吗？此操作无法撤销：</p>
      <div class="rounded-md border bg-muted/40 p-3 text-xs space-y-1">
        <div><span class="text-muted-foreground">案源编号：</span>#{{ intake.id }}</div>
        <div><span class="text-muted-foreground">客户姓名：</span><strong class="text-foreground">{{ intake.name }}</strong></div>
        <div><span class="text-muted-foreground">咨询事项：</span>{{ intake.matter }}</div>
        <div v-if="intake.phone"><span class="text-muted-foreground">联系方式：</span>{{ intake.phone }}</div>
      </div>
    </div>
    <div class="flex justify-end gap-2 mt-4">
      <Button variant="outline" size="sm" :disabled="deleting" @click="deleteDialogOpen = false">取消</Button>
      <Button variant="destructive" size="sm" :loading="deleting" @click="confirmDelete">确认删除</Button>
    </div>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import Sheet from '../ui/Sheet.vue'
import Button from '../ui/Button.vue'
import Badge from '../ui/Badge.vue'
import Input from '../ui/Input.vue'
import Select from '../ui/Select.vue'
import Dialog from '../ui/Dialog.vue'
import SlaBadge from './SlaBadge.vue'
import ScoreBadge from './ScoreBadge.vue'
import TimezoneTip from './TimezoneTip.vue'
import { Trash2 } from 'lucide-vue-next'
import { toast } from 'vue-sonner'
import api from '../../api/client'
import { describeDeleteError } from '../../lib/apiError'

interface TimelineEntry {
  id: string
  time: string
  type: string
  author: string
  content: string
}

const props = defineProps<{
  modelValue: boolean
  intake: any
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', val: boolean): void
  (e: 'saved'): void
  (e: 'deleted', intake: any): void
}>()

const saving = ref(false)
const deleting = ref(false)
const deleteDialogOpen = ref(false)
const form = ref({
  status: 'new',
})

const timelineEntries = ref<TimelineEntry[]>([])
const newEntryType = ref('电话沟通')
const newEntryAuthor = ref('主办律师')
const newEntryContent = ref('')

const checklist = ref([
  { id: 'apostille', title: '当事人身份证明及涉外主体资格认证 (Apostille / 海牙附加证明书)', checked: false },
  { id: 'contract', title: '涉外商事基础交易合同 / 跨境遗嘱 / 汇款追索银行底单凭证', checked: false },
  { id: 'demand', title: '中英双语催告与往来记录 (Demand Letter / 邮件对账认账记录)', checked: false },
  { id: 'jurisdiction', title: '中国涉外法庭 / 国际仲裁机构管辖权与适用法初步审查', checked: false },
  { id: 'asset', title: '债务人/被继承人海外财产线索（不动产、开户行、股权登记）', checked: false },
])

const evidenceScore = computed(() => {
  const total = checklist.value.length
  if (total === 0) return 0
  const checked = checklist.value.filter(i => i.checked).length
  return Math.round((checked / total) * 100)
})

watch(
  () => props.intake,
  (val) => {
    if (val) {
      form.value.status = val.status || 'new'
      const rawNote = (val.note || '').trim()
      if (rawNote.startsWith('{') && rawNote.endsWith('}')) {
        try {
          const parsed = JSON.parse(rawNote)
          timelineEntries.value = Array.isArray(parsed.entries) ? parsed.entries : []
          const checkedIds = new Set(parsed.checkedIds || [])
          checklist.value.forEach(item => {
            item.checked = checkedIds.has(item.id)
          })
        } catch {
          timelineEntries.value = rawNote ? [{ id: '1', time: val.created_at || '', type: '前期纪要', author: '系统', content: rawNote }] : []
        }
      } else if (rawNote) {
        timelineEntries.value = [{ id: '1', time: val.created_at || '', type: '历史纪要', author: '律师团队', content: rawNote }]
      } else {
        timelineEntries.value = []
        checklist.value.forEach(i => i.checked = false)
      }
    }
  },
  { immediate: true }
)

const addTimelineEntry = () => {
  if (!newEntryContent.value.trim()) {
    toast.error('请输入沟通跟进内容')
    return
  }
  const now = new Date()
  const nowStr = `${now.getFullYear()}-${(now.getMonth() + 1).toString().padStart(2, '0')}-${now.getDate().toString().padStart(2, '0')} ${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
  timelineEntries.value.unshift({
    id: Date.now().toString(),
    time: nowStr,
    type: newEntryType.value,
    author: newEntryAuthor.value.trim() || '主办律师',
    content: newEntryContent.value.trim(),
  })
  newEntryContent.value = ''
  toast.success('已追加跟进记录，请点击底部保存生效')
}

const handleSave = async () => {
  if (!props.intake) return
  saving.value = true
  try {
    const payloadNote = JSON.stringify({
      entries: timelineEntries.value,
      checkedIds: checklist.value.filter(i => i.checked).map(i => i.id),
    })
    await api.patch(`/admin/api/intakes/${props.intake.id}`, {
      status: form.value.status,
      note: payloadNote,
    })
    toast.success(`案源 #${props.intake.id} 跟进档案已更新`)
    emit('saved')
    emit('update:modelValue', false)
  } catch (err: any) {
    console.error(err)
    toast.error(err?.response?.data?.detail || '保存跟进档案失败')
  } finally {
    saving.value = false
  }
}

const openDeleteDialog = () => {
  deleteDialogOpen.value = true
}

const confirmDelete = async () => {
  if (!props.intake) return
  const target = props.intake
  deleting.value = true
  try {
    await api.delete(`/admin/api/intakes/${target.id}`)
    deleteDialogOpen.value = false
    emit('update:modelValue', false)
    // 由父组件负责展示“删除成功”结果弹窗与刷新列表
    emit('deleted', target)
  } catch (err: any) {
    console.error('删除线索失败:', err)
    toast.error(describeDeleteError(err))
  } finally {
    deleting.value = false
  }
}
</script>
