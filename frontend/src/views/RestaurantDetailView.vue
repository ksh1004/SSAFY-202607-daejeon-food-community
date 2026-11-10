<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { getRestaurantById, getRestaurantPosts } from '@/api/restaurantApi'
import { useRegionBadges } from '@/composables/useRegionBadges'

const props = defineProps({
  restaurantId: {
    type: String,
    required: true,
  },
})

const router = useRouter()
const { recordVisit } = useRegionBadges()

const restaurant = ref(null)
const isLoading = ref(false)
const errorMessage = ref('')
const justEarnedBadge = ref(false)

const posts = ref([])
const isPostsLoading = ref(false)
const postsMessage = ref('')

const fetchRestaurant = async (restaurantId) => {
  isLoading.value = true
  errorMessage.value = ''
  restaurant.value = null
  justEarnedBadge.value = false

  try {
    const response = await getRestaurantById(restaurantId)

    if (!response.data) {
      errorMessage.value = '음식점 정보를 찾을 수 없습니다.'
      return
    }

    restaurant.value = response.data

    if (restaurant.value.region) {
      justEarnedBadge.value = recordVisit(restaurant.value.region)
    }
  } catch {
    errorMessage.value =
      '음식점 정보를 불러오지 못했습니다. 잠시 후 다시 시도해주세요.'
  } finally {
    isLoading.value = false
  }
}

const fetchPosts = async (restaurantId) => {
  isPostsLoading.value = true
  postsMessage.value = ''
  posts.value = []

  try {
    const response = await getRestaurantPosts(restaurantId)
    const data = response.data

    posts.value = Array.isArray(data)
      ? data
      : (data?.items ?? data?.results ?? [])

    if (posts.value.length === 0) {
      postsMessage.value = '아직 등록된 관련 게시글이 없습니다.'
    }
  } catch {
    postsMessage.value =
      '관련 게시글을 불러오지 못했습니다. 잠시 후 다시 시도해주세요.'
  } finally {
    isPostsLoading.value = false
  }
}

const load = (restaurantId) => {
  fetchRestaurant(restaurantId)
  fetchPosts(restaurantId)
}

watch(
  () => props.restaurantId,
  (restaurantId) => {
    load(restaurantId)
  },
  {
    immediate: true,
  },
)

const viewOnMap = () => {
  router.push({
    name: 'restaurant-explore',
    query: {
      focus: props.restaurantId,
    },
  })
}

const formatPostDate = (dateValue) => {
  if (!dateValue) {
    return ''
  }

  const date = new Date(dateValue)

  if (Number.isNaN(date.getTime())) {
    return ''
  }

  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  })
}
</script>

