<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goBack = () => {
  if (window.history.length > 1) {
    router.back()
    return
  }

  router.push('/')
}
</script>

<template>
  <main class="not-found-page">
    <section class="not-found">
      <div class="not-found__inner">
        <!-- 왼쪽 안내 영역 -->
        <div class="not-found__content">
          <span class="not-found__eyebrow">
            ERROR / PAGE NOT FOUND
          </span>

          <p class="not-found__number" aria-hidden="true">
            404
          </p>

          <h1 class="not-found__title">
            길을 잃은 것 같아요.
          </h1>

          <p class="not-found__description">
            요청한 페이지가 삭제되었거나<br />
            주소가 변경되었을 수 있어요.
          </p>

          <div class="not-found__actions">
            <RouterLink
              to="/"
              class="not-found__home"
            >
              <span
                class="not-found__home-icon"
                aria-hidden="true"
              >
                <svg viewBox="0 0 24 24">
                  <path d="m3 11 9-8 9 8" />
                  <path d="M5 10v10h14V10" />
                  <path d="M9 20v-6h6v6" />
                </svg>
              </span>

              <strong>홈으로 돌아가기</strong>

              <span
                class="not-found__arrow"
                aria-hidden="true"
              >
                →
              </span>
            </RouterLink>

            <button
              type="button"
              class="not-found__back"
              @click="goBack"
            >
              이전 페이지
            </button>
          </div>
        </div>

        <!-- 오른쪽 지도 장식 -->
        <div
          class="not-found-map"
          aria-hidden="true"
        >
          <div class="not-found-map__top">
            <span>LOST LOCAL MAP</span>

            <span>
              <strong>?</strong>
              / 404
            </span>
          </div>

          <div class="not-found-map__body">
            <svg
              class="not-found-map__terrain"
              viewBox="0 0 420 260"
              preserveAspectRatio="none"
            >
              <path
                class="not-found-map__shape"
                d="
                  M53 38
                  C105 12 157 23 197 43
                  C241 65 299 40 350 68
                  C396 93 398 149 360 184
                  C323 218 274 208 231 225
                  C180 244 132 221 87 226
                  C39 231 13 194 17 144
                  C21 94 16 57 53 38Z
                "
              />

              <path
                class="not-found-map__line"
                d="
                  M32 100
                  C79 82 108 95 142 75
                  C177 53 208 58 240 74
                  C274 92 314 83 388 55
                "
              />

              <path
                class="not-found-map__line not-found-map__line--bottom"
                d="
                  M41 207
                  C89 187 126 201 163 181
                  C207 158 235 171 276 188
                  C316 204 349 187 391 170
                "
              />

              <path
                class="not-found-map__route"
                d="
                  M58 197
                  C94 184 107 145 149 150
                  C192 155 202 104 244 108
                  C286 112 300 74 352 64
                "
              />
            </svg>

            <span class="not-found-map__compass">
              <strong>N</strong>
              <i></i>
            </span>

            <div class="not-found-map__checkpoint not-found-map__checkpoint--one">
              <span class="not-found-map__node">
                1
              </span>

              <span class="not-found-map__checkpoint-copy">
                <strong>주소 확인</strong>
                <small>잘못된 주소인가요?</small>
              </span>
            </div>

            <div class="not-found-map__checkpoint not-found-map__checkpoint--two">
              <span class="not-found-map__node">
                2
              </span>

              <span class="not-found-map__checkpoint-copy">
                <strong>경로 재탐색</strong>
                <small>홈으로 돌아가요</small>
              </span>
            </div>

            <div class="not-found-map__destination">
              <span class="not-found-map__pin">
                <svg viewBox="0 0 24 24">
                  <path
                    d="M12 21s6-5.1 6-11a6 6 0 1 0-12 0c0 5.9 6 11 6 11Z"
                  />
                  <circle cx="12" cy="10" r="2.2" />
                </svg>

                <strong>?</strong>
              </span>

              <span class="not-found-map__destination-copy">
                <strong>페이지 없음</strong>
                <small>목적지를 찾지 못했어요</small>
              </span>
            </div>

            <span class="not-found-map__spark not-found-map__spark--one">
              ✦
            </span>

            <span class="not-found-map__spark not-found-map__spark--two">
              ✦
            </span>
          </div>

          <div class="not-found-map__bottom">
            <span>LOCALHUB NAVIGATION</span>

            <strong>경로를 다시 안내할게요.</strong>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>

