import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Search, Users, Percent } from 'lucide-react';
import { usePlayers, useSimilarity } from '../hooks/usePlayers';
import api from '../lib/api';
import { formatNumber } from '../lib/utils';

export default function SimilarityPage() {
  const { result, loading: simLoading, findSimilar } = useSimilarity();
  const { players, fetchPlayers } = usePlayers();
  const [search, setSearch] = useState('');
  const [selectedPlayer, setSelectedPlayer] = useState('');
  const [position, setPosition] = useState('Atacante');
  const [topN, setTopN] = useState(20);
  const [minMinutes, setMinMinutes] = useState(500);
  const [positions, setPositions] = useState<string[]>([]);

  useEffect(() => {
    api.get('/config/positions').then((r) => setPositions(r.data.positions)).catch(() => {});
  }, []);

  useEffect(() => {
    if (search.length >= 2) {
      const t = setTimeout(() => fetchPlayers({ search, limit: 10 }), 200);
      return () => clearTimeout(t);
    }
  }, [search, fetchPlayers]);

  const handleSearch = () => {
    if (selectedPlayer) {
      findSimilar(selectedPlayer, position, topN, minMinutes);
    }
  };

  return (
    <div className="space-y-5">
      <div>
        <h1 className="font-[var(--font-display)] text-lg font-bold tracking-tight flex items-center gap-2">
          <Users size={18} style={{ color: 'var(--color-accent)' }} />
          Similaridade
        </h1>
        <p className="text-xs mt-0.5" style={{ color: 'var(--color-text-muted)' }}>
          Encontre jogadores similares por perfil de desempenho ponderado
        </p>
      </div>

      {/* Controls */}
      <div className="card-glass rounded-lg p-5 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-[1fr_auto_auto_auto_auto] gap-3 items-end">
          <div>
            <label className="block text-[10px] font-[var(--font-display)] tracking-[0.1em] uppercase mb-1" style={{ color: 'var(--color-text-muted)' }}>
              JOGADOR REFERENCIA
            </label>
            <div className="relative">
              <input
                type="text"
                value={search}
                onChange={(e) => { setSearch(e.target.value); setSelectedPlayer(''); }}
                placeholder="Digite o nome..."
                className="w-full px-3 py-2 rounded text-sm outline-none"
                style={{ background: 'var(--color-surface-2)', border: '1px solid var(--color-border-subtle)', color: 'var(--color-text-primary)', fontFamily: 'var(--font-body)' }}
              />
              {search.length >= 2 && !selectedPlayer && players.length > 0 && (
                <div
                  className="absolute top-full left-0 right-0 mt-1 rounded overflow-hidden z-20 max-h-48 overflow-y-auto"
                  style={{ background: 'var(--color-surface-1)', border: '1px solid var(--color-border-active)' }}
                >
                  {players.map((p, i) => (
                    <button
                      key={i}
                      onClick={() => { setSelectedPlayer(p.display_name || p.name); setSearch(p.display_name || p.name); }}
                      className="w-full text-left px-3 py-2 text-sm transition-colors hover:bg-white/5 cursor-pointer"
                      style={{ borderBottom: '1px solid var(--color-border-subtle)', color: 'var(--color-text-primary)' }}
                    >
                      <div>{p.display_name || p.name}</div>
                      <div className="text-[10px]" style={{ color: 'var(--color-text-muted)' }}>{p.team} — {p.position}</div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div>
            <label className="block text-[10px] font-[var(--font-display)] tracking-[0.1em] uppercase mb-1" style={{ color: 'var(--color-text-muted)' }}>POSICAO</label>
            <select value={position} onChange={(e) => setPosition(e.target.value)} className="px-3 py-2 rounded text-sm cursor-pointer outline-none" style={{ background: 'var(--color-surface-2)', border: '1px solid var(--color-border-subtle)', color: 'var(--color-text-secondary)' }}>
              {positions.map((p) => <option key={p} value={p}>{p}</option>)}
            </select>
          </div>

          <div>
            <label className="block text-[10px] font-[var(--font-display)] tracking-[0.1em] uppercase mb-1" style={{ color: 'var(--color-text-muted)' }}>TOP N</label>
            <input type="number" value={topN} onChange={(e) => setTopN(Number(e.target.value))} className="w-16 px-3 py-2 rounded text-sm outline-none" style={{ background: 'var(--color-surface-2)', border: '1px solid var(--color-border-subtle)', color: 'var(--color-text-primary)', fontFamily: 'var(--font-mono)' }} />
          </div>

          <div>
            <label className="block text-[10px] font-[var(--font-display)] tracking-[0.1em] uppercase mb-1" style={{ color: 'var(--color-text-muted)' }}>MIN MIN</label>
            <input type="number" value={minMinutes} onChange={(e) => setMinMinutes(Number(e.target.value))} className="w-20 px-3 py-2 rounded text-sm outline-none" style={{ background: 'var(--color-surface-2)', border: '1px solid var(--color-border-subtle)', color: 'var(--color-text-primary)', fontFamily: 'var(--font-mono)' }} />
          </div>

          <button
            onClick={handleSearch}
            disabled={!selectedPlayer || simLoading}
            className="px-4 py-2 rounded text-sm font-[var(--font-display)] font-semibold tracking-wide uppercase transition-all cursor-pointer disabled:opacity-40"
            style={{ background: 'var(--color-accent)', color: '#fff', border: 'none' }}
          >
            {simLoading ? '...' : 'BUSCAR'}
          </button>
        </div>
      </div>

      {/* Results */}
      {result && (
        <div className="card-glass rounded-lg overflow-hidden">
          <div className="px-4 py-2.5" style={{ borderBottom: '1px solid var(--color-border-subtle)' }}>
            <span className="text-[10px] font-[var(--font-display)] tracking-[0.15em] uppercase" style={{ color: 'var(--color-text-muted)' }}>
              SIMILARES A {result.reference_player} ({result.position})
            </span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr style={{ borderBottom: '1px solid var(--color-border-subtle)' }}>
                  <th className="px-3 py-2.5 text-left text-[10px] font-[var(--font-display)] tracking-[0.1em] uppercase" style={{ color: 'var(--color-text-muted)' }}>#</th>
                  <th className="px-3 py-2.5 text-left text-[10px] font-[var(--font-display)] tracking-[0.1em] uppercase" style={{ color: 'var(--color-text-muted)' }}>Jogador</th>
                  <th className="px-3 py-2.5 text-left text-[10px] font-[var(--font-display)] tracking-[0.1em] uppercase" style={{ color: 'var(--color-text-muted)' }}>Equipa</th>
                  <th className="px-3 py-2.5 text-right text-[10px] font-[var(--font-display)] tracking-[0.1em] uppercase" style={{ color: 'var(--color-text-muted)' }}>Metricas</th>
                  <th className="px-3 py-2.5 text-right text-[10px] font-[var(--font-display)] tracking-[0.1em] uppercase" style={{ color: 'var(--color-accent)' }}>Similaridade</th>
                </tr>
              </thead>
              <tbody>
                {result.similar_players.map((sp, i) => (
                  <motion.tr
                    key={i}
                    initial={{ opacity: 0, x: -6 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.03 }}
                    style={{ borderBottom: '1px solid var(--color-border-subtle)' }}
                    className="transition-colors hover:bg-white/[0.02]"
                  >
                    <td className="px-3 py-2.5 font-[var(--font-mono)] text-xs" style={{ color: 'var(--color-text-muted)' }}>{i + 1}</td>
                    <td className="px-3 py-2.5 font-medium">{sp.display_name || sp.name}</td>
                    <td className="px-3 py-2.5 text-xs" style={{ color: 'var(--color-text-secondary)' }}>{sp.team || '—'}</td>
                    <td className="px-3 py-2.5 text-right font-[var(--font-mono)] text-xs" style={{ color: 'var(--color-text-muted)' }}>{sp.matched_metrics}</td>
                    <td className="px-3 py-2.5 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        <div className="w-16 h-1.5 rounded-full overflow-hidden" style={{ background: 'var(--color-surface-3)' }}>
                          <div className="h-full rounded-full" style={{ width: `${sp.similarity_pct}%`, background: sp.similarity_pct >= 80 ? '#22c55e' : sp.similarity_pct >= 60 ? '#eab308' : '#f97316' }} />
                        </div>
                        <span className="font-[var(--font-mono)] text-xs font-bold" style={{ color: sp.similarity_pct >= 80 ? '#22c55e' : sp.similarity_pct >= 60 ? '#eab308' : '#f97316' }}>
                          {sp.similarity_pct.toFixed(1)}%
                        </span>
                      </div>
                    </td>
                  </motion.tr>
                ))}
                {result.similar_players.length === 0 && (
                  <tr><td colSpan={5} className="px-3 py-8 text-center text-xs" style={{ color: 'var(--color-text-muted)' }}>Nenhum jogador similar encontrado</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
