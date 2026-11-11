"""Build kaliv.dk from project.json and templates, using only the standard library."""

from copy import deepcopy
from datetime import date
from hashlib import sha256
from html import escape, unescape
from pathlib import Path
import json
import posixpath
import re
import shutil
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


ROOT = Path(__file__).resolve().parent.parent
PUBLIC_FILES = (
    ".nojekyll", "CNAME", "index.html", "brief.html", "hub.html",
    "proofs.html", "architecture.html", "progress.html", "404.html",
    "offline.html", "home.css", "home.js", "dossier.css", "dossier.js",
    "site-shell.css", "architecture.js", "proofs.js", "progress.js", "project.json", "llms.txt", "robots.txt", "sitemap.xml",
    "site.webmanifest", "service-worker.js",
    "assets/kaliv-favicon-32.png", "assets/kaliv-apple-touch-icon.png",
    "assets/kaliv-icon-192.png", "assets/kaliv-icon-512.png",
    "assets/kaliv-icon-maskable-512.png", "assets/kaliv-ankh-160.webp",
    "assets/kaliv-ankh-640.webp",
    "assets/modelrig-continuity-female-hair-mobile.webp",
    "assets/modelrig-continuity-female-hair-1920.webp",
    "assets/modelrig-continuity-female-hair-hires.webp",
)


TEMPLATE_FILES = tuple(name for name in PUBLIC_FILES if name.endswith(".html")) + (
    "llms.txt", "sitemap.xml", "proofs.js", "service-worker.js",
)
CORE_MEDIA = (
    "assets/kaliv-favicon-32.png", "assets/kaliv-apple-touch-icon.png",
    "assets/kaliv-icon-192.png", "assets/kaliv-ankh-160.webp",
)
HEAD_KEYS = {
    "physical_proof": "KalivHub-Receiver@physical-proof",
    "receiver_probe": "KalivHub-Receiver@test/nest-hub-microphone-probe-current",
    "receiver_signed": "KalivHub-Receiver@signed-mirror-code-head",
    "ha_sender": "KalivHub@feat/ha-cast-controls-v1",
    "signed_android": "ModelRig@feat/android-kalivhub-mirror",
}
TOKEN = re.compile(r"{{\s*([\w.-]+)(?:\s*\|\s*(\w+))?\s*}}")
ATTR = re.compile(r"(?P<prefix>\b(?:[\w-]*href|src|srcset|content)\s*=\s*)(?P<quote>[\"'])(?P<value>.*?)(?P=quote)", re.DOTALL)
MONTHS = {
    "da": ("januar", "februar", "marts", "april", "maj", "juni", "juli", "august", "september", "oktober", "november", "december"),
    "en": ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"),
}
WORDS = {"da": ("nul", "ét", "to", "tre", "fire"), "en": ("zero", "one", "two", "three", "four")}


def format_date(value, language):
    day = date.fromisoformat(value)
    dot = "." if language == "da" else ""
    return f"{day.day}{dot} {MONTHS[language][day.month - 1]} {day.year}"


