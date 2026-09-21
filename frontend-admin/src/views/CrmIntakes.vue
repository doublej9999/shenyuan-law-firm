<template>
  <div>
    <!-- 数据概览卡片 -->
    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="6">
        <el-card shadow="hover">
          <div style="font-size: 13px; color: #718096;">总咨询线索</div>
          <div style="font-size: 24px; font-weight: bold; margin-top: 8px; color: #2b6cb0;">{{ stats.total || 0 }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div style="font-size: 13px; color: #718096;">新线索待跟进</div>
          <div style="font-size: 24px; font-weight: bold; margin-top: 8px; color: #dd6b20;">{{ stats.new || 0 }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div style="font-size: 13px; color: #718096;">已联系 / 处理中</div>
          <div style="font-size: 24px; font-weight: bold; margin-top: 8px; color: #319795;">{{ (stats.contacted || 0) + (stats.processing || 0) }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div style="font-size: 13px; color: #718096;">已结案转化</div>
          <div style="font-size: 24px; font-weight: bold; margin-top: 8px; color: #38a169;">{{ stats.closed || 0 }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 筛选与搜索 -->
    <el-card shadow="never" style="margin-bottom: 20px;">
      <el-form :inline="true" :model="query">
        <el-form-item label="状态">
          <el-select v-model="query.status" placeholder="全部状态" clearable style="width: 130px;">
            <el-option label="新线索" value="new" />
            <el-option label="已联系" value="contacted" />
            <el-option label="处理中" value="processing" />
            <el-option label="已结案" value="closed" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="query.q" placeholder="客户姓名 / 手机 / 案情关键词" clearable style="width: 260px;" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchData">查询</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 线索表格 -->
    <el-card shadow="never">
      <el-table :data="tableData" v-loading="loading" stripe style="width: 100%;">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="name" label="客户姓名" width="120" />
        <el-table-column label="联系方式" width="180">
          <template #default="{ row }">
            <div>📞 {{ row.phone || '-' }}</div>
            <div v-if="row.email" style="font-size: 12px; color: #718096;">✉️ {{ row.email }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="matter" label="事项分类" width="130" />
        <el-table-column prop="summary" label="案情概况" min-width="250" show-overflow-tooltip />
        <el-table-column prop="score" label="意向评分" width="90">
          <template #default="{ row }">
            <el-tag :type="row.score >= 40 ? 'danger' : 'info'">{{ row.score }} 分</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="流转状态" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="提交时间" width="160" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="openFollowUp(row)">跟进流转</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 跟进对话框 -->
    <el-dialog v-model="dialogVisible" title="线索流转与备注" width="500px">
      <el-form :model="currentItem" label-width="80px">
        <el-form-item label="客户姓名">
          <span>{{ currentItem.name }} ({{ currentItem.phone || currentItem.email }})</span>
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
          <el-input v-model="currentItem.note" type="textarea" :rows="4" placeholder="记录跟进进度、评估法域及沟通要点..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveFollowUp">保存更新</el-button>
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
  const map: Record<string, string> = { new: '新线索', contacted: '已联系', processing: '处理中', closed: '已结案' }
  return map[status] || status
}

const getStatusTag = (status: string) => {
  const map: Record<string, string> = { new: 'warning', contacted: 'primary', processing: 'success', closed: 'info' }
  return map[status] || 'info'
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
