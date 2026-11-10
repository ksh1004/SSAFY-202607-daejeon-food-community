<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import TodayPickCard from '@/components/restaurant/TodayPickCard.vue'

const tasteSlider = ref(null)
const getRegionMapRoute = (keyword) => ({
  name: 'restaurant-explore',
  query: {
    keyword,
  },
})

let slideTimer = null
let currentSlideIndex = 0


const moveToNextTaste = () => {
  const slider = tasteSlider.value

  if (!slider) {
    return
  }

  const cards = slider.querySelectorAll('.taste-card')

  if (cards.length === 0) {
    return
  }

  currentSlideIndex = (currentSlideIndex + 1) % cards.length

  const nextCard = cards[currentSlideIndex]

  slider.scrollTo({
    left: nextCard.offsetLeft - slider.offsetLeft,
    behavior: 'smooth',
  })
}

const stopAutoSlide = () => {
  if (!slideTimer) {
    return
  }

  window.clearInterval(slideTimer)
  slideTimer = null
}

const startAutoSlide = () => {
  stopAutoSlide()

  slideTimer = window.setInterval(moveToNextTaste, 2500)
}

onMounted(() => {
  startAutoSlide()
})

onBeforeUnmount(() => {
  stopAutoSlide()
})
</script>

<template>
  <main class="home">
    <!-- Hero -->
    <section class="hero">
      <div class="hero__decoration hero__decoration--top"></div>
      <div class="hero__decoration hero__decoration--bottom"></div>

      <div class="hero__inner">
        <div class="hero__content">
          <span class="hero__eyebrow">
            <span class="hero__eyebrow-dot"></span>
            우리 동네 맛집 이야기의 시작
          </span>

          <h1 class="hero__title">
            가까운 맛집부터<br />
            새로운 <strong>잇슈</strong>까지
          </h1>

          <p class="hero__description">
            지도에서 숨은 맛집을 발견하고,<br />
            그곳을 다녀온 사람들의 솔직한 이야기를 만나보세요.
          </p>

          <div class="hero__actions">
            <RouterLink to="/map" class="button button--primary">
              지도에서 맛집 찾기
              <span aria-hidden="true">→</span>
            </RouterLink>

            <RouterLink to="/posts" class="button button--secondary">
              커뮤니티 둘러보기
            </RouterLink>
          </div>

          <div class="hero__keywords" aria-label="주요 서비스">
            <span>#대전맛집</span>
            <span>#대전근교맛집</span>
            <span>#숨은맛집</span>
            <span>#동네이야기</span>
          </div>
        </div>

        <div class="hero__visual" aria-hidden="true">
          <div class="hero__visual-main">
            <div class="hero__plate">
              <span class="hero__plate-icon">🍜</span>
            </div>

            <span class="hero__food hero__food--bread">🥐</span>
            <span class="hero__food hero__food--rice">🍚</span>
            <span class="hero__food hero__food--strawberry">🍓</span>

            <div class="hero__bubble hero__bubble--top">
              <span>📍</span>
              대전의 새로운 맛집
            </div>

            <div class="hero__bubble hero__bubble--bottom">
              <span>💬</span>
              오늘 올라온 지역 이야기
            </div>
          </div>
        </div>
      </div>

      <TodayPickCard class="home__today-pick" />
    </section>

    <!-- 대전의 맛 3선 -->
    <section class="taste-section section">
      <div class="section__inner">
        <div class="section-heading">
          <div>
            <span class="section-heading__eyebrow">
              TASTE OF DAEJEON
            </span>

            <h2>대전의 맛 3선</h2>

            <p>
              대전의 식문화와 이야기를 담은 대표 음식을 만나보세요.
            </p>
          </div>

          <RouterLink to="/map" class="section-heading__link">
            지도에서 모두 보기
            <span aria-hidden="true">→</span>
          </RouterLink>
        </div>

        <div
          ref="tasteSlider"
          class="taste-slider"
          aria-label="대전의 맛 3선"
          @mouseenter="stopAutoSlide"
          @mouseleave="startAutoSlide"
          @focusin="stopAutoSlide"
          @focusout="startAutoSlide"
        >
          <!-- 대전빵 -->
          <article class="taste-card">
            <div
              class="taste-card__image taste-card__image--bread"
              role="img"
              aria-label="대전의 다양한 빵"
            >
              <span class="taste-card__number">01</span>
            </div>

            <div class="taste-card__content">
              <span class="taste-card__category">
                대전의 달콤한 자부심
              </span>

              <h3>대전빵</h3>

              <p>
                전국적인 인기를 얻은 대전의 대표 빵집부터 지역 곳곳의
                개성 있는 베이커리까지, 대전에서만 만날 수 있는 다채로운
                빵 문화를 소개합니다.
              </p>

              <RouterLink to="/map" class="taste-card__link">
                빵집 찾아보기
                <span aria-hidden="true">→</span>
              </RouterLink>
            </div>
          </article>

          <!-- 칼국수 -->
          <article class="taste-card">
            <div
              class="taste-card__image taste-card__image--noodle"
              role="img"
              aria-label="대전 칼국수"
            >
              <span class="taste-card__number">02</span>
            </div>

            <div class="taste-card__content">
              <span class="taste-card__category">
                오랜 밀가루 문화의 맛
              </span>

              <h3>칼국수</h3>

              <p>
                쫄깃한 면과 따뜻한 국물이 어우러진 대전의 대표 소울
                푸드입니다. 담백한 멸치 육수부터 얼큰한 국물까지 다양한
                칼국수를 만나보세요.
              </p>

              <RouterLink to="/map" class="taste-card__link">
                칼국수 맛집 찾기
                <span aria-hidden="true">→</span>
              </RouterLink>
            </div>
          </article>

          <!-- 두부두루치기 -->
          <article class="taste-card">
            <div
              class="taste-card__image taste-card__image--tofu"
              role="img"
              aria-label="대전 두부두루치기"
            >
              <span class="taste-card__number">03</span>
            </div>

            <div class="taste-card__content">
              <span class="taste-card__category">
                대전에서 시작된 매콤한 맛
              </span>

              <h3>두부두루치기</h3>

              <p>
                매콤하고 감칠맛 나는 양념에 부드러운 두부를 더한 대전의
                향토 음식입니다. 남은 양념에 우동사리를 비벼 먹는 즐거움도
                놓치지 마세요.
              </p>

              <RouterLink to="/map" class="taste-card__link">
                두부두루치기 찾기
                <span aria-hidden="true">→</span>
              </RouterLink>
            </div>
          </article>
        </div>

        <p class="taste-section__guide">
          좌우로 밀어 다른 음식을 확인해 보세요.
        </p>
      </div>
    </section>

    <!-- 대전 지역별 맛집 -->
    <section class="food-route section">
      <div class="section__inner">
        <div class="food-route__heading">
          <span class="section-heading__eyebrow">
            DAEJEON FOOD ROUTE
          </span>

          <h2>오늘은 어느 동네에서 먹을까요?</h2>

          <p>
            지역을 선택하고 대전 곳곳의 맛있는 이야기를 만나보세요.
          </p>
        </div>

        <div class="food-route__content">
          <!-- 선택 상태 -->
          <input
            id="route-dong"
            class="food-route__radio"
            type="radio"
            name="daejeon-route"
            checked
          />

          <input
            id="route-jung"
            class="food-route__radio"
            type="radio"
            name="daejeon-route"
          />

          <input
            id="route-seo"
            class="food-route__radio"
            type="radio"
            name="daejeon-route"
          />

          <input
            id="route-yuseong"
            class="food-route__radio"
            type="radio"
            name="daejeon-route"
          />

          <input
            id="route-daedeok"
            class="food-route__radio"
            type="radio"
            name="daejeon-route"
          />

          <!-- 맛집 노선 -->
          <div class="food-route__line">
            <label
              for="route-dong"
              class="food-route__station station--dong"
            >
              <span class="food-route__number">01</span>
              <span class="food-route__dot"></span>

              <span class="food-route__station-copy">
                <strong>동구</strong>
                <small>대전역 · 소제동</small>
              </span>
            </label>

            <label
              for="route-jung"
              class="food-route__station station--jung"
            >
              <span class="food-route__number">02</span>
              <span class="food-route__dot"></span>

              <span class="food-route__station-copy">
                <strong>중구</strong>
                <small>은행동 · 대흥동</small>
              </span>
            </label>

            <label
              for="route-seo"
              class="food-route__station station--seo"
            >
              <span class="food-route__number">03</span>
              <span class="food-route__dot"></span>

              <span class="food-route__station-copy">
                <strong>서구</strong>
                <small>둔산동 · 갈마동</small>
              </span>
            </label>

            <label
              for="route-yuseong"
              class="food-route__station station--yuseong"
            >
              <span class="food-route__number">04</span>
              <span class="food-route__dot"></span>

              <span class="food-route__station-copy">
                <strong>유성구</strong>
                <small>봉명동 · 궁동</small>
              </span>
            </label>

            <label
              for="route-daedeok"
              class="food-route__station station--daedeok"
            >
              <span class="food-route__number">05</span>
              <span class="food-route__dot"></span>

              <span class="food-route__station-copy">
                <strong>대덕구</strong>
                <small>송촌동 · 오정동</small>
              </span>
            </label>
          </div>

          <!-- 선택된 지역 설명 -->
          <div class="food-route__panels">
            <!-- 동구 -->
            <article class="food-route__panel panel--dong">
              <div>
                <span class="food-route__panel-number">01</span>

                <h3>
                  동구에서 발견하는<br />
                  오래된 맛과 새로운 공간
                </h3>

                <p>
                  대전역 주변의 노포부터 소제동의 감각적인 공간까지,
                  익숙함과 새로움이 공존하는 동구의 맛집을 만나보세요.
                </p>
              </div>

              <RouterLink
                :to="getRegionMapRoute('동구')"
                class="food-route__link"
              >
                동구 맛집 둘러보기
                <span aria-hidden="true">→</span>
              </RouterLink>
            </article>

            <!-- 중구 -->
            <article class="food-route__panel panel--jung">
              <div>
                <span class="food-route__panel-number">02</span>

                <h3>
                  대전의 오랜 중심에서<br />
                  만나는 로컬 맛집
                </h3>

                <p>
                  은행동과 대흥동의 오래된 음식점부터 새로운 골목 맛집까지,
                  중구의 다채로운 이야기를 확인해 보세요.
                </p>
              </div>

              <RouterLink
                :to="getRegionMapRoute('중구')"
                class="food-route__link"
              >
                중구 맛집 둘러보기
                <span aria-hidden="true">→</span>
              </RouterLink>
            </article>

            <!-- 서구 -->
            <article class="food-route__panel panel--seo">
              <div>
                <span class="food-route__panel-number">03</span>

                <h3>
                  도심 한가운데에서 찾는<br />
                  오늘의 한 끼
                </h3>

                <p>
                  둔산동의 인기 음식점부터 갈마동의 숨은 가게까지,
                  선택지가 풍부한 서구의 맛집을 발견해 보세요.
                </p>
              </div>

              <RouterLink
                :to="getRegionMapRoute('서구')"
                class="food-route__link"
              >
                서구 맛집 둘러보기
                <span aria-hidden="true">→</span>
              </RouterLink>
            </article>

            <!-- 유성구 -->
            <article class="food-route__panel panel--yuseong">
              <div>
                <span class="food-route__panel-number">04</span>

                <h3>
                  낮부터 밤까지 이어지는<br />
                  유성의 맛
                </h3>

                <p>
                  봉명동의 저녁 맛집과 궁동의 가볍고 활기찬 음식점까지,
                  다양한 분위기의 유성구를 둘러보세요.
                </p>
              </div>

              <RouterLink
                :to="getRegionMapRoute('유성구')"
                class="food-route__link"
              >
                유성구 맛집 둘러보기
                <span aria-hidden="true">→</span>
              </RouterLink>
            </article>

            <!-- 대덕구 -->
            <article class="food-route__panel panel--daedeok">
              <div>
                <span class="food-route__panel-number">05</span>

                <h3>
                  동네 사람들이 알고 있는<br />
                  든든한 맛집
                </h3>

                <p>
                  송촌동과 오정동을 중심으로 오래 사랑받아 온 음식점과
                  편안하게 방문하기 좋은 맛집을 만나보세요.
                </p>
              </div>

              <RouterLink
                :to="getRegionMapRoute('대덕구')"
                class="food-route__link"
              >
                대덕구 맛집 둘러보기
                <span aria-hidden="true">→</span>
              </RouterLink>
            </article>
          </div>
        </div>

        <!-- 대전 근교 -->
        <div class="nearby-route">
          <div class="nearby-route__heading">
            <div>
              <span>NEAR DAEJEON</span>
              <h3>조금 더 멀리, 새로운 한 끼</h3>
            </div>

            <p>
              대전에서 가볍게 떠나 만날 수 있는 가까운 도시예요.
            </p>
          </div>

          <div class="nearby-route__cards">
            <!-- 공주 -->
            <RouterLink
              :to="getRegionMapRoute('공주시')"
              class="nearby-card"
            >
              <span class="nearby-card__meta">
                <strong>01</strong>
                GONGJU
              </span>

              <h4>
                오래된 도시에서<br />
                만나는 새로운 맛
              </h4>

              <p>
                익숙한 역사와 골목 사이에서 공주만의 로컬 맛집을
                발견해 보세요.
              </p>

              <span class="nearby-card__cta">
                공주 맛집 둘러보기
                <span aria-hidden="true">→</span>
              </span>
            </RouterLink>

            <!-- 논산 -->
            <RouterLink
              :to="getRegionMapRoute('논산시')"
              class="nearby-card"
            >   
              <span class="nearby-card__meta">
                <strong>02</strong>
                NONSAN
              </span>

              <h4>
                드라이브 끝에서<br />
                발견하는 달콤한 맛
              </h4>

              <p>
                가볍게 떠나는 드라이브와 함께 논산의 다채로운 맛을
                만나보세요.
              </p>

              <span class="nearby-card__cta">
                논산 맛집 둘러보기
                <span aria-hidden="true">→</span>
              </span>
            </RouterLink>

            <!-- 계룡 -->
            <RouterLink
              :to="getRegionMapRoute('계룡시')"
              class="nearby-card"
            >
              <span class="nearby-card__meta">
                <strong>03</strong>
                GYERYONG
              </span>

              <h4>
                가까운 산자락에서<br />
                찾는 든든한 한 끼
              </h4>

              <p>
                대전 가까이에서 여유롭게 즐길 수 있는 계룡의 맛집을
                찾아보세요.
              </p>

              <span class="nearby-card__cta">
                계룡 맛집 둘러보기
                <span aria-hidden="true">→</span>
              </span>
            </RouterLink>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="home-cta">
      <div class="home-cta__inner">
        <div>
          <span class="home-cta__eyebrow">오늘 뭐 먹슈?</span>

          <h2>오늘의 맛있는 이슈를 찾아볼까요?</h2>

          <p>
            지도에서 가까운 맛집을 찾고,
            지역 주민들의 이야기도 확인해 보세요.
          </p>
        </div>

        <RouterLink to="/map" class="button button--primary">
          지도 탐색 시작하기
          <span aria-hidden="true">→</span>
        </RouterLink>
      </div>
    </section>
  </main>
