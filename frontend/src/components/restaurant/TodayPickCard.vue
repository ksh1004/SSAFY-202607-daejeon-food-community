<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { getRestaurants } from '@/api/restaurantApi'

const SPIN_DURATION_MS = 1200
const SPIN_INTERVAL_MS = 80

const restaurants = ref([])
const isLoadingList = ref(true)
const errorMessage = ref('')

const pick = ref(null)
const spinDisplay = ref(null)
const isSpinning = ref(false)

let spinTimer = null
let stopTimer = null

const randomRestaurant = (excludeId = null) => {
  const pool = excludeId
    ? restaurants.value.filter((restaurant) => restaurant.id !== excludeId)
    : restaurants.value
  const source = pool.length > 0 ? pool : restaurants.value
  return source[Math.floor(Math.random() * source.length)]
}

const stopTimers = () => {
  clearInterval(spinTimer)
  clearTimeout(stopTimer)
  spinTimer = null
  stopTimer = null
}

const draw = () => {
  if (restaurants.value.length === 0 || isSpinning.value) return

  isSpinning.value = true

  spinTimer = setInterval(() => {
    spinDisplay.value = randomRestaurant()
  }, SPIN_INTERVAL_MS)

  stopTimer = setTimeout(() => {
    clearInterval(spinTimer)
    spinTimer = null

    const result = randomRestaurant(pick.value?.id)
    pick.value = result
    spinDisplay.value = result
    isSpinning.value = false
  }, SPIN_DURATION_MS)
}

onMounted(async () => {
  try {
    const response = await getRestaurants()
    restaurants.value = response.data
  } catch {
    errorMessage.value = '음식점 정보를 불러오지 못했습니다.'
  } finally {
    isLoadingList.value = false
  }
})

onUnmounted(stopTimers)
</script>

<template>
  <section class="today-pick">
    <div class="today-pick__label">
      <span class="today-pick__emoji" aria-hidden="true">🎲</span>
      <div>
        <span class="today-pick__eyebrow">랜덤 맛집 뽑기</span>
        <p class="today-pick__hint">버튼을 눌러 오늘 갈 동네 맛집을 뽑아보세요!</p>
      </div>
    </div>

    <p v-if="isLoadingList" class="today-pick__status">불러오는 중...</p>
    <p v-else-if="errorMessage" class="today-pick__status">{{ errorMessage }}</p>

    <template v-else>
      <div class="today-pick__card" :class="{ 'today-pick__card--spinning': isSpinning }">
        <template v-if="spinDisplay">
          <img
            v-if="spinDisplay.image"
            :src="spinDisplay.image"
            :alt="spinDisplay.name"
            class="today-pick__image"
          />
          <div v-else class="today-pick__image today-pick__image--empty" aria-hidden="true">🍽️</div>

          <div class="today-pick__info">
            <span v-if="spinDisplay.region" class="today-pick__badge">{{ spinDisplay.region }}</span>
            <strong class="today-pick__name">{{ spinDisplay.name }}</strong>
            <span class="today-pick__address">{{ spinDisplay.roadAddress }}</span>
          </div>
        </template>

        <p v-else class="today-pick__placeholder">두근두근... 어떤 맛집이 나올까요?</p>
      </div>

      <div class="today-pick__actions">
        <RouterLink
          v-if="pick && !isSpinning"
          :to="{ name: 'restaurant-detail', params: { restaurantId: pick.id } }"
          class="today-pick__button today-pick__button--primary"
        >
          상세보기
        </RouterLink>

        <button
          type="button"
          class="today-pick__button"
          :class="{ 'today-pick__button--primary': !pick }"
          :disabled="isSpinning"
          @click="draw"
        >
          {{ isSpinning ? '뽑는 중...' : pick ? '다시 뽑기' : '뽑기' }}
        </button>
      </div>
    </template>
  </section>
</template>

<style scoped>
.today-pick {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 20px;
  width: min(100% - 48px, var(--content-width));
  margin: 32px auto 0;
  padding: 22px 26px;
  border: 1px solid var(--color-primary-200);
  border-radius: var(--radius-xl);
  background: var(--color-primary-50);
}

.today-pick__label {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  gap: 12px;
  min-width: 200px;
}

.today-pick__emoji {
  font-size: 30px;
}

.today-pick__eyebrow {
  display: block;
  color: var(--color-primary);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.06em;
}

.today-pick__hint {
  margin: 4px 0 0;
  color: var(--color-text-secondary);
  font-size: 13px;
}

.today-pick__status {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 14px;
}

.today-pick__card {
  display: flex;
  flex: 1;
  flex-wrap: wrap;
  align-items: center;
  gap: 16px;
  min-width: 280px;
  min-height: 64px;
}

.today-pick__card--spinning {
  animation: today-pick-shake 0.15s ease-in-out infinite;
}

.today-pick__placeholder {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 14px;
  font-weight: 600;
}

.today-pick__image {
  flex-shrink: 0;
  width: 64px;
  height: 64px;
  border-radius: var(--radius-md);
  object-fit: cover;
}

.today-pick__image--empty {
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-surface);
  font-size: 26px;
}

.today-pick__info {
  display: flex;
  min-width: 160px;
  flex: 1;
  flex-direction: column;
  gap: 3px;
}

.today-pick__badge {
  width: fit-content;
  padding: 2px 8px;
  border-radius: 999px;
  background: var(--color-primary);
  color: #ffffff;
  font-size: 11px;
  font-weight: 700;
}

.today-pick__name {
  font-size: 16px;
}

.today-pick__address {
  overflow: hidden;
  color: var(--color-text-secondary);
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.today-pick__actions {
  display: flex;
  flex-shrink: 0;
  gap: 8px;
}

.today-pick__button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 40px;
  padding: 0 16px;
  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: var(--color-text-primary);
  font-size: 13px;
  font-weight: 700;
  text-decoration: none;
  cursor: pointer;
}

.today-pick__button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.today-pick__button--primary {
  border-color: transparent;
  background: var(--color-primary);
  color: #ffffff;
}

.today-pick__button--primary:hover:not(:disabled) {
  background: var(--color-primary-hover);
}

@keyframes today-pick-shake {
  0%,
  100% {
    transform: translateY(0);
  }

  50% {
    transform: translateY(-3px);
  }
}

@media (max-width: 767px) {
  .today-pick {
    width: min(100% - 32px, var(--content-width));
    margin-top: 20px;
    padding: 18px;
  }

  .today-pick__actions {
    width: 100%;
  }

  .today-pick__button {
    flex: 1;
  }
}
</style>
