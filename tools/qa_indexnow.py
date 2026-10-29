#!/usr/bin/env python3
"""Offline regression tests for IndexNow selection and state handling."""
import contextlib
import hashlib
import io
import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest import mock

import submit_index as indexnow


SCRIPT_NO_INDEX = """<script>
if (location.hostname.endsWith('github.io')) {
  document.write('<meta name="robots" content="noindex,follow">');
}
</script>"""
INDEXABLE = f"<!doctype html><html><head>{SCRIPT_NO_INDEX}<meta name='robots' content='index,follow'></head><body>Page</body></html>"
NOINDEX = "<!doctype html><html><head><meta name='robots' content='noindex,follow'></head><body>Page</body></html>"


class OfflineTestCase(unittest.TestCase):
    def setUp(self):
        # No test may contact the real IndexNow endpoint, even if a key is set.
        guard = mock.patch.object(indexnow.urllib.request, "urlopen",
                                  side_effect=AssertionError("network is forbidden in QA"))
        guard.start()
        self.addCleanup(guard.stop)


class RobotsMetaTests(OfflineTestCase):
    def test_directives_and_inert_markup(self):
        cases = [
            ("<meta name='robots' content='noindex, follow'>", True),
            ("<META CONTENT='NOINDEX FOLLOW' NAME=' Robots '>", True),
            ("<meta name=robots content=none>", True),
            ("<meta name=robots content='index,follow'><meta name=robots content='noindex'>", True),
            ("<meta name=robots content='index,nofollow'>", False),
            ("<meta name=robots content='noimageindex,max-image-preview: none'>", False),
            ("<meta name=robots content='max-image-preview:none, noarchive'>", False),
            ("<meta name=googlebot content=noindex>", False),
            (SCRIPT_NO_INDEX + "<meta name=robots content=index>", False),
            ("<!-- <meta name='robots' content='noindex'> -->", False),
            ("<template><template><meta name=robots content=noindex></template></template>", False),
            ("<textarea><meta name=robots content=noindex></textarea>", False),
            ("<title><meta name=robots content=noindex></title>", False),
        ]
        for html, expected in cases:
            with self.subTest(html=html):
                self.assertEqual(indexnow.is_noindex(html), expected)


class SiteCoverageTests(OfflineTestCase):
    def test_sitemap_and_known_exclusions(self):
        root = Path(indexnow.ROOT)
        selected = {url for _rel, url, _digest in indexnow.iter_html_pages()}
        xml = ET.parse(root / "sitemap.xml")
        sitemap_urls = {el.text for el in xml.findall("{*}url/{*}loc")}
        self.assertTrue(sitemap_urls, "expected built sitemap URLs")
        self.assertFalse(sitemap_urls - selected,
                         f"sitemap URLs omitted from IndexNow: {sorted(sitemap_urls - selected)}")
        for path in ("/tools/", "/tools/canvas-calculator/"):
            self.assertIn(indexnow.SITE + path, selected)
        for path in ("/search.html", "/thank-you.html", "/404.html"):
            self.assertNotIn(indexnow.SITE + path, selected)


