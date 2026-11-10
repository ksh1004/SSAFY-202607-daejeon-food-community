<script setup>
import { useRegionBadges } from '@/composables/useRegionBadges'

const { badges, collectedCount, totalCount, progressPercent, isComplete, isCollected } =
  useRegionBadges()
</script>

<template>
  <main class="about">
    <section class="about-hero">
      <span class="about-hero__eyebrow">WHY WE BUILT 잇슈</span>
      <h1 class="about-hero__title">
        흩어진 맛집 정보를,<br />
        우리 동네 사람들의 <strong>진짜 이야기</strong>로
      </h1>
      <p class="about-hero__description">
        잇슈는 공공데이터로 제공되는 대전·충청권 음식점 정보에, 그곳을 다녀온 사람들의 솔직한
        후기를 더해 지역 정보를 더 믿을 수 있게 만드는 걸 목표로 만들어졌습니다. 회원가입 없이
        누구나 자유롭게 이야기를 남길 수 있는 익명 커뮤니티예요.
      </p>
    </section>

    <section class="about-section">
      <div class="section-heading">
        <span class="section-heading__eyebrow">DEVELOPMENT STORY</span>
        <h2>왜 만들었나요?</h2>
      </div>

      <div class="story-grid">
        <article class="story-card">
          <span class="story-card__icon">🗺️</span>
          <h3>지도 위의 정보는 많은데, 이야기는 없었어요</h3>
          <p>
            음식점 위치와 기본 정보는 어디서나 찾을 수 있지만, 정작 "지금 가도 되는지", "주차는
            어떤지" 같은 생생한 이야기는 찾기 어려웠습니다. 잇슈는 지도와 커뮤니티를 한 화면에
            묶어서, 위치 정보와 사람들의 이야기를 동시에 볼 수 있게 했습니다.
          </p>
        </article>

        <article class="story-card">
          <span class="story-card__icon">🕶️</span>
          <h3>가입 없이, 부담 없이</h3>
          <p>
            리뷰 하나 남기자고 회원가입까지 하고 싶지는 않으셨을 거예요. 잇슈는 로그인 없이 글
            제목·내용과 수정용 비밀번호만으로 글을 쓰고 관리할 수 있는 완전 익명 커뮤니티로
            설계했습니다.
          </p>
        </article>

        <article class="story-card">
          <span class="story-card__icon">📍</span>
          <h3>지역 데이터를 지역답게</h3>
          <p>
            대전·충청권 공공데이터를 기반으로, 실제 이 지역에 있는 음식점만 다룹니다. 커뮤니티
            게시글도 특정 음식점과 연결할 수 있어서, "이 동네 이야기"가 자연스럽게 쌓입니다.
          </p>
        </article>
      </div>
    </section>

    <section class="about-section about-section--muted">
      <div class="section-heading">
        <span class="section-heading__eyebrow">FEATURES</span>
        <h2>이런 기능을 만나보세요</h2>
      </div>

      <div class="feature-grid">
        <article class="feature-card">
          <span class="feature-card__icon">🗺️</span>
          <h3>지도에서 맛집 탐색</h3>
          <p>Leaflet 지도 위에서 대전·충청권 음식점을 한눈에 보고, 이름·주소로 검색하고 지역별로 필터링해보세요.</p>
          <RouterLink to="/map" class="feature-card__link">지도 탐색하기 →</RouterLink>
        </article>

        <article class="feature-card">
          <span class="feature-card__icon">🍜</span>
          <h3>음식점 상세 &amp; 관련 게시글</h3>
          <p>마커를 클릭하면 음식점 상세 정보와 함께, 그 음식점에 대해 올라온 커뮤니티 게시글도 바로 확인할 수 있어요.</p>
        </article>

        <article class="feature-card">
          <span class="feature-card__icon">✍️</span>
          <h3>익명 커뮤니티</h3>
          <p>회원가입 없이 제목·내용·비밀번호만으로 글을 쓰고, 같은 비밀번호로 언제든 수정·삭제할 수 있습니다.</p>
          <RouterLink to="/posts" class="feature-card__link">커뮤니티 둘러보기 →</RouterLink>
        </article>

        <article class="feature-card">
          <span class="feature-card__icon">🤖</span>
          <h3>지역 정보 챗봇</h3>
          <p>우측 하단 플로팅 챗봇에게 궁금한 지역 정보를 편하게 물어보세요. 대화 히스토리도 유지됩니다.</p>
        </article>
      </div>
    </section>

    <section class="about-section badge-section">
      <div class="section-heading">
        <span class="section-heading__eyebrow">COLLECTION</span>
        <h2>우리 동네 뱃지 컬렉션</h2>
        <p>
          음식점 상세 페이지를 둘러볼 때마다, 그 지역의 뱃지를 하나씩 모을 수 있어요. 대전 5개
          구와 충청권 4개 지역, 총 {{ totalCount }}개를 모두 모아보세요!
        </p>
      </div>

      <div class="badge-progress">
        <div class="badge-progress__bar">
          <div class="badge-progress__fill" :style="{ width: progressPercent + '%' }"></div>
        </div>
        <span class="badge-progress__label">
          {{ collectedCount }} / {{ totalCount }} 개 수집
          <template v-if="isComplete">· 🎉 전체 컬렉션 완료!</template>
        </span>
      </div>

      <div class="badge-grid">
        <div
          v-for="badge in badges"
          :key="badge.region"
          class="badge-item"
          :class="{ 'badge-item--locked': !isCollected(badge.region) }"
        >
          <span class="badge-item__icon">{{ isCollected(badge.region) ? badge.icon : '🔒' }}</span>
          <strong class="badge-item__label">{{ badge.label }}</strong>
          <span class="badge-item__description">
            {{ isCollected(badge.region) ? badge.description : '아직 방문하지 않은 지역이에요' }}
          </span>
        </div>
      </div>

      <p class="badge-hint">
        <RouterLink to="/map">지도 탐색</RouterLink>에서 음식점 상세 페이지를 열어보면 자동으로
        수집됩니다.
      </p>
    </section>

    <section class="about-cta">
      <div class="about-cta__inner">
        <div>
          <span class="about-cta__eyebrow">지금 바로 시작해보세요</span>
          <h2>우리 동네 첫 뱃지, 지금 모아볼까요?</h2>
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
.about {
  overflow: hidden;
  color: var(--color-text-primary);
}

