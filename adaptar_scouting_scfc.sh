#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════
# SCRIPT 1/2 — ADAPTAÇÃO scouting_scfc → SANTA CRUZ FC (Série C)
# ═══════════════════════════════════════════════════════════════════════
# ONDE RODAR: Terminal do GitHub Codespace do repo scouting_scfc
#   1. Abra github.com/wiilbarreto/scouting_scfc
#   2. Aperte "." (ponto) para abrir github.dev  OU  abra um Codespace
#   3. Abra o terminal (Ctrl+`) e cole este script inteiro
# ═══════════════════════════════════════════════════════════════════════

set -e

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  SCOUTING_SCFC → SANTA CRUZ FC                          ║"
echo "╚══════════════════════════════════════════════════════════╝"

# ── VARIÁVEIS ──────────────────────────────────────────────────────────
LOGO_URL="https://cdn-img.zerozero.pt/img/logos/equipas/2253_imgbank_1683641104.png"
NEW_LOGO="2253_imgbank_1683641104.png"
OLD_LOGO="3154_imgbank_1685113109.png"

# ══════════════════════════════════════════════════════════════════════
# FASE 1 — LOGO
# ══════════════════════════════════════════════════════════════════════
echo ""
echo "━━━ FASE 1: Logo ━━━"
curl -sL "$LOGO_URL" -o "frontend/public/$NEW_LOGO"
rm -f "frontend/public/$OLD_LOGO"
echo "✓ Logo trocada"

# ══════════════════════════════════════════════════════════════════════
# FASE 2 — frontend/index.html (favicon + título)
# ══════════════════════════════════════════════════════════════════════
echo ""
echo "━━━ FASE 2: index.html ━━━"
sed -i "s|$OLD_LOGO|$NEW_LOGO|g" frontend/index.html
sed -i 's|Scouting | Botafogo SA|Scouting | Santa Cruz FC|g' frontend/index.html
sed -i "s|https://cdn-img.zerozero.pt/img/logos/equipas/3154_imgbank_1685113109.png|/$NEW_LOGO|g" frontend/index.html
echo "✓ index.html atualizado"

# ══════════════════════════════════════════════════════════════════════
# FASE 3 — LoginPage.tsx (6 branding + 2 heráldica)
# ══════════════════════════════════════════════════════════════════════
echo ""
echo "━━━ FASE 3: LoginPage.tsx ━━━"
FILE="frontend/src/components/LoginPage.tsx"

# Branding
sed -i "s|$OLD_LOGO|$NEW_LOGO|g" "$FILE"
sed -i 's|Logo Botafogo-SA|Logo Santa Cruz FC|g' "$FILE"
sed -i 's|SCOUTING BFSA|SCOUTING SCFC|g' "$FILE"
sed -i 's|Plataforma de Analise de Jogadores|Departamento de Scouting — Série C|g' "$FILE"
sed -i 's|admin@botafogo-sp.com|adscfc@santacruz.com|g' "$FILE"
sed -i 's|Botafogo Futebol SA — Departamento de Scouting|Santa Cruz FC — Departamento de Scouting|g' "$FILE"

# Heráldica: vermelho nunca toca preto
sed -i 's|rgba(227, 6, 19, 0.06)|rgba(161, 161, 170, 0.06)|g' "$FILE"
sed -i 's|rgba(227, 6, 19, 0.4)|rgba(161, 161, 170, 0.5)|g' "$FILE"
echo "✓ LoginPage.tsx (6 branding + 2 heráldica)"

# ══════════════════════════════════════════════════════════════════════
# FASE 4 — Layout.tsx (4 branding + heráldica sidebar)
# ══════════════════════════════════════════════════════════════════════
echo ""
echo "━━━ FASE 4: Layout.tsx ━━━"
FILE="frontend/src/components/Layout.tsx"

# Branding
sed -i "s|$OLD_LOGO|$NEW_LOGO|g" "$FILE"
sed -i 's|Logo Botafogo-SP|Logo Santa Cruz FC|g' "$FILE"
sed -i 's|BOTAFOGO-SA|SANTA CRUZ FC|g' "$FILE"
sed -i 's|SCOUTING BFSA|SCOUTING SCFC|g' "$FILE"

