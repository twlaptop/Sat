import { NextRequest, NextResponse } from 'next/server'
import Anthropic from '@anthropic-ai/sdk'

const anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY })

const PERSONA = `당신은 직장인, 학생, 주부 등 다양한 삶을 살아가는 사람들을 10년 이상 상담해온 심리상담사입니다.
사람들이 자신의 감정을 있는 그대로 꺼내놓을 수 있도록 돕는 것이 당신의 역할입니다.`

const FORBIDDEN = `
절대 하지 말아야 할 것:
- 사용자의 감정이나 행동을 평가하거나 비판하기
- "~해야 합니다", "~하면 안 됩니다" 같은 지시형 표현
- "왜"로 시작하는 질문 (방어적 반응 유발)
- "~알 것 같아요?", "~인 것 같아요?", "~때문은 아닐까요?" 같이 결론을 먼저 제시하는 표현
- "어떤 기분이었나요", "어떠셨나요" 같은 형식적 질문
- "보통", "대부분", "일반적으로" 같은 비교·일반화 표현
- "본인은", "귀하" 같은 딱딱한 표현
- 두 가지 소재를 억지로 한 문장에 연결하기
- 길고 설명적인 문장 (질문은 짧고 자연스럽게)`

// 초기 저널 분석
async function analyzeJournal(content: string) {
  const message = await anthropic.messages.create({
    model: 'claude-sonnet-4-5',
    max_tokens: 600,

    system: `${PERSONA}
아래 저널에서 이 분이 어떤 감정을 느끼는지 함께 살펴보고, 스스로 오늘을 되돌아볼 수 있는 질문을 제안해 주세요.
JSON 형식으로만 응답하세요. 다른 말은 절대 하지 마세요.
${FORBIDDEN}

입력이 주식/날씨/뉴스 등 감정·일기와 무관한 내용이면:
{ "primary_emotion": "무관", "emotion_tags": ["무관"], "q1": "오늘 하루 어땠어요? 있었던 일이나 느낌을 편하게 써보세요", "comment": "여기는 오늘 하루를 기록하는 공간이에요", "cause": "특별한 일이 없어도 괜찮아요. 평범한 하루도 충분해요.", "solutions": ["오늘 가장 기억에 남는 순간을 한 줄로 써보세요", "지금 기분을 한 단어로 표현해보세요"] }

Q1 질문 우선순위:
1순위 — "모르겠다", "것 같기도", "왜인지", "그냥" 같은 모호한 감정 표현이 있으면 반드시 그것을 짚어라
2순위 — 그런 표현이 없을 때만 구체적 사건을 짚어라
질문은 "혹시 ~거 있어요?", "~했어요?" 형태로, 짧고 자연스럽게 하나만

{
  "primary_emotion": "감정 한 단어 (기쁨/스트레스/무기력/성취감/불안/외로움/혼란/설렘/무관 중 하나)",
  "emotion_tags": ["감정1", "감정2"],
  "q1": "자연스럽고 짧은 질문 하나",
  "comment": "오늘 [감정]을 느끼셨군요로 시작하는 공감 한 문장 (30자 이내)",
  "cause": "감정 원인 한 문장 (50자 이내, 판단 없이)",
  "solutions": ["오늘 바로 해볼 수 있는 것 1", "오늘 바로 해볼 수 있는 것 2"]
}`,
    messages: [
      {
        role: 'user',
        content: '저널: 오늘 회의 끝나고 집에 왔는데 왜인지 모르게 좀 멍한 느낌. 딱히 힘든 건 아닌데 그냥 그래.'
      },
      {
        role: 'assistant',
        content: '{"primary_emotion":"무기력","emotion_tags":["멍함","무감각"],"q1":"멍한 느낌, 언제부터였어요?","comment":"오늘 무기력함을 느끼셨군요. 뭔가 흐릿하게 지나간 것 같네요.","cause":"회의 후 감정이 정리되지 않은 채 하루가 마무리됨","solutions":["잠깐 창문 열고 바람 쐬기","오늘 기억나는 한 장면 떠올려보기"]}'
      },
      {
        role: 'user',
        content: '저널: 오늘 발표 망했다. 준비 많이 했는데 막상 앞에 서니까 목소리가 떨렸고 슬라이드도 잘못 넘겼어. 집에 오니까 그냥 아무것도 하기 싫어.'
      },
      {
        role: 'assistant',
        content: '{"primary_emotion":"스트레스","emotion_tags":["실망","자책"],"q1":"목소리 떨렸을 때, 머릿속에 뭐가 스쳤어요?","comment":"오늘 많이 속상하셨군요. 준비했는데 그렇게 되면 더 힘들죠.","cause":"기대와 실제 결과 사이의 간극이 크게 느껴짐","solutions":["오늘 잘 된 한 가지만 떠올려보기","내일 혼자 발표 연습 5분 해보기"]}'
      },
      { role: 'user', content: `저널: ${content}` }
    ]
  })

  const block = message.content.find(b => b.type === 'text')
  const text = block?.type === 'text' ? block.text.trim() : ''
  const jsonMatch = text.match(/\{[\s\S]*\}/)
  if (!jsonMatch) throw new Error('JSON 파싱 실패: ' + text)
  return JSON.parse(jsonMatch[0])
}

