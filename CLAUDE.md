# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Git & GitHub Workflow

After every meaningful change — new feature, bug fix, visual update, refactor — commit and push immediately. Never leave work uncommitted at the end of a session.

```bash
git add <specific files>
git commit -m "short present-tense description"
git push
```

Commit message rules:
- Present tense, lowercase, no period: `add pawn promotion modal`, `fix castling through check bug`
- Be specific: `change dark squares to gray` not `update styles`
- One logical change per commit — don't bundle unrelated edits

Push to `origin main` after every commit so work is never only local.