<style scoped>
.not-found-page {
  min-height: calc(100vh - var(--header-height));

  background: var(--color-background);
  color: var(--color-text-primary);
}

.not-found {
  min-height: calc(100vh - var(--header-height));

  border-bottom: 1px solid var(--color-border);

  background: #f6f1ed;
}

.not-found__inner {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 430px;
  align-items: center;
  gap: 72px;

  width: min(100% - 48px, var(--content-width));
  min-height: calc(100vh - var(--header-height));
  margin: 0 auto;
  padding: 64px 0;

  box-sizing: border-box;
}

/* =================================
   안내 영역
================================= */

.not-found__content {
  display: flex;
  min-width: 0;
  align-items: flex-start;
  flex-direction: column;
}

.not-found__eyebrow {
  margin-bottom: 13px;

  color: var(--color-primary);

  font-size: 10px;
  font-weight: 850;
  letter-spacing: 0.15em;
}

.not-found__number {
  margin: 0;

  color: var(--color-primary);

  font-size: clamp(86px, 10vw, 138px);
  font-weight: 900;
  line-height: 0.9;
  letter-spacing: -0.08em;

  opacity: 0.17;
}

.not-found__title {
  margin: -12px 0 0;

  color: var(--color-text-primary);

  font-size: clamp(34px, 3.5vw, 48px);
  font-weight: 850;
  line-height: 1.18;
  letter-spacing: -0.055em;
}

.not-found__description {
  margin: 18px 0 0;

  color: var(--color-text-secondary);

  font-size: 15px;
  line-height: 1.75;
}

.not-found__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;

  margin-top: 28px;
}

.not-found__home {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 10px;

  min-width: 220px;
  min-height: 49px;

  padding: 0 14px;

  box-sizing: border-box;

  border-radius: var(--radius-md);

  background: var(--color-primary);
  color: #ffffff;

  font-size: 12px;
  font-weight: 750;
  text-decoration: none;

  box-shadow:
    0 10px 21px rgba(255, 122, 69, 0.2);

  transition:
    background-color var(--transition-fast),
    box-shadow var(--transition-fast),
    transform var(--transition-fast);
}

.not-found__home:hover {
  background: var(--color-primary-hover);

  box-shadow:
    0 14px 25px rgba(255, 122, 69, 0.28);

  transform: translateY(-2px);
}

.not-found__home-icon {
  display: grid;
  place-items: center;

  width: 28px;
  height: 28px;

  border-radius: 8px;

  background: rgba(255, 255, 255, 0.17);
}

.not-found__home-icon svg {
  width: 16px;
  height: 16px;

  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.8;
}

.not-found__arrow {
  font-size: 15px;

  transition: transform var(--transition-fast);
}

.not-found__home:hover .not-found__arrow {
  transform: translateX(4px);
}

.not-found__back {
  min-height: 49px;

  padding: 0 20px;

  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-md);

  background: rgba(255, 255, 255, 0.65);
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

.not-found__back:hover {
  border-color: var(--color-primary);

  background: #ffffff;
  color: var(--color-primary);

  transform: translateY(-2px);
}

/* =================================
   지도 장식
================================= */

.not-found-map {
  width: 430px;
  justify-self: end;

  overflow: hidden;

  border: 1px solid rgba(255, 122, 69, 0.15);
  border-radius: var(--radius-lg);

  background: rgba(255, 255, 255, 0.67);

  box-shadow:
    0 20px 45px rgba(93, 54, 34, 0.11);

  transition:
    box-shadow var(--transition-base),
    transform var(--transition-base);
}

.not-found-map:hover {
  box-shadow:
    0 25px 51px rgba(93, 54, 34, 0.15);

  transform: translateY(-5px);
}

.not-found-map__top,
.not-found-map__bottom {
  display: flex;
  min-height: 42px;
  align-items: center;
  justify-content: space-between;
  gap: 16px;

  padding: 0 16px;

  box-sizing: border-box;
}

