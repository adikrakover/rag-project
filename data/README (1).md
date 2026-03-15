# קטלוג שירים אישי

## תכונות
הוספה וניהול שירים - שם, זמר, קישור, מצב רוח, אהובים
תאריכים בלוח העברי באמצעות Intl.DateTimeFormat
סינון וחיפוש לפי זמר, מצב רוח, אהובים, חודש עברי, חיפוש חופשי
עריכה מוטמעת ללא טעינה מחדש
אחסון מקומי ב-localStorage
חוצה פלטפורמות Windows ו-macOS באמצעות electron-builder

## טכנולוגיות
Electron 28
Vanilla HTML CSS JavaScript
Intl.DateTimeFormat עם he-IL-u-ca-hebrew
localStorage
electron-builder 24

## התקנה
npm install
npm start

## בנייה להפצה
npm run dist

## מבנה הפרויקט
main.js, index.html, script.js, style.css, package.json

## סכמת הנתונים
מפתח: personalSongCatalog
שדות: id, title, artist, isFavorite, dateAdded, url, mood
מצבי רוח: כללי, שמח, רגוע, מרגש, נוסטלגי, עצוב