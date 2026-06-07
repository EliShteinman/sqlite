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
DataTables 1.13.6 + Buttons 2.4.2, Plotly 2.27.0, Font Awesome 6.4.0, JSZip 3.10.1,
ולוגו Red Hat.

> אם בעתיד RedisScope יעבור לגרסת ספרייה חדשה, יש להוסיף את ה-URL לכלי הבנייה
> ולבנות מחדש (ראה תיקיית המקור `redisscope_offline_fixer/`).

## התנהגות בטוחה

- **In-place**: מעדכן את הקבצים במקום. הרצה חוזרת אינה משנה דבר (idempotent).
- **עמיד לתקלות**: קובץ לא קריא בודד מדולג עם אזהרה, בלי להפיל את כל הריצה.
- **לא נוגע בקישורים**: רק `<link>`/`<script>`/`<img>` של ספריות; קישורי `<a href>` נשמרים.
