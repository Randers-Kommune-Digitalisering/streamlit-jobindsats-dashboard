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
    "Kontanthjælp(Satser)": {"table": "jobindsats_y60a02satsery60a02", "periode_col": "Periode Kontanthjælp (satser)"},
    "Sygedagpenge": {"table": "jobindsats_y07a02", "periode_col": "Periode Sygedagpenge"},
    "Fleksjob": {"table": "jobindsats_y08a02", "periode_col": "Periode Fleksjob"},
    "Ledighedsydelse": {"table": "jobindsats_y09a02", "periode_col": "Periode Ledighedsydelse"},
    "Tilbagetrækningsydelser": {"table": "jobindsats_y10a02", "periode_col": "Periode Tilbagetrækningsydelser"},
    "Ressourceforløb": {"table": "jobindsats_y11a02", "periode_col": "Periode Ressourceforløb"},
    "Jobafklaringsforløb": {"table": "jobindsats_y12a02", "periode_col": "Periode Jobafklaringsforløb"},
    "Barselsdagpenge": {"table": "jobindsats_y40a02", "periode_col": "Periode Barselsdagpenge"}
}
