"""Build kaliv.dk from project.json and templates, using only the standard library."""

from copy import deepcopy
from base64 import b64encode
from datetime import date
from dataclasses import dataclass, field
from hashlib import sha256
from html import escape, unescape
from html.parser import HTMLParser
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


HTML_TEMPLATES = tuple(name for name in PUBLIC_FILES if name.endswith(".html"))
LEGACY_SCRIPTS = ("home.js", "dossier.js", "architecture.js", "progress.js", "proofs.js")
LEGACY_STYLES = ("home.css", "dossier.css", "site-shell.css")
EN_FILES = tuple("en/" + name for name in HTML_TEMPLATES)
PUBLIC_FILES += ("site.js", "site.css") + EN_FILES
TEMPLATE_FILES = HTML_TEMPLATES + (
    "llms.txt", "sitemap.xml", "service-worker.js",
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
INCLUDE = re.compile(r'{%\s*include\s+"([a-z-]+)"\s*%}')
PAGE_TITLES = {
    "brief": ("Projektbrief", "Project brief"),
    "hub": ("KalivHub / hjemmet", "KalivHub / home"),
    "architecture": ("Systemarkitektur", "System architecture"),
    "proofs": ("V1-bevisregister", "V1 proof ledger"),
    "progress": ("Offentlig status", "Public status"),
}
ATTR = re.compile(r"(?P<prefix>\b(?:[\w-]*href|src|srcset|content)\s*=\s*)(?P<quote>[\"'])(?P<value>.*?)(?P=quote)", re.DOTALL)
MONTHS = {
    "da": ("januar", "februar", "marts", "april", "maj", "juni", "juli", "august", "september", "oktober", "november", "december"),
    "en": ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"),
}
WORDS = {"da": ("nul", "ét", "to", "tre", "fire"), "en": ("zero", "one", "two", "three", "four")}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
REDIRECT = """(() => {
  const query = new URLSearchParams(location.search);
  if (query.get('lang') !== 'en' || location.pathname.startsWith('/en/')) return;
  const page = location.pathname.split('/').pop() || 'index.html';
  const pages = ['index.html','brief.html','hub.html','proofs.html','architecture.html','progress.html','404.html','offline.html'];
  if (!pages.includes(page)) return;
  query.delete('lang');
  const target = new URL(page === 'index.html' ? '/en/' : '/en/' + page, location.origin);
  target.search = query.toString();
  target.hash = location.hash;
  location.replace(target.href);
})();"""


@dataclass
class Element:
    tag: str
    attrs: dict = field(default_factory=dict)
    children: list = field(default_factory=list)
    parent: object = field(default=None, repr=False)


class Document(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.root = Element("")
        self.stack = [self.root]
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        node = Element(tag, dict(attrs), parent=self.stack[-1])
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if len(self.stack) > 1 and self.stack[-1].tag == tag:
            self.stack.pop()

    def handle_data(self, value):
        self.stack[-1].children.append(value)

    def handle_entityref(self, name):
        self.handle_data(f"&{name};")

    def handle_charref(self, name):
        self.handle_data(f"&#{name};")

    def handle_comment(self, value):
        self.handle_data(f"<!--{value}-->")

    def handle_decl(self, value):
        self.handle_data(f"<!{value}>")


def elements(node):
    for child in node.children:
        if isinstance(child, Element):
            yield child
            yield from elements(child)


def serialize(node):
    if isinstance(node, str):
        return node
    body = "".join(serialize(child) for child in node.children)
    if not node.tag:
        return body
    attrs = "".join(" " + key + ("" if value is None else '="' + escape(value, quote=True) + '"') for key, value in node.attrs.items())
    return f"<{node.tag}{attrs}>" + ("" if node.tag in VOID else body + f"</{node.tag}>")


def page_path(name, language):
    prefix = "/en/" if language == "en" else "/"
    return prefix if name == "index.html" else prefix + name


def local_url(value, language, canonical):
    url = urlsplit(unescape(value))
    origin = urlsplit(canonical)
    if value.startswith("#") or (url.netloc and url.netloc != origin.netloc) or (url.scheme and url.scheme != origin.scheme):
        return value
    name = posixpath.normpath("/" + url.path).lstrip("/")
    if name in ("", "."):
        name = "index.html"
    if name.startswith("en/"):
        name = name[3:] or "index.html"
    query = [(key, item) for key, item in parse_qsl(url.query, keep_blank_values=True) if key != "lang"]
    if name in HTML_TEMPLATES:
        path = page_path(name, language)
    else:
        path = "/" + name
    return urlunsplit((url.scheme, url.netloc, path, urlencode(query), url.fragment))


def compile_html(source, name, language, canonical):
    document = Document(source)
    nodes = list(elements(document.root))
    root = next(node for node in nodes if node.tag == "html")
    head = next(node for node in nodes if node.tag == "head")
    root.attrs.update(lang=language, **{"data-page": name.removesuffix(".html")})
    page = name.removesuffix(".html")
    classes = root.attrs.get("class", "").split() + ["page-" + page]
    if page in PAGE_TITLES:
        classes += ["site-document", "layout-dossier" if page in ("brief", "hub") else "layout-system"]
    root.attrs["class"] = " ".join(classes)
    canonical_url = canonical.rstrip("/") + page_path(name, language)
    for node in nodes:
        if language == "en":
            if "data-en" in node.attrs:
                node.children = [escape(node.attrs["data-en"], quote=False)]
            for source_key, destination in (("data-en-href", "href"), ("data-en-aria-label", "aria-label"), ("data-en-label", "aria-label"), ("data-en-alt", "alt"), ("data-en-content", "content")):
                if source_key in node.attrs:
                    node.attrs[destination] = node.attrs[source_key]
        chosen = node.attrs.get("data-language", node.attrs.get("data-lang"))
        if node.attrs.get("id") in ("lang-da", "lang-en"):
            chosen = node.attrs["id"][-2:]
        if chosen in ("da", "en"):
            node.attrs["href"] = page_path(name, chosen)
            classes = node.attrs.get("class", "").split()
            classes = [item for item in classes if item != "is-current"]
            if chosen == language:
                node.attrs["aria-current"] = "page"
                classes.append("is-current")
            else:
                node.attrs.pop("aria-current", None)
            if classes:
                node.attrs["class"] = " ".join(classes)
            else:
                node.attrs.pop("class", None)
        else:
            for attr in ("href", "src"):
                if attr in node.attrs:
                    node.attrs[attr] = local_url(node.attrs[attr], language, canonical)
        if "data-navlink" in node.attrs:
            node.attrs.pop("data-navlink")
            if urlsplit(node.attrs["href"]).path == page_path(name, language):
                node.attrs.update(**{"class": "is-current", "aria-current": "page"})
        if "srcset" in node.attrs:
            node.attrs["srcset"] = ", ".join(" ".join([local_url(parts[0], language, canonical)] + parts[1:]) for parts in (item.split() for item in node.attrs["srcset"].split(",")) if parts)
        if node.tag == "link" and node.attrs.get("rel") == "canonical":
            node.attrs["href"] = canonical_url
        if node.tag == "link" and node.attrs.get("rel") == "alternate":
            other = "en" if node.attrs.get("hreflang") == "en" else "da"
            node.attrs["href"] = canonical.rstrip("/") + page_path(name, other)
        if node.tag == "meta":
            prop = node.attrs.get("property")
            if prop == "og:url":
                node.attrs["content"] = canonical_url
            elif prop == "og:locale":
                node.attrs["content"] = "en_US" if language == "en" else "da_DK"
            elif prop == "og:locale:alternate":
                node.attrs["content"] = "da_DK" if language == "en" else "en_US"
        if node.tag == "script" and node.attrs.get("type") == "application/ld+json":
            data = json.loads("".join(node.children))
            data.update(inLanguage=language, url=canonical_url)
            if language == "en":
                for field_name in ("name", "description"):
                    if "data-en-" + field_name in node.attrs:
                        data[field_name] = node.attrs["data-en-" + field_name]
            node.children = [json.dumps(data, ensure_ascii=False, indent=2).replace("<", "\\u003c")]
        # Existing translation scripts are replaced by static HTML and one bootstrap.
        node.children = [child for child in node.children if not isinstance(child, Element) or child.tag != "script" or child.attrs.get("type") == "application/ld+json"]
        node.attrs = {key: value for key, value in node.attrs.items() if not key.startswith(("data-da", "data-en", "data-title", "data-description"))}
    script_attrs = {"src": "/site.js", "defer": None}
    if language == "da":
        script_attrs["blocking"] = "render"
    head.children.append(Element("script", script_attrs))
    return serialize(document.root)


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


def expand_partials(source, partials, stack=()):
    def include(match):
        name = match[1]
        if name in stack:
            raise ValueError(f"Circular partial: {' -> '.join((*stack, name))}")
        if name not in partials:
            raise ValueError(f"Unknown partial: {name}")
        return expand_partials(partials[name], partials, (*stack, name))
    result = INCLUDE.sub(include, source)
    if "{%" in result:
        raise ValueError("Unsupported partial directive")
    return result


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


def protect_html(source):
    """Apply the policy before fetches and hash the exact generated JSON-LD."""
    document = Document(source)
    nodes = list(elements(document.root))
    head = next(node for node in nodes if node.tag == "head")
    hashes = []
    for node in nodes:
        if node.tag == "script" and not node.attrs.get("src"):
            digest = b64encode(sha256("".join(node.children).encode("utf-8")).digest()).decode("ascii")
            hashes.append("'sha256-" + digest + "'")
    policy = "; ".join((
        "default-src 'none'", "base-uri 'none'", "object-src 'none'",
        "script-src 'self'" + (" " + " ".join(sorted(set(hashes))) if hashes else ""),
        "style-src 'self'", "img-src 'self'", "font-src 'self'",
        "connect-src 'self'", "worker-src 'self'", "manifest-src 'self'",
        "frame-src 'none'", "form-action 'none'",
    ))
    charset = next((i + 1 for i, node in enumerate(head.children) if isinstance(node, Element) and "charset" in node.attrs), 0)
    head.children.insert(charset, Element("meta", {"http-equiv": "Content-Security-Policy", "content": policy}))
    return serialize(document.root)


def build(root=ROOT):
    root = Path(root)
    project = json.loads((root / "project.json").read_text(encoding="utf-8"))
    context = context_for(project)
    files = {}
    templates = {name: (root / "templates" / name).read_text(encoding="utf-8") for name in TEMPLATE_FILES}
    partials = {path.stem: path.read_text(encoding="utf-8") for path in (root / "templates" / "partials").glob("*.html")}
    for name in PUBLIC_FILES:
        if name not in TEMPLATE_FILES and name not in EN_FILES and name not in LEGACY_SCRIPTS + LEGACY_STYLES and name != "project.json":
            files[name] = (root / name).read_bytes()
    files["site.js"] = REDIRECT.encode("utf-8") + b"\n" + files["site.js"]
    for name in LEGACY_SCRIPTS:
        files[name] = files["site.js"]
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
    # Older cached HTML still uses these URLs. Keep a single maintained CSS source.
    for name in LEGACY_STYLES:
        files[name] = ('@import url("/site.css?v=' + versions["site.css"] + '");\n').encode("utf-8")
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
        titles = PAGE_TITLES.get(Path(name).stem, ("", ""))
        page_context = {**context, "page": {"title_da": titles[0], "title_en": titles[1]}}
        output = render(expand_partials(source, partials), page_context, html=name.endswith((".html", ".xml")))
        if name.endswith(".html"):
            english = compile_html(output, name, "en", project["canonical"])
            files["en/" + name] = protect_html(version_html(english, versions, project["canonical"])).encode("utf-8")
            output = protect_html(version_html(compile_html(output, name, "da", project["canonical"]), versions, project["canonical"]))
        else:
            for page in HTML_TEMPLATES:
                old = project["canonical"] + ("" if page == "index.html" else page) + "?lang=en"
                output = output.replace(old, project["canonical"].rstrip("/") + page_path(page, "en"))
        files[name] = output.encode("utf-8")
    core = []
    for name in sorted(files):
        if Path(name).suffix in (".html", ".css", ".js", ".json", ".txt", ".webmanifest") or name in CORE_MEDIA:
            path = "./" if name == "index.html" else "./en/" if name == "en/index.html" else "./" + name
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
