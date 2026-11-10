<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

import { createPost } from '@/api/postApi'
import restaurantData from '@/data/data.json'

const router = useRouter()

const title = ref('')
const content = ref('')
const password = ref('')
const isPasswordVisible = ref(false)

const restaurantKeyword = ref('')
const selectedRestaurant = ref(null)
const isRestaurantSearchOpen = ref(false)

const isSubmitting = ref(false)
const errorMessage = ref('')

const restaurants = computed(() => {
  if (Array.isArray(restaurantData)) {
    return restaurantData
  }

  return restaurantData.items ?? []
})

const filteredRestaurants = computed(() => {
  const keyword = restaurantKeyword.value.trim().toLowerCase()

  if (!keyword) {
    return restaurants.value
  }

  return restaurants.value.filter((restaurant) => {
    const restaurantTitle = restaurant.title?.toLowerCase() ?? ''
    const addr1 = restaurant.addr1?.toLowerCase() ?? ''
    const addr2 = restaurant.addr2?.toLowerCase() ?? ''

    return (
      restaurantTitle.includes(keyword) ||
      addr1.includes(keyword) ||
      addr2.includes(keyword)
    )
  })
})

const hasFormContent = computed(() => {
  return (
    title.value.trim() !== '' ||
    content.value.trim() !== '' ||
    password.value.trim() !== '' ||
    selectedRestaurant.value !== null
  )
})

const openRestaurantSearch = () => {
  if (isSubmitting.value) {
    return
  }

  isRestaurantSearchOpen.value = true
}

const handleRestaurantKeywordInput = (event) => {
  restaurantKeyword.value = event.target.value
  isRestaurantSearchOpen.value = true
}

const selectRestaurant = (restaurant) => {
  if (isSubmitting.value) {
    return
  }

  selectedRestaurant.value = restaurant
  restaurantKeyword.value = ''
  isRestaurantSearchOpen.value = false
}

const changeSelectedRestaurant = () => {
  if (isSubmitting.value) {
    return
  }

  selectedRestaurant.value = null
  restaurantKeyword.value = ''
  isRestaurantSearchOpen.value = true
}

const clearSelectedRestaurant = () => {
  if (isSubmitting.value) {
    return
  }

  selectedRestaurant.value = null
  restaurantKeyword.value = ''
  isRestaurantSearchOpen.value = false
}

const validateForm = () => {
  if (!title.value.trim()) {
    window.alert('제목을 입력해 주세요.')
    return false
  }

  if (!content.value.trim()) {
    window.alert('내용을 입력해 주세요.')
    return false
  }

  if (!password.value.trim()) {
    window.alert('수정 및 삭제에 사용할 비밀번호를 입력해 주세요.')
    return false
  }

  return true
}

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

const handleCancel = () => {
  if (isSubmitting.value) {
    return
  }

  if (hasFormContent.value) {
    const shouldCancel = window.confirm(
      '작성 중인 내용이 사라집니다. 게시글 작성을 취소하시겠습니까?',
    )

    if (!shouldCancel) {
      return
    }
  }

  router.push('/posts')
}

