#!/usr/bin/env python3
"""GitHub Telemetry and Metrics Extraction Engine."""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Final, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("TelemetryExtractor")

DEFAULT_BOT_ACCOUNTS: Final[frozenset[str]] = frozenset({
    "actions-user",
    "github-actions[bot]",
    "dependabot[bot]",
    "dependabot-preview[bot]",
    "imgbot[bot]",
    "greenkeeper[bot]",
    "renovate[bot]",
    "snyk-bot",
})

REFERRER_CHANNELS: Final[tuple[tuple[str, str, str], ...]] = (
    ("linkedin", "LinkedIn", "share-2"),
    ("telegram", "Telegram", "send"),
    ("t.me", "Telegram", "send"),
    ("google", "Google Search", "search"),
    ("github", "GitHub", "github"),
    ("twitter", "X (Twitter)", "twitter"),
    ("t.co", "X (Twitter)", "twitter"),
    ("x.com", "X (Twitter)", "twitter"),
    ("facebook", "Facebook", "share-2"),
    ("fb.me", "Facebook", "share-2"),
    ("reddit", "Reddit", "message-square"),
    ("youtube", "YouTube", "video"),
)


@dataclass(slots=True, frozen=True)
class BrandConfig:
    """Branding presentation attributes for the dashboard."""

    prefix: str = "open"
    middle: str = "source"
    suffix: str = ".stats"
    prefix_color: str = "#22c55e"
    suffix_color: str = "#f43f5e"
    tagline: str = "TELEMETRÍA & OBSERVABILIDAD"


@dataclass(slots=True, frozen=True)
class RepoVisualOverride:
    """Custom overrides for repository presentation cards."""

    badge: Optional[str] = None
    featured: bool = False
    accent_color: str = "border-t-zinc-700"
    icon: str = "box"


@dataclass(slots=True, frozen=True)
class ExtractorConfig:
    """Runtime configuration resolved from environment and JSON."""

    target: str = "shellaquiles"
    is_org: bool = True
    title: str = "stats — Telemetría & Métricas Open Source"
    brand: BrandConfig = field(default_factory=BrandConfig)
    links: dict[str, str] = field(default_factory=dict)
    exclude_repos: frozenset[str] = field(default_factory=lambda: frozenset({"stats"}))
    repo_overrides: dict[str, RepoVisualOverride] = field(default_factory=dict)
    output_json: Path = field(default_factory=lambda: Path("data.json"))

    @classmethod
    def from_source(cls, config_path: Optional[Path] = None) -> ExtractorConfig:
        """Construct configuration prioritizing env vars over file settings."""
        file_path = config_path or Path(os.getenv("STATS_CONFIG_FILE", "config.json"))
        file_data: dict[str, Any] = {}

        if file_path.is_file():
            try:
                with file_path.open("r", encoding="utf-8") as f:
                    file_data = json.load(f)
            except (json.JSONDecodeError, OSError) as exc:
                logger.warning("Failed loading config file '%s': %s", file_path, exc)

        target = os.getenv("STATS_TARGET") or file_data.get("target", "shellaquiles")
        is_org = (
            os.getenv("STATS_IS_ORG", "").lower() in ("true", "1")
            if "STATS_IS_ORG" in os.environ
            else file_data.get("is_org", True)
        )
        title = os.getenv("STATS_TITLE") or file_data.get(
            "title", f"stats.{target} — Telemetría Open Source"
        )

        brand_data = file_data.get("brand", {})
        brand = BrandConfig(
            prefix=os.getenv("STATS_BRAND_PREFIX") or brand_data.get("prefix", target[:5] if len(target) >= 5 else target),
            middle=os.getenv("STATS_BRAND_MIDDLE") or brand_data.get("middle", target[5:] if len(target) >= 5 else ""),
            suffix=os.getenv("STATS_BRAND_SUFFIX") or brand_data.get("suffix", ".org" if is_org else ".dev"),
            prefix_color=os.getenv("STATS_BRAND_PREFIX_COLOR") or brand_data.get("prefix_color", "#22c55e"),
            suffix_color=os.getenv("STATS_BRAND_SUFFIX_COLOR") or brand_data.get("suffix_color", "#f43f5e"),
            tagline=os.getenv("STATS_TAGLINE") or brand_data.get("tagline", "ECOSISTEMA OPEN SOURCE"),
        )

        links_data = file_data.get("links", {})
        links = {
            "github": os.getenv("STATS_GITHUB_URL") or links_data.get("github", f"https://github.com/{target}"),
            "website": os.getenv("STATS_WEBSITE_URL") or links_data.get("website", f"https://{target}.org"),
        }

        env_exclude = os.getenv("STATS_EXCLUDE_REPOS")
        if env_exclude:
            exclude_repos = frozenset(r.strip() for r in env_exclude.split(",") if r.strip())
        else:
            exclude_repos = frozenset(file_data.get("exclude_repos", ["stats"]))

        raw_overrides = file_data.get("custom_repo_overrides", {})
        repo_overrides = {
            name: RepoVisualOverride(
                badge=opts.get("badge"),
                featured=opts.get("featured", False),
                accent_color=opts.get("accent_color", "border-t-zinc-700"),
                icon=opts.get("icon", "box"),
            )
            for name, opts in raw_overrides.items()
        }

        output_path = Path(os.getenv("STATS_DATA_OUTPUT", "data.json"))

        return cls(
            target=target,
            is_org=is_org,
            title=title,
            brand=brand,
            links=links,
            exclude_repos=exclude_repos,
            repo_overrides=repo_overrides,
            output_json=output_path,
        )


