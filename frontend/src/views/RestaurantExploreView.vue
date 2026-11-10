<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getRestaurants } from '@/api/restaurantApi'
import RestaurantMap from '@/components/restaurant/RestaurantMap.vue'

const ALL_REGIONS = '전체 지역'

const route = useRoute()
const router = useRouter()

const restaurants = ref([])
const isLoading = ref(false)
const errorMessage = ref('')

const keyword = ref('')
const region = ref(ALL_REGIONS)
const selectedId = ref(null)

const mapRef = ref(null)

// 상세 페이지의 "지도에서 위치 확인" 버튼이나 챗봇의 음식점 링크로 들어온 경우, 해당 마커를
// 바로 포커스한다. 이미 지도 화면에 머물러 있는 상태에서 쿼리만 다시 들어와도(라우트가 그대로라
// onMounted는 재실행되지 않으므로) 아래 watch에서 반응한다.
const applyFocusFromQuery = async () => {
  const focusId = route.query.focus
  if (!focusId) return

  const target = restaurants.value.find(
    (restaurant) => String(restaurant.id) === String(focusId),
  )

  if (target) {
    await nextTick()
    selectRestaurant(target)
  }

  router.replace({ query: { ...route.query, focus: undefined } })
}

const fetchRestaurants = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const response = await getRestaurants()
    const data = response.data

    restaurants.value = Array.isArray(data)
      ? data
      : (data?.items ?? data?.results ?? [])
  } catch {
    errorMessage.value =
      '음식점 정보를 불러오지 못했습니다. 잠시 후 다시 시도해주세요.'
  } finally {
    isLoading.value = false
  }

  await applyFocusFromQuery()
}

watch(
  () => route.query.focus,
  (focusId) => {
    if (focusId) applyFocusFromQuery()
  },
)

onMounted(async () => {
  const queryKeyword = route.query.keyword

  keyword.value = queryKeyword
    ? String(queryKeyword)
    : ''

  region.value = ALL_REGIONS

  await fetchRestaurants()
  await nextTick()

  if (queryKeyword) {
    document
      .querySelector('#restaurant-explore')
      ?.scrollIntoView({
        behavior: 'smooth',
        block: 'start',
      })
  }
})

const regionOptions = computed(() => [
  ALL_REGIONS,
  ...new Set(
    restaurants.value
      .map((restaurant) => restaurant.region)
      .filter(Boolean),
  ),
])

const filteredRestaurants = computed(() => {
  const trimmedKeyword = keyword.value.trim()

  return restaurants.value.filter((restaurant) => {
    const matchesRegion =
      region.value === ALL_REGIONS ||
      restaurant.region === region.value

    const matchesKeyword =
      trimmedKeyword === '' ||
      restaurant.name?.includes(trimmedKeyword) ||
      restaurant.region?.includes(trimmedKeyword) ||
      restaurant.roadAddress?.includes(trimmedKeyword) ||
      restaurant.jibunAddress?.includes(trimmedKeyword)

    return matchesRegion && matchesKeyword
  })
})

const handleReset = () => {
  keyword.value = ''
  region.value = ALL_REGIONS
}

const selectRestaurant = (restaurant) => {
  selectedId.value = restaurant.id
  mapRef.value?.focusRestaurant(restaurant.id)
}

const handleMapSelect = (restaurant) => {
  selectedId.value = restaurant.id
}
</script>

