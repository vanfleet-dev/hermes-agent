import { describe, expect, it } from 'vitest'

import {
  DURATION_PAD_LEN,
  VERB_PAD_LEN,
  formatCodexQuotaCompact,
  formatStackHealthCompact,
  padTickerDuration,
  padVerb
} from '../components/appChrome.js'
import { VERBS } from '../content/verbs.js'

describe('FaceTicker verb padding', () => {
  it('pads every verb to the same width', () => {
    for (const verb of VERBS) {
      expect(padVerb(verb)).toHaveLength(VERB_PAD_LEN)
    }
  })

  it('keeps trailing ellipsis attached', () => {
    for (const verb of VERBS) {
      expect(padVerb(verb).startsWith(`${verb}…`)).toBe(true)
    }
  })
})

describe('FaceTicker duration padding', () => {
  it('keeps elapsed segment width stable across second/minute boundaries', () => {
    const samples = [9000, 10000, 59000, 60000, 61000, 3599000]
    const lens = samples.map(ms => padTickerDuration(ms).length)

    expect(new Set(lens)).toEqual(new Set([DURATION_PAD_LEN]))
  })
})

describe('formatCodexQuotaCompact', () => {
  it('renders compact 5h and weekly percentages', () => {
    expect(
      formatCodexQuotaCompact({
        session_used_percent: 12,
        state: 'green',
        weekly_used_percent: 34
      })
    ).toBe('GPT 5H:12% WK:34%')
  })

  it('renders cooldown countdown when blackout is active', () => {
    expect(
      formatCodexQuotaCompact(
        {
          session_reset_at: 1_800,
          state: 'blackout'
        },
        600_000
      )
    ).toBe('GPT CD:20m')
  })
})

describe('formatStackHealthCompact', () => {
  it('renders healthy stack state compactly', () => {
    expect(formatStackHealthCompact({ status: 'healthy' })).toBe('● SRV OK')
  })

  it('marks stale stack state with a suffix', () => {
    expect(formatStackHealthCompact({ stale: true, status: 'degraded' })).toBe('● SRV DEG~')
  })
})