# Heráldica: sidebar indicator — adiciona outline cinza ao vermelho
sed -i "s|style={{ background: 'var(--color-accent)' }}|style={{ background: 'var(--color-accent)', outline: '1px solid var(--color-accent-outline)' }}|g" "$FILE"
echo "✓ Layout.tsx (4 branding + heráldica)"

# ══════════════════════════════════════════════════════════════════════
# FASE 5 — index.css (comentário + 8 heráldica + 2 variáveis novas)
# ══════════════════════════════════════════════════════════════════════
echo ""
echo "━━━ FASE 5: index.css ━━━"
FILE="frontend/src/index.css"

# Comentário
sed -i 's|Botafogo Red|Santa Cruz Red|g' "$FILE"

# Heráldica: glows e bordas vermelhas → cinza neutro
sed -i 's|--color-accent-glow: rgba(227, 6, 19, 0.12);|--color-accent-glow: rgba(160, 160, 170, 0.12);|g' "$FILE"
sed -i 's|--color-accent-glow: rgba(200, 5, 15, 0.10);|--color-accent-glow: rgba(100, 100, 110, 0.10);|g' "$FILE"
sed -i 's|border: 1px solid rgba(227, 6, 19, 0.18);|border: 1px solid rgba(180, 180, 190, 0.22);|g' "$FILE"
sed -i 's|0 0 32px rgba(227, 6, 19, 0.05);|0 0 32px rgba(180, 180, 190, 0.06);|g' "$FILE"
sed -i 's|border-color: rgba(200, 5, 15, 0.12);|border-color: rgba(100, 100, 110, 0.15);|g' "$FILE"
sed -i 's|0 0 24px rgba(200, 5, 15, 0.03);|0 0 24px rgba(100, 100, 110, 0.04);|g' "$FILE"
sed -i 's|border: 2px solid var(--color-accent);|border: 2px solid var(--color-text-secondary);|g' "$FILE"
sed -i 's|border-top-color: var(--color-accent);|border-top-color: var(--color-text-secondary);|g' "$FILE"

# Adicionar variáveis heráldicas no bloco @theme (após --color-border-active)
sed -i '/--color-border-active/a\    --color-accent-buffer: #71717A;\n    --color-accent-outline: rgba(161, 161, 170, 0.35);' "$FILE"

# Adicionar no bloco light theme (após --color-border-active do light)
# Buscar a segunda ocorrência de --color-border-active (que está no light theme)
python3 -c "
import re
with open('$FILE', 'r') as f:
    content = f.read()
# Encontrar a segunda ocorrência de --color-border-active e adicionar após ela
parts = content.split('--color-border-active')
if len(parts) >= 3:
    # Inserir após a segunda ocorrência (no bloco light)
    line_end = parts[2].index(';') + 1
    parts[2] = parts[2][:line_end] + '\n    --color-accent-buffer: #52525B;\n    --color-accent-outline: rgba(82, 82, 91, 0.30);' + parts[2][line_end:]
    content = '--color-border-active'.join(parts)
    with open('$FILE', 'w') as f:
        f.write(content)
    print('  ✓ Variáveis light theme adicionadas')
else:
    print('  ⚠ Bloco light theme não encontrado (adicionar manualmente)')
" 2>/dev/null || echo "  ⚠ Python3 não disponível — adicionar variáveis light manualmente"

echo "✓ index.css (1 comentário + 8 heráldica + variáveis buffer)"

# ══════════════════════════════════════════════════════════════════════
# FASE 6 — Heráldica em SkillCornerPage.tsx e PlayerProfile.tsx
# ══════════════════════════════════════════════════════════════════════
echo ""
echo "━━━ FASE 6: Heráldica nos .tsx restantes ━━━"

