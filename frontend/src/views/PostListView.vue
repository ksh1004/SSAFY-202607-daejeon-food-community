<script setup>
import {
  computed,
  nextTick,
  onMounted,
  ref,
} from 'vue'

import { getPosts } from '@/api/postApi'

const FETCH_SIZE = 30
const DAY_IN_MILLISECONDS = 24 * 60 * 60 * 1000

const searchKeyword = ref('')
const postType = ref('all')
const sortOrder = ref('newest')

const sourcePosts = ref([])
const trendingSourcePosts = ref([])

const page = ref(1)
const size = ref(10)

const pageSizeOptions = [10, 20, 30]

const isLoading = ref(false)
const errorMessage = ref('')

const postBoardRef = ref(null)

/* =================================
   게시글 필터 및 정렬
================================= */

const filteredAndSortedPosts = computed(() => {
  const filteredPosts = sourcePosts.value.filter((post) => {
    const isRestaurantPost = Boolean(
      post.restaurant_id ||
      post.restaurant_title,
    )

    if (postType.value === 'restaurant') {
      return isRestaurantPost
    }

    if (postType.value === 'general') {
      return !isRestaurantPost
    }

    return true
  })

  return [...filteredPosts].sort((first, second) => {
    const firstTime = new Date(
      first.created_at ?? 0,
    ).getTime()

    const secondTime = new Date(
      second.created_at ?? 0,
    ).getTime()

    const safeFirstTime = Number.isNaN(firstTime)
      ? 0
      : firstTime

    const safeSecondTime = Number.isNaN(secondTime)
      ? 0
      : secondTime

    if (sortOrder.value === 'oldest') {
      return safeFirstTime - safeSecondTime
    }

    return safeSecondTime - safeFirstTime
  })
})

const total = computed(
  () => filteredAndSortedPosts.value.length,
)

const posts = computed(() => {
  const startIndex = (page.value - 1) * size.value
  const endIndex = startIndex + size.value

  return filteredAndSortedPosts.value.slice(
    startIndex,
    endIndex,
  )
})

/* =================================
   최근 7일 인기 음식점
================================= */

const trendingRestaurants = computed(() => {
  const restaurantPosts =
    trendingSourcePosts.value.filter((post) => {
      if (
        !post.restaurant_id ||
        !post.restaurant_title ||
        !post.created_at
      ) {
        return false
      }

      return !Number.isNaN(
        new Date(post.created_at).getTime(),
      )
    })

  if (restaurantPosts.length === 0) {
    return []
  }

  const latestRestaurantPostTime = Math.max(
    ...restaurantPosts.map((post) =>
      new Date(post.created_at).getTime(),
    ),
  )

  const periodStart =
    latestRestaurantPostTime -
    7 * DAY_IN_MILLISECONDS

  const restaurantCounts = new Map()

  restaurantPosts.forEach((post) => {
    const createdTime = new Date(
      post.created_at,
    ).getTime()

    if (createdTime < periodStart) {
      return
    }

    const key = String(post.restaurant_id)
    const currentRestaurant =
      restaurantCounts.get(key)

    if (currentRestaurant) {
      currentRestaurant.count += 1
      currentRestaurant.latestTime = Math.max(
        currentRestaurant.latestTime,
        createdTime,
      )
      return
    }

    restaurantCounts.set(key, {
      id: post.restaurant_id,
      title: post.restaurant_title,
      count: 1,
      latestTime: createdTime,
    })
  })

  return [...restaurantCounts.values()]
    .sort(
      (first, second) =>
        second.count - first.count ||
        second.latestTime - first.latestTime,
    )
    .slice(0, 3)
})

/* =================================
   페이지 정보
================================= */

const totalPages = computed(() => {
  if (total.value === 0) {
    return 0
  }

  return Math.ceil(total.value / size.value)
})

const hasPreviousPage = computed(() => page.value > 1)

const hasNextPage = computed(() => {
  return (
    totalPages.value > 0 &&
    page.value < totalPages.value
  )
})

const rangeStart = computed(() => {
  if (total.value === 0) {
    return 0
  }

  return (page.value - 1) * size.value + 1
})

const rangeEnd = computed(() => {
  if (total.value === 0) {
    return 0
  }

  return Math.min(
    page.value * size.value,
    total.value,
  )
})

const paginationItems = computed(() => {
  const lastPage = totalPages.value

  if (lastPage === 0) {
    return []
  }

  if (lastPage <= 7) {
    return Array.from(
      { length: lastPage },
      (_, index) => ({
        type: 'page',
        value: index + 1,
        key: `page-${index + 1}`,
      }),
    )
  }

  const pageSet = new Set([
    1,
    lastPage,
    page.value,
    page.value - 1,
    page.value + 1,
  ])

  if (page.value <= 4) {
    pageSet.add(2)
    pageSet.add(3)
    pageSet.add(4)
    pageSet.add(5)
  }

  if (page.value >= lastPage - 3) {
    pageSet.add(lastPage - 4)
    pageSet.add(lastPage - 3)
    pageSet.add(lastPage - 2)
    pageSet.add(lastPage - 1)
  }

  const selectedPages = [...pageSet]
    .filter(
      (pageNumber) =>
        pageNumber >= 1 &&
        pageNumber <= lastPage,
    )
    .sort((first, second) => first - second)

  const items = []

  selectedPages.forEach(
    (pageNumber, index) => {
      const previousPage =
        selectedPages[index - 1]

      if (
        index > 0 &&
        pageNumber - previousPage > 1
      ) {
        items.push({
          type: 'ellipsis',
          key: `ellipsis-${previousPage}-${pageNumber}`,
        })
      }

      items.push({
        type: 'page',
        value: pageNumber,
        key: `page-${pageNumber}`,
      })
    },
  )

  return items
})

/* =================================
   공통 함수
================================= */

const normalizePostResponse = (responseData) => {
  if (Array.isArray(responseData)) {
    return {
      items: responseData,
      total: responseData.length,
    }
  }

  const items = Array.isArray(responseData?.items)
    ? responseData.items
    : []

  return {
    items,
    total: Number(
      responseData?.total ?? items.length,
    ),
  }
}

