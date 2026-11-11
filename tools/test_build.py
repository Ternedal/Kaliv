"""Exercise propagation, reproducibility, cache invalidation and build failures."""

import json
from pathlib import Path
import re
import shutil
import tempfile
import unittest

from build import PUBLIC_FILES, ROOT, TEMPLATE_FILES, EN_FILES, LEGACY_SCRIPTS, Document, elements, build, page_path


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        inputs = [name for name in PUBLIC_FILES if name not in TEMPLATE_FILES and name not in EN_FILES and name not in LEGACY_SCRIPTS]
        inputs += ["templates/" + name for name in TEMPLATE_FILES]
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
        target = self.root / "home.css"
        target.write_bytes(target.read_bytes() + b"\n/* changed CSS */\n")
        after = build(self.root)
        self.assertNotEqual(before["version"], after["version"])
        self.assertNotEqual(before["versions"]["home.css"], after["versions"]["home.css"])
        self.assertIn("home.css?v=" + after["versions"]["home.css"], after["files"]["index.html"].decode())
        self.assertIn("./home.css?v=" + after["versions"]["home.css"], after["core_assets"])
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


if __name__ == "__main__":
    unittest.main()
