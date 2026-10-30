"""API performance benchmark producing a reviewable markdown report (#24).

Usage (repository root):

    python scripts/benchmark_api.py                 # print markdown to stdout
    python scripts/benchmark_api.py --out performance-report.md

``--out`` only accepts a plain file name; the report is always written into
``<repo>/artifacts/``. Absolute paths, directory components and ``..`` are
rejected so the benchmark can never write outside that directory.

The script never touches the development database: it creates a throwaway
SQLite file in the system temp directory, migrates, seeds synthetic data, tops
it up per scale, and deletes the file afterwards. Each endpoint is measured
through the DRF test client so timings and query counts follow the same code
path as the API tests.
"""

import argparse
import os
import platform
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path
from time import perf_counter

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "artifacts"
SIZES = (100, 500, 1000)
ROUNDS = 5
INNER_FLAG = "CAMPUS_BENCH_INNER"


def resolve_output_path(name):
    """Constrain report output to ``<repo>/artifacts/<name>``.

    Only a plain file name is accepted: anything containing a directory
    component (absolute paths, ``sub/dir/file.md``, ``..`` escapes, either
    separator) is rejected, so the report can never be written outside
    ``artifacts/`` even when the script runs in CI with untrusted input.
    The separators are checked as raw characters, not through ``Path``:
    on POSIX ``Path`` treats ``\\`` as a regular character and would let
    ``..\\report.md`` slip through.
    """
    if (not name or name in (".", "..") or ":" in name
            or "/" in name or "\\" in name):
        raise ValueError(f"--out accepts a plain file name written into artifacts/: got {name!r}")
    return OUTPUT_DIR / name


def run_outer(out_path):
    """Prepare an isolated database, then re-run this script inside it."""
    db_path = Path(tempfile.gettempdir()) / f"campusteam-bench-{os.getpid()}.sqlite3"
    env = dict(os.environ, DB_NAME=str(db_path), DJANGO_DEBUG="true",
               DJANGO_SECRET_KEY="benchmark-only-not-a-secret", **{INNER_FLAG: "1"})
    try:
        completed = subprocess.run([sys.executable, str(Path(__file__).resolve())],
                                   env=env, cwd=BASE_DIR, capture_output=True, text=True)
        if completed.returncode != 0:
            sys.stderr.write(completed.stderr or "benchmark failed\n")
            return completed.returncode
        if out_path:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(completed.stdout, encoding="utf-8")
            print(f"written: {out_path}")
        else:
            print(completed.stdout)
        return 0
    finally:
        for suffix in ("", "-wal", "-shm"):
            candidate = Path(str(db_path) + suffix)
            if candidate.exists():
                candidate.unlink()


def environment():
    import sqlite3
    return dict(
        platform=f"{platform.system()} {platform.release()} ({platform.machine()})",
        cpu=platform.processor() or "unknown",
        cpu_count=os.cpu_count(),
        python=platform.python_version(),
        sqlite=sqlite3.sqlite_version,
        database=os.environ.get("DB_ENGINE", "django.db.backends.sqlite3"),
    )


def create_base():
    """One project/team/owner plus a business admin; returns (team, owner, admin)."""
    from core.models import Project, RecommendationProfile, RecommendationRequirement, Team, TeamMember, User

    owner = User.objects.create_user(username="bench-owner", role=User.Role.LEADER)
    project = Project.objects.create(owner=owner, title="Bench", project_type="course", max_members=4)
    team = Team.objects.create(project=project, leader=owner)
    TeamMember.objects.create(team=team, user=owner)
    RecommendationProfile.objects.create(user=owner, abilities=[100, 80, 60, 0, 0], skills=["Python"],
                                         availability=[{"day": 1, "start": "18:00", "end": "21:00"}],
                                         goal="竞赛获奖", experience="竞赛")
    RecommendationRequirement.objects.create(team=team, abilities=[100, 80, 60, 40, 20], skills=["Python", "Figma"],
                                             availability=[{"day": 1, "start": "18:00", "end": "21:00"}],
                                             goal="竞赛获奖", experience="竞赛", weights={})
    return team, owner, User.objects.create_user(username="bench-admin", role=User.Role.ADMIN)


def ensure_candidates(up_to):
    """Idempotently top up the candidate pool to ``up_to`` synthetic students."""
    from core.models import RecommendationProfile, User

    existing = User.objects.filter(username__startswith="bench-cand-").count()
    if existing >= up_to:
        return
    for start in range(existing, up_to, 100):
        stop = min(start + 100, up_to)
        users = User.objects.bulk_create([User(username=f"bench-cand-{i}") for i in range(start, stop)])
        RecommendationProfile.objects.bulk_create([
            RecommendationProfile(user=user, abilities=[(i * 7) % 101 for _ in range(5)], skills=["Python"],
                                  availability=[{"day": 1, "start": "19:00", "end": "21:00"}], goal="竞赛获奖")
            for i, user in enumerate(users, start=start)])