</template>

<style scoped>
.home {
  overflow: hidden;

  background: #ffffff;
  color: var(--color-text-primary);
}

/* =================================
   공통
================================= */

.section {
  padding: 80px 0;
}

.section__inner,
.hero__inner,
.home-cta__inner {
  width: min(100% - 48px, var(--content-width));
  margin: 0 auto;
}

.section-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 32px;

  margin-bottom: 32px;
}

.section-heading__eyebrow {
  display: block;

  margin-bottom: 9px;

  color: var(--color-primary);

  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.12em;
}

.section-heading p {
  margin: 10px 0 0;

  color: var(--color-text-secondary);

  font-size: 15px;
}

.section-heading__link {
  display: inline-flex;
  flex-shrink: 0;
  align-items: center;
  gap: 8px;

  color: var(--color-text-secondary);

  font-size: 14px;
  font-weight: 700;
  text-decoration: none;

  transition:
    color var(--transition-fast),
    transform var(--transition-fast);
}

.section-heading__link:hover {
  color: var(--color-primary);

  transform: translateX(3px);
}

/* =================================
   버튼
================================= */

.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 11px;

  min-height: 48px;
  padding: 0 20px;

  border: 1px solid transparent;
  border-radius: var(--radius-md);

  font-size: 14px;
  font-weight: 750;
  text-decoration: none;

  transition:
    color var(--transition-fast),
    background-color var(--transition-fast),
    border-color var(--transition-fast),
    box-shadow var(--transition-fast),
    transform var(--transition-fast);
}

