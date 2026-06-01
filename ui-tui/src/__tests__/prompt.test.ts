import { describe, expect, it } from 'vitest'

import { composerPromptText } from '../lib/prompt.js'

describe('composerPromptText', () => {
  it('returns shell prompt for ! commands', () => {
    expect(composerPromptText('❯', 'coder', true)).toBe('$')
  })

  it('does not prefix profile names onto the normal prompt', () => {
    expect(composerPromptText('❯', 'coder')).toBe('❯')
    expect(composerPromptText('❯', 'default')).toBe('❯')
    expect(composerPromptText('❯', 'custom')).toBe('❯')
    expect(composerPromptText('❯')).toBe('❯')
  })

  it('uses a Termux-safe ASCII prompt marker in normal mode', () => {
    expect(composerPromptText('❯', 'coder', false, true, 50)).toBe('>')
  })

  it('suppresses profile prefixes on Termux widths', () => {
    expect(composerPromptText('❯', 'upstr', false, true, 72)).toBe('>')
    expect(composerPromptText('❯', 'upstr', false, true, 120)).toBe('>')
  })
})