def context_for(project):
    date.fromisoformat(project["updated"])
    date.fromisoformat(project["latest_release"]["published"])
    if not re.fullmatch(r"\d+\.\d+\.\d+", project["latest_release"]["version"]):
        raise ValueError("latest_release.version must be a stable x.y.z release")
    items = project["v1_proofs"]
    if {item["id"] for item in items} != {"P01", "P02", "P03", "P04"} or len(items) != 4:
        raise ValueError("Expected exactly one of each P01 through P04")
    if any(item["status"] not in ("open", "closed") for item in items):
        raise ValueError("Proof status must be open or closed")
    context = deepcopy(project)
    closed = sum(item["status"] == "closed" for item in items)
    remaining, total = len(items) - closed, len(items)
    stats = {"closed": closed, "open": remaining, "total": total}
    for language in WORDS:
        for label, number in (("closed", closed), ("open", remaining), ("total", total)):
            stats[f"{label}_word_{language}"] = WORDS[language][number]
    stats["all_open_da"] = ("alle fire" if not closed else f"{WORDS['da'][remaining]} af fire") + " samlede V1-beviser er fortsat åbne"
    stats["all_open_en"] = ("all four" if not closed else f"{WORDS['en'][remaining]} of four") + " complete V1 proofs remain open"
    stats["ledger_open_da"] = "Alle fire står åbne." if not closed else f"{WORDS['da'][remaining].capitalize()} af fire står åbne."
    stats["ledger_open_en"] = "All four remain open." if not closed else f"{WORDS['en'][remaining].capitalize()} of four remain open."
    stats["closed_statement_da"] = "Ingen af de fire systembeviser er lukket endnu." if not closed else f"{WORDS['da'][closed].capitalize()} af de fire systembeviser er lukket."
    stats["closed_statement_en"] = "None of the four system proofs is closed yet." if not closed else f"{WORDS['en'][closed].capitalize()} of the four system proofs {'is' if closed == 1 else 'are'} closed."
    stats["public_open_en"] = "All four public proof gates remain open." if not closed else f"{WORDS['en'][remaining].capitalize()} of four public proof gates remain open."
    context["stats"] = stats
    context["proofs"] = {
        item["id"]: {
            **item,
            "label_da": "Mangler" if item["status"] == "open" else "Bevist",
            "label_en": "Missing" if item["status"] == "open" else "Proven",
            "gate_da": "Åben" if item["status"] == "open" else "Lukket",
            "gate_en": "Open" if item["status"] == "open" else "Closed",
        }
        for item in items
    }
    context["heads"] = {name: project["source_snapshot"]["heads"][key] for name, key in HEAD_KEYS.items()}
    mirror_status = next(item["status"] for item in project["supporting_evidence"] if item["id"] == "E04")
    labels = {"parked": ("Parkeret", "Parked"), "gate_open": ("Gate åben", "Gate open"), "ci_green": ("CI grøn", "CI green"), "released": ("Udgivet", "Released")}
    if mirror_status not in labels:
        raise ValueError(f"Unsupported E04 status: {mirror_status}")
    context["mirror"] = dict(zip(("label_da", "label_en"), labels[mirror_status]))
    return context


def render(source, context, html=False, stack=()):
    def replace(match):
        key, formatter = match.groups()
        if key in stack:
            raise ValueError(f"Circular status reference: {' -> '.join((*stack, key))}")
        value = context
        try:
            for part in key.split("."):
                value = value[int(part)] if isinstance(value, list) else value[part]
        except (KeyError, IndexError, TypeError, ValueError) as error:
            raise ValueError(f"Unknown template value: {key}") from error
        if isinstance(value, str) and "{{" in value:
            value = render(value, context, stack=(*stack, key))
        if formatter == "json":
            return json.dumps(value, ensure_ascii=False, indent=2).replace("<", "\\u003c")
        if formatter in ("date_da", "date_en"):
            value = format_date(value, formatter[-2:])
        elif formatter == "short":
            value = str(value)[:7]
        elif formatter == "capitalize":
            value = str(value).capitalize()
        elif formatter == "lower":
            value = str(value).lower()
        elif formatter:
            raise ValueError(f"Unknown formatter: {formatter}")
        if not isinstance(value, (str, int, float)):
            raise ValueError(f"Template value needs a formatter: {key}")
        return escape(str(value), quote=True) if html else str(value)

    output = TOKEN.sub(replace, source)
    if "{{" in output:
        raise ValueError("Unresolved template marker")
    return output


def render_data(value, context):
    if isinstance(value, dict):
        return {key: render_data(item, context) for key, item in value.items()}
    if isinstance(value, list):
        return [render_data(item, context) for item in value]
    return render(value, context) if isinstance(value, str) else value


