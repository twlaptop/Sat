import { createClient } from '@/lib/supabase/server'
import { redirect } from 'next/navigation'
import HistoryView from '@/components/HistoryView'

export default async function HistoryPage() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) redirect('/login')

  const now = new Date()
  const firstDay = new Date(now.getFullYear(), now.getMonth(), 1).toISOString()
  const lastDay = new Date(now.getFullYear(), now.getMonth() + 1, 0, 23, 59, 59).toISOString()

  const { data: journals } = await supabase
    .from('journals')
    .select('id, content, primary_emotion, emotion_tags, ai_questions, reflection_answers, ai_comment, ai_cause, ai_solutions, created_at')
    .eq('user_id', user.id)
    .gte('created_at', firstDay)
    .lte('created_at', lastDay)
    .order('created_at', { ascending: false })

  const { count: totalCount } = await supabase
    .from('journals')
    .select('*', { count: 'exact', head: true })
    .eq('user_id', user.id)

  return (
    <HistoryView
      journals={journals || []}
      totalCount={totalCount || 0}
      year={now.getFullYear()}
      month={now.getMonth()}
    />
  )
}
