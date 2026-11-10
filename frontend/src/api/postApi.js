import apiClient from './axios'

export const getPosts = (params = {}) => {
  return apiClient.get('/api/posts', {
    params,
  })
}

export const getPostById = (postId) => {
  return apiClient.get(`/api/posts/${postId}`)
}

export const createPost = (payload) => {
  return apiClient.post('/api/posts', payload)
}

export const updatePost = (postId, payload) => {
  return apiClient.put(`/api/posts/${postId}`, payload)
}

export const deletePost = (postId, password) => {
  return apiClient.delete(`/api/posts/${postId}`, {
    data: {
      password,
    },
  })
}