def version_url(url, versions, canonical, relative_to=""):
    parts = urlsplit(unescape(url))
    origin = urlsplit(canonical)
    if (parts.netloc and parts.netloc != origin.netloc) or (parts.scheme and parts.scheme != origin.scheme):
        return url
    path = posixpath.normpath(posixpath.join("/", relative_to, parts.path)).lstrip("/")
    if path not in versions:
        return url
    query = [(key, value) for key, value in parse_qsl(parts.query, keep_blank_values=True) if key != "v"]
    query.append(("v", versions[path]))
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def version_html(source, versions, canonical):
    def attribute(match):
        value = match["value"]
        if match["prefix"].strip().startswith("srcset"):
            candidates = []
            for candidate in value.split(","):
                pieces = candidate.strip().split()
                if pieces:
                    pieces[0] = version_url(pieces[0], versions, canonical)
                candidates.append(" ".join(pieces))
            updated = ", ".join(candidates)
        else:
            updated = version_url(value, versions, canonical)
        if updated == value:
            return match[0]
        return match["prefix"] + match["quote"] + escape(updated, quote=True) + match["quote"]

    return ATTR.sub(attribute, source)


def build(root=ROOT):
    root = Path(root)
    project = json.loads((root / "project.json").read_text(encoding="utf-8"))
    context = context_for(project)
    files = {}
    templates = {name: (root / "templates" / name).read_text(encoding="utf-8") for name in TEMPLATE_FILES}
    for name in PUBLIC_FILES:
        if name not in TEMPLATE_FILES and name != "project.json":
            files[name] = (root / name).read_bytes()
    for name, source in templates.items():
        if name.endswith(".js") and name != "service-worker.js":
            files[name] = render(source, context).encode("utf-8")
    versions = {}
    # Images and scripts are leaves; CSS and the manifest can reference images.
    for name, data in files.items():
        if Path(name).suffix in (".png", ".webp", ".js"):
            versions[name] = sha256(data).hexdigest()[:12]
    for name in (name for name in files if name.endswith(".css")):
        source = files[name].decode("utf-8")
        source = re.sub(r"url\((['\"]?)([^)'\"]+)\1\)", lambda match: f"url({match[1]}{version_url(match[2], versions, project['canonical'])}{match[1]})", source)
        files[name] = source.encode("utf-8")
        versions[name] = sha256(files[name]).hexdigest()[:12]
    manifest = json.loads(files["site.webmanifest"])
    for icon in manifest.get("icons", []):
        icon["src"] = version_url(icon["src"], versions, project["canonical"])
    files["site.webmanifest"] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    versions["site.webmanifest"] = sha256(files["site.webmanifest"]).hexdigest()[:12]
    published = deepcopy(project)
    published.pop("site_copy", None)
    files["project.json"] = (json.dumps(render_data(published, context), ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    for name, source in templates.items():
        if name.endswith(".js"):
            continue
        output = render(source, context, html=name.endswith((".html", ".xml")))
        if name.endswith(".html"):
            output = version_html(output, versions, project["canonical"])
        files[name] = output.encode("utf-8")
    core = []
    for name in sorted(files):
        if Path(name).suffix in (".html", ".css", ".js", ".json", ".txt", ".webmanifest") or name in CORE_MEDIA:
            path = "./" if name == "index.html" else "./" + name
            core.append(version_url(path, versions, project["canonical"]))
    digest = sha256(templates["service-worker.js"].encode("utf-8"))
    for name, data in sorted(files.items()):
        digest.update(name.encode("utf-8") + b"\0" + data + b"\0")
    version = "build-" + digest.hexdigest()[:16]
    worker_context = {**context, "build_version": version, "core_assets": core}
    files["service-worker.js"] = render(templates["service-worker.js"], worker_context).encode("utf-8")
    if set(files) != set(PUBLIC_FILES):
        raise ValueError("Public file set does not match the allowlist")
    # All inputs and templates have been validated before replacing the output.
    output = root / "_site"
    if output.exists():
        shutil.rmtree(output)
    for name, data in files.items():
        destination = output / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
    return {"version": version, "versions": versions, "core_assets": core, "files": files}


if __name__ == "__main__":
    result = build()
    print(f"Built {len(result['files'])} public files; cache {result['version']}")
