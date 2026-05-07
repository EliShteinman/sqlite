import json
import subprocess
import os
import tempfile

GITLAB_GROUP = "arcane-group"  # עדכן לשם הקבוצה שלך ב-GitLab אם צריך


def run_glab(args):
    return subprocess.run(["glab"] + args, capture_output=True, text=True)


def import_metadata():
    with open('migration_data.json', 'r', encoding='utf-8') as f:
        projects = json.load(f)

    for project in projects:
        # חילוץ שם המאגר (למשל מתוך "redis/redis-py" נשאר רק "redis-py")
        repo_name = project['repo'].split('/')[-1]
        gitlab_path = f"{GITLAB_GROUP}/{repo_name}"

        default_branch = project['default_branch']
        releases = project['releases']

        print(f"\n=== Updating Project: {gitlab_path} ===")

        # 1. עדכון Default Branch
        print(f"-> Setting default branch to: {default_branch}")
        encoded_path = gitlab_path.replace('/', '%2F')
        branch_res = run_glab(
            ["api", "-X", "PUT", f"projects/{encoded_path}", "-f", f"default_branch={default_branch}"])
        if branch_res.returncode != 0:
            print(f"   [!] Error setting branch: {branch_res.stderr.strip()}")
        else:
            print("   [v] Branch set successfully.")

        # 2. יצירת השחרורים על גבי התגיות
        if not releases:
            print("-> No releases found to import.")
            continue

        print(f"-> Importing {len(releases)} releases...")
        releases.reverse()  # הפיכת הסדר מהישן לחדש כדי שיבנה כרונולוגית

        for rel in releases:
            tag = rel.get('tag_name')
            name = rel.get('name') or tag
            body = rel.get('body') or "No release notes provided."

            # שמירת טקסט השחרור לקובץ זמני
            with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as tf:
                tf.write(body)
                temp_path = tf.name

            # יצירת השחרור ב-GitLab
            rel_res = run_glab([
                "release", "create", tag,
                "-R", gitlab_path,
                "--name", name,
                "--notes-file", temp_path
            ])

            os.remove(temp_path)

            if rel_res.returncode == 0:
                print(f"   [v] Created release: {tag}")
            else:
                err = rel_res.stderr.strip()
                if "already exists" in err:
                    print(f"   [-] Release {tag} already exists, skipping.")
                else:
                    print(f"   [!] Failed to create {tag}: {err}")


if __name__ == "__main__":
    import_metadata()