const getValidationErrorMessage = (detail) => {
  if (!Array.isArray(detail)) {
    return ''
  }

  return detail
    .map((error) => error.msg)
    .filter(Boolean)
    .join(' / ')
}

const formatPostDate = (dateTime) => {
  if (!dateTime) {
    return '작성일 정보 없음'
  }

  const date = new Date(dateTime)

  if (Number.isNaN(date.getTime())) {
    return '작성일 정보 없음'
  }

  return new Intl.DateTimeFormat('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(date)
}

/* =================================
   목록 상단 이동
================================= */

const scrollToPostBoard = async () => {
  await nextTick()

  postBoardRef.value?.scrollIntoView({
    behavior: 'smooth',
    block: 'start',
  })
}

/* =================================
   게시글 전체 조회
================================= */

const fetchPosts = async () => {
  isLoading.value = true
  errorMessage.value = ''

  const trimmedKeyword =
    searchKeyword.value.trim()

  const createParams = (targetPage) => {
    const params = {
      page: targetPage,
      size: FETCH_SIZE,
    }

    if (trimmedKeyword) {
      params.keyword = trimmedKeyword
    }

    return params
  }

  try {
    const firstResponse = await getPosts(
      createParams(1),
    )

    const firstPage = normalizePostResponse(
      firstResponse.data,
    )

    const apiTotalPages = Math.ceil(
      firstPage.total / FETCH_SIZE,
    )

    let loadedPosts = [...firstPage.items]

    if (apiTotalPages > 1) {
      const remainingRequests = Array.from(
        { length: apiTotalPages - 1 },
        (_, index) =>
          getPosts(createParams(index + 2)),
      )

      const remainingResponses =
        await Promise.all(remainingRequests)

      remainingResponses.forEach((response) => {
        const pageData = normalizePostResponse(
          response.data,
        )

        loadedPosts.push(...pageData.items)
      })
    }

    sourcePosts.value = loadedPosts

    // 검색 중이 아닐 때의 전체 데이터를
    // 최근 7일 인기 음식점 계산에 사용합니다.
    if (!trimmedKeyword) {
      trendingSourcePosts.value = loadedPosts
    }

    if (page.value > totalPages.value) {
      page.value = 1
    }
  } catch (error) {
    sourcePosts.value = []

    if (error.response?.status === 422) {
      const validationMessage =
        getValidationErrorMessage(
          error.response.data?.detail,
        )

      errorMessage.value =
        validationMessage ||
        '검색 조건이 올바르지 않습니다.'
    } else if (!error.response) {
      errorMessage.value =
        '백엔드 서버에 연결할 수 없습니다. 서버 실행 상태를 확인해 주세요.'
    } else {
      errorMessage.value =
        '게시글 목록을 불러오지 못했습니다.'
    }
  } finally {
    isLoading.value = false
  }
}

/* =================================
   검색·필터·페이지 이동
================================= */

const handleSearch = async () => {
  page.value = 1

  await fetchPosts()
  await scrollToPostBoard()
}

const handlePostTypeChange = async (type) => {
  if (postType.value === type) {
    return
  }

  postType.value = type
  page.value = 1

  await scrollToPostBoard()
}

const handleListOptionChange = async () => {
  page.value = 1

  await scrollToPostBoard()
}

const moveToPage = async (targetPage) => {
  if (
    targetPage === page.value ||
    targetPage < 1 ||
    targetPage > totalPages.value
  ) {
    return
  }

  page.value = targetPage

  await scrollToPostBoard()
}

const moveToPreviousPage = async () => {
  if (!hasPreviousPage.value) {
    return
  }

  await moveToPage(page.value - 1)
}

const moveToNextPage = async () => {
  if (!hasNextPage.value) {
    return
  }

  await moveToPage(page.value + 1)
}

onMounted(() => {
  fetchPosts()
})
</script>

<template>
  <main class="post-list-page">
    <!-- 커뮤니티 헤더 -->
    <section class="community-editorial">
      <div class="community-editorial__inner">
        <div class="community-editorial__intro">
          <span class="community-editorial__eyebrow">
            COMMUNITY / LOCAL STORIES
          </span>

          <h1 class="community-editorial__title">
            동네에서 발견한<br />

            <strong>
              맛있는 이야기
            </strong>를 나눠요
          </h1>

          <p class="community-editorial__description">
            맛있었던 메뉴부터 다시 찾고 싶은 이유까지,<br />
            직접 경험한 대전·충청권의 이야기를 자유롭게
            남겨보세요.
          </p>

          <div
            class="community-editorial__categories"
            aria-label="커뮤니티 주요 주제"
          >
            <span>맛집 후기</span>
            <span>메뉴 추천</span>
            <span>동네 정보</span>
            <span>일반 이야기</span>
          </div>
        </div>

        <!-- 새 이야기 작성 -->
        <aside class="community-write">
          <div class="community-write__header">
            <span class="community-write__number">
              01
            </span>

            <span class="community-write__label">
              SHARE YOUR STORY
            </span>
          </div>

          <div class="community-write__content">
            <h2>
              오늘의 경험을<br />
              기록해보세요.
            </h2>

            <p>
              음식점 후기부터 자유로운 동네 이야기까지
              남길 수 있어요.
            </p>
          </div>

          <RouterLink
            to="/posts/new"
            class="community-write__link"
          >
            <span
              class="community-write__plus"
              aria-hidden="true"
            >
              ＋
            </span>

            <strong>
              새 이야기 작성
            </strong>

            <span
              class="community-write__arrow"
              aria-hidden="true"
            >
              →
            </span>
          </RouterLink>
        </aside>
      </div>
    </section>

    <!-- 검색 영역 -->
    <section class="community-tools">
      <div class="community-tools__inner">
        <div class="community-tools__heading">
          <span>
            SEARCH STORIES
          </span>

          <strong>
            어떤 이야기를 찾고 있나요?
          </strong>
        </div>

        <form
          class="community-search"
          @submit.prevent="handleSearch"
        >
          <label
            for="post-search"
            class="sr-only"
          >
            게시글 검색
          </label>

          <div class="community-search__field">
            <svg
              class="community-search__icon"
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
              id="post-search"
              v-model="searchKeyword"
              type="search"
              maxlength="100"
              class="community-search__input"
              placeholder="음식점 이름, 메뉴, 동네 이야기를 검색해보세요."
            />
          </div>

          <button
            type="submit"
            class="community-search__button"
            :disabled="isLoading"
          >
            {{ isLoading ? '검색 중' : '검색' }}
          </button>
        </form>
      </div>
    </section>

    <!-- 게시글 목록 -->
    <section
      ref="postBoardRef"
      class="post-board"
    >
      <div class="post-board__inner">
        <!-- 로딩 -->
        <section
          v-if="isLoading"
          class="post-list-page__status"
          aria-live="polite"
        >
          <span
            class="post-list-page__status-icon"
            aria-hidden="true"
          >
            ···
          </span>

          <strong>
            이야기를 불러오고 있어요.
          </strong>

          <p>
            잠시만 기다려 주세요.
          </p>
        </section>

        <!-- 오류 -->
        <section
          v-else-if="errorMessage"
          class="post-list-page__status post-list-page__status--error"
          role="alert"
        >
          <span
            class="post-list-page__status-icon"
            aria-hidden="true"
          >
            !
          </span>

          <strong>
            게시글을 불러오지 못했어요.
          </strong>

          <p>
            {{ errorMessage }}
          </p>

          <button
            type="button"
            class="post-list-page__retry-button"
            @click="fetchPosts"
          >
            다시 시도
          </button>
        </section>

        <!-- 정상 목록 -->
        <section
          v-else
          class="post-list-page__content"
        >
          <!-- 목록 요약 -->
          <div class="post-list-page__summary">
            <div class="post-list-page__summary-text">
              <span class="post-list-page__summary-eyebrow">
                LOCAL COMMUNITY
              </span>

              <strong>
                지금 {{ total }}개의 이야기가 모였어요
              </strong>

              <p v-if="total > 0">
                {{ rangeStart }}–{{ rangeEnd }}번째 이야기를
                보고 있어요.
              </p>
            </div>

            <div class="post-list-page__summary-actions">
              <RouterLink
                to="/posts/new"
                class="post-list-page__summary-link"
              >
                새 이야기 작성

                <span aria-hidden="true">
                  →
                </span>
              </RouterLink>
            </div>
          </div>

          <!-- 필터와 정렬 -->
          <div class="post-list-page__filters">
            <div
              class="post-list-page__type-filter"
              aria-label="게시글 종류 선택"
            >
              <!-- 전체 -->
              <button
                type="button"
                class="post-list-page__type-button"
                :class="{
                  'post-list-page__type-button--active':
                    postType === 'all',
                }"
                @click="handlePostTypeChange('all')"
              >
                전체보기
              </button>

              <!-- 일반 게시글 -->
              <button
                type="button"
                class="post-list-page__type-button"
                :class="{
                  'post-list-page__type-button--active':
                    postType === 'general',
                }"
                @click="handlePostTypeChange('general')"
              >
                일반 게시글
              </button>

              <!-- 음식점 게시글 -->
              <button
                type="button"
                class="post-list-page__type-button"
                :class="{
                  'post-list-page__type-button--active':
                    postType === 'restaurant',
                }"
                @click="handlePostTypeChange('restaurant')"
              >
                음식점 게시글
              </button>
            </div>

            <div class="post-list-page__filter-selects">
              <label class="post-list-page__select-control">
                <span class="sr-only">
                  게시글 정렬 기준
                </span>

                <select
                  v-model="sortOrder"
                  class="post-list-page__filter-select"
                  aria-label="게시글 정렬 기준"
                  @change="handleListOptionChange"
                >
                  <option value="newest">
                    최신순
                  </option>

                  <option value="oldest">
                    오래된순
                  </option>
                </select>
              </label>

              <label class="post-list-page__select-control">
                <span class="sr-only">
                  한 페이지에 표시할 게시글 수
                </span>

                <select
                  v-model.number="size"
                  class="post-list-page__filter-select"
                  aria-label="한 페이지에 표시할 게시글 수"
                  @change="handleListOptionChange"
                >
                  <option
                    v-for="option in pageSizeOptions"
                    :key="option"
                    :value="option"
                  >
                    {{ option }}개씩 보기
                  </option>
                </select>
              </label>
            </div>
          </div>

          <!-- 게시글 목록 -->
          <ul
            v-if="posts.length > 0"
            class="post-list"
          >
            <li
              v-for="post in posts"
              :key="post.id"
              class="post-list__item"
              :class="{
                'post-list__item--restaurant':
                  post.restaurant_title,
                'post-list__item--general':
                  !post.restaurant_title,
              }"
            >
              <RouterLink
                :to="`/posts/${post.id}`"
                class="post-list__link"
              >
                <div class="post-list__main">
                  <div class="post-list__meta">
                    <!-- 음식점 연동 -->
                    <span
                      v-if="post.restaurant_title"
                      class="post-list__badge post-list__badge--restaurant"
                    >
                      <span
                        class="post-list__badge-dot"
                        aria-hidden="true"
                      ></span>

                      <span class="post-list__badge-text">
                        {{ post.restaurant_title }}
                      </span>
                    </span>

                    <!-- 일반 게시글 -->
                    <span
                      v-else
                      class="post-list__badge post-list__badge--general"
                    >
                      <span
                        class="post-list__badge-dot"
                        aria-hidden="true"
                      ></span>

                      <span class="post-list__badge-text">
                        일반 이야기
                      </span>
                    </span>

                    <span class="post-list__date">
                      작성 {{ formatPostDate(post.created_at) }}
                    </span>
                  </div>

                  <h2 class="post-list__title">
                    {{ post.title }}
                  </h2>

                  <p class="post-list__content">
                    {{ post.content }}
                  </p>
                </div>

                <div class="post-list__side">
                  <span class="post-list__read-more">
                    이야기 읽기
                  </span>

                  <span
                    class="post-list__arrow"
                    aria-hidden="true"
                  >
                    →
                  </span>
                </div>
              </RouterLink>
            </li>
          </ul>

          <!-- 빈 상태 -->
          <div
            v-else
            class="post-list-page__empty"
          >
            <div
              class="post-list-page__empty-visual"
              aria-hidden="true"
            >
              <span>💬</span>
            </div>

            <strong>
              아직 검색된 이야기가 없어요.
            </strong>

            <p>
              다른 검색어를 입력하거나 첫 번째 이야기를
              남겨보세요.
            </p>

            <RouterLink
              to="/posts/new"
              class="post-list-page__empty-link"
            >
              새 이야기 작성

              <span aria-hidden="true">
                →
              </span>
            </RouterLink>
          </div>

          <!-- 최근 7일 인기 음식점 -->
          <aside class="post-trending">
            <div class="post-trending__header">
              <div>
                <span class="post-trending__eyebrow">
                  WEEKLY HOT PLACE
                </span>

                <strong>많이 언급된 음식점</strong>
              </div>

              <span
                class="post-trending__icon"
                aria-hidden="true"
              >
                ↗
              </span>
            </div>

            <p class="post-trending__description">
              최근 게시글 기준 7일 동안 자주 언급된 음식점이에요.
            </p>

            <ol
              v-if="trendingRestaurants.length > 0"
              class="post-trending__list"
            >
              <li
                v-for="(restaurant, index) in trendingRestaurants"
                :key="restaurant.id"
                class="post-trending__item"
              >
                <RouterLink
                  :to="`/restaurants/${restaurant.id}`"
                  class="post-trending__link"
                >
                  <span class="post-trending__rank">
                    {{ index + 1 }}
                  </span>

                  <span class="post-trending__copy">
                    <strong>
                      {{ restaurant.title }}
                    </strong>

                    <small>
                      최근 7일 {{ restaurant.count }}회 언급
                    </small>
                  </span>

                  <span
                    class="post-trending__arrow"
                    aria-hidden="true"
                  >
                    →
                  </span>
                </RouterLink>
              </li>
            </ol>

            <div
              v-else
              class="post-trending__empty"
            >
              아직 집계할 음식점 게시글이 없어요.
            </div>
          </aside>

          <!-- 숫자 페이지네이션 -->
          <nav
            v-if="totalPages > 1"
            class="post-list-page__pagination"
            aria-label="게시글 페이지 이동"
          >
            <button
              type="button"
              class="post-list-page__page-button post-list-page__page-button--direction"
              :disabled="
                !hasPreviousPage || isLoading
              "
              aria-label="이전 페이지"
              @click="moveToPreviousPage"
            >
              <span aria-hidden="true">
                ←
              </span>

              <span class="post-list-page__direction-text">
                이전
              </span>
            </button>

            <div class="post-list-page__page-numbers">
              <template
                v-for="item in paginationItems"
                :key="item.key"
              >
                <span
                  v-if="item.type === 'ellipsis'"
                  class="post-list-page__ellipsis"
                  aria-hidden="true"
                >
                  ···
                </span>

                <button
                  v-else
                  type="button"
                  class="post-list-page__number-button"
                  :class="{
                    'post-list-page__number-button--active':
                      item.value === page,
                  }"
                  :aria-current="
                    item.value === page
                      ? 'page'
                      : undefined
                  "
                  :aria-label="`${item.value}페이지로 이동`"
                  :disabled="isLoading"
                  @click="moveToPage(item.value)"
                >
                  {{ item.value }}
                </button>
              </template>
            </div>

            <button
              type="button"
              class="post-list-page__page-button post-list-page__page-button--direction"
              :disabled="
                !hasNextPage || isLoading
              "
              aria-label="다음 페이지"
              @click="moveToNextPage"
            >
              <span class="post-list-page__direction-text">
                다음
              </span>

              <span aria-hidden="true">
                →
              </span>
            </button>
          </nav>
        </section>
      </div>
    </section>
  </main>
