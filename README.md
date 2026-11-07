# Kaliv / ModelRig

Dette repository indeholder den offentlige projektside for **ModelRig** og den første produktmanifestation, **Kaliv**.

- [Dansk side](https://kaliv.dk/)
- [English site](https://kaliv.dk/?lang=en)

## Hvad siden forklarer

ModelRig er et local-first fundament for vedvarende AI med hukommelse, tid, perception, handling og kropsliggørelse under eksplicit kontrol. Kaliv er produktlaget på tværs af Windows, Android og Quest.

## Struktur

- `index.html` — den responsive DA/EN-præsentation
- `404.html` — brandet fejlside
- `assets/` — hero-grafik og Kaliv-ankh
- `robots.txt` og `sitemap.xml` — søgemaskineindeksering
- `site.webmanifest` — webapp-metadata
- `.github/workflows/pages.yml` — automatisk GitHub Pages-deployment

## Publicering

Hver ændring på `main` udløser den fastlåste GitHub Pages-workflow. Den offentlige side bliver publiceret på [kaliv.dk](https://kaliv.dk/).

## Repositoryets rolle

Dette repository er den offentlige webpræsentation. ModelRig-systemets komponenter og runtime udvikles i deres respektive projekt-repositories.


## Tværgående dokumentation

- [Kaliv-økosystemets komponenter og ansvarsgrænser](docs/KALIV_ECOSYSTEM.md)
- [KalivNexus](https://github.com/Ternedal/KalivNexus) er et foreslået API-/capability-broker-lag og er ikke dokumenteret som en produktionsklar integration.
- [ModelRig](https://github.com/Ternedal/ModelRig) er backend- og orkestreringsprojektet; denne repository indeholder websitet og må ikke forveksles med Windows-, Android- eller VR-klienternes runtime.

Den offentlige hjemmeside bør kun beskrive funktioner som tilgængelige, når den relevante integration og release er verificeret.
