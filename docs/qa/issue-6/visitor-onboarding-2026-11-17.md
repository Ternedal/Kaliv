# kaliv.dk: positionering, onboarding og status

Dato: 17. november 2026. Grundlag: `eb39a419e3132710e9bde3c71fe42b802ab5b548` på Ternedal/Kaliv.

Ændringerne er en kladde til review. Udgivelsesversion **v2.0.20**, dato **14. november 2026**, eksisterende release-links og checksum-link er bevaret. RAM-/diskminimum, fuld CPU-drift, kontaktvalg samt Windows-/VR-skærmbilleder kræver stadig afklaring. Ingen ny stack eller nye afhængigheder er tilføjet.

## Konkrete tekstændringer per side

Alle tekster kommer fra de samme skabeloner og genereres samtidigt til DA og `/en/`. Tabellen viser centrale før/efter-eksempler; patchen indeholder hele ændringen.

| Side | Før (DA) | Efter (DA) | Before (EN) | After (EN) |
|---|---|---|---|---|
| `/` | “Tal og skriv på computer og telefon. Mød Kaliv i VR. Modellerne kører på din egen rig.” | “Kaliv er en personlig AI, som du kan skrive og tale med på computer og telefon.” Dernæst forklares rig som egen Windows-/Linux-maskine med ModelRig. Et dokumenteret RTX 3060/12 GB-eksempel er tydeligt adskilt fra et generelt minimum. | “Talk and write on your computer and phone. Meet Kaliv in VR. The models run on your own rig.” | “Kaliv is a personal AI you can write and talk to on your computer and phone.” Rig and the documented hardware example are explained immediately below. |
| `/` status | VR: “Udviklet”; Hub nævnt uden status. | “Windows og Android: Udgivet. VR og Hub: Under udvikling.” Samme formulering genbruges på brief, download og progress. | VR: “Developed”. | “Windows and Android: Released. VR and Hub: Under development.” |
| `/#vr` | “Quest-klienten er udviklet i Unity og OpenXR.” / “BodyRig-avatarer og bevægelse”. | “Quest-klienten har kode til parring, chat, avatarer og medievisning.” Kræver source-build; ingen offentlig VR-APK i denne udgivelse. “Avatarer og bevægelse”. | “The Quest client is developed in Unity and OpenXR.” / “BodyRig avatars and motion”. | “The Quest client has code for pairing, chat, avatars and media playback.” Source-build/public-APK boundary stated; internal module name removed. |
| `/` billeder | Kun hero-illustration og ankh. | To optagelser af den faktiske Android-brugerflade fra release-taggets UI-tests. Tydelig mærkning som testdata og ikke fysisk acceptbevis. | Illustration only. | Two actual Android UI test captures, explicitly labelled as test data rather than physical acceptance evidence. |
| `brief.html` | “Én idé. Tre apps.” / “Kaliv VR er den udviklede Quest-klient…” | “Det kan du bruge i dag.” Udgivne Windows-/Android-apps, VR-source-build og Hub under udvikling beskrives hver for sig. Rig forklares; link til dataflow. | “One idea. Three apps.” / “Kaliv VR is the developed Quest client…” | “What you can use today.” The same release/development boundaries and rig definition as DA. |
| `download.html` første gang | “Start ModelRig på din rig…” med GitHub-link. | Fem trin: installér Ollama/hent model; hent server og worker; start dem i hver sit PowerShell-vindue; lav parringskode; forbind klient. Kommandoer står på siden. | “Start ModelRig on your rig…” with a GitHub link. | Five on-page steps with matching PowerShell commands and separate full-guide links. |
| `download.html` Java | “Installér Java 21.” | Temurin JDK 21 LTS, Windows x64, HotSpot, MSI; officielt filtreret downloadlink og PATH-anvisning. Eksisterende `java -jar`-kommando bevaret. | “Install Java 21.” | The same recommended build, official download link and PATH instructions. |
| `download.html` Android | “Appen til din telefon.” | “Kræver Android 8.0 eller nyere.” Sideload-tilladelse pr. browser/filapp og manuel godkendelse af tilbudte opdateringer forklares. | “The app for your phone.” | “Requires Android 8.0 or newer.” Matching sideload and update instructions. |
| `download.html` krav og FAQ | Ingen samlet hardwareboks eller FAQ. | Tabel med OS, RAM, GPU/VRAM, disk og LAN. Ukendte minima fremgår som uafklarede. Ingen udgivet macOS-/Linux-klient. Seks FAQ i eksisterende side. | No combined requirements or FAQ. | Matching requirements and six FAQ; Linux-server and Linux-client availability are distinguished. |
| `progress.html` | “0/4 samlede beviser er lukket.” Hub: “Under afprøvning”. | “V1-kriterier: 0 af 4 bekræftet”, straks fulgt af fire korte forklaringer. Hub: “Under udvikling”. Statusordene Udgivet / Under test / Under udvikling defineres. | “0/4 overall proofs are closed.” Hub: “In testing”. | “V1 criteria: 0 of 4 confirmed”, four explanations and the same three status definitions. |
| `proofs.html` | “0/4 beviser lukket”; “Mangler”. | “V1-kriterier: 0 af 4 bekræftet”; “Ikke bekræftet”. Fire forklaringer lige under tælleren; historisk evidens forbliver i details. | “0/4 proofs closed”; “Missing”. | “V1 criteria: 0 of 4 confirmed”; “Not confirmed”. Matching explanations and definitions. |
| `hub.html` | “KalivHub forbinder Kaliv med Nest Hub og Home Assistant.” / “Se teknisk afgrænsning”. | Øverst: manuel fysisk samtale er afprøvet; samlet hjemmeopsætning kan endnu ikke installeres som godkendt produkt; mikrofoninput er ikke verificeret. Ét details: “Teknisk evidens”. Sender beskrives som komponenten, der sender data til skærmen. | “KalivHub connects Kaliv to Nest Hub and Home Assistant.” / “View technical scope”. | Matching can/cannot-use description; one “Technical evidence” disclosure; sender terminology explained. |
| `architecture.html` | VR-klientens rolle uden status. | “Under udvikling. Unity/OpenXR-klient: chat, avatar og medievisning på Quest.” | VR role without status. | “Under development. Unity/OpenXR client: chat, avatars and media on Quest.” |
| `privacy.html` (ny) | Fandtes ikke. | “Her ligger dine data.” Lokal klientlagring, dokumentindeks/serverhukommelse, valgfrie cloud-ruter, nuværende dataafgrænsninger, tale, HTTP/LAN samt hjemmesidens cache. | Did not exist. | “Where your data goes.” Identical data-flow and storage boundaries. |
| Fælles footer | “Personlig AI. Bygget på ModelRig.” og GitHub-link. | “Bygget af Anders Ternedal”, privatliv, MIT-link til hjemmesidens LICENSE, kontakt via GitHub Issues som konkret kladdevalg. | “Personal AI. Built on ModelRig.” | “Built by Anders Ternedal”, privacy, website MIT license and draft contact choice. |
| `404.html`, `offline.html`, brand | Dekorativ ankh kunne have beskrivende alt-tekst på EN. | `alt="" aria-hidden="true"` på dekorative ankh-billeder, begge sprog. | Decorative ankh could receive an English alt description. | Empty alt and aria-hidden in both languages. |

