import React from 'react';
import { Download } from 'lucide-react';
import html2canvas from 'html2canvas';

const ChartExportButton = ({ targetRef, filename }) => {
  const handleExport = async () => {
    if (!targetRef?.current) return;
    try {
      const canvas = await html2canvas(targetRef.current, {
        backgroundColor: '#111111',
        scale: 2,
        logging: false,
        useCORS: true,
      });
      const link = document.createElement('a');
      link.download = filename;
      link.href = canvas.toDataURL('image/png');
      link.click();
    } catch (err) {
      console.error('Chart export failed:', err);
    }
  };

  return (
    <button className="chart-export-btn" onClick={handleExport} title="Export as PNG">
      <Download size={14} />
    </button>
  );
};

export default ChartExportButton;