.button:hover {
  transform: translateY(-2px);
}

.button--primary {
  background: var(--color-primary);
  color: #ffffff;

  box-shadow:
    0 9px 22px rgba(255, 122, 69, 0.2);
}

.button--primary:hover {
  background: var(--color-primary-hover);

  box-shadow:
    0 13px 26px rgba(255, 122, 69, 0.26);
}

.button--secondary {
  border-color: var(--color-border-strong);

  background: #ffffff;
  color: var(--color-text-primary);
}

.button--secondary:hover {
  border-color: var(--color-primary);

  color: var(--color-primary);
}

/* =================================
   Hero
================================= */

.hero {
  position: relative;

  display: flex;
  min-height: 590px;
  flex-direction: column;
  align-items: stretch;
  justify-content: center;

  border-bottom: 1px solid var(--color-border);

  background:
    radial-gradient(
      circle at 85% 25%,
      rgba(255, 122, 69, 0.09),
      transparent 25%
    ),
    #ffffff;
}

.hero__inner {
  position: relative;
  z-index: 1;

  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(360px, 0.78fr);
  align-items: center;
  gap: 56px;

  padding: 70px 0;
}

.hero__eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;

  margin-bottom: 20px;

  color: var(--color-text-secondary);

  font-size: 13px;
  font-weight: 700;
}