.not-found-map__top {
  border-bottom: 1px solid var(--color-border);
}

.not-found-map__top span {
  color: var(--color-text-disabled);

  font-size: 8px;
  font-weight: 800;
  letter-spacing: 0.11em;
}

.not-found-map__top span:first-child,
.not-found-map__top strong {
  color: var(--color-primary);
}

.not-found-map__body {
  position: relative;

  height: 260px;

  overflow: hidden;
}

.not-found-map__terrain {
  position: absolute;
  inset: 0;

  width: 100%;
  height: 100%;
}

.not-found-map__shape {
  fill: rgba(255, 255, 255, 0.6);
  stroke: rgba(255, 122, 69, 0.16);
  stroke-width: 1.4;
}

.not-found-map__line {
  fill: none;
  stroke: rgba(169, 157, 151, 0.22);
  stroke-width: 1.2;
}

.not-found-map__line--bottom {
  stroke: rgba(255, 122, 69, 0.11);
}

.not-found-map__route {
  fill: none;

  stroke: var(--color-primary);
  stroke-width: 3;
  stroke-linecap: round;
  stroke-dasharray: 8 10;

  opacity: 0.45;

  animation: not-found-route 7s linear infinite;
}

.not-found-map__compass {
  position: absolute;
  top: 31px;
  left: 40px;
  z-index: 3;

  display: grid;
  place-items: center;

  width: 34px;
  height: 34px;

  border: 1px solid rgba(255, 122, 69, 0.2);
  border-radius: 50%;

  background: rgba(255, 255, 255, 0.76);
  color: var(--color-primary);

  font-size: 8px;
  font-style: normal;
  font-weight: 850;

  animation: not-found-compass 8s ease-in-out infinite;
}

.not-found-map__compass i {
  position: absolute;
  top: 5px;

  width: 0;
  height: 0;

  border-right: 3px solid transparent;
  border-bottom: 8px solid var(--color-primary);
  border-left: 3px solid transparent;
}

.not-found-map__checkpoint {
  position: absolute;
  z-index: 4;

  display: flex;
  align-items: center;
  gap: 8px;
}

.not-found-map__checkpoint--one {
  bottom: 35px;
  left: 28px;
}

.not-found-map__checkpoint--two {
  top: 106px;
  left: 146px;
}

.not-found-map__node {
  display: grid;
  place-items: center;

  width: 31px;
  height: 31px;

  flex-shrink: 0;

  border: 2px solid var(--color-primary-200);
  border-radius: 50%;

  background: #ffffff;
  color: var(--color-primary);

  font-size: 10px;
  font-weight: 850;

  box-shadow:
    0 0 0 5px rgba(255, 122, 69, 0.06);

  transition:
    background-color var(--transition-fast),
    border-color var(--transition-fast),
    color var(--transition-fast),
    transform var(--transition-fast);
}

.not-found-map__checkpoint:hover .not-found-map__node {
  border-color: var(--color-primary);

  background: var(--color-primary);
  color: #ffffff;

  transform: scale(1.12);
}

