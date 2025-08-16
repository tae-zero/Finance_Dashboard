'use client'

import IndustryAnalysis from '@/components/IndustryAnalysis';

type PageProps = {
  params: {
    industryName: string;
  };
};

export default function Page({ params }: PageProps) {
  const { industryName } = params;

  return (
    <div className="min-h-screen bg-gray-50">
      <IndustryAnalysis industryName={decodeURIComponent(industryName)} />
    </div>
  );
}
