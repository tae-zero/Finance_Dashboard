import { useState } from 'react';

export const useTooltip = () => {
  const [showTooltip, setShowTooltip] = useState(false);
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });

  const handleMouseEnter = (e) => {
    setTooltipPosition({ x: e.clientX, y: e.clientY });
    setShowTooltip(true);
  };

  const handleMouseMove = (e) => {
    setTooltipPosition({ x: e.clientX, y: e.clientY });
  };

  const handleMouseLeave = () => {
    setShowTooltip(false);
  };

  return {
    showTooltip,
    tooltipPosition,
    handleMouseEnter,
    handleMouseMove,
    handleMouseLeave
  };
};

export const TooltipImage = ({ show, position, imageSrc, alt, width = "400px" }) => {
  if (!show) return null;

  return (
    <div
      style={{
        position: 'fixed',
        top: position.y + 20,
        left: position.x + 20,
        backgroundColor: 'white',
        border: '1px solid #ccc',
        padding: '8px',
        borderRadius: '6px',
        boxShadow: '0 0 6px rgba(0,0,0,0.15)',
        zIndex: 1000,
      }}
    >
      <img src={imageSrc} alt={alt} style={{ width }} />
    </div>
  );
};