</template>

<style scoped>
.post-list-page {
  min-height: 100vh;

  background: var(--color-background);
  color: var(--color-text-primary);
}

/* =================================
   공통 너비
================================= */

.community-editorial__inner,
.community-tools__inner {
  width: min(
    100% - 48px,
    var(--content-width)
  );
  margin: 0 auto;
}

/* 목록만 조금 더 좁게 */
.post-board__inner {
  width: min(100% - 48px, var(--content-width));
  margin: 0 auto;
}

/* =================================
   에디토리얼 헤더
================================= */

.community-editorial {
  border-bottom: 1px solid var(--color-border);

  background: #f6f1ed;
}

.community-editorial__inner {
  display: grid;
  grid-template-columns:
    minmax(0, 1fr)
    370px;
  align-items: center;
  gap: 72px;

  height: var(--subpage-hero-height);
  min-height: 0;
  padding: var(--subpage-hero-padding-y) 0;

  box-sizing: border-box;
}

.community-editorial__intro {
  display: flex;
  align-items: flex-start;
  flex-direction: column;
  justify-content: center;
}

.community-editorial__eyebrow {
  margin-bottom: 14px;

  color: var(--color-primary);

  font-size: 10px;
  font-weight: 850;
  letter-spacing: 0.15em;
}

