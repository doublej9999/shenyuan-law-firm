<template>
  <div class="country-dial-select" ref="containerRef">
    <!-- 触发按钮 -->
    <button
      type="button"
      class="dial-trigger"
      :class="{ 'is-open': isOpen, 'is-dark': darkTheme }"
      @click="toggleDropdown"
      :aria-expanded="isOpen"
      aria-label="选择国际电话区号"
    >
      <span class="trigger-flag">{{ selectedCountry.flag }}</span>
      <span class="trigger-code">{{ selectedCountry.dialCode }}</span>
      <svg class="trigger-arrow" viewBox="0 0 20 20" fill="currentColor" width="12" height="12">
        <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
      </svg>
    </button>

    <!-- 下拉弹出层（支持搜索填入与滑选） -->
    <transition name="dial-fade">
      <div v-if="isOpen" class="dial-dropdown" :class="{ 'is-dark': darkTheme }">
        <div class="dial-search-box">
          <input
            ref="searchInputRef"
            v-model="searchQuery"
            type="text"
            class="dial-search-input"
            :placeholder="isEn ? 'Search country or code (e.g. +971, UAE)...' : '搜索国家或区号 (如: 971, 阿联酋)...'"
            @click.stop
            @keydown.esc="closeDropdown"
          />
          <button v-if="searchQuery" type="button" class="search-clear" @click="searchQuery = ''">✕</button>
        </div>

        <ul class="dial-list" role="listbox">
          <li
            v-for="country in filteredCountries"
            :key="country.code"
            class="dial-item"
            :class="{ 'is-active': country.dialCode === modelValue }"
            role="option"
            :aria-selected="country.dialCode === modelValue"
            @click="selectCountry(country)"
          >
            <span class="item-flag">{{ country.flag }}</span>
            <span class="item-name">{{ isEn ? country.nameEn : country.nameZh }}</span>
            <span class="item-code">{{ country.dialCode }}</span>
          </li>
          <li v-if="filteredCountries.length === 0" class="dial-empty">
            {{ isEn ? 'No matching country found' : '未找到匹配国家/区号' }}
          </li>
        </ul>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { GEO_COUNTRY_MAP, type GeoCountryMeta } from '@/composables/useUserGeo'

const props = withDefaults(
  defineProps<{
    modelValue: string // 如 '+86', '+971'
    isEn?: boolean
    darkTheme?: boolean
  }>(),
  {
    isEn: false,
    darkTheme: false,
  }
)

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'select', country: GeoCountryMeta): void
}>()

const isOpen = ref(false)
const searchQuery = ref('')
const containerRef = ref<HTMLElement | null>(null)
const searchInputRef = ref<HTMLInputElement | null>(null)

// 转换所有国家为数组
const countryList = computed<GeoCountryMeta[]>(() => Object.values(GEO_COUNTRY_MAP))

// 当前选中的国家信息，根据 modelValue 匹配
const selectedCountry = computed<GeoCountryMeta>(() => {
  const targetCode = props.modelValue?.trim()
  const matched = countryList.value.find((c) => c.dialCode === targetCode)
  if (matched) return matched
  // 默认中国
  return GEO_COUNTRY_MAP.CN
})

// 实时过滤搜索结果（支持中文名、英文名、二字码、区号数字）
const filteredCountries = computed(() => {
  const q = searchQuery.value.trim().toLowerCase().replace(/^\+/, '')
  if (!q) return countryList.value

  return countryList.value.filter((c) => {
    const rawDial = c.dialCode.replace('+', '')
    return (
      rawDial.includes(q) ||
      c.nameZh.toLowerCase().includes(q) ||
      c.nameEn.toLowerCase().includes(q) ||
      c.code.toLowerCase().includes(q)
    )
  })
})

const toggleDropdown = () => {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    nextTick(() => {
      searchInputRef.value?.focus()
    })
  }
}

const closeDropdown = () => {
  isOpen.value = false
  searchQuery.value = ''
}

const selectCountry = (country: GeoCountryMeta) => {
  emit('update:modelValue', country.dialCode)
  emit('select', country)
  closeDropdown()
}