class GitHubTelemetryExtractor:
    """Extracts, normalizes, and aggregates telemetry metrics from GitHub."""

    __slots__ = ("config",)

    def __init__(self, config: ExtractorConfig) -> None:
        self.config = config

    @staticmethod
    def _gh_api(endpoint: str) -> Any:
        """Call GitHub API via GitHub CLI and return parsed JSON."""
        return GitHubTelemetryExtractor._run_gh("api", endpoint)

    @staticmethod
    def _run_gh(*args: str) -> Any:
        """Run gh CLI command with structured error suppression."""
        try:
            res = subprocess.run(
                ["gh", *args],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
            )
            return json.loads(res.stdout)
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            return None

    @staticmethod
    def normalize_referrer(raw_name: Optional[str]) -> tuple[str, str]:
        """Map referrer strings to canonical channels and icons."""
        if not raw_name:
            return "Directo", "globe"
        lower_name = raw_name.lower()
        for pattern, canonical, icon in REFERRER_CHANNELS:
            if pattern in lower_name:
                return canonical, icon
        return raw_name, "globe"

    @staticmethod
    def is_bot(login: Optional[str]) -> bool:
        """Identify automated bot and service accounts."""
        return not login or login in DEFAULT_BOT_ACCOUNTS or login.endswith("[bot]")

    def discover_repositories(self) -> list[str]:
        """Query target for all active, non-archived public repositories."""
        logger.info("Discovering public repositories for '%s'...", self.config.target)
        payload = self._run_gh(
            "repo",
            "list",
            self.config.target,
            "--json",
            "name,isArchived,isFork,isPrivate",
            "--limit",
            "100",
        )
        if not isinstance(payload, list):
            logger.warning("Repository discovery failed or returned empty payload.")
            return []

        discovered = [
            repo["name"]
            for repo in payload
            if not repo.get("isArchived")
            and not repo.get("isPrivate")
            and repo.get("name") not in self.config.exclude_repos
        ]
        logger.info("Discovered %d active repositories: %s", len(discovered), ", ".join(discovered))
        return discovered

    def _resolve_visuals(self, repo_name: str, language: str) -> tuple[Optional[str], bool, str, str]:
        """Resolve visual badges, border accents and icons."""
        if repo_name in self.config.repo_overrides:
            ov = self.config.repo_overrides[repo_name]
            return ov.badge, ov.featured, ov.accent_color, ov.icon

        lang = language.lower()
        if "python" in lang:
            return None, False, "border-t-[#1e3a8a]", "code-2"
        if "javascript" in lang or "typescript" in lang:
            return None, False, "border-t-[#b45309]", "layout"
        if "shell" in lang or "bash" in lang:
            return None, False, "border-t-[#046a38]", "terminal"
        if "css" in lang or "html" in lang:
            return None, False, "border-t-zinc-400", "file-code"
        return None, False, "border-t-zinc-600", "folder-git-2"

    def fetch_repository_metrics(self, repo_name: str) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
        """Collect all metrics for a single repository."""
        full_repo = f"{self.config.target}/{repo_name}"

        info = self._run_gh(
            "repo",
            "view",
            full_repo,
            "--json",
            "name,description,url,homepageUrl,createdAt,updatedAt,pushedAt,stargazerCount,forkCount,diskUsage,licenseInfo,repositoryTopics,primaryLanguage",
        ) or {}

        views_data = self._gh_api(f"repos/{full_repo}/traffic/views") or {}
        clones_data = self._gh_api(f"repos/{full_repo}/traffic/clones") or {}
        raw_referrers = self._gh_api(f"repos/{full_repo}/traffic/popular/referrers") or []
        releases = self._gh_api(f"repos/{full_repo}/releases") or []
        prs = self._run_gh("pr", "list", "-R", full_repo, "--state", "all", "--json", "number") or []
        contribs = self._gh_api(f"repos/{full_repo}/contributors") or []

        valid_contribs = [c for c in contribs if not self.is_bot(c.get("login"))]
        total_commits = sum(c.get("contributions", 0) for c in valid_contribs)

        # Referrer aggregation
        normalized_refs: dict[str, dict[str, Any]] = {}
        for r in raw_referrers:
            canon, icon = self.normalize_referrer(r.get("referrer"))
            entry = normalized_refs.setdefault(canon, {"name": canon, "views": 0, "uniques": 0, "icon": icon})
            entry["views"] += r.get("count", 0)
            entry["uniques"] += r.get("uniques", 0)

        primary_lang = (info.get("primaryLanguage") or {}).get("name", "Other")
        badge, featured, accent_color, icon = self._resolve_visuals(repo_name, primary_lang)
        topics = [t["name"] for t in (info.get("repositoryTopics") or [])]
        license_name = (info.get("licenseInfo") or {}).get("name", "None")
        clean_license = (
            license_name.replace(" License", "")
            .replace("General Public v3.0", "GPL-3.0")
            .replace("General Public License", "GPL")
        )

        repo_dict = {
            "name": info.get("name", repo_name),
            "description": info.get("description") or "",
            "url": info.get("url", f"https://github.com/{full_repo}"),
            "homepageUrl": info.get("homepageUrl") or "",
            "created_at": (info.get("createdAt") or "2026-01-01")[:10],
            "stars": info.get("stargazerCount", 0),
            "forks": info.get("forkCount", 0),
            "commits": total_commits,
            "contributors": len(valid_contribs) if valid_contribs else 1,
            "language": primary_lang,
            "license": clean_license,
            "clones_14d": clones_data.get("count", 0),
            "clones_uniques_14d": clones_data.get("uniques", 0),
            "views_14d": views_data.get("count", 0),
            "uniques_14d": views_data.get("uniques", 0),
            "releases": len(releases),
            "prs": len(prs),
            "featured": featured,
            "badge": badge,
            "icon": icon,
            "accentColor": accent_color,
            "topics": topics,
            "referrers": list(normalized_refs.values()),
        }

        return repo_dict, list(normalized_refs.values()), valid_contribs

    def run(self) -> None:
        """Execute full extraction pipeline and export data.json."""
        repositories = self.discover_repositories()
        repos_data: list[dict[str, Any]] = []
        global_referrers: dict[str, dict[str, Any]] = {}
        global_contributors: dict[str, dict[str, Any]] = {}

        for repo_name in repositories:
            logger.info("Processing repository: %s/%s...", self.config.target, repo_name)
            repo_item, repo_refs, repo_contribs = self.fetch_repository_metrics(repo_name)
            repos_data.append(repo_item)

            for ref in repo_refs:
                entry = global_referrers.setdefault(
                    ref["name"], {"name": ref["name"], "views": 0, "uniques": 0, "icon": ref["icon"]}
                )
                entry["views"] += ref["views"]
                entry["uniques"] += ref["uniques"]

            for c in repo_contribs:
                login = c["login"]
                entry = global_contributors.setdefault(
                    login,
                    {
                        "login": login,
                        "avatar_url": c.get("avatar_url"),
                        "html_url": c.get("html_url"),
                        "contributions": 0,
                        "repos_count": 0,
                        "repos": [],
                    },
                )
                entry["contributions"] += c.get("contributions", 0)
                entry["repos_count"] += 1
                entry["repos"].append(repo_name)

        sorted_contributors = sorted(
            global_contributors.values(), key=lambda x: x["contributions"], reverse=True
        )
        sorted_referrers = sorted(
            global_referrers.values(), key=lambda x: x["views"], reverse=True
        )

        payload = {
            "meta": {
                "target": self.config.target,
                "is_org": self.config.is_org,
                "title": self.config.title,
                "brand": asdict(self.config.brand),
                "links": self.config.links,
            },
            "summary": {
                "total_stars": sum(d["stars"] for d in repos_data),
                "total_forks": sum(d["forks"] for d in repos_data),
                "total_commits": sum(d["commits"] for d in repos_data),
                "total_clones_14d": sum(d["clones_14d"] for d in repos_data),
                "total_clones_uniques_14d": sum(d["clones_uniques_14d"] for d in repos_data),
                "total_views_14d": sum(d["views_14d"] for d in repos_data),
                "total_views_uniques_14d": sum(d["uniques_14d"] for d in repos_data),
                "total_releases": sum(d["releases"] for d in repos_data),
                "total_prs": sum(d["prs"] for d in repos_data),
                "total_repos": len(repos_data),
                "total_contributors": len(sorted_contributors),
            },
            "repos": repos_data,
            "referrers": sorted_referrers,
            "contributors": sorted_contributors,
        }

        with self.config.output_json.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        logger.info("✅ Telemetry exported successfully to %s", self.config.output_json)


def main() -> None:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description="Extract GitHub telemetry into data.json.")
    parser.add_argument("--config", "-c", type=Path, default=None, help="Path to config.json")
    args = parser.parse_args()

    config = ExtractorConfig.from_source(config_path=args.config)
    extractor = GitHubTelemetryExtractor(config=config)
    extractor.run()


if __name__ == "__main__":
    main()
