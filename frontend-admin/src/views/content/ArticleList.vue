<template>
  <div class="space-y-4">
    <!-- Header Card -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <div>
        <h1 class="text-xl font-bold tracking-tight text-foreground">涉外法律内容工厂 (CMS Studio)</h1>
        <p class="text-xs text-muted-foreground mt-0.5">
          管理跨国商事诉讼、海牙公证、涉外继承中英双语专栏文章与 SEO 知识库
        </p>
      </div>
      <Button @click="openCreate">
        <Plus class="mr-1.5 h-4 w-4" />
        新建双语文章
      </Button>
    </div>

    <!-- Filters -->
    <Card class="p-3">
      <div class="flex flex-wrap items-center gap-3">
        <div class="w-40">
          <Select v-model="filterStatus" @update:model-value="fetchArticles">
            <option value="">全部发布状态</option>
            <option value="draft">草稿箱 (Draft)</option>
            <option value="published">已发布 (Published)</option>
          </Select>
        </div>
        <div class="w-44">
          <Select v-model="filterBusiness" @update:model-value="fetchArticles">
            <option value="">全部业务领域</option>
            <option value="recovery">跨境债权追收 (Recovery)</option>
            <option value="trade">国际贸易争议 (Trade)</option>
            <option value="legacy">涉外家事与继承 (Legacy)</option>
            <option value="general">涉外综合合规 (General)</option>
          </Select>
        </div>
        <div class="text-xs text-muted-foreground ml-auto font-medium">
          共 {{ articles.length }} 篇专业文章
        </div>
      </div>
    </Card>

    <!-- Articles Table -->
    <Card class="overflow-hidden border">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs">
          <thead class="bg-muted/50 border-b text-muted-foreground">
            <tr>
              <th class="py-3 px-4 font-semibold w-16">ID</th>
              <th class="py-3 px-4 font-semibold w-48">URL 标识 (Slug)</th>
              <th class="py-3 px-4 font-semibold">中文标题与双语对照</th>
              <th class="py-3 px-4 font-semibold w-36">业务线 / 意图</th>
              <th class="py-3 px-4 font-semibold w-28">状态</th>
              <th class="py-3 px-4 font-semibold w-36">更新时间</th>
              <th class="py-3 px-4 font-semibold w-36 text-right">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border">
            <tr
              v-for="item in articles"
              :key="item.id"
              class="hover:bg-muted/30 transition-colors"
            >
              <td class="py-3 px-4 font-mono font-medium text-foreground">#{{ item.id }}</td>
              <td class="py-3 px-4 font-mono text-[11px] text-muted-foreground">
                <span class="bg-muted px-1.5 py-0.5 rounded">{{ item.slug }}</span>
              </td>
              <td class="py-3 px-4 space-y-1 max-w-md">
                <div class="font-bold text-foreground truncate">{{ item.title_zh }}</div>
                <div v-if="item.title_en" class="text-[11px] text-muted-foreground truncate italic">
                  EN: {{ item.title_en }}
                </div>
              </td>
              <td class="py-3 px-4">
                <Badge variant="outline">{{ item.business }}</Badge>
                <span class="ml-1 text-[10px] text-muted-foreground font-mono">[{{ item.intent }}]</span>
              </td>
              <td class="py-3 px-4">
                <Badge :variant="item.status === 'published' ? 'success' : 'warning'">
                  {{ item.status === 'published' ? '已发布' : '草稿' }}
                </Badge>
              </td>
              <td class="py-3 px-4 text-muted-foreground font-mono text-[11px]">
                {{ formatDate(item.updated_at) }}
              </td>
              <td class="py-3 px-4 text-right space-x-1">
                <Button variant="ghost" size="sm" class="text-xs text-primary" @click="openEdit(item)">
                  编辑
                </Button>
                <Button
                  v-if="item.status !== 'published'"
                  variant="outline"
                  size="sm"
                  class="text-xs text-emerald-600 hover:text-emerald-700 hover:bg-emerald-50"
                  @click="handlePublish(item.id)"
                >
                  发布
                </Button>
              </td>
            </tr>
            <tr v-if="articles.length === 0">
              <td colspan="7" class="py-12 text-center text-muted-foreground">
                暂无文章记录
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </Card>

    <!-- Dual Column Markdown Editor Sheet -->
    <Sheet
      v-model="editorOpen"
      :title="isEdit ? `编辑双语文章 #${currentArticle.id}` : '撰写全新双语文章'"
      size="xl"
    >
      <div class="space-y-4">
        <!-- Slug & Business Metadata -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div>
            <label class="text-xs font-semibold text-muted-foreground mb-1 block">URL Slug (唯一路径)</label>
            <Input
              v-model="currentArticle.slug"
              placeholder="e.g. cross-border-debt-guide"
              :disabled="isEdit"
            />
          </div>
          <div>
            <label class="text-xs font-semibold text-muted-foreground mb-1 block">涉外业务领域</label>
            <Select v-model="currentArticle.business">
              <option value="recovery">跨境债权追收 (Recovery)</option>
              <option value="trade">国际贸易争议 (Trade)</option>
              <option value="legacy">涉外家事与继承 (Legacy)</option>
              <option value="general">涉外综合合规 (General)</option>
            </Select>
          </div>
          <div>
            <label class="text-xs font-semibold text-muted-foreground mb-1 block">SEO 搜索意图 (Intent)</label>
            <Select v-model="currentArticle.intent">
              <option value="I">信息型 (Informational)</option>
              <option value="C">商业调查型 (Commercial)</option>
              <option value="T">高交易转化型 (Transactional)</option>
            </Select>
          </div>
        </div>

        <!-- Titles Dual Input -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <label class="text-xs font-semibold text-muted-foreground mb-1 block">中文标题</label>
            <Input v-model="currentArticle.title_zh" placeholder="输入中文专业标题..." />
          </div>
          <div>
            <label class="text-xs font-semibold text-muted-foreground mb-1 block">English Title</label>
            <Input v-model="currentArticle.title_en" placeholder="Enter English legal title..." />
          </div>
        </div>

        <!-- Descriptions Dual Input -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <div class="flex justify-between items-center mb-1">
              <label class="text-xs font-semibold text-muted-foreground">中文 SEO 描述</label>
              <span class="text-[10px] font-mono text-muted-foreground">{{ (currentArticle.description_zh || '').length }}/120字</span>
            </div>
            <textarea
              v-model="currentArticle.description_zh"
              rows="2"
              placeholder="用于 Google/Baidu 搜索摘要..."
              class="w-full rounded-md border border-input bg-background p-2 text-xs outline-none focus:ring-1 focus:ring-primary"
            />
          </div>
          <div>
            <div class="flex justify-between items-center mb-1">
              <label class="text-xs font-semibold text-muted-foreground">English Meta Description</label>
              <span class="text-[10px] font-mono text-muted-foreground">{{ (currentArticle.description_en || '').length }}/160 chars</span>
            </div>
            <textarea
              v-model="currentArticle.description_en"
              rows="2"
              placeholder="For Google snippet..."
              class="w-full rounded-md border border-input bg-background p-2 text-xs outline-none focus:ring-1 focus:ring-primary"
            />
          </div>
        </div>

        <!-- Dual Column Split: Markdown Editing & Preview -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
          <!-- Chinese Column -->
          <div class="space-y-2 border rounded-lg p-3 bg-muted/10">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold text-foreground">🇨🇳 中文正文 (Markdown)</span>
              <span class="text-[10px] text-muted-foreground">支持法条、引用与加粗</span>
            </div>
            <textarea
              v-model="currentArticle.body_zh"
              rows="14"
              placeholder="# 引言与案情事实&#10;&#10;输入中文 Markdown 正文..."
              class="w-full font-mono rounded-md border border-input bg-background p-2.5 text-xs outline-none focus:ring-1 focus:ring-primary leading-relaxed"
            />
            <div class="mt-2 pt-2 border-t text-[11px] text-muted-foreground font-semibold">中文实时渲染预览：</div>
            <div class="max-h-48 overflow-y-auto p-2 bg-background rounded border">
              <MarkdownRenderer :content="currentArticle.body_zh" />
            </div>
          </div>

          <!-- English Column -->
          <div class="space-y-2 border rounded-lg p-3 bg-muted/10">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold text-foreground">🇺🇸 English Body (Markdown)</span>
              <span class="text-[10px] text-muted-foreground">Cross-border legal insights</span>
            </div>
            <textarea
              v-model="currentArticle.body_en"
              rows="14"
              placeholder="# Executive Summary&#10;&#10;Write English legal draft in Markdown..."
              class="w-full font-mono rounded-md border border-input bg-background p-2.5 text-xs outline-none focus:ring-1 focus:ring-primary leading-relaxed"
            />
            <div class="mt-2 pt-2 border-t text-[11px] text-muted-foreground font-semibold">English Live Preview:</div>
            <div class="max-h-48 overflow-y-auto p-2 bg-background rounded border">
              <MarkdownRenderer :content="currentArticle.body_en" />
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <Button variant="outline" size="sm" @click="editorOpen = false">取消</Button>
        <Button size="sm" :loading="saving" @click="handleSaveArticle">保存双语快照</Button>
      </template>
    </Sheet>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Card from '../../components/ui/Card.vue'