class StateAndSelectionTests(OfflineTestCase):
    def setUp(self):
        super().setUp()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.site = "https://example.test"
        self.state_path = self.root / "data" / "indexnow-state.json"
        patcher = mock.patch.multiple(indexnow, ROOT=str(self.root),
                                     STATE_PATH=str(self.state_path), SITE=self.site,
                                     KEY="offline-test-key")
        patcher.start()
        self.addCleanup(patcher.stop)
        self.write("index.html", INDEXABLE)
        self.write("tools/index.html", INDEXABLE)
        self.write("tools/canvas-calculator/index.html", INDEXABLE)
        self.write("search.html", NOINDEX)
        self.write("thank-you.html", NOINDEX)
        self.write("404.html", NOINDEX)
        self.write("tools/source.py", "# not an HTML page")
        self.write("docs/internal.html", INDEXABLE)
        self.write("data/internal.html", INDEXABLE)
        self.write(".git/internal.html", INDEXABLE)

    def write(self, rel, content):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def digest(self, rel):
        return hashlib.sha256((self.root / rel).read_bytes()).hexdigest()

    def selected(self):
        return {url: digest for _rel, url, digest in indexnow.iter_html_pages()}

    def write_state(self, version, pages, site=None):
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps({"version": version, "site": site or self.site,
                                               "updated": "2026-01-01T00:00:00Z",
                                               "pages": pages}), encoding="utf-8")

    def read_state(self):
        return json.loads(self.state_path.read_text(encoding="utf-8"))

    def run_main(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(indexnow.main(), 0)

    def legacy_pages(self):
        return {self.site + "/": self.digest("index.html"),
                self.site + "/search.html": self.digest("search.html"),
                self.site + "/thank-you.html": self.digest("thank-you.html")}

    def test_public_tools_included_and_noindex_excluded(self):
        self.assertEqual(set(self.selected()), {self.site + "/", self.site + "/tools/",
                                              self.site + "/tools/canvas-calculator/"})

    def test_v1_migration_submits_new_tools_not_legacy_noindex(self):
        legacy = self.legacy_pages()
        legacy[self.site + "/already-gone/"] = "unknown-prior-status"
        self.write_state(1, legacy)
        self.write("search.html", NOINDEX.replace("Page", "Updated legacy noindex page"))
        with mock.patch.object(indexnow, "submit", return_value=True) as submit:
            self.run_main()
        self.assertEqual(set(submit.call_args.args[0]),
                         {self.site + "/tools/", self.site + "/tools/canvas-calculator/"})
        state = self.read_state()
        self.assertEqual(state["version"], 2)
        self.assertEqual(state["pages"], self.selected())
        self.assertEqual(state["pages"][self.site + "/"], self.digest("index.html"))

    def test_v1_migration_without_submissions_cleans_up_state(self):
        self.write_state(1, {**self.legacy_pages(), **self.selected()})
        with mock.patch.object(indexnow, "submit") as submit:
            self.run_main()
        submit.assert_not_called()
        self.assertEqual(self.read_state()["version"], 2)
        self.assertEqual(self.read_state()["pages"], self.selected())

    def test_failed_submission_keeps_v1_state_and_retries(self):
        self.write_state(1, self.legacy_pages())
        original = self.state_path.read_bytes()
        with mock.patch.object(indexnow, "submit", side_effect=[False, True]) as submit:
            self.run_main()
            self.assertEqual(self.state_path.read_bytes(), original)
            self.run_main()
        self.assertEqual(submit.call_count, 2)
        self.assertEqual(submit.call_args_list[0], submit.call_args_list[1])
        self.assertEqual(self.read_state()["pages"], self.selected())

    def test_noindex_transition_retries_once_then_stays_excluded(self):
        self.write_state(2, self.selected())
        self.write("tools/index.html", NOINDEX)
        original = self.state_path.read_bytes()
        with mock.patch.object(indexnow, "submit", side_effect=[False, True, True]) as submit:
            with contextlib.redirect_stdout(io.StringIO()) as pending:
                self.assertEqual(indexnow.main(check_pending=True), 0)
            self.assertEqual(pending.getvalue().strip(), "true")
            self.run_main()
            self.assertEqual(self.state_path.read_bytes(), original)
            self.run_main()
            self.assertNotIn(self.site + "/tools/", self.read_state()["pages"])
            self.write("tools/index.html", NOINDEX.replace("Page", "Updated noindex page"))
            self.run_main()
            self.assertEqual(submit.call_count, 2, "routine noindex edits must not ping")
            self.write("tools/index.html", INDEXABLE)
            self.run_main()
        self.assertEqual([c.args[0] for c in submit.call_args_list],
                         [[self.site + "/tools/"], [self.site + "/tools/"],
                          [self.site + "/tools/"]])
        self.assertEqual(self.read_state()["pages"], self.selected())

    def test_changed_indexable_page_only(self):
        self.write_state(2, self.selected())
        self.write("index.html", INDEXABLE.replace("Page", "Changed page"))
        with mock.patch.object(indexnow, "submit", return_value=True) as submit:
            self.run_main()
        submit.assert_called_once_with([self.site + "/"])
        self.assertEqual(self.read_state()["pages"], self.selected())

    def test_removed_url_is_notified_once_and_retried_after_failure(self):
        self.write_state(2, self.selected())
        (self.root / "tools/index.html").unlink()
        original = self.state_path.read_bytes()
        with mock.patch.object(indexnow, "submit", side_effect=[False, True, True]) as submit:
            with contextlib.redirect_stdout(io.StringIO()) as pending:
                self.assertEqual(indexnow.main(check_pending=True), 0)
            self.assertEqual(pending.getvalue().strip(), "true")
            self.run_main()
            self.assertEqual(self.state_path.read_bytes(), original)
            self.run_main()
            self.run_main()
            self.assertEqual(submit.call_count, 2, "a removal should not be repeated after success")
            self.write("tools/index.html", INDEXABLE)
            self.run_main()
        self.assertEqual([c.args[0] for c in submit.call_args_list],
                         [[self.site + "/tools/"], [self.site + "/tools/"],
                          [self.site + "/tools/"]])
        self.assertEqual(self.read_state()["pages"], self.selected())

    def test_unreadable_tree_does_not_submit_or_overwrite_state(self):
        self.write_state(2, self.selected())
        original = self.state_path.read_bytes()

        def broken_walk(_root, onerror):
            onerror(PermissionError("unreadable directory"))
            yield  # make this a generator, like os.walk

        with mock.patch.object(indexnow.os, "walk", side_effect=broken_walk):
            with mock.patch.object(indexnow, "submit") as submit:
                with self.assertRaises(PermissionError):
                    self.run_main()
        submit.assert_not_called()
        self.assertEqual(self.state_path.read_bytes(), original)

    def test_other_site_state_cannot_generate_cross_host_transitions(self):
        self.write_state(2, {"https://other.test/search.html": "old"}, site="https://other.test")
        with mock.patch.object(indexnow, "submit", return_value=True) as submit:
            self.run_main()
        self.assertEqual(set(submit.call_args.args[0]), set(self.selected()))
        self.assertEqual(self.read_state()["site"], self.site)

    def test_invalid_state_fails_closed_without_submitting(self):
        for raw in ("{invalid", '{"version": 999, "pages": {}}',
                    '{"version": 2, "pages": {"https://example.test/": null}}'):
            with self.subTest(raw=raw):
                self.state_path.parent.mkdir(parents=True, exist_ok=True)
                self.state_path.write_text(raw, encoding="utf-8")
                with mock.patch.object(indexnow, "submit") as submit:
                    with self.assertRaises(ValueError):
                        self.run_main()
                submit.assert_not_called()
                self.assertEqual(self.state_path.read_text(encoding="utf-8"), raw)

    def test_state_write_failure_keeps_previous_manifest_for_retry(self):
        self.write_state(1, self.legacy_pages())
        original = self.state_path.read_bytes()
        with mock.patch.object(indexnow, "submit", return_value=True) as submit:
            with mock.patch.object(indexnow.os, "replace", side_effect=OSError("disk error")):
                with self.assertRaises(OSError):
                    self.run_main()
            self.assertEqual(self.state_path.read_bytes(), original)
            self.assertEqual(list(self.state_path.parent.glob(".indexnow-state-*.tmp")), [])
            self.run_main()
        self.assertEqual(submit.call_count, 2)
        self.assertEqual(submit.call_args_list[0], submit.call_args_list[1])
        self.assertEqual(self.read_state()["pages"], self.selected())

    def test_foreign_url_in_same_site_state_is_not_sent(self):
        self.write_state(2, {**self.selected(), "https://other.test/old/": "old"})
        with mock.patch.object(indexnow, "submit") as submit:
            self.run_main()
        submit.assert_not_called()
        self.assertNotIn("https://other.test/old/", indexnow.load_state()["pages"])

    def test_no_key_neither_submits_nor_writes(self):
        self.write_state(1, self.legacy_pages())
        original = self.state_path.read_bytes()
        with mock.patch.object(indexnow, "KEY", ""), mock.patch.object(indexnow, "submit") as submit:
            self.run_main()
        submit.assert_not_called()
        self.assertEqual(self.state_path.read_bytes(), original)

    def test_preview_and_retry_check_never_submit_or_write(self):
        self.write_state(1, self.legacy_pages())
        original = self.state_path.read_bytes()
        with mock.patch.object(indexnow, "submit") as submit:
            with contextlib.redirect_stdout(io.StringIO()) as pending:
                self.assertEqual(indexnow.main(check_pending=True), 0)
            self.assertEqual(pending.getvalue().strip(), "true")
            with mock.patch.object(indexnow, "KEY", ""):
                with contextlib.redirect_stdout(io.StringIO()) as pending_without_key:
                    self.assertEqual(indexnow.main(check_pending=True), 0)
                self.assertEqual(pending_without_key.getvalue().strip(), "false")
                with contextlib.redirect_stdout(io.StringIO()) as preview:
                    self.assertEqual(indexnow.main(dry_run=True), 0)
            self.assertIn(self.site + "/tools/", preview.getvalue())
            self.assertIn(self.site + "/tools/canvas-calculator/", preview.getvalue())
            self.assertNotIn(self.site + "/search.html", preview.getvalue())
            submit.assert_not_called()
            self.assertEqual(self.state_path.read_bytes(), original)

    def test_retry_check_ignores_routine_noindex_edits(self):
        self.write_state(2, self.selected())
        self.write("search.html", NOINDEX.replace("Page", "Edited noindex page"))
        with mock.patch.object(indexnow, "submit") as submit:
            with contextlib.redirect_stdout(io.StringIO()) as pending:
                self.assertEqual(indexnow.main(check_pending=True), 0)
            self.assertEqual(pending.getvalue().strip(), "false")
            submit.assert_not_called()

    def test_mocked_http_payload_and_responses(self):
        response = mock.MagicMock()
        response.__enter__.return_value.status = 202
        urls = [self.site + "/tools/", self.site + "/tools/canvas-calculator/"]
        with mock.patch.object(indexnow.urllib.request, "urlopen", return_value=response) as request:
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertTrue(indexnow.submit(urls))
        sent = request.call_args.args[0]
        self.assertEqual(sent.full_url, "https://api.indexnow.org/indexnow")
        self.assertEqual(sent.get_method(), "POST")
        self.assertEqual(json.loads(sent.data), {"host": "example.test", "key": "offline-test-key",
                                                 "keyLocation": self.site + "/offline-test-key.txt",
                                                 "urlList": urls})
        response.__enter__.return_value.status = 200
        with mock.patch.object(indexnow.urllib.request, "urlopen", return_value=response):
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertTrue(indexnow.submit(urls))
        response.__enter__.return_value.status = 204
        with mock.patch.object(indexnow.urllib.request, "urlopen", return_value=response):
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertFalse(indexnow.submit(urls))
        with mock.patch.object(indexnow.urllib.request, "urlopen", side_effect=OSError("offline")):
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertFalse(indexnow.submit(urls))


if __name__ == "__main__":
    unittest.main(verbosity=2)
