'use client'

import { useParams } from 'next/navigation';
import IndustryAnalysis from '@/components/IndustryAnalysis';

export default function IndustryPage() {
  const params = useParams();
  const industryName = params.industryName as string;

  return (
    <div className="min-h-screen bg-gray-50">
      <IndustryAnalysis industryName={decodeURIComponent(industryName)} />
    </div>
  );
}