// 点击外部关闭
const handleDocumentClick = (e: MouseEvent) => {
  if (containerRef.value && !containerRef.value.contains(e.target as Node)) {
    closeDropdown()
  }
}

onMounted(() => {
  document.addEventListener('click', handleDocumentClick)
})

onUnmounted(() => {
  document.removeEventListener('click', handleDocumentClick)
})
</script>

<style scoped>
.country-dial-select {
  position: relative;
  display: inline-block;
  user-select: none;
}

.dial-trigger {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 44px;
  padding: 0 10px;
  background: #f4eee4;
  border: 1px solid #dcd1c0;
  border-right: none;
  border-radius: 8px 0 0 8px;
  color: #1a2a30;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.dial-trigger:hover,
.dial-trigger.is-open {
  background: #eae2d3;
  color: #0d222e;
}

.dial-trigger.is-dark {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.18);
  color: #f8fafc;
}

.dial-trigger.is-dark:hover,
.dial-trigger.is-dark.is-open {
  background: rgba(255, 255, 255, 0.16);
  border-color: rgba(255, 255, 255, 0.3);
}

.trigger-flag {
  font-size: 16px;
  line-height: 1;
}

.trigger-code {
  font-variant-numeric: tabular-nums;
  font-size: 13px;
}

.trigger-arrow {
  color: #718096;
  transition: transform 0.2s ease;
}

.dial-trigger.is-open .trigger-arrow {
  transform: rotate(180deg);
}

/* 下拉菜单 */
.dial-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  z-index: 1050;
  width: 270px;
  max-width: 85vw;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.15), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  animation: dial-fade-in 0.15s ease-out;
}

.dial-dropdown.is-dark {
  background: #132f38;
  border-color: rgba(255, 255, 255, 0.15);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.35);
}

.dial-search-box {
  position: relative;
  padding: 8px;
  border-bottom: 1px solid #edf2f7;
  background: #fafafa;
}

.dial-dropdown.is-dark .dial-search-box {
  background: #0f242c;
  border-bottom-color: rgba(255, 255, 255, 0.1);
}

.dial-search-input {
  width: 100%;
  height: 32px;
  padding: 0 24px 0 8px;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  font-size: 12px;
  background: #ffffff;
  color: #1e293b;
  outline: none;
  box-sizing: border-box;
}

.dial-search-input:focus {
  border-color: #084d50;
  box-shadow: 0 0 0 2px rgba(8, 77, 80, 0.15);
}

.dial-dropdown.is-dark .dial-search-input {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
  color: #f8fafc;
}

.dial-dropdown.is-dark .dial-search-input:focus {
  border-color: #f1b68f;
  box-shadow: 0 0 0 2px rgba(241, 182, 143, 0.25);
}

.search-clear {
  position: absolute;
  right: 14px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #94a3b8;
  font-size: 12px;
  cursor: pointer;
  padding: 4px;
}

.dial-list {
  max-height: 220px;
  overflow-y: auto;
  list-style: none;
  padding: 4px 0;
  margin: 0;
  -webkit-overflow-scrolling: touch;
}

.dial-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  gap: 8px;
  cursor: pointer;
  font-size: 13px;
  color: #334155;
  transition: background 0.15s ease;
}

.dial-dropdown.is-dark .dial-item {
  color: #e2e8f0;
}

.dial-item:hover {
  background: #f1f5f9;
}

.dial-dropdown.is-dark .dial-item:hover {
  background: rgba(255, 255, 255, 0.08);
}

.dial-item.is-active {
  background: #e6f4f2;
  font-weight: 600;
  color: #084d50;
}

.dial-dropdown.is-dark .dial-item.is-active {
  background: rgba(241, 182, 143, 0.15);
  color: #f1b68f;
}

.item-flag {
  font-size: 15px;
  line-height: 1;
}

.item-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-code {
  font-variant-numeric: tabular-nums;
  color: #64748b;
  font-size: 12px;
}

.dial-dropdown.is-dark .item-code {
  color: #94a3b8;
}

.dial-empty {
  padding: 16px;
  text-align: center;
  font-size: 12px;
  color: #94a3b8;
}

@keyframes dial-fade-in {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
