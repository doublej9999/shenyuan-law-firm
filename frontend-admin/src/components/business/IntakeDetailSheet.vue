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
          <div class="text-xs font-semibold text-muted-foreground uppercase tracking-wider">证据材料清单与审查 (Checklist)</div>
          <span class="text-[11px] text-muted-foreground">依据涉外争议核验</span>
        </div>
        <div class="space-y-2">
          <label
            v-for="(item, idx) in checklist"
            :key="idx"
            class="flex items-center gap-2 text-xs text-foreground/80 cursor-pointer hover:text-foreground"
          >
            <input type="checkbox" v-model="item.checked" class="rounded border-input text-primary focus:ring-primary h-4 w-4" />
            <span :class="item.checked ? 'line-through text-muted-foreground' : ''">{{ item.title }}</span>
          </label>
        </div>
      </div>

      <!-- Follow-up Notes & Status Flow -->
      <div class="rounded-lg border p-4 space-y-3 bg-muted/10">
        <div class="text-xs font-semibold text-muted-foreground uppercase tracking-wider">律师跟进纪要与阶段推进</div>
        <div class="space-y-3">
          <div>
            <label class="text-xs text-muted-foreground mb-1 block">流转案件阶段</label>
            <Select v-model="form.status">
              <option value="new">新线索 (待初审)</option>
              <option value="contacted">已初审联系</option>
              <option value="processing">方案评估推进中</option>
              <option value="closed">已签约/已结案</option>
            </Select>
          </div>
          <div>
            <label class="text-xs text-muted-foreground mb-1 block">录入跟进备注 (沟通时间、方案反馈等)</label>
            <textarea
              v-model="form.note"
              rows="3"
              placeholder="例如：2025-03-21 电话沟通，当事人表示合同争议标的为 30 万美元，已提示准备海牙公证授权委托书..."
              class="w-full rounded-md border border-input bg-background p-2.5 text-xs outline-none focus:ring-1 focus:ring-primary"
            />
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
import { ref, watch } from 'vue'
import Sheet from '../ui/Sheet.vue'
import Button from '../ui/Button.vue'
import Badge from '../ui/Badge.vue'
import Select from '../ui/Select.vue'
import Dialog from '../ui/Dialog.vue'
import SlaBadge from './SlaBadge.vue'
import ScoreBadge from './ScoreBadge.vue'
import TimezoneTip from './TimezoneTip.vue'
import { Trash2 } from 'lucide-vue-next'
import { toast } from 'vue-sonner'
import api from '../../api/client'

const props = defineProps<{
  modelValue: boolean
  intake: any
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', val: boolean): void
  (e: 'saved'): void
}>()

const saving = ref(false)
const deleting = ref(false)
const deleteDialogOpen = ref(false)
const form = ref({
  status: 'new',
  note: '',
})

const checklist = ref([
  { title: '当事人身份证明及涉外主体资格认证 (Apostille / 海牙附加证明书)', checked: false },
  { title: '涉外商事基础交易合同 / 跨境遗嘱 / 汇款追索银行底单凭证', checked: false },
  { title: '中英双语催告记录 (Demand Letter / 邮件往来记录)', checked: false },
  { title: '中国涉外法庭 / 国际仲裁机构管辖权初步审查', checked: false },
])

watch(
  () => props.intake,
  (val) => {
    if (val) {
      form.value.status = val.status || 'new'
      form.value.note = val.note || ''
    }
  },
  { immediate: true }
)

const handleSave = async () => {
  if (!props.intake) return
  saving.value = true
  try {
    await api.patch(`/admin/api/intakes/${props.intake.id}`, {
      status: form.value.status,
      note: form.value.note,
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
  deleting.value = true
  try {
    await api.delete(`/admin/api/intakes/${props.intake.id}`)
    toast.success(`客户【${props.intake.name}】的案源档案已删除`)
    deleteDialogOpen.value = false
    emit('saved')
    emit('update:modelValue', false)
  } catch (err: any) {
    console.error('删除线索失败:', err)
    toast.error(err?.response?.data?.detail || '删除客户档案失败')
  } finally {
    deleting.value = false
  }
}
</script>