<template>
  <main class="explore-page">
    <!-- 지도 탐색 Hero -->
    <section class="explore-editorial">
      <div class="explore-editorial__inner">
        <!-- 왼쪽 소개 영역 -->
        <div class="explore-editorial__intro">
          <span class="explore-editorial__eyebrow">
            MAP / LOCAL DISCOVERY
          </span>

          <h1 class="explore-editorial__title">
            지도에서 발견하는<br />
            <strong>우리 동네 맛집</strong>
          </h1>

          <p class="explore-editorial__description">
            가까운 음식점부터 대전·충청권의 숨은 맛집까지,<br />
            지역을 선택하고 지도에서 한눈에 찾아보세요.
          </p>

          <div
            class="explore-editorial__categories"
            aria-label="지도 탐색 주요 기능"
          >
            <span>지역별 탐색</span>
            <span>음식점 검색</span>
            <span>지도 위치 확인</span>
          </div>
        </div>

        <!-- 오른쪽 인터랙티브 지도 탐험 -->
        <div class="explore-adventure">
          <div class="explore-adventure__top">
            <span class="explore-adventure__eyebrow">
              TODAY'S FOOD QUEST
            </span>

            <span class="explore-adventure__progress">
              <strong>01</strong>
              / 03
            </span>
          </div>

          <div
            class="explore-adventure__map"
            aria-hidden="true"
          >
            <!-- 지도 지형과 이동 경로 -->
            <svg
              class="explore-adventure__terrain"
              viewBox="0 0 400 220"
              preserveAspectRatio="none"
            >
              <path
                class="explore-adventure__terrain-shape"
                d="
                  M56 26
                  C102 5 145 17 183 34
                  C224 53 283 29 329 55
                  C372 80 380 126 348 157
                  C318 187 274 186 234 199
                  C191 214 146 203 106 205
                  C64 207 25 187 20 146
                  C15 103 18 46 56 26Z
                "
              />

              <path
                class="explore-adventure__terrain-line"
                d="
                  M31 89
                  C74 75 106 87 132 68
                  C164 45 195 50 224 65
                  C255 82 292 77 367 49
                "
              />

              <path
                class="explore-adventure__terrain-line explore-adventure__terrain-line--bottom"
                d="
                  M41 182
                  C86 166 122 179 158 163
                  C198 145 224 155 263 170
                  C301 184 330 168 369 153
                "
              />

              <path
                class="explore-adventure__route"
                d="
                  M54 171
                  C86 161 99 128 137 132
                  C176 136 185 87 226 91
                  C267 95 281 60 326 52
                "
              />
            </svg>

            <!-- 첫 번째 체크포인트 -->
            <div
              class="explore-adventure__checkpoint explore-adventure__checkpoint--one"
            >
              <span class="explore-adventure__node">
                1
              </span>

              <span class="explore-adventure__checkpoint-copy">
                <strong>지역 선택</strong>
                <small>어디서 먹을까요?</small>
              </span>
            </div>

            <!-- 두 번째 체크포인트 -->
            <div
              class="explore-adventure__checkpoint explore-adventure__checkpoint--two"
            >
              <span class="explore-adventure__node">
                2
              </span>

              <span class="explore-adventure__checkpoint-copy">
                <strong>맛집 발견</strong>
                <small>목록을 둘러봐요</small>
              </span>
            </div>

            <!-- 목적지 -->
            <div class="explore-adventure__destination">
              <span class="explore-adventure__pin">
                <svg viewBox="0 0 24 24">
                  <path
                    d="M12 21s6-5.1 6-11a6 6 0 1 0-12 0c0 5.9 6 11 6 11Z"
                  />
                  <circle cx="12" cy="10" r="2.2" />
                </svg>
              </span>

              <span class="explore-adventure__destination-copy">
                <strong>오늘의 맛집</strong>
                <small>지도에서 발견!</small>
              </span>
            </div>

            <!-- 나침반 -->
            <span class="explore-adventure__compass">
              <strong>N</strong>
              <i></i>
            </span>

            <!-- 장식 -->
            <span
              class="explore-adventure__spark explore-adventure__spark--one"
            >
              ✦
            </span>

            <span
              class="explore-adventure__spark explore-adventure__spark--two"
            >
              ✦
            </span>
          </div>

          <a
            href="#restaurant-explore"
            class="explore-adventure__start"
          >
            <span
              class="explore-adventure__start-icon"
              aria-hidden="true"
            >
              ▶
            </span>

            <strong>맛집 탐험 시작</strong>

            <span
              class="explore-adventure__start-arrow"
              aria-hidden="true"
            >
              →
            </span>
          </a>
        </div>
      </div>
    </section>

    <!-- 검색 도구 영역 -->
    <section
      id="restaurant-explore"
      class="explore-tools"
    >
      <div class="explore-tools__inner">
        <div class="explore-tools__heading">
          <span>FIND A RESTAURANT</span>

          <strong>어떤 맛집을 찾고 있나요?</strong>
        </div>

        <div class="explore-toolbar">
          <label
            class="explore-search"
            for="restaurant-keyword"
          >
            <span class="sr-only">
              음식점명 또는 주소로 검색
            </span>

            <svg
              class="explore-search__icon"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <circle
                cx="11"
                cy="11"
                r="7"
              />

              <path d="m16.5 16.5 4 4" />
            </svg>

            <input
              id="restaurant-keyword"
              v-model="keyword"
              type="search"
              class="explore-search__input"
              placeholder="음식점명, 지역 또는 주소로 검색해보세요."
            />
          </label>

          <label class="explore-region">
            <span class="sr-only">
              지역 필터
            </span>

            <select
              v-model="region"
              class="explore-region__select"
              aria-label="지역 필터"
            >
              <option
                v-for="option in regionOptions"
                :key="option"
                :value="option"
              >
                {{ option }}
              </option>
            </select>

            <svg
              class="explore-region__icon"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path d="m8 10 4 4 4-4" />
            </svg>
          </label>

          <button
            type="button"
            class="explore-reset"
            @click="handleReset"
          >
            초기화
          </button>
        </div>
      </div>
    </section>

    <!-- 지도 및 음식점 목록 -->
    <section class="explore-content">
      <div class="explore-content__inner">
        <div class="explore-content__summary">
          <div>
            <span class="explore-content__eyebrow">
              RESTAURANT RESULTS
            </span>

            <strong>
              검색 결과 {{ filteredRestaurants.length }}개
            </strong>
          </div>

          <p>
            목록의 음식점을 선택하면 지도에서 위치를 확인할 수 있어요.
          </p>
        </div>

        <div class="explore-body">
          <!-- 음식점 목록 -->
          <section
            class="explore-list-panel"
            aria-label="음식점 목록"
          >
            <div class="explore-panel-heading">
              <div>
                <span>LIST</span>
                <strong>음식점 목록</strong>
              </div>

              <span class="explore-panel-heading__count">
                {{ filteredRestaurants.length }}
              </span>
            </div>

            <div class="explore-list-panel__body">
              <!-- 로딩 -->
              <div
                v-if="isLoading"
                class="explore-status"
                aria-live="polite"
              >
                <span
                  class="explore-status__icon"
                  aria-hidden="true"
                >
                  ···
                </span>

                <strong>음식점을 불러오고 있어요.</strong>

                <p>잠시만 기다려 주세요.</p>
              </div>

              <!-- 오류 -->
              <div
                v-else-if="errorMessage"
                class="explore-status explore-status--error"
                role="alert"
              >
                <span
                  class="explore-status__icon"
                  aria-hidden="true"
                >
                  !
                </span>

                <strong>음식점을 불러오지 못했어요.</strong>

                <p>{{ errorMessage }}</p>

                <button
                  type="button"
                  class="explore-retry"
                  @click="fetchRestaurants"
                >
                  다시 시도
                </button>
              </div>

              <!-- 검색 결과 없음 -->
              <div
                v-else-if="filteredRestaurants.length === 0"
                class="explore-status"
              >
                <span
                  class="explore-status__empty-icon"
                  aria-hidden="true"
                >
                  ⌕
                </span>

                <strong>조건에 맞는 음식점이 없어요.</strong>

                <p>
                  다른 검색어나 지역을 선택해보세요.
                </p>

                <button
                  type="button"
                  class="explore-status__reset"
                  @click="handleReset"
                >
                  검색 조건 초기화
                </button>
              </div>

              <!-- 음식점 목록 -->
              <ul
                v-else
                class="explore-list"
              >
                <li
                  v-for="restaurant in filteredRestaurants"
                  :key="restaurant.id"
                  class="explore-list__item"
                >
                  <button
                    type="button"
                    class="explore-card"
                    :class="{
                      'explore-card--active':
                        restaurant.id === selectedId,
                    }"
                    @click="selectRestaurant(restaurant)"
                  >
                    <div class="explore-card__top">
                      <span
                        v-if="restaurant.region"
                        class="explore-card__badge"
                      >
                        <span
                          class="explore-card__badge-dot"
                          aria-hidden="true"
                        ></span>

                        {{ restaurant.region }}
                      </span>

                      <span
                        class="explore-card__arrow"
                        aria-hidden="true"
                      >
                        →
                      </span>
                    </div>

                    <strong class="explore-card__name">
                      {{ restaurant.name }}
                    </strong>

                    <span class="explore-card__address">
                      {{ restaurant.roadAddress }}
                    </span>

                    <span
                      v-if="restaurant.jibunAddress"
                      class="explore-card__address explore-card__address--sub"
                    >
                      {{ restaurant.jibunAddress }}
                    </span>
                  </button>
                </li>
              </ul>
            </div>
          </section>

          <!-- 지도 -->
          <section
            class="explore-map-panel"
            aria-label="음식점 지도"
          >
            <div class="explore-panel-heading">
              <div>
                <span>MAP</span>
                <strong>지도에서 위치 확인</strong>
              </div>

              <span class="explore-panel-heading__guide">
                마커를 선택해보세요
              </span>
            </div>

            <div class="explore-map-panel__body">
              <RestaurantMap
                ref="mapRef"
                :restaurants="filteredRestaurants"
                :selected-id="selectedId"
                @select="handleMapSelect"
              />
            </div>
          </section>
        </div>
      </div>
    </section>
  </main>
