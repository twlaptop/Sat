import { createClient } from '@supabase/supabase-js'
import { NextRequest, NextResponse } from 'next/server'

function maskEmail(email: string) {
  const [local, domain] = email.split('@')
  const masked = local.slice(0, 2) + '*'.repeat(Math.max(local.length - 2, 3))
  return `${masked}@${domain}`
}

export async function POST(request: NextRequest) {
  const { name } = await request.json()
  if (!name) return NextResponse.json({ error: '이름을 입력해 주세요.' }, { status: 400 })

  const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY
  if (!serviceRoleKey) {
    return NextResponse.json({ error: '서비스 설정 오류입니다.' }, { status: 500 })
  }

  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    serviceRoleKey
  )

  const { data, error } = await supabase
    .from('profiles')
    .select('email, name')
    .eq('name', name)

  if (error || !data || data.length === 0) {
    return NextResponse.json({ found: false })
  }

  const results = data.map(p => ({ maskedEmail: maskEmail(p.email), name: p.name }))
  return NextResponse.json({ found: true, results })
}
