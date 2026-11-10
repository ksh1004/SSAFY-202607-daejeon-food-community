import apiClient from './axios'

const MAX_PAGE_SIZE = 100

const getRegionFromAddress = (addr1 = '') => addr1.trim().split(/\s+/).slice(0, 2).join(' ')

const normalizeRestaurant = (raw) => ({
  id: raw.content_id,
  name: raw.title,
  region: getRegionFromAddress(raw.addr1 ?? ''),
  roadAddress: raw.addr1,
  jibunAddress: raw.addr2 || null,
  lat: Number(raw.mapy),
  lng: Number(raw.mapx),
  image: raw.firstimage || null,
})

export const getRestaurants = async () => {
  const all = []
  let page = 1
  let total = Infinity

  while (all.length < total) {
    const response = await apiClient.get('/api/restaurants', {
      params: { page, size: MAX_PAGE_SIZE },
    })
    const { items, total: totalCount } = response.data

    all.push(...items)
    total = totalCount
    page += 1

    if (items.length === 0) break
  }

  return { data: all.map(normalizeRestaurant) }
}

export const getRestaurantById = async (restaurantId) => {
  try {
    const response = await apiClient.get(`/api/restaurants/${restaurantId}`)
    return { data: normalizeRestaurant(response.data) }
  } catch (error) {
    if (error.response?.status === 404) {
      return { data: null }
    }
    throw error
  }
}

export const getRestaurantPosts = (restaurantId, params = {}) => {
  return apiClient.get('/api/posts', {
    params: { restaurant_id: restaurantId, ...params },
  })
}