def measure(endpoints, rounds=ROUNDS):
    from django.db import connection
    from django.test.utils import CaptureQueriesContext

    results = {}
    for name, call in endpoints.items():
        call()  # warm-up: first request pays template/import/JIT costs, not the query path
        durations, queries = [], []
        for _ in range(rounds):
            with CaptureQueriesContext(connection) as captured:
                started = perf_counter()
                response = call()
                durations.append((perf_counter() - started) * 1000)
                queries.append(len(captured))
            assert response.status_code == 200, f"{name} -> {response.status_code}: {response.content[:200]}"
        ordered = sorted(durations)
        results[name] = dict(median_ms=round(statistics.median(durations), 2),
                             p95_ms=round(ordered[min(len(ordered) - 1, int(len(ordered) * 0.95))], 2),
                             max_ms=round(max(durations), 2), queries=queries[0])
    return results


def run_inner():
    # Running as a script puts scripts/ on sys.path, not the project root.
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "campusteam.settings")
    import django
    django.setup()
    from django.core.management import call_command
    call_command("migrate", verbosity=0, interactive=False)

    from rest_framework.authtoken.models import Token
    from rest_framework.test import APIClient

    team, owner, admin = create_base()
    member_client, admin_client = APIClient(), APIClient()
    member_client.credentials(HTTP_AUTHORIZATION=f"Token {Token.objects.create(user=owner).key}")
    admin_client.credentials(HTTP_AUTHORIZATION=f"Token {Token.objects.create(user=admin).key}")
    base = "/api/v1"
    endpoints = {
        "GET /projects?page=1": lambda: member_client.get(f"{base}/projects", {"page": 1}),
        "GET /teams/{id}/capability-matrix": lambda: member_client.get(f"{base}/teams/{team.id}/capability-matrix"),
        "GET /teams/{id}/gaps": lambda: member_client.get(f"{base}/teams/{team.id}/gaps"),
        "GET /teams/{id}/recommendations?top_k=5":
            lambda: member_client.get(f"{base}/teams/{team.id}/recommendations", {"top_k": 5}),
        "GET /teams/{id}/health": lambda: member_client.get(f"{base}/teams/{team.id}/health"),
        "GET /admin/analytics": lambda: admin_client.get(f"{base}/admin/analytics"),
    }
    results = {}
    for size in SIZES:
        ensure_candidates(size)
        for name, row in measure(endpoints).items():
            results[(name, size)] = row

    lines = ["# API 性能回归报告（#24）", "",
             "本报告由 `python scripts/benchmark_api.py` 自动生成，数据来自隔离的临时 SQLite 数据库；",
             "结论仅用于回归对比，不代表生产容量承诺。", "",
             "## 运行环境", "", "| 项目 | 值 |", "|---|---|"]
    lines += [f"| {key} | {value} |" for key, value in environment().items()]
    lines += ["", "## 数据规模与结果", "",
              f"候选人数量：{', '.join(str(s) for s in SIZES)}；固定 1 个项目、1 个团队、1 名成员；"
              f"每个规模重复 {ROUNDS} 次，记录中位数、P95 与 SQL 查询数。", "",
              "| 接口 | 100 人 中位/P95 (ms) | 查询 | 500 人 中位/P95 (ms) | 查询 | 1000 人 中位/P95 (ms) | 查询 |",
              "|---|---:|---:|---:|---:|---:|---:|"]
    for name in endpoints:
        cells = []
        for size in SIZES:
            row = results[(name, size)]
            cells += [f"{row['median_ms']} / {row['p95_ms']}", str(row["queries"])]
        lines.append(f"| `{name}` | " + " | ".join(cells) + " |")
    lines += ["", "## 结论", ""]
    for name in endpoints:
        queries = [results[(name, size)]["queries"] for size in SIZES]
        medians = [results[(name, size)]["median_ms"] for size in SIZES]
        growth = medians[-1] / medians[0] if medians[0] else 0
        if len(set(queries)) != 1:
            lines.append(f"- `{name}`：查询数随规模变化 {queries}，需排查 N+1。")
            continue
        if growth >= 3:
            trend = f"耗时随候选人数近似线性增长（{medians[0]} → {medians[-1]} ms）"
        elif growth >= 1.5:
            trend = f"耗时有增长但明显低于线性（{medians[0]} → {medians[-1]} ms）"
        else:
            trend = f"耗时基本不随候选人数变化（{medians[0]} → {medians[-1]} ms）"
        lines.append(f"- `{name}`：SQL 查询数恒为 {queries[0]}，三种规模下无 N+1；{trend}。")
    lines += ["", "## 复现方式", "", "```powershell",
              "python scripts/benchmark_api.py",
              "python scripts/benchmark_api.py --out performance-report.md",
              "```", "",
              "``--out`` 只接受纯文件名，报告固定写入仓库的 ``artifacts/`` 目录。", ""]
    print("\n".join(lines))
    return 0


def main():
    parser = argparse.ArgumentParser(description="CampusTeam API benchmark")
    parser.add_argument("--out",
                        help="write the markdown report to artifacts/<name>; a plain file name only")
    args = parser.parse_args()
    if os.environ.get(INNER_FLAG) == "1":
        return run_inner()
    try:
        out_path = resolve_output_path(args.out) if args.out else None
    except ValueError as exc:
        parser.error(str(exc))
    return run_outer(out_path)


if __name__ == "__main__":
    raise SystemExit(main())