<template>
  <main class="restaurant-detail-page">
    <!-- 음식점 상세 Hero -->
    <section class="detail-hero">
      <div class="detail-hero__inner">
        <!-- 로딩 -->
        <div
          v-if="isLoading"
          class="detail-state detail-state--hero"
          aria-live="polite"
        >
          <span class="detail-state__icon" aria-hidden="true">···</span>

          <strong>음식점 정보를 불러오고 있어요.</strong>

          <p>잠시만 기다려 주세요.</p>
        </div>

        <!-- 오류 -->
        <div
          v-else-if="errorMessage"
          class="detail-state detail-state--hero detail-state--error"
          role="alert"
        >
          <span class="detail-state__icon" aria-hidden="true">!</span>

          <strong>음식점 정보를 불러오지 못했어요.</strong>

          <p>{{ errorMessage }}</p>

          <button
            type="button"
            class="detail-state__button"
            @click="load(props.restaurantId)"
          >
            다시 시도
          </button>
        </div>

        <!-- 음식점 정보 -->
        <template v-else-if="restaurant">
          <div class="detail-hero__content">
            <RouterLink
              :to="{ name: 'restaurant-explore' }"
              class="detail-back"
            >
              <svg
                class="detail-back__icon"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path d="m15 18-6-6 6-6" />
              </svg>

              지도 탐색으로 돌아가기
            </RouterLink>

            <span
              v-if="restaurant.region"
              class="detail-region"
            >
              <span
                class="detail-region__dot"
                aria-hidden="true"
              ></span>

              {{ restaurant.region }}
            </span>

            <h1 class="detail-hero__title">
              {{ restaurant.name }}
            </h1>

            <p class="detail-hero__description">
              지도에서 발견한 지역 맛집의 위치와 정보를 확인하고,<br />
              방문자들의 관련 이야기도 함께 살펴보세요.
            </p>

            <div
              class="detail-hero__facts"
              aria-label="음식점 주요 정보"
            >
              <span class="detail-hero__fact">
                <svg
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    d="M12 21s6-5.1 6-11a6 6 0 1 0-12 0c0 5.9 6 11 6 11Z"
                  />
                  <circle cx="12" cy="10" r="2.2" />
                </svg>

                {{ restaurant.roadAddress || '주소 정보 없음' }}
              </span>

              <span
                v-if="restaurant.tel"
                class="detail-hero__fact"
              >
                <svg
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    d="M7.2 3.5 9.7 6c.5.5.6 1.2.2 1.8L8.6 9.7a15.4 15.4 0 0 0 5.7 5.7l1.9-1.3c.6-.4 1.3-.3 1.8.2l2.5 2.5c.6.6.6 1.5.1 2.1-1 1.2-2.5 1.8-4 1.5-6.9-1.4-11.6-6.1-13-13-.3-1.5.3-3 1.5-4 .6-.5 1.5-.5 2.1.1Z"
                  />
                </svg>

                {{ restaurant.tel }}
              </span>
            </div>
          </div>

          <!-- 음식점 이미지 -->
          <div class="detail-visual">
            <div
              class="detail-visual__frame"
              :class="{
                'detail-visual__frame--empty': !restaurant.image,
              }"
            >
              <img
                v-if="restaurant.image"
                :src="restaurant.image"
                :alt="`${restaurant.name} 음식점 이미지`"
              />

              <div
                v-else
                class="detail-visual__empty"
              >
                <svg
                  class="detail-visual__empty-terrain"
                  viewBox="0 0 400 240"
                  preserveAspectRatio="none"
                  aria-hidden="true"
                >
                  <path
                    d="
                      M48 35
                      C104 10 151 21 194 42
                      C240 64 290 38 343 66
                      C386 89 389 143 352 175
                      C315 207 269 197 225 214
                      C178 232 132 210 88 215
                      C39 221 12 184 17 135
                      C21 86 14 52 48 35Z
                    "
                  />

                  <path
                    class="detail-visual__route"
                    d="
                      M55 185
                      C96 173 108 129 148 135
                      C190 141 196 89 238 94
                      C280 99 296 62 347 53
                    "
                  />
                </svg>

                <span class="detail-visual__pin">
                  <svg viewBox="0 0 24 24">
                    <path
                      d="M12 21s6-5.1 6-11a6 6 0 1 0-12 0c0 5.9 6 11 6 11Z"
                    />
                    <circle cx="12" cy="10" r="2.2" />
                  </svg>
                </span>

                <span class="detail-visual__empty-text">
                  이미지 준비 중
                </span>
              </div>

              <div class="detail-visual__overlay">
                <span v-if="restaurant.region">
                  {{ restaurant.region }}
                </span>

                <strong>{{ restaurant.name }}</strong>
              </div>
            </div>

            <button
              type="button"
              class="detail-map-button"
              @click="viewOnMap"
            >
              <span
                class="detail-map-button__icon"
                aria-hidden="true"
              >
                <svg viewBox="0 0 24 24">
                  <path
                    d="M12 21s6-5.1 6-11a6 6 0 1 0-12 0c0 5.9 6 11 6 11Z"
                  />
                  <circle cx="12" cy="10" r="2.2" />
                </svg>
              </span>

              <strong>지도에서 위치 확인</strong>

              <span
                class="detail-map-button__arrow"
                aria-hidden="true"
              >
                →
              </span>
            </button>
          </div>
        </template>
      </div>
    </section>

    <!-- 신규 뱃지 알림 -->
    <section
      v-if="restaurant && justEarnedBadge"
      class="detail-badge-notice"
    >
      <div class="detail-badge-notice__inner">
        <span
          class="detail-badge-notice__icon"
          aria-hidden="true"
        >
          ★
        </span>

        <div>
          <span>NEW REGION BADGE</span>

          <strong>
            {{ restaurant.region }} 지역 뱃지를 획득했어요!
          </strong>

          <p>
            서비스 소개 페이지에서 지금까지 모은 지역 컬렉션을
            확인해보세요.
          </p>
        </div>
      </div>
    </section>

    <!-- 상세 콘텐츠 -->
    <section
      v-if="restaurant"
      class="detail-content"
    >
      <div class="detail-content__inner">
        <div class="detail-content__summary">
          <div>
            <span class="detail-content__eyebrow">
              PLACE INFORMATION
            </span>

            <strong>맛집 정보와 지역 이야기를 확인해보세요.</strong>
          </div>

          <p>
            방문 전 위치와 연락처를 확인하고 관련 게시글을 살펴볼 수 있어요.
          </p>
        </div>

        <div class="detail-content__grid">
          <!-- 방문 정보 -->
          <aside class="detail-info-panel">
            <div class="detail-panel-heading">
              <div>
                <span>INFORMATION</span>
                <strong>방문 정보</strong>
              </div>

              <span
                class="detail-panel-heading__icon"
                aria-hidden="true"
              >
                i
              </span>
            </div>

            <div class="detail-info-panel__body">
              <dl class="detail-info-list">
                <div class="detail-info-list__item">
                  <dt>음식점명</dt>
                  <dd>{{ restaurant.name }}</dd>
                </div>

                <div class="detail-info-list__item">
                  <dt>지역</dt>
                  <dd>{{ restaurant.region || '지역 정보 없음' }}</dd>
                </div>

                <div class="detail-info-list__item">
                  <dt>도로명 주소</dt>
                  <dd>
                    {{ restaurant.roadAddress || '주소 정보 없음' }}
                  </dd>
                </div>

                <div
                  v-if="restaurant.jibunAddress"
                  class="detail-info-list__item"
                >
                  <dt>지번 주소</dt>
                  <dd>{{ restaurant.jibunAddress }}</dd>
                </div>

                <div class="detail-info-list__item">
                  <dt>전화번호</dt>
                  <dd>{{ restaurant.tel || '전화번호 정보 없음' }}</dd>
                </div>
              </dl>

              <button
                type="button"
                class="detail-info-map"
                @click="viewOnMap"
              >
                <svg
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    d="M12 21s6-5.1 6-11a6 6 0 1 0-12 0c0 5.9 6 11 6 11Z"
                  />
                  <circle cx="12" cy="10" r="2.2" />
                </svg>

                지도에서 다시 확인
              </button>
            </div>
          </aside>

          <!-- 관련 게시글 -->
          <section class="detail-post-panel">
            <div class="detail-panel-heading">
              <div>
                <span>COMMUNITY STORIES</span>
                <strong>관련 게시글</strong>
              </div>

              <span class="detail-panel-heading__count">
                {{ posts.length }}
              </span>
            </div>

            <div class="detail-post-panel__body">
              <!-- 게시글 로딩 -->
              <div
                v-if="isPostsLoading"
                class="detail-state"
                aria-live="polite"
              >
                <span class="detail-state__icon" aria-hidden="true">
                  ···
                </span>

                <strong>관련 게시글을 불러오고 있어요.</strong>

                <p>잠시만 기다려 주세요.</p>
              </div>

              <!-- 게시글 오류 -->
              <div
                v-else-if="
                  postsMessage &&
                  posts.length === 0 &&
                  postsMessage.includes('불러오지 못했습니다')
                "
                class="detail-state detail-state--error"
                role="alert"
              >
                <span class="detail-state__icon" aria-hidden="true">
                  !
                </span>

                <strong>관련 게시글을 불러오지 못했어요.</strong>

                <p>{{ postsMessage }}</p>

                <button
                  type="button"
                  class="detail-state__button"
                  @click="fetchPosts(props.restaurantId)"
                >
                  다시 시도
                </button>
              </div>

              <!-- 게시글 없음 -->
              <div
                v-else-if="posts.length === 0"
                class="detail-state"
              >
                <span
                  class="detail-state__empty-icon"
                  aria-hidden="true"
                >
                  ✎
                </span>

                <strong>아직 등록된 이야기가 없어요.</strong>

                <p>
                  이 음식점에 관한 첫 번째 지역 이야기를 기다리고 있어요.
                </p>
              </div>

              <!-- 게시글 목록 -->
              <ul
                v-else
                class="detail-post-list"
              >
                <li
                  v-for="post in posts"
                  :key="post.id"
                  class="detail-post-list__item"
                >
                  <RouterLink
                    :to="{
                      name: 'post-detail',
                      params: {
                        postId: post.id,
                      },
                    }"
                    class="detail-post-card"
                  >
                    <div class="detail-post-card__content">
                      <span class="detail-post-card__eyebrow">
                        LOCAL STORY
                      </span>

                      <strong class="detail-post-card__title">
                        {{ post.title }}
                      </strong>

                      <span
                        v-if="post.created_at"
                        class="detail-post-card__date"
                      >
                        {{ formatPostDate(post.created_at) }}
                      </span>
                    </div>

                    <span
                      class="detail-post-card__arrow"
                      aria-hidden="true"
                    >
                      →
                    </span>
                  </RouterLink>
                </li>
              </ul>
            </div>
          </section>
        </div>
      </div>
    </section>
  </main>
