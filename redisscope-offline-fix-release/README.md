# RedisScope Offline Report Fixer

הופך דוחות HTML של RedisScope לעצמאיים, כך שייפתחו ויוצגו כראוי על מכונות
**ללא גישה לאינטרנט** (air-gapped).

## הבעיה שזה פותר

דוחות RedisScope טוענים את ספריות התצוגה (Bootstrap, jQuery, DataTables,
Plotly, Font Awesome, Bootstrap Icons ולוגו) מרשת ה-CDN הציבורית. על שרת מבודד
ההורדות נכשלות, והדוח נראה שבור — בלי עיצוב, בלי אייקונים, וטבלאות שלא עובדות.

הכלי עובר על כל קובץ HTML ומחליף כל קישור CDN בתוכן האמיתי של הספרייה (JS/CSS
מוטמעים, פונטים ותמונות כ-base64). התוצאה: דוחות עצמאיים לחלוטין. קישורי תיעוד
(redis.io, github.com) נשמרים כפי שהם.

---

## התקנה (חד-פעמית, על השרת)

```bash
chmod +x redisscope-offline-fix
sudo mv redisscope-offline-fix /usr/local/bin/
```

> הבינארי הוא x86_64 ל-Linux/RHEL9 — בדיוק כמו redisscope עצמו. אין צורך ב-Python
> ובאף תלות. הכל ארוז בתוכו.

## בדיקת הגרסה המותקנת

```bash
redisscope-offline-fix --version
```

## עדכון לגרסה חדשה

הכלי הוא קובץ בודד ללא הגדרות או state, ולכן עדכון = החלפת הקובץ:

```bash
# 1. ודא איזו גרסה מותקנת כעת
redisscope-offline-fix --version

# 2. החלף את הבינארי הישן בחדש (דורס את הקובץ הקיים)
chmod +x redisscope-offline-fix
sudo mv -f redisscope-offline-fix /usr/local/bin/redisscope-offline-fix

# 3. ודא שהעדכון נקלט
redisscope-offline-fix --version   # אמור להציג 1.1.0
```

> **חשוב — דוחות שכבר תוקנו בגרסה הישנה:** הגרסה הישנה (1.0.0) לא הכירה את
> vis-network, ולכן בדוחות עם טופולוגיית רשת היא השאירה את הקישור הזה כפי שהוא.
> פשוט הרץ את הגרסה החדשה שוב על אותם דוחות — הכלי idempotent ויטמיע רק את מה
> שנותר חיצוני (כולל vis-network), בלי לפגוע במה שכבר תוקן:
>
> ```bash
> redisscope-offline-fix /path/to/redisscope_html
> ```

## שימוש

```bash
# תיקון כל הדוחות בתיקייה (כולל תת-תיקיות)
redisscope-offline-fix /path/to/redisscope_html

# או מתוך התיקייה עצמה
cd redisscope_html && redisscope-offline-fix
```

זרימת עבודה טיפוסית:

```bash
./redisscope --sp support_package.tar.gz   # מייצר את הדוח (redisscope_html/)
redisscope-offline-fix redisscope_html      # הופך אותו לעצמאי
```

לאחר מכן אפשר להעביר את `redisscope_html/` לכל מקום והוא ייפתח אופליין.

## אפשרויות

| דגל | תיאור |
|-----|-------|
| `--dry-run` | מראה מה ישתנה בלי לכתוב |
| `--backup`  | שומר עותק `.bak` לכל קובץ |
| `--verbose` | לוג מפורט (debug) |
| `--quiet`   | רק אזהרות ושגיאות |
| `--strict`  | מחזיר קוד שגיאה אם נכס כלשהו לא נמצא בחבילה |

## אימות תקינות (אופציונלי)

```bash
shasum -a 256 -c <(echo "$(cat redisscope-offline-fix.sha256)  redisscope-offline-fix")
```

---

## מה מוטמע

הבינארי אורז בתוכו את הספריות הבאות (כולל הפונטים):
Bootstrap 5.3.0, Bootstrap Icons (1.10.0 / 1.10.5 / 1.11.0), jQuery 3.7.0,
DataTables 1.13.6 + Buttons 2.4.2, Plotly 2.27.0, vis-network 9.1.2 (טופולוגיית רשת),
Font Awesome 6.4.0, JSZip 3.10.1, ולוגו Red Hat.

> הערה: RedisScope מקשר ל-CSS של vis-network בנתיב שמחזיר 404 (ב-vis-network 9
> הסגנונות ארוזים בתוך ה-JS). הכלי מתקן זאת — הוא מטמיע CSS תקין מנתיב עובד.

> אם בעתיד RedisScope יעבור לגרסת ספרייה חדשה, יש להוסיף את ה-URL לכלי הבנייה
> ולבנות מחדש (ראה תיקיית המקור `redisscope_offline_fixer/`).

## התנהגות בטוחה

- **In-place**: מעדכן את הקבצים במקום. הרצה חוזרת אינה משנה דבר (idempotent).
- **עמיד לתקלות**: קובץ לא קריא בודד מדולג עם אזהרה, בלי להפיל את כל הריצה.
- **לא נוגע בקישורים**: רק `<link>`/`<script>`/`<img>` של ספריות; קישורי `<a href>` נשמרים.
