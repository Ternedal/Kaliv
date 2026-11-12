"""Exercise propagation, reproducibility, cache invalidation and build failures."""

import json
from pathlib import Path
import re
import shutil
import tempfile
import unittest

from build import PUBLIC_FILES, ROOT, TEMPLATE_FILES, EN_FILES, LEGACY_SCRIPTS, LEGACY_STYLES, Document, elements, build, page_path


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        inputs = [name for name in PUBLIC_FILES if name not in TEMPLATE_FILES and name not in EN_FILES and name not in LEGACY_SCRIPTS + LEGACY_STYLES]
        inputs += ["templates/" + name for name in TEMPLATE_FILES]
        inputs += [path.relative_to(ROOT).as_posix() for path in (ROOT / "templates/partials").glob("*.html")]
        for name in inputs:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        self.project = json.loads((self.root / "project.json").read_text())

    def save(self):
        (self.root / "project.json").write_text(json.dumps(self.project, ensure_ascii=False), encoding="utf-8")

    def test_reproducible_and_only_public_files(self):
        (self.root / "README.md").write_text("private source", encoding="utf-8")
        first = build(self.root)
        second = build(self.root)
        self.assertEqual(first["files"], second["files"])
        self.assertEqual(first["version"], second["version"])
        self.assertEqual(set(first["files"]), set(PUBLIC_FILES))
        self.assertEqual(len(first["core_assets"]), len(set(first["core_assets"])))
        for path in (self.root / "_site").rglob("*"):
            if path.is_file():
                self.assertIn(path.relative_to(self.root / "_site").as_posix(), PUBLIC_FILES)

    def test_release_and_dates_propagate_from_one_value(self):
        self.project["latest_release"]["version"] = "9.8.7"
        self.project["latest_release"]["published"] = "2030-12-23"
        self.project["updated"] = "2030-12-24"
        self.save()
        files = build(self.root)["files"]
        for name in ("index.html", "brief.html", "proofs.html", "architecture.html", "progress.html", "llms.txt"):
            self.assertIn("v9.8.7", files[name].decode(), name)
        for name in ("index.html", "brief.html", "hub.html", "proofs.html", "architecture.html", "progress.html", "sitemap.xml"):
            self.assertIn("2030-12-24", files[name].decode(), name)
        self.assertIn("24. december 2030", files["index.html"].decode())
        self.assertIn("24 December 2030", files["en/index.html"].decode())
        self.assertIn("2030-12-23", files["llms.txt"].decode())
        manifest = json.loads(files["project.json"])
        self.assertTrue(manifest["latest_release"]["tag_url"].endswith("v9.8.7"))
        self.assertEqual(manifest["supporting_evidence"][0]["name"], "Kaliv v9.8.7 release")
        self.assertEqual(manifest["source_snapshot"]["recorded"], self.project["source_snapshot"]["recorded"])

    def test_proof_state_changes_counts_labels_and_descriptions(self):
        self.project["v1_proofs"][0]["status"] = "closed"
        self.save()
        files = build(self.root)["files"]
        self.assertIn("1<span>/4</span>", files["index.html"].decode())
        self.assertIn("1/4", files["brief.html"].decode())
        self.assertIn("1/4", files["progress.html"].decode())
        self.assertIn('>Bevist</span>', files["proofs.html"].decode())
        self.assertIn('>Proven</span>', files["en/proofs.html"].decode())
        self.assertIn('>Lukket</span>', files["progress.html"].decode())
        self.assertIn("three concrete results still missing", files["en/proofs.html"].decode())
        self.assertIn("Three of four public proof gates remain open.", files["llms.txt"].decode())

    def test_historical_heads_are_resolved_in_pages_and_manifest(self):
        key = "KalivHub-Receiver@physical-proof"
        self.project["source_snapshot"]["heads"][key] = "123abcd" + "0" * 33
        self.save()
        files = build(self.root)["files"]
        self.assertIn("123abcd", files["hub.html"].decode())
        self.assertIn("123abcd" + "0" * 33, files["llms.txt"].decode())
        manifest = json.loads(files["project.json"])
        receiver = next(item for item in manifest["components"] if item["name"] == "KalivHub-Receiver")
        self.assertIn("123abcd", receiver["status"])

    def test_asset_and_html_changes_invalidate_cache(self):
        before = build(self.root)
        target = self.root / "site.css"
        target.write_bytes(target.read_bytes() + b"\n/* changed CSS */\n")
        after = build(self.root)
        self.assertNotEqual(before["version"], after["version"])
        self.assertNotEqual(before["versions"]["site.css"], after["versions"]["site.css"])
        self.assertIn("site.css?v=" + after["versions"]["site.css"], after["files"]["index.html"].decode())
        self.assertIn("./site.css?v=" + after["versions"]["site.css"], after["core_assets"])
        for alias in LEGACY_STYLES:
            self.assertIn("site.css?v=" + after["versions"]["site.css"], after["files"][alias].decode())
        template = self.root / "templates/index.html"
        template.write_text(template.read_text() + "\n<!-- changed HTML -->\n", encoding="utf-8")
        self.assertNotEqual(after["version"], build(self.root)["version"])

    def test_generated_asset_urls_match_file_contents(self):
        import hashlib
        from urllib.parse import parse_qs, urlsplit
        result = build(self.root)
        for path in result["core_assets"]:
            url = urlsplit(path)
            if "v" in parse_qs(url.query):
                name = url.path.removeprefix("./")
                expected = hashlib.sha256(result["files"][name]).hexdigest()[:12]
                self.assertEqual(parse_qs(url.query)["v"], [expected])
        worker = result["files"]["service-worker.js"].decode()
        self.assertEqual(json.loads(re.search(r"const CORE_ASSETS = (\[[\s\S]*?\]);", worker)[1]), result["core_assets"])

    def test_invalid_template_preserves_last_valid_output(self):
        before = build(self.root)
        template = self.root / "templates/index.html"
        template.write_text(template.read_text() + "{{ missing.value }}", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Unknown template value"):
            build(self.root)
        self.assertEqual((self.root / "_site/index.html").read_bytes(), before["files"]["index.html"])

    def test_english_is_static_with_matching_metadata(self):
        result = build(self.root)
        for name in EN_FILES:
            document = Document(result["files"][name].decode())
            nodes = list(elements(document.root))
            self.assertEqual(next(n for n in nodes if n.tag == "html").attrs["lang"], "en")
            self.assertFalse(any(key.startswith(("data-en", "data-da")) for n in nodes for key in n.attrs))
            title = next(n for n in nodes if n.tag == "title")
            self.assertTrue(title.children)
            canonical = next((n.attrs["href"] for n in nodes if n.tag == "link" and n.attrs.get("rel") == "canonical"), None)
            if canonical:
                self.assertEqual(canonical, "https://kaliv.dk" + page_path(name.removeprefix("en/"), "en"))
                self.assertEqual(next(n.attrs["content"] for n in nodes if n.tag == "meta" and n.attrs.get("property") == "og:locale"), "en_US")
            for n in nodes:
                if n.tag == "script" and n.attrs.get("type") == "application/ld+json":
                    structured = json.loads("".join(n.children))
                    self.assertEqual(structured["inLanguage"], "en")
                    self.assertEqual(structured["url"], canonical)
        self.assertIn("The same AI.", result["files"]["en/index.html"].decode())
        self.assertNotIn("?lang=en", result["files"]["sitemap.xml"].decode())
        self.assertIn("https://kaliv.dk/en/", result["files"]["llms.txt"].decode())

    def test_language_links_work_without_translation_scripts(self):
        result = build(self.root)
        for filename in ("brief.html", "en/brief.html"):
            nodes = list(elements(Document(result["files"][filename].decode()).root))
            controls = [n for n in nodes if n.tag == "a" and n.attrs.get("data-language") in ("da", "en")]
            self.assertEqual({n.attrs["href"] for n in controls}, {"/brief.html", "/en/brief.html"})
            self.assertEqual(sum(n.attrs.get("aria-current") == "page" for n in controls), 1)
        for alias in LEGACY_SCRIPTS:
            self.assertIn("location.replace(target.href)", result["files"][alias].decode())
            self.assertNotIn("querySelectorAll", result["files"][alias].decode())

    def test_shared_brand_reaches_both_languages_and_each_navigation_is_current(self):
        partial = self.root / "templates/partials/brand.html"
        partial.write_text(partial.read_text().replace("<strong>Kaliv</strong>", "<strong>Kaliv build test</strong>"))
        result = build(self.root)
        for name in ("index", "brief", "hub", "architecture", "proofs", "progress", "download"):
            for prefix in ("", "en/"):
                html = result["files"][prefix + name + ".html"].decode()
                self.assertIn("<strong>Kaliv build test</strong>", html)
                nodes = list(elements(Document(html).root))
                styles = [n for n in nodes if n.tag == "link" and n.attrs.get("rel") == "stylesheet"]
                self.assertEqual(len(styles), 1)
                self.assertTrue(styles[0].attrs["href"].startswith("/site.css?v="))
                self.assertFalse(any(n.tag == "style" or (n.tag == "script" and not n.attrs.get("src") and n.attrs.get("type") != "application/ld+json") for n in nodes))
                nav = next(n for n in nodes if n.tag == "nav" and n.attrs.get("class") in ("header-actions", "primary-nav"))
                current = [n for n in nav.children if not isinstance(n, str) and n.attrs.get("aria-current") == "page"]
                self.assertEqual(len(current), 0 if name in ("index", "architecture") else 1)
                if current:
                    self.assertEqual(current[0].attrs["href"], "/" + prefix + name + ".html")

    def test_partial_failures_preserve_last_valid_output(self):
        before = build(self.root)
        partial = self.root / "templates/partials/brand.html"
        for source, message in (('{% include "missing" %}', "Unknown partial"), ('{% include "brand" %}', "Circular partial")):
            partial.write_text(source)
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                build(self.root)
            self.assertEqual((self.root / "_site/index.html").read_bytes(), before["files"]["index.html"])

    def test_csp_precedes_resources_and_tracks_generated_inline_metadata(self):
        from base64 import b64encode
        from hashlib import sha256
        before = build(self.root)
        for name, data in before["files"].items():
            if not name.endswith(".html"):
                continue
            nodes = list(elements(Document(data.decode()).root))
            head = next(n for n in nodes if n.tag == "head")
            children = [n for n in head.children if not isinstance(n, str)]
            self.assertIn("charset", children[0].attrs)
            self.assertEqual(children[1].attrs.get("http-equiv"), "Content-Security-Policy")
            policy = children[1].attrs["content"]
            self.assertNotIn("unsafe-", policy)
            self.assertIn("worker-src 'self'", policy)
            self.assertIn("base-uri 'none'", policy)
            self.assertNotIn("frame-ancestors", policy)
            for script in (n for n in nodes if n.tag == "script" and not n.attrs.get("src")):
                digest = b64encode(sha256("".join(script.children).encode()).digest()).decode()
                self.assertIn("'sha256-" + digest + "'", policy)
        self.project["updated"] = "2030-12-24"
        self.save()
        after = build(self.root)
        def policy(result):
            return next(n.attrs["content"] for n in elements(Document(result["files"]["en/index.html"].decode()).root) if n.attrs.get("http-equiv") == "Content-Security-Policy")
        self.assertNotEqual(policy(before), policy(after))

    def test_downloads_follow_the_reviewed_release_and_share_links_with_manifest(self):
        self.project["latest_release"]["version"] = "9.8.7"
        self.save()
        files = build(self.root)["files"]
        manifest = json.loads(files["project.json"])
        for locale in ("", "en/"):
            html = files[locale + "download.html"].decode()
            for name in ("windows", "android", "checksums"):
                asset = manifest["downloads"][name]
                self.assertTrue(asset["url"].startswith("https://github.com/Ternedal/ModelRig/releases/download/v9.8.7/"))
                self.assertIn(asset["url"], html)
            self.assertIn("-LiteralPath", html)
            self.assertIn("-Algorithm SHA256", html)
            self.assertIn(manifest["latest_release"]["url"], html)
        self.assertEqual(manifest["downloads"]["windows"]["filename"], "Kaliv-windows-x64-9.8.7.jar")

    def test_ecosystem_status_has_one_source_and_does_not_change_proof_states(self):
        for name in ("KalivNexus", "LanguageRig"):
            component = next(item for item in self.project["components"] if item["name"] == name)
            component["status"] = name + " status propagation test"
        self.save()
        files = build(self.root)["files"]
        manifest = json.loads(files["project.json"])
        for name in ("KalivNexus", "LanguageRig"):
            self.assertIn("https://github.com/Ternedal/" + name, manifest["repositories"])
            self.assertIn(name + " status propagation test", files["llms.txt"].decode())
        self.assertEqual([item["status"] for item in manifest["v1_proofs"]], ["open"] * 4)


if __name__ == "__main__":
    unittest.main()