## Teknik og leverance

- Den eksisterende Python-standardbiblioteksrenderer bevares. Den genererer fortsat statisk HTML; ingen framework, bundler eller nye runtime-scripts.
- `blocking="render"` er fjernet. Kun det lille, eksisterende sprogredirect køres inline i DA-head, efter CSP og før øvrige ressourcer. CSP tillader dets præcise SHA-256. `/en/` kræver ikke redirect eller oversættelses-JS.
- Den almindelige `site.js` indeholder ikke længere redirect. Gamle JS-aliaser bevarer redirect for allerede cachede gamle dokumenter.
- `?lang=en` bevarer query-parametre og fragment. URL-struktur, `#vr`, `#windows`, `#android` og eksisterende download-/checksum-links består.
- Hreflang, canonical, JSON-LD, WebP/picture, skip-link, service worker og cache-hashes bevares. Privatliv indgår i sitemap, sprogskift, offline-cache og alle browserchecks.
- Android-billederne er konverteret tabsfrit til WebP; de indlæses lazy med eksplicitte, korrekte dimensioner. Eksisterende hero bevares.
- Kildepatch: PR'ens diff. Genereret HTML-patch: `rendered-html-patch.zip`, som indeholder `rendered-html.patch` (DA og EN, til review; `_site` er ikke versionsstyret). HTML-patchen erstatter ikke kildepatchen og den eksisterende renderer.