const handleSubmit = async () => {
  if (isSubmitting.value || !validateForm()) {
    return
  }

  isSubmitting.value = true
  errorMessage.value = ''
  isRestaurantSearchOpen.value = false

  const postData = {
    restaurant_id: selectedRestaurant.value?.contentid ?? null,
    title: title.value.trim(),
    content: content.value.trim(),
    password: password.value,
  }

  try {
    const response = await createPost(postData)

    router.push(`/posts/${response.data.id}`)
  } catch (error) {
    const detailMessage = getErrorDetailMessage(
      error.response?.data?.detail,
    )

    if (error.response?.status === 422) {
      errorMessage.value =
        detailMessage ||
        '입력한 게시글 정보가 올바르지 않습니다.'
    } else if (error.response?.status === 404) {
      errorMessage.value =
        detailMessage ||
        '선택한 음식점 정보를 찾을 수 없습니다.'
    } else if (error.response?.status === 400) {
      errorMessage.value =
        detailMessage ||
        '게시글을 등록할 수 없습니다. 입력 내용을 확인해 주세요.'
    } else if (!error.response) {
      errorMessage.value =
        '백엔드 서버에 연결할 수 없습니다. 서버 실행 상태를 확인해 주세요.'
    } else {
      errorMessage.value =
        detailMessage || '게시글 작성 중 오류가 발생했습니다.'
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <main class="post-create-page">
    <!-- 상단 소개 영역 -->
    <section class="post-create-hero">
      <div
        class="post-create-hero__decoration post-create-hero__decoration--top"
      ></div>

      <div
        class="post-create-hero__decoration post-create-hero__decoration--bottom"
      ></div>

      <div class="post-create-page__inner">
        <header class="post-create-page__header">
          <span class="post-create-page__eyebrow">
            <span class="post-create-page__eyebrow-dot"></span>
            LOCAL COMMUNITY
          </span>

          <h1 class="post-create-page__title">
            나만의 맛있는<br />
            <strong>이야기</strong>를 남겨보세요
          </h1>

          <p class="post-create-page__description">
            대전·충청권에서 발견한 맛집과 음식에 대한 이야기를
            자유롭게 공유해 주세요.
          </p>

          <div class="post-create-page__guide">
            <span>익명 작성</span>
            <span>음식점 연결</span>
            <span>비밀번호로 수정·삭제</span>
          </div>
        </header>
      </div>
    </section>

    <!-- 작성 폼 -->
    <section class="post-create-content">
      <div class="post-create-page__inner">
        <form class="post-form" @submit.prevent="handleSubmit">
          <div class="post-form__heading">
            <div>
              <span class="post-form__heading-eyebrow">
                WRITE YOUR STORY
              </span>

              <h2>게시글 작성</h2>

              <p>
                <span class="post-form__required">*</span>
                표시는 필수 입력 항목입니다.
              </p>
            </div>

            <div class="post-form__heading-icon" aria-hidden="true">
              ✍️
            </div>
          </div>

          <!-- 제목 -->
          <div class="post-form__group">
            <div class="post-form__label-area">
              <span class="post-form__number">01</span>

              <div>
                <label for="title" class="post-form__label">
                  제목
                  <span class="post-form__required">*</span>
                </label>

                <p class="post-form__label-description">
                  어떤 이야기인지 알 수 있도록 제목을 작성해 주세요.
                </p>
              </div>
            </div>

            <input
              id="title"
              v-model="title"
              type="text"
              maxlength="100"
              class="post-form__input"
              placeholder="예: 대전역 근처에서 발견한 칼국수 맛집"
              :disabled="isSubmitting"
            />

            <div class="post-form__count">
              {{ title.length }} / 100
            </div>
          </div>

          <!-- 음식점 -->
          <div class="post-form__group">
            <div class="post-form__label-area">
              <span class="post-form__number">02</span>

              <div>
                <label
                  for="restaurant-search"
                  class="post-form__label"
                >
                  음식점

                  <span class="post-form__optional">
                    선택 사항
                  </span>
                </label>

                <p class="post-form__label-description">
                  게시글과 관련된 음식점을 검색해 연결할 수 있어요.
                </p>
              </div>
            </div>

            <div
              v-if="selectedRestaurant"
              class="selected-restaurant"
            >
              <div class="selected-restaurant__icon" aria-hidden="true">
                📍
              </div>

              <div class="selected-restaurant__information">
                <span class="selected-restaurant__badge">
                  선택된 음식점
                </span>

                <strong class="selected-restaurant__title">
                  {{ selectedRestaurant.title }}
                </strong>

                <span class="selected-restaurant__address">
                  {{ selectedRestaurant.addr1 }}
                  {{ selectedRestaurant.addr2 }}
                </span>
              </div>

              <div class="selected-restaurant__actions">
                <button
                  type="button"
                  class="selected-restaurant__button"
                  :disabled="isSubmitting"
                  @click="changeSelectedRestaurant"
                >
                  변경
                </button>

                <button
                  type="button"
                  class="selected-restaurant__button selected-restaurant__button--remove"
                  :disabled="isSubmitting"
                  @click="clearSelectedRestaurant"
                >
                  해제
                </button>
              </div>
            </div>

            <div v-else class="restaurant-search">
              <div class="restaurant-search__field">
                <span
                  class="restaurant-search__icon"
                  aria-hidden="true"
                >
                  ⌕
                </span>

                <input
                  id="restaurant-search"
                  :value="restaurantKeyword"
                  type="search"
                  class="post-form__input restaurant-search__input"
                  placeholder="음식점명이나 주소를 검색하세요."
                  autocomplete="off"
                  :disabled="isSubmitting"
                  @focus="openRestaurantSearch"
                  @input="handleRestaurantKeywordInput"
                  @compositionupdate="handleRestaurantKeywordInput"
                />
              </div>

              <div
                v-if="isRestaurantSearchOpen"
                class="restaurant-search__results"
              >
                <div class="restaurant-search__result-heading">
                  <span>검색 결과</span>

                  <strong>
                    {{ filteredRestaurants.length }}개
                  </strong>
                </div>

                <button
                  v-for="restaurant in filteredRestaurants"
                  :key="restaurant.contentid"
                  type="button"
                  class="restaurant-search__item"
                  :disabled="isSubmitting"
                  @click="selectRestaurant(restaurant)"
                >
                  <span
                    class="restaurant-search__item-icon"
                    aria-hidden="true"
                  >
                    📍
                  </span>

                  <span class="restaurant-search__item-copy">
                    <strong class="restaurant-search__title">
                      {{ restaurant.title }}
                    </strong>

                    <span class="restaurant-search__address">
                      {{ restaurant.addr1 }}
                      {{ restaurant.addr2 }}
                    </span>
                  </span>

                  <span
                    class="restaurant-search__arrow"
                    aria-hidden="true"
                  >
                    →
                  </span>
                </button>

                <p
                  v-if="filteredRestaurants.length === 0"
                  class="restaurant-search__empty"
                >
                  <span aria-hidden="true">🔍</span>
                  검색 결과가 없습니다.
                </p>
              </div>
            </div>

            <p class="post-form__help">
              특정 음식점에 관한 글이 아니라면 선택하지 않아도
              됩니다.
            </p>
          </div>

          <!-- 내용 -->
          <div class="post-form__group">
            <div class="post-form__label-area">
              <span class="post-form__number">03</span>

              <div>
                <label for="content" class="post-form__label">
                  내용
                  <span class="post-form__required">*</span>
                </label>

                <p class="post-form__label-description">
                  음식, 분위기, 방문 경험 등 솔직한 이야기를
                  작성해 주세요.
                </p>
              </div>
            </div>

            <textarea
              id="content"
              v-model="content"
              class="post-form__textarea"
              placeholder="어떤 음식을 먹었는지, 가게 분위기는 어땠는지 자유롭게 작성해 보세요."
              :disabled="isSubmitting"
            />
          </div>

          <!-- 비밀번호 -->
          <div class="post-form__group post-form__group--last">
            <div class="post-form__label-area">
              <span class="post-form__number">04</span>

              <div>
                <label for="password" class="post-form__label">
                  수정 / 삭제 비밀번호
                  <span class="post-form__required">*</span>
                </label>

                <p class="post-form__label-description">
                  작성한 게시글을 수정하거나 삭제할 때 사용합니다.
                </p>
              </div>
            </div>

            <div class="password-field">
              <input
                id="password"
                v-model="password"
                :type="isPasswordVisible ? 'text' : 'password'"
                maxlength="20"
                class="post-form__input password-field__input"
                placeholder="비밀번호를 입력하세요."
                autocomplete="new-password"
                :disabled="isSubmitting"
              />

              <button
                type="button"
                class="password-field__toggle"
                :disabled="isSubmitting"
                :aria-label="
                  isPasswordVisible
                    ? '비밀번호 숨기기'
                    : '비밀번호 보기'
                "
                @click="isPasswordVisible = !isPasswordVisible"
              >
                {{ isPasswordVisible ? '숨기기' : '보기' }}
              </button>
            </div>

            <div class="post-form__notice">
              <span aria-hidden="true">🔒</span>

              <p>
                입력한 비밀번호는 다시 확인할 수 없으므로
                잊어버리지 않도록 주의해 주세요.
              </p>
            </div>
          </div>

          <!-- 오류 메시지 -->
          <div
            v-if="errorMessage"
            class="post-form__error"
            role="alert"
          >
            <span aria-hidden="true">!</span>
            {{ errorMessage }}
          </div>

          <!-- 버튼 -->
          <div class="post-form__actions">
            <button
              type="button"
              class="post-form__cancel"
              :disabled="isSubmitting"
              @click="handleCancel"
            >
              취소
            </button>

            <button
              type="submit"
              class="post-form__submit"
              :disabled="isSubmitting"
            >
              <span>
                {{ isSubmitting ? '작성 중...' : '게시글 작성' }}
              </span>

              <span v-if="!isSubmitting" aria-hidden="true">
                →
              </span>
            </button>
          </div>
        </form>
      </div>
    </section>
  </main>
</template>

<style scoped>
.post-create-page {
  overflow: hidden;

  background: #ffffff;
  color: var(--color-text-primary);
}

.post-create-page__inner {
  width: min(100% - 48px, var(--content-width));
  margin: 0 auto;
}

/* =================================
   상단 소개 영역
================================= */

.post-create-hero {
  position: relative;

  padding: 72px 0 92px;

  border-bottom: 1px solid var(--color-border);

  background:
    radial-gradient(
      circle at 86% 24%,
      rgba(255, 122, 69, 0.11),
      transparent 27%
    ),
    radial-gradient(
      circle at 8% 90%,
      rgba(255, 184, 77, 0.07),
      transparent 24%
    ),
    #ffffff;
}

.post-create-page__header {
  position: relative;
  z-index: 1;

  width: min(100%, 820px);
  margin: 0 auto;
}

.post-create-page__eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 9px;

  margin-bottom: 20px;

  color: var(--color-text-secondary);

  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.12em;
}

.post-create-page__eyebrow-dot {
  width: 7px;
  height: 7px;

  border-radius: 50%;

  background: var(--color-primary);

  box-shadow:
    0 0 0 5px rgba(255, 122, 69, 0.1);
}

.post-create-page__title {
  margin: 0;

  font-size: clamp(38px, 4.2vw, 52px);
  font-weight: 850;
  line-height: 1.18;
  letter-spacing: -0.06em;
}

.post-create-page__title strong {
  position: relative;
  z-index: 1;

  color: var(--color-primary);
}

.post-create-page__title strong::after {
  position: absolute;
  right: 0;
  bottom: 2px;
  left: 0;
  z-index: -1;

  height: 8px;

  border-radius: var(--radius-pill);

  background: rgba(255, 122, 69, 0.13);

  content: '';
}

.post-create-page__description {
  max-width: 570px;

  margin: 20px 0 0;

  color: var(--color-text-secondary);

  font-size: 16px;
  line-height: 1.75;
}

.post-create-page__guide {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;

  margin-top: 24px;
}

.post-create-page__guide span {
  padding: 7px 11px;

  border: 1px solid var(--color-border);
  border-radius: var(--radius-pill);

  background: rgba(255, 255, 255, 0.76);
  color: var(--color-text-secondary);

  font-size: 11px;
  font-weight: 700;

  backdrop-filter: blur(8px);
}

.post-create-hero__decoration {
  position: absolute;

  border-radius: 50%;

  background: var(--color-primary);

  opacity: 0.06;
}

.post-create-hero__decoration--top {
  top: 42px;
  right: -54px;

  width: 150px;
  height: 150px;
}

.post-create-hero__decoration--bottom {
  bottom: 28px;
  left: -48px;

  width: 110px;
  height: 110px;
}

/* =================================
   작성 폼
================================= */

.post-create-content {
  padding: 0 0 96px;

  background: var(--color-background);
}

.post-form {
  position: relative;
  z-index: 2;

  width: min(100%, 820px);
  margin: -42px auto 0;
  padding: 40px;

  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);

  background: #ffffff;

  box-shadow:
    0 20px 45px rgba(32, 33, 36, 0.08);
}

.post-form__heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 30px;

  margin-bottom: 34px;
  padding-bottom: 30px;

  border-bottom: 1px solid var(--color-border);
}