.hero__eyebrow-dot {
  width: 7px;
  height: 7px;

  border-radius: 50%;

  background: var(--color-primary);

  box-shadow:
    0 0 0 5px rgba(255, 122, 69, 0.1);
}

.hero__title {
  max-width: 620px;

  margin: 0;

  font-size: clamp(42px, 4.5vw, 58px);
  font-weight: 850;
  line-height: 1.15;
  letter-spacing: -0.065em;
}

.hero__title strong {
  position: relative;

  color: var(--color-primary);
}

.hero__title strong::after {
  position: absolute;
  right: 0;
  bottom: 1px;
  left: 0;
  z-index: -1;

  height: 8px;

  border-radius: var(--radius-pill);

  background: rgba(255, 122, 69, 0.13);

  content: '';
}

.hero__description {
  margin: 22px 0 0;

  color: var(--color-text-secondary);

  font-size: 17px;
  line-height: 1.7;
}

.hero__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 11px;

  margin-top: 28px;
}

.hero__keywords {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;

  margin-top: 22px;
}

.hero__keywords span {
  color: var(--color-text-disabled);

  font-size: 12px;
  font-weight: 600;
}

.home__today-pick {
  margin-bottom: 56px;
}

.hero__visual {
  display: flex;
  justify-content: center;
}

.hero__visual-main {
  position: relative;

  width: min(100%, 410px);
  aspect-ratio: 1;

  border: 1px solid rgba(255, 122, 69, 0.13);
  border-radius: 42% 58% 50% 50%;

  background:
    linear-gradient(
      145deg,
      rgba(255, 122, 69, 0.1),
      rgba(255, 184, 77, 0.04)
    );
}

.hero__plate {
  position: absolute;
  top: 50%;
  left: 50%;

  display: grid;
  place-items: center;

  width: 200px;
  height: 200px;

  border: 15px solid #ffffff;
  border-radius: 50%;

  background: #f6f7f8;

  box-shadow: var(--shadow-panel);

  transform: translate(-50%, -50%);
}

.hero__plate-icon {
  font-size: 82px;

  filter:
    drop-shadow(0 10px 10px rgba(32, 33, 36, 0.11));
}

.hero__food {
  position: absolute;

  display: grid;
  place-items: center;

  width: 60px;
  height: 60px;

  border: 1px solid var(--color-border);
  border-radius: 19px;

  background: #ffffff;

  font-size: 30px;

  box-shadow: var(--shadow-card);

  animation: food-float 4s ease-in-out infinite;
}

.hero__food--bread {
  top: 14%;
  right: 14%;
}

