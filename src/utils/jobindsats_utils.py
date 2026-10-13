ydelsesgrupper_udfaldsmål_options = [
    "Forventet andel (pct.)",
    "Faktisk andel (pct.)",
]

ydelsesgrupper_målgruppe_options = [
    "Sygedagpenge mv.",
    "Ydelsesgrupper i alt",
    "A-dagpenge mv.",
    "Kontanthjælp mv."
]

ydelser_udfaldsmål_options = [
    "Antal personer",
    "Antal fuldtidspersoner",
    "Fuldtidspersoner i pct. af arbejdsstyrken",
    "Fuldtidspersoner i pct. af befolkningen"
]

ydelser = {
    "A-Dagpenge": {"table": "jobindsats_y01a02", "periode_col": "Periode A-Dagpenge"},
    "Sygedagpenge": {"table": "jobindsats_y07a02", "periode_col": "Periode Sygedagpenge"},
    "Fleksjob": {"table": "jobindsats_y08a02", "periode_col": "Periode Fleksjob"},
    "Ledighedsydelse": {"table": "jobindsats_y09a02", "periode_col": "Periode Ledighedsydelse"},
    "Ressourceforløb": {"table": "jobindsats_y11a02", "periode_col": "Periode Ressourceforløb"},
    "Jobafklaringsforløb": {"table": "jobindsats_y12a02", "periode_col": "Periode Jobafklaringsforløb"},
}