.about-hero {
  padding: 88px 0 64px;
  text-align: center;
  background: linear-gradient(180deg, var(--color-primary-50), var(--color-background) 70%);
}

.about-hero__eyebrow {
  display: inline-block;
  margin-bottom: 18px;
  color: var(--color-primary);
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.1em;
}

.about-hero__title {
  max-width: 720px;
  margin: 0 auto;
  font-size: clamp(30px, 4vw, 44px);
  line-height: 1.35;
  letter-spacing: -0.03em;
}

.about-hero__title strong {
  color: var(--color-primary);
}

.about-hero__description {
  max-width: 560px;
  margin: 22px auto 0;
  color: var(--color-text-secondary);
  font-size: 16px;
  line-height: 1.75;
}

.about-section {
  width: min(100% - 48px, var(--content-width));
  margin: 0 auto;
  padding: 72px 0;
}

.about-section--muted {
  width: 100%;
  max-width: none;
  padding: 72px 24px;
  background: var(--color-surface-soft);
}

.about-section--muted > * {
  width: min(100% - 0px, var(--content-width));
  margin-left: auto;
  margin-right: auto;
}

.section-heading {
  margin-bottom: 36px;
  text-align: center;
}

.section-heading__eyebrow {
  display: block;
  margin-bottom: 10px;
  color: var(--color-primary);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.1em;
}

.section-heading h2 {
  margin: 0;
  font-size: clamp(24px, 3vw, 32px);
  letter-spacing: -0.03em;
}

.section-heading p {
  max-width: 520px;
  margin: 12px auto 0;
  color: var(--color-text-secondary);
  font-size: 15px;
  line-height: 1.7;
}

.story-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 20px;
}

.story-card {
  padding: 28px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  background: var(--color-surface);
  box-shadow: var(--shadow-card);
}

.story-card__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  margin-bottom: 16px;
  border-radius: var(--radius-md);
  background: var(--color-primary-50);
  font-size: 24px;
}

