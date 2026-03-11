import { twMerge } from 'tailwind-merge';

export function cn(...classes: (string | undefined | null | false)[]) {
  return twMerge(classes.filter(Boolean).join(' '));
}

export function getScoreClass(score: number): string {
  if (score >= 75) return 'score-elite';
  if (score >= 60) return 'score-above';
  if (score >= 40) return 'score-average';
  return 'score-below';
}

export function getScoreColor(score: number): string {
  if (score >= 75) return '#22c55e';
  if (score >= 60) return '#eab308';
  if (score >= 40) return '#f97316';
  return '#ef4444';
}

export function getPerformanceLabel(cls: string | null): string {
  const map: Record<string, string> = {
    'Muito Alto': 'ELITE',
    'Alto': 'ACIMA',
    'Médio': 'MÉDIO',
    'Baixo': 'ABAIXO',
    'Muito Baixo': 'FRACO',
  };
  return cls ? map[cls] || cls : '—';
}

export function formatNumber(val: number | null | undefined): string {
  if (val === null || val === undefined) return '—';
  return val % 1 === 0 ? val.toString() : val.toFixed(1);
}
