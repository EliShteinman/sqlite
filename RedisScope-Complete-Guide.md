# RedisScope — מדריך מלא להתקנה, הפעלה ושימוש

**גרסה:** 1.24.5
**Build target:** rhel9
**Build date:** 2026-05-11 16:17:44
**Author:** Yoni Rosenfeld <yoni.rosenfeld@redis.com>
**Python embedded:** 3.9
**Format:** PyInstaller standalone executable

> כל המידע במסמך זה חולץ ישירות מקוד הכלי ואומת בהרצה בפועל על RHEL 9.7 x86_64.

---

## תוכן עניינים

1. [רקע](#1-רקע)
2. [תוכן החבילה](#2-תוכן-החבילה)
3. [דרישות מערכת](#3-דרישות-מערכת)
4. [התקנה](#4-התקנה)
5. [סקריפט ההפעלה run_redisscope.sh](#5-סקריפט-ההפעלה-run_redisscopesh)
6. [שיטות הפעלה](#6-שיטות-הפעלה)
7. [רשימה מלאה של כל הפלגים](#7-רשימה-מלאה-של-כל-הפלגים)
8. [דוגמאות שימוש מובנות](#8-דוגמאות-שימוש-מובנות)
9. [משתני סביבה](#9-משתני-סביבה)
10. [מבנה הפלט](#10-מבנה-הפלט)
11. [ארכיטקטורת הפלאגינים](#11-ארכיטקטורת-הפלאגינים)
12. [בדיקות שהכלי מבצע](#12-בדיקות-שהכלי-מבצע)
13. [מנגנון ה-Masking לעומק](#13-מנגנון-ה-masking-לעומק)
14. [זיהוי Cloud אוטומטי](#14-זיהוי-cloud-אוטומטי)
15. [מצב Active-Active (CRDB)](#15-מצב-active-active-crdb)
16. [מצב Kubernetes (מוסתר)](#16-מצב-kubernetes-מוסתר)
17. [פתרון בעיות](#17-פתרון-בעיות)
18. [אי-התאמות מול התיעוד הרשמי](#18-אי-התאמות-מול-התיעוד-הרשמי)
19. [Cheat Sheet — תרגום מהיר](#19-cheat-sheet--תרגום-מהיר)

---

## 1. רקע

**RedisScope** הוא כלי אבחון פנימי של Redis המנתח חבילות תמיכה (support packages) של Redis Enterprise ויוצר דוחות מקיפים בפורמט HTML וטקסט.

הכלי הוא בינארי standalone שנבנה באמצעות PyInstaller — כל קוד ה-Python, הספריות והבינארים הנדרשים ארוזים בתוך קובץ ELF יחיד בגודל כ-68MB. **אין צורך להתקין Python, pip או תלויות חיצוניות כלשהן** על השרת.

הכלי מבוסס על:
- Python 3.9
- redis 6.4.0
- cryptography 48.0.0
- pandas 2.3.3, numpy 1.26.4
- jinja2 (לתבניות HTML)
- reportlab (ל-PDF)
- beautifulsoup4 (לעיבוד HTML)
- ועוד 17 ספריות

הניתוח מורכב ממערכת **פלאגינים** מודולרית עם מעל 100 בדיקות שונות, המסווגות ל-12 קטגוריות (פירוט בפרק 11).

---

## 2. תוכן החבילה

לאחר חילוץ `redisscope-1.24.5-rhel9.tar.gz`, התיקייה `redisscope-1.24.5-rhel9/` מכילה ארבעה קבצים:

| קובץ | גודל | תיאור |
|---|---|---|
| `redisscope` | ~68MB | הבינארי הראשי — קובץ ELF x86_64 dynamically linked, מבוסס PyInstaller. דורש `chmod +x`. |
| `run_redisscope.sh` | 644B | סקריפט עזר ב-bash שמטפל בהרשאות ההרצה ומפעיל את הבינארי עם כל הארגומנטים. ראו פרק 5. |
| `README.txt` | 4.1KB | תיעוד קצר וחלקי של היצרן. לפי הקוד בפועל, התיעוד הזה **לא מדויק**. ראו פרק 18. |
| `VERSION.txt` | 107B | פרטי בילד: גרסה, target OS, תאריך build, שם מכונת ה-build. |

### תוכן `VERSION.txt`

```
RedisScope Version: 1.24.5
Build Target: rhel9
Build Date: 2026-05-11 16:17:44
Build Host: LAPTOP-PF5NQE9M
```

### תוכן `redisscope` (בינארי)

```
ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked,
interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 3.2.0, stripped
```

הבינארי הוא PyInstaller bundle: בזמן ריצה הוא חולץ את עצמו ל-`/tmp/_MEIxxxxxx/` (משתנה לכל הרצה), מפעיל מתוכו את `python3.9` ואת `redisscope/__init__.py` שכולל את `main_cli()`.

---

## 3. דרישות מערכת

### דרישות מערכת רשמיות (מתוך README)

- **מערכת הפעלה:** RHEL 9
- **ארכיטקטורה:** x86_64
- **זיכרון:** מינימום 2GB RAM (מומלץ)
- **דיסק:** כ-500MB עבור הניתוח + גודל חבילת התמיכה
- **Python:** **לא נדרש** (הבינארי הוא standalone)
- **תלויות:** אין

### דרישות מערכת אמיתיות (מהקוד)

הקוד עצמו דורש:
- `glibc` עדכני (לפחות 2.28, כלומר RHEL 8/9 או דביאן 10+)
- `/tmp` עם הרשאת כתיבה ומקום פנוי לפחות בגודל הבינארי × 2 (PyInstaller מחלץ ל-`/tmp/_MEIxxx`)
- `tar` להרצת ה-`oc cp` או חילוץ ידני

### אומת בפועל

הכלי הורץ בהצלחה על **Red Hat Enterprise Linux 9.7 (Plow)** עם פלט תקין של `--version` ו-`--help`.

---

## 4. התקנה

### שלב 1: העברת החבילה לשרת

```bash
# העתקה מהמכונה המקומית לשרת
scp redisscope-1.24.5-rhel9.tar.gz user@your-rhel9-server:/tmp/
```

### שלב 2: חילוץ הארכיון

```bash
cd /tmp
tar -xzf redisscope-1.24.5-rhel9.tar.gz
cd redisscope-1.24.5-rhel9
```

### שלב 3: הקצאת הרשאות הרצה

```bash
chmod +x redisscope
chmod +x run_redisscope.sh
```

### שלב 4: אימות התקנה

```bash
./redisscope --version
# Expected output: RedisScope 1.24.5
```

### הסרת התקנה

הכלי לא תומך בשדרוגים. כדי להתקין גרסה חדשה:

```bash
rm -rf /tmp/redisscope-1.24.5-rhel9
# ואז להתקין את הגרסה החדשה כרגיל
```

### התקנה גלובלית (אופציונלית)

כדי להפעיל מכל מקום במערכת:

```bash
sudo cp redisscope /usr/local/bin/
sudo chmod +x /usr/local/bin/redisscope
# עכשיו אפשר להריץ פשוט: redisscope --help
```

---

## 5. סקריפט ההפעלה `run_redisscope.sh`

זהו סקריפט עזר קצר ב-bash שמוודא שהבינארי קיים, בודק שיש לו הרשאת הרצה, ומפעיל אותו עם כל הארגומנטים שהועברו:

```bash
#!/bin/bash
# RedisScope Launcher Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REDISSCOPE_BIN="$SCRIPT_DIR/redisscope"

if [ ! -f "$REDISSCOPE_BIN" ]; then
    echo "❌ Error: redisscope binary not found at $REDISSCOPE_BIN"
    exit 1
fi

if [ ! -x "$REDISSCOPE_BIN" ]; then
    echo "🔧 Making redisscope executable..."
    chmod +x "$REDISSCOPE_BIN"
fi

echo "🚀 Running RedisScope..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
"$REDISSCOPE_BIN" "$@"
```

### ניתוח שורה-שורה

1. `SCRIPT_DIR=...` — מאתר את התיקייה שבה נמצא הסקריפט עצמו (לא ה-cwd). כך אפשר להפעיל את הסקריפט מכל מקום והוא ימצא את הבינארי.
2. `REDISSCOPE_BIN=...` — נתיב מלא לבינארי.
3. בדיקה ש**הקובץ קיים** — אם לא, יוצא בשגיאה.
4. בדיקה ש**יש הרשאת הרצה** — אם לא, מבצע `chmod +x` אוטומטית. זה אומר שאם פספסת את שלב 3 בהתקנה, הסקריפט יתקן את זה.
5. מדפיס באנר ומריץ את הבינארי עם `"$@"` — כל הארגומנטים שהועברו לסקריפט.

### מתי להשתמש בסקריפט ומתי בבינארי ישירות?

| תרחיש | המלצה |
|---|---|
| הרצה ראשונה / לא בטוח אם יש הרשאות | `./run_redisscope.sh` |
| הרצות חוזרות, הכל מוגדר | `./redisscope` ישירות |
| אוטומציה / CI | `./redisscope` ישירות (פלט נקי יותר, בלי הבאנר) |
| אינטראקטיבי, רוצה לראות שמשהו רץ | `./run_redisscope.sh` (יש לו 🚀) |

---

## 6. שיטות הפעלה

הכלי תומך בשתי שיטות מקבילות:

### שיטה A — העברת חבילה כפרמטר (`--sp`)

הכלי יחלץ את החבילה אוטומטית. פורמטים נתמכים: **`.tar.gz`, `.tgz`, `.tar`, `.zip`**.

```bash
./redisscope --sp /path/to/support_package.tar.gz
```

**מה קורה ברקע:**
1. הכלי בודק שהקובץ קיים.
2. יוצר תיקייה `redisscope_sp` בתיקיית העבודה הנוכחית.
3. מחלץ לתוכה את הארכיון.
4. `cd` אוטומטי לשם.
5. ממשיך בניתוח רגיל.

אם החילוץ נכשל חלקית, הכלי **ימשיך לנתח** את הקבצים שכן חולצו ויסמן זאת כשגיאה בקטגוריית CRITICAL בדוח.

### שיטה B — הפעלה מתיקייה עם חבילה מחולצת

```bash
mkdir 12345                    # ticket number
cp support_package.tar.gz 12345/
cd 12345
tar xzf support_package.tar.gz
../redisscope                  # רצים מהתיקייה מעליה
```

זוהי השיטה ההיסטורית. הכלי מצפה למצוא במצב זה את התיקייה הנוכחית כשורש חבילת התמיכה (אז שם יש את `node_*/`, `cluster_info`, `ccs-redis.json` וכו').

> ⚠️ הכלי **לא** תומך בפרמטר positional בסגנון `./redisscope file.tar.gz`. למרות שה-README.txt הרשמי מציג את זה — זה שגוי. חייבים `--sp` לפני נתיב הקובץ.

---

## 7. רשימה מלאה של כל הפלגים

24 פלגים נתמכים. הסעיף הזה מקיף ומדויק לחלוטין על פי הקוד.

### 7.1 פלגים בסיסיים

#### `--sp FILE`

**תיאור:** Support package file path (will be extracted automatically)

**ערך:** נתיב לקובץ ארכיון של חבילת תמיכה. פורמטים: `.tar.gz`, `.tgz`, `.tar`, `.zip`.

**ברירת מחדל:** אין. אם לא ניתן, הכלי מצפה לרוץ מתיקייה שמכילה כבר חבילה מחולצת.

**דוגמה:**
```bash
./redisscope --sp /home/user/support_2026-05-15.tar.gz
```

---

#### `--version`

**תיאור:** Print version and exit

**ערך:** flag — אין ערך.

**התנהגות:** מדפיס `RedisScope <version>` ופרטים נוספים (Branch, Commit, Python version, Pip version, install date) ויוצא מיד עם קוד 0.

**דוגמה:**
```bash
$ ./redisscope --version
RedisScope 1.24.5
```

---

#### `--verbose`, `-v`

**תיאור:** Show detailed plugin execution logs on console (INFO level)

**ערך:** flag.

**התנהגות:** ברירת המחדל היא להציג רק `ERROR` ומעלה במסך. עם `--verbose` רואים גם `INFO`. הלוג המלא נשמר תמיד ל-`redisscope_logs/` בלי קשר לפלג.

**דוגמה:**
```bash
./redisscope --sp sp.tar.gz --verbose
./redisscope --sp sp.tar.gz -v
```

---

### 7.2 מצב Mask

#### `--mask`

**תיאור:** Mask reports

**ערך:** flag.

**התנהגות:** אחרי שהכלי מסיים לייצר את הדוח הרגיל ב-`redisscope_html/`, הוא יוצר עותק מצונזר ב-`redisscope_html_mask/` ומפיק קובץ `mask_mappings.json` עם המיפוי המלא. ראו פרק 13 לעומק.

**מה ממוסך:**
- כתובות IP פנימיות של nodes → `1.1.1.1`, `2.2.2.2` וכו'.
- כתובות IP חיצוניות של nodes → דומה.
- שמות מסדי נתונים → `db-1`, `db-2` וכו'.
- שם ה-cluster → `redis.domain.com`.
- IPs של clients (לפעמים).

**דוגמה:**
```bash
./redisscope --sp sp.tar.gz --mask
```

---

### 7.3 מטא-מידע לדוח

#### `--title TEXT`

**תיאור:** Custom title for the final report

**ערך:** מחרוזת חופשית.

**התנהגות:** מחליף את כותרת הדוח הראשית.

```bash
./redisscope --sp sp.tar.gz --title "Customer ABC - Q2 2026 Health Check"
```

---

#### `--ticket ID`

**תיאור:** Zendesk ticket ID to display in the dashboard (optional)

**ערך:** מחרוזת — בדרך כלל מזהה כרטיס Zendesk.

**התנהגות:** מוצג בלוח המחוונים. רק קישוטי, לא משפיע על הניתוח.

```bash
./redisscope --sp sp.tar.gz --ticket 87654
```

---

#### `--sp-name NAME`

**תיאור:** Support package filename (for display in report, no extraction)

**ערך:** שם קובץ (string).

**התנהגות:** **לא** מבצע חילוץ. רק שם להצגה בדוח. שימושי כשרצים מתיקייה עם חבילה מחולצת ורוצים שהדוח יציג את שם הארכיון המקורי.

```bash
./redisscope --sp-name original-support-pkg-20260501.tar.gz
```

---

#### `--filescom-path PATH`

**תיאור:** Original Files.com path (for display in report as clickable link)

**ערך:** URL או נתיב Files.com.

**התנהגות:** מציג קישור לחיץ בדוח לחבילת התמיכה ב-Files.com — שימושי כשהדוח עובר בין אנשים והם רוצים לגשת לחבילה המקורית.

```bash
./redisscope --sp sp.tar.gz --filescom-path "https://redis.files.com/sp/abc123.tar.gz"
```

---

### 7.4 סינון לפי זמן

#### `--start "YYYY-MM-DD [HH:MM:SS]"`

**תיאור:** Start date/time: YYYY-MM-DD or 'YYYY-MM-DD HH:MM:SS'

**ערך:** תאריך בפורמט `YYYY-MM-DD` או `YYYY-MM-DD HH:MM:SS`.

**התנהגות:** הכלי יסנן את ניתוח הלוגים והאירועים לטווח שבין `--start` ל-`--end`.

**ולידציה:** פורמט שגוי גורם לשגיאה: `"Not a valid date: '<x>'. Use YYYY-MM-DD or 'YYYY-MM-DD HH:MM:SS' format."`

```bash
./redisscope --sp sp.tar.gz --start "2026-05-10"
./redisscope --sp sp.tar.gz --start "2026-05-10 14:30:00"
```

---

#### `--end "YYYY-MM-DD [HH:MM:SS]"`

**תיאור:** End date/time: YYYY-MM-DD or 'YYYY-MM-DD HH:MM:SS'

**ערך:** זהה ל-`--start`.

```bash
./redisscope --sp sp.tar.gz --end "2026-05-15 23:59:59"
```

---

### 7.5 זיהוי Cloud / BDB

#### `--cloud INT`, `-c INT`

**תיאור:** Cloud identifier as an integer (optional)

**ערך:** מספר שלם (cluster ID של Redis Cloud).

**התנהגות:** אם הכלי מזהה אוטומטית שמדובר ב-Redis Cloud deployment (ראו פרק 14), הוא מנסה גם לזהות את ה-BDB ID האוטומטית. ה-`--cloud` מאפשר לעקוף את הזיהוי האוטומטי.

```bash
./redisscope --sp sp.tar.gz --cloud 12345
./redisscope --sp sp.tar.gz -c 12345
```

---

#### `--bdb INT`

**תיאור:** BDB identifier that modifies cloud

**ערך:** מספר שלם (BDB ID).

**התנהגות:** דורס את ה-Cloud ID כשמשתמשים בשניהם. לרוב כשרוצים לנתח מסד נתונים ספציפי באשכול cloud.

```bash
./redisscope --sp sp.tar.gz --bdb 7
./redisscope --sp sp.tar.gz --cloud 12345 --bdb 7
```

---

### 7.6 Active-Active

#### `--aa`

**תיאור:** Active-Active multi-cluster debug mode. Directory should contain subdirectories of all participant clusters' support packages.

**ערך:** flag.

**התנהגות:** מצב מיוחד לניתוח CRDB (Conflict-Free Replicated DB). יש להריץ מתיקייה שמכילה תת-תיקיות, אחת לכל cluster משתתף, וכל תת-תיקייה מכילה חבילת תמיכה מחולצת.

```
aa-analysis/
├── cluster-east/    ← חבילת תמיכה מחולצת של ה-cluster המזרחי
├── cluster-west/    ← של המערבי
└── cluster-eu/      ← של האירופי
```

```bash
cd aa-analysis
../redisscope --aa
```

---

#### `--aa-filter-cluster PATTERN`

**תיאור:** Filter AA analysis by cluster name pattern (used with --aa)

**ערך:** תבנית שם (תומך wildcard `*`).

**התנהגות:** מצומצם את הניתוח רק ל-clusters ששמם תואם לתבנית.

```bash
../redisscope --aa --aa-filter-cluster "prod-*"
```

---

#### `--aa-filter-crdb PATTERN`

**תיאור:** Filter AA analysis by CRDB name pattern (used with --aa)

**ערך:** תבנית שם CRDB.

```bash
../redisscope --aa --aa-filter-crdb "session-cache"
```

---

#### `--aa-filter-bdb ID`

**תיאור:** Filter AA analysis by BDB ID (used with --aa)

**ערך:** BDB ID (מחרוזת או מספר).

```bash
../redisscope --aa --aa-filter-bdb 5
```

---

### 7.7 שליטה בסריקת לוגים

#### `--skiplogs`

**תיאור:** Skip test_sp processing if this flag is set

**ערך:** flag.

**התנהגות:** מדלג על שלב עיבוד הלוגים העיקרי. שימושי כשרוצים רק את הניתוח הקונפיגורטיבי (cluster, nodes, bdbs) ללא ניתוח הלוגים — מאיץ מאוד.

```bash
./redisscope --sp sp.tar.gz --skiplogs
```

---

#### `--force-full`

**תיאור:** Force full log scan (4 days) even for large clusters (>5 nodes). Default: 3 days for large clusters

**ערך:** flag.

**הקשר:** ברירת מחדל ל-clusters עם **יותר מ-5 nodes** היא לסרוק רק 3 ימים של לוגים, כדי לחסוך זמן. הפלג הזה כופה סריקה מלאה של 4 ימים.

**dest פנימי:** `force_full_logs`

```bash
./redisscope --sp sp.tar.gz --force-full
```

---

#### `--count-pattern-occurrences`

**תיאור:** Count all occurrences of log patterns per node (slower but more detailed)

**ערך:** flag.

**הקשר:** ברירת מחדל היא לזהות שדפוס לוג מסוים *קיים*. הפלג הזה גורם לכלי לספור **כמה פעמים** כל דפוס מופיע לכל node — מספק יותר תובנות אבל איטי משמעותית.

**dest פנימי:** `count_pattern_occurrences`

```bash
./redisscope --sp sp.tar.gz --count-pattern-occurrences
```

---

### 7.8 פלטי HTML

#### `--single`

**תיאור:** Generate a single HTML file (default: multi-page for web server deployment)

**ערך:** flag.

**ברירת מחדל:** `False` (כלומר ייצור מולטי-פייג').

**הקשר:** ה-UI החדש (Bootstrap-based) הוא מולטי-פייג' — נוצרים מספר קבצי HTML בתיקייה אחת, מתאים לפריסה לשרת אינטרנט. עם `--single` הכל מתאחד לקובץ HTML יחיד שאפשר לפתוח מקומית בלי שרת.

```bash
./redisscope --sp sp.tar.gz --single
```

---

#### `--shiry`

**תיאור:** Use old UI (single-page HTML) instead of new Bootstrap UI

**ערך:** flag.

**ברירת מחדל:** `False`.

**הקשר:** בגרסאות הישנות ה-UI היה HTML יחיד פשוט יותר (כנראה שמו של מי שכתב/ה את ה-UI הישן הוא Shiry). הפלג הזה מחזיר את ה-UI הישן. עוקף את `--single` (כי גם ככה זה single-page).

```bash
./redisscope --sp sp.tar.gz --shiry
```

---

### 7.9 פלגים נוספים

#### `--test`

**תיאור:** Enable test mode

**ערך:** flag.

**התנהגות:** מצב בדיקה. הקוד מתייחס לזה כ-`args.test` בכמה מקומות, מאפשר בדיקות פנימיות. לא מומלץ לשימוש שגרתי.

```bash
./redisscope --sp sp.tar.gz --test
```

---

### 7.10 פלגים מוסתרים (`argparse.SUPPRESS`)

הפלגים הבאים **לא יופיעו ב-`--help`** אבל הם נתמכים בקוד:

#### `--k8s`

**תיאור:** מצב Kubernetes (פלאגין `k8s_log_collector`).

**התנהגות:** מאפיין את הניתוח לאשכולות Redis Enterprise on Kubernetes / OpenShift. הכלי יעבד גם פלט של `kubectl logs` ו-`k8s log_collector`. ראו פרק 16.

```bash
./redisscope --sp sp.tar.gz --k8s
```

---

#### `--export-json`

**תיאור:** ייצוא JSON של תוצאות הניתוח.

**dest פנימי:** `export_json`

**משתנה סביבה לעקיפה:** `REDISSCOPE_DISABLE_JSON_EXPORT` (אם מוגדר, מבטל את הייצוא).

```bash
./redisscope --sp sp.tar.gz --export-json
```

---

## 8. דוגמאות שימוש מובנות

מתוך `--help` של הכלי עצמו:

```
Examples:
  redisscope --sp support_package.tar.gz
      Extract and analyze a support package file.

  redisscope --start 2025-01-01 --end 2025-01-31 --cloud 123
      Run the script for January 2025 with cloud ID 123.

  redisscope --start "2025-01-01 08:00:00" --end "2025-01-01 12:00:00"
      Run the script for a specific 4-hour time window.

  redisscope --cloud 12345
      Run in cloud mode for BDB ID 12345.

  redisscope --bdb 12345
      Run for specific BDB ID.

  redisscope --mask
      Run and mask IP addresses and domain names.

  redisscope --shiry
      Use old UI (single-page HTML) instead of new Bootstrap UI.

  redisscope --verbose
      Show detailed plugin execution logs on console (INFO level).

  redisscope --aa
      Active-Active multi-cluster debug mode. Run from a directory containing
      subdirectories of all participant clusters' support packages.

  redisscope --version
      Print the version of RedisScope and exit.
```

---

## 9. משתני סביבה

הכלי קורא מספר משתני סביבה. רובם פנימיים (PyInstaller / לשימוש בין פלאגינים), אבל יש שניים-שלושה שכדאי להכיר:

### משתנים פנימיים שמוגדרים אוטומטית

| משתנה | תיאור |
|---|---|
| `REDISSCOPE_RUN_DIR` | תיקיית הריצה הנוכחית של הכלי |
| `REDISSCOPE_ORIGINAL_DIR` | תיקיית המקור (לפני `cd` לתוך `redisscope_sp`) |
| `REDISSCOPE_TAB_STRUCTURE_PATH` | נתיב לקובץ הגדרת ה-tabs ב-HTML |
| `REDISSCOPE_TEMPLATE_PATH` | נתיב לתבניות Jinja2 |
| `_MEIPASS` | מוגדר על ידי PyInstaller — נתיב לתיקיית החילוץ הזמנית |

### משתנים שניתן לקבוע מבחוץ

| משתנה | תיאור |
|---|---|
| `REDISSCOPE_DISABLE_JSON_EXPORT` | אם מוגדר (לכל ערך), משתלט על `--export-json` ומבטל אותו |
| `K8S_ONLY_MODE` | מצב מיוחד שמופעל פנימית עבור `--k8s` (אין צורך להגדיר ידנית) |
| `K8S_NAMESPACE_DIR` | תיקיית namespace של k8s (פנימי) |
| `K8S_ORIGINAL_DIR` | תיקיית מקור k8s (פנימי) |
| `ZENDESK_USER` | אם מסונכרן עם Zendesk (לא בשימוש בגרסה זו) |
| `ZENDESK_PASS` | סיסמה ל-Zendesk (לא בשימוש בגרסה זו) |

### דוגמה לשימוש

```bash
REDISSCOPE_DISABLE_JSON_EXPORT=1 ./redisscope --sp sp.tar.gz
```

---

## 10. מבנה הפלט

לאחר ריצה מוצלחת, ייווצרו בתיקיית העבודה הנוכחית:

```
.
├── redisscope_<dirname>_Report.html      ← הדוח HTML המרכזי
├── redisscope_all/                        ← כל הנתונים הגולמיים
│   ├── *.json                            ← נתוני cluster, nodes, bdbs
│   ├── *.txt                             ← פלט בפורמט טקסט
│   └── ...
├── redisscope_html/                      ← דוחות HTML (לפריסת שרת)
│   ├── index.html
│   ├── nodes.html
│   ├── bdbs.html
│   ├── usage.html
│   ├── errors.html
│   └── assets/
│       ├── css/
│       ├── js/
│       └── img/
├── redisscope_html_mask/                 ← רק אם --mask: עותק ממוסך של redisscope_html
├── redisscope_logs/                      ← לוגים של ריצת הכלי
│   ├── data_generation.log
│   ├── global.log
│   └── plugin_*.log
├── redisscope_upload_to_ticket/          ← קבצים מסוננים להעלאה לכרטיס
│   ├── redisscope_<dirname>_Report.html  ← (העתק)
│   └── mask_mappings.json                ← (רק אם --mask)
├── redisscope_sp/                        ← רק עם --sp: חבילת תמיכה מחולצת
└── .redisscope_extraction_error.json     ← רק אם חילוץ נכשל חלקית
```

### תפקיד כל תיקייה

| תיקייה | מטרה |
|---|---|
| `redisscope_all/` | אוסף הנתונים הגולמיים שנאספו מהחבילה — קבצי JSON ו-TXT שמשמשים לבניית הדוחות |
| `redisscope_html/` | תיקיית הדוח הראשית. **אם משתמשים ב-multi-page** — מכילה את כל הדפים והנכסים |
| `redisscope_html_mask/` | רק אם הוגדר `--mask`. עותק מצונזר של `redisscope_html/` |
| `redisscope_logs/` | לוגי ריצה של הכלי עצמו (פתרון בעיות בכלי, לא בחבילה הנותחת) |
| `redisscope_upload_to_ticket/` | **תיקיית המוצר המרכזית** — קבצים שיש להעלות לכרטיס התמיכה |
| `redisscope_sp/` | רק אם הוגדר `--sp` — תיקיית חילוץ של חבילת התמיכה |

### הקובץ `.redisscope_extraction_error.json`

אם החילוץ של חבילת התמיכה נכשל חלקית, ייווצר קובץ JSON עם השדות:
- `error`: סוג השגיאה (`Archive Extraction Error`).
- `severity`: `CRITICAL`.
- `category`: `Support Package`.
- `recommended_action`: בקשה להוריד מחדש את החבילה.

הקובץ הזה מופיע בתור שגיאה בדוח עצמו בקטגוריית CRITICAL.

---

## 11. ארכיטקטורת הפלאגינים

הכלי בנוי ממערכת פלאגינים מודולרית. בזמן ריצה הוא טוען פלאגינים מתיקיית `plugins/` הפנימית בסדר מספרי. שמות התיקיות מתחילים במספר כדי לקבוע את סדר הריצה.

### קטגוריות הפלאגינים (לפי סדר ריצה)

| # | קטגוריה | מטרה |
|---|---|---|
| 01 | `01_headers` | בדיקות תקינות ראשוניות וכותרת בדוח |
| 03 | `03_nodes` | בדיקות ברמת ה-node (כ-50 בדיקות שונות) |
| 04 | `04_bdbs` | בדיקות ברמת מסד הנתונים (BDB) |
| 06 | `06_usage` | ניתוח שימוש: זיכרון, מפתחות, ביצועים |
| 07 | `07_upgrade_healthcheck` | בדיקות לפני שדרוג גרסה |
| 10 | `10_rdi` | Redis Data Integration — זיהוי ובדיקה |
| 90 | `90_log_analysis` | ניתוח לוגים, דפוסי שגיאה, אירועים |
| 91 | `91_failover_analysis` | ניתוח אירועי failover |
| 95 | `95_print_info` | יצירת טבלאות מידע (cluster, nodes, dbs, LDAP, certificates, modules, persistence, Azure, 3rd-party, CRDB, network, users, replicaof) |
| 96 | `96_errors` | אסיפת שגיאות והמלצות |
| 97 | `97_html` | יצירת הדוח HTML הסופי |
| 99 | `99_end` | הודעת סיום |

### תוספים מורחבים

יש שתי תיקיות מיוחדות בתוך `plugins/`:

#### `plugins/testground/`

פלאגינים חדשים ב"גן ניסויים" — נטענים מאוחר יותר, יכולים לעקוף תוצאות של פלאגינים קודמים.

קיים בגרסה זו:
- `check_connectivity_root_cause.pyc`

#### `plugins/extended_suite_scripts/`

סקריפטים ש**אפשר להריץ בנפרד** אחרי הניתוח הראשי, לקבלת דוחות מתמחים:

| סקריפט | תיאור |
|---|---|
| `certificate_report.pyc` | דוח מפורט על תעודות SSL/TLS — מה תקף, מה פג, מה עומד לפוג. תומך ב-`--output` ו-`--path`. |
| `cluster_watchdog_analyzer.pyc` | ניתוח של watchdog logs ב-cluster level. תומך ב-`--output` ו-`--path`. |
| `persistence_files_report.pyc` | דוח מפורט על קבצי AOF/RDB. תומך ב-`--output`. |

> אפשר להריץ אותם מתוך הבינארי? **לא ישירות**, כי הם מבוצעים בתוך מנוע הפלאגינים. אבל הם רצים אוטומטית כחלק מהניתוח אם הקטגוריה רלוונטית.

---

## 12. בדיקות שהכלי מבצע

הרשימה כוללת מעל 100 בדיקות בודדות. הנה החלוקה לפי קטגוריות:

### 12.1 בדיקות Cluster (`01_headers`, `95_print_info`)

- שגיאות חילוץ ראשוניות.
- כותרת הדוח, גרסת cluster, גרסת Redis, גרסת OS, תאריך התקנה.
- מצב הרישיון (Trial / Production / Enterprise).
- DNS @ entries מוגדרים כראוי.
- DNS cnm entries מוגדרים כראוי.
- כל משימות ה-resource manager הושלמו.
- מצב Upgrade.
- Private Service Connect מוגדר ל-GCP.

### 12.2 בדיקות Nodes (`03_nodes`)

הרשימה (לפי שמות הפלאגינים שזיהיתי):

- `check_expired_certificates` — תעודות שפג תוקפן.
- `check_expired_certificates_in_use` — תעודות שפג תוקפן ועדיין בשימוש.
- `certs_san_validation` — תקינות SAN בתעודות.
- `check_dnsmasq` — שירות dnsmasq.
- `check_disk_usage` — שימוש בדיסק.
- `check_disk_space_requirements` — מקום דיסק לפי דרישות מינימום.
- `check_duplicate_external_ip_address` — IPs חיצוניים כפולים.
- `check_duplicate_services` — שירותים כפולים.
- `check_execute_rladmin` — האם `rladmin status extra all` רץ בהצלחה.
- `check_high_cpu` — תהליכים מעל 80% CPU.
- `check_endpoint_watchdog_status` — סטטוס endpoint watchdog.
- `check_heartbeatd_errors` — שגיאות heartbeatd.
- `check_debug_logging` — האם debug logging פעיל.
- `check_debug_mode` — האם debug mode פעיל.
- `check_ccs_down_red_188659` — בעיית CCS down ספציפית.
- `check_ccs_quorum_loss` — אובדן quorum של CCS.
- `ccs_wrong_master_check` — master שגוי ב-CCS.
- `05_network_interface_analysis` — ניתוח ממשקי רשת.
- ועוד בדיקות לפי תוכן התיקייה.

### 12.3 בדיקות BDB (`04_bdbs`)

- `bdb_state_machine_validator` — תקינות state machine.
- `check_bdb_state_machine` — סטטוס state machine.
- `check_bdb_status` — סטטוס כללי של BDB.
- `check_bdb_dead_nodes_list` — רשימת nodes מתים שמשפיעים על BDB.
- `check_bdb_module_compatibility` — תאימות modules.
- `check_aof_policy_everywrite` — מדיניות AOF everywrite.
- `check_backup_delay` — עיכובי גיבוי.
- `check_backup_in_progress` — גיבויים פעילים כרגע.
- `check_backup_fork_capacity` — קיבולת fork לגיבוי.
- `check_forwarding_state` — מצב forwarding.
- `check_database_balance` — איזון בין clusters.
- `check_acl_consistency` — עקביות ACL.
- `check_authentication_without_cert` — אימות ללא תעודה.
- `check_internal_max_bulk_len` — הגדרת `max_bulk_length`.
- `check_keysizes` — גדלי מפתחות.
- `check_memory_utilization` — שימוש בזיכרון.
- `check_missing_ccs_entries` — כניסות CCS חסרות.
- `audit_shard_txt_config_drift` — drift בתצורת shard.

### 12.4 בדיקות Usage (`06_usage`)

- `average_key_size_per_bdb` — גודל מפתח ממוצע.
- `check_3rd_party_processes` — תהליכי צד שלישי על השרת.
- `compare_3rd_party_processes_across_nodes` — השוואת תהליכי צד שלישי בין nodes.
- `compare_all_master_shards_number_of_keys` — מספר מפתחות בין shards.
- `compare_all_master_shards_used_memory` — זיכרון בין shards.
- `check_commands_to_notify` — פקודות שיש להתריע עליהן.
- `check_database_persistence` — persistence ב-DB.
- `check_node_persistence_storage` — אחסון persistence ב-node.
- `check_eviction_policy_configured` — מדיניות eviction.
- `check_license_shard_limits` — מגבלות license על shards.
- `check_swap` — שימוש ב-swap.
- `check_time_service_running` — שירות זמן (chronyd / ntpd).
- `check_uptime` — uptime.
- `connection_reset_by_peer` — בעיות חיבור.
- `connection_reset_unnamed_clients` — חיבורים שמתאפסים בלי שם.
- `core_even_test` — מספר ליבות זוגי.
- `detect_lua_usage` — שימוש ב-Lua scripts.
- `detect_memory_limit_reached` — הגעה למגבלת זיכרון.

### 12.5 בדיקות Upgrade (`07_upgrade_healthcheck`)

- `check_os_module_upgrade_compatibility` — תאימות modules לשדרוג מערכת הפעלה.

### 12.6 בדיקות RDI (`10_rdi`)

- `00_detect_rdi` — זיהוי האם RDI (Redis Data Integration) מותקן.
- `01_analyze_rdi_logs` — ניתוח לוגי RDI.
- `02_extract_rdi_config` — חילוץ תצורת RDI.
- `03_render_rdi_tables` — יצירת טבלאות RDI בדוח.

### 12.7 ניתוח לוגים (`90_log_analysis`)

- `check_sasl_packages` — חבילות SASL.
- `events_parser` — ניתוח אירועים.
- `log_formatters` — עיצוב לוגים לדוח.
- `logs_patterns` — זיהוי דפוסי שגיאה ידועים.

### 12.8 ניתוח Failover (`91_failover_analysis`)

- `process_failovers` — עיבוד אירועי failover.
- `ccs_state_machine_debug` — debug של state machine.

### 12.9 חלקי "Print Info" (`95_print_info`)

יוצר את הטבלאות בדוח: cluster, license, nodes (טבלה + cards), DBs, LDAP, certificates, modules, persistence, Azure, security, 3rd-party processes, CRDB info, network issues, users, replicaof.

### 12.10 שגיאות והמלצות (`96_errors`)

- `11_print_errors` — אסיפת כל השגיאות לטבלה אחת.
- `12_export_recommendations_audit` — ייצוא המלצות לתיקון.

### 12.11 יצירת HTML (`97_html`)

- `15_create_ccs_viewer` — viewer ל-CCS.
- `20_create_html` — יצירת ה-HTML הראשי.
- `22_create_usage_report_html` — דוח usage נפרד.
- `25_export_json` — ייצוא JSON (מבוטל עם `--export-json` או `REDISSCOPE_DISABLE_JSON_EXPORT`).

### 12.12 סיום (`99_end`)

- `9999_print_end_message` — הודעת סיום וסיכום.

---

## 13. מנגנון ה-Masking לעומק

### איך זה עובד פנימית

הקוד מ-`general/generate_data_helpers/masking.py`:

> *Create masking map for IPs, domains, and other sensitive data.*
> *NOTE: This function ONLY creates the mapping - it does NOT modify the data objects.*
> *The actual masking is applied later during HTML generation by replacing strings in HTML files.*
> *This ensures that:*
> *1. RedisScope runs normally without masking during data processing*
> *2. Original unmasked HTML is generated in redisscope_html/*
> *3. Masked HTML is created in redisscope_html_mask/ at the end*

כלומר:
1. הניתוח רץ **כרגיל** עם הנתונים האמיתיים.
2. נוצר HTML רגיל ב-`redisscope_html/`.
3. בסוף, **post-processing** מעתיק את כל קבצי HTML ל-`redisscope_html_mask/` ומחליף בהם את המחרוזות הרגישות לפי מיפוי.

### מה נכלל ב-mapping

קובץ `mask_mappings.json` (נוצר בתיקיית הריצה) מכיל:

```json
{
  "bdb_names": [
    { "original": "test",  "new": "db-1" },
    { "original": "dummy", "new": "db-2" }
  ],
  "node_internal_ips": [
    { "original": "172.31.32.157", "new": "1.1.1.1" },
    { "original": "172.31.33.239", "new": "2.2.2.2" },
    { "original": "172.31.44.210", "new": "3.3.3.3" }
  ],
  "node_external_ips": [],
  "cluster_name": [
    {
      "original": "karmi3.primary.cs.redislabs.com",
      "new": "redis.domain.com"
    }
  ]
}
```

### Client IPs

יש פונקציה `generate_client_ip` שיוצרת כתובת IP אקראית עבור client IPs (כדי שלא יתנגשו עם ה-masked IPs של ה-nodes).

### שימוש מומלץ

```bash
./redisscope --sp sp.tar.gz --mask

# אחרי הסיום:
# - להעלות ל-ticket: redisscope_html_mask/ ו-redisscope_upload_to_ticket/
# - לשמור פנימית: mask_mappings.json (לתרגום חזרה כשמקבלים תשובה)
```

---

## 14. זיהוי Cloud אוטומטי

הכלי מזהה אוטומטית אם חבילת התמיכה מגיעה מ-Redis Cloud. מתוך הקוד:

> *Detect if the current support package is from a Redis Cloud deployment.*
> *Only detects Redis Cloud Pro and Redis Cloud (not Azure or K8s).*
> *Azure clusters are detected separately but don't use the --cloud flag.*

### איך זה מזוהה

הכלי בודק את הנתונים הבאים:

1. **קובץ `ccs-redis.json`** או **`ccs-redis.rdb`** או **`database_*/database_*_ccs_info.txt`** — מחפש בתוכם:
   - `dns_names: rlrcp.com` → Redis Cloud Pro
   - `dns_names: cloud.redislabs.com` → Redis Cloud
2. **קובץ `.rladmin`** — מחפש את חלק `DATABASES:` ובעיקר `db:DB:ID`.
3. **שם ה-cluster** מקובץ `cluster` (cluster info).

### הודעות הזיהוי

```
☁️ Detected Redis Cloud Pro deployment (dns_names: rlrcp.com)
☁️ Detected Redis Cloud deployment (dns_names: cloud.redislabs.com)
☁️ Auto-detected cloud BDB ID: <id>
☁️ Cloud deployment detected - using BDB ID: <id>
☁️ Auto-detected <N> cloud BDB IDs: <list>
```

### עקיפה ידנית

`--cloud INT` ו-`--bdb INT` מאפשרים לעקוף את הזיהוי.

---

## 15. מצב Active-Active (CRDB)

המצב הזה מנתח cluster Redis Enterprise כשמדובר בפריסת **Active-Active** עם מספר clusters משתתפים שמסנכרנים ביניהם (Conflict-Free Replicated Database).

### דרישות מבנה תיקייה

```
aa-debug/
├── cluster1/           ← חבילת תמיכה מחולצת של cluster ראשון
│   ├── node_*/
│   ├── cluster_info
│   ├── ccs-redis.json
│   └── ...
├── cluster2/           ← חבילת תמיכה מחולצת של cluster שני
└── cluster3/           ← וכו'
```

### הפעלה

```bash
cd aa-debug
../redisscope --aa
```

### סינון

יש שלושה פלגי סינון שמצמצמים את הניתוח:

```bash
# רק clusters ששמם תואם תבנית
../redisscope --aa --aa-filter-cluster "prod-*"

# רק CRDB ספציפי
../redisscope --aa --aa-filter-crdb "session-cache"

# רק BDB ID ספציפי
../redisscope --aa --aa-filter-bdb 5

# שילוב
../redisscope --aa \
  --aa-filter-cluster "prod-*" \
  --aa-filter-crdb "session-cache" \
  --aa-filter-bdb 5
```

### הודעות זיהוי

```
🔗 Active-Active Multi-Cluster Debug Mode
==================================================
```

---

## 16. מצב Kubernetes (מוסתר)

הפלג `--k8s` לא מופיע ב-`--help` הרגיל אבל הוא תומך בניתוח clusters שרצים על Kubernetes / OpenShift.

### מה הוא עושה

המודול `redisscope.general.k8s_log_collector` עם הפונקציה `process_k8s_if_needed()`:

- מזהה האם חבילת התמיכה כוללת תיקייה מסוג `k8s_log_collector`.
- מעבד פלט של `kubectl logs` ו-`kubectl describe`.
- מתאים את הניתוח למבנה namespace של k8s.
- מגדיר משתני סביבה: `K8S_ONLY_MODE`, `K8S_NAMESPACE_DIR`, `K8S_ORIGINAL_DIR`.

### הודעות

```
🐳 Kubernetes mode enabled
❌ Failed to process k8s log_collector: <reason>
❌ K8s processing error: <reason>
```

### הפעלה

```bash
./redisscope --sp sp.tar.gz --k8s
```

---

## 17. פתרון בעיות

### `Permission denied`

```bash
chmod +x ./redisscope
# או:
chmod +x ./run_redisscope.sh
```

### `Exec format error`

הבינארי הוא x86_64, יש לוודא שהשרת הוא x86_64 ולא ARM:

```bash
file ./redisscope
# צריך להיות: ELF 64-bit LSB executable, x86-64
uname -m
# צריך להיות: x86_64
```

### `Support package file not found`

הכלי לא מצא את הקובץ שצוין ב-`--sp`. בדוק נתיב מלא:

```bash
./redisscope --sp $(pwd)/support_pkg.tar.gz
```

### `Unsupported file format`

הפורמטים הנתמכים: `.tar.gz`, `.tgz`, `.tar`, `.zip`. אם הקובץ שלך הוא משהו אחר (`.7z`, `.bz2` וכו'), יש להמיר אותו תחילה.

### `Partial extraction: Archive appears corrupt or incomplete`

הארכיון פגום. הכלי ינתח חלקית ויסמן זאת בדוח. ההמלצה היא להוריד מחדש את חבילת התמיכה. הפלט יכלול:

- הקובץ `.redisscope_extraction_error.json`
- שורת CRITICAL בדוח: "Archive Extraction Error"

### `RedisScope failed to start due to incompatible Python syntax`

מופיע אם מנסים להריץ את הבינארי על Python ישן (< 3.10). **לא רלוונטי לבינארי standalone** אבל אם תנסה להריץ את הקוד המקור — תקבל את ההודעה.

### דוח לא נוצר

```bash
# לבדוק לוגים:
ls redisscope_logs/
cat redisscope_logs/global.log

# לרוץ בvverbose:
./redisscope --sp sp.tar.gz --verbose
```

### Out of disk space

הכלי דורש מקום פנוי של לפחות **2x גודל הבינארי** ב-`/tmp` (לחילוץ PyInstaller) + **2x גודל החבילה** בתיקיית הריצה. סך הכל לפחות 1GB פנוי לחבילה רגילה.

```bash
df -h /tmp .
```

### לוגי הכלי איפה

```
redisscope_logs/
├── data_generation.log        ← שלב יצירת הנתונים
├── global.log                 ← לוג כללי
└── plugin_*.log               ← לוג של כל פלאגין בנפרד
```

---

## 18. אי-התאמות מול התיעוד הרשמי

### vs. `README.txt` בחבילה

ה-README הרשמי בחבילה מציג:

```
./redisscope /path/to/support_package.tar.gz
```

**זה שגוי.** הכלי לא תומך בארגומנט positional. הצורה הנכונה היא:

```
./redisscope --sp /path/to/support_package.tar.gz
```

ה-`./redisscope <file>` ייצור הודעת שגיאה: `error: unrecognized arguments: <file>`.

### vs. PDF הישן

ה-PDF הישן (`RedisScope Installation and Operation.pdf`) מציג:

| נושא | ב-PDF | במציאות |
|---|---|---|
| OS | RHEL 8 | RHEL 9 |
| Archive format | `.zip` | `.tar.gz` |
| Binary name | `redisscope-rhel` | `redisscope` |
| Execution | `../redisscope` מתיקייה עם חבילה מחולצת | `--sp` או הרצה מתיקייה |

ה-PDF הישן **דווקא צודק** לגבי דפוס ההפעלה משיטה B (מתיקייה עם חבילה מחולצת), אבל מפספס את `--sp`, את כל מצב Active-Active, וכן את 20+ הפלגים החדשים שנוספו מאז.

### פלגים שלא מתועדים בכלל

הפלגים הבאים תומכים על ידי הכלי אבל לא מופיעים בשום מקום (`argparse.SUPPRESS`):

- `--k8s`
- `--export-json`

---

## 19. Cheat Sheet — תרגום מהיר

### הפעלות נפוצות

```bash
# ניתוח בסיסי
./redisscope --sp sp.tar.gz

# עם דוח ממוסך
./redisscope --sp sp.tar.gz --mask

# טווח תאריכים
./redisscope --sp sp.tar.gz --start 2026-05-01 --end 2026-05-15

# verbose + טווח + ticket
./redisscope --sp sp.tar.gz -v --start 2026-05-01 --ticket 12345 \
  --title "Customer ABC Q2 Analysis"

# סריקה מהירה (ללא לוגים)
./redisscope --sp sp.tar.gz --skiplogs

# Active-Active
cd aa-dir; ../redisscope --aa

# UI ישן (single page)
./redisscope --sp sp.tar.gz --shiry

# UI חדש (single page)
./redisscope --sp sp.tar.gz --single

# K8s mode (מוסתר)
./redisscope --sp sp.tar.gz --k8s

# גרסה
./redisscope --version

# עזרה
./redisscope --help
```

### טבלת פלגים בקצרה

| פלג | קצור | סוג | תיאור |
|---|---|---|---|
| `--sp FILE` | — | str | חבילת תמיכה לחילוץ |
| `--sp-name NAME` | — | str | שם להצגה בדוח |
| `--filescom-path PATH` | — | str | קישור Files.com |
| `--start "..."` | — | date | תאריך התחלה |
| `--end "..."` | — | date | תאריך סיום |
| `--cloud INT` | `-c` | int | Cloud ID |
| `--bdb INT` | — | int | BDB ID |
| `--mask` | — | flag | דוח מצונזר |
| `--ticket ID` | — | str | מזהה Zendesk |
| `--title TEXT` | — | str | כותרת דוח |
| `--verbose` | `-v` | flag | פלט מפורט |
| `--skiplogs` | — | flag | דלג על לוגים |
| `--force-full` | — | flag | סריקת לוגים מלאה |
| `--count-pattern-occurrences` | — | flag | ספירת דפוסים |
| `--single` | — | flag | HTML יחיד |
| `--shiry` | — | flag | UI ישן |
| `--aa` | — | flag | Active-Active |
| `--aa-filter-cluster P` | — | str | סינון cluster |
| `--aa-filter-crdb P` | — | str | סינון CRDB |
| `--aa-filter-bdb ID` | — | str | סינון BDB |
| `--test` | — | flag | מצב בדיקה |
| `--k8s` | — | flag | (מוסתר) Kubernetes |
| `--export-json` | — | flag | (מוסתר) JSON |
| `--version` | — | flag | גרסה ויציאה |
| `--help` | `-h` | flag | עזרה |

### תיקיות פלט בקצרה

| תיקייה | מה יש בה | תעלה לכרטיס? |
|---|---|---|
| `redisscope_html/` | HTML מלא | אם לא masked |
| `redisscope_html_mask/` | HTML ממוסך | ✅ כן |
| `redisscope_all/` | נתונים גולמיים | בדרך כלל לא |
| `redisscope_logs/` | לוגי הכלי | רק לבדיקת בעיות בכלי |
| `redisscope_upload_to_ticket/` | אוסף מסונן | ✅ כן |
| `redisscope_sp/` | חבילה מחולצת | ❌ לא |

---

## הערות חשובות

> ⚠️ **RedisScope can make mistakes.**
> הדוחות הם כלי עזר לאבחון — יש לוודא ממצאים קריטיים בכלים נוספים לפני נקיטת פעולה במערכת ייצור.

> 📞 **תמיכה:** support@redis.com

> 📚 **תיעוד רשמי של Redis:** https://redis.io/docs/

---

*מסמך זה הופק על בסיס ניתוח הקוד של RedisScope 1.24.5 ואומת בהרצה אמיתית של הבינארי על RHEL 9.7 x86_64.*