.post-form__heading-eyebrow {
  display: block;

  margin-bottom: 8px;

  color: var(--color-primary);

  font-size: 10px;
  font-weight: 850;
  letter-spacing: 0.12em;
}

.post-form__heading h2 {
  margin: 0;

  font-size: 28px;
  font-weight: 850;
  line-height: 1.3;
  letter-spacing: -0.045em;
}

.post-form__heading p {
  margin: 8px 0 0;

  color: var(--color-text-secondary);

  font-size: 12px;
}

.post-form__heading-icon {
  display: grid;
  flex-shrink: 0;
  place-items: center;

  width: 66px;
  height: 66px;

  border: 1px solid rgba(255, 122, 69, 0.16);
  border-radius: 22px;

  background:
    linear-gradient(
      145deg,
      rgba(255, 122, 69, 0.12),
      rgba(255, 184, 77, 0.05)
    );

  font-size: 29px;
}

.post-form__group {
  position: relative;

  padding-bottom: 32px;

  border-bottom: 1px solid var(--color-border);
}

.post-form__group + .post-form__group {
  margin-top: 32px;
}

.post-form__group--last {
  padding-bottom: 0;

  border-bottom: 0;
}

.post-form__label-area {
  display: flex;
  align-items: flex-start;
  gap: 15px;

  margin-bottom: 15px;
}