.community-editorial__title {
  margin: 0;

  color: var(--color-text-primary);

  font-size: clamp(36px, 3.6vw, 46px);
  font-weight: 850;
  line-height: 1.18;
  letter-spacing: -0.055em;
}

.community-editorial__title strong {
  color: var(--color-primary);
}

.community-editorial__description {
  max-width: 650px;

  margin: 17px 0 0;

  color: var(--color-text-secondary);

  font-size: 15px;
  line-height: 1.72;
}

.community-editorial__categories {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;

  margin-top: 21px;
}

.community-editorial__categories span {
  padding: 6px 10px;

  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-pill);

  background: rgba(255, 255, 255, 0.5);
  color: var(--color-text-secondary);

  font-size: 11px;
  font-weight: 700;
}

/* =================================
   새 이야기 작성 카드
================================= */

.community-write {
  position: relative;

  display: flex;
  height: var(--subpage-side-content-height);
  min-height: 0;
  align-self: center;
  flex-direction: column;
  justify-content: space-between;

  box-sizing: border-box;
  padding: 25px;

  border: 1px solid var(--color-border);
  border-left: 5px solid var(--color-primary);
  border-radius: var(--radius-lg);

  background: #ffffff;

  box-shadow:
    0 13px 32px rgba(93, 54, 34, 0.09);
}