</template>

<style scoped>
.restaurant-detail-page {
  min-height: 100vh;

  background: var(--color-background);
  color: var(--color-text-primary);
}

/* =================================
   공통 너비
================================= */

.detail-hero__inner,
.detail-badge-notice__inner,
.detail-content__inner {
  width: min(100% - 48px, var(--content-width));
  margin: 0 auto;
}

/* =================================
   상세 Hero
================================= */

.detail-hero {
  border-bottom: 1px solid var(--color-border);

  background: #f6f1ed;
}

.detail-hero__inner {
  position: relative;

  display: grid;
  grid-template-columns: minmax(0, 1fr) 400px;
  align-items: center;
  gap: 64px;

  height: var(--subpage-hero-height, 356px);
  min-height: 0;
  padding: var(--subpage-hero-padding-y, 44px) 0;

  box-sizing: border-box;
}

.detail-hero__content {
  display: flex;
  min-width: 0;
  max-width: 720px;
  align-items: flex-start;
  flex-direction: column;
  justify-content: center;
}

.detail-back {
  position: absolute;
  top: 18px;
  left: 0;

  display: inline-flex;
  align-items: center;
  gap: 5px;

  color: var(--color-text-secondary);

  font-size: 11px;
  font-weight: 750;
  text-decoration: none;

  transition:
    color var(--transition-fast),
    transform var(--transition-fast);
}

