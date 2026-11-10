import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '@/views/HomeView.vue'
import RestaurantExploreView from '@/views/RestaurantExploreView.vue'
import RestaurantDetailView from '@/views/RestaurantDetailView.vue'
import PostListView from '@/views/PostListView.vue'
import PostDetailView from '@/views/PostDetailView.vue'
import PostCreateView from '@/views/PostCreateView.vue'
import PostEditView from '@/views/PostEditView.vue'
import AboutView from '@/views/AboutView.vue'
import NotFoundView from '@/views/NotFoundView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),

  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/map',
      name: 'restaurant-explore',
      component: RestaurantExploreView,
    },
    {
      path: '/restaurants/:restaurantId',
      name: 'restaurant-detail',
      component: RestaurantDetailView,
      props: true,
    },
    {
      path: '/posts',
      name: 'post-list',
      component: PostListView,
    },
    {
      path: '/posts/new',
      name: 'post-create',
      component: PostCreateView,
    },
    {
      path: '/posts/:postId',
      name: 'post-detail',
      component: PostDetailView,
      props: true,
    },
    {
      path: '/posts/:postId/edit',
      name: 'post-edit',
      component: PostEditView,
      props: true,
    },
    {
      path: '/about',
      name: 'about',
      component: AboutView,
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: NotFoundView,
    },
  ],

  scrollBehavior() {
    return {
      top: 0,
    }
  },
})

export default router