# SkillCornerPage.tsx
if [ -f "frontend/src/pages/SkillCornerPage.tsx" ]; then
    sed -i "s|rgba(227,6,19,0.25)|var(--color-accent-outline)|g" frontend/src/pages/SkillCornerPage.tsx
    sed -i "s|rgba(227,6,19,0.2)|var(--color-accent-outline)|g" frontend/src/pages/SkillCornerPage.tsx
    sed -i "s|rgba(227,6,19,0.1)|var(--color-accent-outline)|g" frontend/src/pages/SkillCornerPage.tsx
    sed -i "s|rgba(227, 6, 19, 0.25)|var(--color-accent-outline)|g" frontend/src/pages/SkillCornerPage.tsx
    sed -i "s|rgba(227, 6, 19, 0.2)|var(--color-accent-outline)|g" frontend/src/pages/SkillCornerPage.tsx
    sed -i "s|rgba(227, 6, 19, 0.1)|var(--color-accent-outline)|g" frontend/src/pages/SkillCornerPage.tsx
    echo "✓ SkillCornerPage.tsx heráldica"
fi

# PlayerProfile.tsx
if [ -f "frontend/src/pages/PlayerProfile.tsx" ]; then
    sed -i "s|rgba(227, 6, 19, 0.3)|var(--color-accent-outline)|g" frontend/src/pages/PlayerProfile.tsx
    sed -i "s|rgba(227,6,19,0.3)|var(--color-accent-outline)|g" frontend/src/pages/PlayerProfile.tsx
    echo "✓ PlayerProfile.tsx heráldica"
fi

# ══════════════════════════════════════════════════════════════════════
# FASE 7 — backend/auth.py (credenciais)
# ══════════════════════════════════════════════════════════════════════
echo ""
echo "━━━ FASE 7: auth.py ━━━"
sed -i 's|scouting-bfsa-secret-key-change-in-production|scouting-scfc-secret-key-change-in-production|g' backend/auth.py
sed -i 's|botafogo2024|scfc1914|g' backend/auth.py
sed -i 's|admin@botafogo-sp.com|adscfc@santacruz.com|g' backend/auth.py
sed -i 's|caiofelipead@gmail.com|adscfc@santacruz.com|g' backend/auth.py
sed -i 's|bfsa2026|scfc1914|g' backend/auth.py
sed -i 's|Caio Felipe|Admin SCFC|g' backend/auth.py
echo "✓ auth.py (6 substituições)"

# ══════════════════════════════════════════════════════════════════════
# FASE 8 — backend/services/sync_sheets.py (SUBSTITUIÇÃO TOTAL)
# ══════════════════════════════════════════════════════════════════════
echo ""
echo "━━━ FASE 8: sync_sheets.py (reescrita total) ━━━"

cat > backend/services/sync_sheets.py << 'SYNC_EOF'
"""
sync_sheets.py — Sync Google Sheets → Neon PostgreSQL.
Adaptado para Santa Cruz FC — Série C.
Puxa CSVs públicos do Google Sheets e faz upsert no banco.
"""

import os
import io
import logging
import urllib.request
from typing import Dict

import pandas as pd

from services.database import init_scouting_tables, upsert_sheet_data, get_sync_status

logger = logging.getLogger(__name__)

# ── Planilhas do Santa Cruz FC (CSV público) ──────────────────────────
SHEET_CADASTRO_URL = os.environ.get(
    "SHEET_CADASTRO_URL",
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vRc74viAa9e3hBoS6HqM7wU4iOM9jq4Jt9JoJvdNH8ahKIQr_3dcdFj9NbXIeYFQw/pub?output=csv"
)

SHEET_FILTROS_URL = os.environ.get(
    "SHEET_FILTROS_URL",
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vQNdzRzcdNsGdRv3qQ2sud5trZLSCEl5mB0HLfGVqVMITrq1YdW7nKDKTQDAmQbqSYQkDzy69haWxlf/pub?output=csv"
)

GOOGLE_SHEET_ID = os.environ.get("GOOGLE_SHEET_ID", "")

SHEET_URLS = {
    "cadastro": SHEET_CADASTRO_URL,
    "oferecidos": SHEET_FILTROS_URL,
}

SHEET_NAMES = {
    "analises": "Análises",
    "oferecidos": "Oferecidos",
    "skillcorner": "SkillCorner",
    "wyscout": "WyScout",
}


