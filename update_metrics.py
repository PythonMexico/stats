#!/usr/bin/env python3
"""
Script para refrescar los datos del dashboard de analíticas de Shellaquiles Org
capturando métricas de toda la vida, tráfico (visitas y clones),
fuentes de origen (referrers) y el cuadro de honor completo de contribuidores y colaboradores.
"""

import subprocess
import json
import os
import re

def discover_repos():
    """Descubre dinámicamente todos los repositorios públicos de la organización shellaquiles."""
    try:
        raw_list = json.loads(subprocess.check_output([
            'gh', 'repo', 'list', 'shellaquiles',
            '--json', 'name,isArchived,isFork,isPrivate',
            '--limit', '100'
        ]))
        # Filtrar solo repositorios no archivados y públicos (excluyendo el repo de stats interno si se desea)
        discovered = [
            r['name'] for r in raw_list 
            if not r.get('isArchived') and not r.get('isPrivate') and r['name'] != 'stats'
        ]
        return discovered
    except Exception as e:
        print(f"⚠️ Error al descubrir repositorios con 'gh repo list': {e}")
        return ['cron-quiles', 'tribuTACOS', 'shellaquiles-org', 'pandocquiles', 'KARNITAS', 'frases-chingonas']

def normalize_referrer(raw_name):
    if not raw_name:
        return 'Directo', 'globe'
    
    lower = raw_name.lower()
    if 'linkedin' in lower:
        return 'LinkedIn', 'share-2'
    elif 'telegram' in lower or 't.me' in lower:
        return 'Telegram', 'send'
    elif 'google' in lower:
        return 'Google Search', 'search'
    elif 'github' in lower:
        return 'GitHub', 'github'
    elif 'twitter' in lower or 't.co' in lower or 'x.com' in lower:
        return 'X (Twitter)', 'twitter'
    elif 'facebook' in lower or 'fb' in lower:
        return 'Facebook', 'share-2'
    elif 'reddit' in lower:
        return 'Reddit', 'message-square'
    elif 'youtube' in lower:
        return 'YouTube', 'video'
    else:
        return raw_name, 'globe'

