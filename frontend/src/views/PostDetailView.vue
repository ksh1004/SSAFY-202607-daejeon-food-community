<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { deletePost, getPostById } from '@/api/postApi'
import restaurantData from '@/data/data.json'

const route = useRoute()
const router = useRouter()

const post = ref(null)

const isLoading = ref(false)
const errorMessage = ref('')

const isDeleteModalOpen = ref(false)
const deletePassword = ref('')
const isDeletePasswordVisible = ref(false)
const isDeleting = ref(false)
const deleteErrorMessage = ref('')

/* =================================
   음식 카드 뒤집기
================================= */

const foodCardPool = [
  {
    id: 'korean',
    emoji: '🍚',
    name: '든든한 한식',
    description: '오늘은 따뜻하고 든든한 한 끼가 어울려요.',
  },
  {
    id: 'noodle',
    emoji: '🍜',
    name: '따뜻한 면 요리',
    description: '후루룩 즐기는 면 요리로 기분을 채워보세요.',
  },
  {
    id: 'snack',
    emoji: '🍢',
    name: '가볍게 분식',
    description: '떡볶이와 튀김처럼 익숙한 맛은 어떨까요?',
  },
  {
    id: 'meat',
    emoji: '🥩',
    name: '고기 한 판',
    description: '오늘은 맛있는 고기로 제대로 배를 채워보세요.',
  },
  {
    id: 'japanese',
    emoji: '🍣',
    name: '깔끔한 일식',
    description: '담백하고 깔끔한 일식 메뉴를 추천해요.',
  },
  {
    id: 'cafe',
    emoji: '🍰',
    name: '달콤한 카페',
    description: '커피와 디저트로 잠깐 쉬어가는 건 어떨까요?',
  },
  {
    id: 'chinese',
    emoji: '🥟',
    name: '풍미 가득 중식',
    description: '진한 풍미가 당기는 날에는 중식이 잘 어울려요.',
  },
  {
    id: 'western',
    emoji: '🍝',
    name: '기분 좋은 양식',
    description: '파스타와 피자 같은 특별한 한 끼를 즐겨보세요.',
  },
  {
    id: 'chicken',
    emoji: '🍗',
    name: '바삭한 치킨',
    description: '바삭하고 고소한 치킨으로 기분을 전환해 보세요.',
  },
]

const foodCards = ref([])
const selectedFoodCardIndex = ref(null)

const selectedFoodCard = computed(() => {
  if (selectedFoodCardIndex.value === null) {
    return null
  }

  return foodCards.value[selectedFoodCardIndex.value] ?? null
})

const shuffleArray = (items) => {
  const copiedItems = [...items]

  for (let index = copiedItems.length - 1; index > 0; index -= 1) {
    const randomIndex = Math.floor(Math.random() * (index + 1))

    ;[copiedItems[index], copiedItems[randomIndex]] = [
      copiedItems[randomIndex],
      copiedItems[index],
    ]
  }

  return copiedItems
}

const shuffleFoodCards = () => {
  foodCards.value = shuffleArray(foodCardPool).slice(0, 3)
  selectedFoodCardIndex.value = null
}

const selectFoodCard = (index) => {
  if (selectedFoodCardIndex.value !== null) {
    return
  }

  selectedFoodCardIndex.value = index
}

const moveToExplore = () => {
  router.push('/map')
}

shuffleFoodCards()

/* =================================
   음식점 데이터
================================= */

const restaurantItems = Array.isArray(restaurantData.items)
  ? restaurantData.items
  : []

const matchedRestaurant = computed(() => {
  if (!post.value || post.value.restaurant_id === null) {
    return null
  }

  const restaurantId = String(post.value.restaurant_id)

  return (
    restaurantItems.find(
      (restaurant) =>
        String(restaurant.contentid) === restaurantId,
    ) ?? null
  )
})

const restaurantTitle = computed(() => {
  return (
    matchedRestaurant.value?.title ??
    post.value?.restaurant_title ??
    '음식점 정보 없음'
  )
})

const restaurantAddress = computed(() => {
  if (!matchedRestaurant.value) {
    return ''
  }

  return [
    matchedRestaurant.value.addr1,
    matchedRestaurant.value.addr2,
  ]
    .filter(Boolean)
    .join(' ')
})