.post-form__number {
  display: grid;
  flex-shrink: 0;
  place-items: center;

  width: 30px;
  height: 30px;

  border-radius: 10px;

  background: var(--color-primary-light);
  color: var(--color-primary);

  font-size: 10px;
  font-weight: 850;
}

.post-form__label {
  display: block;

  color: var(--color-text-primary);

  font-size: 15px;
  font-weight: 800;
  line-height: 1.4;
}

.post-form__label-description {
  margin: 5px 0 0;

  color: var(--color-text-secondary);

  font-size: 12px;
  line-height: 1.5;
}

.post-form__required {
  margin-left: 3px;

  color: var(--color-error);
}

.post-form__optional {
  margin-left: 7px;

  color: var(--color-text-disabled);

  font-size: 11px;
  font-weight: 600;
}

.post-form__input,
.post-form__textarea {
  width: 100%;

  box-sizing: border-box;

  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);

  background: #ffffff;
  color: var(--color-text-primary);

  font: inherit;

  outline: none;

  transition:
    border-color var(--transition-fast),
    box-shadow var(--transition-fast),
    background-color var(--transition-fast);
}

.post-form__input {
  min-height: 52px;
  padding: 0 16px;
}

.post-form__textarea {
  min-height: 260px;
  padding: 17px 16px;

  line-height: 1.7;

  resize: vertical;
}

