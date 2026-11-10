import apiClient from './axios'

export const sendChatMessage = (payload) => {
  // LLM 응답은 일반 REST 호출보다 오래 걸릴 수 있어 타임아웃을 넉넉히 잡는다.
  return apiClient.post('/api/chat', payload, { timeout: 30000 })
}
