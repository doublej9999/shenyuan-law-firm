<template>
  <div>
    <el-card shadow="never" style="margin-bottom: 20px;">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <div style="font-weight: bold; font-size: 16px;">涉外法律专业文章库 (CMS)</div>
        <el-button type="primary" @click="openCreate">新建双语文章</el-button>
      </div>
    </el-card>

    <el-card shadow="never">
      <el-table :data="articles" v-loading="loading" stripe style="width: 100%;">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="slug" label="URL Slug" width="200" />
        <el-table-column prop="title_zh" label="中文标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="title_en" label="英文标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="business" label="业务领域" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'published' ? 'success' : 'warning'">
              {{ row.status === 'published' ? '已发布' : '草稿' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="openEdit(row)">编辑</el-button>
            <el-button v-if="row.status !== 'published'" link type="success" size="small" @click="publishArticle(row)">发布上线</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 编辑抽屉 -->
    <el-drawer v-model="drawerVisible" :title="isEdit ? '编辑文章' : '新建文章'" size="60%">
      <el-form :model="currentArticle" label-position="top">
        <el-form-item label="文章 Slug (URL 路径标识)">
          <el-input v-model="currentArticle.slug" placeholder="例如: cross-border-inheritance-guide" :disabled="isEdit" />
        </el-form-item>
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
              <el-input v-model="currentArticle.body_zh" type="textarea" :rows="12" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="英文正文 (Markdown)">
              <el-input v-model="currentArticle.body_en" type="textarea" :rows="12" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="drawerVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveArticle">保存快照并更新</el-button>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api/client'

const loading = ref(false)
const saving = ref(false)
const articles = ref([])
const drawerVisible = ref(false)
const isEdit = ref(false)
const currentArticle = ref<any>({})

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
  }
  drawerVisible.value = true
}

const openEdit = (row: any) => {
  isEdit.value = true
  currentArticle.value = { ...row }
  drawerVisible.value = true
}

const saveArticle = async () => {
  saving.value = true
  try {
    if (isEdit.value) {
      await api.put(`/admin/api/content/${currentArticle.value.id}`, currentArticle.value)
      ElMessage.success('文章已更新并归档新版本')
    } else {
      await api.post('/admin/api/content', currentArticle.value)
      ElMessage.success('文章创建成功')
    }
    drawerVisible.value = false
    fetchArticles()
  } catch (err) {
    console.error(err)
  } finally {
    saving.value = false
  }
}

const publishArticle = async (row: any) => {
  try {
    await api.post(`/admin/api/content/${row.id}/publish`)
    ElMessage.success('文章已正式发布上线')
    fetchArticles()
  } catch (err) {
    console.error(err)
  }
}

onMounted(() => {
  fetchArticles()
})
</script>