const normalizeImageUrl = (imageUrl) => {
  if (!imageUrl) {
    return ''
  }

  return imageUrl.replace(/^http:\/\//i, 'https://')
}

const restaurantImage = computed(() => {
  const firstImage = matchedRestaurant.value?.firstimage
  const secondImage = matchedRestaurant.value?.firstimage2

  return normalizeImageUrl(firstImage || secondImage || '')
})

const isUpdated = computed(() => {
  if (!post.value) {
    return false
  }

  return post.value.created_at !== post.value.updated_at
})

/* =================================
   공통 함수
================================= */

const getErrorDetailMessage = (detail) => {
  if (typeof detail === 'string') {
    return detail
  }

  if (!Array.isArray(detail)) {
    return ''
  }

  return detail
    .map((error) => error.msg)
    .filter(Boolean)
    .join(' / ')
}

const formatDateTime = (dateTime) => {
  if (!dateTime) {
    return ''
  }

  const date = new Date(dateTime)

  if (Number.isNaN(date.getTime())) {
    return dateTime
  }

  return new Intl.DateTimeFormat('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

/* =================================
   게시글 조회
================================= */

const fetchPost = async (routePostId) => {
  const parsedPostId = Number(routePostId)

  post.value = null
  errorMessage.value = ''

  if (!Number.isInteger(parsedPostId) || parsedPostId < 1) {
    isLoading.value = false
    errorMessage.value = '올바르지 않은 게시글 번호입니다.'
    return
  }

  isLoading.value = true

  try {
    const response = await getPostById(parsedPostId)

    post.value = response.data
  } catch (error) {
    post.value = null

    const detailMessage = getErrorDetailMessage(
      error.response?.data?.detail,
    )

    if (error.response?.status === 422) {
      errorMessage.value =
        detailMessage || '올바르지 않은 게시글 번호입니다.'
    } else if (error.response?.status === 404) {
      errorMessage.value =
        detailMessage || '존재하지 않는 게시글입니다.'
    } else if (!error.response) {
      errorMessage.value =
        '백엔드 서버에 연결할 수 없습니다. 서버 실행 상태를 확인해 주세요.'
    } else {
      errorMessage.value =
        detailMessage || '게시글을 불러오지 못했습니다.'
    }
  } finally {
    isLoading.value = false
  }
}

const retryFetchPost = () => {
  fetchPost(route.params.postId)
}

const moveToRestaurantDetail = () => {
  if (!post.value?.restaurant_id) {
    return
  }

  router.push(`/restaurants/${post.value.restaurant_id}`)
}

/* =================================
   게시글 삭제
================================= */

const openDeleteModal = () => {
  deletePassword.value = ''
  deleteErrorMessage.value = ''
  isDeletePasswordVisible.value = false
  isDeleteModalOpen.value = true
}

const closeDeleteModal = () => {
  if (isDeleting.value) {
    return
  }

  isDeleteModalOpen.value = false
  deletePassword.value = ''
  deleteErrorMessage.value = ''
  isDeletePasswordVisible.value = false
}

const handleDelete = async () => {
  if (isDeleting.value) {
    return
  }

  const trimmedPassword = deletePassword.value.trim()

  if (!trimmedPassword) {
    deleteErrorMessage.value = '비밀번호를 입력해 주세요.'
    return
  }

  const shouldDelete = window.confirm(
    '삭제한 게시글은 복구할 수 없습니다. 정말 삭제하시겠습니까?',
  )

  if (!shouldDelete) {
    return
  }

  isDeleting.value = true
  deleteErrorMessage.value = ''

  try {
    await deletePost(post.value.id, trimmedPassword)

    isDeleteModalOpen.value = false
    await router.push('/posts')
  } catch (error) {
    const detailMessage = getErrorDetailMessage(
      error.response?.data?.detail,
    )

    if (error.response?.status === 422) {
      deleteErrorMessage.value =
        detailMessage || '삭제 요청 정보가 올바르지 않습니다.'
    } else if (
      error.response?.status === 400 ||
      error.response?.status === 401 ||
      error.response?.status === 403
    ) {
      deleteErrorMessage.value =
        detailMessage || '비밀번호가 일치하지 않습니다.'
    } else if (error.response?.status === 404) {
      deleteErrorMessage.value =
        detailMessage || '존재하지 않는 게시글입니다.'
    } else if (!error.response) {
      deleteErrorMessage.value =
        '백엔드 서버에 연결할 수 없습니다.'
    } else {
      deleteErrorMessage.value =
        detailMessage || '게시글 삭제 중 오류가 발생했습니다.'
    }
  } finally {
    isDeleting.value = false
  }
}

watch(
  () => route.params.postId,
  (postId) => {
    fetchPost(postId)
  },
  {
    immediate: true,
  },
)
</script>

<template>
  <main class="post-detail-page">
    <div class="post-detail-shell">
      <!-- 상단 이동 및 관리 버튼 -->
      <!-- 상단 목록 이동 -->
      <header class="page-toolbar">
        <RouterLink
          to="/posts"
          class="page-toolbar__back"
        >
          <span aria-hidden="true">←</span>
          커뮤니티 목록
        </RouterLink>
      </header>

      <!-- 로딩 -->
      <section
        v-if="isLoading"
        class="post-detail-status"
        aria-live="polite"
      >
        <div
          class="post-detail-status__spinner"
          aria-hidden="true"
        ></div>

        <strong class="post-detail-status__title">
          게시글을 불러오고 있어요
        </strong>

        <p class="post-detail-status__message">
          잠시만 기다려 주세요.
        </p>
      </section>

      <!-- 오류 -->
      <section
        v-else-if="errorMessage"
        class="post-detail-status post-detail-status--error"
        role="alert"
      >
        <span
          class="post-detail-status__error-mark"
          aria-hidden="true"
        >
          !
        </span>

        <strong class="post-detail-status__title">
          게시글을 표시할 수 없습니다
        </strong>

        <p class="post-detail-status__message">
          {{ errorMessage }}
        </p>

        <div class="post-detail-status__actions">
          <RouterLink
            to="/posts"
            class="post-detail-status__button post-detail-status__button--secondary"
          >
            목록으로
          </RouterLink>

          <button
            type="button"
            class="post-detail-status__button post-detail-status__button--primary"
            @click="retryFetchPost"
          >
            다시 시도
          </button>
        </div>
      </section>

      <!-- 게시글 상세 -->
      <div
        v-else-if="post"
        class="post-layout"
      >
        <!-- 왼쪽: 게시글 -->
        <article class="story-card">
          <header class="story-card__header">
            <div class="story-card__category-row">
              <div class="story-card__category">
                <span
                  class="story-card__category-dot"
                  aria-hidden="true"
                ></span>

                <span v-if="post.restaurant_id">
                  {{ restaurantTitle }}
                </span>

                <span v-else>
                  일반 이야기
                </span>
              </div>

              <span class="story-card__number">
                POST {{ String(post.id).padStart(2, '0') }}
              </span>
            </div>

            <h1 class="story-card__title">
              {{ post.title }}
            </h1>

            <div class="story-card__meta">
              <span>
                작성 {{ formatDateTime(post.created_at) }}
              </span>

              <span v-if="isUpdated">
                수정 {{ formatDateTime(post.updated_at) }}
              </span>
            </div>
          </header>

          <div class="story-card__body">
            <div class="story-card__body-heading">
              <span>STORY</span>
              <strong>이야기 본문</strong>
            </div>

            <div class="story-card__content">
              {{ post.content }}
            </div>
          </div>

          <footer class="story-card__footer">
            <span>LOCALHUB COMMUNITY</span>

            <p>
              지역의 이야기를 함께 나누어 주셔서 감사해요.
            </p>
          </footer>
        </article>

        <!-- 오른쪽: 연결된 음식점 -->
        <aside
          v-if="post.restaurant_id"
          class="place-sidebar"
        >
          <div class="place-sidebar__heading">
            <div>
              <span>RELATED PLACE</span>
              <h2>이 글과 연결된 음식점</h2>
            </div>

            <span
              class="place-sidebar__pin"
              aria-hidden="true"
            >
              📍
            </span>
          </div>

          <button
            type="button"
            class="place-card"
            :aria-label="`${restaurantTitle} 음식점 상세보기`"
            @click="moveToRestaurantDetail"
          >
            <div class="place-card__thumbnail">
              <img
                v-if="restaurantImage"
                :src="restaurantImage"
                :alt="`${restaurantTitle} 이미지`"
                class="place-card__image"
              />

              <div
                v-else
                class="place-card__placeholder"
                aria-hidden="true"
              >
                <span>🍽️</span>
                <small>LOCAL PLACE</small>
              </div>

              <span class="place-card__image-label">
                연결된 음식점
              </span>
            </div>

            <div class="place-card__information">
              <span class="place-card__eyebrow">
                RESTAURANT
              </span>

              <strong class="place-card__title">
                {{ restaurantTitle }}
              </strong>

              <p
                v-if="restaurantAddress"
                class="place-card__address"
              >
                <span aria-hidden="true">📍</span>
                {{ restaurantAddress }}
              </p>

              <p
                v-else
                class="place-card__address place-card__address--empty"
              >
                주소 정보가 없습니다.
              </p>

              <div class="place-card__link">
                <span>음식점 상세보기</span>
                <span aria-hidden="true">→</span>
              </div>
            </div>
          </button>

          <p class="place-sidebar__guide">
            카드를 선택하면 음식점 위치와 상세 정보를 확인할 수
            있어요.
          </p>

          <div class="sidebar-post-actions">
            <span class="sidebar-post-actions__label">
              POST MANAGEMENT
            </span>

            <div class="sidebar-post-actions__buttons">
              <RouterLink
                :to="`/posts/${post.id}/edit`"
                class="sidebar-post-actions__button sidebar-post-actions__button--edit"
              >
                수정
              </RouterLink>

              <button
                type="button"
                class="sidebar-post-actions__button sidebar-post-actions__button--delete"
                @click="openDeleteModal"
              >
                삭제
              </button>
            </div>
          </div>
        </aside>

        <!-- 오른쪽: 음식 카드 뒤집기 -->
        <aside
          v-else
          class="food-game-sidebar"
        >
          <div class="food-game-sidebar__heading">
            <div>
              <span>FOOD PICK</span>
              <h2>오늘의 음식 카드</h2>
            </div>

            <span
              class="food-game-sidebar__icon"
              aria-hidden="true"
            >
              🎴
            </span>
          </div>

          <p class="food-game-sidebar__description">
            카드 한 장을 골라 오늘의 메뉴를 확인해 보세요.
          </p>

          <div class="food-card-deck">
            <button
              v-for="(foodCard, index) in foodCards"
              :key="foodCard.id"
              type="button"
              class="food-pick-card"
              :class="{
                'food-pick-card--flipped':
                  selectedFoodCardIndex === index,
                'food-pick-card--inactive':
                  selectedFoodCardIndex !== null &&
                  selectedFoodCardIndex !== index,
              }"
              :disabled="
                selectedFoodCardIndex !== null &&
                selectedFoodCardIndex !== index
              "
              :aria-label="
                selectedFoodCardIndex === index
                  ? `${foodCard.name} 카드`
                  : `${index + 1}번 음식 카드 선택`
              "
              @click="selectFoodCard(index)"
            >
              <span class="food-pick-card__inner">
                <span class="food-pick-card__front">
                  <span class="food-pick-card__pattern">
                    잇슈
                  </span>

                  <strong>?</strong>

                  <small>
                    CARD {{ index + 1 }}
                  </small>
                </span>

                <span class="food-pick-card__back">
                  <span
                    class="food-pick-card__emoji"
                    aria-hidden="true"
                  >
                    {{ foodCard.emoji }}
                  </span>

                  <strong>
                    {{ foodCard.name }}
                  </strong>
                </span>
              </span>
            </button>
          </div>

          <div
            v-if="!selectedFoodCard"
            class="food-game-empty"
          >
            <span aria-hidden="true">👆</span>

            <p>
              마음에 드는 카드를 선택해 주세요.
            </p>
          </div>

          <div
            v-else
            class="food-game-result"
            aria-live="polite"
          >
            <span class="food-game-result__label">
              오늘의 추천
            </span>

            <div class="food-game-result__title">
              <span aria-hidden="true">
                {{ selectedFoodCard.emoji }}
              </span>

              <strong>
                {{ selectedFoodCard.name }}
              </strong>
            </div>

            <p>
              {{ selectedFoodCard.description }}
            </p>

            <div class="food-game-result__actions">
              <button
                type="button"
                class="food-game-result__button food-game-result__button--shuffle"
                @click="shuffleFoodCards"
              >
                다시 섞기
              </button>

              <button
                type="button"
                class="food-game-result__button food-game-result__button--explore"
                @click="moveToExplore"
              >
                지도에서 찾기
                <span aria-hidden="true">→</span>
              </button>
            </div>
          </div>

          <p class="food-game-sidebar__guide">
            음식 카드는 가볍게 메뉴를 고르는 랜덤 추천이에요.
          </p>

          <div class="sidebar-post-actions">
            <span class="sidebar-post-actions__label">
              POST MANAGEMENT
            </span>

            <div class="sidebar-post-actions__buttons">
              <RouterLink
                :to="`/posts/${post.id}/edit`"
                class="sidebar-post-actions__button sidebar-post-actions__button--edit"
              >
                수정
              </RouterLink>

              <button
                type="button"
                class="sidebar-post-actions__button sidebar-post-actions__button--delete"
                @click="openDeleteModal"
              >
                삭제
              </button>
            </div>
          </div>
        </aside>
      </div>
    </div>

    <!-- 삭제 모달 -->
    <div
      v-if="isDeleteModalOpen"
      class="delete-modal"
      role="presentation"
      @click.self="closeDeleteModal"
    >
      <section
        class="delete-modal__panel"
        role="dialog"
        aria-modal="true"
        aria-labelledby="delete-modal-title"
      >
        <div class="delete-modal__mark" aria-hidden="true">
          !
        </div>

        <span class="delete-modal__eyebrow">
          DELETE POST
        </span>

        <h2
          id="delete-modal-title"
          class="delete-modal__title"
        >
          게시글을 삭제할까요?
        </h2>

        <p class="delete-modal__description">
          작성할 때 사용한 비밀번호를 입력해 주세요.
          삭제한 게시글은 복구할 수 없습니다.
        </p>

        <label
          for="delete-password"
          class="delete-modal__label"
        >
          삭제 비밀번호
        </label>

        <div class="delete-password-field">
          <input
            id="delete-password"
            v-model="deletePassword"
            :type="
              isDeletePasswordVisible
                ? 'text'
                : 'password'
            "
            class="delete-password-field__input"
            placeholder="비밀번호를 입력하세요."
            maxlength="20"
            autocomplete="current-password"
            :disabled="isDeleting"
            @keyup.enter="handleDelete"
          />

          <button
            type="button"
            class="delete-password-field__toggle"
            :disabled="isDeleting"
            :aria-label="
              isDeletePasswordVisible
                ? '삭제 비밀번호 숨기기'
                : '삭제 비밀번호 보기'
            "
            @click="
              isDeletePasswordVisible =
                !isDeletePasswordVisible
            "
          >
            {{
              isDeletePasswordVisible
                ? '숨기기'
                : '보기'
            }}
          </button>
        </div>

        <p
          v-if="deleteErrorMessage"
          class="delete-modal__error"
          role="alert"
        >
          {{ deleteErrorMessage }}
        </p>

        <div class="delete-modal__actions">
          <button
            type="button"
            class="delete-modal__button delete-modal__button--cancel"
            :disabled="isDeleting"
            @click="closeDeleteModal"
          >
            취소
          </button>

          <button
            type="button"
            class="delete-modal__button delete-modal__button--confirm"
            :disabled="isDeleting"
            @click="handleDelete"
          >
            {{ isDeleting ? '삭제 중...' : '삭제하기' }}
          </button>
        </div>
      </section>
    </div>
  </main>
</template>

<style scoped>
:global(html) {
  overflow-y: scroll;
  scrollbar-gutter: stable;
}

:global(body),
:global(#app) {
  width: 100%;
  min-width: 0;
}

.post-detail-page {
  width: 100%;
  min-height: calc(100vh - 72px);
  box-sizing: border-box;
  padding: 26px 0 80px;

  background:
    radial-gradient(
      circle at 88% 0%,
      rgba(255, 122, 69, 0.08),
      transparent 23%
    ),
    linear-gradient(
      180deg,
      #fffaf7 0,
      #f7f8fa 260px,
      #f7f8fa 100%
    );

  color: var(--color-text-primary);
}

.post-detail-shell {
  width: min(100% - 48px, var(--content-width));
  margin: 0 auto;
}

/* =================================
   상단 도구
================================= */

.page-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;

  margin-bottom: 17px;
}

.page-toolbar__back {
  display: inline-flex;
  align-items: center;
  gap: 8px;

  color: var(--color-text-secondary);

  font-size: 13px;
  font-weight: 750;
  text-decoration: none;

  transition:
    gap var(--transition-fast),
    color var(--transition-fast);
}

.page-toolbar__back:hover {
  gap: 12px;
  color: var(--color-primary);
}

.page-toolbar__actions {
  display: flex;
  gap: 8px;
}

.page-toolbar__button {
  display: inline-flex;
  min-width: 74px;
  min-height: 39px;
  align-items: center;
  justify-content: center;

  padding: 0 13px;

  border-radius: 11px;

  font-size: 12px;
  font-weight: 750;
  text-decoration: none;

  cursor: pointer;

  transition:
    border-color var(--transition-fast),
    background-color var(--transition-fast),
    color var(--transition-fast),
    transform var(--transition-fast);
}

.page-toolbar__button:hover {
  transform: translateY(-1px);
}

.page-toolbar__button--edit {
  border: 1px solid var(--color-border-strong);
  background: rgba(255, 255, 255, 0.9);
  color: var(--color-text-secondary);
}

.page-toolbar__button--edit:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.page-toolbar__button--delete {
  border: 1px solid rgba(220, 53, 69, 0.23);
  background: rgba(255, 255, 255, 0.9);
  color: var(--color-error);
}

.page-toolbar__button--delete:hover {
  border-color: var(--color-error);
  background: var(--color-error);
  color: #ffffff;
}

/* =================================
   게시글 + 사이드바
================================= */

.post-layout {
  display: grid;
  grid-template-columns:
    minmax(0, 1fr)
    minmax(280px, 330px);
  align-items: start;
  gap: 18px;
}

/* =================================
   게시글 카드
================================= */

.story-card {
  position: relative;

  min-width: 0;
  overflow: hidden;

  border: 1px solid rgba(228, 221, 215, 0.94);
  border-radius: 24px;

  background: #ffffff;

  box-shadow:
    0 18px 45px rgba(45, 41, 38, 0.08);
}

.story-card::before {
  position: absolute;
  top: 0;
  right: 0;
  left: 0;

  height: 4px;

  background:
    linear-gradient(
      90deg,
      var(--color-primary),
      #ffb067
    );

  content: '';
}

.story-card__header {
  padding: 40px 42px 31px;

  border-bottom: 1px solid var(--color-border);

  background:
    radial-gradient(
      circle at 96% 0%,
      rgba(255, 122, 69, 0.1),
      transparent 27%
    ),
    linear-gradient(
      135deg,
      #ffffff 48%,
      #fffaf7 100%
    );
}

.story-card__category-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;

  margin-bottom: 20px;
}

