import { flushPromises, mount } from '@vue/test-utils'
import ElementPlus from 'element-plus'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import HomeView from '@/views/HomeView.vue'

const { push, cards } = vi.hoisted(() => ({
  push: vi.fn(),
  cards: vi.fn(),
}))

vi.mock('vue-router', () => ({
  useRouter: () => ({ push }),
}))

vi.mock('@/stores/user', () => ({
  useUserStore: () => ({
    isLoggedIn: false,
    user: null,
  }),
}))

vi.mock('@/api', () => ({
  applicationApi: { apply: vi.fn() },
  recruitmentApi: { cards },
}))

describe('HomeView', () => {
  beforeEach(() => {
    cards.mockResolvedValue({
      items: [
        {
          id: 7,
          team_id: 12,
          title: '回归测试招募',
          competition_track: 'math_modeling',
          target_size: 3,
          required_skills: ['数学理论'],
          current_members: 1,
          team_name: '测试队',
          team_status: 'recruiting',
        },
      ],
      total: 1,
      skip: 0,
      limit: 12,
    })
  })

  it('passes filters to the card API and opens the matching team detail', async () => {
    const wrapper = mount(HomeView, {
      global: { plugins: [ElementPlus] },
    })
    await flushPromises()

    expect(cards).toHaveBeenCalledWith(0, 12, undefined, undefined)

    const skillInput = wrapper.find('input[placeholder*="数据分析"]')
    await skillInput.setValue('数学理论')
    const searchButton = wrapper
      .findAll('button')
      .find((button) => button.text().includes('搜索'))
    expect(searchButton).toBeTruthy()
    await searchButton!.trigger('click')
    await flushPromises()

    expect(cards).toHaveBeenLastCalledWith(
      0,
      12,
      undefined,
      '数学理论',
    )

    const detailButton = wrapper
      .findAll('button')
      .find((button) => button.text().includes('查看详情'))
    expect(detailButton).toBeTruthy()
    await detailButton!.trigger('click')
    expect(push).toHaveBeenCalledWith('/teams/12')
  })
})
