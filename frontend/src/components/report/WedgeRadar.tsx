interface WedgeRadarProps {
  data: Array<{ metric: string; p: number }>;
  size?: number;
}

export default function WedgeRadar({ data, size = 380 }: WedgeRadarProps) {
  if (!data.length) return null;

  const cx = size / 2;
  const cy = size / 2;
  const maxR = size / 2 - 60;
  const innerR = 30;
  const n = data.length;
  const wedgeAngle = (2 * Math.PI) / n;
  const gap = 0.02; // small gap between wedges

  function getWedgeColor(p: number): string {
    if (p >= 95) return '#1B9E5A';
    if (p >= 85) return '#80CBA2';
    if (p >= 65) return '#D97706';
    return '#4A4A4A';
  }

  function describeArc(
    startAngle: number,
    endAngle: number,
    rInner: number,
    rOuter: number,
  ): string {
    const x1o = cx + rOuter * Math.sin(startAngle);
    const y1o = cy - rOuter * Math.cos(startAngle);
    const x2o = cx + rOuter * Math.sin(endAngle);
    const y2o = cy - rOuter * Math.cos(endAngle);
    const x1i = cx + rInner * Math.sin(endAngle);
    const y1i = cy - rInner * Math.cos(endAngle);
    const x2i = cx + rInner * Math.sin(startAngle);
    const y2i = cy - rInner * Math.cos(startAngle);
    const largeArc = endAngle - startAngle > Math.PI ? 1 : 0;

    return [
      `M ${x1o} ${y1o}`,
      `A ${rOuter} ${rOuter} 0 ${largeArc} 1 ${x2o} ${y2o}`,
      `L ${x1i} ${y1i}`,
      `A ${rInner} ${rInner} 0 ${largeArc} 0 ${x2i} ${y2i}`,
      'Z',
    ].join(' ');
  }

  // Rings
  const rings = [25, 50, 75, 100];

  return (
    <div style={styles.container}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <rect width={size} height={size} rx={12} fill="#0C1B37" />

        {/* Background rings */}
        {rings.map((pct) => (
          <circle
            key={pct}
            cx={cx}
            cy={cy}
            r={innerR + ((maxR - innerR) * pct) / 100}
            fill="none"
            stroke="rgba(255,255,255,0.06)"
            strokeWidth={1}
          />
        ))}

        {/* Wedges */}
        {data.map((d, i) => {
          const startAngle = i * wedgeAngle + gap;
          const endAngle = (i + 1) * wedgeAngle - gap;
          const pNorm = Math.min(d.p, 100) / 100;
          const rOuter = innerR + (maxR - innerR) * pNorm;

          return (
            <path
              key={i}
              d={describeArc(startAngle, endAngle, innerR, rOuter)}
              fill={getWedgeColor(d.p)}
              opacity={0.85}
            />
          );
        })}

        {/* Labels */}
        {data.map((d, i) => {
          const midAngle = (i + 0.5) * wedgeAngle;
          const labelR = maxR + 32;
          const lx = cx + labelR * Math.sin(midAngle);
          const ly = cy - labelR * Math.cos(midAngle);

          return (
            <g key={`label-${i}`}>
              <text
                x={lx}
                y={ly - 6}
                textAnchor="middle"
                dominantBaseline="middle"
                fill="rgba(255,255,255,0.8)"
                fontSize={8}
                fontFamily="'DM Sans', sans-serif"
                fontWeight={500}
              >
                {d.metric.length > 14 ? d.metric.slice(0, 14) + '…' : d.metric}
              </text>
              <text
                x={lx}
                y={ly + 6}
                textAnchor="middle"
                dominantBaseline="middle"
                fill={getWedgeColor(d.p)}
                fontSize={10}
                fontFamily="'JetBrains Mono', monospace"
                fontWeight={700}
              >
                P{d.p}
              </text>
            </g>
          );
        })}

        {/* Center */}
        <circle cx={cx} cy={cy} r={innerR} fill="#0C1B37" stroke="rgba(255,255,255,0.1)" strokeWidth={1} />
        <text
          x={cx}
          y={cy - 4}
          textAnchor="middle"
          dominantBaseline="middle"
          fill="#80CBA2"
          fontSize={14}
          fontFamily="'JetBrains Mono', monospace"
          fontWeight={700}
        >
          {data.length}
        </text>
        <text
          x={cx}
          y={cy + 10}
          textAnchor="middle"
          dominantBaseline="middle"
          fill="rgba(255,255,255,0.5)"
          fontSize={7}
          fontFamily="'DM Sans', sans-serif"
          fontWeight={600}
          textDecoration="uppercase"
        >
          ELITE
        </text>
      </svg>

      {/* Legend */}
      <div style={styles.legend}>
        <div style={styles.legendItem}>
          <span style={{ ...styles.legendDot, background: '#1B9E5A' }} />
          <span style={styles.legendText}>P95+ Elite</span>
        </div>
        <div style={styles.legendItem}>
          <span style={{ ...styles.legendDot, background: '#80CBA2' }} />
          <span style={styles.legendText}>P85-94 Destaque</span>
        </div>
        <div style={styles.legendItem}>
          <span style={{ ...styles.legendDot, background: '#D97706' }} />
          <span style={styles.legendText}>P65-84 Acima</span>
        </div>
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: 16,
  },
  legend: {
    display: 'flex',
    gap: 20,
    justifyContent: 'center',
    flexWrap: 'wrap',
  },
  legendItem: {
    display: 'flex',
    alignItems: 'center',
    gap: 6,
  },
  legendDot: {
    width: 10,
    height: 10,
    borderRadius: 3,
    display: 'inline-block',
  },
  legendText: {
    fontFamily: "'DM Sans', sans-serif",
    fontSize: 11,
    color: '#4A4A4A',
  },
};
