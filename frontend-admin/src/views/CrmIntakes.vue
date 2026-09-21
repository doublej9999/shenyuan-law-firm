<template>
  <div class="crm-page">
    <!-- 数据概览卡片 (与 admin.html 一致的风格) -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="num">{{ stats.total || 0 }}</div>
        <div class="lbl">总咨询线索</div>
      </div>
      <div class="stat-card">
        <div class="num num-new">{{ stats.new || 0 }}</div>
        <div class="lbl">新线索待跟进</div>
      </div>
      <div class="stat-card">
        <div class="num num-process">{{ (stats.contacted || 0) + (stats.processing || 0) }}</div>
        <div class="lbl">已联系 / 处理中</div>
      </div>
      <div class="stat-card">
        <div class="num num-closed">{{ stats.closed || 0 }}</div>
        <div class="lbl">已结案转化</div>
      </div>
    </div>

    <!-- 筛选与搜索工具条 -->
    <div class="toolbar-card">
      <div class="toolbar-form">
        <el-select v-model="query.status" placeholder="全部状态" clearable style="width: 140px;">
          <el-option label="新线索" value="new" />
          <el-option label="已联系" value="contacted" />
          <el-option label="处理中" value="processing" />
          <el-option label="已结案" value="closed" />
        </el-select>
        <el-input 
          v-model="query.q" 
          placeholder="搜索客户姓名 / 电话 / 事项 / 摘要" 
          clearable 
          style="width: 280px;" 
          @keyup.enter="fetchData"
        />
        <el-button type="primary" class="btn-search" @click="fetchData">查询</el-button>
        <el-button @click="resetQuery">重置</el-button>
        <div class="spacer"></div>
        <span class="count-tag">共 {{ tableData.length }} 条记录</span>
      </div>
    </div>

    <!-- 线索表格 -->
    <div class="table-card">
      <el-table 
        :data="tableData" 
        v-loading="loading" 
        stripe 
        style="width: 100%;"
        header-cell-class-name="shenyuan-th"
      >
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="客户姓名" width="120">
          <template #default="{ row }">
            <strong>{{ row.name }}</strong>
          </template>
        </el-table-column>
        <el-table-column label="联系方式" width="180">
          <template #default="{ row }">
            <div>📞 {{ row.phone || '-' }}</div>
            <div v-if="row.email" style="font-size: 11.5px; color: #627180;">✉️ {{ row.email }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="matter" label="国家 / 事项" width="150">
          <template #default="{ row }">
            <span class="matter-badge">{{ row.matter }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="summary" label="问题描述与诉求" min-width="240" show-overflow-tooltip />
        <el-table-column prop="score" label="评分" width="90">
          <template #default="{ row }">
            <span class="score-badge" :class="row.score >= 40 ? 's-high' : 's-mid'">
              {{ row.score }} 分
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="流转状态" width="110">
          <template #default="{ row }">
            <span class="status-badge" :class="`b-${row.status}`">
              {{ getStatusLabel(row.status) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="提交时间" width="160" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="openFollowUp(row)">跟进流转</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 跟进流转对话框 -->
    <el-dialog v-model="dialogVisible" title="线索状态流转与跟进备注" width="520px">
      <el-form :model="currentItem" label-width="80px">
        <el-form-item label="客户姓名">
          <strong>{{ currentItem.name }}</strong>
          <span style="margin-left: 10px; color: #627180; font-size: 13px;">({{ currentItem.phone || currentItem.email }})</span>
        </el-form-item>
        <el-form-item label="咨询事项">
          <span>{{ currentItem.matter }}</span>
        </el-form-item>
        <el-form-item label="流转状态">
          <el-radio-group v-model="currentItem.status">
            <el-radio-button value="new">新线索</el-radio-button>
            <el-radio-button value="contacted">已联系</el-radio-button>
            <el-radio-button value="processing">处理中</el-radio-button>
            <el-radio-button value="closed">已结案</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="跟进记录">
          <el-input 
            v-model="currentItem.note" 
            type="textarea" 
            :rows="4" 
            placeholder="记录接洽时间、法域可行性评估、报价或下一步动作..." 
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" class="btn-save" :loading="saving" @click="saveFollowUp">保存更新</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api/client'

const loading = ref(false)
const saving = ref(false)
const tableData = ref([])
const stats = ref<any>({})
const query = ref({ status: '', q: '' })
const dialogVisible = ref(false)
const currentItem = ref<any>({})

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = { 
    new: '新线索', 
    contacted: '已联系', 
    processing: '处理中', 
    closed: '已结案' 
  }
  return map[status] || status
}

const fetchData = async () => {
  loading.value = true
  try {
    const params: any = {}
    if (query.value.status) params.status = query.value.status
    if (query.value.q) params.q = query.value.q
    const res: any = await api.get('/admin/api/intakes', { params })
    tableData.value = res
    const s: any = await api.get('/admin/api/stats')
    stats.value = s
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const resetQuery = () => {
  query.value = { status: '', q: '' }
  fetchData()
}

const openFollowUp = (row: any) => {
  currentItem.value = { ...row }
  dialogVisible.value = true
}

const saveFollowUp = async () => {
  saving.value = true
  try {
    await api.patch(`/admin/api/intakes/${currentItem.value.id}`, {
      status: currentItem.value.status,
      note: currentItem.value.note,
    })
    ElMessage.success('跟进更新成功')
    dialogVisible.value = false
    fetchData()
  } catch (err) {
    console.error(err)
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.crm-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-card {
  background: #fffdf9;
  border: 1px solid #d9d9d2;
  border-radius: 8px;
  padding: 16px 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.02);
}

.stat-card .num {
  font-size: 26px;
  font-weight: 800;
  color: #084d50;
  line-height: 1.1;
  font-family: serif;
}

.stat-card .num-new { color: #d76e39; }
.stat-card .num-process { color: #0d6c6b; }
.stat-card .num-closed { color: #4a5568; }

.stat-card .lbl {
  font-size: 12.5px;
  color: #627180;
  margin-top: 6px;
}

.toolbar-card {
  background: #fffdf9;
  border: 1px solid #d9d9d2;
  border-radius: 8px;
  padding: 14px 18px;
}

.toolbar-form {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.spacer {
  flex: 1;
}

.count-tag {
  color: #627180;
  font-size: 13px;
}

.btn-search {
  background: #084d50 !important;
  border-color: #084d50 !important;
}

.table-card {
  background: #fffdf9;
  border: 1px solid #d9d9d2;
  border-radius: 8px;
  overflow: hidden;
}

:deep(.shenyuan-th) {
  background-color: #f4eee4 !important;
  color: #627180 !important;
  font-size: 12.5px !important;
  font-weight: 700 !important;
}

.matter-badge {
  font-weight: 600;
  color: #084d50;
  font-size: 13px;
}

.score-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 700;
}

.score-badge.s-high {
  background: #fbe9e7;
  color: #c0392b;
}

.score-badge.s-mid {
  background: #fef3c7;
  color: #b45309;
}

.status-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 700;
}

.b-new {
  background: #f7e5d6;
  color: #6b341d;
}

.b-contacted {
  background: #deefea;
  color: #084d50;
}

.b-processing {
  background: #e3eaf6;
  color: #1f3a6e;
}

.b-closed {
  background: #e5e5e0;
  color: #4a4a44;
}

.btn-save {
  background: #d76e39 !important;
  border-color: #d76e39 !important;
}
</style>