.detail-back:hover {
  color: var(--color-primary);

  transform: translateX(-2px);
}

.detail-back__icon {
  width: 15px;
  height: 15px;

  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 2;
}

.detail-region {
  display: inline-flex;
  align-items: center;
  gap: 6px;

  margin-bottom: 14px;
  padding: 6px 10px;

  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-pill);

  background: rgba(255, 255, 255, 0.5);
  color: var(--color-primary-active);

  font-size: 10px;
  font-weight: 800;
}

.detail-region__dot {
  width: 5px;
  height: 5px;

  border-radius: 50%;

  background: var(--color-primary);
}

.detail-hero__title {
  margin: 0;

  color: var(--color-text-primary);

  font-size: clamp(36px, 3.6vw, 46px);
  font-weight: 850;
  line-height: 1.18;
  letter-spacing: -0.055em;

  word-break: keep-all;
}

.detail-hero__description {
  max-width: 650px;
  margin: 17px 0 0;

  color: var(--color-text-secondary);

  font-size: 15px;
  line-height: 1.72;
  word-break: keep-all;
}

.detail-hero__facts {
  display: flex;
  max-width: 100%;
  flex-wrap: wrap;
  gap: 8px;

  margin-top: 21px;
}

.detail-hero__fact {
  display: inline-flex;
  min-width: 0;
  max-width: 440px;
  align-items: center;
  gap: 7px;

  padding: 6px 10px;

  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-pill);

  background: rgba(255, 255, 255, 0.5);
  color: var(--color-text-secondary);

  font-size: 11px;
  font-weight: 700;
  line-height: 1.35;
}

.detail-hero__fact svg {
  width: 13px;
  height: 13px;

  flex-shrink: 0;

  fill: none;
  stroke: var(--color-primary);
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.8;
}

/* =================================
   음식점 이미지
================================= */

.detail-visual {
  position: relative;

  width: 400px;
  height: 260px;
  justify-self: end;

  transition: transform var(--transition-base);
}

.detail-visual:hover {
  transform: translateY(-4px);
}

.detail-visual__frame {
  position: absolute;
  inset: 0 0 20px;

  overflow: hidden;

  border: 1px solid rgba(255, 122, 69, 0.14);
  border-radius: var(--radius-lg);

  background: var(--color-primary-50);

  box-shadow:
    0 18px 42px rgba(93, 54, 34, 0.1);
}

.detail-visual__frame::after {
  position: absolute;
  inset: auto 0 0;
  z-index: 1;

  height: 48%;

  background: linear-gradient(
    to top,
    rgba(45, 31, 25, 0.72),
    rgba(45, 31, 25, 0)
  );

  content: '';
  pointer-events: none;
}

.detail-visual__frame img {
  width: 100%;
  height: 100%;

  object-fit: cover;

  transition: transform 0.5s ease;
}

.detail-visual:hover .detail-visual__frame img {
  transform: scale(1.035);
}

.detail-visual__frame--empty {
  background:
    linear-gradient(
      145deg,
      rgba(255, 255, 255, 0.3),
      rgba(255, 122, 69, 0.04)
    ),
    var(--color-primary-50);
}

.detail-visual__frame--empty::after {
  background: linear-gradient(
    to top,
    rgba(255, 255, 255, 0.92),
    rgba(255, 255, 255, 0)
  );
}

.detail-visual__empty {
  position: relative;

  display: flex;
  width: 100%;
  height: 100%;
  align-items: center;
  justify-content: center;
  flex-direction: column;

  overflow: hidden;
}

.detail-visual__empty-terrain {
  position: absolute;
  inset: 0;

  width: 100%;
  height: 100%;
}

