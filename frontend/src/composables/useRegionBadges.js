import { computed, reactive } from 'vue'

// 대전_충청권 데이터셋에 실제로 존재하는 9개 지역(구/시/군) 기준 뱃지 목록
export const REGION_BADGES = [
  { region: '대전광역시 동구', label: '동구', icon: '🚉', description: '대전역이 있는 관문 지역' },
  { region: '대전광역시 중구', label: '중구', icon: '🥐', description: '성심당의 도시' },
  { region: '대전광역시 서구', label: '서구', icon: '🏢', description: '정부대전청사가 있는 곳' },
  { region: '대전광역시 유성구', label: '유성구', icon: '♨️', description: '유성온천으로 유명한 지역' },
  { region: '대전광역시 대덕구', label: '대덕구', icon: '🔬', description: '대덕연구개발특구' },
  { region: '충청남도 계룡시', label: '계룡시', icon: '⛰️', description: '계룡산이 있는 군사 도시' },
  { region: '충청남도 공주시', label: '공주시', icon: '🏯', description: '백제의 고도' },
  { region: '충청남도 논산시', label: '논산시', icon: '🍓', description: '딸기로 유명한 곡창지대' },
  { region: '충청북도 옥천군', label: '옥천군', icon: '🌊', description: '금강이 흐르는 고장' },
]

const STORAGE_KEY = 'localhub-region-badges'

const loadCollected = () => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return new Set(raw ? JSON.parse(raw) : [])
  } catch {
    return new Set()
  }
}

// 모듈 스코프의 단일 reactive 상태 - 여러 컴포넌트에서 import해도 같은 상태를 공유한다.
const state = reactive({
  collected: loadCollected(),
})

const persist = () => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify([...state.collected]))
}

export const useRegionBadges = () => {
  // 아직 수집하지 않은 지역이면 true를 반환해, 호출부에서 "새로 획득" 연출에 쓸 수 있게 한다.
  const recordVisit = (region) => {
    if (!region || !REGION_BADGES.some((badge) => badge.region === region)) return false
    if (state.collected.has(region)) return false

    state.collected.add(region)
    persist()
    return true
  }

  const isCollected = (region) => state.collected.has(region)

  const collectedCount = computed(() => state.collected.size)
  const totalCount = REGION_BADGES.length
  const progressPercent = computed(() => Math.round((collectedCount.value / totalCount) * 100))
  const isComplete = computed(() => collectedCount.value === totalCount)

  return {
    badges: REGION_BADGES,
    collectedCount,
    totalCount,
    progressPercent,
    isComplete,
    isCollected,
    recordVisit,
  }
}
