# Kaliv — projektsiden kaliv.dk

Dette repository indeholder den offentlige projektside for **Kaliv** og **ModelRig**: [kaliv.dk](https://kaliv.dk/) (dansk) og [kaliv.dk/?lang=en](https://kaliv.dk/?lang=en) (engelsk).

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
| `templates/404.html` | Fejlside |
| `templates/offline.html` | Vises af service workeren uden forbindelse |

## Øvrige filer

| Fil | Rolle |
|---|---|
| `project.json` | Statuskilden: release, gennemgangsdato, commits, bevisstatus og de fælles statusformuleringer (`site_copy`). Buildet skriver også det offentlige manifest herfra |
| `templates/llms.txt`, `templates/sitemap.xml` | Tekstoversigt til sprogmodeller og sitemap, genereret fra statuskilden |
| `templates/service-worker.js` | Cache og offline-side. Cache-navn og precache-liste genereres af buildet |
| `templates/proofs.js` | Script til bevisregisteret, med værdier fra statuskilden |
| `home.css`, `home.js` | Forsidens stylesheet og sprogskift |
| `dossier.css`, `dossier.js` | Stylesheet og sprogskift for `brief.html` og `hub.html` |
| `site-shell.css` | Fælles header og footer på undersiderne |
| `architecture.js`, `progress.js` | Sprogskift for arkitektur- og statussiden |
| `robots.txt`, `site.webmanifest`, `CNAME` | Indeksering, webapp-metadata og domæne |
| `assets/` | Hero-billede i tre størrelser, Kaliv-ankh og ikoner |
| `tools/build.py` | Buildet. Kun Pythons standardbibliotek |
| `tools/test_build.py` | Tests af statusgenerering og indholdshash |
| `tools/check-site.mjs` | Kontrol af det byggede site i CI |
| `docs/qa/issue-6/` | Målinger og skærmbilleder fra rettelserne i [issue #6](https://github.com/Ternedal/Kaliv/issues/6) |

Sitet har ingen eksterne ressourcer, og buildet har ingen afhængigheder ud over Python 3. [`tools/README.md`](tools/README.md) beskriver markører og filtre i skabelonerne.

## Sprog

Dansk er standard og står direkte i HTML'en. Den engelske tekst står i `data-en`-attributter på de samme elementer, og et script bytter teksten, når adressen har `?lang=en`. Uden JavaScript vises siden derfor altid på dansk.

Når du ændrer en tekst, skal både elementets indhold (dansk) og `data-da`/`data-en` rettes.

## Opdatering af status

Ret status ét sted: `project.json`. Release, gennemgangsdato, commit-snapshot og bevisstatus hentes derfra til alle sider, `llms.txt`, sitemap og JSON-LD, når sitet bygges. En ukendt markør i en skabelon stopper buildet.

Hent version, datoer og commit-id'er fra GitHub, når du retter dem. Behold de historiske testdatoer, når kun gennemgangsdatoen ændres. Siden må ikke beskrive noget som bevist, før beviset findes.

## Cache

Der er ingen versionsnumre at vedligeholde. Buildet giver CSS, JavaScript, billeder og manifest en indholdshash i deres URL, og service workerens cache-navn følger det samlede output.

## Build og lokal visning

```bash
python3 tools/build.py
python3 -m unittest discover -s tools -p test_build.py -v
python3 -m http.server 8000 --directory _site
```

Åbn `http://localhost:8000/`. `_site/` er genereret og committes ikke. Ryd sitets data i browseren, hvis du ser en gammel version; service workeren gemmer filerne.

## Publicering

Hvert push til `main` kører `.github/workflows/pages.yml`. Den bygger med `tools/build.py` og publicerer kun `_site/` til GitHub Pages på domænet i `CNAME` (kaliv.dk). Skabeloner, værktøjer og denne README publiceres ikke.

`.github/workflows/site-checks.yml` kører på hver pull request og på `main`: build og tests, markup, links, visning ved flere skærmbredder, tilgængelighed, cache og Lighthouse. Rapporterne ligger som artefakt på kørslen.

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