.hero__food--rice {
  bottom: 14%;
  left: 12%;

  animation-delay: -1.2s;
}

.hero__food--strawberry {
  right: 8%;
  bottom: 22%;

  animation-delay: -2.3s;
}

.hero__bubble {
  position: absolute;

  display: flex;
  align-items: center;
  gap: 7px;

  padding: 10px 13px;

  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);

  background: rgba(255, 255, 255, 0.94);
  color: var(--color-text-primary);

  font-size: 12px;
  font-weight: 700;

  box-shadow: var(--shadow-card);

  backdrop-filter: blur(10px);
}

.hero__bubble--top {
  top: 15%;
  left: -5%;
}

.hero__bubble--bottom {
  right: -6%;
  bottom: 11%;
}

.hero__decoration {
  position: absolute;

  border-radius: 50%;

  background: var(--color-primary);

  opacity: 0.07;
}

.hero__decoration--top {
  top: 90px;
  right: -65px;

  width: 150px;
  height: 150px;
}

.hero__decoration--bottom {
  bottom: 50px;
  left: -70px;

  width: 120px;
  height: 120px;
}

/* =================================
   대전의 맛 3선
================================= */

.taste-section {
  background: var(--color-background);
}

.taste-slider {
  display: flex;
  gap: 20px;

  overflow-x: auto;

  padding: 4px 2px 22px;

  scroll-behavior: smooth;
  scroll-snap-type: x mandatory;

  scrollbar-color: var(--color-border-strong) transparent;
  scrollbar-width: thin;
}

.taste-slider::-webkit-scrollbar {
  height: 5px;
}

.taste-slider::-webkit-scrollbar-thumb {
  border-radius: var(--radius-pill);

  background: var(--color-border-strong);
}

.taste-card {
  display: grid;
  flex: 0 0 min(820px, 78vw);
  grid-template-columns: 1.08fr 0.92fr;

  min-height: 400px;

  overflow: hidden;

  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);

  background: #ffffff;

  box-shadow: var(--shadow-card);

  scroll-snap-align: start;
}

.taste-card__image {
  position: relative;

  min-height: 370px;

  background-position: center;
  background-size: cover;
}

.taste-card__image--bread {
  background-image:
    linear-gradient(
      180deg,
      transparent 55%,
      rgba(0, 0, 0, 0.22)
    ),
    url('/images/daejeon-bread.png');
}

.taste-card__image--noodle {
  background-image:
    linear-gradient(
      180deg,
      transparent 55%,
      rgba(0, 0, 0, 0.22)
    ),
    url('/images/daejeon-kalguksu.png');
}

.taste-card__image--tofu {
  background-image:
    linear-gradient(
      180deg,
      transparent 55%,
      rgba(0, 0, 0, 0.22)
    ),
    url('/images/daejeon-tofu.png');
}

.taste-card__number {
  position: absolute;
  top: 22px;
  left: 22px;

  color: rgba(255, 255, 255, 0.92);

  font-size: 40px;
  font-weight: 850;
  letter-spacing: -0.06em;

  text-shadow:
    0 4px 14px rgba(0, 0, 0, 0.2);
}

.taste-card__content {
  display: flex;
  flex-direction: column;
  justify-content: center;

  padding: 36px;
}

.taste-card__category {
  margin-bottom: 11px;

  color: var(--color-primary);

  font-size: 12px;
  font-weight: 800;
}

.taste-card__content h3 {
  margin: 0;

  font-size: 34px;
  line-height: 1.25;
  letter-spacing: -0.045em;
}

.taste-card__content p {
  margin: 17px 0 0;

  color: var(--color-text-secondary);

  font-size: 14px;
  line-height: 1.75;
}

.taste-card__link {
  display: inline-flex;
  align-items: center;
  align-self: flex-start;
  gap: 8px;

  margin-top: 25px;

  color: var(--color-text-primary);

  font-size: 13px;
  font-weight: 750;
  text-decoration: none;

  transition:
    color var(--transition-fast),
    gap var(--transition-fast);
}

.taste-card__link:hover {
  gap: 11px;

  color: var(--color-primary);
}

.taste-section__guide {
  display: none;

  margin: 4px 0 0;

  color: var(--color-text-disabled);

  font-size: 12px;
  text-align: center;
}

/* =================================
   대전 맛집 노선
================================= */

.food-route {
  overflow: hidden;

  background: #ffffff;
}

.food-route__heading {
  max-width: 620px;

  margin-bottom: 52px;
}

.section-heading h2,
.food-route__heading h2 {
  margin: 0;

  font-size: clamp(28px, 2.8vw, 36px);
  font-weight: 850;
  line-height: 1.25;
  letter-spacing: -0.045em;
}

.food-route__heading p {
  margin: 13px 0 0;

  color: var(--color-text-secondary);

  font-size: 15px;
}

.food-route__content {
  position: relative;
}

.food-route__radio {
  position: absolute;

  width: 1px;
  min-height: 0;
  height: 1px;

  margin: 0;
  padding: 0;

  overflow: hidden;

  opacity: 0;
  pointer-events: none;
}

/* 노선 */

.food-route__line {
  position: relative;

  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));

  margin-bottom: 42px;
}

