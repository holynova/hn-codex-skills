import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO_ROOT / "skills"


def load_module(name: str, rel_path: str):
    path = SKILLS_DIR / rel_path
    spec = importlib.util.spec_from_file_location(name, str(path))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


token_stats = load_module("hn_token_stats", "hn-token-stats/scripts/token_stats.py")
ai_update = load_module("hn_ai_update", "hn-ai-software-update/scripts/update_ai_software.py")
skills_sync = load_module("hn_skills_sync", "hn-skills-sync/scripts/sync_skills.py")
mole_clean = load_module("hn_mole_clean", "hn-clean/scripts/mole_cleanup.py")
hn_daily = load_module("hn_daily_orch", "hn-daily/scripts/hn_daily.py")


class TokenStatsTests(unittest.TestCase):
    def test_exact_reference_card_rendering(self):
        # Raw counts whose 1-wan rounded totals and week sum (10亿7,585万) match the prompt spec
        rows = [
            ("2026-11-19", 64_084_000),
            ("2026-11-20", 322_134_000),
            ("2026-11-21", 97_134_000),
            ("2026-11-22", 491_524_000),
            ("2026-11-23", 57_314_000),
            ("2026-11-24", 20_140_000),
            ("2026-11-25", 23_520_000),
        ]
        rendered = token_stats.render_card("Codex", rows)
        expected = "\n".join([
            "📊 Codex Token｜近7日（11/19–11/25）",
            "日期 | 进度条         | Token",
            "11/19 | █▋░░░░░░░░░░ | 6,408万",
            "11/20 | ███████▉░░░░ | 3亿2,213万",
            "11/21 | ██▍░░░░░░░░░ | 9,713万",
            "11/22 | ████████████ | 4亿9,152万",
            "11/23 | █▍░░░░░░░░░░ | 5,731万",
            "11/24 | ▌░░░░░░░░░░░ | 2,014万",
            "11/25 | ▋░░░░░░░░░░░ | 2,352万",
            "7日累计：约 10亿7,585万 Token",
            "注：含缓存，按1万取整；进度按周峰值，每格含1/8刻度。",
        ])
        self.assertEqual(rendered, expected)

    def test_edge_cases_format_and_bars(self):
        self.assertEqual(token_stats.format_cn_tokens(0), "0万")
        self.assertEqual(token_stats.format_cn_tokens(4_999), "<1万")
        self.assertEqual(token_stats.format_cn_tokens(100_000_000), "1亿")
        self.assertEqual(token_stats.render_bar(0, 100), "░░░░░░░░░░░░")
        self.assertEqual(token_stats.render_bar(1, 1_000_000), "▏░░░░░░░░░░░")
        self.assertEqual(token_stats.render_bar(100, 100), "████████████")

    def test_window_default_ends_yesterday(self):
        with self.subTest("default ends yesterday"):
            w = token_stats.compute_window(7, include_today=False, end_date_str=None, tz_name="Asia/Shanghai")
            self.assertEqual(len(w), 7)
            w_inc = token_stats.compute_window(7, include_today=True, end_date_str=None, tz_name="Asia/Shanghai")
            self.assertEqual(w[-1] < w_inc[-1], True)


class AiSoftwareUpdateTests(unittest.TestCase):
    def test_catalog_matching_and_semver(self):
        formula_cat = {"opencode", "mole", "claude-code"}
        self.assertTrue(ai_update.match_catalog_name("anomalyco/tap/opencode", formula_cat))
        self.assertTrue(ai_update.match_catalog_name("claude-code@latest", formula_cat))
        self.assertFalse(ai_update.match_catalog_name("ffmpeg", formula_cat))

        self.assertTrue(ai_update.matches_only("mole", {"mo"}))
        self.assertTrue(ai_update.matches_only("@google/gemini-cli", {"gemini"}))
        self.assertFalse(ai_update.matches_only("opencode", {"codex"}))

        self.assertTrue(ai_update.is_newer_version("0.2.1-rc.5", "0.2.2-rc.5"))
        self.assertFalse(ai_update.is_newer_version("0.2.1-rc.5", "0.2.1-rc.5"))
        self.assertTrue(ai_update.is_newer_version("1.7.0", "1.9.0"))
        self.assertFalse(ai_update.is_newer_version("1.0.0-beta.12", "0.9.0"))


class SkillsSyncTests(unittest.TestCase):
    def test_repo_discovery_excludes_backup_and_syncs_temp_home(self):
        active, archived = skills_sync.discover_repo_skills(REPO_ROOT)
        self.assertIn("hn-daily", active)
        self.assertIn("hn-ai-software-update", active)
        self.assertIn("hn-skills-sync", active)
        self.assertIn("hn-token-stats", active)
        self.assertIn("hn-clean", active)
        for arch in archived:
            self.assertNotIn(arch, active)

        with tempfile.TemporaryDirectory() as tmp:
            fake_home = Path(tmp)
            (fake_home / ".codex" / "skills").mkdir(parents=True)
            (fake_home / ".agents" / "skills" / "custom-third-party").mkdir(parents=True)
            (fake_home / ".agents" / "skills" / "custom-third-party" / "SKILL.md").write_text("keep me", encoding="utf-8")
            (fake_home / ".claude" / "skills").mkdir(parents=True)
            (fake_home / ".gemini" / "config" / "skills").mkdir(parents=True)

            dry = skills_sync.sync_all(
                apply=False,
                repo="holynova/hn-codex-skills",
                local_repo=str(REPO_ROOT),
                skip_third_party=True,
                skip_hn_skills=False,
                home=fake_home,
            )
            self.assertEqual(set(dry["hn_skills"]["added"]), set(active))

            applied = skills_sync.sync_all(
                apply=True,
                repo="holynova/hn-codex-skills",
                local_repo=str(REPO_ROOT),
                skip_third_party=True,
                skip_hn_skills=False,
                home=fake_home,
            )
            self.assertEqual(applied["hn_skills"]["status"], "ok")
            self.assertEqual(applied["hn_skills"]["archived_present"], [])
            self.assertTrue((fake_home / ".codex" / "skills" / "hn-daily" / "SKILL.md").is_file())
            self.assertTrue((fake_home / ".agents" / "skills" / "hn-daily" / "SKILL.md").is_file())
            self.assertTrue((fake_home / ".claude" / "skills" / "hn-daily").is_symlink())
            self.assertTrue((fake_home / ".gemini" / "config" / "skills" / "hn-daily").is_symlink())
            # Unrelated third-party skill preserved
            self.assertEqual((fake_home / ".agents" / "skills" / "custom-third-party" / "SKILL.md").read_text(), "keep me")


