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
    "Fuldtidspersoner i pct. af arbejdsstyrken 16-66 år",
    "Fuldtidspersoner i pct. af befolkningen 16-66 år"
]

ydelser = {
    "A-Dagpenge": {"table": "jobindsats_y01a02", "periode_col": "Periode A-Dagpenge"},
    "Revalidering": {"table": "jobindsats_y04a02", "periode_col": "Periode Revalidering"},
    "Kontanthjælp": {"table": "jobindsats_y60a02", "periode_col": "Periode Kontanthjælp"},
    "Sygedagpenge": {"table": "jobindsats_y07a02", "periode_col": "Periode Sygedagppenge"},
    "Fleksjob": {"table": "jobindsats_y08a02", "periode_col": "Periode Fleksjob"},
    "Ledighedsydelse": {"table": "jobindsats_y09a02", "periode_col": "Periode Ledighedsydelse"},
    "Tilbagetrækningsydelser": {"table": "jobindsats_y10a02", "periode_col": "Periode Tilbagetrækningsydelser"},
    "Ressourceforløb": {"table": "jobindsats_y11a02", "periode_col": "Periode Ressourceforløb"},
    "Jobafklaringsforløb": {"table": "jobindsats_y12a02", "periode_col": "Periode Jobafklaringsforløb"},
    "Selvforsørgelses- og hjemrejseydelse samt overgangsydelse": {"table": "jobindsats_y35a02", "periode_col": "Periode Selvforsørgelses- og hjemrejseydelse samt overgangsyde"},
    "Uddannelseshjælp": {"table": "jobindsats_y38a02", "periode_col": "Periode Uddannelseshjælp"},
    "Barselsdagpenge": {"table": "jobindsats_y40a02", "periode_col": "Periode Barselsdagpenge"}
}