.detail-visual__empty-terrain path:first-child {
  fill: rgba(255, 255, 255, 0.57);
  stroke: rgba(255, 122, 69, 0.15);
  stroke-width: 1.3;
}

.detail-visual__route {
  fill: none;
  stroke: var(--color-primary);
  stroke-width: 2.5;
  stroke-dasharray: 7 9;
  stroke-linecap: round;

  opacity: 0.4;

  animation: detail-route-move 7s linear infinite;
}

.detail-visual__pin {
  position: relative;
  z-index: 2;

  display: grid;
  place-items: center;

  width: 57px;
  height: 57px;

  border-radius: 20px;

  background: var(--color-primary);
  color: #ffffff;

  box-shadow:
    0 14px 27px rgba(255, 122, 69, 0.24);

  animation: detail-pin-float 3.3s ease-in-out infinite;
}

.detail-visual__pin svg {
  width: 28px;
  height: 28px;

  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.8;
}

.detail-visual__empty-text {
  position: relative;
  z-index: 2;

  margin-top: 10px;
  padding: 6px 9px;

  border: 1px solid var(--color-border);
  border-radius: 10px;

  background: rgba(255, 255, 255, 0.88);
  color: var(--color-text-disabled);

  font-size: 9px;
  font-weight: 700;

  backdrop-filter: blur(8px);
}

.detail-visual__overlay {
  position: absolute;
  right: 16px;
  bottom: 18px;
  left: 16px;
  z-index: 3;

  display: flex;
  min-width: 0;
  align-items: flex-start;
  flex-direction: column;
  gap: 5px;

  padding-right: 176px;
}

.detail-visual__overlay span {
  padding: 4px 7px;

  border-radius: var(--radius-pill);

  background: rgba(255, 255, 255, 0.88);
  color: var(--color-primary-active);

  font-size: 9px;
  font-weight: 800;
}

.detail-visual__overlay strong {
  overflow: hidden;

  max-width: 100%;

  color: #ffffff;

  font-size: 15px;
  line-height: 1.3;
  letter-spacing: -0.025em;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.detail-visual__frame--empty .detail-visual__overlay strong {
  color: var(--color-text-primary);
}

.detail-map-button {
  position: absolute;
  right: 3px;
  bottom: 0;
  z-index: 7;

  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 9px;

  width: 208px;
  min-height: 42px;

  box-sizing: border-box;
  padding: 0 13px;

  border: 0;
  border-radius: var(--radius-md);

  background: var(--color-primary);
  color: #ffffff;

  font: inherit;
  font-size: 11px;
  font-weight: 750;

  box-shadow:
    0 9px 19px rgba(255, 122, 69, 0.2);

  cursor: pointer;

  transition:
    background-color var(--transition-fast),
    box-shadow var(--transition-fast),
    transform var(--transition-fast);
}

.detail-map-button:hover {
  background: var(--color-primary-hover);

  box-shadow:
    0 13px 23px rgba(255, 122, 69, 0.27);

  transform: translateY(-2px);
}

.detail-map-button__icon {
  display: grid;
  place-items: center;

  width: 25px;
  height: 25px;

  border-radius: 8px;

  background: rgba(255, 255, 255, 0.17);
}

.detail-map-button__icon svg {
  width: 14px;
  height: 14px;

  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.9;
}

.detail-map-button__arrow {
  font-size: 14px;

  transition: transform var(--transition-fast);
}

.detail-map-button:hover .detail-map-button__arrow {
  transform: translateX(4px);
}

/* =================================
   뱃지 획득 알림
================================= */

.detail-badge-notice {
  border-bottom: 1px solid var(--color-border);

  background: #ffffff;
}

.detail-badge-notice__inner {
  display: flex;
  align-items: center;
  gap: 14px;

  padding-top: 18px;
  padding-bottom: 18px;
}

.detail-badge-notice__icon {
  display: grid;
  place-items: center;

  width: 45px;
  height: 45px;

  flex-shrink: 0;

  border-radius: 15px;

  background: var(--color-accent-light);
  color: var(--color-primary);

  font-size: 17px;

  animation: detail-badge-pop 0.55s ease;
}

.detail-badge-notice__inner > div {
  display: flex;
  flex-direction: column;
}

.detail-badge-notice__inner span:not(.detail-badge-notice__icon) {
  margin-bottom: 3px;

  color: var(--color-primary);

  font-size: 8px;
  font-weight: 850;
  letter-spacing: 0.13em;
}

.detail-badge-notice__inner strong {
  color: var(--color-text-primary);

  font-size: 14px;
}

.detail-badge-notice__inner p {
  margin: 3px 0 0;

  color: var(--color-text-secondary);

  font-size: 11px;
  line-height: 1.5;
}

/* =================================
   상세 콘텐츠
================================= */

.detail-content {
  padding: 52px 0 80px;

  background: var(--color-background);
}

.detail-content__summary {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 28px;

  margin-bottom: 21px;
}

.detail-content__summary > div {
  display: flex;
  align-items: flex-start;
  flex-direction: column;
}

.detail-content__eyebrow {
  margin-bottom: 6px;

  color: var(--color-primary);

  font-size: 9px;
  font-weight: 850;
  letter-spacing: 0.13em;
}

.detail-content__summary strong {
  color: var(--color-text-primary);

  font-size: 22px;
  line-height: 1.35;
  letter-spacing: -0.035em;
}

.detail-content__summary p {
  margin: 0;

  color: var(--color-text-secondary);

  font-size: 13px;
}

.detail-content__grid {
  display: grid;
  grid-template-columns: 340px minmax(0, 1fr);
  align-items: start;
  gap: 18px;
}

/* =================================
   패널 공통
================================= */

.detail-info-panel,
.detail-post-panel {
  overflow: hidden;

  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);

  background: var(--color-surface);

  box-shadow: var(--shadow-card);
}

