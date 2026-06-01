import { describe, expect, it } from 'vitest'

import { statusRuleWidths } from '../components/appChrome.js'

describe('statusRuleWidths', () => {
  it('uses the full width for the left segment', () => {
    for (const cols of [1, 8, 12, 20, 40, 100]) {
      expect(statusRuleWidths(cols)).toEqual({ leftWidth: cols, rightWidth: 0, separatorWidth: 0 })
    }
  })

  it('normalizes invalid widths to at least one column', () => {
    expect(statusRuleWidths(0)).toEqual({ leftWidth: 1, rightWidth: 0, separatorWidth: 0 })
  })
})