.story-card__category {
  display: inline-flex;
  align-items: center;
  gap: 9px;

  color: var(--color-primary);

  font-size: 12px;
  font-weight: 800;
}

.story-card__category-dot {
  width: 7px;
  height: 7px;

  border-radius: 50%;

  background: var(--color-primary);

  box-shadow:
    0 0 0 5px rgba(255, 122, 69, 0.09);
}

.story-card__number {
  color: var(--color-text-disabled);

  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.1em;
}

.story-card__title {
  max-width: 720px;
  margin: 0;

  font-size: clamp(25px, 2.4vw, 30px);
  font-weight: 850;
  line-height: 1.28;
  letter-spacing: -0.06em;

  overflow-wrap: anywhere;
}

.story-card__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 20px;

  margin-top: 22px;

  color: var(--color-text-disabled);

  font-size: 11px;
}

.story-card__body {
  padding: 34px 42px 30px;
}

.story-card__body-heading {
  display: flex;
  align-items: center;
  gap: 10px;

  margin-bottom: 25px;
}

.story-card__body-heading span {
  color: var(--color-primary);

  font-size: 9px;
  font-weight: 850;
  letter-spacing: 0.12em;
}

.story-card__body-heading span::after {
  display: inline-block;

  width: 28px;
  height: 1px;
  margin-left: 10px;

  background: rgba(255, 122, 69, 0.35);

  vertical-align: middle;

  content: '';
}

