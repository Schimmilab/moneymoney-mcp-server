# MoneyMoney MCP Server (read-only)

Liest Konten, Umsätze, Depot und Kategorien aus **MoneyMoney** über dessen
offizielle AppleScript-Schnittstelle. **MoneyMoney hält die Bank-Credentials —
dieser Server liest nur** (kein Schreiben, keine TAN, keine FinTS-Eigenimplementierung).
Gleiches Muster wie der things3-MCP.

## Voraussetzung (wichtig)

MoneyMoney.app muss **laufen** und die **Datenbank entsperrt** sein — die
Export-Befehle scheitern bei gesperrter DB. Daher **interaktiv**, nicht headless/Cron.

## Tools (alle read-only)

| Tool | Zweck |
|---|---|
| `mm_accounts` | Konten + Salden, Währung, Typ, IBAN, uuid |
| `mm_transactions(account, from_date, to_date?)` | Umsätze eines Kontos im Datumsbereich (ISO `YYYY-MM-DD`) |
| `mm_portfolio(account)` | Wertpapiere/Edelmetalle eines Depot-Kontos (Konto-Name aus `mm_accounts`) |
| `mm_categories` | Kategorienbaum |

Icons/Binärdaten werden aus dem Export gestrippt, damit die Ausgabe schlank bleibt.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Registrieren

```bash
claude mcp add moneymoney -- ~/workspace/moneymoney-mcp-server/.venv/bin/python \
  ~/workspace/moneymoney-mcp-server/moneymoney_mcp.py
```

Danach Claude-Code neu starten; MoneyMoney offen + entsperrt halten.
