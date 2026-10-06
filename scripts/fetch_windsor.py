"""Busca os dados de Meta Ads da conta Lopes ABC no Windsor.ai e grava em data.json.

Roda no GitHub Actions (ver .github/workflows/atualizar-dados.yml).
A chave da API vem do secret WINDSOR_API_KEY — nunca coloque a chave no código.
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

ACCOUNT_ID = "854204220059560"  # Lopes ABC (Meta Ads)
FIELDS = [
    "date",
    "campaign",
    "adset_name",
    "ad_name",
    "spend",
    "impressions",
    "reach",
    "clicks",
    "actions_lead",
]
DATE_PRESET = os.environ.get("WINDSOR_DATE_PRESET", "last_90d")
OUT = os.path.join(os.path.dirname(__file__), "..", "data.json")


def main() -> int:
    api_key = (os.environ.get("WINDSOR_API_KEY") or "").strip()
    if not api_key:
        print("::error::WINDSOR_API_KEY não definido")
        return 1

    params = urllib.parse.urlencode({
        "api_key": api_key,
        "date_preset": DATE_PRESET,
        "fields": ",".join(FIELDS),
        "select_accounts": ACCOUNT_ID,
    })
    url = f"https://connectors.windsor.ai/facebook?{params}"

    try:
        with urllib.request.urlopen(url, timeout=120) as resp:
            payload = json.load(resp)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:800]
        print(f"::error::ERRO Windsor HTTP {e.code}: {body}")
        return 1
    except Exception as e:  # rede, timeout, JSON inválido
        print(f"::error::ERRO ao chamar o Windsor: {type(e).__name__}: {e}"[:800])
        return 1

    rows = payload.get("data", payload) if isinstance(payload, dict) else payload
    if not isinstance(rows, list):
        print(f"::error::Resposta inesperada do Windsor: {str(payload)[:500]}")
        return 1
    if not rows:
        # Não sobrescreve dados bons com um retorno vazio (falha temporária da API).
        print("Windsor retornou 0 linhas; mantendo data.json anterior")
        return 0

    out = {
        "atualizado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "conta": "Lopes ABC",
        "periodo": DATE_PRESET,
        "linhas": rows,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"{len(rows)} linhas gravadas em data.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
