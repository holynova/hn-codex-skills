import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

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

    def test_heavy_brew_source_build_detection(self):
        sample = (
            "==> Would upgrade 1 requested outdated package\n"
            "anomalyco/tap/opencode 1.18.31 -> 1.19.6\n"
            "==> 3 homebrew/core formulae that would build from source\n"
            "llvm\n"
            "rust\n"
            "ripgrep\n"
            "\n"
            "This is a Tier 3 configuration:\n"
        )
        detected = ai_update.detect_heavy_brew_source_build(sample)
        self.assertEqual(detected, ["llvm", "rust", "ripgrep"])
        self.assertEqual(ai_update.detect_heavy_brew_source_build("==> Upgrading 1 outdated package:\nmole 1.58.0 -> 1.74.0\n"), [])

    def test_uv_already_latest_classification(self):
        bucket1, entry1 = ai_update.classify_uv_upgrade("notebooklm-mcp-cli", "0.16.6", "0.16.6", "Nothing to upgrade")
        self.assertEqual(bucket1, "already_latest")
        self.assertEqual(entry1["version"], "0.16.6")

        bucket2, entry2 = ai_update.classify_uv_upgrade("notebooklm-mcp-cli", "0.16.6", "0.16.6", "")
        self.assertEqual(bucket2, "already_latest")

        bucket3, entry3 = ai_update.classify_uv_upgrade("notebooklm-mcp-cli", "0.12.0", "0.16.6", "Upgraded notebooklm-mcp-cli v0.12.0 -> v0.16.6")
        self.assertEqual(bucket3, "upgraded")
        self.assertEqual(entry3["after"], "0.16.6")


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

        mole_174_apply = (
            "Cleanup complete\n"
            "Removed: 3.06GB · 160 items\n"
            "Free space: 24.81GB (+5.96GB)\n"
        )
        c174 = mole_clean.parse_clean_output(mole_174_apply)
        self.assertEqual(c174["freed_space"], "3.06GB · 160 items")
        self.assertEqual(c174["items"], 160)

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
        self.assertEqual(mole_clean.classify_clean_apply(124, "", "", True), "skipped_timeout")

    def test_apply_skips_redundant_dry_run_unless_with_preview(self):
        calls = []

        def fake_run(cmd, timeout):
            calls.append(cmd)
            if cmd[1] == "--version":
                return 0, "Mole version 1.74.0", "", False
            if cmd[1] == "clean":
                return 0, "Removed: 1.0GB · 10 items\n", "", False
            if cmd[1] == "optimize":
                return 0, "Applied 2 optimizations\n", "", False
            return 0, "", "", False

        with mock.patch.object(mole_clean, "find_mole", return_value="/opt/homebrew/bin/mo"), \
             mock.patch.object(mole_clean, "measure_volume", return_value={"mount_point": "/", "avail_kb": 1024, "avail_gb": 1.0}), \
             mock.patch.object(mole_clean, "run_cmd", side_effect=fake_run):
            res = mole_clean.execute(apply=True, skip_clean=False, skip_optimize=False, timeout=90, with_preview=False)
            self.assertEqual(res["status"], "ok")
            self.assertNotIn("dry_run", res["clean"])
            self.assertNotIn("dry_run", res["optimize"])
            self.assertEqual([c[1:] for c in calls], [["--version"], ["clean"], ["optimize"]])

    def test_clean_mandatory_long_timeout_defaults(self):
        self.assertGreaterEqual(mole_clean.parse_args([]).timeout, 900)
        self.assertGreaterEqual(hn_daily.DEFAULT_STAGE_TIMEOUTS["clean"], 1000)