import Button from '../../components/ui/Button.vue'
import Input from '../../components/ui/Input.vue'
import Select from '../../components/ui/Select.vue'
import Badge from '../../components/ui/Badge.vue'
import Sheet from '../../components/ui/Sheet.vue'
import MarkdownRenderer from '../../components/business/MarkdownRenderer.vue'
import api from '../../api/client'
import { Plus } from 'lucide-vue-next'

const articles = ref<any[]>([])
const filterStatus = ref('')
const filterBusiness = ref('')
const editorOpen = ref(false)
const isEdit = ref(false)
const saving = ref(false)
const currentArticle = ref<any>({})

const fetchArticles = async () => {
  try {
    const params: any = {}
    if (filterStatus.value) params.status = filterStatus.value
    const res: any = await api.get('/admin/api/content', { params })
    articles.value = res || []
  } catch (err) {
    console.error(err)
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
    business: 'recovery',
    intent: 'I',
    status: 'draft',
  }
  editorOpen.value = true
}

const openEdit = (item: any) => {
  isEdit.value = true
  currentArticle.value = { ...item }
  editorOpen.value = true
}

const handleSaveArticle = async () => {
  saving.value = true
  try {
    if (isEdit.value) {
      await api.put(`/admin/api/content/${currentArticle.value.id}`, currentArticle.value)
    } else {
      await api.post('/admin/api/content', currentArticle.value)
    }
    editorOpen.value = false
    fetchArticles()
  } catch (err) {
    console.error(err)
  } finally {
    saving.value = false
  }
}

const handlePublish = async (id: number) => {
  try {
    await api.post(`/admin/api/content/${id}/publish`)
    fetchArticles()
  } catch (err) {
    console.error(err)
  }
}

const formatDate = (iso: string) => {
  if (!iso) return ''
  const d = new Date(iso)
  return `${d.getFullYear()}-${(d.getMonth() + 1).toString().padStart(2, '0')}-${d.getDate().toString().padStart(2, '0')}`
}

onMounted(() => {
  fetchArticles()
})
</script>
