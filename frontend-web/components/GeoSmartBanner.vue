<template>
  <transition name="geo-slide">
    <div v-if="smartRecommendation" class="geo-smart-banner" role="region" aria-label="Jurisdiction Recommendation">
      <div class="wrap geo-banner-wrap">
        <div class="geo-banner-content">
          <span class="geo-flag" aria-hidden="true">{{ smartRecommendation.flag }}</span>
          <span class="geo-text">{{ smartRecommendation.text }}</span>
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

          <button
            type="button"
            class="geo-close-btn"
            aria-label="关闭提示"
            @click="onDismiss"
          >
            ✕
          </button>
        </div>
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
}

.geo-banner-wrap {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  gap: 12px;
  min-height: 40px;
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
  overflow: hidden;
  text-overflow: ellipsis;
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
  font-size: 13px;
  cursor: pointer;
  padding: 4px 6px;
  line-height: 1;
  border-radius: 3px;
  transition: color 0.15s ease;
}

.geo-close-btn:hover {
  color: #ffffff;
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

@media (max-width: 768px) {
  .geo-banner-wrap {
    flex-direction: column;
    align-items: flex-start;
    padding: 10px 14px;
    gap: 8px;
  }

  .geo-banner-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .geo-text {
    font-size: 12px;
  }
}
</style>
