import { fetchOpsUrl } from '@/app/lib/ops';
import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  return NextResponse.json({ ops_display_url: await fetchOpsUrl() });
}
