interface ReportRadarProps {
  data: Array<{ name: string; value: number }>;
  size?: number;
}

export default function ReportRadar({ data, size = 340 }: ReportRadarProps) {
  if (!data.length) return null;

  const cx = size / 2;
  const cy = size / 2;
  const maxR = size / 2 - 50;
  const n = data.length;
  const angleStep = (2 * Math.PI) / n;

  function polarToXY(angle: number, r: number): [number, number] {
    return [cx + r * Math.sin(angle), cy - r * Math.cos(angle)];
  }

  function getColor(v: number): string {
    if (v >= 90) return '#1B9E5A';
    if (v >= 65) return '#D97706';
    if (v >= 36) return '#8A8A8A';
    return '#C8102E';
  }

  // Rings
  const rings = [25, 50, 75, 100];

  // Data polygon
  const polyPoints = data
    .map((d, i) => {
      const angle = i * angleStep;
      const r = (Math.min(d.value, 100) / 100) * maxR;
      return polarToXY(angle, r);
    })
    .map(([x, y]) => `${x},${y}`)
    .join(' ');

  // Average
  const avg = Math.round(data.reduce((s, d) => s + d.value, 0) / n);

  return (
    <div style={styles.container}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <rect width={size} height={size} rx={12} fill="#0C1B37" />

        {/* Rings */}
        {rings.map((pct) => (
          <circle
            key={pct}
            cx={cx}
            cy={cy}
            r={(pct / 100) * maxR}
            fill="none"
            stroke="rgba(255,255,255,0.08)"
            strokeWidth={1}
          />
        ))}

        {/* Axis lines */}
        {data.map((_, i) => {
          const angle = i * angleStep;
          const [ex, ey] = polarToXY(angle, maxR);
          return (
            <line
              key={i}
              x1={cx}
              y1={cy}
              x2={ex}
              y2={ey}
              stroke="rgba(255,255,255,0.06)"
              strokeWidth={1}
            />
          );
        })}

        {/* Data polygon fill */}
        <polygon
          points={polyPoints}
          fill="rgba(200, 16, 46, 0.15)"
          stroke="#C8102E"
          strokeWidth={2}
        />

        {/* Data dots */}
        {data.map((d, i) => {
          const angle = i * angleStep;
          const r = (Math.min(d.value, 100) / 100) * maxR;
          const [x, y] = polarToXY(angle, r);
          return (
            <circle
              key={i}
              cx={x}
              cy={y}
              r={4}
              fill={getColor(d.value)}
              stroke="#0C1B37"
              strokeWidth={2}
            />
          );
        })}

        {/* Labels */}
        {data.map((d, i) => {
          const angle = i * angleStep;
          const [lx, ly] = polarToXY(angle, maxR + 28);
          return (
            <text
              key={i}
              x={lx}
              y={ly}
              textAnchor="middle"
              dominantBaseline="middle"
              fill={getColor(d.value)}
              fontSize={9}
              fontFamily="'DM Sans', sans-serif"
              fontWeight={600}
            >
              {d.name.length > 12 ? d.name.slice(0, 12) + '…' : d.name}
            </text>
          );
        })}

        {/* Center score */}
        <circle cx={cx} cy={cy} r={22} fill="rgba(200, 16, 46, 0.9)" />
        <text
          x={cx}
          y={cy + 1}
          textAnchor="middle"
          dominantBaseline="middle"
          fill="#fff"
          fontSize={14}
          fontFamily="'JetBrains Mono', monospace"
          fontWeight={700}
        >
          {avg}
        </text>
      </svg>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    display: 'flex',
    justifyContent: 'center',
  },
};
