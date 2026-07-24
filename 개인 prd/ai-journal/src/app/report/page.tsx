import { createClient } from '@/lib/supabase/server'
import { redirect } from 'next/navigation'
import WeeklyReport from '@/components/WeeklyReport'

export default async function ReportPage() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) redirect('/login')

  // 이번 주 월~일 계산 (KST)
  const now = new Date()
  const kst = new Date(now.getTime() + 9 * 60 * 60 * 1000)
  const day = kst.getDay()
  const monday = new Date(kst)
  monday.setDate(kst.getDate() - (day === 0 ? 6 : day - 1))
  monday.setHours(0, 0, 0, 0)
  const sunday = new Date(monday)
  sunday.setDate(monday.getDate() + 6)
  sunday.setHours(23, 59, 59, 999)

  const { data: journals } = await supabase
    .from('journals')
    .select('id, content, primary_emotion, emotion_tags, created_at')
    .eq('user_id', user.id)
    .gte('created_at', new Date(monday.getTime() - 9 * 60 * 60 * 1000).toISOString())
    .lte('created_at', new Date(sunday.getTime() - 9 * 60 * 60 * 1000).toISOString())
    .order('created_at', { ascending: true })

  // 지난 주
  const lastMonday = new Date(monday)
  lastMonday.setDate(monday.getDate() - 7)
  const lastSunday = new Date(monday)
  lastSunday.setDate(monday.getDate() - 1)
  lastSunday.setHours(23, 59, 59, 999)

  const { data: lastWeekJournals } = await supabase
    .from('journals')
    .select('primary_emotion')
    .eq('user_id', user.id)
    .gte('created_at', new Date(lastMonday.getTime() - 9 * 60 * 60 * 1000).toISOString())
    .lte('created_at', new Date(lastSunday.getTime() - 9 * 60 * 60 * 1000).toISOString())

  return (
    <WeeklyReport
      journals={journals || []}
      lastWeekJournals={lastWeekJournals || []}
      weekStart={monday.toISOString()}
    />
  )
}
