import { describe, expect, it } from 'vitest'

import { label } from '@/utils/format'

describe('team status labels', () => {
  it('shows active teams as completed instead of in competition', () => {
    expect(label('active')).toBe('组队完成')
  })
})