.story-card__body-heading strong {
  font-size: 15px;
  font-weight: 850;
}

.story-card__content {
  min-height: 310px;

  color: var(--color-text-primary);

  font-size: 16px;
  line-height: 1.95;
  white-space: pre-wrap;

  overflow-wrap: anywhere;
}

.story-card__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;

  padding: 17px 42px;

  border-top: 1px solid var(--color-border);

  background: #fafafa;
}

.story-card__footer > span {
  color: var(--color-primary);

  font-size: 9px;
  font-weight: 850;
  letter-spacing: 0.12em;
}

.story-card__footer p {
  margin: 0;

  color: var(--color-text-disabled);

  font-size: 10px;
}

/* =================================
   음식점 사이드바
================================= */

.place-sidebar,
.food-game-sidebar {
  min-width: 0;
  overflow: hidden;

  padding: 18px;

  border: 1px solid rgba(228, 221, 215, 0.94);
  border-radius: 22px;

  background: #ffffff;

  box-shadow:
    0 16px 38px rgba(45, 41, 38, 0.07);
}

.place-sidebar__heading,
.food-game-sidebar__heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;

  margin-bottom: 15px;
}

.place-sidebar__heading span:first-child,
.food-game-sidebar__heading div > span {
  display: block;

  margin-bottom: 5px;

  color: var(--color-primary);

  font-size: 9px;
  font-weight: 850;
  letter-spacing: 0.12em;
}

