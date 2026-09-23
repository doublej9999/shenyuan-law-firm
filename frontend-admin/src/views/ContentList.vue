<template>
  <div>
    <!-- 顶部操作栏 -->
    <el-card shadow="never" style="margin-bottom: 20px;">
      <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
        <div>
          <span style="font-weight: bold; font-size: 17px; color: #1f2937;">涉外法律专业文章库 (CMS)</span>
          <span style="margin-left: 12px; font-size: 13px; color: #6b7280;">
            支持 AI 双语自动撰写、SEO 质量门禁与搜索引擎即时收录联动
          </span>
        </div>
        <div style="display: flex; gap: 10px;">
          <el-button type="success" @click="openAiDrawer">
            ✨ AI 智能撰稿 & 选题
          </el-button>
          <el-button type="primary" @click="openCreate">新建双语文章</el-button>
        </div>
      </div>
    </el-card>

    <!-- 文章表格 -->
    <el-card shadow="never">
      <el-table :data="articles" v-loading="loading" stripe style="width: 100%;">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="slug" label="URL Slug" width="180" show-overflow-tooltip />
        <el-table-column prop="title_zh" label="中文标题" min-width="220" show-overflow-tooltip />
        <el-table-column prop="title_en" label="英文标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="business" label="业务领域" width="110">
          <template #default="{ row }">
            <el-tag size="small" effect="plain">{{ row.business }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'published' ? 'success' : 'warning'">
              {{ row.status === 'published' ? '已发布' : '草稿' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="openEdit(row)">编辑</el-button>
            <el-button v-if="row.status !== 'published'" link type="success" size="small" @click="publishArticle(row)">发布上线</el-button>
            <el-button v-if="row.status === 'published'" link type="info" size="small" @click="notifyIndexing(row)">推送收录</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- AI 智能撰稿抽屉 -->
    <el-drawer v-model="aiDrawerVisible" title="✨ AI 涉外法律文章智能生成工作台" size="65%">
      <div style="padding: 0 10px;">
        <!-- 选题推荐面板 -->
        <div style="margin-bottom: 22px;">
          <div style="font-weight: 600; font-size: 14px; margin-bottom: 8px; color: #374151;">
            🎯 智能推荐选题池（结合 GSC 机会词、搜索缺口与业务矩阵）
          </div>
          <div v-loading="loadingSuggestions" style="display: flex; flex-wrap: wrap; gap: 8px;">
            <el-tag
              v-for="(item, idx) in suggestedTopics"
              :key="idx"
              effect="light"
              type="info"
              style="cursor: pointer; padding: 6px 12px; height: auto;"
              @click="applySuggestion(item)"
            >
              <strong>[{{ item.business }}]</strong> {{ item.topic }}
            </el-tag>
            <div v-if="suggestedTopics.length === 0 && !loadingSuggestions" style="font-size: 12px; color: #9ca3af;">
              暂无未使用的推荐选题，可直接在下方输入自定义主题
            </div>
          </div>
        </div>

        <el-divider />

        <!-- 生成表单 -->
        <el-form label-position="top">
          <el-row :gutter="16">
            <el-col :span="16">
              <el-form-item label="文章主题 / 核心痛点关键词 (Topic)">
                <el-input v-model="aiForm.topic" placeholder="例如：外贸货代卷款失联货权救济 / 涉外继承境内房产过户公证" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="业务线 (Business)">
                <el-select v-model="aiForm.business" style="width: 100%;">
                  <el-option label="国际贸易纠纷 (trade)" value="trade" />
                  <el-option label="跨境债务追收与执行 (recovery)" value="recovery" />
                  <el-option label="涉外继承与家办 (legacy)" value="legacy" />
                  <el-option label="通用涉外商事 (general)" value="general" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="补充生成要求 (可选)">
            <el-input
              v-model="aiForm.custom_prompt"
              placeholder="例如：着重分析中国生效判决在香港或新加坡的认可与执行程序要点"
              type="textarea"
              :rows="2"
            />
          </el-form-item>

          <div style="margin: 18px 0;">
            <el-button type="success" :loading="generating" @click="handleAiGenerate" style="width: 100%; height: 40px;">
              🚀 开始全自动生成双语文章与 SEO 审查
            </el-button>
          </div>
        </el-form>

        <!-- 生成结果与质量审查看板 -->
        <div v-if="aiResult" style="margin-top: 24px;">
          <el-card shadow="never" style="background: #f9fafb; border: 1px solid #e5e7eb; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <div>
                <span style="font-weight: bold; font-size: 15px;">📊 SEO 质量门禁体检</span>
                <span style="margin-left: 12px; font-size: 13px;">
                  得分: <el-tag :type="aiResult.quality.passed ? 'success' : 'danger'" style="font-weight: bold;">
                    {{ aiResult.quality.score }} / 100 分
                  </el-tag>
                </span>
                <span style="margin-left: 8px; font-size: 13px; color: #6b7280;">
                  (字数: 中文 {{ aiResult.quality.word_count_zh }} 字 / 英文 {{ aiResult.quality.word_count_en }} 字符)
                </span>
              </div>
              <div>
                <el-button type="primary" size="small" @click="loadGeneratedIntoEditor">
                  填入编辑工作台 &rarr;
                </el-button>
              </div>
            </div>

            <!-- 问题与警告展示 -->
            <div v-if="aiResult.quality.issues && aiResult.quality.issues.length > 0" style="margin-top: 10px; color: #dc2626; font-size: 12px;">
              <strong>需修正问题：</strong> {{ aiResult.quality.issues.join('；') }}
            </div>
            <div v-if="aiResult.quality.warnings && aiResult.quality.warnings.length > 0" style="margin-top: 6px; color: #d97706; font-size: 12px;">
              <strong>优化建议：</strong> {{ aiResult.quality.warnings.join('；') }}
            </div>
          </el-card>

          <!-- 快速预览 -->
          <el-tabs type="border-card">
            <el-tab-pane label="中文正文预览">
              <div style="font-weight: bold; margin-bottom: 6px;">{{ aiResult.article.title_zh }}</div>
              <div style="font-size: 12px; color: #6b7280; margin-bottom: 12px;">{{ aiResult.article.description_zh }}</div>
              <el-input type="textarea" :rows="10" :model-value="aiResult.article.body_zh" readonly />
            </el-tab-pane>
            <el-tab-pane label="英文正文预览">
              <div style="font-weight: bold; margin-bottom: 6px;">{{ aiResult.article.title_en }}</div>
              <div style="font-size: 12px; color: #6b7280; margin-bottom: 12px;">{{ aiResult.article.description_en }}</div>
              <el-input type="textarea" :rows="10" :model-value="aiResult.article.body_en" readonly />
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </el-drawer>

    <!-- 文章编辑与发布抽屉 -->
    <el-drawer v-model="drawerVisible" :title="isEdit ? '编辑文章' : '新建文章'" size="65%">
      <div style="padding: 0 10px;">
        <el-form :model="currentArticle" label-position="top">
          <el-row :gutter="16">
            <el-col :span="16">
              <el-form-item label="文章 Slug (URL 路径标识)">
                <el-input v-model="currentArticle.slug" placeholder="例如: cross-border-inheritance-guide" :disabled="isEdit" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="业务线 (Business)">
                <el-select v-model="currentArticle.business" style="width: 100%;">
                  <el-option label="国际贸易 (trade)" value="trade" />
                  <el-option label="跨境追收 (recovery)" value="recovery" />
                  <el-option label="涉外继承 (legacy)" value="legacy" />
                  <el-option label="通用涉外 (general)" value="general" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="中文标题">
                <el-input v-model="currentArticle.title_zh" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="英文标题">
                <el-input v-model="currentArticle.title_en" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="中文摘要 (SEO Description)">
                <el-input v-model="currentArticle.description_zh" type="textarea" :rows="3" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="英文摘要 (SEO Description)">
                <el-input v-model="currentArticle.description_en" type="textarea" :rows="3" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="中文正文 (Markdown)">
                <el-input v-model="currentArticle.body_zh" type="textarea" :rows="14" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="英文正文 (Markdown)">
                <el-input v-model="currentArticle.body_en" type="textarea" :rows="14" />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </div>

      <template #footer>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <el-button @click="triggerQualityCheck">🔍 执行 SEO 质量审查</el-button>
          <div>
            <el-button @click="drawerVisible = false">取消</el-button>
            <el-button type="primary" :loading="saving" @click="saveArticle">保存为草稿</el-button>
            <el-button type="success" :loading="saving" @click="saveAndPublishArticle">保存并立即发布上线</el-button>
          </div>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api/client'

const loading = ref(false)
const saving = ref(false)
const articles = ref<any[]>([])
const drawerVisible = ref(false)
const isEdit = ref(false)
const currentArticle = ref<any>({})

// AI 智能撰稿相关状态
const aiDrawerVisible = ref(false)
const loadingSuggestions = ref(false)
const generating = ref(false)
const suggestedTopics = ref<any[]>([])
const aiForm = ref({
  topic: '',
  business: 'trade',
  custom_prompt: ''
})
const aiResult = ref<any>(null)

const fetchArticles = async () => {
  loading.value = true
  try {
    const res: any = await api.get('/admin/api/content')
    articles.value = res
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const openCreate = () => {
  isEdit.value = false
  currentArticle.value = {
    slug: '',
    title_zh: '',
    title_en: '',
    description_zh: '',
    description_en: '',
    body_zh: '',
    body_en: '',
    business: 'general',
    intent: 'I',
    status: 'draft',
  }
  drawerVisible.value = true
}

const openEdit = (row: any) => {
  isEdit.value = true
  currentArticle.value = { ...row }
  drawerVisible.value = true
}

const openAiDrawer = async () => {
  aiDrawerVisible.value = true
  if (suggestedTopics.value.length === 0) {
    loadingSuggestions.value = true
    try {
      const res: any = await api.get('/admin/api/content/topic-suggestions')
      suggestedTopics.value = res || []
    } catch (err) {
      console.error(err)
    } finally {
      loadingSuggestions.value = false
    }
  }
}

const applySuggestion = (item: any) => {
  aiForm.value.topic = item.topic
  aiForm.value.business = item.business
  ElMessage.info(`已加载选题：${item.topic}`)
}

const handleAiGenerate = async () => {
  if (!aiForm.value.topic) {
    ElMessage.warning('请输入或选择文章主题')
    return
  }
  generating.value = true
  try {
    const res: any = await api.post('/admin/api/content/ai-generate', aiForm.value)
    aiResult.value = res
    ElMessage.success('文章与 SEO 审查完成！')
  } catch (err: any) {
    ElMessage.error(err.message || '生成失败，请重试')
  } finally {
    generating.value = false
  }
}

const loadGeneratedIntoEditor = () => {
  if (!aiResult.value || !aiResult.value.article) return
  isEdit.value = false
  currentArticle.value = {
    ...aiResult.value.article,
    status: 'draft',
  }
  aiDrawerVisible.value = false
  drawerVisible.value = true
  ElMessage.success('已载入编辑抽屉，可进一步微调或直接发布')
}

const triggerQualityCheck = async () => {
  try {
    const res: any = await api.post('/admin/api/content/quality-check', currentArticle.value)
    const statusMsg = res.passed ? '✅ 质量审查通过！' : '⚠️ 存在需要关注的项：'
    const detail = (res.issues || []).concat(res.warnings || []).join('\n• ')
    ElMessageBox.alert(
      `当前得分：${res.score} / 100 分\n${detail ? '• ' + detail : '各项指标合规良好'}`,
      statusMsg,
      { type: res.passed ? 'success' : 'warning' }
    )
  } catch (err: any) {
    ElMessage.error('审查失败: ' + err.message)
  }
}

const saveArticle = async () => {
  saving.value = true
  try {
    if (isEdit.value) {
      await api.put(`/admin/api/content/${currentArticle.value.id}`, currentArticle.value)
      ElMessage.success('文章已更新并归档新版本')
    } else {
      await api.post('/admin/api/content', currentArticle.value)
      ElMessage.success('文章创建成功（草稿）')
    }
    drawerVisible.value = false
    fetchArticles()
  } catch (err) {
    console.error(err)
  } finally {
    saving.value = false
  }
}

const saveAndPublishArticle = async () => {
  saving.value = true
  try {
    let artId = currentArticle.value.id
    if (isEdit.value) {
      await api.put(`/admin/api/content/${artId}`, currentArticle.value)
    } else {
      const res: any = await api.post('/admin/api/content', currentArticle.value)
      artId = res.id
    }
    await api.post(`/admin/api/content/${artId}/publish`)
    ElMessage.success('文章已成功发布，并已触发搜索引擎主动收录推送！')
    drawerVisible.value = false
    fetchArticles()
  } catch (err: any) {
    ElMessage.error('发布失败: ' + err.message)
  } finally {
    saving.value = false
  }
}

const publishArticle = async (row: any) => {
  try {
    await api.post(`/admin/api/content/${row.id}/publish`)
    ElMessage.success('文章已正式发布上线，并已向搜索引擎发起收录通知')
    fetchArticles()
  } catch (err) {
    console.error(err)
  }
}

const notifyIndexing = async (row: any) => {
  try {
    const res: any = await api.post(`/admin/api/content/${row.id}/notify-indexing`)
    ElMessage.success(`已向搜索引擎主动发起重推通知`)
  } catch (err) {
    console.error(err)
  }
}

onMounted(() => {
  fetchArticles()
})
</script>
