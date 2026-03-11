import { useState, useEffect, useCallback } from 'react';
import api from '../lib/api';
import type { PlayerSummary, PlayerProfile, RankingResponse, SimilarityResponse } from '../types/api';

export function usePlayers() {
  const [players, setPlayers] = useState<PlayerSummary[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);

  const fetchPlayers = useCallback(async (params: {
    position?: string;
    league?: string;
    search?: string;
    min_minutes?: number;
    limit?: number;
    offset?: number;
  } = {}) => {
    setLoading(true);
    try {
      const res = await api.get('/players', { params });
      setPlayers(res.data.players);
      setTotal(res.data.total);
    } catch (err) {
      console.error('Failed to fetch players:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  return { players, total, loading, fetchPlayers };
}

export function usePlayerProfile(displayName: string | null) {
  const [profile, setProfile] = useState<PlayerProfile | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!displayName) {
      setProfile(null);
      return;
    }
    setLoading(true);
    api.get(`/players/${encodeURIComponent(displayName)}/profile`)
      .then((res) => setProfile(res.data))
      .catch((err) => console.error('Failed to fetch profile:', err))
      .finally(() => setLoading(false));
  }, [displayName]);

  return { profile, loading };
}

export function useRankings() {
  const [rankings, setRankings] = useState<RankingResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchRankings = useCallback(async (position: string, minMinutes: number = 0, league?: string, topN: number = 50) => {
    setLoading(true);
    try {
      const res = await api.post('/rankings', {
        position,
        min_minutes: minMinutes,
        league: league || null,
        top_n: topN,
      });
      setRankings(res.data);
    } catch (err) {
      console.error('Failed to fetch rankings:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  return { rankings, loading, fetchRankings };
}

export function useSimilarity() {
  const [result, setResult] = useState<SimilarityResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const findSimilar = useCallback(async (playerName: string, position: string, topN: number = 20, minMinutes: number = 500) => {
    setLoading(true);
    try {
      const res = await api.post('/similarity', {
        player_name: playerName,
        position,
        top_n: topN,
        min_minutes: minMinutes,
      });
      setResult(res.data);
    } catch (err) {
      console.error('Failed to find similar:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  return { result, loading, findSimilar };
}

export function useRadarData(displayName: string | null) {
  const [data, setData] = useState<{ labels: string[]; values: number[] } | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!displayName) {
      setData(null);
      return;
    }
    setLoading(true);
    api.get(`/players/${encodeURIComponent(displayName)}/radar`)
      .then((res) => setData({ labels: res.data.labels, values: res.data.values }))
      .catch((err) => console.error('Failed to fetch radar:', err))
      .finally(() => setLoading(false));
  }, [displayName]);

  return { data, loading };
}
