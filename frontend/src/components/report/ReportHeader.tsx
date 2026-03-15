interface ReportHeaderProps {
  name: string;
  badges: string[];
  clusterDef: string;
  photo: string | null;
  clubLogo: string | null;
}

export default function ReportHeader({ name, badges, clusterDef, photo, clubLogo }: ReportHeaderProps) {
  const now = new Date();
  const monthNames = [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro',
  ];
  const subtitle = `RELATÓRIO PRESCRITIVO — ${monthNames[now.getMonth()]} ${now.getFullYear()} — BFSA`;

  return (
    <div style={styles.hero}>
      <div style={styles.heroContent}>
        <div style={styles.heroLeft}>
          <div style={styles.subtitle}>{subtitle}</div>
          <h1 style={styles.name}>{name}</h1>
          <div style={styles.badgeRow}>
            {badges.map((b, i) => (
              <span key={i} style={styles.badge}>{b}</span>
            ))}
          </div>
          <div style={styles.clusterDef}>{clusterDef}</div>
        </div>
        <div style={styles.heroRight}>
          {clubLogo && (
            <img
              src={`/api/image-proxy?url=${encodeURIComponent(clubLogo)}`}
              alt="Club"
              style={styles.clubLogo}
              onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
            />
          )}
          {photo && (
            <img
              src={`/api/image-proxy?url=${encodeURIComponent(photo)}`}
              alt={name}
              style={styles.photo}
              onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
            />
          )}
        </div>
      </div>
      <div style={styles.divider} />
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  hero: {
    background: 'linear-gradient(135deg, #0C1B37 0%, #162a4f 50%, #1a3260 100%)',
    borderRadius: 14,
    padding: '40px 44px 32px',
    color: '#fff',
    position: 'relative',
    overflow: 'hidden',
    marginBottom: 32,
  },
  heroContent: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
    gap: 24,
  },
  heroLeft: {
    flex: 1,
  },
  heroRight: {
    display: 'flex',
    alignItems: 'flex-end',
    gap: 16,
    flexShrink: 0,
  },
  subtitle: {
    fontFamily: "'DM Sans', sans-serif",
    fontSize: 10,
    fontWeight: 600,
    letterSpacing: '0.15em',
    textTransform: 'uppercase',
    color: 'rgba(255,255,255,0.5)',
    marginBottom: 12,
  },
  name: {
    fontFamily: "'DM Serif Display', serif",
    fontSize: 42,
    fontWeight: 400,
    lineHeight: 1.1,
    margin: 0,
    letterSpacing: '-0.02em',
  },
  badgeRow: {
    display: 'flex',
    gap: 8,
    flexWrap: 'wrap',
    marginTop: 14,
  },
  badge: {
    background: 'rgba(200, 16, 46, 0.85)',
    color: '#fff',
    fontFamily: "'DM Sans', sans-serif",
    fontSize: 10,
    fontWeight: 600,
    padding: '4px 12px',
    borderRadius: 20,
    letterSpacing: '0.04em',
    textTransform: 'uppercase',
  },
  clusterDef: {
    fontFamily: "'DM Sans', sans-serif",
    fontSize: 13,
    color: 'rgba(255,255,255,0.6)',
    marginTop: 12,
    fontStyle: 'italic',
  },
  clubLogo: {
    width: 56,
    height: 56,
    objectFit: 'contain',
    opacity: 0.7,
  },
  photo: {
    width: 120,
    height: 120,
    objectFit: 'cover',
    borderRadius: 12,
    border: '2px solid rgba(255,255,255,0.2)',
  },
  divider: {
    height: 2,
    background: 'linear-gradient(90deg, #C8102E, transparent)',
    marginTop: 24,
    borderRadius: 1,
  },
};