</template>

<style scoped>
.explore-page {
  min-height: 100vh;

  background: var(--color-background);
  color: var(--color-text-primary);

  scroll-behavior: smooth;
}

/* =================================
   공통 너비
================================= */

.explore-editorial__inner,
.explore-tools__inner,
.explore-content__inner {
  width: min(100% - 48px, var(--content-width));
  margin: 0 auto;
}

/* =================================
   지도 탐색 Hero
================================= */

.explore-editorial {
  border-bottom: 1px solid var(--color-border);

  background: #f6f1ed;
}

.explore-editorial__inner {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 400px;
  align-items: center;
  gap: 64px;

  height: var(--subpage-hero-height, 356px);
  min-height: 0;
  padding: var(--subpage-hero-padding-y, 44px) 0;

  box-sizing: border-box;
}

.explore-editorial__intro {
  display: flex;
  min-width: 0;
  max-width: 720px;
  align-items: flex-start;
  flex-direction: column;
  justify-content: center;
}

.explore-editorial__eyebrow {
  margin-bottom: 14px;

  color: var(--color-primary);

  font-size: 10px;
  font-weight: 850;
  letter-spacing: 0.15em;
}

.explore-editorial__title {
  margin: 0;

  color: var(--color-text-primary);

  font-size: clamp(36px, 3.6vw, 46px);
  font-weight: 850;
  line-height: 1.18;
  letter-spacing: -0.055em;
}