.community-write__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}

.community-write__number {
  color: var(--color-primary);

  font-size: 12px;
  font-weight: 850;
}

.community-write__label {
  color: var(--color-text-disabled);

  font-size: 9px;
  font-weight: 850;
  letter-spacing: 0.12em;
}

.community-write__content {
  margin: 23px 0;
}

.community-write__content h2 {
  margin: 0;

  color: var(--color-text-primary);

  font-size: 23px;
  font-weight: 850;
  line-height: 1.3;
  letter-spacing: -0.04em;
}

.community-write__content p {
  margin: 9px 0 0;

  color: var(--color-text-secondary);

  font-size: 12px;
  line-height: 1.6;
}

.community-write__link {
  display: grid;
  grid-template-columns:
    auto
    1fr
    auto;
  align-items: center;
  gap: 11px;

  min-height: 48px;
  padding: 0 15px;

  border-radius: var(--radius-md);

  background: var(--color-primary);
  color: #ffffff;

  font-size: 13px;
  font-weight: 750;
  text-decoration: none;

  box-shadow:
    0 9px 20px rgba(255, 122, 69, 0.2);

  transition:
    background-color var(--transition-fast),
    box-shadow var(--transition-fast),
    transform var(--transition-fast);
}

.community-write__link:hover {
  background: var(--color-primary-hover);

  box-shadow:
    0 12px 24px rgba(255, 122, 69, 0.27);

  transform: translateY(-2px);
}

.community-write__plus {
  display: grid;
  width: 28px;
  height: 28px;
  place-items: center;

  border-radius: 9px;

  background: rgba(255, 255, 255, 0.16);

  font-size: 18px;
  font-weight: 400;
}

.community-write__arrow {
  font-size: 16px;

  transition: transform var(--transition-fast);
}

.community-write__link:hover
  .community-write__arrow {
  transform: translateX(4px);
}

/* =================================
   검색 영역
================================= */

.community-tools {
  padding: 26px 0;

  border-bottom: 1px solid var(--color-border);

  background: #ffffff;
}

.community-tools__inner {
  display: grid;
  grid-template-columns:
    250px
    minmax(0, 1fr);
  align-items: center;
  gap: 32px;
}

.community-tools__heading {
  display: flex;
  flex-direction: column;
}

.community-tools__heading span {
  margin-bottom: 5px;

  color: var(--color-primary);

  font-size: 9px;
  font-weight: 850;
  letter-spacing: 0.13em;
}

.community-tools__heading strong {
  color: var(--color-text-primary);

  font-size: 17px;
  line-height: 1.4;
  letter-spacing: -0.025em;
}

.community-search {
  display: flex;
  gap: 9px;
}

.community-search__field {
  display: flex;
  min-width: 0;
  min-height: 48px;
  flex: 1;
  align-items: center;
  gap: 11px;

  padding: 0 16px;

  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);

  background: var(--color-background);

  transition:
    border-color var(--transition-fast),
    box-shadow var(--transition-fast);
}

.community-search__field:focus-within {
  border-color: var(--color-primary);

  box-shadow:
    0 0 0 3px rgba(255, 122, 69, 0.09);
}

.community-search__icon {
  width: 19px;
  height: 19px;

  flex-shrink: 0;

  fill: none;
  stroke: var(--color-text-disabled);
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.8;
}

.community-search__input {
  width: 100%;
  min-width: 0;
  height: 46px;

  padding: 0;

  border: 0;
  outline: 0;

  background: transparent;
  color: var(--color-text-primary);

  font: inherit;
  font-size: 14px;
}

.community-search__input::placeholder {
  color: var(--color-text-disabled);
}

.community-search__input::-webkit-search-cancel-button {
  cursor: pointer;
}

.community-search__button {
  min-width: 88px;
  min-height: 48px;

  padding: 0 20px;

  border: 0;
  border-radius: var(--radius-md);

  background: var(--color-text-primary);
  color: #ffffff;

  font: inherit;
  font-size: 13px;
  font-weight: 750;

  cursor: pointer;

  transition:
    background-color var(--transition-fast),
    transform var(--transition-fast);
}

.community-search__button:hover:not(:disabled) {
  background: var(--color-primary);

  transform: translateY(-1px);
}

.community-search__button:disabled {
  cursor: not-allowed;

  opacity: 0.5;
}

/* =================================
   게시글 영역
================================= */

.post-board {
  scroll-margin-top: 86px;

  padding: 43px 0 72px;

  background: var(--color-background);
}

.post-list-page__content {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 286px;
  align-items: start;
  gap: 18px;
}

.post-list-page__summary,
.post-list-page__filters {
  grid-column: 1 / -1;
}

.post-list-page__summary {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;

  margin-bottom: 0;
}

.post-list-page__summary-text {
  display: flex;
  align-items: flex-start;
  flex-direction: column;
}

.post-list-page__summary-eyebrow {
  margin-bottom: 6px;

  color: var(--color-primary);

  font-size: 9px;
  font-weight: 850;
  letter-spacing: 0.12em;
}

.post-list-page__summary strong {
  color: var(--color-text-primary);

  font-size: 21px;
  line-height: 1.35;
  letter-spacing: -0.035em;
}

.post-list-page__summary-text p {
  margin: 5px 0 0;

  color: var(--color-text-disabled);

  font-size: 11px;
}

.post-list-page__summary-actions {
  display: flex;
  flex-shrink: 0;
  align-items: center;
}

.post-list-page__summary-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;

  padding-bottom: 3px;

  border-bottom: 1px solid var(--color-border-strong);

  color: var(--color-text-secondary);

  font-size: 12px;
  font-weight: 750;
  text-decoration: none;

  transition:
    border-color var(--transition-fast),
    color var(--transition-fast),
    gap var(--transition-fast);
}