.food-route__line::before {
  position: absolute;
  top: 31px;
  right: 10%;
  left: 10%;

  height: 3px;

  border-radius: var(--radius-pill);

  background: var(--color-border-strong);

  content: '';
}

.food-route__station {
  position: relative;
  z-index: 1;

  display: flex;
  flex-direction: column;
  align-items: center;

  cursor: pointer;
}

.food-route__number {
  margin-bottom: 11px;

  color: var(--color-text-disabled);

  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.08em;
}

.food-route__dot {
  position: relative;

  display: block;

  width: 20px;
  height: 20px;

  border: 6px solid #ffffff;
  border-radius: 50%;

  background: var(--color-border-strong);

  box-shadow:
    0 0 0 2px var(--color-border-strong);

  transition:
    width var(--transition-base),
    height var(--transition-base),
    background-color var(--transition-base),
    box-shadow var(--transition-base),
    transform var(--transition-base);
}

.food-route__station-copy {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;

  margin-top: 14px;

  text-align: center;

  transition:
    color var(--transition-base),
    transform var(--transition-base);
}

.food-route__station-copy strong {
  font-size: 16px;
  font-weight: 800;
}

.food-route__station-copy small {
  color: var(--color-text-secondary);

  font-size: 11px;
}

/* 선택된 노선 */

#route-dong:checked
  ~ .food-route__line
  .station--dong
  .food-route__dot,
#route-jung:checked
  ~ .food-route__line
  .station--jung
  .food-route__dot,
#route-seo:checked
  ~ .food-route__line
  .station--seo
  .food-route__dot,
#route-yuseong:checked
  ~ .food-route__line
  .station--yuseong
  .food-route__dot,
#route-daedeok:checked
  ~ .food-route__line
  .station--daedeok
  .food-route__dot {
  width: 34px;
  height: 34px;

  background: var(--color-primary);

  box-shadow:
    0 0 0 2px var(--color-primary),
    0 0 0 8px rgba(255, 122, 69, 0.1),
    0 9px 18px rgba(255, 122, 69, 0.18);

  transform: translateY(-7px);
}

#route-dong:checked
  ~ .food-route__line
  .station--dong
  .food-route__station-copy,
#route-jung:checked
  ~ .food-route__line
  .station--jung
  .food-route__station-copy,
#route-seo:checked
  ~ .food-route__line
  .station--seo
  .food-route__station-copy,
#route-yuseong:checked
  ~ .food-route__line
  .station--yuseong
  .food-route__station-copy,
#route-daedeok:checked
  ~ .food-route__line
  .station--daedeok
  .food-route__station-copy {
  color: var(--color-primary);

  transform: translateY(-4px);
}

/* 선택 설명 패널 */

.food-route__panels {
  min-height: 215px;
}

.food-route__panel {
  display: none;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: flex-end;
  gap: 38px;

  padding: 34px 38px;

  border: 1px solid rgba(255, 122, 69, 0.16);
  border-radius: var(--radius-xl);

  background:
    radial-gradient(
      circle at 92% 15%,
      rgba(255, 122, 69, 0.1),
      transparent 26%
    ),
    #fafafa;

  animation: route-panel-open 260ms ease;
}

#route-dong:checked ~ .food-route__panels .panel--dong,
#route-jung:checked ~ .food-route__panels .panel--jung,
#route-seo:checked ~ .food-route__panels .panel--seo,
#route-yuseong:checked ~ .food-route__panels .panel--yuseong,
#route-daedeok:checked ~ .food-route__panels .panel--daedeok {
  display: grid;
}

.food-route__panel-number {
  display: block;

  margin-bottom: 9px;

  color: var(--color-primary);

  font-size: 11px;
  font-weight: 850;
  letter-spacing: 0.1em;
}

.food-route__panel h3 {
  margin: 0;

  font-size: clamp(24px, 2.7vw, 30px);
  line-height: 1.3;
  letter-spacing: -0.045em;
}

.food-route__panel p {
  max-width: 680px;

  margin: 13px 0 0;

  color: var(--color-text-secondary);

  font-size: 14px;
  line-height: 1.7;
}

.food-route__link {
  display: inline-flex;
  flex-shrink: 0;
  align-items: center;
  gap: 10px;

  min-height: 46px;
  padding: 0 18px;

  border-radius: var(--radius-md);

  background: var(--color-primary);
  color: #ffffff;

  font-size: 13px;
  font-weight: 750;
  text-decoration: none;

  transition:
    background-color var(--transition-fast),
    box-shadow var(--transition-fast),
    transform var(--transition-fast);
}

.food-route__link:hover {
  background: var(--color-primary-hover);

  box-shadow:
    0 9px 20px rgba(255, 122, 69, 0.2);

  transform: translateY(-2px);
}

/* =================================
   대전 근교
================================= */

.nearby-route {
  margin-top: 64px;
  padding-top: 44px;

  border-top: 1px solid var(--color-border);
}

.nearby-route__heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 28px;

  margin-bottom: 22px;
}

.nearby-route__heading span {
  display: block;

  margin-bottom: 6px;

  color: var(--color-primary);

  font-size: 10px;
  font-weight: 850;
  letter-spacing: 0.11em;
}

.nearby-route__heading h3 {
  margin: 0;

  font-size: 23px;
  line-height: 1.3;
  letter-spacing: -0.04em;
}