.explore-editorial__title strong {
  color: var(--color-primary);
}

.explore-editorial__description {
  max-width: 650px;
  margin: 17px 0 0;

  color: var(--color-text-secondary);

  font-size: 15px;
  line-height: 1.72;
}

.explore-editorial__categories {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;

  margin-top: 21px;
}

.explore-editorial__categories span {
  padding: 6px 10px;

  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-pill);

  background: rgba(255, 255, 255, 0.5);
  color: var(--color-text-secondary);

  font-size: 11px;
  font-weight: 700;
}

/* =================================
   인터랙티브 지도 탐험
================================= */

.explore-adventure {
  position: relative;

  width: 400px;
  height: 260px;
  justify-self: end;

  transition: transform var(--transition-base);
}

.explore-adventure:hover {
  transform: translateY(-4px);
}

.explore-adventure__top {
  position: absolute;
  top: 0;
  right: 8px;
  left: 8px;
  z-index: 6;

  display: flex;
  align-items: center;
  justify-content: space-between;
}

.explore-adventure__eyebrow {
  color: var(--color-primary);

  font-size: 9px;
  font-weight: 850;
  letter-spacing: 0.14em;
}

.explore-adventure__progress {
  color: var(--color-text-disabled);

  font-size: 10px;
  font-weight: 750;
}

.explore-adventure__progress strong {
  color: var(--color-primary);

  font-size: 12px;
}

/* 지도 */

.explore-adventure__map {
  position: absolute;
  inset: 20px 0 0;
}

.explore-adventure__terrain {
  position: absolute;
  inset: 0;

  width: 100%;
  height: 100%;

  overflow: visible;
}

.explore-adventure__terrain-shape {
  fill: rgba(255, 255, 255, 0.58);
  stroke: rgba(255, 122, 69, 0.16);
  stroke-width: 1.4;
}

.explore-adventure__terrain-line {
  fill: none;
  stroke: rgba(169, 157, 151, 0.2);
  stroke-width: 1.2;
}

.explore-adventure__terrain-line--bottom {
  stroke: rgba(255, 122, 69, 0.1);
}

.explore-adventure__route {
  fill: none;

  stroke: var(--color-primary);
  stroke-width: 3;
  stroke-linecap: round;
  stroke-dasharray: 8 10;

  opacity: 0.52;

  animation: adventure-route-move 7s linear infinite;
}

/* 체크포인트 */

.explore-adventure__checkpoint {
  position: absolute;
  z-index: 4;

  display: flex;
  align-items: center;
  gap: 8px;
}

.explore-adventure__checkpoint--one {
  bottom: 44px;
  left: 27px;
}

.explore-adventure__checkpoint--two {
  top: 91px;
  left: 142px;
}

.explore-adventure__node {
  display: grid;
  place-items: center;

  width: 31px;
  height: 31px;

  flex-shrink: 0;

  box-sizing: border-box;

  border: 2px solid var(--color-primary-200);
  border-radius: 50%;

  background: #ffffff;
  color: var(--color-primary);

  font-size: 10px;
  font-weight: 850;

  box-shadow:
    0 0 0 5px rgba(255, 122, 69, 0.06);

  transition:
    border-color var(--transition-fast),
    background-color var(--transition-fast),
    box-shadow var(--transition-fast),
    color var(--transition-fast),
    transform var(--transition-fast);
}

.explore-adventure__checkpoint:hover .explore-adventure__node {
  border-color: var(--color-primary);

  background: var(--color-primary);
  color: #ffffff;

  box-shadow:
    0 0 0 7px rgba(255, 122, 69, 0.12),
    0 9px 18px rgba(255, 122, 69, 0.16);

  transform: scale(1.12);
}

.explore-adventure__checkpoint-copy {
  display: flex;
  flex-direction: column;

  padding: 7px 9px;

  border: 1px solid var(--color-border);
  border-radius: 10px;

  background: rgba(255, 255, 255, 0.91);

  box-shadow:
    0 6px 16px rgba(93, 54, 34, 0.06);

  backdrop-filter: blur(8px);

  transition: transform var(--transition-fast);
}

.explore-adventure__checkpoint:hover
  .explore-adventure__checkpoint-copy {
  transform: translateY(-3px);
}

