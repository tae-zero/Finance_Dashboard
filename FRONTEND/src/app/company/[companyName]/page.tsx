'use client'

import { useParams } from 'next/navigation';
import CompanyDetail from '@/components/CompanyDetail';

export default function CompanyPage() {
  const params = useParams();
  const companyName = params.companyName as string;

  return (
    <div className="min-h-screen bg-gray-50">
      <CompanyDetail companyName={decodeURIComponent(companyName)} />
    </div>
  );
}
