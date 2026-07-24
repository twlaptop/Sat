import { createClient } from '@/lib/supabase/server'
import { redirect } from 'next/navigation'
import JournalEditor from '@/components/JournalEditor'

export default async function Home() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) redirect('/login')

  const { data: journals } = await supabase
    .from('journals')
    .select('id, content, primary_emotion, emotion_tags, created_at')
    .order('created_at', { ascending: false })
    .limit(7)

  const today = new Date().toISOString().split('T')[0]
  const { count } = await supabase
    .from('journals')
    .select('*', { count: 'exact', head: true })
    .eq('user_id', user.id)
    .gte('created_at', today)

  return <JournalEditor user={user} recentJournals={journals || []} todayCount={count || 0} />
}
