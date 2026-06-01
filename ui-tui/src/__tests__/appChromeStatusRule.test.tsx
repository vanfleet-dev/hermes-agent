import React from 'react'
import { describe, expect, it, vi } from 'vitest'

import { formatCodexQuotaCompact, StatusRule } from '../components/appChrome.js'
import { DEFAULT_THEME } from '../theme.js'

type ReactNodeLike = React.ReactNode

const textContent = (node: ReactNodeLike): string => {
  if (node === null || node === undefined || typeof node === 'boolean') {
    return ''
  }

  if (typeof node === 'string' || typeof node === 'number') {
    return String(node)
  }

  if (Array.isArray(node)) {
    return node.map(textContent).join('')
  }

  if (React.isValidElement(node)) {
    return textContent(node.props.children)
  }

  return ''
}

describe('StatusRule', () => {
  it('hides ready, compression, voice, and session-count segments', () => {
    const quota = { session_used_percent: 34, state: 'green' as const, weekly_used_percent: 51 }
    const element = StatusRule({
      bgCount: 0,
      busy: false,
      cols: 140,
      cwdLabel: '~/repo',
      liveSessionCount: 3,
      model: 'kimi-k2.6',
      onSessionCountClick: vi.fn(),
      profileName: 'default',
      sessionStartedAt: null,
      showCost: false,
      status: 'ready',
      statusColor: DEFAULT_THEME.color.ok,
      t: DEFAULT_THEME,
      turnStartedAt: null,
      usage: { codex_quota: quota, compressions: 4, total: 0 },
      voiceLabel: 'voice off'
    })

    const text = textContent(element)

    expect(text).not.toContain('ready')
    expect(text).not.toContain('cmp 4')
    expect(text).not.toContain('voice off')
    expect(text).not.toContain('3 sessions')
    expect(text).toContain(formatCodexQuotaCompact(quota))
  })

  it('hides codex quota for non-primary profiles', () => {
    const quota = { session_used_percent: 34, state: 'green' as const, weekly_used_percent: 51 }
    const element = StatusRule({
      bgCount: 0,
      busy: false,
      cols: 140,
      cwdLabel: '~/repo',
      liveSessionCount: 0,
      model: 'kimi-k2.6',
      profileName: 'secondary',
      sessionStartedAt: null,
      showCost: false,
      status: 'ready',
      statusColor: DEFAULT_THEME.color.ok,
      t: DEFAULT_THEME,
      turnStartedAt: null,
      usage: { codex_quota: quota, total: 0 },
      voiceLabel: ''
    })

    expect(textContent(element)).not.toContain(formatCodexQuotaCompact(quota))
  })
})