def _download_csv_public(url: str, label: str) -> pd.DataFrame:
    """Download CSV público direto do Google Sheets."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read().decode("utf-8")
        df = pd.read_csv(io.StringIO(raw), dtype=str, na_values=["", "-", "N/A", "nan"])
        logger.info("Downloaded '%s': %d rows x %d cols", label, len(df), len(df.columns))
        return df
    except Exception as e:
        logger.error("Failed to download '%s': %s", label, e)
        return pd.DataFrame()


def _download_sheet_csv(sheet_id: str, sheet_name: str) -> pd.DataFrame:
    """Download a single Google Sheet tab as CSV → DataFrame (via gviz)."""
    import urllib.parse
    encoded = urllib.parse.quote(sheet_name)
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={encoded}"
    return _download_csv_public(url, sheet_name)


def sync_all_sheets() -> Dict[str, int]:
    """Sync all sheets → Neon PostgreSQL."""
    init_scouting_tables()
    results = {}

    # 1. Sync planilhas públicas diretas (cadastro + filtros)
    for key, url in SHEET_URLS.items():
        try:
            df = _download_csv_public(url, key)
            count = upsert_sheet_data(key, df)
            results[key] = count
        except Exception as e:
            logger.error("Sync failed for '%s': %s", key, e)
            results[key] = -1

    # 2. Sync abas gviz (se GOOGLE_SHEET_ID configurado)
    if GOOGLE_SHEET_ID:
        for key, sheet_name in SHEET_NAMES.items():
            if key in results:
                continue
            try:
                df = _download_sheet_csv(GOOGLE_SHEET_ID, sheet_name)
                count = upsert_sheet_data(key, df)
                results[key] = count
            except Exception as e:
                logger.error("Sync failed for '%s': %s", key, e)
                results[key] = -1

    logger.info("Sync complete: %s", results)
    return results


def sync_single_sheet(sheet_key: str) -> int:
    """Sync a single sheet by key."""
    init_scouting_tables()

    if sheet_key in SHEET_URLS:
        df = _download_csv_public(SHEET_URLS[sheet_key], sheet_key)
        return upsert_sheet_data(sheet_key, df)

    if GOOGLE_SHEET_ID:
        sheet_name = SHEET_NAMES.get(sheet_key)
        if not sheet_name:
            raise ValueError(f"Unknown sheet key: {sheet_key}")
        df = _download_sheet_csv(GOOGLE_SHEET_ID, sheet_name)
        return upsert_sheet_data(sheet_key, df)

    raise ValueError(f"No URL or SHEET_ID configured for: {sheet_key}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    results = sync_all_sheets()
    print(f"Sync results: {results}")
    status = get_sync_status()
    print(f"Sync status: {status}")
SYNC_EOF

echo "✓ sync_sheets.py reescrito"

# ══════════════════════════════════════════════════════════════════════
# FASE 9 — backend/main.py (referências textuais — ORDEM IMPORTA)
# ══════════════════════════════════════════════════════════════════════
echo ""
echo "━━━ FASE 9: main.py ━━━"
# ORDEM CRÍTICA: mais específico primeiro
sed -i 's|Botafogo-SP|Santa Cruz FC|g' backend/main.py
sed -i 's|Botafogo|Santa Cruz|g' backend/main.py
sed -i 's|BFSA|SCFC|g' backend/main.py
echo "✓ main.py (3 substituições na ordem correta)"

# ══════════════════════════════════════════════════════════════════════
# FASE 10 — GIT COMMIT
# ══════════════════════════════════════════════════════════════════════
echo ""
echo "━━━ FASE 10: Commit ━━━"
git add -A
git commit -m "Adaptar sistema para Santa Cruz FC (Série C)

- Identidade visual: logo, favicon, textos
- Autenticação: login adscfc@santacruz.com / scfc1914
- Planilhas: sync_sheets.py reescrito para CSVs públicos
- Correção heráldica: vermelho nunca toca preto/branco (buffers cinza)
- Referências: Botafogo-SP → Santa Cruz FC, BFSA → SCFC"

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  ✅ scouting_scfc ADAPTADO COM SUCESSO                  ║"
echo "║                                                          ║"
echo "║  Para enviar ao GitHub:  git push                        ║"
echo "║  Login: adscfc@santacruz.com / scfc1914                  ║"
echo "╚══════════════════════════════════════════════════════════╝"