.post-form__input::placeholder,
.post-form__textarea::placeholder {
  color: var(--color-text-disabled);
}

.post-form__input:hover:not(:disabled),
.post-form__textarea:hover:not(:disabled) {
  border-color: var(--color-border-strong);
}

.post-form__input:focus,
.post-form__textarea:focus {
  border-color: var(--color-primary);

  box-shadow:
    0 0 0 4px rgba(255, 122, 69, 0.1);
}

.post-form__input:disabled,
.post-form__textarea:disabled {
  cursor: not-allowed;

  background: var(--color-background);

  opacity: 0.65;
}

.post-form__count {
  margin-top: 7px;

  color: var(--color-text-disabled);

  font-size: 11px;
  text-align: right;
}

.post-form__help {
  margin: 9px 0 0;

  color: var(--color-text-secondary);

  font-size: 12px;
  line-height: 1.5;
}

/* =================================
   음식점 검색
================================= */

.restaurant-search {
  position: relative;
}

.restaurant-search__field {
  position: relative;
}

.restaurant-search__icon {
  position: absolute;
  top: 50%;
  left: 17px;
  z-index: 1;

  color: var(--color-text-disabled);

  font-size: 21px;

  pointer-events: none;

  transform: translateY(-54%);
}

.restaurant-search__input {
  padding-right: 16px;
  padding-left: 48px;
}