.place-sidebar__heading h2,
.food-game-sidebar__heading h2 {
  margin: 0;

  font-size: 17px;
  font-weight: 850;
  line-height: 1.35;
  letter-spacing: -0.035em;
}

.place-sidebar__pin,
.food-game-sidebar__icon {
  display: grid;
  flex-shrink: 0;
  place-items: center;

  width: 38px;
  height: 38px;

  border-radius: 13px;

  background: var(--color-primary-light);

  font-size: 17px;
}

/* 음식점 카드 */

.place-card {
  display: block;
  width: 100%;
  overflow: hidden;

  padding: 0;

  border: 1px solid rgba(255, 122, 69, 0.18);
  border-radius: 17px;

  background: #ffffff;
  color: inherit;

  font: inherit;
  text-align: left;

  cursor: pointer;

  transition:
    border-color var(--transition-base),
    box-shadow var(--transition-base),
    transform var(--transition-base);
}

.place-card:hover {
  border-color: rgba(255, 122, 69, 0.4);

  box-shadow:
    0 13px 28px rgba(45, 41, 38, 0.1);

  transform: translateY(-3px);
}

.place-card__thumbnail {
  position: relative;
  overflow: hidden;
}

.place-card__image,
.place-card__placeholder {
  width: 100%;
  height: 195px;
}

.place-card__image {
  display: block;
  object-fit: cover;

  transition: transform 450ms ease;
}

.place-card:hover .place-card__image {
  transform: scale(1.04);
}

.place-card__placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;

  background:
    linear-gradient(
      145deg,
      var(--color-primary-light),
      #ffffff
    );
}

.place-card__placeholder span {
  font-size: 38px;
}

