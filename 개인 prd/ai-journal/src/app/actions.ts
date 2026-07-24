'use server'

import { createClient } from '@/lib/supabase/server'
import { createClient as createAdmin } from '@supabase/supabase-js'
import { revalidatePath } from 'next/cache'

export async function saveJournal(content: string, aiResult: {
  emotion_tags: string[]
  primary_emotion: string
  ai_confidence: string
  questions: string[]
}) {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) throw new Error('로그인이 필요합니다')

  // service role로 RLS 우회하여 저장
  const admin = createAdmin(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  )

  const { error } = await admin.from('journals').insert({
    user_id: user.id,
    content,
    emotion_tags: aiResult.emotion_tags,
    primary_emotion: aiResult.primary_emotion,
    ai_confidence: aiResult.ai_confidence,
    ai_questions: aiResult.questions,
  })

  if (error) throw new Error(error.message)
  revalidatePath('/')
}

export async function signOut() {
  const supabase = await createClient()
  await supabase.auth.signOut()
}
