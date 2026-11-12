# Kaliv — projektsiden kaliv.dk

Dette repository indeholder den offentlige projektside for **Kaliv** og **ModelRig**: [kaliv.dk](https://kaliv.dk/) (dansk) og [kaliv.dk/en/](https://kaliv.dk/en/) (engelsk).

Kaliv er én personlig AI på tværs af Windows, Android, hjemmet (KalivHub) og VR (Quest). ModelRig er den lokale infrastruktur, der holder identitet, hukommelse og tilladelser. Siden forklarer projektet og skelner mellem det, der er udgivet, det der er set på rigtig hardware, og det der stadig mangler bevis.

Repoet er kun websitet. Produktets kode ligger i de repositories, der står under [Relaterede repositories](#relaterede-repositories).

## Sider

Siderne ligger som skabeloner i `templates/` og bygges til `_site/`:

| Skabelon | Indhold |
|---|---|
| `templates/index.html` | Forside |
| `templates/brief.html` | Projektbrief |
| `templates/hub.html` | KalivHub — Kaliv i hjemmet |
| `templates/architecture.html` | Systemarkitektur |
| `templates/proofs.html` | V1-bevisregister |
| `templates/progress.html` | Status |
| `templates/download.html` | Windows-/Android-downloads og SHA-256-kontrol |
| `templates/404.html` | Fejlside |
| `templates/offline.html` | Vises af service workeren uden forbindelse |

## Øvrige filer

| Fil | Rolle |
|---|---|
| `project.json` | Statuskilden: release, gennemgangsdato, commits, bevisstatus og de fælles statusformuleringer (`site_copy`). Buildet skriver også det offentlige manifest herfra |
| `templates/llms.txt`, `templates/sitemap.xml` | Tekstoversigt til sprogmodeller og sitemap, genereret fra statuskilden |
| `templates/service-worker.js` | Cache og offline-side. Cache-navn og precache-liste genereres af buildet |
| `templates/partials/` | Fælles brand, navigation, header og footer med forsiden som layoutvariant |
| `site.css` | Ét stylesheet med fælles regler og afgrænsede sidevarianter |
| `site.js` | Lille bootstrap til service worker, offline og kompatibilitet |
| `robots.txt`, `site.webmanifest`, `CNAME` | Indeksering, webapp-metadata og domæne |
| `assets/` | Hero-billede i tre størrelser, Kaliv-ankh og ikoner |
| `tools/build.py` | Buildet. Kun Pythons standardbibliotek |
| `tools/test_build.py` | Tests af status, fælles komponenter, statisk engelsk og indholdshash |
| `tools/check-release.py`, `tools/test_release.py` | Ugentlig kontrol af seneste ModelRig-release og tests af rapporteringen |
| `tools/check-site.mjs` | Kontrol af det byggede site i CI |
| `docs/qa/issue-6/` | Målinger og skærmbilleder fra rettelserne i [issue #6](https://github.com/Ternedal/Kaliv/issues/6) |

Sitet har ingen eksterne ressourcer, og buildet har ingen afhængigheder ud over Python 3. [`tools/README.md`](tools/README.md) beskriver markører og filtre i skabelonerne.

## Sprog

Dansk og engelsk bygges fra samme skabelon: dansk til `/` og engelsk til `/en/`. Begge sprog har færdig HTML, almindelige sprog-links og metadata på sidens sprog og virker uden JavaScript. Gamle `?lang=en`-links viderestilles med JavaScript; øvrige query-parametre og fragmentet bevares.

Når du ændrer en tekst, skal både elementets indhold (dansk) og `data-en` rettes. Attributoversættelser som `data-en-aria-label` og `data-en-content` bygges på samme måde. Oversættelsesattributterne findes kun i skabelonerne.

## Opdatering af status

Ret status ét sted: `project.json`. Release, gennemgangsdato, commit-snapshot og bevisstatus hentes derfra til alle sider, `llms.txt`, sitemap og JSON-LD, når sitet bygges. En ukendt markør i en skabelon stopper buildet.

Hent version, datoer og commit-id'er fra GitHub, når du retter dem. Behold de historiske testdatoer, når kun gennemgangsdatoen ændres. Siden må ikke beskrive noget som bevist, før beviset findes.

`downloads` samler filnavne og links til den gennemgåede release. Kontrollér dem
mod releasens Assets og `SHA256SUMS.txt`, når versionen ændres. Downloadsidens
fil-links følger den viste version; linket til seneste udgivelse peger altid på
GitHubs `releases/latest`. KalivNexus og LanguageRig beskrives i manifestet og
`llms.txt` med deres aktuelle grænser, adskilt fra V1-beviserne.

## Cache

Der er ingen versionsnumre at vedligeholde. Buildet giver CSS, JavaScript, billeder og manifest en indholdshash i deres URL, og service workerens cache-navn følger det samlede output.

## Build og lokal visning

```bash
python3 tools/build.py
python3 -m unittest discover -s tools -p 'test_*.py' -v
python3 -m http.server 8000 --directory _site
```

På Windows kan de samme kommandoer køres med `py` i stedet for `python3`; se [statusvejledningen](tools/README.md).

Åbn `http://localhost:8000/` og `http://localhost:8000/en/`. `_site/` er genereret og committes ikke. Ryd sitets data i browseren, hvis du ser en gammel version; service workeren gemmer filerne.

## Publicering

Hvert push til `main` kører `.github/workflows/pages.yml`. Den bygger med `tools/build.py` og publicerer kun `_site/` til GitHub Pages på domænet i `CNAME` (kaliv.dk). Skabeloner, værktøjer og denne README publiceres ikke.

`.github/workflows/site-checks.yml` kører på hver pull request og på `main`: build og tests, markup, links, visning ved flere skærmbredder, tilgængelighed, cache og Lighthouse. Rapporterne ligger som artefakt på kørslen.

`.github/workflows/release-drift.yml` sammenligner statusfilen med seneste offentlige ModelRig-release hver mandag kl. 07.20 UTC. Ved afvigelse opretter eller opdaterer den én opgave fra GitHub Actions; den ændrer ikke indhold eller bevisstatus. Den kan også startes manuelt, med eller uden oprettelse af opgaven. API-fejl får kørslen til at fejle frem for at blive rapporteret som ajourført.

Planen for sitet og det, der mangler, står i [issue #6](https://github.com/Ternedal/Kaliv/issues/6).

## Relaterede repositories

| Repository | Rolle |
|---|---|
| [ModelRig](https://github.com/Ternedal/ModelRig) | Backend og kontrolplan samt Kaliv-klienterne til Android, Windows og VR |
| [VoiceRig](https://github.com/Ternedal/VoiceRig) | Stemme: bygger `.mrvoice`-stemmeprofiler og leverer lokal tale til ModelRig |
| [BodyRig](https://github.com/Ternedal/BodyRig) | Krop: `.mrbody`-pakker, bevægelse og klon-pipeline |
| [VisionRig](https://github.com/Ternedal/VisionRig) | Syn: kamera- og sensorinput omsat til strukturerede observationer |
| [LanguageRig](https://github.com/Ternedal/LanguageRig) | Tilpasning og evaluering af dansk sprogmodel |
| [KalivNexus](https://github.com/Ternedal/KalivNexus) | Register over eksterne API-kapabiliteter; endnu ikke koblet til ModelRig |
| [KalivHub](https://github.com/Ternedal/KalivHub) | Hjemmeklienten: Home Assistant og Cast til Nest Hub (privat repository) |
| [KalivHub-Receiver](https://github.com/Ternedal/KalivHub-Receiver) | Cast-modtageren, der vises på Nest Hub |
| [SkyPlayer-Engine](https://github.com/Ternedal/SkyPlayer-Engine) | Unity/OpenXR-pakke til afspilning og passthrough i Kaliv VR |

Systemets ansvarsfordeling er defineret i [ModelRig: docs/KALIV_SYSTEM_DEFINITION.md](https://github.com/Ternedal/ModelRig/blob/main/docs/KALIV_SYSTEM_DEFINITION.md).

## Licens

Se [LICENSE](LICENSE).
