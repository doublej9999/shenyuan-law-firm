<template>
  <transition name="geo-slide">
    <div v-if="smartRecommendation" class="geo-smart-banner" role="region" aria-label="Jurisdiction Recommendation">
      <div class="wrap geo-banner-wrap">
        <div class="geo-banner-content">
          <span class="geo-flag" aria-hidden="true">{{ smartRecommendation.flag }}</span>
          <span class="geo-text geo-text-full">{{ smartRecommendation.text }}</span>
          <span class="geo-text geo-text-short">{{ smartRecommendation.shortText || smartRecommendation.text }}</span>
        </div>

        <div class="geo-banner-actions">
          <NuxtLink
            v-if="smartRecommendation.actionUrl"
            :to="smartRecommendation.actionUrl"
            class="geo-btn geo-btn-primary"
            @click="onActionClick"
          >
            {{ smartRecommendation.actionLabel }}
          </NuxtLink>

          <NuxtLink
            v-if="smartRecommendation.langSwitchUrl"
            :to="smartRecommendation.langSwitchUrl"
            class="geo-btn geo-btn-secondary"
            @click="onActionClick"
          >
            {{ smartRecommendation.langSwitchLabel }}
          </NuxtLink>
        </div>

        <button
          type="button"
          class="geo-close-btn"
          aria-label="关闭提示"
          @click.stop="onDismiss"
        >
          ✕
        </button>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { useUserGeo } from '@/composables/useUserGeo'

const { smartRecommendation, dismissBanner } = useUserGeo()

const onActionClick = () => {
  dismissBanner()
}

const onDismiss = () => {
  dismissBanner()
}
</script>

<style scoped>
.geo-smart-banner {
  background: linear-gradient(90deg, #0d222e 0%, #163647 100%);
  color: #f8fafc;
  font-size: 13px;
  line-height: 1.4;
  border-bottom: 1px solid rgba(241, 182, 143, 0.25);
  position: relative;
  z-index: 1000;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
  padding-top: env(safe-area-inset-top, 0);
}

.geo-banner-wrap {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  gap: 12px;
  min-height: 40px;
  position: relative;
}

.geo-banner-content {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.geo-flag {
  font-size: 16px;
  line-height: 1;
  flex-shrink: 0;
}

.geo-text {
  color: #e2e8f0;
  font-weight: 400;
  letter-spacing: normal;
}

.geo-text-full {
  display: inline;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.geo-text-short {
  display: none;
}

.geo-banner-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.geo-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 4px;
  text-decoration: none;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.geo-btn-primary {
  background: #f1b68f;
  color: #0d222e;
}

.geo-btn-primary:hover {
  background: #f5cca8;
  box-shadow: 0 2px 6px rgba(241, 182, 143, 0.3);
}

.geo-btn-secondary {
  background: rgba(255, 255, 255, 0.12);
  color: #f8fafc;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.geo-btn-secondary:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.35);
}

.geo-close-btn {
  background: none;
  border: none;
  color: #94a3b8;
  font-size: 14px;
  cursor: pointer;
  padding: 6px 8px;
  line-height: 1;
  border-radius: 4px;
  transition: all 0.15s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.geo-close-btn:hover {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.1);
}

.geo-slide-enter-active,
.geo-slide-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.geo-slide-enter-from,
.geo-slide-leave-to {
  transform: translateY(-100%);
  opacity: 0;
}

/* 移动端紧凑响应式适配 (< 768px) */
@media (max-width: 768px) {
  .geo-smart-banner {
    padding-top: max(4px, env(safe-area-inset-top));
  }

  .geo-banner-wrap {
    flex-direction: column;
    align-items: flex-start;
    padding: 8px 12px 10px 12px;
    gap: 6px;
    min-height: auto;
  }

  .geo-banner-content {
    width: 100%;
    padding-right: 36px; /* 为右上角关闭按钮留足安全空间，防止重叠 */
    align-items: flex-start;
  }

  .geo-flag {
    margin-top: 1px;
    font-size: 15px;
  }

  .geo-text-full {
    display: none;
  }

  .geo-text-short {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    font-size: 12px;
    line-height: 1.35;
    color: #e2e8f0;
  }

  .geo-banner-actions {
    width: 100%;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 6px;
    margin-top: 2px;
  }

  .geo-btn {
    font-size: 11px;
    padding: 4px 10px;
    border-radius: 4px;
  }

  /* 右上角固定关闭按钮，提供舒适的防误触热区 */
  .geo-close-btn {
    position: absolute;
    top: 6px;
    right: 6px;
    width: 32px;
    height: 32px;
    padding: 0;
    font-size: 13px;
    color: #94a3b8;
  }

  .geo-close-btn:active {
    color: #ffffff;
    background: rgba(255, 255, 255, 0.15);
  }
}
</style>