.restaurant-search__results {
  position: absolute;
  top: calc(100% + 9px);
  right: 0;
  left: 0;
  z-index: 20;

  max-height: 340px;
  overflow-y: auto;

  padding: 8px;

  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);

  background: #ffffff;

  box-shadow:
    0 16px 36px rgba(32, 33, 36, 0.13);

  scrollbar-color: var(--color-border-strong) transparent;
  scrollbar-width: thin;
}

.restaurant-search__results::-webkit-scrollbar {
  width: 5px;
}

.restaurant-search__results::-webkit-scrollbar-thumb {
  border-radius: var(--radius-pill);

  background: var(--color-border-strong);
}

.restaurant-search__result-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;

  padding: 8px 10px 10px;

  color: var(--color-text-disabled);

  font-size: 11px;
  font-weight: 700;
}

.restaurant-search__result-heading strong {
  color: var(--color-primary);
}

.restaurant-search__item {
  display: flex;
  width: 100%;
  align-items: center;
  gap: 12px;

  padding: 13px 12px;

  border: 0;
  border-radius: var(--radius-md);

  background: transparent;

  text-align: left;

  cursor: pointer;

  transition:
    background-color var(--transition-fast),
    transform var(--transition-fast);
}

.restaurant-search__item:hover:not(:disabled) {
  background: var(--color-primary-light);

  transform: translateX(2px);
}

.restaurant-search__item:disabled {
  cursor: not-allowed;

  opacity: 0.65;
}

.restaurant-search__item-icon {
  display: grid;
  flex-shrink: 0;
  place-items: center;

  width: 34px;
  height: 34px;

  border-radius: 11px;

  background: #ffffff;

  font-size: 15px;

  box-shadow:
    0 4px 12px rgba(32, 33, 36, 0.07);
}

.restaurant-search__item-copy {
  display: flex;
  min-width: 0;
  flex: 1;
  flex-direction: column;
  gap: 5px;
}

.restaurant-search__title {
  overflow: hidden;

  color: var(--color-text-primary);

  font-size: 14px;
  font-weight: 750;

  text-overflow: ellipsis;
  white-space: nowrap;
}

.restaurant-search__address {
  overflow: hidden;

  color: var(--color-text-secondary);

  font-size: 11px;
  line-height: 1.4;

  text-overflow: ellipsis;
  white-space: nowrap;
}

.restaurant-search__arrow {
  flex-shrink: 0;

  color: var(--color-text-disabled);

  transition:
    color var(--transition-fast),
    transform var(--transition-fast);
}

.restaurant-search__item:hover
  .restaurant-search__arrow {
  color: var(--color-primary);

  transform: translateX(3px);
}

.restaurant-search__empty {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 7px;

  margin: 0;
  padding: 30px 12px;

  color: var(--color-text-secondary);

  font-size: 13px;
  text-align: center;
}

/* =================================
   선택된 음식점
================================= */

.selected-restaurant {
  display: flex;
  align-items: center;
  gap: 15px;

  padding: 18px;

  border: 1px solid rgba(255, 122, 69, 0.22);
  border-radius: var(--radius-lg);

  background:
    radial-gradient(
      circle at 100% 0%,
      rgba(255, 122, 69, 0.11),
      transparent 35%
    ),
    #fffaf7;
}

.selected-restaurant__icon {
  display: grid;
  flex-shrink: 0;
  place-items: center;

  width: 45px;
  height: 45px;

  border-radius: 15px;

  background: #ffffff;

  font-size: 20px;

  box-shadow:
    0 6px 15px rgba(255, 122, 69, 0.12);
}