.post-list-page__summary-link:hover {
  gap: 11px;

  border-color: var(--color-primary);

  color: var(--color-primary);
}

/* 필터 및 정렬 */

.post-list-page__filters {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;

  margin-top: -2px;
  padding: 12px;

  border: 1px solid var(--color-border);
  border-radius: 15px;

  background: #ffffff;

  box-shadow:
    0 5px 14px rgba(45, 41, 38, 0.035);
}

.post-list-page__type-filter {
  display: inline-flex;
  align-items: center;
  gap: 5px;

  padding: 4px;

  border-radius: 11px;

  background: var(--color-background);
}

.post-list-page__type-button {
  min-height: 34px;

  padding: 0 13px;

  border: 0;
  border-radius: 9px;

  background: transparent;
  color: var(--color-text-secondary);

  font: inherit;
  font-size: 12px;
  font-weight: 650;

  cursor: pointer;

  transition:
    background-color var(--transition-fast),
    color var(--transition-fast),
    box-shadow var(--transition-fast);
}

.post-list-page__type-button:hover {
  color: var(--color-primary);
}

.post-list-page__type-button--active {
  background: #ffffff;
  color: var(--color-primary);

  box-shadow:
    0 3px 9px rgba(45, 41, 38, 0.07);
}

.post-list-page__filter-selects {
  display: flex;
  align-items: center;
  gap: 8px;
}

.post-list-page__select-control {
  display: inline-flex;
}

.post-list-page__filter-select {
  min-width: 112px;
  height: 39px;

  padding: 0 31px 0 12px;

  border: 1px solid var(--color-border);
  border-radius: 10px;
  outline: none;

  background: #ffffff;
  color: var(--color-text-secondary);

  font: inherit;
  font-size: 12px;
  font-weight: 650;

  cursor: pointer;

  transition:
    border-color var(--transition-fast),
    box-shadow var(--transition-fast);
}

.post-list-page__filter-select:hover {
  border-color: var(--color-border-strong);
}

.post-list-page__filter-select:focus {
  border-color: var(--color-primary);

  box-shadow:
    0 0 0 3px rgba(255, 122, 69, 0.09);
}

/* =================================
   게시글 목록
================================= */

.post-list {
  display: grid;
  grid-column: 1;
  gap: 9px;

  margin: 0;
  padding: 0;

  list-style: none;
}

.post-list__item {
  position: relative;

  overflow: hidden;

  border: 1px solid var(--color-border);
  border-radius: 15px;

  background: var(--color-surface);

  box-shadow:
    0 5px 14px rgba(45, 41, 38, 0.045);

  transition:
    border-color var(--transition-base),
    box-shadow var(--transition-base),
    transform var(--transition-base);
}

.post-list__item::before {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;

  width: 3px;

  content: '';
}

.post-list__item--restaurant::before {
  background: var(--color-primary);
}

.post-list__item--general::before {
  background: #4f987d;
}

.post-list__item:hover {
  border-color: rgba(255, 122, 69, 0.3);

  box-shadow:
    0 10px 22px rgba(93, 54, 34, 0.08);

  transform: translateY(-2px);
}

.post-list__link {
  display: flex;
  min-width: 0;
  align-items: center;
  justify-content: space-between;
  gap: 24px;

  padding: 15px 18px 14px 20px;

  color: inherit;
  text-decoration: none;
}

.post-list__main {
  min-width: 0;
  flex: 1;
}

.post-list__meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;

  margin-bottom: 8px;
}

.post-list__badge {
  display: inline-flex;
  min-width: 0;
  max-width: min(100%, 500px);
  align-items: center;
  gap: 7px;

  padding: 4px 9px;

  overflow: hidden;

  border-radius: var(--radius-pill);

  font-size: 10px;
  font-weight: 750;

  white-space: nowrap;
}

.post-list__badge-text {
  overflow: hidden;

  text-overflow: ellipsis;
}

.post-list__badge-dot {
  width: 5px;
  height: 5px;

  flex-shrink: 0;

  border-radius: 50%;

  background: currentColor;
}

.post-list__badge--restaurant {
  background: var(--color-primary-50);
  color: var(--color-primary-active);
}

.post-list__badge--general {
  background: #eaf6f1;
  color: #2f755d;
}

.post-list__date {
  flex-shrink: 0;

  color: var(--color-text-disabled);

  font-size: 10px;
  font-weight: 500;
}

.post-list__title {
  margin: 0;

  overflow: hidden;

  color: var(--color-text-primary);

  font-size: 17px;
  font-weight: 800;
  line-height: 1.4;
  letter-spacing: -0.025em;

  text-overflow: ellipsis;
  white-space: nowrap;
}

.post-list__content {
  display: -webkit-box;

  margin: 4px 0 0;

  overflow: hidden;

  color: var(--color-text-secondary);

  font-size: 12px;
  line-height: 1.55;

  -webkit-box-orient: vertical;
  -webkit-line-clamp: 1;
}

.post-list__side {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  gap: 12px;
}

.post-list__read-more {
  color: var(--color-text-disabled);

  font-size: 10px;
  font-weight: 700;

  transition: color var(--transition-fast);
}

.post-list__arrow {
  display: grid;
  width: 29px;
  height: 29px;
  place-items: center;

  border: 1px solid var(--color-border);
  border-radius: 50%;

  color: var(--color-text-disabled);

  font-size: 12px;

  transition:
    border-color var(--transition-fast),
    background-color var(--transition-fast),
    color var(--transition-fast),
    transform var(--transition-fast);
}

.post-list__item:hover
  .post-list__read-more {
  color: var(--color-primary);
}

.post-list__item:hover
  .post-list__arrow {
  border-color: var(--color-primary);

  background: var(--color-primary);
  color: #ffffff;

  transform: translateX(3px);
}

/* =================================
   최근 7일 인기 음식점
================================= */

