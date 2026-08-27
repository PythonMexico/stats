#!/usr/bin/env python3
"""
Telemetry Extractor for GitHub Profiles and Organizations.

100% Generic, Zero-Hardcode, Fork-Ready Engine.
Discovers repositories, extracts lifetime and 14-day telemetry,
normalizes traffic channels, and exports pure data.json.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("TelemetryExtractor")

@dataclass
class BrandConfig:
    prefix: str = "open"
    middle: str = "source"
    suffix: str = ".stats"
    prefix_color: str = "#22c55e"
    suffix_color: str = "#f43f5e"
    tagline: str = "TELEMETRÍA & OBSERVABILIDAD"

@dataclass
class RepoVisualOverride:
    badge: Optional[str] = None
    featured: bool = False
    accent_color: str = "border-t-zinc-700"
    icon: str = "box"

@dataclass
class ExtractorConfig:
    target: str = "shellaquiles"
    is_org: bool = True
    title: str = "stats — Telemetría & Métricas Open Source"
    brand: BrandConfig = field(default_factory=BrandConfig)
    links: Dict[str, str] = field(default_factory=dict)
    exclude_repos: List[str] = field(default_factory=lambda: ["stats"])
    repo_overrides: Dict[str, RepoVisualOverride] = field(default_factory=dict)
    output_json: str = "data.json"

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> ExtractorConfig:
        raw_data: Dict[str, Any] = {}
        target_path = config_path or os.getenv("STATS_CONFIG_FILE", "config.json")
        
        if os.path.exists(target_path):
            try:
                with open(target_path, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
            except Exception as e:
                logger.warning(f"No se pudo cargar {target_path} ({e}). Usando defaults y variables de entorno.")

        target = os.getenv("STATS_TARGET", raw_data.get("target", "shellaquiles"))
        is_org_env = os.getenv("STATS_IS_ORG")
        is_org = is_org_env.lower() in ("true", "1") if is_org_env else raw_data.get("is_org", True)
        title = os.getenv("STATS_TITLE", raw_data.get("title", f"stats.{target} — Telemetría Open Source"))

        raw_brand = raw_data.get("brand", {})
        brand = BrandConfig(
            prefix=os.getenv("STATS_BRAND_PREFIX", raw_brand.get("prefix", target[:5] if len(target) >= 5 else target)),
            middle=os.getenv("STATS_BRAND_MIDDLE", raw_brand.get("middle", target[5:] if len(target) >= 5 else "")),
            suffix=os.getenv("STATS_BRAND_SUFFIX", raw_brand.get("suffix", ".org" if is_org else ".dev")),
            prefix_color=os.getenv("STATS_BRAND_PREFIX_COLOR", raw_brand.get("prefix_color", "#22c55e")),
            suffix_color=os.getenv("STATS_BRAND_SUFFIX_COLOR", raw_brand.get("suffix_color", "#f43f5e")),
            tagline=os.getenv("STATS_TAGLINE", raw_brand.get("tagline", "ECOSISTEMA OPEN SOURCE")),
        )

        raw_links = raw_data.get("links", {})
        links = {
            "github": os.getenv("STATS_GITHUB_URL", raw_links.get("github", f"https://github.com/{target}")),
            "website": os.getenv("STATS_WEBSITE_URL", raw_links.get("website", f"https://{target}.org")),
        }

        env_exclude = os.getenv("STATS_EXCLUDE_REPOS")
        if env_exclude:
            exclude_repos = [r.strip() for r in env_exclude.split(",") if r.strip()]
        else:
            exclude_repos = raw_data.get("exclude_repos", ["stats"])

        raw_overrides = raw_data.get("custom_repo_overrides", {})
        repo_overrides = {
            k: RepoVisualOverride(
                badge=v.get("badge"),
                featured=v.get("featured", False),
                accent_color=v.get("accent_color", "border-t-zinc-700"),
                icon=v.get("icon", "box"),
            )
            for k, v in raw_overrides.items()
        }

        output_json = os.getenv("STATS_DATA_OUTPUT", "data.json")

        return cls(
            target=target,
            is_org=is_org,
            title=title,
            brand=brand,
            links=links,
            exclude_repos=exclude_repos,
            repo_overrides=repo_overrides,
            output_json=output_json,
        )

BOT_LOGINS = {
    "actions-user",
    "github-actions[bot]",
    "dependabot[bot]",
    "dependabot-preview[bot]",
    "imgbot[bot]",
    "greenkeeper[bot]",
    "renovate[bot]",
    "snyk-bot",
}

REFERRER_RULES = [
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
]

class GitHubTelemetryExtractor:
    """Pure generic data extraction & aggregation service."""

    def __init__(self, config: ExtractorConfig):
        self.config = config

    def _execute_gh(self, args: List[str]) -> Any:
        cmd = ["gh"] + args
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
            return json.loads(output)
        except Exception:
            return None

    def normalize_referrer(self, raw_name: Optional[str]) -> Tuple[str, str]:
        if not raw_name:
            return "Directo", "globe"
        lower = raw_name.lower()
        for pattern, canonical, icon in REFERRER_RULES:
            if pattern in lower:
                return canonical, icon
        return raw_name, "globe"

    def is_bot(self, login: Optional[str]) -> bool:
        if not login:
            return True
        return login in BOT_LOGINS or login.endswith("[bot]")

    def discover_repositories(self) -> List[str]:
        logger.info(f"📡 Descubriendo repositorios públicos para '{self.config.target}'...")
        payload = self._execute_gh([
            "repo", "list", self.config.target,
            "--json", "name,isArchived,isFork,isPrivate",
            "--limit", "100"
        ])
        if not payload:
            logger.warning("Sin repositorios descubiertos o error de red.")
            return []

        discovered = [
            r["name"]
            for r in payload
            if not r.get("isArchived")
            and not r.get("isPrivate")
            and r["name"] not in self.config.exclude_repos
        ]
        logger.info(f"📡 Repositorios descubiertos ({len(discovered)}): {', '.join(discovered)}")
        return discovered

    def _determine_visuals(self, repo_name: str, primary_lang: str) -> Tuple[Optional[str], bool, str, str]:
        if repo_name in self.config.repo_overrides:
            ov = self.config.repo_overrides[repo_name]
            return ov.badge, ov.featured, ov.accent_color, ov.icon

        lang_lower = (primary_lang or "").lower()
        if "python" in lang_lower:
            return None, False, "border-t-[#1e3a8a]", "code-2"
        if "javascript" in lang_lower or "typescript" in lang_lower:
            return None, False, "border-t-[#b45309]", "layout"
        if "shell" in lang_lower or "bash" in lang_lower:
            return None, False, "border-t-[#046a38]", "terminal"
        if "css" in lang_lower or "html" in lang_lower:
            return None, False, "border-t-zinc-400", "file-code"
        return None, False, "border-t-zinc-600", "folder-git-2"

    def fetch_repo_data(self, repo_name: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]]]:
        full_repo = f"{self.config.target}/{repo_name}"

        info = self._execute_gh([
            "repo", "view", full_repo,
            "--json", "name,description,url,homepageUrl,createdAt,updatedAt,pushedAt,stargazerCount,forkCount,diskUsage,licenseInfo,repositoryTopics,primaryLanguage"
        ]) or {}

        views_data = self._execute_gh(["api", f"repos/{full_repo}/traffic/views"]) or {}
        clones_data = self._execute_gh(["api", f"repos/{full_repo}/traffic/clones"]) or {}

        raw_refs = self._execute_gh(["api", f"repos/{full_repo}/traffic/popular/referrers"]) or []
        normalized_refs: Dict[str, Dict[str, Any]] = {}
        for r in raw_refs:
            canon, icon = self.normalize_referrer(r.get("referrer"))
            if canon not in normalized_refs:
                normalized_refs[canon] = {"name": canon, "views": 0, "uniques": 0, "icon": icon}
            normalized_refs[canon]["views"] += r.get("count", 0)
            normalized_refs[canon]["uniques"] += r.get("uniques", 0)

        releases = self._execute_gh(["api", f"repos/{full_repo}/releases"]) or []
        prs = self._execute_gh(["pr", "list", "-R", full_repo, "--state", "all", "--json", "number"]) or []

        contribs = self._execute_gh(["api", f"repos/{full_repo}/contributors"]) or []
        valid_contribs = [c for c in contribs if not self.is_bot(c.get("login"))]
        total_commits = sum(c.get("contributions", 0) for c in valid_contribs)

        primary_lang = (info.get("primaryLanguage") or {}).get("name", "Other")
        badge, featured, accent_color, icon = self._determine_visuals(repo_name, primary_lang)
        topics = [t["name"] for t in (info.get("repositoryTopics") or [])]
        license_name = (info.get("licenseInfo") or {}).get("name", "None")
        clean_license = license_name.replace(" License", "").replace("General Public v3.0", "GPL-3.0").replace("General Public License", "GPL")

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
        repos = self.discover_repositories()
        repos_data: List[Dict[str, Any]] = []
        global_referrers: Dict[str, Dict[str, Any]] = {}
        global_contributors: Dict[str, Dict[str, Any]] = {}

        for repo_name in repos:
            logger.info(f" -> Procesando {self.config.target}/{repo_name}...")
            repo_item, repo_refs, repo_contribs = self.fetch_repo_data(repo_name)
            repos_data.append(repo_item)

            for ref in repo_refs:
                name = ref["name"]
                if name not in global_referrers:
                    global_referrers[name] = {"name": name, "views": 0, "uniques": 0, "icon": ref["icon"]}
                global_referrers[name]["views"] += ref["views"]
                global_referrers[name]["uniques"] += ref["uniques"]

            for c in repo_contribs:
                login = c["login"]
                if login not in global_contributors:
                    global_contributors[login] = {
                        "login": login,
                        "avatar_url": c.get("avatar_url"),
                        "html_url": c.get("html_url"),
                        "contributions": 0,
                        "repos_count": 0,
                        "repos": []
                    }
                global_contributors[login]["contributions"] += c.get("contributions", 0)
                global_contributors[login]["repos_count"] += 1
                global_contributors[login]["repos"].append(repo_name)

        sorted_contributors = sorted(global_contributors.values(), key=lambda x: x["contributions"], reverse=True)
        sorted_referrers = sorted(list(global_referrers.values()), key=lambda x: x["views"], reverse=True)

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

        with open(self.config.output_json, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ Telemetría exportada limpiamente a {self.config.output_json}")

def main():
    parser = argparse.ArgumentParser(description="Extract GitHub telemetry into data.json (SRP).")
    parser.add_argument("--config", "-c", type=str, default=None, help="Path to config.json")
    args = parser.parse_args()

    config = ExtractorConfig.load(config_path=args.config)
    extractor = GitHubTelemetryExtractor(config=config)
    extractor.run()

if __name__ == "__main__":
    main()