.selected-restaurant__information {
  display: flex;
  min-width: 0;
  flex: 1;
  flex-direction: column;
  gap: 5px;
}

.selected-restaurant__badge {
  width: fit-content;

  padding: 4px 8px;

  border-radius: var(--radius-pill);

  background: rgba(255, 122, 69, 0.11);
  color: var(--color-primary);

  font-size: 10px;
  font-weight: 800;
}

.selected-restaurant__title {
  margin-top: 2px;

  overflow: hidden;

  color: var(--color-text-primary);

  font-size: 16px;
  font-weight: 800;

  text-overflow: ellipsis;
  white-space: nowrap;
}

.selected-restaurant__address {
  overflow: hidden;

  color: var(--color-text-secondary);

  font-size: 11px;
  line-height: 1.4;

  text-overflow: ellipsis;
  white-space: nowrap;
}

.selected-restaurant__actions {
  display: flex;
  flex-shrink: 0;
  gap: 7px;
}

.selected-restaurant__button {
  min-height: 35px;
  padding: 0 11px;

  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);

  background: #ffffff;
  color: var(--color-primary);

  font-size: 11px;
  font-weight: 750;

  cursor: pointer;

  transition:
    border-color var(--transition-fast),
    color var(--transition-fast),
    background-color var(--transition-fast);
}

.selected-restaurant__button:hover:not(:disabled) {
  border-color: var(--color-primary);

  background: var(--color-primary-light);
}

.selected-restaurant__button:disabled {
  cursor: not-allowed;

  opacity: 0.65;
}

.selected-restaurant__button--remove {
  color: var(--color-text-secondary);
}

.selected-restaurant__button--remove:hover:not(:disabled) {
  border-color: var(--color-error);

  background: #fff8f8;
  color: var(--color-error);
}

/* =================================
   비밀번호
================================= */

.password-field {
  position: relative;
}

.password-field__input {
  padding-right: 80px;
}

.password-field__toggle {
  position: absolute;
  top: 50%;
  right: 11px;

  min-width: 54px;
  min-height: 32px;

  padding: 0 9px;

  border: 0;
  border-radius: var(--radius-sm);

  background: var(--color-primary-light);
  color: var(--color-primary);

  font-size: 11px;
  font-weight: 750;

  cursor: pointer;

  transform: translateY(-50%);

  transition:
    background-color var(--transition-fast),
    color var(--transition-fast);
}

.password-field__toggle:hover:not(:disabled) {
  background: rgba(255, 122, 69, 0.17);
}

.password-field__toggle:disabled {
  cursor: not-allowed;

  opacity: 0.65;
}

.post-form__notice {
  display: flex;
  align-items: flex-start;
  gap: 9px;

  margin-top: 10px;
  padding: 12px 14px;

  border-radius: var(--radius-md);

  background: var(--color-background);
  color: var(--color-text-secondary);
}

.post-form__notice span {
  flex-shrink: 0;

  font-size: 13px;
}

.post-form__notice p {
  margin: 0;

  font-size: 11px;
  line-height: 1.6;
}

/* =================================
   오류 및 버튼
================================= */

.post-form__error {
  display: flex;
  align-items: flex-start;
  gap: 10px;

  margin-top: 30px;
  padding: 14px 16px;

  border: 1px solid rgba(229, 72, 77, 0.28);
  border-radius: var(--radius-md);

  background: rgba(229, 72, 77, 0.05);
  color: var(--color-error);

  font-size: 13px;
  font-weight: 700;
  line-height: 1.6;
}

.post-form__error span {
  display: grid;
  flex-shrink: 0;
  place-items: center;

  width: 20px;
  height: 20px;

  border-radius: 50%;

  background: var(--color-error);
  color: #ffffff;

  font-size: 11px;
}

.post-form__actions {
  display: flex;
  justify-content: flex-end;
  gap: 11px;

  margin-top: 38px;
  padding-top: 30px;

  border-top: 1px solid var(--color-border);
}

