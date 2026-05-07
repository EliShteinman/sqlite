import json
import subprocess

# הרשימה המדויקת של 12 המאגרים ב-GitHub
repos = [
    "RedisLabs/redis-enterprise-k8s-docs",
    "redis-field-engineering/redis-enterprise-observability",
    "redis/redis",
    "RediSearch/RediSearch",
    "RedisGraph/RedisGraph",
    "RedisInsight/RedisInsight",
    "RedisTimeSeries/RedisTimeSeries",
    "RedisGears/RedisGears",
    "RedisJSON/RedisJSON",
    "RedisBloom/RedisBloom",
    "redis/redis-py",
    "prometheus-operator/prometheus-operator"
]

migration_data = []

for repo in repos:
    print(f"Exporting data for {repo}...")

    # שליפת שם ענף ברירת המחדל
    branch_res = subprocess.run(
        ["gh", "repo", "view", repo, "--json", "defaultBranchRef", "-q", ".defaultBranchRef.name"],
        capture_output=True, text=True
    )
    default_branch = branch_res.stdout.strip()

    # שליפת היסטוריית השחרורים
    rel_res = subprocess.run(
        ["gh", "api", f"repos/{repo}/releases"],
        capture_output=True, text=True
    )
    releases = json.loads(rel_res.stdout) if rel_res.returncode == 0 else []

    migration_data.append({
        "repo": repo,
        "default_branch": default_branch,
        "releases": releases
    })

# שמירה לקובץ
with open("migration_data.json", "w", encoding="utf-8") as f:
    json.dump(migration_data, f, indent=2)

print("Export complete! Please copy 'migration_data.json' to the isolated network.")