class DailyOrchestratorTests(unittest.TestCase):
    def test_dag_parallel_and_serial_order_and_streaming_plan_c(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mock_specs = {
                "hn-ai-software-update/scripts/update_ai_software.py": (
                    "import json, time\n"
                    "time.sleep(0.25)\n"
                    "print(json.dumps({'status': 'partial', 'upgraded': [{'name':'mole','manager':'brew-formula','before':'1.58','after':'1.74'}], 'outdated': [], 'already_latest': [{'name':'codex'}], 'manual_apps': [], 'issues': [{'name':'opencode','manager':'brew-formula','message':'needs_manual: src'}]}))\n"
                ),
                "hn-token-stats/scripts/token_stats.py": (
                    "import json, time\n"
                    "time.sleep(0.05)\n"
                    "card = '📊 Codex Token｜近7日（11/19–11/25）\\n日期 | 进度条         | Token\\n11/19 | ████████████ | 1,000万\\n7日累计：约 1,000万 Token\\n注：含缓存，按1万取整；进度按周峰值，每格含1/8刻度。'\n"
                    "print(json.dumps({'status': 'ok', 'combined_total': 10000000, 'cards': [{'agent':'codex','label':'Codex','text': card}]}))\n"
                ),
                "hn-skills-sync/scripts/sync_skills.py": (
                    "import json, time\n"
                    "time.sleep(0.05)\n"
                    "print(json.dumps({'status': 'ok', 'repo':'holynova/hn-codex-skills', 'third_party':{'status':'ok','updated':['a'],'unchanged':[]}, 'hn_skills':{'status':'ok','active_count':30,'added':['hn-daily'],'updated':[],'symlink_repairs':[],'warnings':[]}}))\n"
                ),
                "hn-clean/scripts/mole_cleanup.py": (
                    "import json, time\n"
                    "time.sleep(0.05)\n"
                    "print(json.dumps({'status': 'ok', 'before_disk': {'avail_gb': 10.0}, 'after_disk': {'avail_gb': 12.0}, 'observed_delta_kb': 2097152, 'clean':{'status':'ok','apply':{'freed_space':'2.0GB · 10 items','advisories':['pnpm store · 2GB']}}, 'optimize':{'status':'ok','apply':{'applied_count':2}}}))\n"
                ),
            }
            for rel, code in mock_specs.items():
                p = root / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(code, encoding="utf-8")

            streamed = []
            report = hn_daily.orchestrate(
                apply=True,
                skills_root=root,
                on_stage_done=lambda stage, st, idx, tot: streamed.append((stage, idx, tot, st["ended_epoch"])),
            )
            st = report["stages"]

            # Streaming fired immediately: tokens (0.05s) finished strictly before update (0.25s) ended!
            self.assertEqual([x[0] for x in streamed], ["tokens", "update", "skills", "clean"])
            self.assertLess(streamed[0][3], st["update"]["ended_epoch"])
            self.assertEqual([x[1] for x in streamed], [1, 2, 3, 4])

            # Serial constraints
            self.assertGreaterEqual(st["skills"]["started_epoch"], st["update"]["ended_epoch"] - 0.01)
            self.assertGreaterEqual(st["clean"]["started_epoch"], st["skills"]["ended_epoch"] - 0.01)

            # Plan C concise format + embedded 7-day graphical card
            md = hn_daily.render_markdown(report)
            self.assertIn("⚠️ Daily 汇总｜", md)
            self.assertIn("更新 1 项 · 同步 2 技能 · 可用空间 +2.00 GB（→ 12.00 GB） · 7日 1,000万 Token", md)
            self.assertIn("- **软件（⚠️）**：", md)
            self.assertIn("- **Skills（✅）**：", md)
            self.assertIn("- **清理（✅）**：", md)
            self.assertIn("11/19 | ████████████ | 1,000万", md)

    def test_fast_fail_timeout_skips_slow_step_without_blocking(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mock_specs = {
                "hn-ai-software-update/scripts/update_ai_software.py": "import time\ntime.sleep(3.0)\n",
                "hn-token-stats/scripts/token_stats.py": (
                    "import json\n"
                    "print(json.dumps({'status': 'ok', 'combined_total': 100000, 'cards': [{'agent':'codex','label':'Codex','text':'📊 ok'}]}))\n"
                ),
                "hn-skills-sync/scripts/sync_skills.py": (
                    "import json\n"
                    "print(json.dumps({'status': 'ok', 'repo':'r', 'third_party':{'status':'ok','updated':[],'unchanged':[]}, 'hn_skills':{'status':'ok','active_count':1,'added':[],'updated':[],'symlink_repairs':[],'warnings':[]}}))\n"
                ),
                "hn-clean/scripts/mole_cleanup.py": (
                    "import json\n"
                    "print(json.dumps({'status': 'ok', 'clean':{'status':'ok','apply':{'freed_space':'1MB'}}, 'optimize':{'status':'ok','apply':{'applied_count':1}}}))\n"
                ),
            }
            for rel, code in mock_specs.items():
                p = root / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(code, encoding="utf-8")

            t0 = time.time()
            report = hn_daily.orchestrate(
                apply=True,
                skills_root=root,
                stage_timeouts={"update": 0.25, "tokens": 5, "skills": 5, "clean": 5},
            )
            elapsed = time.time() - t0
            self.assertLess(elapsed, 2.0)
            self.assertEqual(report["stages"]["update"]["status"], "skipped_timeout")
            self.assertEqual(report["stages"]["tokens"]["status"], "ok")
            self.assertEqual(report["stages"]["skills"]["status"], "ok")
            self.assertEqual(report["stages"]["clean"]["status"], "ok")
            md = hn_daily.render_markdown(report)
            self.assertIn("- **软件（⏭️）**：已跳过（超时", md)


if __name__ == "__main__":
    unittest.main()
