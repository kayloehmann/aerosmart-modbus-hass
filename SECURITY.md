# Security Policy

## Kontext

Öffentliches Repo, über HACS installierbar. Home-Assistant-Custom-Integration
für das aerosmart-Gerät, aufgesetzt auf HAs `modbus_connection`-Hub. Das
Register-Modell ist eine **vendored Kopie** von `aerosmart-modbus` (nicht als
PyPI-Dependency eingebunden, damit HACS aus diesem Repo allein installieren
kann) — siehe `custom_components/aerosmart/aerosmart_modbus/NOTICE.md`.

## Was hier als Sicherheitsproblem zählt

- **HACS-Supply-Chain**: Custom Components laufen mit vollem Zugriff auf die
  Home-Assistant-Instanz jedes Nutzers, der diese Integration installiert —
  jeder Commit auf `main` ist potenziell sofort live bei fremden Installationen.
  Entsprechend hoher Bar für Reviews auf diesem Repo.
- Die vendored Kopie des Register-Modells veraltet gegenüber
  `aerosmart-modbus` (kein automatischer Sync) — ein dort gefixtes
  `writable`/Scale-Problem bleibt hier bestehen, bis es manuell nachgezogen
  wird. Das ist ein aktiver Prozess-Risiko-Punkt, kein einmaliger Fund.
- Ein falsches Register-Schreib-Flag mit denselben physischen Folgen wie in
  `aerosmart-modbus` beschrieben (reale Heizungs-/Lüftungsanlage).
- Ein manipulierter `config_flow`, der mehr als die dokumentierten zwei
  Modbus-Unit-IDs anspricht oder Zugangsdaten anderer Hub-Integrationen
  mitliest.

## Melden

Öffentliches Solo-Repo, HACS-Nutzer außerhalb meines eigenen Haushalts sind
möglich — Issue hier öffnen, oder GitHub Private Vulnerability Reporting für
nicht-öffentliche Meldungen.

## Reaktionszusage

Ein Sync-Rückstand zur vendored `aerosmart-modbus`-Kopie oder ein falsches
Register-Flag wird als kritisch behandelt: Fix + Release vor der nächsten
HACS-Ankündigung. Bekannte Nutzer (falls über Issues identifizierbar) werden
auf den Fix hingewiesen.

## Automatisierte Härtung

Wöchentlicher `GitHub Security Sweep`: Vulnerability Alerts, Dependabot
Security Updates, Secret Scanning + Push Protection, Branch Protection auf
`main`, Private Vulnerability Reporting — alle vier Punkte aktiv (öffentliches
Repo).