.nearby-route__heading p {
  margin: 0;

  color: var(--color-text-secondary);

  font-size: 13px;
}

.nearby-route__cards {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.nearby-card {
  position: relative;

  display: flex;
  min-width: 0;
  min-height: 220px;
  flex-direction: column;

  overflow: hidden;

  padding: 26px;

  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);

  background:
    radial-gradient(
      circle at 100% 0%,
      rgba(255, 122, 69, 0.075),
      transparent 34%
    ),
    #ffffff;

  color: var(--color-text-primary);
  text-decoration: none;

  box-shadow: var(--shadow-card);

  transition:
    border-color var(--transition-base),
    box-shadow var(--transition-base),
    transform var(--transition-base);
}

.nearby-card::before {
  position: absolute;
  top: 0;
  left: 26px;

  width: 32px;
  height: 3px;

  border-radius: 0 0 var(--radius-pill) var(--radius-pill);

  background: var(--color-primary);

  content: '';
}

.nearby-card:hover {
  border-color: rgba(255, 122, 69, 0.28);

  box-shadow:
    0 13px 27px rgba(32, 33, 36, 0.08);

  transform: translateY(-5px);
}

.nearby-card__meta {
  display: flex;
  align-items: center;
  gap: 8px;

  color: var(--color-text-disabled);

  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.1em;
}

.nearby-card__meta strong {
  color: var(--color-primary);

  font-size: 11px;
}

.nearby-card h4 {
  margin: 20px 0 0;

  font-size: 22px;
  font-weight: 850;
  line-height: 1.35;
  letter-spacing: -0.045em;
}

.nearby-card p {
  margin: 13px 0 22px;

  color: var(--color-text-secondary);

  font-size: 13px;
  line-height: 1.65;
}

.nearby-card__cta {
  display: inline-flex;
  align-items: center;
  gap: 8px;

  margin-top: auto;

  color: var(--color-text-primary);

  font-size: 13px;
  font-weight: 750;

  transition:
    color var(--transition-fast),
    gap var(--transition-fast);
}

.nearby-card:hover .nearby-card__cta {
  gap: 12px;

  color: var(--color-primary);
}

/* =================================
   하단 CTA
================================= */

.home-cta {
  padding: 0 0 80px;

  background: #ffffff;
}

.home-cta__inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 40px;

  overflow: hidden;

  padding: 42px 46px;

  border: 1px solid rgba(255, 122, 69, 0.16);
  border-radius: var(--radius-xl);

  background:
    radial-gradient(
      circle at 90% 20%,
      rgba(255, 122, 69, 0.12),
      transparent 26%
    ),
    #fafafa;
}

.home-cta__eyebrow {
  display: block;

  margin-bottom: 7px;

  color: var(--color-primary);

  font-size: 12px;
  font-weight: 800;
}

.home-cta h2 {
  margin: 0;

  font-size: 28px;
  line-height: 1.3;
  letter-spacing: -0.04em;
}

.home-cta p {
  margin: 9px 0 0;

  color: var(--color-text-secondary);

  font-size: 14px;
}

/* =================================
   애니메이션
================================= */

@keyframes food-float {
  0%,
  100% {
    transform: translateY(0) rotate(0);
  }

  50% {
    transform: translateY(-7px) rotate(3deg);
  }
}

@keyframes route-panel-open {
  from {
    opacity: 0;

    transform: translateY(9px);
  }

  to {
    opacity: 1;

    transform: translateY(0);
  }
}

/* =================================
   태블릿
================================= */

@media (max-width: 1023px) {
  .hero__inner {
    grid-template-columns: minmax(0, 1fr) 330px;
    gap: 36px;
  }

  .hero__visual-main {
    width: 330px;
  }

  .hero__plate {
    width: 165px;
    height: 165px;

    border-width: 13px;
  }

  .hero__plate-icon {
    font-size: 68px;
  }

  .hero__food {
    width: 52px;
    height: 52px;

    border-radius: 17px;

    font-size: 26px;
  }

  .hero__bubble {
    font-size: 11px;
  }

  .taste-card {
    flex-basis: min(760px, 84vw);
  }

  .taste-card__content {
    padding: 31px;
  }

  .food-route__panel {
    gap: 28px;

    padding: 32px;
  }

  .nearby-card {
    padding: 23px;
  }

  .nearby-card::before {
    left: 23px;
  }

  .nearby-card h4 {
    font-size: 20px;
  }
}

/* =================================
   모바일
================================= */