.explore-adventure__checkpoint-copy strong {
  color: var(--color-text-primary);

  font-size: 10px;
  line-height: 1.35;
}

.explore-adventure__checkpoint-copy small {
  margin-top: 1px;

  color: var(--color-text-disabled);

  font-size: 8px;
}

/* 목적지 */

.explore-adventure__destination {
  position: absolute;
  top: 26px;
  right: 21px;
  z-index: 5;

  display: flex;
  align-items: center;
  flex-direction: column;
}

.explore-adventure__pin {
  position: relative;

  display: grid;
  place-items: center;

  width: 58px;
  height: 58px;

  border-radius: 21px;

  background: var(--color-primary);
  color: #ffffff;

  box-shadow:
    0 15px 28px rgba(255, 122, 69, 0.25);

  animation: adventure-pin-float 3.4s ease-in-out infinite;
}

.explore-adventure__pin::after {
  position: absolute;
  right: -7px;
  bottom: -7px;

  width: 17px;
  height: 17px;

  box-sizing: border-box;

  border: 3px solid #f6f1ed;
  border-radius: 50%;

  background: var(--color-accent);

  content: '';
}

.explore-adventure__pin svg {
  width: 29px;
  height: 29px;

  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.8;
}

.explore-adventure__destination-copy {
  display: flex;
  align-items: center;
  flex-direction: column;

  margin-top: 8px;
  padding: 6px 9px;

  border: 1px solid var(--color-border);
  border-radius: 10px;

  background: rgba(255, 255, 255, 0.92);

  box-shadow:
    0 7px 17px rgba(93, 54, 34, 0.06);

  backdrop-filter: blur(8px);
}

.explore-adventure__destination-copy strong {
  color: var(--color-primary-active);

  font-size: 10px;
}

.explore-adventure__destination-copy small {
  margin-top: 1px;

  color: var(--color-text-disabled);

  font-size: 8px;
}

/* 나침반 */

.explore-adventure__compass {
  position: absolute;
  top: 40px;
  left: 41px;
  z-index: 3;

  display: grid;
  place-items: center;

  width: 32px;
  height: 32px;

  border: 1px solid rgba(255, 122, 69, 0.2);
  border-radius: 50%;

  background: rgba(255, 255, 255, 0.74);
  color: var(--color-primary);

  font-size: 8px;
  font-style: normal;
  font-weight: 850;

  animation: adventure-compass-turn 8s ease-in-out infinite;
}

.explore-adventure__compass i {
  position: absolute;
  top: 5px;

  width: 0;
  height: 0;

  border-right: 3px solid transparent;
  border-bottom: 8px solid var(--color-primary);
  border-left: 3px solid transparent;
}

/* 장식 */

.explore-adventure__spark {
  position: absolute;
  z-index: 3;

  color: var(--color-primary);

  font-size: 12px;

  animation: adventure-spark 2.4s ease-in-out infinite;
}

.explore-adventure__spark--one {
  top: 35px;
  left: 111px;
}

.explore-adventure__spark--two {
  right: 118px;
  bottom: 62px;

  animation-delay: -1.2s;
}

/* 탐험 시작 */

.explore-adventure__start {
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

  border-radius: var(--radius-md);

  background: var(--color-primary);
  color: #ffffff;

  font-size: 11px;
  font-weight: 750;
  text-decoration: none;

  box-shadow:
    0 9px 19px rgba(255, 122, 69, 0.2);

  transition:
    background-color var(--transition-fast),
    box-shadow var(--transition-fast),
    transform var(--transition-fast);
}

.explore-adventure__start:hover {
  background: var(--color-primary-hover);

  box-shadow:
    0 13px 23px rgba(255, 122, 69, 0.27);

  transform: translateY(-2px);
}

.explore-adventure__start-icon {
  display: grid;
  place-items: center;

  width: 25px;
  height: 25px;

  border-radius: 8px;

  background: rgba(255, 255, 255, 0.17);

  font-size: 8px;
}

.explore-adventure__start-arrow {
  font-size: 14px;

  transition: transform var(--transition-fast);
}

.explore-adventure__start:hover
  .explore-adventure__start-arrow {
  transform: translateX(4px);
}

/* =================================
   검색 도구 영역
================================= */

.explore-tools {
  padding: 28px 0;

  border-bottom: 1px solid var(--color-border);

  background: #ffffff;

  scroll-margin-top: calc(var(--header-height) + 16px);
}

.explore-tools__inner {
  display: grid;
  grid-template-columns: 250px minmax(0, 1fr);
  align-items: center;
  gap: 32px;
}

.explore-tools__heading {
  display: flex;
  flex-direction: column;
}

.explore-tools__heading span {
  margin-bottom: 5px;

  color: var(--color-primary);

  font-size: 9px;
  font-weight: 850;
  letter-spacing: 0.13em;
}