.post-trending {
  position: sticky;
  top: calc(var(--header-height, 72px) + 18px);

  grid-column: 2;
  grid-row: 3;

  overflow: hidden;

  padding: 18px;

  border: 1px solid rgba(255, 122, 69, 0.18);
  border-radius: 17px;

  background:
    radial-gradient(
      circle at 100% 0%,
      rgba(255, 122, 69, 0.1),
      transparent 34%
    ),
    #ffffff;

  box-shadow:
    0 10px 25px rgba(45, 41, 38, 0.06);
}

.post-trending__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
}

.post-trending__header > div {
  display: flex;
  flex-direction: column;
}

.post-trending__eyebrow {
  margin-bottom: 5px;

  color: var(--color-primary);

  font-size: 8px;
  font-weight: 750;
  letter-spacing: 0.12em;
}

.post-trending__header strong {
  color: var(--color-text-primary);

  font-size: 16px;
  font-weight: 700;
}

.post-trending__icon {
  display: grid;
  width: 34px;
  height: 34px;
  flex-shrink: 0;
  place-items: center;

  border-radius: 11px;

  background: var(--color-primary-50);
  color: var(--color-primary);

  font-size: 14px;
}

.post-trending__description {
  margin: 11px 0 14px;

  color: var(--color-text-secondary);

  font-size: 11px;
  line-height: 1.6;
}

.post-trending__list {
  display: flex;
  flex-direction: column;
  gap: 7px;

  margin: 0;
  padding: 0;

  list-style: none;
}

.post-trending__link {
  display: grid;
  grid-template-columns: 28px minmax(0, 1fr) auto;
  align-items: center;
  gap: 10px;

  padding: 11px 10px;

  border: 1px solid transparent;
  border-radius: 12px;

  color: inherit;
  text-decoration: none;

  transition:
    border-color var(--transition-fast),
    background-color var(--transition-fast),
    transform var(--transition-fast);
}

.post-trending__link:hover {
  border-color: rgba(255, 122, 69, 0.2);

  background: #fff8f3;

  transform: translateX(2px);
}

.post-trending__rank {
  display: grid;
  width: 28px;
  height: 28px;
  place-items: center;

  border-radius: 9px;

  background: var(--color-primary-50);
  color: var(--color-primary);

  font-size: 11px;
  font-weight: 750;
}

.post-trending__copy {
  display: flex;
  min-width: 0;
  flex-direction: column;
}

.post-trending__copy strong {
  overflow: hidden;

  color: #4b4642;

  font-size: 13px;
  font-weight: 600;
  line-height: 1.4;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.post-trending__copy small {
  margin-top: 3px;

  color: var(--color-text-disabled);

  font-size: 10px;
}

.post-trending__arrow {
  color: var(--color-text-disabled);

  font-size: 12px;
}

.post-trending__empty {
  padding: 24px 10px;

  border-radius: 12px;

  background: var(--color-background);
  color: var(--color-text-disabled);

  font-size: 11px;
  line-height: 1.6;
  text-align: center;
}

/* =================================
   상태 화면
================================= */

.post-list-page__status {
  display: flex;
  align-items: center;
  flex-direction: column;

  padding: 58px 24px;

  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);

  background: var(--color-surface);
  color: var(--color-text-secondary);

  text-align: center;

  box-shadow: var(--shadow-card);
}

.post-list-page__status-icon {
  display: grid;
  width: 54px;
  height: 54px;
  place-items: center;

  margin-bottom: 17px;

  border-radius: 18px;

  background: var(--color-primary-50);
  color: var(--color-primary);

  font-size: 19px;
  font-weight: 850;
}

.post-list-page__status strong {
  color: var(--color-text-primary);

  font-size: 18px;
}

.post-list-page__status p {
  margin: 8px 0 0;

  font-size: 14px;
}

.post-list-page__status--error
  .post-list-page__status-icon {
  background: rgba(220, 38, 38, 0.08);
  color: var(--color-error);
}

.post-list-page__retry-button {
  min-height: 42px;

  margin-top: 20px;
  padding: 0 17px;

  border: 1px solid var(--color-primary);
  border-radius: var(--radius-md);

  background: var(--color-surface);
  color: var(--color-primary);

  font: inherit;
  font-size: 13px;
  font-weight: 750;

  cursor: pointer;
}

.post-list-page__retry-button:hover {
  background: var(--color-primary);
  color: #ffffff;
}

/* =================================
   빈 상태
================================= */

.post-list-page__empty {
  display: flex;
  grid-column: 1;
  align-items: center;
  flex-direction: column;

  padding: 54px 24px;

  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);

  background: var(--color-surface);
  color: var(--color-text-primary);

  text-align: center;

  box-shadow: var(--shadow-card);
}

.post-list-page__empty-visual {
  display: grid;
  width: 68px;
  height: 68px;
  place-items: center;

  margin-bottom: 19px;

  border-radius: 23px;

  background:
    linear-gradient(
      145deg,
      var(--color-primary-50),
      var(--color-accent-light)
    );

  font-size: 30px;
}

.post-list-page__empty strong {
  font-size: 18px;
}

.post-list-page__empty p {
  margin: 9px 0 0;

  color: var(--color-text-secondary);

  font-size: 14px;
}

.post-list-page__empty-link {
  display: inline-flex;
  min-height: 44px;
  align-items: center;
  gap: 9px;

  margin-top: 21px;
  padding: 0 18px;

  border-radius: var(--radius-md);

  background: var(--color-primary);
  color: #ffffff;

  font-size: 13px;
  font-weight: 750;
  text-decoration: none;
}

.post-list-page__empty-link:hover {
  background: var(--color-primary-hover);
}

/* =================================
   숫자 페이지네이션
================================= */

.post-list-page__pagination {
  display: flex;
  grid-column: 1;
  align-items: center;
  justify-content: center;
  gap: 14px;

  margin-top: 29px;
}

.post-list-page__page-numbers {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
}

.post-list-page__number-button {
  display: grid;
  width: 37px;
  height: 37px;
  place-items: center;

  padding: 0;

  border: 1px solid transparent;
  border-radius: 11px;

  background: transparent;
  color: var(--color-text-secondary);

  font: inherit;
  font-size: 12px;
  font-weight: 750;

  cursor: pointer;

  transition:
    border-color var(--transition-fast),
    background-color var(--transition-fast),
    color var(--transition-fast),
    transform var(--transition-fast);
}