.story-card h3 {
  margin: 0 0 10px;
  font-size: 17px;
  line-height: 1.4;
}

.story-card p {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 14px;
  line-height: 1.7;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 18px;
}

.feature-card {
  display: flex;
  flex-direction: column;
  padding: 26px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  background: var(--color-surface);
}

.feature-card__icon {
  margin-bottom: 14px;
  font-size: 28px;
}

.feature-card h3 {
  margin: 0 0 8px;
  font-size: 16px;
}

.feature-card p {
  flex: 1;
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 13px;
  line-height: 1.6;
}

.feature-card__link {
  margin-top: 14px;
  color: var(--color-primary);
  font-size: 13px;
  font-weight: 700;
  text-decoration: none;
}

.feature-card__link:hover {
  color: var(--color-primary-hover);
}

.badge-section {
  text-align: center;
}

.badge-progress {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  max-width: 420px;
  margin: 0 auto 32px;
}

.badge-progress__bar {
  width: 100%;
  height: 12px;
  overflow: hidden;
  border-radius: var(--radius-pill);
  background: var(--color-surface-soft);
}

.badge-progress__fill {
  height: 100%;
  border-radius: var(--radius-pill);
  background: linear-gradient(90deg, var(--color-primary), var(--color-accent));
  transition: width var(--transition-base);
}

.badge-progress__label {
  color: var(--color-text-secondary);
  font-size: 14px;
  font-weight: 700;
}

.badge-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  text-align: left;
}

.badge-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 20px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  background: var(--color-surface);
  box-shadow: var(--shadow-card);
  transition: transform var(--transition-fast);
}

.badge-item:not(.badge-item--locked):hover {
  transform: translateY(-3px);
}

.badge-item--locked {
  border-style: dashed;
  background: var(--color-surface-soft);
  opacity: 0.75;
}

.badge-item__icon {
  margin-bottom: 6px;
  font-size: 30px;
}

.badge-item__label {
  font-size: 15px;
}

.badge-item__description {
  color: var(--color-text-secondary);
  font-size: 12px;
  line-height: 1.5;
}

.badge-hint {
  margin: 28px 0 0;
  color: var(--color-text-secondary);
  font-size: 13px;
}

.badge-hint a {
  color: var(--color-primary);
  font-weight: 700;
  text-decoration: none;
}

.about-cta {
  width: min(100% - 48px, var(--content-width));
  margin: 0 auto 96px;
  padding: 46px 52px;
  overflow: hidden;
  border: 1px solid var(--color-primary-200);
  border-radius: var(--radius-xl);
  background:
    radial-gradient(circle at 90% 20%, var(--color-primary-100), transparent 26%),
    var(--color-primary-50);
}

.about-cta__inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 32px;
}

.about-cta__eyebrow {
  display: block;
  margin-bottom: 8px;
  color: var(--color-primary);
  font-size: 13px;
  font-weight: 800;
}

.about-cta h2 {
  margin: 0;
  font-size: 26px;
  letter-spacing: -0.03em;
}

.button {
  display: inline-flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  gap: 12px;
  min-height: 52px;
  padding: 0 22px;
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  font-size: 15px;
  font-weight: 750;
  text-decoration: none;
  transition:
    color var(--transition-fast),
    background-color var(--transition-fast),
    transform var(--transition-fast);
}

.button:hover {
  transform: translateY(-2px);
}

.button--primary {
  background: var(--color-primary);
  color: #ffffff;
}

.button--primary:hover {
  background: var(--color-primary-hover);
}

@media (max-width: 1023px) {
  .story-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .feature-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .badge-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 767px) {
  .about-hero {
    padding: 64px 0 48px;
  }

  .about-section,
  .about-section--muted {
    padding: 48px 0;
  }

  .about-section--muted {
    padding: 48px 20px;
  }

  .story-grid,
  .feature-grid,
  .badge-grid {
    grid-template-columns: 1fr;
  }

  .about-cta {
    padding: 32px 24px;
  }

  .about-cta__inner {
    flex-direction: column;
    align-items: flex-start;
  }

  .button {
    width: 100%;
  }
}
</style>
