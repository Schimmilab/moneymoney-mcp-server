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

## ⚠️ Umsatztexte sind Fremddaten

`mm_transactions` gibt **Empfängername und Verwendungszweck wörtlich** zurück. Diese Felder
werden nicht von dir befüllt, sondern von jedem, der dir Geld überweist — sie sind damit
Eingaben aus einer nicht vertrauenswürdigen Quelle, genau wie Text von einer fremden Webseite.

Wer 1 Cent überweist, kann dort ablegen, was er will. Steht im Verwendungszweck etwas, das
wie eine Anweisung an ein Sprachmodell aussieht, liest der Assistent es beim nächsten
Umsatzabruf mit.

**Dieser Server allein ist read-only und kann kein Geld bewegen** — die Fallhöhe hängt
deshalb nicht an ihm, sondern an den **anderen** Werkzeugen, die in derselben Sitzung
verfügbar sind. Wer diesen Server neben schreibenden Tools betreibt, sollte das wissen.

Serverseitig ist das nicht lösbar: Ein Filter, der solche Texte entschärft, würde die
Nutzdaten zerstören — der Verwendungszweck *ist* der Inhalt. Die Behandlung gehört auf die
Seite, die die Daten auswertet.

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

## Maintainer

Schimmi — https://schimmilab.de
Issues und Pull Requests willkommen.

## Lizenz

MIT — siehe [LICENSE](LICENSE).