.explore-tools__heading strong {
  color: var(--color-text-primary);

  font-size: 17px;
  line-height: 1.4;
  letter-spacing: -0.025em;
}

.explore-toolbar {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 190px auto;
  gap: 9px;
}

.explore-search {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: 11px;

  min-height: 50px;
  padding: 0 16px;

  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);

  background: var(--color-background);

  transition:
    border-color var(--transition-fast),
    box-shadow var(--transition-fast);
}

.explore-search:focus-within {
  border-color: var(--color-primary);

  box-shadow:
    0 0 0 3px rgba(255, 122, 69, 0.09);
}

.explore-search__icon {
  width: 19px;
  height: 19px;

  flex-shrink: 0;

  fill: none;
  stroke: var(--color-text-disabled);
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.8;
}

.explore-search__input {
  width: 100%;
  min-width: 0;
  height: 48px;

  padding: 0;

  border: 0;
  outline: 0;

  background: transparent;
  color: var(--color-text-primary);

  font: inherit;
  font-size: 14px;
}

.explore-search__input::placeholder {
  color: var(--color-text-disabled);
}

.explore-search__input::-webkit-search-cancel-button {
  cursor: pointer;
}

.explore-region {
  position: relative;

  display: flex;
  min-width: 0;
}

.explore-region__select {
  width: 100%;
  min-height: 50px;

  padding: 0 42px 0 15px;

  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  outline: none;

  appearance: none;

  background: var(--color-background);
  color: var(--color-text-primary);

  font: inherit;
  font-size: 13px;
  font-weight: 700;

  cursor: pointer;

  transition:
    border-color var(--transition-fast),
    box-shadow var(--transition-fast);
}

.explore-region__select:focus {
  border-color: var(--color-primary);

  box-shadow:
    0 0 0 3px rgba(255, 122, 69, 0.09);
}

.explore-region__icon {
  position: absolute;
  top: 50%;
  right: 15px;

  width: 18px;
  height: 18px;

  fill: none;
  stroke: var(--color-text-secondary);
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.8;

  pointer-events: none;

  transform: translateY(-50%);
}

.explore-reset {
  min-width: 82px;
  min-height: 50px;

  padding: 0 18px;

  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-md);

  background: #ffffff;
  color: var(--color-text-secondary);

  font: inherit;
  font-size: 13px;
  font-weight: 750;

  cursor: pointer;

  transition:
    border-color var(--transition-fast),
    color var(--transition-fast),
    transform var(--transition-fast);
}

.explore-reset:hover {
  border-color: var(--color-primary);

  color: var(--color-primary);

  transform: translateY(-1px);
}

/* =================================
   지도 콘텐츠 영역
================================= */

.explore-content {
  padding: 52px 0 80px;

  background: var(--color-background);
}

.explore-content__summary {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 28px;

  margin-bottom: 21px;
}

.explore-content__summary > div {
  display: flex;
  align-items: flex-start;
  flex-direction: column;
}

.explore-content__eyebrow {
  margin-bottom: 6px;

  color: var(--color-primary);

  font-size: 9px;
  font-weight: 850;
  letter-spacing: 0.13em;
}

.explore-content__summary strong {
  font-size: 22px;
  line-height: 1.35;
  letter-spacing: -0.035em;
}

.explore-content__summary p {
  margin: 0;

  color: var(--color-text-secondary);

  font-size: 13px;
}

.explore-body {
  display: grid;
  grid-template-columns: 360px minmax(0, 1fr);
  gap: 18px;
  align-items: start;
}

/* =================================
   목록·지도 공통 패널
================================= */

.explore-list-panel,
.explore-map-panel {
  overflow: hidden;

  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);

  background: var(--color-surface);

  box-shadow: var(--shadow-card);
}

.explore-panel-heading {
  display: flex;
  min-height: 65px;
  align-items: center;
  justify-content: space-between;
  gap: 16px;

  padding: 0 18px;

  border-bottom: 1px solid var(--color-border);

  background: #ffffff;
}