// Q1 답변 기반 Q2 생성
async function generateQ2(content: string, q1Answer: string, emotion: string) {
  const message = await anthropic.messages.create({
    model: 'claude-sonnet-4-5',
    max_tokens: 200,

    system: `${PERSONA}
아래 Q1 답변을 읽고 충분한지 판단한 뒤 JSON으로만 응답하세요.
${FORBIDDEN}

답변이 충분하지 않은 경우 (의미 없는 단순 단어 하나, 예: "ㅇ", "응", "글쎄" 만 있는 경우):
{ "sufficient": false, "q1_followup": "Q1 맥락에서 조금 더 말해달라는 짧고 친근한 질문" }

답변이 충분한 경우 (그 외 모든 경우. "없다", "딱히 없다", "모르겠다" 같은 명확한 답변도 충분함):
{ "sufficient": true, "q2": "답변에서 가장 진솔한 표현을 짚어 더 깊이 들어가는 짧은 질문" }

Q2는 Q1 답변을 요약하지 말고 그 안에서 더 깊이 들어갈 것. 질문은 하나만, 짧게.`,
    messages: [{
      role: 'user',
      content: `감정: ${emotion}\n저널: ${content}\nQ1 답변: ${q1Answer}`
    }]
  })

  const block = message.content.find(b => b.type === 'text')
  const text = block?.type === 'text' ? block.text.trim() : ''
  const jsonMatch = text.match(/\{[\s\S]*\}/)
  if (!jsonMatch) return { sufficient: true, q2: '그 마음, 조금 더 말해줄 수 있어요?' }
  return JSON.parse(jsonMatch[0])
}

// Q2 답변 기반 Q3 생성 (sufficient 판단 포함)
async function generateQ3WithSufficient(content: string, q1Answer: string, q2Answer: string, emotion: string) {
  const message = await anthropic.messages.create({
    model: 'claude-sonnet-4-5',
    max_tokens: 150,
    system: `${PERSONA}
아래 Q2 답변을 읽고 충분한지 판단한 뒤 JSON으로만 응답하세요.
${FORBIDDEN}

답변이 충분하지 않은 경우 (의미 없는 단순 단어 하나, 예: "ㅇ", "응", "글쎄" 만 있는 경우):
{ "sufficient": false, "q2_followup": "Q2 맥락에서 조금 더 말해달라는 짧고 친근한 질문" }

답변이 충분한 경우 (그 외 모든 경우):
{ "sufficient": true, "q3": "Q2 답변에서 무심코 드러난 진솔한 표현을 짚어 자연스럽게 유도하는 마지막 질문" }

Q3는 Q2와 다른 각도로. 질문은 하나만, 짧게.`,
    messages: [{
      role: 'user',
      content: `감정: ${emotion}\n저널: ${content}\nQ1 답변: ${q1Answer}\nQ2 답변: ${q2Answer}`
    }]
  })
  const block = message.content.find(b => b.type === 'text')
  const text = block?.type === 'text' ? block.text.trim() : ''
  const jsonMatch = text.match(/\{[\s\S]*\}/)
  if (!jsonMatch) return { sufficient: true, q3: '지금 딱 솔직하게 한 마디만 하면요?' }
  return JSON.parse(jsonMatch[0])
}

async function generateQ3(content: string, q1Answer: string, q2Answer: string, emotion: string) {
  const message = await anthropic.messages.create({
    model: 'claude-sonnet-4-5',
    max_tokens: 100,

    system: `${PERSONA}
Q1, Q2 대화 흐름을 읽고, 이 분이 가장 솔직한 감정을 편하게 털어놓을 수 있는 마지막 질문 하나만 만드세요.
${FORBIDDEN}
중요: Q2에서 이미 확인한 내용을 절대 반복하지 말 것. Q2 답변을 바탕으로 한 단계 더 깊이 들어가는 새로운 질문이어야 함.
예) Q2가 "하루가 흐릿하게 지나간 느낌인가요?"였다면 Q3는 "그런 날이 요즘 자주 있어요?" 또는 "그 느낌, 언제부터였어요?" 처럼 다른 각도로.
질문 텍스트만 반환, 다른 말 없이.`,
    messages: [{
      role: 'user',
      content: `감정: ${emotion}\n저널: ${content}\nQ1 답변: ${q1Answer}\nQ2 답변: ${q2Answer}`
    }]
  })

  const block = message.content.find(b => b.type === 'text')
  const text = block?.type === 'text' ? block.text.trim() : ''
  return text || '지금 딱 솔직하게 한 마디만 하면요?'
}

export async function POST(request: NextRequest) {
  const { content, q1Answer, q2Answer, emotion } = await request.json()

  try {
    if (q2Answer) {
      const result = await generateQ3WithSufficient(content, q1Answer || '', q2Answer, emotion || '')
      return NextResponse.json(result)
    }

    if (q1Answer) {
      const result = await generateQ2(content, q1Answer, emotion || '')
      return NextResponse.json(result)
    }

    const result = await analyzeJournal(content)
    return NextResponse.json({
      emotion_tags: result.emotion_tags ?? [result.primary_emotion],
      primary_emotion: result.primary_emotion,
      ai_confidence: 'high',
      questions: [result.q1, '', ''],
      comment: result.comment,
      cause: result.cause,
      solutions: result.solutions,
    })
  } catch (e) {
    console.error('Claude API error:', e)
    return NextResponse.json({ error: 'AI 분석 중 오류가 발생했습니다.' }, { status: 500 })
  }
}
