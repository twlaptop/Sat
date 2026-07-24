# AI 감정 저널

> 직장인·학생이 하루를 자유롭게 쓰면, Claude AI가 상담사처럼 맥락에 맞는 회고 질문을 던져주는 PWA 앱

**배포 URL**: https://ai-journal-olive.vercel.app

---

## 스택

| 레이어 | 기술 |
|---|---|
| 프론트 | Next.js 14 (App Router) + TypeScript + Tailwind |
| DB / 인증 | Supabase |
| AI | Claude API (claude-sonnet-4-5) |
| 배포 | Vercel + PWA |

---

## 핵심 기능

- **AI 감정 분류** — 저널 입력 시 8가지 감정 자동 태깅
- **맥락 기반 회고 질문** — Q1 → Q1.1 → Q2 → Q2.1 → Q3 동적 생성
- **리롤 기능** — 방향 힌트 입력 후 질문 재생성
- **별점 시스템** — 질문 품질 5단계 평가 → DB 저장 → Few-shot 개선
- **주간 리포트** — 7일치 감정 흐름 그래프 + AI 한마디

---

## 로컬 실행

```bash
npm install
npm run dev
```

`.env.local` 필요:
```
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
ANTHROPIC_API_KEY=
NEXT_PUBLIC_APP_URL=http://localhost:3000
```
