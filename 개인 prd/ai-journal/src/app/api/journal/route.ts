import { createClient as createAdmin } from '@supabase/supabase-js'
import { createClient } from '@/lib/supabase/server'
import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const supabase = await createClient()
    const { data: { user }, error: authError } = await supabase.auth.getUser()

    console.log('user:', user?.id, 'authError:', authError?.message)
    console.log('SERVICE_KEY exists:', !!process.env.SUPABASE_SERVICE_ROLE_KEY)

    if (!user) return NextResponse.json({ error: '로그인이 필요합니다' }, { status: 401 })

    const body = await request.json()

    const admin = createAdmin(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_ROLE_KEY!
    )

    const { error } = await admin.from('journals').insert({
      user_id: user.id,
      content: body.content,
      emotion_tags: body.emotion_tags,
      primary_emotion: body.primary_emotion,
      ai_confidence: body.ai_confidence,
      ai_questions: body.questions,
      reflection_answers: body.answers,
      ai_comment: body.comment,
      ai_cause: body.cause,
      ai_solutions: body.solutions,
      question_ratings: body.question_ratings ?? [0, 0, 0],
    })

    console.log('insert error:', error?.message)

    if (error) return NextResponse.json({ error: error.message }, { status: 500 })

    return NextResponse.json({ success: true })
  } catch (e) {
    console.error('journal API error:', e)
    return NextResponse.json({ error: String(e) }, { status: 500 })
  }
}