.place-card__placeholder small {
  margin-top: 8px;

  color: var(--color-primary);

  font-size: 9px;
  font-weight: 850;
  letter-spacing: 0.12em;
}

.place-card__image-label {
  position: absolute;
  bottom: 11px;
  left: 11px;

  padding: 5px 8px;

  border-radius: var(--radius-pill);

  background: rgba(255, 255, 255, 0.92);
  color: var(--color-primary);

  font-size: 9px;
  font-weight: 850;
}

.place-card__information {
  padding: 20px 18px 17px;
}

.place-card__eyebrow {
  color: var(--color-primary);

  font-size: 9px;
  font-weight: 850;
  letter-spacing: 0.12em;
}

.place-card__title {
  display: block;

  margin-top: 8px;

  font-size: 20px;
  font-weight: 850;
  line-height: 1.35;
}

.place-card__address {
  display: flex;
  align-items: flex-start;
  gap: 5px;

  margin: 9px 0 0;

  color: var(--color-text-secondary);

  font-size: 11px;
  line-height: 1.55;
}

.place-card__address--empty {
  opacity: 0.7;
}

.place-card__link {
  display: flex;
  align-items: center;
  justify-content: space-between;

  margin-top: 19px;
  padding-top: 14px;

  border-top: 1px solid var(--color-border);

  color: var(--color-text-primary);

  font-size: 12px;
  font-weight: 800;
}

.place-card__link span:last-child {
  color: var(--color-primary);
  font-size: 17px;
}

.place-sidebar__guide,
.food-game-sidebar__guide {
  margin: 13px 3px 0;

  color: var(--color-text-disabled);

  font-size: 10px;
  line-height: 1.55;
}

/* =================================
   음식 카드 뒤집기
================================= */

.food-game-sidebar {
  background:
    radial-gradient(
      circle at 100% 0%,
      rgba(255, 122, 69, 0.09),
      transparent 32%
    ),
    #ffffff;
}

.food-game-sidebar__description {
  margin: -2px 0 17px;

  color: var(--color-text-secondary);

  font-size: 11px;
  line-height: 1.6;
}

.food-card-deck {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
}

.food-pick-card {
  height: 132px;

  padding: 0;

  border: 0;

  background: transparent;

  cursor: pointer;
  perspective: 900px;

  transition: opacity var(--transition-fast);
}

.food-pick-card:disabled {
  cursor: default;
}

.food-pick-card--inactive {
  opacity: 0.4;
}

.food-pick-card__inner {
  position: relative;

  display: block;
  width: 100%;
  height: 100%;

  transform-style: preserve-3d;

  transition: transform 520ms cubic-bezier(0.2, 0.8, 0.2, 1);
}

.food-pick-card:not(.food-pick-card--flipped):not(
    .food-pick-card--inactive
  ):hover
  .food-pick-card__inner {
  transform: translateY(-4px) rotate(-1deg);
}

.food-pick-card--flipped .food-pick-card__inner {
  transform: rotateY(180deg);
}

.food-pick-card__front,
.food-pick-card__back {
  position: absolute;
  inset: 0;

  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;

  overflow: hidden;

  border-radius: 14px;

  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
}

.food-pick-card__front {
  border: 1px solid rgba(255, 122, 69, 0.2);

  background:
    radial-gradient(
      circle at 20% 15%,
      rgba(255, 255, 255, 0.25),
      transparent 22%
    ),
    linear-gradient(
      145deg,
      var(--color-primary),
      #ff9a65
    );

  color: #ffffff;

  box-shadow:
    0 9px 20px rgba(255, 122, 69, 0.17);
}

.food-pick-card__front::before,
.food-pick-card__front::after {
  position: absolute;

  width: 38px;
  height: 38px;

  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 50%;

  content: '';
}

.food-pick-card__front::before {
  top: -13px;
  left: -13px;
}

.food-pick-card__front::after {
  right: -13px;
  bottom: -13px;
}

.food-pick-card__pattern {
  position: absolute;
  top: 10px;

  font-size: 8px;
  font-weight: 850;
  letter-spacing: 0.12em;

  opacity: 0.75;
}

.food-pick-card__front strong {
  font-size: 31px;
  font-weight: 800;
}

.food-pick-card__front small {
  position: absolute;
  bottom: 10px;

  font-size: 7px;
  font-weight: 800;
  letter-spacing: 0.1em;

  opacity: 0.75;
}

.food-pick-card__back {
  padding: 9px;

  box-sizing: border-box;

  border: 1px solid rgba(255, 122, 69, 0.26);

  background:
    radial-gradient(
      circle at 50% 25%,
      rgba(255, 122, 69, 0.12),
      transparent 40%
    ),
    #fffaf7;

  color: var(--color-text-primary);

  transform: rotateY(180deg);
}

.food-pick-card__emoji {
  font-size: 29px;
}

.food-pick-card__back strong {
  margin-top: 9px;

  font-size: 10px;
  font-weight: 850;
  line-height: 1.4;
  text-align: center;
}

.food-game-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 7px;

  min-height: 56px;
  margin-top: 13px;
  padding: 0 12px;

  border-radius: 13px;

  background: var(--color-background);
  color: var(--color-text-secondary);
}

.food-game-empty p {
  margin: 0;

  font-size: 10px;
}

/* 선택 결과 */

.food-game-result {
  margin-top: 13px;
  padding: 15px;

  border: 1px solid rgba(255, 122, 69, 0.16);
  border-radius: 15px;

  background:
    linear-gradient(
      145deg,
      #fffaf7,
      #ffffff
    );

  animation: food-result-open 300ms ease;
}

.food-game-result__label {
  color: var(--color-primary);

  font-size: 8px;
  font-weight: 850;
  letter-spacing: 0.12em;
}