.post-form__cancel,
.post-form__submit {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;

  min-width: 128px;
  min-height: 48px;
  padding: 0 19px;

  border-radius: var(--radius-md);

  font-size: 14px;
  font-weight: 750;

  cursor: pointer;

  transition:
    color var(--transition-fast),
    background-color var(--transition-fast),
    border-color var(--transition-fast),
    box-shadow var(--transition-fast),
    transform var(--transition-fast);
}

.post-form__cancel:hover:not(:disabled),
.post-form__submit:hover:not(:disabled) {
  transform: translateY(-2px);
}

.post-form__cancel {
  border: 1px solid var(--color-border-strong);

  background: #ffffff;
  color: var(--color-text-secondary);
}

.post-form__cancel:hover:not(:disabled) {
  border-color: var(--color-text-secondary);

  color: var(--color-text-primary);
}

.post-form__submit {
  border: 1px solid var(--color-primary);

  background: var(--color-primary);
  color: #ffffff;

  box-shadow:
    0 9px 22px rgba(255, 122, 69, 0.2);
}

.post-form__submit:hover:not(:disabled) {
  background: var(--color-primary-hover);

  box-shadow:
    0 13px 26px rgba(255, 122, 69, 0.26);
}

.post-form__cancel:disabled,
.post-form__submit:disabled {
  cursor: not-allowed;

  opacity: 0.65;

  transform: none;
}

/* =================================
   태블릿
================================= */

@media (max-width: 1023px) {
  .post-create-hero {
    padding-top: 64px;
  }

  .post-form {
    box-sizing: border-box;
  }
}

/* =================================
   모바일
================================= */

@media (max-width: 767px) {
  .post-create-page__inner {
    width: min(100% - 32px, var(--content-width));
  }

  .post-create-hero {
    padding: 52px 0 76px;
  }

  .post-create-page__title {
    font-size: 37px;
  }

  .post-create-page__description {
    margin-top: 17px;

    font-size: 14px;
  }

  .post-create-page__guide {
    margin-top: 20px;
  }

  .post-create-page__guide span {
    padding: 6px 9px;

    font-size: 10px;
  }

  .post-create-content {
    padding-bottom: 64px;
  }

  .post-form {
    margin-top: -31px;
    padding: 27px 21px;

    border-radius: var(--radius-lg);
  }

  .post-form__heading {
    align-items: flex-start;

    margin-bottom: 28px;
    padding-bottom: 25px;
  }

  .post-form__heading h2 {
    font-size: 24px;
  }

  .post-form__heading-icon {
    width: 50px;
    height: 50px;

    border-radius: 17px;

    font-size: 23px;
  }

  .post-form__group {
    padding-bottom: 27px;
  }

  .post-form__group + .post-form__group {
    margin-top: 27px;
  }

  .post-form__group--last {
    padding-bottom: 0;
  }

  .post-form__label-area {
    gap: 11px;
  }

  .post-form__number {
    width: 27px;
    height: 27px;

    border-radius: 9px;
  }

  .post-form__textarea {
    min-height: 230px;
  }

  .selected-restaurant {
    align-items: flex-start;
    flex-wrap: wrap;
  }

  .selected-restaurant__information {
    width: calc(100% - 60px);
  }

  .selected-restaurant__actions {
    width: 100%;
    margin-top: 4px;
  }

  .selected-restaurant__button {
    flex: 1;
  }

  .restaurant-search__results {
    max-height: 290px;
  }

  .post-form__actions {
    flex-direction: column-reverse;

    margin-top: 31px;
    padding-top: 25px;
  }

  .post-form__cancel,
  .post-form__submit {
    width: 100%;

    box-sizing: border-box;
  }
}

/* =================================
   모션 감소
================================= */

@media (prefers-reduced-motion: reduce) {
  .post-form__input,
  .post-form__textarea,
  .restaurant-search__item,
  .restaurant-search__arrow,
  .selected-restaurant__button,
  .password-field__toggle,
  .post-form__cancel,
  .post-form__submit {
    transition: none;
  }
}
</style>