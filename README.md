# Kaliv — projektsiden kaliv.dk

Dette repository indeholder den offentlige projektside for **Kaliv** og **ModelRig**: [kaliv.dk](https://kaliv.dk/) (dansk) og [kaliv.dk/?lang=en](https://kaliv.dk/?lang=en) (engelsk).

Kaliv er én personlig AI på tværs af Windows, Android, hjemmet (KalivHub) og VR (Quest). ModelRig er den lokale infrastruktur, der holder identitet, hukommelse og tilladelser. Siden forklarer projektet og skelner mellem det, der er udgivet, det der er set på rigtig hardware, og det der stadig mangler bevis.

Repoet er kun websitet. Produktets kode ligger i de repositories, der står under [Relaterede repositories](#relaterede-repositories).

## Sider

| Fil | Indhold |
|---|---|
| `index.html` | Forside |
| `brief.html` | Projektbrief |
| `hub.html` | KalivHub — Kaliv i hjemmet |
| `architecture.html` | Systemarkitektur |
| `proofs.html` | V1-bevisregister |
| `progress.html` | Status |
| `404.html` | Fejlside |
| `offline.html` | Vises af service workeren uden forbindelse |

## Øvrige filer

| Fil | Rolle |
|---|---|
| `home.css`, `home.js` | Forsidens stylesheet og sprogskift |
| `dossier.css`, `dossier.js` | Stylesheet og sprogskift for `brief.html` og `hub.html` |
| `site-shell.css` | Fælles header og footer på de fem undersider |
| `project.json` | Maskinlæsbart manifest: komponenter, status, bevisgrænser og kildesnapshot |
| `llms.txt` | Samme oversigt i tekstform til sprogmodeller |
| `sitemap.xml`, `robots.txt` | Indeksering |
| `site.webmanifest` | Webapp-metadata og ikoner |
| `service-worker.js` | Cache og offline-side |
| `assets/` | Hero-billede i tre størrelser, Kaliv-ankh og ikoner |
| `dist/` | En kopi af sitets filer. Ingen side bruger den; se [Publicering](#publicering) |

`architecture.html`, `progress.html` og `proofs.html` har deres sidespecifikke CSS og sprogskift inline i filen.

Sitet har ingen build, ingen afhængigheder og ingen eksterne ressourcer.

## Sprog

Dansk er standard og står direkte i HTML'en. Den engelske tekst står i `data-en`-attributter på de samme elementer, og et script bytter teksten, når adressen har `?lang=en`. Uden JavaScript vises siden derfor altid på dansk.

Når du ændrer en tekst, skal både elementets indhold (dansk) og `data-da`/`data-en` rettes.

## Opdatering af status

Statusoplysninger er skrevet i hånden flere steder og skal rettes samlet:

| Oplysning | Står i |
|---|---|
| Seneste release | `index.html`, `brief.html`, `proofs.html`, `architecture.html`, `progress.html`, `project.json`, `llms.txt` |
| "Opdateret"-dato | Alle seks indholdssider (synlig tekst og `dateModified` i JSON-LD), `project.json`, `sitemap.xml` (`lastmod`) |
| Commit-snapshot af de øvrige repositories | `progress.html`, `hub.html`, `project.json`, `llms.txt` |
| Bevisstatus og kendte grænser | `proofs.html`, `progress.html`, `hub.html`, `project.json`, `llms.txt` |

Hent version, datoer og commit-id'er fra GitHub, når du retter dem. Siden må ikke beskrive noget som bevist, før beviset findes.

## Cache-versioner

Browsere og service workeren gemmer filerne. Når en cachet fil ændres, skal versionen hæves:

- `?v=`-nummeret på `home.css`, `home.js` og `site-shell.css` i de HTML-filer, der henter dem.
- `CACHE_NAME` i `service-worker.js`, og de samme `?v=`-numre i `CORE_ASSETS`.

`dossier.css` og `dossier.js` hentes uden versionsnummer.

## Lokal visning

```bash
python3 -m http.server 8000
```

Åbn `http://localhost:8000/`. Forsiden registrerer service workeren også på `localhost` (undersiderne gør det kun over HTTPS); ryd sitets data i browseren, hvis du ser en gammel version.

## Publicering

Hvert push til `main` kører `.github/workflows/pages.yml`, som publicerer til GitHub Pages på domænet i `CNAME` (kaliv.dk). Workflowet uploader hele repo-roden. Derfor ligger `README.md`, `LICENSE` og `dist/` også på kaliv.dk.

Der er ingen automatisk kontrol af en pull request før merge. Åbn siderne lokalt ved mobil- og desktopbredde, og test begge sprog, før du merger.

Planen for at rette deploy, engelske sider og statusvedligeholdelse står i [issue #6](https://github.com/Ternedal/Kaliv/issues/6).

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
