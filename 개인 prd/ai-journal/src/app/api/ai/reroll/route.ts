import { NextRequest, NextResponse } from 'next/server'
import Anthropic from '@anthropic-ai/sdk'

const anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY })

export async function POST(request: NextRequest) {
  const { content, q1Answer, q2Answer, rerollHint, rerollQ, emotion } = await request.json()

  const qIndex = Number(rerollQ ?? 0)

  const hintText = rerollHint
    ? `\n사용자가 원하는 방향: "${rerollHint}"`
    : ''

  let userContent = `저널: ${content}`
  if (qIndex >= 1 && q1Answer) userContent += `\nQ1 답변: ${q1Answer}`
  if (qIndex >= 2 && q2Answer) userContent += `\nQ2 답변: ${q2Answer}`
  if (emotion) userContent += `\n감지된 감정: ${emotion}`

  const system = `당신은 직장인, 학생 등 다양한 사람들을 10년 이상 상담해온 심리상담사입니다.
아래 저널과 대화 맥락을 읽고, Q${qIndex + 1}에 해당하는 새로운 질문 하나만 만드세요.${hintText}

규칙:
- 이전에 했던 질문과 다른 새로운 각도로
- 짧고 자연스럽게, 판단하지 않는 톤
- "왜"로 시작 금지, "~아닐까요?" 금지
- 질문 텍스트만 반환, 다른 말 없이`

  try {
    const message = await anthropic.messages.create({
      model: 'claude-sonnet-4-5',
      max_tokens: 100,
      system,
      messages: [{ role: 'user', content: userContent }]
    })

    const text = message.content[0].type === 'text' ? message.content[0].text.trim() : ''
    return NextResponse.json({ question: text })
  } catch (e) {
    console.error('Reroll error:', e)
    return NextResponse.json({ error: '질문 생성 중 오류가 발생했습니다.' }, { status: 500 })
  }
}
