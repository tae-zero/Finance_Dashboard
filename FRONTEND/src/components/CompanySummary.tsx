'use client'

interface CompanySummaryProps {
  summary: string;
  outline: { [key: string]: any };
}

function CompanySummary({ summary, outline }: CompanySummaryProps) {
  return (
    <div style={{ marginTop: '50px' }}>
      {/* 📌 말풍선 본체 */}
      <div style={{
        position: 'relative',
        background: '#f8f9fa',
        border: '2px solid #ccc',
        borderRadius: '12px',
        padding: '20px',
        fontSize: '16px',
        maxWidth: '600px',
        boxShadow: '0 4px 10px rgba(0, 0, 0, 0.05)',
        marginBottom: '30px'
      }}>
        {/* 꼬리 테두리 */}
        <div style={{
          position: 'absolute',
          top: '-22px',
          left: '30px',
          width: 0,
          height: 0,
          borderLeft: '11px solid transparent',
          borderRight: '11px solid transparent',
          borderBottom: '22px solid #ccc',
          zIndex: 5
        }}></div>

        {/* 꼬리 내부 색상 */}
        <div style={{
          position: 'absolute',
          top: '-20px',
          left: '31px',
          width: 0,
          height: 0,
          borderLeft: '10px solid transparent',
          borderRight: '10px solid transparent',
          borderBottom: '20px solid #f8f9fa',
          zIndex: 10
        }}></div>

        <h3 style={{ fontSize: '25px', margin: '0 0 10px 0' }}>📝 기업 요약</h3>
        <p style={{ fontSize: '20px', margin: 0 }}>{summary || '요약 정보 없음'}</p>
      </div>


    </div>
  );
}

export default CompanySummary;
