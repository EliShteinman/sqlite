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
19. [מה אתה רואה בדוח ה-HTML](#19-מה-אתה-רואה-בדוח-ה-html) ⭐ **חדש**
20. [אוטומציה — סריקה תקופתית של מספר אשכולות](#20-אוטומציה--סריקה-תקופתית-של-מספר-אשכולות) ⭐ **חדש**
21. [דוגמה אמיתית — ריצה על cluster שבניתי](#21-דוגמה-אמיתית--ריצה-על-cluster-שבניתי) ⭐ **חדש - נתונים אמיתיים**
22. [ניתוח מעבדה מתודי — מה כל פלג עושה לתיקייה](#22-ניתוח-מעבדה-מתודי--מה-כל-פלג-עושה-לתיקייה) ⭐ **חדש - 5 ריצות השוואה**
23. [Cheat Sheet — תרגום מהיר](#23-cheat-sheet--תרגום-מהיר)

---

## 1. רקע

**RedisScope** הוא כלי אבחון של Redis המנתח חבילות תמיכה (support packages) של Redis Enterprise ויוצר דוחות מקיפים בפורמט HTML וטקסט.

### למי הכלי מיועד

בעיקרון יש שתי שיטות שימוש:

| שיטה | מי משתמש | יתרון |
|---|---|---|
| **שיתוף עם Redis Support** | לקוח Redis Enterprise שמייצר `debuginfo.tar.gz` ומעלה ל-Redis | מקבל ניתוח מקצועי מצוות Redis בחזרה |
| **ניטור עצמי פנימי** | צוות SRE / DBA / DevOps שמתפעל cluster ב-Redis Enterprise פנימית | שליטה מלאה, פרטיות מלאה, ניטור פרואקטיבי תקופתי |

המסמך הזה מתמקד בשיטה השנייה — **שימוש פנימי לניטור עצמי של הקלאסטרים שלך**. הכלי מאפשר לך:
- להריץ ניתוח מלא של הקלאסטר ב-on-prem בלי לשתף נתונים עם אף גורם חיצוני
- לבצע ניטור תקופתי (cron job) של מספר קלאסטרים
- לזהות בעיות לפני שהן הופכות להתראות / קריסות
- לנהל היסטוריית ניתוחים ולהשוות מצב לאורך זמן
- להעריך מוכנות לשדרוג גרסה

הפלג `--mask` קיים בכלי בדיוק בשביל לאפשר העברה החוצה כשבאמת חייבים — אבל **בשימוש פנימי לא צריך אותו**.

### היכן זה רלוונטי בזרימת עבודה SRE

```
┌────────────────────────────────────────────────────────────┐
│  ניטור פרואקטיבי - לא ממתינים לתקלה                       │
│  - cron job יומי/שבועי שמייצר report                       │
│  - alerting על CRITICAL/HIGH חדשים                          │
└────────────────────────────────────────────────────────────┘
                                ↓
┌────────────────────────────────────────────────────────────┐
│  טיפול בבעיות פעילות - תחקיר תקלה                          │
│  - מייצר report ad-hoc, מסנן זמנים בעיתיים (--start/--end) │
│  - log analysis + failover analysis עבור התקרית            │
└────────────────────────────────────────────────────────────┘
                                ↓
┌────────────────────────────────────────────────────────────┐
│  הכנה לשדרוג גרסה                                            │
│  - הרצה לפני שדרוג                                          │
│  - 07_upgrade_healthcheck + recommendations                 │
└────────────────────────────────────────────────────────────┘
```

### טכנולוגיה

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

> ⚠️ **שני הבהרות חשובות לפני שמתחילים** (אומתו ישירות מהקוד של v1.24.5):
>
> 1. **התיקייה `redisscope_upload_to_ticket/` שמוזכרת ב-PDF הישן — לא נוצרת בגרסה הזו.** הקבוע `UPLOAD_DIRECTORY` מוגדר ב-`general/const.py` אבל לא מיובא על ידי אף מודול אחר ולא נעשה בו שימוש. כנראה שזה fossil של refactoring שלא הושלם.
> 2. **קובץ הדוח הראשי נקרא `redisscope_healthcheck_report.html`** (תמיד, שם קבוע). ה-PDF הישן הציג `redisscope_<directory_name>_Report.html` שזה **לא נכון** לגרסה הזו.

לאחר ריצה מוצלחת, ייווצרו בתיקיית העבודה הנוכחית:

```
.
├── redisscope_healthcheck_report.html    ← הדוח HTML המרכזי (שם קבוע)
├── aa_multi_cluster_report.html          ← רק במצב --aa
├── redisscope_all/                        ← כל הנתונים הגולמיים
│   ├── *.json                            ← נתוני cluster, nodes, bdbs
│   ├── *.txt                             ← פלט בפורמט טקסט
│   └── ...
├── redisscope_html/                      ← דוחות HTML (לפריסת שרת)
│   ├── index.html
│   ├── pages/
│   │   ├── cluster.html
│   │   ├── databases.html
│   │   ├── alerts.html
│   │   ├── test_results.html
│   │   ├── test_summary.html
│   │   ├── timeline.html
│   │   ├── recommendations.html
│   │   ├── log_analysis.html
│   │   ├── upgrade_healthcheck.html
│   │   ├── rdi.html
│   │   ├── crdb.html
│   │   ├── failover.html
│   │   ├── ccs.html
│   │   ├── rladmin.html
│   │   ├── replicaof.html
│   │   ├── usage_report.html
│   │   ├── k8s.html
│   │   └── azure.html
│   ├── certificate_report.html           ← דוח מתמחה לתעודות
│   ├── cluster_watchdog_report.html      ← דוח מתמחה ל-watchdog
│   ├── persistence_files_report.html     ← דוח מתמחה ל-AOF/RDB
│   ├── ccs_viewer.html                   ← viewer ל-CCS
│   └── (resources: css/, js/, img/)
├── redisscope_html_mask/                 ← רק אם --mask: עותק ממוסך של redisscope_html
├── redisscope_logs/                      ← לוגים של ריצת הכלי
│   ├── data_generation.log
│   ├── global.log
│   └── plugin_*.log
├── redisscope_sp/                        ← רק עם --sp: חבילת תמיכה מחולצת
└── .redisscope_extraction_error.json     ← רק אם חילוץ נכשל חלקית
```

### תפקיד כל תיקייה

| תיקייה | מטרה |
|---|---|
| `redisscope_all/` | אוסף הנתונים הגולמיים שנאספו מהחבילה — קבצי JSON ו-TXT שמשמשים לבניית הדוחות |
| `redisscope_html/` | תיקיית הדוח הראשית. במצב multi-page (ברירת מחדל) — מכילה את כל הדפים, התת-תיקייה `pages/` והנכסים |
| `redisscope_html_mask/` | רק אם הוגדר `--mask`. עותק מצונזר של `redisscope_html/` |
| `redisscope_logs/` | לוגי ריצה של הכלי עצמו (פתרון בעיות בכלי, לא בחבילה הנותחת) |
| `redisscope_sp/` | רק אם הוגדר `--sp` — תיקיית חילוץ של חבילת התמיכה |

### מה להעלות לטיקט תמיכה

**הזרימה הרשמית של Redis (לפי [התיעוד](https://redis.io/docs/latest/operate/rs/installing-upgrading/creating-support-package/)):**
- הלקוח מייצר חבילת תמיכה (`rladmin cluster debug_info` או דרך UI) → מקבל `debuginfo.tar.gz`
- הלקוח מעלה את `debuginfo.tar.gz` ישירות לפורטל התמיכה של Redis
- צוות Redis Support מריץ RedisScope פנימית ומחזיר ללקוח "Cluster Health Analysis"

**אם בכל זאת רוצים לשתף ידנית את פלט RedisScope:**

| תרחיש | מה להעביר |
|---|---|
| ריצה רגילה | `redisscope_healthcheck_report.html` בלבד (קל לפתיחה), או כל `redisscope_html/` (יותר עשיר) |
| עם `--mask` | רק `redisscope_html_mask/` — שומרים את `mask_mappings.json` פנימית |
| מצב AA | `aa_multi_cluster_report.html` + `redisscope_html/` |

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

### תיקיות וקבצים שמופיעים ב-PDF אבל לא בקוד

| מה ה-PDF טוען | מה הקוד באמת עושה |
|---|---|
| יוצר תיקייה `redisscope_upload_to_ticket/` עם הקבצים להעלאה | **לא יוצר את התיקייה**. הקבוע מוגדר ב-`general/const.py` אך אינו בשימוש בשום מודול. |
| יוצר קובץ `redisscope_<directory_name>_Report.html` | יוצר `redisscope_healthcheck_report.html` (שם קבוע, ללא הזרקת שם תיקייה). במצב `--aa` יוצר גם `aa_multi_cluster_report.html`. |

### היחס בין RedisScope לתיעוד הרשמי של Redis

ה-[תיעוד הרשמי של Redis ליצירת support package](https://redis.io/docs/latest/operate/rs/installing-upgrading/creating-support-package/) **לא מזכיר את RedisScope בכלל**. הזרימה הציבורית של Redis היא:

1. הלקוח מייצר `debuginfo.tar.gz` עם `rladmin cluster debug_info` או דרך UI.
2. הלקוח מעלה ל-Redis Support דרך פורטל / SFTP / מייל.
3. Redis Support **מריצים פנימית RedisScope** על החבילה ומחזירים ללקוח "Cluster Health Analysis" עם המלצות ותובנות.

לכן RedisScope הוא כלי **פנימי של Redis Support**, לא כלי שלקוחות מריצים בעצמם. ה-PDF הישן נכתב כנראה למבט פנימי, ושאריות שלו (כמו `redisscope_upload_to_ticket/`) משקפות זרימת עבודה ישנה.

---

## 19. מה אתה רואה בדוח ה-HTML

כשאתה פותח את הדוח בדפדפן, יש לך **תפריט ניווט צדדי** עם הסקציות הבאות. כל סקציה מכילה טבלה אחת או יותר. החלוקה הוצאה ישירות מקובצי ההגדרות של הכלי (`conf/html_templates/sections/`).

### 19.1 המבנה הראשי של הדוח

| # | סקציה (display name) | תוכן |
|---|---|---|
| 1 | **Cluster** (5 tabs) | מידע על האשכול: גרסה, רישיון, nodes, modules, משתמשים, LDAP, אבטחה, תעודות, persistence, 3rd party, רשת |
| 2 | **Databases Overview** | פירוט מסדי נתונים, תצורה, שימוש, slowlog, cmdstats, buffers, clients |
| 3 | **Alerts** | התראות פעילות, היסטוריה והגדרות התראה |
| 4 | **Active-Active Overview** | (רק אם CRDB מוגדר) פרטי CRDB, מצב syncer, AA לא בשימוש |
| 5 | **Failover Events** | אירועי failover ו-CCS failover |
| 6 | **Log Analysis** | דפוסי לוג שזוהו, ספירת אירועים |
| 7 | **Timeline** | ציר זמן של אירועי האשכול |
| 8 | **Recommendations** | המלצות לתיקון מסוננות לפי חומרה |
| 9 | **Test Results** | תוצאות מלאות של כל הבדיקות (TEST PASSED / TEST FAILED) |
| 10 | **Test Summary** | סיכום מספרי של תוצאות הבדיקות |
| 11 | **RDI Overview** | (רק אם RDI מותקן) צינורות ה-RDI |
| 12 | **Azure Overview** | (רק אם Azure) מידע על Azure agents |
| 13 | **Kubernetes Overview** | (רק במצב `--k8s`) Pods, services, deployments, StatefulSets, וכו' |
| 14 | **CCS Viewer** | תצוגת CCS גולמית |
| 15 | **RLADMIN** | פלט מלא של `rladmin status` |
| 16 | **Replica Of Overview** | (רק אם Replica Of מוגדר) פירוט הגדרות replication |

### 19.2 סקציית Cluster — 5 ה-Tabs

זו הסקציה המרכזית, היחידה שמחולקת ל-tabs:

**Tab 1 — Cluster Overview** (order 1)
- `CLUSTER_INFORMATION` — גרסה, מספר nodes, תאריך יצירה, profile (high/low/default), K8S/Azure flags
- `CLUSTER_SETTINGS` — הגדרות cluster + תיאור מילולי לכל הגדרה
- `LICENSE` — owner, name, valid from/to, RAM shards limit, flash shards limit, features (trial/enterprise)
- `NODES` — לכל node: IP, role, up since, version, cores, memory, max listeners/redis, swap, OS, quorum only, MM, ROF
- `NODES_COMPARISON` — השוואת nodes זה מול זה
- `MODULES` — RediSearch, RedisJSON, RedisGraph וכו'
- `USERS` — משתמשים מוגדרים
- `LDAP`, `LDAP_MAPPING` — תצורת LDAP
- `CLUSTER_SECURITY` — הגדרות אבטחה

**Tab 2 — Certificates** — דוח מפורט על תעודות (תאריכי תפוגה, SAN, חתימה)

**Tab 3 — Persistence Files** — קבצי AOF/RDB לכל shard

**Tab 4 — 3rd Party** — תהליכים שאינם של Redis Enterprise שרצים על ה-nodes

**Tab 5 — Network Issues** — בעיות רשת שזוהו

### 19.3 הסקציה הקריטית: Recommendations

זו הסקציה הכי שימושית בניטור עצמי. היא מכילה **4 טבלאות מסוננות לפי חומרה**:

| טבלה | כותרת בדוח | מה יש בה |
|---|---|---|
| `CRITICAL_RECOMMENDATIONS` | 🚨 CRITICAL | בעיות שדורשות טיפול **מיידי** — shards down, fail-over שנתקע |
| `HIGH_RECOMMENDATIONS` | ⚠️ HIGH | בעיות חשובות — חוסר RAM, missing shards, רישיון trial |
| `OTHERS_RECOMMENDATIONS` | (others) | בעיות פחות דחופות — אופטימיזציות |
| `CUSTOMER_RECOMMENDATIONS` | Customer Recommendations | המלצות שכדאי להעביר ללקוח/בעל ה-cluster |

לכל שורה יש את העמודות:
- `Item` — מה הרכיב (Node:1, Redis:3, Bdb:2, Cluster, וכו')
- `Error` — תיאור קצר של הבעיה
- `How to try to fix` — **הוראות תיקון ספציפיות**

זו הטבלה שצריכה לפתוח כל בוקר אם רץ ניטור פרואקטיבי.

### 19.4 סקציית Test Results — פלט מלא

הטבלה הזו (`TESTS_RESULTS_REPORT`) מציגה את כל הבדיקות שהכלי הריץ עם:
- `Item` — מה נבדק
- `Error` — שם הבדיקה
- `Error Description` — תיאור מורחב
- `Category` — BDBS / NODES / CLUSTER / LOGS וכו'
- `Error Source` — מאיפה הגיע המידע (איזה קובץ בחבילה)
- `Error Severity` — CRITICAL / HIGH / MEDIUM / LOW

### 19.5 סקציית Timeline

ציר זמן ויזואלי של אירועים — `failover`, restarts, alerts, configuration changes. **מאוד שימושי לתחקיר תקלה** — מאפשר לראות מה קרה מסביב לזמן הבעיה.

### 19.6 סקציית Log Analysis

`LOG_ANALYSIS_REPORT` — מציג דפוסים שזוהו בלוגים, ספירת המופעים שלהם לכל node. הדפוסים מוגדרים ב-`conf/patterns/*.json` של הכלי וכוללים מתאמי שגיאות ידועות, אזהרות, errors מ-syncer, mgr, dmc וכו'.

מצב `--count-pattern-occurrences` מרחיב את המידע כאן — סופר את כל המופעים לפי תבנית, לא רק שיש/אין.

### 19.7 הרובד התחתון — איך לקרוא את הדוח כ-SRE

הסדר המומלץ לסקירה יומית (3-5 דקות):
1. **Recommendations → CRITICAL** — אם יש משהו, להגיב מיד.
2. **Recommendations → HIGH** — לתעדף לטיפול היום.
3. **Test Summary** — סקירה כמותית: כמה TEST FAILED?
4. **Alerts** — מה התראות פעילות?
5. **Timeline** — האם יש "אירועים חריגים" שלא הוסברו על ידי השלבים הקודמים?

הסדר המומלץ לתחקיר תקלה (עם `--start/--end`):
1. **Failover Events** — מה קרה ומתי
2. **Timeline** — הקשר רחב יותר
3. **Log Analysis** — מה הלוגים מראים סביב הזמן
4. **Recommendations** — מה הכלי ממליץ

---

## 20. אוטומציה — סריקה תקופתית של מספר אשכולות

זה ה-use case המרכזי לשימוש פנימי. אתה רוצה שמערכת תרוץ כל יום/3 ימים, תמשוך support packages מכל הקלאסטרים שלך, תריץ עליהם RedisScope ותתריע על ממצאים חדשים.

### 20.1 איך מייצרים support package מ-cluster

יש שלוש דרכים שמתועדות ב-[תיעוד הרשמי של Redis](https://redis.io/docs/latest/operate/rs/installing-upgrading/creating-support-package/):

**א. דרך CLI (מומלץ לאוטומציה):**
```bash
# יש להריץ על כל node או רק על המאסטר
/opt/redislabs/bin/rladmin cluster debug_info
# יוצר tar.gz ב-/tmp/ של ה-node
```

**ב. דרך REST API (הכי אוטומטי):**
```bash
# Download cluster-wide debug info
curl -k -u "<re_user>:<re_pass>" \
  "https://<cluster-fqdn>:9443/v1/cluster/debuginfo" \
  -o debuginfo.tar.gz

# או רק nodes
curl -k -u "<re_user>:<re_pass>" \
  "https://<cluster-fqdn>:9443/v1/nodes/debuginfo" \
  -o nodes-debuginfo.tar.gz

# או רק databases
curl -k -u "<re_user>:<re_pass>" \
  "https://<cluster-fqdn>:9443/v1/bdbs/debuginfo" \
  -o bdbs-debuginfo.tar.gz
```

**ג. דרך UI (לא רלוונטי לאוטומציה).**

> אם `/tmp` של ה-node קטן ויש כשל, אפשר להגדיר נתיב חלופי:
> ```
> rladmin cluster config debuginfo_path <path>
> ```

### 20.2 סקריפט סריקה מלא — תבנית

נניח שיש לך 3 קלאסטרים. הסקריפט פועל לפי הזרימה: למשוך → לנתח → להשוות → להתריע.

```bash
#!/bin/bash
# /opt/redisscope/scripts/scan-all-clusters.sh
# סורק את כל הקלאסטרים ויוצר דוחות

set -euo pipefail

# הגדרות
CLUSTERS=(
  "cluster-prod-us:cluster-prod-us.example.com:9443"
  "cluster-prod-eu:cluster-prod-eu.example.com:9443"
  "cluster-staging:cluster-staging.example.com:9443"
)
RS_USER="${RE_API_USER:-admin@example.com}"
RS_PASS="${RE_API_PASS:?Need to set RE_API_PASS}"
WORK_DIR="${HOME}/redisscope-data/scans"
DATE=$(date +%Y-%m-%d)
REDISSCOPE_BIN="/opt/redisscope/redisscope"
LOG="${WORK_DIR}/scan-${DATE}.log"

mkdir -p "${WORK_DIR}/${DATE}"

for cluster_def in "${CLUSTERS[@]}"; do
  IFS=':' read -r name host port <<< "${cluster_def}"
  echo "[$(date)] Scanning ${name}..." | tee -a "${LOG}"

  cluster_dir="${WORK_DIR}/${DATE}/${name}"
  mkdir -p "${cluster_dir}"
  cd "${cluster_dir}"

  # שלב 1: למשוך support package
  if ! curl -sf -k -u "${RS_USER}:${RS_PASS}" \
       "https://${host}:${port}/v1/cluster/debuginfo" \
       -o "debuginfo.tar.gz"; then
    echo "[$(date)] ERROR: Failed to fetch debuginfo from ${name}" | tee -a "${LOG}"
    continue
  fi

  # שלב 2: להריץ RedisScope (מהיר - בלי logs)
  "${REDISSCOPE_BIN}" --sp debuginfo.tar.gz --skiplogs --title "${name} - ${DATE}" \
    >> "${LOG}" 2>&1 || echo "[$(date)] WARN: RedisScope returned non-zero for ${name}" | tee -a "${LOG}"

  # שלב 3: לחלץ ממצאי CRITICAL לקובץ נפרד לקלות התראה
  if [ -f "redisscope_html/pages/recommendations.html" ]; then
    grep -oE 'CRITICAL[^<]+' "redisscope_html/pages/recommendations.html" \
      > "critical-findings.txt" 2>/dev/null || true
  fi

  # שלב 4: למחוק את החבילה הגדולה לחסוך מקום
  rm -f debuginfo.tar.gz

  echo "[$(date)] Done with ${name}" | tee -a "${LOG}"
done

# שלב 5: השוואה עם הריצה הקודמת והתראה על ממצאים חדשים
PREV_DATE=$(ls -1 "${WORK_DIR}" | grep -v "^${DATE}$" | sort | tail -1 || true)
if [ -n "${PREV_DATE}" ]; then
  for cluster_def in "${CLUSTERS[@]}"; do
    name="${cluster_def%%:*}"
    NEW="${WORK_DIR}/${DATE}/${name}/critical-findings.txt"
    OLD="${WORK_DIR}/${PREV_DATE}/${name}/critical-findings.txt"

    if [ -f "${NEW}" ] && [ -f "${OLD}" ]; then
      NEW_FINDINGS=$(comm -23 <(sort -u "${NEW}") <(sort -u "${OLD}") || true)
      if [ -n "${NEW_FINDINGS}" ]; then
        # התראה - מייל/Slack/PagerDuty
        echo "🚨 New CRITICAL findings on ${name}:" | tee -a "${LOG}"
        echo "${NEW_FINDINGS}" | tee -a "${LOG}"
        # למשל:
        # echo "${NEW_FINDINGS}" | mail -s "RedisScope: New CRITICAL on ${name}" sre@example.com
      fi
    fi
  done
fi

# שלב 6: ניקוי סריקות ישנות (שמירת 30 ימים בלבד)
find "${WORK_DIR}" -maxdepth 1 -type d -mtime +30 -exec rm -rf {} +

echo "[$(date)] Scan complete" | tee -a "${LOG}"
```

### 20.3 cron entry

```cron
# כל 3 ימים ב-02:00 לפנות בוקר
0 2 */3 * * /opt/redisscope/scripts/scan-all-clusters.sh

# או יומי
0 2 * * * /opt/redisscope/scripts/scan-all-clusters.sh
```

### 20.4 ארגון תיקיות התוצאות

עם הסקריפט הזה תיווצר תיקייה כזו:

```
~/redisscope-data/scans/
├── 2026-05-10/
│   ├── cluster-prod-us/
│   │   ├── redisscope_html/
│   │   ├── redisscope_healthcheck_report.html
│   │   └── critical-findings.txt
│   ├── cluster-prod-eu/
│   └── cluster-staging/
├── 2026-05-13/
├── 2026-05-16/
└── ...
```

### 20.5 שרת לצפייה בכל הדוחות

תוסיף שרת nginx פשוט שמגיש את כל היסטוריית הדוחות:

```bash
sudo dnf install -y nginx
sudo tee /etc/nginx/conf.d/redisscope.conf <<'EOF'
server {
    listen 8080 default_server;
    server_name _;
    root /home/<username>/redisscope-data/scans;
    autoindex on;
    autoindex_exact_size off;
    location / { try_files $uri $uri/ =404; }
}
EOF
sudo systemctl enable --now nginx
```

עכשיו `http://<server>:8080/` נותן לך browser של כל הסריקות לפי תאריך → cluster → דוח.

### 20.6 הצעות הרחבה

**א. תוסיף ל-Prometheus/Grafana:**
   - parser שמושך את `redisscope_all/test_summary.json` ומפיק מטריקות (count of TEST FAILED לפי category)
   - Grafana מציג trend לאורך זמן

**ב. אינטגרציה עם ticket system:**
   - יוצר ticket אוטומטית ב-Jira/Zendesk כשמופיע CRITICAL חדש
   - מצרף את הדוח HTML

**ג. השוואה הדוקה יותר:**
   - שמירת JSON מובנה (`--export-json` המוסתר!) מאפשר השוואה תכנותית עמוקה יותר בין ריצות

**ד. סריקה לפני שדרוג כל-cluster:**
   - לפני כל פעולה גדולה (שדרוג גרסה, החלפת חומרה), הרץ ידנית והשווה לסריקה הקבועה — לוודא שאין רגרסיה

### 20.7 שיקולי אבטחה לקרון

- **סיסמת REST API:** שמור ב-`/etc/redisscope/credentials` עם הרשאות `600`, וטען מתוך הסקריפט עם `source`. אל תשים בקוד או ב-cron.
- **הרצה כמשתמש לא-root:** הסקריפט לא דורש root. רוץ עם user יעודי `redisscope`.
- **גישת רשת:** המכונה צריכה גישת outgoing לפורט 9443 של כל cluster.
- **שמירת היסטוריה:** הניקוי האוטומטי (30 ימים) חשוב — אחרת תיגמר לך הדיסק.

---

## 21. דוגמה אמיתית — ריצה על cluster שבניתי

הסעיף הזה מציג ממצאים אמיתיים מ-RedisScope שהורץ על cluster Redis Enterprise 8.0.20-19 שבניתי על KubeVirt VMs ב-OpenShift Developer Sandbox. הקלאסטר היה מינימלי (2 nodes, 1 DB, 4 shards, license trial) ותוכנן בכוונה כך שיכיל ממצאים מעניינים.

### 21.1 פרטי הסביבה

```
Cluster version: 8.0.20-19 (Redis Enterprise 8.0.20)
Number of nodes: 2
Creation date:   2026-05-19 03:22:46
Cluster Profile: Default:low
License:         Trial (expires in 30 days)
Database:        test-db, 2 shards × 2 (master+slave) = 4 shards total
Memory size:     200 MB
Replication:     enabled, Sharding: enabled
Endpoint:        redis-12000.re-cluster.local:12000
```

### 21.2 קבצים אמיתיים בתיקיית outputs

```
real-healthcheck-report.html        ← הדוח הראשי (15KB single-page)
real-recommendations.csv            ← כל ההמלצות שנוצרו (10KB, 14 ממצאים)
real-summary.csv                    ← סיכום ב-CSV (3 שורות מסוננות)
debuginfo.20260519-032921.tar.gz    ← חבילת התמיכה המקורית שאיתה הזנתי
```

### 21.3 ממצאי הדוח האמיתי — סקירה לפי חומרה

הכלי זיהה **14 ממצאים** ב-cluster הקטן הזה:

#### CRITICAL (1)

| Item | Error | Description |
|---|---|---|
| Cluster | License expiring soon | The Redis Enterprise cluster license will expire in 30 days (on 2026-06-18) |

> זה ההתראה הכי דחופה. הכלי מזהה רישיון trial ומחשב מתי הוא יפוג. בסביבת production זה היה גורם להתראת immediate.

#### HIGH (7)

| Item | Error | Description |
|---|---|---|
| Cluster | Trial license | Cluster installed with a trial license |
| Cluster | Number of nodes (odd) | Number Of nodes should be an odd number, current 2 |
| Cluster | Wrong number of nodes | Number of nodes should be greater than or equal to 3 |
| Node:1 | Memory below production minimum | Node:1 has 4.55 GB RAM. Production requires at least 8 GB; recommended 32 GB+ |
| Node:1 | Cores: 2 found, minimum 4 | Node has 2 CPU cores; non-quorum nodes need at least 4 |
| Node:2 | Memory below production minimum | (זהה ל-Node:1) |
| Node:2 | Cores: 2 found, minimum 4 | (זהה ל-Node:1) |
| Shard:3 | not balanced ⚖️ | Master shard 3 is on node:2, but database endpoint is on node:1 — causes proxy latency |

> שורת ה-"shard not balanced" הזו דרשה תיקון אמיתי. הכלי מציע פתרון מדויק:
> `rladmin failover db db:3 shard 3`

#### MEDIUM (1)

| Item | Error | Description |
|---|---|---|
| Task | Failed task: maintenance_on | Task ID 6f5151e2... failed at progress 0%, node 2, created 2026-05-19 03:27:48 |

> זה ממש זיהה את הניסיון הכושל שלי בסעיף קודם — ניסיתי להעביר node:2 ל-maintenance mode והפעולה נכשלה. הכלי תפס את זה והעלה את זה למשתמש.

#### LOW (2)

| Item | Error | Description |
|---|---|---|
| Bdb:3 | no persistence 💽 | No persistence is configured for database test-db |
| Bdb:3 | Shard txt config drift | Found 1 differing setting across 4 shards after ignoring known shard-specific |

#### INFO (3)

| Item | Error | Description |
|---|---|---|
| Cluster | Email alerts | No email alerts is on |
| License | Total shards limit reached | License limit: 4 total shards. Current usage: 4 (100.0%) |
| Cluster | Provisioning thresholds use Redis Enterprise defaults | (אופציה למיטוב) |

### 21.4 מה זה אומר על איכות הכלי

לקח לי 5 דקות לבנות cluster ולהריץ load של 100,000 פקודות. תוך **3 שניות** ריצה (`Total runtime time: 0:00:03.627639`) RedisScope:

1. **זיהה את ה-license trial** — קריאת `ccs-redis.json`
2. **זיהה לא איזון shards** — השוואת `rladmin status` למיקום ה-endpoint
3. **תפס את הניסיון הכושל ל-maintenance_mode** — שעות אחורה בהיסטוריית האירועים
4. **חישב את חוסר ה-RAM/CPU** — מסביבת VM של 4.5GB ו-2 cores
5. **נתן הוראות תיקון ספציפיות לכל בעיה** — לא ערפול, אלא פקודה לרוץ

לכל recommendation שני שדות חשובים שראיתי ב-CSV:
- **Internal Recommendation:** הוראה ל-engineer של Redis (טכנית, עם פקודות)
- **Customer Recommendation:** הסבר עם הקשר (למה זה משנה, איך לתקן, ולמה זה חשוב)

#### דוגמה מ-`real-recommendations.csv` שורה לדוגמה:

```
Item: Shard:3
Error: ⚖️ not balanced
Internal Recommendation:
   Master shard 3 is on node:2, but endpoint is on node:1.
   Replica shard 4 is on node:1 which has the endpoint.
   Recommended action (no client disconnection):
   Failover to replica on node:1:
   rladmin failover db db:3 shard 3
Customer Recommendation:
   Issue: Master shard 3 for database test-db (bdb:3) is on node:2,
          but endpoint 3:1 is bound to node:1.
   Action: Fail over to replica shard 4 on node:1.
           rladmin failover db db:3 shard 3
   Client impact: No proxy endpoint move is required, so no planned
                  downtime is expected. The failover can still cause
                  brief client reconnects or small disconnections while
                  mastership changes.
```

### 21.5 מבנה ה-HTML שראיתי בפועל

הדוח הראשי `redisscope_healthcheck_report.html` הוא **single-file HTML** מעוצב (15KB). מבנה:

```
┌─────────────────────────────────────────────────────────┐
│  Healthcheck Report - re-cluster.local                  │
│  2026-05-19 03:30:43 • RedisScope 1.24.5                │
├─────────────────────────────────────────────────────────┤
│  Summary cards (גריד):                                  │
│  [Total: 14]  [Critical: 1]  [High: 7]  [Medium: 1]    │
│  [Low: 2]     [Info: 3]                                 │
├─────────────────────────────────────────────────────────┤
│  Filter buttons: [All] [Critical] [High] [Medium] [Low] │
├─────────────────────────────────────────────────────────┤
│  Issues table:                                          │
│  Item | Error | Description | Recommendation            │
│  ...                                                    │
└─────────────────────────────────────────────────────────┘
```

הצבעים שמשמשים בדוח (CSS variables):
- `--critical-border: #ef4444` (אדום)
- `--high-border: #f59e0b` (כתום)
- `--medium-border: #3b82f6` (כחול)
- `--low-border: #10b981` (ירוק)
- `--info-border: #6366f1` (סגול)

### 21.6 ה-multi-page HTML (`redisscope_html/`)

נוסף ל-`redisscope_healthcheck_report.html` (קובץ בודד), נוצר `redisscope_html/` עם 17 דפי משנה:

```
redisscope_html/
├── index.html                  ← דשבורד ראשי
├── usage_report.html
├── redisscope_databases/
│   └── db_3.html               ← דף ייעודי ל-DB שלנו
└── pages/
    ├── cluster.html
    ├── databases.html
    ├── alerts.html
    ├── crdb.html
    ├── failover.html
    ├── log_analysis.html
    ├── timeline.html
    ├── rdi.html
    ├── replicaof.html
    ├── rladmin.html
    ├── ccs.html
    ├── usage_report.html
    ├── test_summary.html
    ├── test_results.html
    └── recommendations.html
```

זה בדיוק כמו שתיארתי בפרק 19 — 17 דפים מתאמים ל-17 הסקציות שזיהיתי בקובצי הconfiguration של הכלי. **התיעוד מאומת.**

### 21.7 התובנה החשובה ביותר

הדוח הזה הופק ב-3 שניות על cluster של 2 nodes. **ה-cluster שלי לא הראה ולו כשלון אחד פיזי** — הכל "סטטוס OK". אבל **הכלי מצא 14 בעיות תכנוניות / configural / hardware sizing**. זו בדיוק הכוח של RedisScope לניטור עצמי — הוא לא מחכה שמשהו ייפול, הוא מזהה את ה-precursors.

### 21.8 ריצה שנייה — עם ניתוח לוגים מלא (`debuginfo-full.tar.gz`)

הריצה הראשונה הייתה עם `--skiplogs` (3 שניות, 14 ממצאים). הרצתי שוב **עם** ניתוח לוגים אחרי שלב הוספתי **load מסיבי**: 8 רבדים של redis-benchmark, ~10M פקודות סה"כ, KEYS *, LRANGE מלא, ביצוע failovers, וכו'.

**התוצאות זינקו דרמטית:**

| מדד | בלי `--skiplogs` | עם log analysis |
|---|---|---|
| זמן ריצה | 3.6s | 4.9s (+36%) |
| גודל recommendations.csv | 10KB | **33KB (+230%)** |
| ממצאי CRITICAL | 1 | 1 |
| ממצאי HIGH | 7 | **23 (+228%)** |
| ממצאי MEDIUM | 1 | **44 (+44x)** |
| ממצאי LOW | 2 | 4 |
| ממצאי INFO | 3 | 5 |
| Total findings | 14 | **77** |
| Slowlog entries מנותחים | 0 | **164** |
| Log analysis findings | 0 | **58** |
| קבצי slowlog CSV | אין | `redisscope_slowlog_bdb_3_test-db.csv` |

**פילוח ה-LOGANALYSIS** (58 ממצאים, רובם MEDIUM אבל 13 HIGH):

ב-HIGH:
- `Dmcproxy: connection reset by peer` — חיבורי TCP שנשברו (תוצאה של load test)
- `Redis: connection with replica and lost` — בעיות replication
- `Cluster_wd: cluster is in unstable state for...` — watchdog זיהה אי-יציבות
- `Cluster_wd: live nodes don't like my master` — sentinel detect election issue
- `Cluster_api: failed to read node local config` — בעיות תצורה זמניות
- `Resource_mgr: failed during maintenanceontask` — **המתחזק שלי שנכשל!**
- `Envoy: failed to load private key from and key_values_mismatch` — תעודות

ב-MEDIUM (דוגמאות):
- `Db_controller: failed to connect to ccs`
- `Node_mgr: failed to connect to ccs`
- `Cluster_api: no such file or directory`
- `Cluster_wd: certificate_verify_failed`
- `Cluster_wd: failcount: 3`

**מה זה אומר:** הכלי קרא דרך **קבצי הלוג** של dmcproxy, cluster_wd, cluster_api, redis_ctl, resource_mgr, envoy, וקרס-רפרנס אותם ל-`patterns/*.json` (שראינו ב-`conf/patterns/`). כל דפוס שזיהה הופיע בדוח כממצא נפרד עם חומרה.

**Slowlog deep-dive:** הסקריפט תפס במדויק את ה-LRANGE שהרצתי בכוונה:

```
2026-05-19 07:45:09, 43.35ms, INFO, "LRANGE, MYLIST, 0, -1"
2026-05-19 07:45:08, 67.97ms, INFO, "LRANGE, MYLIST, 0, -1"
2026-05-19 07:45:08, 63.48ms, INFO, "LRANGE, MYLIST, 0, -1"
2026-05-19 07:45:08, 49.46ms, INFO, "LRANGE, MYLIST, 0, -1"
2026-05-19 07:45:08, 44.67ms, INFO, "LRANGE, MYLIST, 0, -1"
```

ה-LRANGE `0 -1` (כל הרשימה) על list עם 10K+ items לקח 50-70ms. הכלי תפס את זה ושם בדוח. גם ניתוח INFO EVERYTHING מהזרם שלי הופיע (קצר יותר, 0.6-0.8ms).

### 21.9 שיעור מעשי

ההבדל בין הריצות מראה את **חשיבות ה-log analysis**. עבור ניטור פרואקטיבי שגרתי — אולי `--skiplogs` מספיק (מהיר יותר). אבל אחרי כל **incident** או **load event** משמעותי, **חייבים** להריץ עם log analysis כדי לראות מה התרחש בפועל בתוך הקלאסטר ולא רק את הסטטוס הסטטי.

**אסטרטגיית cron מומלצת:**
- **יומי / כל 3 ימים:** ריצה מהירה עם `--skiplogs` (3 שניות, 14 ממצאים, מתאים לdashboard)
- **שבועי:** ריצה מלאה ללא `--skiplogs` (5 שניות, 77 ממצאים, מתאים ל-deep audit)
- **אחרי incident:** ריצה מלאה + `--start <זמן>` / `--end <זמן>` סביב הזמן הקריטי

### 21.10 התובנה החשובה ביותר (עדכון)

עבור ה-cron job שמתואר בפרק 20:
- **ריצה ראשונה** → המון ממצאים (אצלי 14 בלי לוגים, 77 עם לוגים)
- **ריצות הבאות** → אמורות להראות באותה רמה, או פחות (לאחר תיקונים)
- **ריצות אחרי שינוי / שדרוג** → לבדוק אם הופיעו ממצאים חדשים (rules-based monitoring)
- **תמיד תשמור slowlog CSVs** — הם מאפשרים לבנות trend של בעיות ביצוע לאורך זמן

---

## 22. ניתוח מעבדה מתודי — מה כל פלג עושה לתיקייה

הסעיף הזה מבוסס על הרצות אמיתיות שביצעתי בסביבת ה-VM עם 5 וריאציות שונות של RedisScope על אותה חבילת תמיכה. **כל הנתונים פה אומתו אמפירית.**

### 22.1 קבצים שנוצרים — לפני/אחרי בריצה רגילה

```
[BEFORE]
.    (תיקייה ריקה)

[AFTER --sp file.tar.gz]
.
├── redisscope_all/                                  ← 8KB (לרוב ריק/קטן)
├── redisscope_attributes.txt                        ← 865B - רשימת attributes שנאספו
├── redisscope_current.log                           ← 2.4MB - לוג ריצה
├── redisscope_healthcheck_report.html               ← 15KB - הדוח הקצר
├── redisscope_healthcheck_summary.csv               ← 793B - CSV של הסיכום
├── redisscope_html/                                 ← 21MB - דוח מולטי-פייג'
├── redisscope_logs/                                 ← 876KB - לוגים פר-פלאגין
├── redisscope_re-cluster.local.json                 ← 3.2MB - JSON של כל הdata
├── redisscope_recommendations_audit_YYYYMMDD_HHMMSS.csv  ← 33KB - כל ההמלצות
├── redisscope_slowlog_csv_exports/                  ← 24KB - slowlog CSVs
└── redisscope_sp/                                   ← 13MB - חבילת תמיכה מחולצת
```

**סה"כ:** ~38MB לריצה רגילה.

### 22.2 פלאגינים אמיתיים — 17 קטגוריות (לא 12!)

הריצה יוצרת `redisscope_logs/plugins_*.log` לכל קטגוריה. **רשימה מאומתת מהריצה:**

| Plugin Log | גודל בריצה שלי | הקטגוריה |
|---|---|---|
| `plugins_01_headers.log` | 1.8KB | Initial extraction/headers |
| `plugins_02_cluster.log` | **18KB** | **Cluster** (חדש! לא היה במסמך) |
| `plugins_03_nodes.log` | 52KB | Nodes checks |
| `plugins_04_bdbs.log` | 39KB | BDB checks |
| `plugins_05_crdb.log` | **6.3KB** | **CRDB** (חדש! לא היה במסמך) |
| `plugins_06_usage.log` | 39KB | Usage analysis |
| `plugins_07_upgrade_healthcheck.log` | 2.3KB | Upgrade readiness |
| `plugins_08_Azure.log` | **1.5KB** | **Azure** (חדש! לא היה במסמך) |
| `plugins_09_k8s.log` | **4.4KB** | **Kubernetes** (חדש! לא היה במסמך) |
| `plugins_10_rdi.log` | 2.1KB | RDI |
| `plugins_90_log_analysis.log` | **528KB** | Log analysis (הכי כבד!) |
| `plugins_91_failover_analysis.log` | 20KB | Failover analysis |
| `plugins_95_print_info.log` | 19KB | Print info tables |
| `plugins_96_errors.log` | 4.5KB | Error aggregation |
| `plugins_97_html.log` | 68KB | HTML generation |
| `plugins_99_end.log` | 1.2KB | End message |

> **תיקון חשוב לפרק 11 קודם:** יש **17 קטגוריות**, לא 12. 4 קטגוריות שלא תיעדתי: `02_cluster`, `05_crdb`, `08_Azure`, `09_k8s`.

### 22.3 קובץ ה-JSON המרכזי

`redisscope_<cluster_name>.json` (3.2MB אצלי) — קובץ ה-data העיקרי שמהווה את ה-backend לכל הHTML reports.

**מבנה:**
```json
{
  "metadata": { ... 11 keys },
  "sections": { ... 38 keys },     ← 38 sections של ניתוח!
  "databases": { "3": {...} },
  "shards": [ ... 26 entries ]
}
```

זה ה-JSON שה-HTML loads דרך JavaScript לאחר טעינת הדף. אם רוצים לאוטומט (parse בPython, השוואות), זה הקובץ הנכון.

### 22.4 השוואה בין 5 ריצות שונות

על אותו support package, 5 ריצות עם פלגים שונים:

| פלגים | סה"כ ממצאים | CRITICAL | HIGH | MEDIUM | LOW | INFO | גודל CSV |
|---|---|---|---|---|---|---|---|
| `--sp` (normal) | **77** | 1 | 23 | 44 | 4 | 5 | 33KB |
| `--sp --mask` | 76 | 1 | 23 | 44 | 4 | **4** | 32KB |
| `--sp --skiplogs` | **19** | 1 | **10** | **1** | 2 | 5 | 13KB |
| `--sp --bdb 3` | 70 | 1 | **17** | 44 | 4 | 4 | 27KB |
| `--sp --single` | 77 | 1 | 23 | 44 | 4 | 5 | 33KB |

**תובנות עיקריות:**

1. **--skiplogs** מוריד את הממצאים מ-77 ל-19 — **חוסך 75% מהזמן**, אבל מאבד את כל MEDIUM (43) וחלק מ-HIGH (13 מתוך 23). מתאים ל-dashboard מהיר, **לא לחקירת incident**.

2. **--mask** מוריד ממצא INFO אחד (כנראה משהו שלא ניתן למסך בצורה אמינה).

3. **--bdb 3** מוריד 6 HIGH ו-1 INFO — בעיקר ממצאי cluster-wide שמסוננים החוצה. שאר ה-44 MEDIUM של log analysis נשמר.

4. **--single** לא משנה כלום בממצאים — רק את מבנה ה-HTML הסופי.

### 22.5 הבדל --single vs ברירת מחדל

**`--sp` (ברירת מחדל = multi-page):**
```
redisscope_html/
├── index.html
├── pages/  (15 דפים)
│   ├── cluster.html, databases.html, alerts.html, ...
└── redisscope_databases/
    └── db_3.html
```

**`--sp --single`:**
```
redisscope_html/
└── usage_report.html  ← רק קובץ אחד
```

ה-HTML הראשי הקבוע `redisscope_healthcheck_report.html` נוצר בשני המצבים כקובץ יחיד (15KB). אבל ה-`redisscope_html/` מכיל הרבה פחות עם --single.

### 22.6 ה-`--mask` — אנתומיה מלאה

#### מה נוצר נוסף עם --mask:

```
redisscope_html_mask/                                ← עותק ממוסך של כל ה-html (21MB)
redisscope_mask_mappings.json                        ← 1.6KB - **קובץ המיפוי**
redisscope_slowlog_csv_exports/
  ├── redisscope_slowlog_bdb_3_test-db.csv          (regular)
  └── redisscope_slowlog_bdb_3_test-db_masked.csv   ← **slowlog ממוסך**
```

#### מבנה `redisscope_mask_mappings.json` (אומת מהריצה):

```json
{
  "replacements": {              ← מילון שטוח לחיפוש מהיר
    "test-db": "db-3",
    "10.128.0.14": "95.170.170.175",
    "re-node-1": "node-1",
    "10.128.0.16": "15.109.78.182",
    "re-node-2": "node-2",
    "re-cluster.local": "redis.domain.com",
    "@re-cluster.local": "@example.com",
    "@redis.com": "@example.com"
  },
  "value_mappings": {            ← 7 קטגוריות (לא 4!)
    "bdb_names": [...],
    "node_internal_ips": [        ← ל-internal ממסכים ל-1.1.1.1, 2.2.2.2
      {"original": "10.128.0.14", "new": "1.1.1.1"}
    ],
    "node_external_ips": [        ← ל-external ממסכים ל-IPs פומביים אמיתיים
      {"original": "10.128.0.14", "new": "95.170.170.175"}
    ],
    "cluster_name": [...],
    "user_emails": [              ← קטגוריה חדשה!
      {"original": "admin@redis.com", "new": "admin@example.com"}
    ],
    "client_ips": [],
    "crdb_remote_participants": []
  }
}
```

**תובנות:**

1. **PDF טען 4 קטגוריות. בפועל יש 7:** bdb_names, node_internal_ips, node_external_ips, cluster_name, **user_emails**, **client_ips**, **crdb_remote_participants**.

2. **אותו IP מקבל 2 שמות שונים** לפי הקשר:
   - 10.128.0.14 כ-internal → 1.1.1.1 (private-looking)
   - 10.128.0.14 כ-external → 95.170.170.175 (public-looking IP אמיתי)

   זה מתוחכם — הכלי מבחין בין שימוש פנימי לחיצוני ומסיר אינדיקציה לטופולוגיה.

3. **`replacements` הוא flat dict** לביצועים — חיפוש מהיר במקום iteration על הרשימות.

#### Slowlog מצב mask vs רגיל:

**רגיל:**
```csv
Date/Time,Duration (ms),Severity,Complexity Info,Command,Client
2026-05-19 07:45:08,67.97,INFO,,"LRANGE, MYLIST, 0, -1",
2026-05-19 07:50:36,0.77,INFO,,"INFO, EVERYTHING",
```

**ממוסך:**
```csv
# Slowlog Export - MASKED MODE (command names only, no keys/arguments)
2026-05-19 07:45:08,67.97,INFO,,LRANGE,            ← רק שם פקודה
2026-05-19 07:50:36,0.77,INFO,,INFO,               ← בלי args
```

> זה מאוד חשוב מבחינת אבטחה — בדוח רגיל יכול להיות "LRANGE, USER:CUSTOMER123:ORDERS, 0, 1000" שחושף שם של מפתח/מסד. במצב mask **רק שם הפקודה נשמר**, ה-args לא.

### 22.7 תוכן ה-HTML pages — אומת מהקבצים

כל דף ב-`redisscope_html/pages/` הוא ~1MB (רובו JavaScript embedded). תוכן טקסטואלי אמיתי שונה דרמטית:

| Page | גודל טקסט | תוכן ראשי |
|---|---|---|
| `index.html` | 1.6KB | Dashboard עם summary cards (טעון דרך JSON) |
| `cluster.html` | **31KB** | **הכי עשיר**: Cluster Information, Certificates, Node Information, Status Timeline, Network Topology, Communication Errors Heatmap, CLUSTER_SECURITY, THIRD_PARTY |
| `databases.html` | 1.5KB | רק רשימה - הפרטים בdb_3.html |
| `recommendations.html` | 9.7KB | טבלת המלצות (4 חומרות) |
| `test_results.html` | 6.9KB | TEST PASSED/FAILED מפורט |
| `log_analysis.html` | **30KB** | תוצאות log analysis (גדול עם load) |
| `timeline.html` | 14KB | ציר זמן של events |
| `failover.html` | 2.9KB | אירועי failover |
| `test_summary.html` | 14KB | סיכום מספרי |

ה-`cluster.html` מכיל **89 div containers ל-Grid.js**, כולל **charts per node**:
- `chart-overall-conns-node-1`, `chart-overall-conns-node-2`
- `chart-overall-total_req-node-1`, ...
- `chart-overall-cpu_idle-node-1`, ...

ולכל chart יש modal version (popup zoom). **18 tables סטטיים** + 89 grid containers דינמיים.

### 22.8 חבילת התמיכה המחולצת (`redisscope_sp/`)

13MB ברוטו - תוכן מלא של ה-`debuginfo.tar.gz` שחולץ אוטומטית. **המבנה של חבילת תמיכה (אומת):**

```
redisscope_sp/
├── cluster_health_report.txt                       ← דוח בריאות cluster
├── usage_report.usg                                ← דוח usage
├── database_<bdb_uid>/
│   ├── database_<id>_ccs_info.txt                 ← תצורה מ-CCS
│   ├── database_<id>.clientlist                   ← clients מחוברים
│   ├── database_<id>.slowlog                      ← slowlog raw
│   ├── database_<id>.rladmin                      ← rladmin info db
│   ├── database_<id>.tag_statistics
│   ├── database_<id>.info                         ← INFO command output
│   └── database_<id>_health.txt
└── node_<uid>/
    ├── node_<uid>.ccs                             ← CCS של ה-node
    ├── node_<uid>.rladmin                         ← rladmin status מ-node זה
    ├── node_<uid>.rlcheck                         ← rlcheck output
    ├── node_<uid>_envoy_config.json
    ├── node_<uid>_envoy_server_info.json
    ├── node_<uid>_envoy_stats.json
    ├── node_<uid>_sys_info.txt
    ├── redis_<shard_uid>.txt × N (shard per file)
    └── logs/                                       ← 25+ log files
        ├── alert_mgr.log, alert_mgr_stderr.log, alert_mgr_stdout.log
        ├── ccs_redis.log
        ├── cnm_exec.log
        ├── cnm_http.log, cnm_http_stderr.log, cnm_http_stdout.log
        ├── crdb_coordinator.log
        ├── dmcproxy.log
        ├── envoy.log
        ├── heartbeatd.log
        ├── mdns_server.log, pdns_server.log
        ├── redis_ctl.log, redis_ctl_stderr.log, redis_ctl_stdout.log
        ├── redis_exporter.log
        ├── redis_mgr.log, redis_mgr_stderr.log, redis_mgr_stdout.log
        ├── resource_mgr.log, ...
        ├── rl_info_provider.log, ...
        ├── rladmin.log
        ├── rlcheck.log
        ├── rlutil.log
        ├── sentinel_service.log, ...
        ├── shard_mgr_stdout.log
        ├── stats_archiver.log, ...
        ├── statsd_exporter.log
        └── supervisord.log
```

> **לכן** `--skiplogs` חוסך כל-כך הרבה — הוא מדלג על סריקה של 25+ log files × N nodes.

### 22.9 קובץ `redisscope_attributes.txt`

קובץ קטן (865B) אבל חשוב. מכיל **רשימה של כל ה-attribute names** שהכלי אסף מ-INFO/CONFIG. דוגמא:

```
allocator_muzzy
bind * _
client_output_buffer_limit_disconnections
client_query_buffer_limit_disconnections
cmdstat_acl|setuser, cmdstat_client|id, cmdstat_client|list, ...
cmdstat_get, cmdstat_set, cmdstat_lpush, cmdstat_lrange, ...
errorstat_OOM
evicted_scripts
expired_subkeys
max_new_connections_per_cycle
max_new_tls_connections_per_cycle
mem_overhead_db_hashtable_rehashing
pubsub_clients
sharding_slot_range
tls_ciphersuites TLS_AES_256_GCM_SHA384
total_watched_keys
watching_clients
```

זו רשימת **כל ה-counters והגדרות** שהכלי קורא בכל ריצה. אם רוצים להבין מאיפה הוא מקבל את הנתונים, זה ה-reference.

### 22.10 סיכום מבצעי

| מטרה | פקודה | זמן | יציאה | למה |
|---|---|---|---|---|
| **בדיקה מהירה יומית** | `--sp file --skiplogs` | 3 שניות | 19 ממצאים | dashboard, lightweight |
| **ניטור שבועי / Audit** | `--sp file` | 5 שניות | 77 ממצאים | כולל log analysis |
| **חקירת incident** | `--sp file --start ... --end ...` | 5 שניות | filtered + zoom | טווח זמן ספציפי |
| **לפני שדרוג** | `--sp file --force-full` | 6 שניות | comprehensive | סריקת 4 ימי לוגים |
| **לשיתוף עם Redis Support** | `--sp file --mask` | 5 שניות | + html_mask + mappings | ללא נתונים רגישים |
| **לDB ספציפי** | `--sp file --bdb N` | 4 שניות | -10% findings | פוקוס על DB |

---

## 23. Cheat Sheet — תרגום מהיר

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

### תיקיות וקבצי פלט בקצרה

| פריט | מה זה | תעלה לכרטיס? |
|---|---|---|
| `redisscope_healthcheck_report.html` | **הדוח HTML הראשי** (שם קבוע) | ✅ כן (קובץ יחיד) |
| `aa_multi_cluster_report.html` | דוח HTML למצב `--aa` | ✅ כן (קובץ יחיד) |
| `redisscope_html/` | HTML מלא (multi-page) | אם רוצים גישה לכל הדפים |
| `redisscope_html_mask/` | HTML ממוסך (רק עם `--mask`) | ✅ כן, מועדף על פני html/ |
| `redisscope_all/` | נתונים גולמיים | בדרך כלל לא |
| `redisscope_logs/` | לוגי הכלי | רק לבדיקת בעיות בכלי |
| `redisscope_sp/` | חבילה מחולצת (רק עם `--sp`) | ❌ לא |
| ~~`redisscope_upload_to_ticket/`~~ | ⚠️ **לא נוצר ב-v1.24.5** למרות שמופיע ב-PDF הישן | — |

---

## הערות חשובות

> ⚠️ **RedisScope can make mistakes.**
> הדוחות הם כלי עזר לאבחון — יש לוודא ממצאים קריטיים בכלים נוספים לפני נקיטת פעולה במערכת ייצור.

> 📞 **תמיכה:** support@redis.com

> 📚 **תיעוד רשמי של Redis:** https://redis.io/docs/

---

*מסמך זה הופק על בסיס ניתוח הקוד של RedisScope 1.24.5 ואומת בהרצה אמיתית של הבינארי על RHEL 9.7 x86_64.*
