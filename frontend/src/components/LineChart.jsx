import React from 'react';

function LineChart({ data, width = 800, height = 300 }) {
  if (!data || data.length === 0) {
    return <div style={{ padding: '2rem', textAlign: 'center', color: '#999' }}>No data available</div>;
  }

  const padding = 40;
  const chartWidth = width - 2 * padding;
  const chartHeight = height - 2 * padding;

  // Find min/max values
  const yValues = data.map(d => d.y);
  const yMin = Math.min(...yValues);
  const yMax = Math.max(...yValues);
  const yRange = yMax - yMin || 1;

  // Generate points for the line
  const points = data.map((point, index) => {
    const x = padding + (index / (data.length - 1)) * chartWidth;
    const y = padding + chartHeight - ((point.y - yMin) / yRange) * chartHeight;
    return `${x},${y}`;
  }).join(' ');

  return (
    <svg width={width} height={height} style={{ border: '1px solid #ddd', background: '#fff' }}>
      {/* Y-axis */}
      <line 
        x1={padding} 
        y1={padding} 
        x2={padding} 
        y2={height - padding} 
        stroke="#333" 
        strokeWidth="2"
      />
      {/* X-axis */}
      <line 
        x1={padding} 
        y1={height - padding} 
        x2={width - padding} 
        y2={height - padding} 
        stroke="#333" 
        strokeWidth="2"
      />
      
      {/* Grid lines */}
      {[0, 0.25, 0.5, 0.75, 1].map((ratio, i) => {
        const y = padding + chartHeight * ratio;
        const value = Math.round(yMax - ratio * yRange);
        return (
          <g key={i}>
            <line 
              x1={padding} 
              y1={y} 
              x2={width - padding} 
              y2={y} 
              stroke="#eee" 
              strokeWidth="1"
            />
            <text x={padding - 10} y={y + 5} textAnchor="end" fontSize="12" fill="#666">
              {value}
            </text>
          </g>
        );
      })}

      {/* Data line */}
      <polyline
        points={points}
        fill="none"
        stroke="#3498db"
        strokeWidth="2"
      />

      {/* Data points */}
      {data.map((point, index) => {
        const x = padding + (index / (data.length - 1)) * chartWidth;
        const y = padding + chartHeight - ((point.y - yMin) / yRange) * chartHeight;
        return (
          <circle 
            key={index} 
            cx={x} 
            cy={y} 
            r="3" 
            fill="#3498db"
          />
        );
      })}

      {/* Labels */}
      <text x={width / 2} y={height - 5} textAnchor="middle" fontSize="14" fill="#333">
        Date
      </text>
      <text 
        x={15} 
        y={height / 2} 
        textAnchor="middle" 
        fontSize="14" 
        fill="#333"
        transform={`rotate(-90, 15, ${height / 2})`}
      >
        AQI Value
      </text>
    </svg>
  );
}

export default LineChart;