.not-found-map__checkpoint-copy {
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

.not-found-map__checkpoint:hover
  .not-found-map__checkpoint-copy {
  transform: translateY(-3px);
}

.not-found-map__checkpoint-copy strong {
  color: var(--color-text-primary);

  font-size: 10px;
  line-height: 1.35;
}

.not-found-map__checkpoint-copy small {
  margin-top: 1px;

  color: var(--color-text-disabled);

  font-size: 8px;
}

.not-found-map__destination {
  position: absolute;
  top: 29px;
  right: 26px;
  z-index: 5;

  display: flex;
  align-items: center;
  flex-direction: column;
}

.not-found-map__pin {
  position: relative;

  display: grid;
  place-items: center;

  width: 62px;
  height: 62px;

  border-radius: 22px;

  background: var(--color-primary);
  color: #ffffff;

  box-shadow:
    0 16px 30px rgba(255, 122, 69, 0.26);

  animation: not-found-pin 3.3s ease-in-out infinite;
}

.not-found-map__pin svg {
  width: 31px;
  height: 31px;

  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.8;
}

.not-found-map__pin > strong {
  position: absolute;
  top: 18px;

  font-size: 11px;
}

.not-found-map__destination-copy {
  display: flex;
  align-items: center;
  flex-direction: column;

  margin-top: 9px;
  padding: 7px 10px;

  border: 1px solid var(--color-border);
  border-radius: 10px;

  background: rgba(255, 255, 255, 0.92);

  box-shadow:
    0 7px 17px rgba(93, 54, 34, 0.06);

  backdrop-filter: blur(8px);
}

.not-found-map__destination-copy strong {
  color: var(--color-primary-active);

  font-size: 10px;
}

.not-found-map__destination-copy small {
  margin-top: 2px;

  color: var(--color-text-disabled);

  font-size: 8px;
}

.not-found-map__spark {
  position: absolute;
  z-index: 3;

  color: var(--color-primary);

  font-size: 12px;

  animation: not-found-spark 2.4s ease-in-out infinite;
}

.not-found-map__spark--one {
  top: 41px;
  left: 116px;
}

.not-found-map__spark--two {
  right: 127px;
  bottom: 49px;

  animation-delay: -1.2s;
}

.not-found-map__bottom {
  border-top: 1px solid var(--color-border);
}

.not-found-map__bottom span {
  color: var(--color-primary);

  font-size: 8px;
  font-weight: 850;
  letter-spacing: 0.1em;
}

.not-found-map__bottom strong {
  color: var(--color-text-secondary);

  font-size: 11px;
}

/* =================================
   애니메이션
================================= */

@keyframes not-found-route {
  to {
    stroke-dashoffset: -72;
  }
}

@keyframes not-found-pin {
  0%,
  100% {
    transform: translateY(0) rotate(-3deg);
  }

  50% {
    transform: translateY(-8px) rotate(3deg);
  }
}

@keyframes not-found-compass {
  0%,
  100% {
    transform: rotate(-6deg);
  }

  50% {
    transform: rotate(10deg);
  }
}

@keyframes not-found-spark {
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
  .not-found__inner {
    grid-template-columns: minmax(0, 1fr) 360px;
    gap: 40px;
  }

  .not-found-map {
    width: 360px;
  }

  .not-found-map__checkpoint--two {
    left: 115px;
  }
}

/* =================================
   모바일
================================= */

@media (max-width: 767px) {
  .not-found__inner {
    grid-template-columns: 1fr;
    gap: 38px;

    width: min(100% - 32px, var(--content-width));
    padding: 48px 0;
  }

  .not-found__content {
    align-items: center;

    text-align: center;
  }

  .not-found__number {
    font-size: 96px;
  }

  .not-found__title {
    margin-top: -8px;

    font-size: 34px;
  }

  .not-found__description {
    font-size: 14px;
  }

  .not-found__actions {
    width: 100%;
    justify-content: center;
  }

  .not-found-map {
    width: min(100%, 430px);
    justify-self: center;
  }
}

/* =================================
   작은 모바일
================================= */

@media (max-width: 420px) {
  .not-found__title {
    font-size: 30px;
  }

  .not-found__actions {
    flex-direction: column;
  }

  .not-found__home,
  .not-found__back {
    width: 100%;
  }

  .not-found-map__body {
    height: 240px;
  }

  .not-found-map__checkpoint-copy {
    display: none;
  }

  .not-found-map__checkpoint--one {
    bottom: 44px;
    left: 35px;
  }

  .not-found-map__checkpoint--two {
    top: 112px;
    left: 46%;
  }

  .not-found-map__destination {
    right: 15px;
  }

  .not-found-map__bottom span {
    display: none;
  }

  .not-found-map__bottom {
    justify-content: flex-end;
  }
}

/* =================================
   모션 감소
================================= */

@media (prefers-reduced-motion: reduce) {
  .not-found-map__route,
  .not-found-map__pin,
  .not-found-map__compass,
  .not-found-map__spark {
    animation: none;
  }

  .not-found__home,
  .not-found__arrow,
  .not-found__back,
  .not-found-map,
  .not-found-map__node,
  .not-found-map__checkpoint-copy {
    transition: none;
  }
}
</style>