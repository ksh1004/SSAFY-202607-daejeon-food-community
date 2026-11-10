<script setup>
import { onMounted, onBeforeUnmount, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const props = defineProps({
  restaurants: {
    type: Array,
    default: () => [],
  },
  selectedId: {
    type: [Number, String, null],
    default: null,
  },
  center: {
    type: Array,
    default: () => [36.3599, 127.3853], // 정부대전청사 주변 기본 좌표
  },
  zoom: {
    type: Number,
    default: 15,
  },
})

const emit = defineEmits(['select', 'marker-click'])

const router = useRouter()
const mapContainer = ref(null)

let map = null
let markerLayer = null
const markersById = new Map()

const createPinIcon = (isActive) => {
  const color = isActive ? 'var(--color-accent, #f97316)' : 'var(--color-primary, #2563eb)'
  return L.divIcon({
    className: 'restaurant-pin',
    html: `
      <svg width="22" height="29" viewBox="0 0 32 42" xmlns="http://www.w3.org/2000/svg">
        <path
          d="M16 0C7.163 0 0 7.163 0 16c0 11 16 26 16 26s16-15 16-26C32 7.163 24.837 0 16 0z"
          fill="${color}"
          stroke="#ffffff"
          stroke-width="1.5"
        />
        <circle cx="16" cy="16" r="6" fill="#ffffff" />
      </svg>
    `,
    iconSize: [22, 29],
    iconAnchor: [11, 29],
    popupAnchor: [0, -26],
  })
}

const buildPopupContent = (restaurant) => {
  const wrapper = document.createElement('div')
  wrapper.className = 'restaurant-popup'
  wrapper.innerHTML = `
    <div class="restaurant-popup__top">
      ${
        restaurant.image
          ? `<img class="restaurant-popup__thumb" src="${restaurant.image}" alt="${restaurant.name}" />`
          : ''
      }
      <div class="restaurant-popup__info">
        ${restaurant.category ? `<p class="restaurant-popup__badge">${restaurant.category}</p>` : ''}
        <h3 class="restaurant-popup__title">${restaurant.name}</h3>
        <p class="restaurant-popup__address">${restaurant.roadAddress ?? ''}</p>
        ${
          restaurant.jibunAddress
            ? `<p class="restaurant-popup__address restaurant-popup__address--sub">${restaurant.jibunAddress}</p>`
            : ''
        }
      </div>
    </div>
    <button type="button" class="restaurant-popup__button">상세보기</button>
  `

  wrapper.querySelector('.restaurant-popup__button').addEventListener('click', () => {
    router.push({ name: 'restaurant-detail', params: { restaurantId: restaurant.id } })
  })

  return wrapper
}

const clearMarkers = () => {
  markerLayer?.clearLayers()
  markersById.clear()
}

const renderMarkers = ({ fitToResults = true } = {}) => {
  if (!map) return

  clearMarkers()

  const withCoords = props.restaurants.filter(
    (restaurant) => Number.isFinite(restaurant.lat) && Number.isFinite(restaurant.lng),
  )

  withCoords.forEach((restaurant) => {
    const marker = L.marker([restaurant.lat, restaurant.lng], {
      icon: createPinIcon(restaurant.id === props.selectedId),
    })

    marker.bindPopup(buildPopupContent(restaurant))
    marker.on('click', () => emit('marker-click', restaurant))
    marker.on('popupopen', () => emit('select', restaurant))

    marker.addTo(markerLayer)
    markersById.set(restaurant.id, marker)
  })

  if (!fitToResults) return

  if (withCoords.length > 0) {
    const bounds = L.latLngBounds(withCoords.map((r) => [r.lat, r.lng]))
    map.fitBounds(bounds, { padding: [48, 48], maxZoom: 16 })
  } else {
    map.setView(props.center, props.zoom)
  }
}

const refreshMarkerIcons = () => {
  markersById.forEach((marker, id) => {
    marker.setIcon(createPinIcon(id === props.selectedId))
  })
}

const focusRestaurant = (id) => {
  const marker = markersById.get(id)
  if (!marker || !map) return

  map.flyTo(marker.getLatLng(), Math.max(map.getZoom(), 15), { duration: 0.6 })
  marker.openPopup()
}

defineExpose({ focusRestaurant })

onMounted(() => {
  map = L.map(mapContainer.value, {
    zoomControl: true,
  }).setView(props.center, props.zoom)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors',
  }).addTo(map)

  markerLayer = L.layerGroup().addTo(map)

  // 최초 진입 시에는 전체 마커에 맞춰 확대/축소하지 않고, 정부대전청사 주변 기본 범위를 유지한다.
  renderMarkers({ fitToResults: false })
})

onBeforeUnmount(() => {
  map?.remove()
  map = null
})

// 최초 데이터 로딩(빈 배열 -> 전체 목록) 시에는 정부대전청사 주변 기본 범위를 유지하고,
// 이후 검색/필터로 목록이 바뀔 때만 결과에 맞춰 지도 범위를 자동 조정한다.
let isFirstRestaurantsUpdate = true

watch(
  () => props.restaurants,
  () => {
    renderMarkers({ fitToResults: !isFirstRestaurantsUpdate })
    isFirstRestaurantsUpdate = false
  },
  { deep: true },
)

watch(
  () => props.selectedId,
  () => refreshMarkerIcons(),
)
</script>

<template>
  <div ref="mapContainer" class="restaurant-map" role="application" aria-label="음식점 위치 지도" />
</template>

<style scoped>
.restaurant-map {
  width: 100%;
  height: 100%;
  min-height: 320px;
  border-radius: var(--radius-lg);
  overflow: hidden;
}
</style>

<style>
.restaurant-pin {
  filter: drop-shadow(0 2px 4px rgba(15, 23, 42, 0.25));
}

.leaflet-popup-content-wrapper {
  border-radius: var(--radius-md);
}

.restaurant-popup {
  min-width: 200px;
}

.restaurant-popup__top {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.restaurant-popup__thumb {
  flex-shrink: 0;
  width: 56px;
  height: 56px;
  border-radius: var(--radius-sm);
  object-fit: cover;
}

.restaurant-popup__info {
  min-width: 0;
  flex: 1;
}

.restaurant-popup__badge {
  display: inline-block;
  margin: 0 0 6px;
  padding: 2px 8px;
  border-radius: 999px;
  background: var(--color-primary-50);
  color: var(--color-primary);
  font-size: 12px;
  font-weight: 700;
}

.restaurant-popup__title {
  margin: 0 0 6px;
  font-size: 16px;
  font-weight: 800;
  color: var(--color-text-primary);
}

.restaurant-popup__address {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 13px;
  line-height: 1.5;
}

.restaurant-popup__address--sub {
  margin-bottom: 10px;
}

.restaurant-popup__button {
  width: 100%;
  min-height: 36px;
  margin-top: 4px;
  border: 0;
  border-radius: var(--radius-sm);
  background: var(--color-primary);
  color: #ffffff;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
}

.restaurant-popup__button:hover {
  background: var(--color-primary-hover);
}
</style>