class MoleCleanupTests(unittest.TestCase):
    def test_df_and_mole_output_parsers(self):
        df_sample = (
            "Filesystem   1024-blocks      Used Available Capacity iused     ifree %iused  Mounted on\n"
            "/dev/disk3s5   239362496 208000000  19776102    92%  500000 100000000    0%   /System/Volumes/Data\n"
        )
        parsed = mole_clean.parse_df_k(df_sample)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["avail_kb"], 19776102)
        self.assertEqual(parsed["mount_point"], "/System/Volumes/Data")

        clean_sample = (
            "\x1b[32m  → Homebrew cache · 383.8MB dry\x1b[0m\n"
            "  ⊙ pnpm store · 1.57GB · ~/Library/pnpm/store\n"
            "  ⊙ Build artifacts · 4+ dirs, 243.6MB+ · mo purge\n"
            "Potential space: 6.97GB | Items: 303 | Categories: 6\n"
            "Detailed file list: ~/.config/mole/clean-list.txt\n"
        )
        c_parsed = mole_clean.parse_clean_output(mole_clean.strip_ansi(clean_sample))
        self.assertEqual(c_parsed["potential_space"], "6.97GB")
        self.assertEqual(c_parsed["items"], 303)
        self.assertEqual(c_parsed["categories"], 6)
        self.assertEqual(len(c_parsed["advisories"]), 2)

        opt_sample = (
            "  ◎ Broken login item: Steam (app not found)\n"
            "Would apply 2 optimizations\n"
            "13 unchanged | 2 skipped | 2 need attention | 1 failed\n"
        )
        o_parsed = mole_clean.parse_optimize_output(opt_sample)
        self.assertEqual(o_parsed["planned_count"], 2)
        self.assertEqual(len(o_parsed["attention_items"]), 1)
        self.assertEqual(mole_clean.classify_optimize_apply(1, "", "sudo: a password is required", False), "needs_admin")
        self.assertEqual(mole_clean.classify_clean_apply(243, "Space freed: 1.2GB", "EACCES", False), "partial")


class DailyOrchestratorTests(unittest.TestCase):
    def test_dag_parallel_and_serial_order_and_failure_isolation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mock_specs = {
                "hn-ai-software-update/scripts/update_ai_software.py": (
                    "import json, sys, time\n"
                    "time.sleep(0.25)\n"
                    "print(json.dumps({'status': 'partial', 'upgraded': [], 'outdated': [], 'already_latest': [], 'manual_apps': [], 'issues': [{'name':'x','manager':'m','message':'warn'}]}))\n"
                ),
                "hn-token-stats/scripts/token_stats.py": (
                    "import json, time\n"
                    "time.sleep(0.25)\n"
                    "print(json.dumps({'status': 'ok', 'cards': [{'agent':'codex','label':'Codex','text':'📊 ok'}]}))\n"
                ),
                "hn-skills-sync/scripts/sync_skills.py": (
                    "import json, time\n"
                    "time.sleep(0.05)\n"
                    "print(json.dumps({'status': 'ok', 'repo':'r', 'third_party':{'status':'ok','updated':[],'unchanged':[]}, 'hn_skills':{'status':'ok','active_count':1,'added':[],'updated':[],'symlink_repairs':[],'warnings':[]}}))\n"
                ),
                "hn-clean/scripts/mole_cleanup.py": (
                    "import json, time\n"
                    "time.sleep(0.05)\n"
                    "print(json.dumps({'status': 'ok', 'clean':{'status':'ok','dry_run':{}}, 'optimize':{'status':'ok','dry_run':{}}}))\n"
                ),
            }
            for rel, code in mock_specs.items():
                p = root / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(code, encoding="utf-8")

            report = hn_daily.orchestrate(apply=True, skills_root=root)
            st = report["stages"]

            # Stage 1 overlap: both start before either finishes
            self.assertLess(st["tokens"]["started_epoch"], st["update"]["ended_epoch"])
            self.assertLess(st["update"]["started_epoch"], st["tokens"]["ended_epoch"])

            # Stage 2 runs after Stage 1 update completes
            self.assertGreaterEqual(st["skills"]["started_epoch"], st["update"]["ended_epoch"] - 0.01)

            # Stage 3 runs after Stage 1 & Stage 2 complete
            self.assertGreaterEqual(st["clean"]["started_epoch"], st["skills"]["ended_epoch"] - 0.01)
            self.assertGreaterEqual(st["clean"]["started_epoch"], st["tokens"]["ended_epoch"] - 0.01)

            # Failure isolation: partial update still lets clean & tokens finish
            self.assertEqual(st["tokens"]["status"], "ok")
            self.assertEqual(st["clean"]["status"], "ok")
            md = hn_daily.render_markdown(report)
            self.assertIn("📊 ok", md)


if __name__ == "__main__":
    unittest.main()