.detail-panel-heading {
  display: flex;
  min-height: 65px;
  align-items: center;
  justify-content: space-between;
  gap: 16px;

  padding: 0 18px;

  border-bottom: 1px solid var(--color-border);

  background: #ffffff;
}

.detail-panel-heading > div {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.detail-panel-heading > div span {
  color: var(--color-primary);

  font-size: 9px;
  font-weight: 850;
  letter-spacing: 0.12em;
}

.detail-panel-heading strong {
  color: var(--color-text-primary);

  font-size: 15px;
  line-height: 1.4;
}

.detail-panel-heading__icon,
.detail-panel-heading__count {
  display: grid;
  place-items: center;

  min-width: 31px;
  height: 31px;
  padding: 0 8px;

  box-sizing: border-box;

  border-radius: var(--radius-pill);

  background: var(--color-primary-50);
  color: var(--color-primary);

  font-size: 11px;
  font-weight: 800;
}

/* =================================
   방문 정보 카드
================================= */

.detail-info-panel {
  overflow: hidden;

  padding: 5px;

  border: 0;
  border-radius: var(--radius-lg);

  background:
    linear-gradient(
      145deg,
      var(--color-primary),
      #ff9b67
    );

  box-shadow:
    0 12px 28px rgba(255, 122, 69, 0.16);
}

/* 방문 정보 상단 */

.detail-info-panel .detail-panel-heading {
  min-height: 66px;

  padding: 0 17px;

  border-bottom: 0;

  background: transparent;
}

.detail-info-panel
  .detail-panel-heading
  > div
  span {
  color: rgba(255, 255, 255, 0.78);

  font-size: 9px;
  font-weight: 600;
  letter-spacing: 0.1em;
}

.detail-info-panel
  .detail-panel-heading
  strong {
  color: #ffffff;

  font-size: 16px;
  font-weight: 650;
}

.detail-info-panel
  .detail-panel-heading__icon {
  display: grid;
  min-width: 32px;
  height: 32px;
  place-items: center;

  padding: 0;

  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 10px;

  background: rgba(255, 255, 255, 0.16);
  color: #ffffff;

  font-size: 12px;
  font-weight: 600;
}

/* 안쪽 밝은 정보 영역 */

.detail-info-panel__body {
  padding: 7px 18px 17px;

  border-radius: calc(var(--radius-lg) - 5px);

  background: #fffaf6;
}

/* 정보 목록 */

.detail-info-list {
  margin: 0;
}

.detail-info-list__item {
  display: grid;
  grid-template-columns: 78px minmax(0, 1fr);
  align-items: start;
  gap: 13px;

  padding: 16px 3px;

  border-bottom: 1px solid rgba(255, 122, 69, 0.14);

  transition:
    background-color var(--transition-fast),
    padding var(--transition-fast);
}

.detail-info-list__item:first-child {
  padding-top: 16px;
}

.detail-info-list__item:last-child {
  border-bottom: 0;
}

.detail-info-list__item:hover {
  padding-right: 8px;
  padding-left: 8px;

  border-radius: 9px;

  background: rgba(255, 122, 69, 0.05);
}

/* 음식점명, 지역, 주소 */

.detail-info-list dt {
  color: var(--color-primary);

  font-size: 11px;
  font-weight: 600;
  line-height: 1.6;
}

/* 실제 정보 */

.detail-info-list dd {
  margin: 0;

  color: #4b4642;

  font-size: 14px;
  font-weight: 450;
  line-height: 1.6;

  word-break: keep-all;
}

/* 지도 버튼 */

.detail-info-map {
  display: flex;
  width: 100%;
  min-height: 46px;
  align-items: center;
  justify-content: center;
  gap: 8px;

  margin-top: 11px;
  padding: 0 14px;

  border: 1px solid rgba(255, 122, 69, 0.28);
  border-radius: 11px;

  background: #ffffff;
  color: var(--color-primary);

  font: inherit;
  font-size: 13px;
  font-weight: 600;

  cursor: pointer;

  transition:
    border-color var(--transition-fast),
    background-color var(--transition-fast),
    color var(--transition-fast),
    transform var(--transition-fast);
}

.detail-info-map:hover {
  border-color: #ffffff;

  background: var(--color-primary);
  color: #ffffff;

  transform: translateY(-1px);
}

.detail-info-map svg {
  width: 16px;
  height: 16px;

  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.8;
}

/* =================================
   관련 게시글
================================= */

.detail-post-panel__body {
  min-height: 340px;
  padding: 14px;

  background: #fafafa;
}

.detail-post-list {
  display: flex;
  flex-direction: column;
  gap: 10px;

  margin: 0;
  padding: 0;

  list-style: none;
}

.detail-post-list__item {
  min-width: 0;
}

.detail-post-card {
  position: relative;

  display: flex;
  min-height: 92px;
  align-items: center;
  justify-content: space-between;
  gap: 22px;

  overflow: hidden;

  padding: 17px 18px 16px 21px;

  border: 1px solid var(--color-border);
  border-radius: 14px;

  background: #ffffff;
  color: inherit;

  text-decoration: none;

  box-shadow:
    0 3px 10px rgba(45, 41, 38, 0.035);

  transition:
    border-color var(--transition-fast),
    background-color var(--transition-fast),
    box-shadow var(--transition-fast),
    transform var(--transition-fast);
}

.detail-post-card::before {
  position: absolute;
  top: 14px;
  bottom: 14px;
  left: 0;

  width: 3px;

  border-radius: 0 4px 4px 0;

  background: var(--color-primary);

  content: '';

  opacity: 0.55;

  transition:
    opacity var(--transition-fast),
    top var(--transition-fast),
    bottom var(--transition-fast);
}

.detail-post-card:hover {
  border-color: rgba(255, 122, 69, 0.35);

  background: #fffaf7;

  box-shadow:
    0 8px 20px rgba(93, 54, 34, 0.09);

  transform: translateY(-2px);
}

.detail-post-card:hover::before {
  top: 0;
  bottom: 0;

  opacity: 1;
}

.detail-post-card__content {
  display: flex;
  min-width: 0;
  flex: 1;
  flex-direction: column;
}

.detail-post-card__eyebrow {
  margin-bottom: 7px;

  color: var(--color-primary);

  font-size: 10px;
  font-weight: 650;
  letter-spacing: 0.1em;
}

.detail-post-card__title {
  overflow: hidden;

  color: #3f3a37;

  font-size: 16px;
  font-weight: 600;
  line-height: 1.5;
  letter-spacing: -0.015em;

  text-overflow: ellipsis;
  white-space: nowrap;

  transition: color var(--transition-fast);
}

.detail-post-card:hover .detail-post-card__title {
  color: var(--color-primary-active);
}

.detail-post-card__date {
  margin-top: 7px;

  color: var(--color-text-disabled);

  font-size: 12px;
  font-weight: 400;
}

.detail-post-card__arrow {
  display: grid;
  width: 36px;
  height: 36px;
  flex-shrink: 0;
  place-items: center;

  border: 1px solid var(--color-border-strong);
  border-radius: 50%;

  background: #ffffff;
  color: var(--color-text-secondary);

  font-size: 14px;

  transition:
    border-color var(--transition-fast),
    background-color var(--transition-fast),
    color var(--transition-fast),
    transform var(--transition-fast);
}

.detail-post-card:hover .detail-post-card__arrow {
  border-color: var(--color-primary);

  background: var(--color-primary);
  color: #ffffff;

  transform: translateX(3px);
}

/* =================================
   상태 화면
================================= */

.detail-state {
  display: flex;
  min-height: 300px;
  align-items: center;
  justify-content: center;
  flex-direction: column;

  padding: 28px 20px;

  color: var(--color-text-secondary);

  box-sizing: border-box;

  text-align: center;
}

.detail-state--hero {
  grid-column: 1 / -1;

  min-height: 260px;
}

.detail-state__icon,
.detail-state__empty-icon {
  display: grid;
  place-items: center;

  width: 52px;
  height: 52px;

  margin-bottom: 15px;

  border-radius: 17px;

  background: var(--color-primary-50);
  color: var(--color-primary);

  font-size: 18px;
  font-weight: 850;
}

.detail-state strong {
  color: var(--color-text-primary);

  font-size: 15px;
}

.detail-state p {
  max-width: 430px;
  margin: 7px 0 0;

  font-size: 12px;
  line-height: 1.6;
}

.detail-state--error .detail-state__icon {
  background: rgba(220, 38, 38, 0.08);
  color: var(--color-error);
}

.detail-state__button {
  min-height: 39px;

  margin-top: 17px;
  padding: 0 15px;

  border: 1px solid var(--color-primary);
  border-radius: var(--radius-md);

  background: #ffffff;
  color: var(--color-primary);

  font: inherit;
  font-size: 12px;
  font-weight: 750;

  cursor: pointer;

  transition:
    background-color var(--transition-fast),
    color var(--transition-fast);
}

.detail-state__button:hover {
  background: var(--color-primary);
  color: #ffffff;
}

/* =================================
   애니메이션
================================= */

@keyframes detail-route-move {
  to {
    stroke-dashoffset: -64;
  }
}

@keyframes detail-pin-float {
  0%,
  100% {
    transform: translateY(0) rotate(-3deg);
  }

  50% {
    transform: translateY(-7px) rotate(3deg);
  }
}

@keyframes detail-badge-pop {
  0% {
    opacity: 0;
    transform: scale(0.6) rotate(-10deg);
  }

  70% {
    transform: scale(1.08) rotate(3deg);
  }

  100% {
    opacity: 1;
    transform: scale(1) rotate(0);
  }
}

/* =================================
   태블릿
================================= */

@media (max-width: 1023px) {
  .detail-hero__inner {
    grid-template-columns: minmax(0, 1fr) 340px;
    gap: 38px;
  }

  .detail-hero__title {
    font-size: 40px;
  }

  .detail-visual {
    width: 340px;
  }

  .detail-visual__overlay {
    padding-right: 150px;
  }

  .detail-content__grid {
    grid-template-columns: 300px minmax(0, 1fr);
  }
}

/* =================================
   모바일
================================= */

@media (max-width: 767px) {
  .detail-hero__inner,
  .detail-badge-notice__inner,
  .detail-content__inner {
    width: min(100% - 32px, var(--content-width));
  }

  .detail-hero__inner {
    grid-template-columns: 1fr;
    gap: 26px;

    height: auto;
    min-height: 0;
    padding: 42px 0;
  }

  .detail-hero__content {
    max-width: 100%;
  }

  .detail-back {
    position: static;

    margin-bottom: 17px;
  }

  .detail-hero__title {
    font-size: 34px;
  }

  .detail-hero__description {
    font-size: 14px;
  }

  .detail-hero__description br {
    display: none;
  }

  .detail-hero__facts {
    width: 100%;
  }

  .detail-hero__fact {
    max-width: 100%;
  }

  .detail-visual {
    width: min(100%, 400px);
    height: 255px;
    justify-self: center;

    transform: none;
  }

  .detail-visual:hover {
    transform: none;
  }

  .detail-visual__overlay {
    padding-right: 156px;
  }

  .detail-badge-notice__inner {
    align-items: flex-start;

    padding-top: 16px;
    padding-bottom: 16px;
  }

  .detail-content {
    padding: 44px 0 64px;
  }

  .detail-content__summary {
    align-items: flex-start;
    flex-direction: column;
    gap: 8px;
  }

  .detail-content__summary strong {
    font-size: 19px;
  }

  .detail-content__summary p {
    font-size: 12px;
  }

  .detail-content__grid {
    grid-template-columns: 1fr;
  }

  .detail-info-panel {
    order: 2;
  }

  .detail-post-panel {
    order: 1;
  }

  .detail-panel-heading {
    min-height: 60px;

    padding: 0 15px;
  }
}

/* =================================
   작은 모바일
================================= */

@media (max-width: 420px) {
  .detail-hero__title {
    font-size: 31px;
  }

  .detail-visual {
    height: 245px;
  }

  .detail-map-button {
    width: 190px;
  }

  .detail-visual__overlay {
    padding-right: 138px;
  }

  .detail-badge-notice__icon {
    width: 40px;
    height: 40px;

    border-radius: 13px;
  }

  .detail-post-card {
    min-height: 72px;
    gap: 10px;

    padding: 12px;
  }
}

/* =================================
   모션 감소
================================= */

@media (prefers-reduced-motion: reduce) {
  .detail-visual__route,
  .detail-visual__pin,
  .detail-badge-notice__icon {
    animation: none;
  }

  .detail-back,
  .detail-map-button,
  .detail-map-button__arrow,
  .detail-visual,
  .detail-visual__frame img,
  .detail-info-map,
  .detail-post-card,
  .detail-post-card__title,
  .detail-post-card__arrow,
  .detail-state__button {
    transition: none;
  }
}
</style>