.explore-panel-heading > div {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.explore-panel-heading span {
  color: var(--color-primary);

  font-size: 9px;
  font-weight: 850;
  letter-spacing: 0.12em;
}

.explore-panel-heading strong {
  color: var(--color-text-primary);

  font-size: 15px;
  line-height: 1.4;
}

.explore-panel-heading__count {
  display: grid;
  place-items: center;

  min-width: 31px;
  height: 31px;
  padding: 0 8px;

  border-radius: var(--radius-pill);

  background: var(--color-primary-50);
  color: var(--color-primary) !important;

  font-size: 11px !important;
  letter-spacing: 0 !important;
}

.explore-panel-heading__guide {
  color: var(--color-text-disabled) !important;

  font-size: 11px !important;
  font-weight: 650 !important;
  letter-spacing: 0 !important;
}

/* =================================
   음식점 목록
================================= */

.explore-list-panel__body {
  height: 575px;

  overflow-y: auto;

  scrollbar-color: var(--color-border-strong) transparent;
  scrollbar-width: thin;
}

.explore-list-panel__body::-webkit-scrollbar {
  width: 5px;
}

.explore-list-panel__body::-webkit-scrollbar-thumb {
  border-radius: var(--radius-pill);

  background: var(--color-border-strong);
}

.explore-list {
  display: flex;
  flex-direction: column;
  gap: 7px;

  margin: 0;
  padding: 9px;

  list-style: none;
}

.explore-list__item {
  min-width: 0;
}

.explore-card {
  position: relative;

  display: flex;
  width: 100%;
  min-height: 0;
  align-items: flex-start;
  flex-direction: column;
  gap: 5px;

  padding: 14px;

  border: 1px solid transparent;
  border-radius: var(--radius-md);

  background: transparent;
  color: inherit;

  font: inherit;
  text-align: left;

  cursor: pointer;

  transition:
    border-color var(--transition-fast),
    background-color var(--transition-fast),
    box-shadow var(--transition-fast),
    transform var(--transition-fast);
}

.explore-card::before {
  position: absolute;
  top: 14px;
  bottom: 14px;
  left: 0;

  width: 3px;

  border-radius: 0 var(--radius-pill) var(--radius-pill) 0;

  background: var(--color-primary);

  content: '';

  opacity: 0;

  transition: opacity var(--transition-fast);
}

.explore-card:hover {
  background: var(--color-primary-50);

  transform: translateX(2px);
}

.explore-card--active {
  border-color: rgba(255, 122, 69, 0.3);

  background: var(--color-primary-50);

  box-shadow:
    0 6px 16px rgba(255, 122, 69, 0.08);
}

.explore-card--active::before {
  opacity: 1;
}

.explore-card__top {
  display: flex;
  width: 100%;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.explore-card__badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;

  padding: 5px 8px;

  border-radius: var(--radius-pill);

  background: var(--color-primary-50);
  color: var(--color-primary-active);

  font-size: 10px;
  font-weight: 750;
}

.explore-card__badge-dot {
  width: 5px;
  height: 5px;

  border-radius: 50%;

  background: var(--color-primary);
}

.explore-card__arrow {
  display: grid;
  place-items: center;

  width: 26px;
  height: 26px;

  flex-shrink: 0;

  border: 1px solid var(--color-border);
  border-radius: 50%;

  color: var(--color-text-disabled);

  font-size: 11px;

  transition:
    border-color var(--transition-fast),
    background-color var(--transition-fast),
    color var(--transition-fast),
    transform var(--transition-fast);
}

.explore-card:hover .explore-card__arrow,
.explore-card--active .explore-card__arrow {
  border-color: var(--color-primary);

  background: var(--color-primary);
  color: #ffffff;

  transform: translateX(2px);
}

.explore-card__name {
  margin-top: 3px;

  color: var(--color-text-primary);

  font-size: 15px;
  font-weight: 800;
  line-height: 1.4;
}

.explore-card__address {
  color: var(--color-text-secondary);

  font-size: 12px;
  line-height: 1.5;
}

.explore-card__address--sub {
  color: var(--color-text-disabled);
}

/* =================================
   지도
================================= */

.explore-map-panel__body {
  height: 575px;
}

.explore-map-panel__body :deep(.map) {
  height: 100%;
}

/* =================================
   상태 화면
================================= */

.explore-status {
  display: flex;
  min-height: 300px;
  align-items: center;
  justify-content: center;
  flex-direction: column;

  padding: 28px 20px;

  color: var(--color-text-secondary);

  text-align: center;
}

.explore-status__icon,
.explore-status__empty-icon {
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

.explore-status strong {
  color: var(--color-text-primary);

  font-size: 15px;
}

.explore-status p {
  margin: 7px 0 0;

  font-size: 12px;
  line-height: 1.6;
}

.explore-status--error .explore-status__icon {
  background: rgba(220, 38, 38, 0.08);
  color: var(--color-error);
}

.explore-retry,
.explore-status__reset {
  min-height: 39px;

  margin-top: 17px;
  padding: 0 14px;

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

.explore-retry:hover,
.explore-status__reset:hover {
  background: var(--color-primary);
  color: #ffffff;
}

/* =================================
   접근성
================================= */

.sr-only {
  position: absolute;

  width: 1px;
  height: 1px;

  margin: -1px;
  padding: 0;

  overflow: hidden;

  border: 0;

  clip: rect(0, 0, 0, 0);

  white-space: nowrap;
}

/* =================================
   애니메이션
================================= */

@keyframes adventure-route-move {
  to {
    stroke-dashoffset: -72;
  }
}

@keyframes adventure-pin-float {
  0%,
  100% {
    transform: translateY(0) rotate(-3deg);
  }

  50% {
    transform: translateY(-8px) rotate(3deg);
  }
}

@keyframes adventure-compass-turn {
  0%,
  100% {
    transform: rotate(-5deg);
  }

  50% {
    transform: rotate(9deg);
  }
}

@keyframes adventure-spark {
  0%,
  100% {
    opacity: 0.25;
    transform: scale(0.75) rotate(0);
  }

  50% {
    opacity: 1;
    transform: scale(1.15) rotate(18deg);
  }
}

/* =================================
   태블릿
================================= */

@media (max-width: 1023px) {
  .explore-editorial__inner {
    grid-template-columns: minmax(0, 1fr) 340px;
    gap: 38px;
  }

  .explore-editorial__title {
    font-size: 40px;
  }

  .explore-adventure {
    width: 340px;

    transform: scale(0.94);
    transform-origin: right center;
  }

  .explore-adventure:hover {
    transform: scale(0.94) translateY(-4px);
  }

  .explore-adventure__checkpoint--two {
    left: 116px;
  }

  .explore-tools__inner {
    grid-template-columns: 210px minmax(0, 1fr);
    gap: 22px;
  }

  .explore-toolbar {
    grid-template-columns: minmax(0, 1fr) 165px auto;
  }

  .explore-body {
    grid-template-columns: 315px minmax(0, 1fr);
  }
}

/* =================================
   모바일
================================= */

@media (max-width: 767px) {
  .explore-editorial__inner,
  .explore-tools__inner,
  .explore-content__inner {
    width: min(100% - 32px, var(--content-width));
  }

  .explore-editorial__inner {
    grid-template-columns: 1fr;
    gap: 26px;

    height: auto;
    min-height: 0;
    padding: 42px 0;
  }

  .explore-editorial__intro {
    max-width: 100%;
  }

  .explore-editorial__title {
    font-size: 34px;
  }

  .explore-editorial__description {
    font-size: 14px;
  }

  .explore-editorial__description br {
    display: none;
  }

  .explore-adventure {
    width: min(100%, 400px);
    height: 255px;
    justify-self: center;

    transform: none;
  }

  .explore-adventure:hover {
    transform: none;
  }

  .explore-adventure__checkpoint--one {
    left: 18px;
  }

  .explore-adventure__checkpoint--two {
    left: 39%;
  }

  .explore-adventure__destination {
    right: 12px;
  }

  .explore-tools {
    padding: 23px 0;
  }

  .explore-tools__inner {
    grid-template-columns: 1fr;
    gap: 14px;
  }

  .explore-toolbar {
    grid-template-columns: minmax(0, 1fr) auto;
  }

  .explore-search {
    grid-column: 1 / -1;
  }

  .explore-region {
    min-width: 0;
  }

  .explore-reset {
    min-width: 78px;
  }

  .explore-content {
    padding: 44px 0 64px;
  }

  .explore-content__summary {
    align-items: flex-start;
    flex-direction: column;
    gap: 8px;
  }

  .explore-content__summary strong {
    font-size: 19px;
  }

  .explore-content__summary p {
    font-size: 12px;
  }

  .explore-body {
    grid-template-columns: 1fr;
  }

  .explore-map-panel {
    order: -1;
  }

  .explore-map-panel__body {
    height: 320px;
  }

  .explore-list-panel__body {
    height: 420px;
  }

  .explore-panel-heading {
    min-height: 60px;

    padding: 0 15px;
  }

  .explore-panel-heading__guide {
    display: none;
  }
}

/* =================================
   작은 모바일
================================= */

@media (max-width: 420px) {
  .explore-adventure {
    height: 245px;
  }

  .explore-adventure__top {
    right: 2px;
    left: 2px;
  }

  .explore-adventure__checkpoint-copy {
    display: none;
  }

  .explore-adventure__checkpoint--one {
    bottom: 54px;
    left: 35px;
  }

  .explore-adventure__checkpoint--two {
    top: 102px;
    left: 47%;
  }

  .explore-adventure__destination-copy {
    padding: 5px 7px;
  }

  .explore-adventure__start {
    width: 190px;
  }

  .explore-toolbar {
    grid-template-columns: 1fr;
  }

  .explore-search {
    grid-column: auto;
  }

  .explore-reset {
    width: 100%;
  }
}

/* =================================
   모션 감소
================================= */

@media (prefers-reduced-motion: reduce) {
  .explore-adventure__route,
  .explore-adventure__pin,
  .explore-adventure__compass,
  .explore-adventure__spark {
    animation: none;
  }

  .explore-adventure,
  .explore-adventure__node,
  .explore-adventure__checkpoint-copy,
  .explore-adventure__start,
  .explore-adventure__start-arrow,
  .explore-reset,
  .explore-card,
  .explore-card__arrow,
  .explore-retry,
  .explore-status__reset {
    transition: none;
  }
}
</style>