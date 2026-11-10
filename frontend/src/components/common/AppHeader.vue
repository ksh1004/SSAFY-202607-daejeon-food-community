<script setup>
import { ref } from 'vue'

const isMenuOpen = ref(false)

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
}

const closeMenu = () => {
  isMenuOpen.value = false
}
</script>

<template>
  <header class="app-header">
    <div class="app-header__inner">
      <RouterLink to="/" class="app-header__logo" @click="closeMenu">
        <svg
          class="app-header__logo-icon"
          viewBox="0 0 32 32"
          fill="none"
          aria-hidden="true"
        >
          <ellipse
            cx="10"
            cy="8"
            rx="4"
            ry="5.5"
            stroke="currentColor"
            stroke-width="2.4"
          />

          <path
            d="M10 13.5V26"
            stroke="currentColor"
            stroke-width="2.4"
            stroke-linecap="round"
          />

          <path
            d="M20 5.5L18.5 26"
            stroke="currentColor"
            stroke-width="2.4"
            stroke-linecap="round"
          />

          <path
            d="M25 5.5L23.5 26"
            stroke="currentColor"
            stroke-width="2.4"
            stroke-linecap="round"
          />
        </svg>

        <span>잇슈</span>
      </RouterLink>

      <button
        type="button"
        class="app-header__menu-button"
        :class="{ 'app-header__menu-button--open': isMenuOpen }"
        aria-label="메뉴 열기"
        :aria-expanded="isMenuOpen"
        @click="toggleMenu"
      >
        <span></span>
        <span></span>
        <span></span>
      </button>

      <nav
        class="app-header__nav"
        :class="{ 'app-header__nav--open': isMenuOpen }"
        aria-label="주요 메뉴"
      >
        <RouterLink to="/map" @click="closeMenu">
          지도 탐색
        </RouterLink>

        <RouterLink to="/posts" @click="closeMenu">
          커뮤니티
        </RouterLink>

        <RouterLink to="/about" @click="closeMenu">
          서비스 소개
        </RouterLink>
      </nav>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: 1000;

  border-bottom: 1px solid var(--color-border);
  background: rgba(255, 255, 255, 0.96);

  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.app-header__inner {
  position: relative;

  display: flex;
  align-items: center;

  min-height: 68px;
  max-width: var(--container-max-width, 1200px);

  margin: 0 auto;
  padding: 0 24px;
}

/* 로고 */

.app-header__logo {
  display: inline-flex;
  align-items: center;
  gap: 8px;

  color: var(--color-primary, #f97316);

  font-size: 23px;
  font-weight: 800;
  letter-spacing: -0.05em;
  text-decoration: none;
}

.app-header__logo-icon {
  width: 29px;
  height: 29px;

  color: var(--color-primary, #f97316);
}

/* 메뉴 */

.app-header__nav {
  display: flex;
  align-items: center;
  gap: 32px;

  margin-left: auto;
}

.app-header__nav a {
  position: relative;

  display: flex;
  align-items: center;

  min-height: 68px;

  color: var(--color-text-secondary, #4b3a30);

  font-size: 15px;
  font-weight: 600;
  letter-spacing: -0.02em;
  text-decoration: none;

  transition: color 160ms ease;
}

.app-header__nav a:hover {
  color: var(--color-primary, #f97316);
}

.app-header__nav a.router-link-active {
  color: var(--color-primary, #f97316);
  font-weight: 700;
}

.app-header__nav a.router-link-active::after {
  position: absolute;
  right: 0;
  bottom: 0;
  left: 0;

  height: 3px;

  border-radius: 3px 3px 0 0;
  background: var(--color-primary, #f97316);

  content: '';
}

/* 모바일 버튼 */

.app-header__menu-button {
  display: none;
  flex-direction: column;
  justify-content: center;
  gap: 5px;

  width: 40px;
  height: 40px;

  margin-left: auto;
  padding: 8px;

  border: 0;
  background: transparent;

  cursor: pointer;
}

.app-header__menu-button span {
  display: block;

  width: 22px;
  height: 2px;

  border-radius: 2px;
  background: var(--color-text-primary, #1f1712);

  transition:
    transform 180ms ease,
    opacity 180ms ease;
}

.app-header__menu-button--open span:nth-child(1) {
  transform: translateY(7px) rotate(45deg);
}

.app-header__menu-button--open span:nth-child(2) {
  opacity: 0;
}

.app-header__menu-button--open span:nth-child(3) {
  transform: translateY(-7px) rotate(-45deg);
}

@media (max-width: 767px) {
  .app-header__inner {
    min-height: 60px;
    padding: 0 16px;
  }

  .app-header__logo {
    font-size: 21px;
  }

  .app-header__logo-icon {
    width: 26px;
    height: 26px;
  }

  .app-header__menu-button {
    display: flex;
  }

  .app-header__nav {
    position: absolute;
    top: calc(100% + 8px);
    right: 16px;
    left: 16px;

    display: none;
    flex-direction: column;
    align-items: stretch;
    gap: 0;

    margin: 0;
    padding: 6px;

    border: 1px solid var(--color-border);
    border-radius: var(--radius-md, 12px);

    background: #ffffff;

    box-shadow:
      0 12px 30px rgba(31, 23, 18, 0.1);
  }

  .app-header__nav--open {
    display: flex;
  }

  .app-header__nav a {
    min-height: 48px;
    padding: 0 14px;

    border-radius: 8px;
  }

  .app-header__nav a:hover,
  .app-header__nav a.router-link-active {
    background: var(--color-primary-50, #fff7ed);
  }

  .app-header__nav a.router-link-active::after {
    top: 50%;
    right: 14px;
    bottom: auto;
    left: auto;

    width: 5px;
    height: 5px;

    border-radius: 50%;

    transform: translateY(-50%);
  }
}
</style>