# Build og status

Kør fra repo-roden:

```powershell
py tools\build.py
py -m unittest discover -s tools -p "test_*.py" -v
py -m http.server 8000 --directory _site
```

`project.json` er kilden til release, gennemgangsdato, historiske commits og
bevisstatus. `site_copy` samler de fælles statusformuleringer. Behold de historiske
testdatoer, når kun hjemmesidens gennemgangsdato ændres. Produktpåstande og
bevisstatus skal fortsat være dokumenterede og godkendte.

Siderne ligger i `templates/`. Fælles elementer hentes med `{% include "header" %}` fra `templates/partials/`. Headerens sidetitel og aktive navigation vælges af buildet. Forsiden har sin egen layoutvariant med samme brand og navigationslinks. Alle sider bruger `site.css`; `:where(...)` afgrænser varianterne uden at øge selectorernes specificitet. Ukendte eller cirkulære includes stopper buildet.

 Markører som `{{ latest_release.version }}` og
`{{ updated | date_da }}` henter værdier fra statuskilden. `short`, `date_en`,
`capitalize`, `lower` og `json` er også understøttet. HTML og attributter escapes;
`json` bruges til JavaScript-værdier. Ukendte markører stopper buildet.

Buildet genererer sider, llms.txt, sitemap, JSON-LD og det offentlige project.json
til `_site/`. Det offentlige manifest indeholder opløste værdier. `site_copy`
bruges kun under buildet. Kildeskabeloner og værktøjer publiceres ikke.

Dansk og engelsk genereres fra de samme skabeloner. Dansk står i elementets tekst;
`data-en` og fx `data-en-aria-label` angiver den engelske værdi. Buildet fjerner
oversættelsesattributterne og skriver færdig HTML til `/` og `/en/`, inklusive
metadata, lokale links og sprogkontroller. Begge sprog virker uden JavaScript.
Gamle `?lang=en`-links viderestilles med et lille script, som bevarer øvrige
query-parametre og fragmentet. De gamle script-URL'er bevares som kompatibilitet
for allerede cachede sider; `site.js` håndterer kun offline og service worker.

CSS, JavaScript, billeder og manifest får indholdshash i deres URL. Workerens
cache-navn afhænger af det samlede output og worker-skabelonen. Precache-listen
genereres fra den eksplicitte publiceringsliste og de små ikoner. Der skal ikke
længere vedligeholdes `vXX`-numre. Workerens URL er uændret, og gamle side-links
virker fortsat. Nye engelske links peger direkte på `/en/`.

GitHub Pages bygger med samme Python-script og publicerer kun `_site/`.
Genereret output committes ikke. Buildet har ingen eksterne afhængigheder.

## Opdatér en dokumenteret status

1. Kontrollér seneste offentlige release og de relevante PR'er/commits på GitHub.
   `py tools\check-release.py` sammenligner release-versionen uden at skrive noget.
2. Ret `project.json`: `latest_release` for release, `updated` for datoen for den
   faktiske indholdsgennemgang, `source_snapshot.heads` for historiske commits og
   `v1_proofs` for dokumenterede beviser. Behold historiske testdatoer. Et merge
   eller en udgivelse ændrer ikke automatisk et bevis fra `open` til `closed`.
3. Kør build og tests som vist øverst. Se både dansk og engelsk i den lokale
   forhåndsvisning, inklusive statuskort og metadata. Ret fælles statusformuleringer
   i `site_copy`, hvis de faktiske forhold kræver en ny tekst.
4. Opret en PR med kilderne til ændrede påstande. Produktindhold følger
   indholdsgodkendelsen i issue #6. Merge først, når CI og godkendelserne er på plads.
   Kontrollér derefter det publicerede `project.json` og de berørte sider.

## Ugentlig releasekontrol

`release-drift.yml` kører mandag kl. 07.20 UTC og kan startes manuelt i Actions.
Den kører også på main, når selve tjekket eller dets workflow ændres, så den
faktiske integration kontrolleres ved publicering af rettelser til tjekket.
Den opretter eller opdaterer en enkelt bot-opgave ved afvigelse. Gentagne kørsler
med samme afvigelse skriver ikke igen. Personers opgaver ændres ikke. En løst
opgave lukkes som del af den dokumenterede indholdsgennemgang.

Scriptet skriver som standard ikke til GitHub. `--write` kræver `GITHUB_TOKEN`
med adgang til issues i `GITHUB_REPOSITORY`. Workflowet giver kun sit isolerede
releasejob denne skriveret; PR-kontrollen har fortsat kun læseadgang. Ved API-fejl
fejler kørslen. Der er ingen automatisk opdatering af release, datoer eller beviser.
