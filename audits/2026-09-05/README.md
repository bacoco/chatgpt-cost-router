# Audit and remediation evidence

The original audit examined all 13 files at commit
`ca763e51842cb1b53452fb41464232600572c6cd`. Its report, dashboard and ZIP are
preserved byte for byte. Their findings describe that historical revision.

| File | Meaning |
|---|---|
| [original-audit.md](original-audit.md) | Complete original findings and coverage |
| [original-shipguard.html](original-shipguard.html) | Original standalone ShipGuard review; download to open |
| [original-audit-evidence.zip](original-audit-evidence.zip) | Original evidence and verification bundle |
| [REMEDIATION.md](REMEDIATION.md) | Every finding and design obligation mapped to its resolution |
| [regressions-before.txt](regressions-before.txt) | Executed regression failures against the original contracts |
| [tests-after.txt](tests-after.txt) | Executed tests against the remediated implementation |
| [verification.json](verification.json) | Final measured checks, independent review and limitations |

The original audit distinguished executable defects, specification gaps and
future integration obligations. The remediation retains that distinction.
Synthetic examples and fixtures are not live capability evidence, authorization,
provider prices or measured savings. GitHub Actions supplies continuing validation
for subsequent changes; these files are a dated record.