@media (max-width: 767px) {
  .section {
    padding: 64px 0;
  }

  .section__inner,
  .hero__inner,
  .home-cta__inner {
    width: min(100% - 32px, var(--content-width));
  }

  .section-heading {
    align-items: flex-start;

    margin-bottom: 26px;
  }
  .section-heading p {
    font-size: 14px;
  }

  .section-heading__link {
    display: none;
  }

  /* Hero */

  .hero {
    min-height: auto;
  }

  .hero__inner {
    grid-template-columns: 1fr;
    gap: 44px;

    padding: 54px 0 64px;
  }

  .hero__eyebrow {
    margin-bottom: 17px;

    font-size: 12px;
  }

  .hero__title {
    font-size: 39px;
  }

  .hero__description {
    margin-top: 19px;

    font-size: 15px;
  }

  .hero__description br {
    display: none;
  }

  .hero__actions {
    flex-direction: column;

    margin-top: 25px;
  }

  .button {
    width: 100%;

    box-sizing: border-box;
  }

  .hero__visual-main {
    width: min(100%, 320px);
  }

  .hero__plate {
    width: 150px;
    height: 150px;
  }

  .hero__plate-icon {
    font-size: 62px;
  }

  .hero__food {
    width: 48px;
    height: 48px;

    font-size: 24px;
  }

  .hero__bubble {
    padding: 9px 11px;

    font-size: 10px;
  }

  .hero__bubble--top {
    left: -1%;
  }

  .hero__bubble--bottom {
    right: -1%;
  }

  /* 맛 3선 */

  .taste-card {
    flex-basis: 88vw;
    grid-template-columns: 1fr;

    min-height: 0;
  }

  .taste-card__image {
    min-height: 240px;
  }

  .taste-card__number {
    top: 18px;
    left: 18px;

    font-size: 34px;
  }

  .taste-card__content {
    padding: 25px 22px 28px;
  }

  .taste-card__content h3 {
    font-size: 28px;
  }

  .taste-card__content p {
    margin-top: 14px;

    font-size: 13px;
  }

  .taste-card__link {
    margin-top: 21px;
  }

  .taste-section__guide {
    display: block;
  }

  /* 맛집 노선 */

  .food-route__heading {
    margin-bottom: 40px;
  }
  .food-route__heading h2 {
    font-size: 27px;
  }

  .food-route__heading p {
    font-size: 14px;
  }

  .food-route__line {
    grid-template-columns: 1fr;

    margin-bottom: 30px;
    padding-left: 16px;
  }

  .food-route__line::before {
    top: 23px;
    bottom: 23px;
    left: 28px;

    width: 3px;
    height: auto;
  }

  .food-route__station {
    min-height: 70px;
    flex-direction: row;
    align-items: center;
  }

  .food-route__number {
    display: none;
  }

  .food-route__dot {
    flex-shrink: 0;
  }

  .food-route__station-copy {
    align-items: flex-start;

    margin: 0 0 0 20px;

    text-align: left;
  }

  .food-route__station-copy strong {
    font-size: 15px;
  }

  #route-dong:checked
    ~ .food-route__line
    .station--dong
    .food-route__dot,
  #route-jung:checked
    ~ .food-route__line
    .station--jung
    .food-route__dot,
  #route-seo:checked
    ~ .food-route__line
    .station--seo
    .food-route__dot,
  #route-yuseong:checked
    ~ .food-route__line
    .station--yuseong
    .food-route__dot,
  #route-daedeok:checked
    ~ .food-route__line
    .station--daedeok
    .food-route__dot {
    width: 31px;
    height: 31px;

    transform: translateX(-5px);
  }

  #route-dong:checked
    ~ .food-route__line
    .station--dong
    .food-route__station-copy,
  #route-jung:checked
    ~ .food-route__line
    .station--jung
    .food-route__station-copy,
  #route-seo:checked
    ~ .food-route__line
    .station--seo
    .food-route__station-copy,
  #route-yuseong:checked
    ~ .food-route__line
    .station--yuseong
    .food-route__station-copy,
  #route-daedeok:checked
    ~ .food-route__line
    .station--daedeok
    .food-route__station-copy {
    transform: none;
  }

  .food-route__panels {
    min-height: 0;
  }

  .food-route__panel {
    grid-template-columns: 1fr;
    align-items: flex-start;
    gap: 24px;

    padding: 26px 22px;
  }

  .food-route__panel h3 {
    font-size: 23px;
  }

  .food-route__panel p {
    font-size: 13px;
  }

  .food-route__link {
    width: 100%;

    box-sizing: border-box;
    justify-content: center;
  }

  /* 근교 */

  .nearby-route {
    margin-top: 54px;
    padding-top: 40px;
  }

  .nearby-route__heading {
    align-items: flex-start;
    flex-direction: column;
    gap: 7px;
  }

  .nearby-route__heading h3 {
    font-size: 22px;
  }

  .nearby-route__cards {
    grid-template-columns: 1fr;
  }

  .nearby-card {
    min-height: 190px;

    padding: 23px;
  }

  .nearby-card::before {
    left: 23px;
  }

  .nearby-card h4 {
    margin-top: 18px;

    font-size: 21px;
  }

  /* CTA */

  .home-cta {
    padding-bottom: 64px;
  }

  .home-cta__inner {
    align-items: flex-start;
    flex-direction: column;
    gap: 25px;

    padding: 32px 25px;
  }

  .home-cta h2 {
    font-size: 25px;
  }

  .home-cta p {
    font-size: 13px;
  }
}

/* =================================
   모션 감소 설정
================================= */

@media (prefers-reduced-motion: reduce) {
  .hero__food {
    animation: none;
  }

  .taste-slider {
    scroll-behavior: auto;
  }

  .button,
  .taste-card__link,
  .food-route__dot,
  .food-route__station-copy,
  .food-route__link,
  .nearby-card,
  .nearby-card__cta {
    transition: none;
  }

  .food-route__panel {
    animation: none;
  }
}
</style>