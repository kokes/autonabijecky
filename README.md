# Git scraping elektro nabijíček pro auta

Poznámky:
- stahujem data od jednotlivých poskytovatelů, takže pokrytí celkem nízký (byť používáme ty největší)
- chtěl jsem použít [fDrive](https://fdrive.cz/data/export/pub/charging-stations.json), ale nejde tam rozlišit mezi českýma a zahraničníma (a s polygonama si hrát nechci)
- chtěl jsem použít [nabijto.cz](https://www.nabijto.cz/api/chargers), ale vypadá to celkem neaktualizovaně
- rád bych
  - přidal diff, který se propíše do commit message (např. "4 nové ČEZ nabíječky, jedna PRE zrušena")
  - spočítal nabíjecí body, ne jen nabíječky