.post-list-page__number-button:hover:not(
    .post-list-page__number-button--active
  ):not(:disabled) {
  border-color: var(--color-border);

  background: #ffffff;
  color: var(--color-primary);

  transform: translateY(-1px);
}

.post-list-page__number-button--active {
  border-color: var(--color-primary);

  background: var(--color-primary);
  color: #ffffff;

  box-shadow:
    0 7px 16px rgba(255, 122, 69, 0.2);
}

.post-list-page__number-button:disabled {
  cursor: not-allowed;
}

.post-list-page__ellipsis {
  display: grid;
  width: 25px;
  height: 37px;
  place-items: center;

  color: var(--color-text-disabled);

  font-size: 11px;
  font-weight: 800;
}

.post-list-page__page-button {
  display: inline-flex;
  min-width: 74px;
  min-height: 37px;
  align-items: center;
  justify-content: center;
  gap: 7px;

  padding: 0 12px;

  border: 1px solid var(--color-border);
  border-radius: 11px;

  background: var(--color-surface);
  color: var(--color-text-secondary);

  font: inherit;
  font-size: 12px;
  font-weight: 700;

  cursor: pointer;

  transition:
    border-color var(--transition-fast),
    color var(--transition-fast),
    transform var(--transition-fast);
}

.post-list-page__page-button:hover:not(:disabled) {
  border-color: var(--color-primary);

  color: var(--color-primary);

  transform: translateY(-1px);
}

.post-list-page__page-button:disabled {
  cursor: not-allowed;

  opacity: 0.38;
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
   태블릿
================================= */

@media (max-width: 1023px) {
  .community-editorial__inner {
    grid-template-columns:
      minmax(0, 1fr)
      320px;
    gap: 42px;
  }

  .community-editorial__title {
    font-size: 40px;
  }

  .community-tools__inner {
    grid-template-columns:
      220px
      minmax(0, 1fr);
    gap: 24px;
  }

  .post-list-page__content {
    grid-template-columns: minmax(0, 1fr) 250px;
  }

  .post-list-page__filters {
    align-items: stretch;
    flex-direction: column;
  }

  .post-list-page__filter-selects {
    justify-content: flex-end;
  }
}

/* =================================
   모바일
================================= */

@media (max-width: 767px) {
  .community-editorial__inner,
  .community-tools__inner,
  .post-board__inner {
    width: min(
      100% - 32px,
      var(--content-width)
    );
  }

  .community-editorial__inner {
    grid-template-columns: 1fr;
    gap: 30px;

    height: auto;
    padding: 42px 0;
  }

  .community-editorial__title {
    font-size: 34px;
  }

  .community-editorial__description {
    font-size: 14px;
  }

  .community-editorial__description br {
    display: none;
  }

  .community-write {
    height: auto;
    min-height: 185px;

    padding: 22px;
  }

  .community-write__content h2 {
    font-size: 21px;
  }

  .community-tools {
    padding: 22px 0;
  }

  .community-tools__inner {
    grid-template-columns: 1fr;
    gap: 14px;
  }

  .community-search {
    flex-direction: column;
  }

  .community-search__button {
    width: 100%;
  }

  .post-board {
    scroll-margin-top: 72px;

    padding: 37px 0 60px;
  }

  .post-list-page__summary {
    align-items: stretch;
    flex-direction: column;
    gap: 14px;
  }

  .post-list-page__summary strong {
    font-size: 19px;
  }

  .post-list-page__content {
    grid-template-columns: 1fr;
    gap: 14px;
  }

  .post-list-page__summary-actions {
    display: none;
  }

  .post-list-page__filters {
    align-items: stretch;
    flex-direction: column;
    gap: 10px;

    padding: 10px;
  }

  .post-list-page__type-filter {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .post-list-page__type-button {
    padding: 0 7px;

    font-size: 11px;
  }

  .post-list-page__filter-selects {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .post-list-page__select-control,
  .post-list-page__filter-select {
    width: 100%;
  }

  .post-list {
    grid-column: 1;
  }

  .post-trending {
    position: static;

    grid-column: 1;
    grid-row: auto;

    padding: 16px;
  }

  .post-list__link {
    align-items: flex-start;
    gap: 12px;

    padding: 15px 15px 14px 17px;
  }

  .post-list__meta {
    align-items: flex-start;
    flex-direction: column;
    gap: 6px;
  }

  .post-list__badge {
    max-width: 100%;
  }

  .post-list__date {
    font-size: 10px;
  }

  .post-list__title {
    font-size: 16px;
    white-space: normal;
  }

  .post-list__content {
    font-size: 12px;
  }

  .post-list__read-more {
    display: none;
  }

  .post-list__side {
    padding-top: 3px;
  }

  .post-list__arrow {
    width: 29px;
    height: 29px;
  }

  .post-list-page__status,
  .post-list-page__empty {
    padding: 46px 20px;
  }

  .post-list-page__pagination {
    gap: 6px;

    margin-top: 25px;
  }

  .post-list-page__page-numbers {
    gap: 2px;
  }

  .post-list-page__number-button {
    width: 33px;
    height: 33px;

    border-radius: 9px;

    font-size: 11px;
  }

  .post-list-page__ellipsis {
    width: 16px;
    height: 33px;
  }

  .post-list-page__page-button {
    min-width: 35px;
    width: 35px;
    min-height: 35px;

    padding: 0;
  }

  .post-list-page__direction-text {
    display: none;
  }
}

/* =================================
   모션 감소 설정
================================= */

@media (prefers-reduced-motion: reduce) {
  .community-write__link,
  .community-write__arrow,
  .community-search__button,
  .post-list__item,
  .post-list__arrow,
  .post-list__read-more,
  .post-list-page__number-button,
  .post-list-page__page-button,
  .post-list-page__type-button,
  .post-trending__link {
    transition: none;
  }
}
</style>