.food-game-result__title {
  display: flex;
  align-items: center;
  gap: 9px;

  margin-top: 9px;
}

.food-game-result__title span {
  font-size: 24px;
}

.food-game-result__title strong {
  font-size: 17px;
  font-weight: 850;
  letter-spacing: -0.035em;
}

.food-game-result > p {
  margin: 9px 0 0;

  color: var(--color-text-secondary);

  font-size: 10px;
  line-height: 1.6;
}

.food-game-result__actions {
  display: grid;
  grid-template-columns: 0.85fr 1.15fr;
  gap: 7px;

  margin-top: 14px;
}

.food-game-result__button {
  display: inline-flex;
  min-height: 39px;
  align-items: center;
  justify-content: center;
  gap: 6px;

  padding: 0 9px;

  border-radius: 11px;

  font-size: 10px;
  font-weight: 800;

  cursor: pointer;

  transition:
    border-color var(--transition-fast),
    background-color var(--transition-fast),
    color var(--transition-fast),
    transform var(--transition-fast);
}

.food-game-result__button:hover {
  transform: translateY(-2px);
}

.food-game-result__button--shuffle {
  border: 1px solid var(--color-border-strong);

  background: #ffffff;
  color: var(--color-text-secondary);
}

.food-game-result__button--shuffle:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.food-game-result__button--explore {
  border: 1px solid var(--color-primary);

  background: var(--color-primary);
  color: #ffffff;
}

/* =================================
   사이드바 게시글 관리
================================= */

.sidebar-post-actions {
  margin-top: 17px;
  padding-top: 15px;

  border-top: 1px solid var(--color-border);
}

.sidebar-post-actions__label {
  display: block;

  margin-bottom: 9px;

  color: var(--color-text-disabled);

  font-size: 8px;
  font-weight: 700;
  letter-spacing: 0.11em;
}

.sidebar-post-actions__buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.sidebar-post-actions__button {
  display: inline-flex;
  min-height: 40px;
  align-items: center;
  justify-content: center;

  padding: 0 12px;

  border-radius: 11px;

  font: inherit;
  font-size: 12px;
  font-weight: 650;
  text-decoration: none;

  cursor: pointer;

  transition:
    border-color var(--transition-fast),
    background-color var(--transition-fast),
    color var(--transition-fast),
    transform var(--transition-fast);
}

.sidebar-post-actions__button:hover {
  transform: translateY(-1px);
}

.sidebar-post-actions__button--edit {
  border: 1px solid var(--color-border-strong);

  background: #ffffff;
  color: var(--color-text-secondary);
}

.sidebar-post-actions__button--edit:hover {
  border-color: var(--color-primary);

  background: #fff8f3;
  color: var(--color-primary);
}

.sidebar-post-actions__button--delete {
  border: 1px solid rgba(220, 53, 69, 0.2);

  background: rgba(220, 53, 69, 0.04);
  color: var(--color-error);
}

.sidebar-post-actions__button--delete:hover {
  border-color: var(--color-error);

  background: var(--color-error);
  color: #ffffff;
}


/* =================================
   상태 화면
================================= */

.post-detail-status {
  padding: 64px 30px;

  border: 1px solid var(--color-border);
  border-radius: 24px;

  background: #ffffff;

  text-align: center;

  box-shadow:
    0 18px 45px rgba(32, 33, 36, 0.07);
}

.post-detail-status__spinner {
  width: 24px;
  height: 24px;
  margin: 0 auto 20px;

  border: 3px solid rgba(255, 122, 69, 0.18);
  border-top-color: var(--color-primary);
  border-radius: 50%;

  animation: status-spin 800ms linear infinite;
}

.post-detail-status__error-mark {
  display: grid;
  place-items: center;

  width: 50px;
  height: 50px;
  margin: 0 auto 19px;

  border-radius: 16px;

  background: rgba(220, 53, 69, 0.08);
  color: var(--color-error);

  font-size: 22px;
  font-weight: 850;
}

.post-detail-status__title {
  display: block;

  font-size: 20px;
  font-weight: 850;
}

.post-detail-status__message {
  margin: 9px 0 0;

  color: var(--color-text-secondary);

  font-size: 14px;
}

.post-detail-status__actions {
  display: flex;
  justify-content: center;
  gap: 9px;

  margin-top: 25px;
}

.post-detail-status__button {
  display: inline-flex;
  min-width: 106px;
  min-height: 44px;
  align-items: center;
  justify-content: center;

  padding: 0 16px;

  border-radius: var(--radius-md);

  font: inherit;
  font-size: 13px;
  font-weight: 750;
  text-decoration: none;

  cursor: pointer;
}

.post-detail-status__button--secondary {
  border: 1px solid var(--color-border-strong);
  background: #ffffff;
  color: var(--color-text-secondary);
}

.post-detail-status__button--primary {
  border: 1px solid var(--color-primary);
  background: var(--color-primary);
  color: #ffffff;
}

/* =================================
   삭제 모달
================================= */

.delete-modal {
  position: fixed;
  inset: 0;
  z-index: 2000;

  display: grid;
  place-items: center;

  padding: 20px;

  background: rgba(28, 27, 26, 0.52);

  backdrop-filter: blur(6px);
}

.delete-modal__panel {
  width: min(100%, 430px);
  padding: 29px;

  box-sizing: border-box;

  border-radius: 22px;

  background: #ffffff;

  box-shadow:
    0 26px 70px rgba(15, 23, 42, 0.24);

  animation: modal-open 220ms ease;
}

.delete-modal__mark {
  display: grid;
  place-items: center;

  width: 48px;
  height: 48px;
  margin-bottom: 18px;

  border-radius: 15px;

  background: rgba(220, 53, 69, 0.08);
  color: var(--color-error);

  font-size: 21px;
  font-weight: 850;
}

