# Build og status

Kør fra repo-roden:

```powershell
py tools\build.py
py -m unittest discover -s tools -p test_build.py -v
py -m http.server 8000 --directory _site
```

`project.json` er kilden til release, gennemgangsdato, historiske commits og
bevisstatus. `site_copy` samler de fælles statusformuleringer. Behold de historiske
testdatoer, når kun hjemmesidens gennemgangsdato ændres. Produktpåstande og
bevisstatus skal fortsat være dokumenterede og godkendte.

Siderne ligger i `templates/`. Markører som `{{ latest_release.version }}` og
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