def fetch_metrics():
    repos = discover_repos()
    full_data = []
    global_referrers = {}
    all_contributors = {}
    print(f"📡 Descubiertos {len(repos)} repositorios: {', '.join(repos)}")
    print("📡 Obteniendo métricas, tráfico y contribuidores de GitHub...")

    for repo in repos:
        print(f" -> Procesando {repo}...")
        try:
            repo_info = json.loads(subprocess.check_output([
                'gh', 'repo', 'view', f'shellaquiles/{repo}',
                '--json', 'name,description,url,homepageUrl,createdAt,updatedAt,pushedAt,stargazerCount,forkCount,diskUsage,licenseInfo,repositoryTopics,primaryLanguage'
            ]))
        except Exception as e:
            print(f"Error al leer repo {repo}: {e}")
            continue

        # Tráfico de vistas
        try:
            views = json.loads(subprocess.check_output(['gh', 'api', f'repos/shellaquiles/{repo}/traffic/views']))
        except:
            views = {'count': 0, 'uniques': 0}

        # Tráfico de clones/descargas
        try:
            clones = json.loads(subprocess.check_output(['gh', 'api', f'repos/shellaquiles/{repo}/traffic/clones']))
        except:
            clones = {'count': 0, 'uniques': 0}

        # Referrers agrupados y normalizados
        normalized_repo_referrers = {}
        try:
            raw_referrers = json.loads(subprocess.check_output(['gh', 'api', f'repos/shellaquiles/{repo}/traffic/popular/referrers']))
            for ref in raw_referrers:
                raw_name = ref.get('referrer', 'Directo')
                canonical_name, icon = normalize_referrer(raw_name)
                
                # Global
                if canonical_name not in global_referrers:
                    global_referrers[canonical_name] = {'name': canonical_name, 'views': 0, 'uniques': 0, 'icon': icon}
                global_referrers[canonical_name]['views'] += ref.get('count', 0)
                global_referrers[canonical_name]['uniques'] += ref.get('uniques', 0)

                # Por repo
                if canonical_name not in normalized_repo_referrers:
                    normalized_repo_referrers[canonical_name] = {'referrer': canonical_name, 'count': 0, 'uniques': 0}
                normalized_repo_referrers[canonical_name]['count'] += ref.get('count', 0)
                normalized_repo_referrers[canonical_name]['uniques'] += ref.get('uniques', 0)

            referrers = list(normalized_repo_referrers.values())
        except:
            referrers = []

        # Releases
        try:
            releases = json.loads(subprocess.check_output(['gh', 'api', f'repos/shellaquiles/{repo}/releases']))
            release_count = len(releases)
        except:
            release_count = 0

        # PRs
        try:
            prs = json.loads(subprocess.check_output(['gh', 'pr', 'list', '-R', f'shellaquiles/{repo}', '--state', 'all', '--json', 'number']))
            prs_count = len(prs)
        except:
            prs_count = 0

        # Commits & Contribuidores
        try:
            contribs = json.loads(subprocess.check_output(['gh', 'api', f'repos/shellaquiles/{repo}/contributors']))
            total_commits = sum(c.get('contributions', 0) for c in contribs)
            contrib_count = len(contribs)
            
            for c in contribs:
                login = c.get('login')
                if not login or login in ['actions-user', 'github-actions[bot]', 'dependabot[bot]'] or login.endswith('[bot]'):
                    continue
                if login not in all_contributors:
                    all_contributors[login] = {
                        'login': login,
                        'avatar_url': c.get('avatar_url'),
                        'html_url': c.get('html_url'),
                        'contributions': 0,
                        'repos_count': 0,
                        'repos': []
                    }
                all_contributors[login]['contributions'] += c.get('contributions', 0)
                all_contributors[login]['repos_count'] += 1
                all_contributors[login]['repos'].append(repo)
        except:
            total_commits = 0
            contrib_count = 1

        topics = [t['name'] for t in (repo_info.get('repositoryTopics') or [])]
        lang = (repo_info.get('primaryLanguage') or {}).get('name', 'Shell')
        
        badge = None
        featured = False
        accentColor = "border-t-zinc-700"
        icon = "box"

        if repo == 'cron-quiles':
            featured = True
            badge = "LÍDER EN TRÁFICO (CLI)"
            accentColor = "border-t-[#1e3a8a]"
            icon = "calendar-sync"
        elif repo == 'tribuTACOS':
            featured = True
            badge = "CFDI 4.0 / FISCAL"
            accentColor = "border-t-[#046a38]"
            icon = "calculator"
        elif repo == 'shellaquiles-org':
            accentColor = "border-t-zinc-800"
            badge = "PORTAL CENTRAL"
            icon = "globe"
        elif repo == 'pandocquiles':
            badge = "DOCS ENGINE"
            accentColor = "border-t-[#b45309]"
            icon = "file-text"
        elif repo == 'KARNITAS':
            accentColor = "border-t-[#1e3a8a]"
            badge = "AGENT RUNTIME"
            icon = "cpu"
        elif repo == 'frases-chingonas':
            accentColor = "border-t-zinc-400"
            icon = "quote"
        else:
            # Asignación inteligente para cualquier repo nuevo futuro
            if 'python' in lang.lower():
                accentColor = "border-t-[#1e3a8a]"
                icon = "code-2"
            elif 'javascript' in lang.lower() or 'typescript' in lang.lower():
                accentColor = "border-t-[#b45309]"
                icon = "layout"
            elif 'shell' in lang.lower():
                accentColor = "border-t-[#046a38]"
                icon = "terminal"
            else:
                accentColor = "border-t-zinc-600"
                icon = "folder-git-2"

        full_data.append({
            'name': repo_info.get('name'),
            'description': repo_info.get('description') or '',
            'url': repo_info.get('url'),
            'homepageUrl': repo_info.get('homepageUrl') or '',
            'created_at': repo_info.get('createdAt')[:10],
            'stars': repo_info.get('stargazerCount', 0),
            'forks': repo_info.get('forkCount', 0),
            'commits': total_commits,
            'contributors': contrib_count,
            'language': lang,
            'license': (repo_info.get('licenseInfo') or {}).get('name', 'None').replace(' License', '').replace('General Public v3.0', 'GPL-3.0').replace('General Public License', 'GPL'),
            'clones_14d': clones.get('count', 0),
            'clones_uniques_14d': clones.get('uniques', 0),
            'views_14d': views.get('count', 0),
            'uniques_14d': views.get('uniques', 0),
            'releases': release_count,
            'prs': prs_count,
            'featured': featured,
            'badge': badge,
            'icon': icon,
            'accentColor': accentColor,
            'topics': topics,
            'referrers': referrers
        })

    sorted_contributors = sorted(all_contributors.values(), key=lambda x: x['contributions'], reverse=True)

    export_payload = {
        'repos': full_data,
        'referrers': sorted(list(global_referrers.values()), key=lambda x: x['views'], reverse=True),
        'contributors': sorted_contributors
    }

    json_path = os.path.join(os.path.dirname(__file__), 'data.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(export_payload, f, indent=2, ensure_ascii=False)

    html_path = os.path.join(os.path.dirname(__file__), 'index.html')
    if os.path.exists(html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            html = f.read()

        total_stars = sum(d['stars'] for d in full_data)
        total_forks = sum(d['forks'] for d in full_data)
        total_commits = sum(d['commits'] for d in full_data)
        total_clones = sum(d['clones_14d'] for d in full_data)
        total_clones_uniques = sum(d['clones_uniques_14d'] for d in full_data)
        total_views = sum(d['views_14d'] for d in full_data)
        total_views_uniques = sum(d['uniques_14d'] for d in full_data)
        total_releases = sum(d['releases'] for d in full_data)
        total_prs = sum(d['prs'] for d in full_data)
        total_contributors = len(sorted_contributors)
        total_repos_count = len(full_data)

        # Actualizar contadores en HTML
        html = re.sub(r'id="kpi-stars">.*?</div>', f'id="kpi-stars">{total_stars} ⭐</div>', html)
        html = re.sub(r'id="kpi-forks">.*?</div>', f'id="kpi-forks">{total_forks} 🍴</div>', html)
        html = re.sub(r'id="kpi-commits">.*?</div>', f'id="kpi-commits">{total_commits}</div>', html)
        html = re.sub(r'id="kpi-clones-hero">.*?</div>', f'id="kpi-clones-hero">{total_clones}</div>', html)
        html = re.sub(r'id="kpi-clones-uniques">.*?</div>', f'id="kpi-clones-uniques">{total_clones_uniques}</div>', html)
        html = re.sub(r'id="kpi-views-hero">.*?</div>', f'id="kpi-views-hero">{total_views}</div>', html)
        html = re.sub(r'id="kpi-views-uniques">.*?</div>', f'id="kpi-views-uniques">{total_views_uniques}</div>', html)
        html = re.sub(r'id="kpi-releases">.*?</div>', f'id="kpi-releases">{total_releases} Releases</div>', html)
        html = re.sub(r'id="kpi-prs">.*?</div>', f'id="kpi-prs">{total_prs} PRs</div>', html)
        html = re.sub(r'id="kpi-contributors-count">.*?</div>', f'id="kpi-contributors-count">{total_contributors} Colaboradores</div>', html)
        html = re.sub(r'id="sidebar-repo-count">.*?</span>', f'id="sidebar-repo-count">{total_repos_count} REPOSITORIOS</span>', html)

        json_str = json.dumps(full_data, indent=4, ensure_ascii=False)
        html = re.sub(r'const data = \[.*?\];', f'const data = {json_str};', html, flags=re.DOTALL)

        refs_str = json.dumps(export_payload['referrers'], indent=4, ensure_ascii=False)
        html = re.sub(r'const referrersData = \[.*?\];', f'const referrersData = {refs_str};', html, flags=re.DOTALL)

        contribs_str = json.dumps(sorted_contributors, indent=4, ensure_ascii=False)
        html = re.sub(r'const contributorsData = \[.*?\];', f'const contributorsData = {contribs_str};', html, flags=re.DOTALL)

        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✅ Shellaquiles Stats dashboard actualizado exitosamente en {html_path}")

if __name__ == '__main__':
    fetch_metrics()
