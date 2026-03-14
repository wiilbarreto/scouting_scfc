import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { DollarSign, AlertCircle, TrendingUp, TrendingDown } from 'lucide-react';
import { useMutation } from '@tanstack/react-query';
import api from '../lib/api';
import { usePlayers } from '../hooks/usePlayers';
import { getScoreColor } from '../lib/utils';

interface MarketValueResult {
  player: string;
  display_name: string | null;
  position: string | null;
  estimated_market_value: number | null;
  market_value_gap: number | null;
  market_value_gap_pct: number | null;
  value_category: string | null;
  is_undervalued: boolean | null;
}

const VALUE_LABELS: Record<string, { label: string; color: string }> = {
  'elite': { label: 'Elite', color: '#22c55e' },
  'high': { label: 'Alto', color: '#3b82f6' },
  'medium': { label: 'Medio', color: '#eab308' },
  'low': { label: 'Baixo', color: '#f97316' },
  'very_low': { label: 'Muito Baixo', color: '#ef4444' },
};

export default function MarketValuePage() {
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [selectedPlayer, setSelectedPlayer] = useState('');
  const [currentValue, setCurrentValue] = useState('');
  const [timer, setTimer] = useState<ReturnType<typeof setTimeout> | null>(null);

  const searchParams = useMemo(() => ({ search: debouncedSearch || undefined, limit: 10 }), [debouncedSearch]);
  const { data: searchData } = usePlayers(debouncedSearch.length >= 2 && !selectedPlayer ? searchParams : { limit: 0 });
  const players = searchData?.players ?? [];

  const handleSearchChange = (v: string) => {
    setSearch(v);
    setSelectedPlayer('');
    if (timer) clearTimeout(timer);
    setTimer(setTimeout(() => setDebouncedSearch(v), 200));
  };

  const valuation = useMutation({
    mutationFn: async () => {
      const payload: Record<string, unknown> = { player_name: selectedPlayer };
      if (currentValue) payload.current_value = parseFloat(currentValue);
      const res = await api.post('/market_value', payload);
      return res.data as MarketValueResult;
    },
  });

  const result = valuation.data;
  const cat = result?.value_category ? VALUE_LABELS[result.value_category] : null;

  return (
    <div className="space-y-5">
      <div>
        <h1 className="font-[var(--font-display)] text-lg font-bold tracking-tight flex items-center gap-2">
          <DollarSign size={18} style={{ color: 'var(--color-accent)' }} />
          Valor de Mercado
        </h1>
        <p className="text-xs mt-0.5" style={{ color: 'var(--color-text-muted)' }}>
          Estimativa com XGBoost — Khalife et al. (MDPI 2025), R² {'>'} 0.90
        </p>
      </div>

      {valuation.error && (
        <div className="flex items-center gap-2 px-4 py-3 rounded text-sm" style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', color: '#ef4444' }}>
          <AlertCircle size={16} /><span>Erro: {(valuation.error as Error).message}</span>
        </div>
      )}

      <div className="card-glass rounded-lg p-5 space-y-4" style={{ overflow: 'visible' }}>
        <div className="grid grid-cols-1 md:grid-cols-[1fr_auto_auto] gap-3 items-end" style={{ overflow: 'visible' }}>
          <div>
            <label className="block text-[10px] font-[var(--font-display)] tracking-[0.1em] uppercase mb-1" style={{ color: 'var(--color-text-muted)' }}>JOGADOR</label>
            <div className="relative">
              <input type="text" value={search} onChange={(e) => handleSearchChange(e.target.value)} placeholder="Digite o nome do jogador..." className="w-full px-3 py-2 rounded text-sm outline-none" style={{ background: 'var(--color-surface-2)', border: '1px solid var(--color-border-subtle)', color: 'var(--color-text-primary)' }} />
              {debouncedSearch.length >= 2 && !selectedPlayer && players.length > 0 && (
                <div className="absolute top-full left-0 right-0 mt-1 rounded overflow-hidden z-50 max-h-48 overflow-y-auto" style={{ background: 'var(--color-surface-1)', border: '1px solid var(--color-border-active)' }}>
                  {players.map((p, i) => (
                    <button key={i} onClick={() => { setSelectedPlayer(p.display_name || p.name); setSearch(p.display_name || p.name); setDebouncedSearch(''); }} className="w-full text-left px-3 py-2 text-sm hover:bg-white/5 cursor-pointer" style={{ borderBottom: '1px solid var(--color-border-subtle)', color: 'var(--color-text-primary)' }}>
                      <div>{p.display_name || p.name}</div>
                      <div className="text-[10px]" style={{ color: 'var(--color-text-muted)' }}>{p.team} — {p.league}</div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
          <div>
            <label className="block text-[10px] font-[var(--font-display)] tracking-[0.1em] uppercase mb-1" style={{ color: 'var(--color-text-muted)' }}>VALOR ATUAL (opcional)</label>
            <input type="number" value={currentValue} onChange={(e) => setCurrentValue(e.target.value)} placeholder="Ex: 50 (score)" className="px-3 py-2 rounded text-sm outline-none w-40" style={{ background: 'var(--color-surface-2)', border: '1px solid var(--color-border-subtle)', color: 'var(--color-text-primary)' }} />
          </div>
          <button
            onClick={() => valuation.mutate()}
            disabled={!selectedPlayer || valuation.isPending}
            className="px-5 py-2 rounded text-sm font-[var(--font-display)] font-semibold tracking-wide uppercase transition-all cursor-pointer disabled:opacity-40"
            style={{ background: 'var(--color-accent)', color: '#fff', border: 'none' }}
          >
            {valuation.isPending ? '...' : 'ESTIMAR'}
          </button>
        </div>
      </div>

      {result && (
        <>
          <div className="card-glass rounded-lg p-5" style={{ background: 'linear-gradient(135deg, rgba(30,41,59,0.8), rgba(15,23,42,0.8))' }}>
            <div className="font-bold text-xl">{result.player}</div>
            <div className="text-xs mt-1" style={{ color: 'var(--color-text-muted)' }}>{result.position}</div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="card-glass rounded-lg p-4 text-center">
              <div className="text-[10px] font-[var(--font-display)] tracking-[0.1em] uppercase" style={{ color: 'var(--color-text-muted)' }}>VALOR ESTIMADO</div>
              <div className="text-2xl font-[var(--font-mono)] font-bold mt-1" style={{ color: getScoreColor(result.estimated_market_value ?? 50) }}>
                {result.estimated_market_value?.toFixed(1) ?? '-'}
              </div>
              <div className="text-[9px]" style={{ color: 'var(--color-text-muted)' }}>Score de valor</div>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="card-glass rounded-lg p-4 text-center">
              <div className="text-[10px] font-[var(--font-display)] tracking-[0.1em] uppercase" style={{ color: 'var(--color-text-muted)' }}>CATEGORIA</div>
              <div className="text-xl font-[var(--font-display)] font-bold mt-1 uppercase" style={{ color: cat?.color ?? '#6b7280' }}>
                {cat?.label ?? '-'}
              </div>
            </motion.div>

            {result.market_value_gap !== null && (
              <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="card-glass rounded-lg p-4 text-center">
                <div className="text-[10px] font-[var(--font-display)] tracking-[0.1em] uppercase" style={{ color: 'var(--color-text-muted)' }}>GAP DE VALOR</div>
                <div className="text-2xl font-[var(--font-mono)] font-bold mt-1 flex items-center justify-center gap-1" style={{ color: result.market_value_gap > 0 ? '#22c55e' : '#ef4444' }}>
                  {result.market_value_gap > 0 ? <TrendingUp size={18} /> : <TrendingDown size={18} />}
                  {result.market_value_gap > 0 ? '+' : ''}{result.market_value_gap.toFixed(1)}
                </div>
                <div className="text-[9px]" style={{ color: 'var(--color-text-muted)' }}>
                  {result.is_undervalued ? 'Subvalorizado' : 'Sobrevalorizado'}
                </div>
              </motion.div>
            )}

            {result.market_value_gap_pct !== null && (
              <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="card-glass rounded-lg p-4 text-center">
                <div className="text-[10px] font-[var(--font-display)] tracking-[0.1em] uppercase" style={{ color: 'var(--color-text-muted)' }}>GAP %</div>
                <div className="text-2xl font-[var(--font-mono)] font-bold mt-1" style={{ color: result.market_value_gap_pct > 0 ? '#22c55e' : '#ef4444' }}>
                  {result.market_value_gap_pct > 0 ? '+' : ''}{result.market_value_gap_pct.toFixed(1)}%
                </div>
              </motion.div>
            )}
          </div>
        </>
      )}

      {!result && !valuation.isPending && (
        <div className="card-glass rounded-lg p-8 text-center" style={{ color: 'var(--color-text-muted)' }}>
          <DollarSign size={32} className="mx-auto mb-3 opacity-30" />
          <p className="text-sm">Selecione um jogador e clique em ESTIMAR</p>
          <p className="text-xs mt-1 opacity-60">XGBoost com segmentacao por posicao x faixa etaria</p>
        </div>
      )}
    </div>
  );
}