## Verificerede fakta og kilder

Alle ModelRig-links nedenfor peger på **v2.0.20**, ikke på nyere udviklingskode.

| Faktum | Kilde |
|---|---|
| Android minSdk 26 = Android 8.0 | [app/build.gradle.kts](https://github.com/Ternedal/ModelRig/blob/v2.0.20/android/app/build.gradle.kts#L45) |
| Android tilbyder opdatering, som brugeren selv installerer | [AppUi.kt](https://github.com/Ternedal/ModelRig/blob/v2.0.20/android/app/src/main/java/dk/ternedal/modelrig/ui/AppUi.kt#L1003), [opdateringskort](https://github.com/Ternedal/ModelRig/blob/v2.0.20/android/app/src/main/java/dk/ternedal/modelrig/ui/AppUi.kt#L2428) |
| Java/JDK 21 til desktop | [desktop/README.md](https://github.com/Ternedal/ModelRig/blob/v2.0.20/desktop/README.md#L39), [Adoptium JDK 21](https://adoptium.net/temurin/releases/?arch=x64&mode=filter&os=windows&package=jdk&version=21), [MSI-installation](https://adoptium.net/installation/windows) |
| Server/worker-exe findes, kilde-ZIP er ikke en installer | [release](https://github.com/Ternedal/ModelRig/releases/tag/v2.0.20), [worker-entrypoint](https://github.com/Ternedal/ModelRig/blob/v2.0.20/worker/run_worker.py#L1), [release-workflow](https://github.com/Ternedal/ModelRig/blob/v2.0.20/.github/workflows/build-and-release.yml#L408) |
| Startorden, LAN og parring | [deploy](https://github.com/Ternedal/ModelRig/blob/v2.0.20/deploy/README.md#L3), [pair CLI](https://github.com/Ternedal/ModelRig/blob/v2.0.20/backend/cmd/modelrig-server/main.go#L123) |
| qwen3:14b er dokumenteret på RTX 3060/12 GB; ikke samlet hardwareminimum | [MODELS.md](https://github.com/Ternedal/ModelRig/blob/v2.0.20/MODELS.md#L7) |
| Lokal Android-/Windows-lagring | [ChatDb.kt](https://github.com/Ternedal/ModelRig/blob/v2.0.20/android/app/src/main/java/dk/ternedal/modelrig/data/ChatDb.kt#L10), [DesktopChatDb.kt](https://github.com/Ternedal/ModelRig/blob/v2.0.20/desktop/composeApp/src/main/kotlin/dk/ternedal/modelrig/desktop/data/DesktopChatDb.kt#L264) |
| Workerens dataområde og dokumentindeks | [paths.py](https://github.com/Ternedal/ModelRig/blob/v2.0.20/worker/app/paths.py#L17), [store.py](https://github.com/Ternedal/ModelRig/blob/v2.0.20/worker/app/store.py#L20) |
| Aktuel besked og systeminstruktioner til cloud; ikke tidligere samtaleture | [Android CloudClient](https://github.com/Ternedal/ModelRig/blob/v2.0.20/android/app/src/main/java/dk/ternedal/modelrig/net/CloudClient.kt#L13), [desktop ChatRouter](https://github.com/Ternedal/ModelRig/blob/v2.0.20/desktop/composeApp/src/main/kotlin/dk/ternedal/modelrig/desktop/net/ChatRouter.kt#L31), [SECURITY](https://github.com/Ternedal/ModelRig/blob/v2.0.20/SECURITY.md#L218) |
| Værktøjsresultater kan sendes, private read-resultater er ikke blokeret som standard | [tools.py](https://github.com/Ternedal/ModelRig/blob/v2.0.20/worker/app/tools.py#L1138), [SECURITY](https://github.com/Ternedal/ModelRig/blob/v2.0.20/SECURITY.md#L226) |
| Voice sender aktuel transskription til valgt cloud-sprogmodel | [voice_pipeline.py](https://github.com/Ternedal/ModelRig/blob/v2.0.20/worker/app/voice_pipeline.py#L237) |
| MIT-licens på både hjemmeside og ModelRig | [Kaliv LICENSE](https://github.com/Ternedal/Kaliv/blob/main/LICENSE), [ModelRig LICENSE](https://github.com/Ternedal/ModelRig/blob/v2.0.20/LICENSE) |

### Oprindelse for app-optagelser

- `assets/kaliv-android-chat.webp`: [ChatScreen1ScreenshotTest.screen1Dark.png](https://github.com/Ternedal/ModelRig/blob/v2.0.20/android/app/src/test/screenshots/dk.ternedal.modelrig.ui.chat.ChatScreen1ScreenshotTest.screen1Dark.png), Git-blob `9bcf764f31e3b32b31818b4071b731d2ffbc8bbb`, 1078 × 2399.
- `assets/kaliv-android-pairing.webp`: [PairingUiScreenshotTest.screen5Dark.png](https://github.com/Ternedal/ModelRig/blob/v2.0.20/android/app/src/test/screenshots/dk.ternedal.modelrig.ui.chat.PairingUiScreenshotTest.screen5Dark.png), Git-blob `8733193671b2ffe40181e1d07362f336f3a0e26c`, 1078 × 1430.
- Optagelserne viser appens faktiske UI med testdata. De opfylder ikke ønsket om fysiske Windows-/VR-optagelser, og de præsenteres ikke som sådan. Ingen nye illustrationsbilleder er genereret.

## Afklaringer til Anders, samlet

1. **Hardware:** Hvilket konkret standardsetup vil du stå inde for: Windows-/Linux-version, standardmodel, minimum RAM, GPU/VRAM og ledig disk? Er hele dette setup fysisk afprøvet uden GPU? Indtil da angiver kladden det dokumenterede 12 GB-eksempel og uafklarede minima.
2. **Skærmbilleder:** Hvor findes aktuelle optagelser fra Windows-klienten og Kaliv VR, som vi må bruge? Findes der også en fysisk Android-optagelse til erstatning for UI-testbillederne?
3. **Kontakt:** Skal offentlig kontakt pege på GitHub Issues i Ternedal/Kaliv som i kladden, eller en bestemt mailadresse?

**Allerede afklaret fra kilder:** Android-minimum er 8.0. Opdateringer kræver brugerens installation. Hjemmesidens LICENSE er MIT; linkteksten er afgrænset til hjemmesiden, så den ikke foregiver at dække samtlige modeller og afhængigheder.

## Validering

- 23 lokale Python-tests består, herunder CSP-hash/-rækkefølge, redirect uden render-blocking, DA/EN-struktur og ingen synlige tekniske evidensnumre uden for details.
- Releaseversion, releasedato, tidligere download-URLs og checksum-URL sammenlignes med udgangspunktet som særskilt reviewkontrol.
- Visuelt gennemgået i browser: forside, Windows-start, privatliv DA/EN, statusside og sprogskift. QA-billede: `forside-da.jpg`.
- Fulde browser-/Lighthouse-resultater tilføjes, når PR-checket er afsluttet. Det omfatter 80 viewport/sprog-cases, 24 langsomme legacy-sprogredirects, 16 mobil-Lighthouse-kørsler, CSP, offline og no-JS.
- Windows-kommandoerne er verificeret mod release/kildekode; de er ikke fysisk kørt på en ny Windows-rig i denne session.

## Licensnotits for genbrugte Android UI-optagelser

MIT License

Copyright (c) 2026 Anders Ternedal Nielbæk

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