.delete-modal__eyebrow {
  display: block;

  margin-bottom: 6px;

  color: var(--color-error);

  font-size: 9px;
  font-weight: 850;
  letter-spacing: 0.12em;
}

.delete-modal__title {
  margin: 0;

  font-size: 23px;
  font-weight: 850;
}

.delete-modal__description {
  margin: 12px 0 0;

  color: var(--color-text-secondary);

  font-size: 13px;
  line-height: 1.7;
}

.delete-modal__label {
  display: block;

  margin: 22px 0 9px;

  font-size: 13px;
  font-weight: 800;
}

.delete-password-field {
  position: relative;
}

.delete-password-field__input {
  width: 100%;
  min-height: 50px;

  box-sizing: border-box;
  padding: 0 78px 0 15px;

  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);

  background: #ffffff;
  color: var(--color-text-primary);

  font: inherit;

  outline: none;
}

.delete-password-field__input:focus {
  border-color: var(--color-primary);

  box-shadow:
    0 0 0 4px rgba(255, 122, 69, 0.1);
}

.delete-password-field__toggle {
  position: absolute;
  top: 50%;
  right: 10px;

  min-width: 54px;
  min-height: 31px;

  border: 0;
  border-radius: var(--radius-sm);

  background: var(--color-primary-light);
  color: var(--color-primary);

  font-size: 11px;
  font-weight: 750;

  cursor: pointer;

  transform: translateY(-50%);
}

.delete-modal__error {
  margin: 13px 0 0;
  padding: 11px 13px;

  border: 1px solid rgba(220, 53, 69, 0.22);
  border-radius: var(--radius-md);

  background: rgba(220, 53, 69, 0.05);
  color: var(--color-error);

  font-size: 12px;
  font-weight: 700;
}

.delete-modal__actions {
  display: flex;
  justify-content: flex-end;
  gap: 9px;

  margin-top: 24px;
  padding-top: 21px;

  border-top: 1px solid var(--color-border);
}

.delete-modal__button {
  min-width: 96px;
  min-height: 43px;

  padding: 0 15px;

  border-radius: var(--radius-md);

  font-size: 13px;
  font-weight: 750;

  cursor: pointer;
}

.delete-modal__button--cancel {
  border: 1px solid var(--color-border-strong);
  background: #ffffff;
  color: var(--color-text-secondary);
}

.delete-modal__button--confirm {
  border: 1px solid var(--color-error);
  background: var(--color-error);
  color: #ffffff;
}

.delete-modal__button:disabled,
.delete-password-field__toggle:disabled {
  cursor: not-allowed;
  opacity: 0.65;
}

/* =================================
   애니메이션
================================= */

@keyframes status-spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes modal-open {
  from {
    opacity: 0;
    transform: translateY(10px) scale(0.98);
  }

  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes food-result-open {
  from {
    opacity: 0;
    transform: translateY(7px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* =================================
   태블릿
================================= */

@media (max-width: 1000px) {
  .post-layout {
    grid-template-columns:
      minmax(0, 1fr)
      minmax(250px, 290px);
  }

  .story-card__header,
  .story-card__body {
    padding-right: 34px;
    padding-left: 34px;
  }

  .story-card__footer {
    padding-right: 34px;
    padding-left: 34px;
  }

  .food-pick-card {
    height: 120px;
  }
}

/* =================================
   모바일
================================= */

@media (max-width: 767px) {
  .post-detail-page {
    padding: 19px 0 60px;
  }

  .post-detail-shell {
    width: min(100% - 32px, var(--content-width));
  }

  .page-toolbar {
    margin-bottom: 13px;
  }

  .page-toolbar__back {
    font-size: 12px;
  }

  .page-toolbar__button {
    min-width: 58px;
    min-height: 35px;
    padding: 0 10px;
  }

  .post-layout {
    grid-template-columns: minmax(0, 1fr);
    gap: 14px;
  }

  .story-card {
    border-radius: 20px;
  }

  .story-card__header {
    padding: 32px 22px 26px;
  }

  .story-card__number {
    display: none;
  }

  .story-card__title {
    font-size: 23px;
    line-height: 1.4;
  }

  .story-card__meta {
    flex-direction: column;
    gap: 5px;
  }

  .story-card__body {
    padding: 28px 22px 24px;
  }

  .story-card__content {
    min-height: 170px;

    font-size: 15px;
    line-height: 1.85;
  }

  .story-card__footer {
    align-items: flex-start;
    flex-direction: column;
    gap: 7px;

    padding: 16px 22px;
  }

  .place-sidebar,
  .food-game-sidebar {
    padding: 16px;
    border-radius: 20px;
  }

  .place-card__image,
  .place-card__placeholder {
    height: 210px;
  }

  .food-pick-card {
    height: 145px;
  }

  .food-pick-card__front strong {
    font-size: 36px;
  }

  .food-pick-card__emoji {
    font-size: 34px;
  }

  .food-game-result__actions {
    grid-template-columns: 1fr;
  }

  .post-detail-status {
    padding: 48px 22px;
  }

  .post-detail-status__actions {
    flex-direction: column;
  }

  .post-detail-status__button {
    width: 100%;
    box-sizing: border-box;
  }

  .delete-modal__panel {
    padding: 25px 21px;
  }

  .delete-modal__actions {
    flex-direction: column-reverse;
  }

  .delete-modal__button {
    width: 100%;
  }
}

@media (prefers-reduced-motion: reduce) {
  .post-detail-status__spinner,
  .delete-modal__panel,
  .food-game-result {
    animation: none;
  }

  .food-pick-card__inner {
    transition: none;
  }
}
</style>