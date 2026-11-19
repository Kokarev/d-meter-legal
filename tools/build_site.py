"""Builds the static d-meter-legal pages (EN/UK).

Usage: python3 tools/build_site.py OUT_DIR YYYY-MM-DD

The date is the "Last updated" date of the documents: the actual publication
date.
"""
import datetime
import pathlib
import sys

OUT = pathlib.Path(sys.argv[1])
_DATE = datetime.date.fromisoformat(sys.argv[2])
_UK_MONTHS = ("січня", "лютого", "березня", "квітня", "травня", "червня",
              "липня", "серпня", "вересня", "жовтня", "листопада", "грудня")
UPDATED = {
    "en": f"{_DATE.day} {_DATE.strftime('%B')} {_DATE.year}",
    "uk": f"{_DATE.day} {_UK_MONTHS[_DATE.month - 1]} {_DATE.year}",
}
EMAIL = "almasoft.team@gmail.com"
DEV = "Pavlo Kokaryev"

APPLE_EULA = "https://www.apple.com/legal/internet-services/itunes/dev/stdeula/"
APPLE_PRIVACY = "https://www.apple.com/legal/privacy/"
APPLE_SUBS = "https://support.apple.com/118428"
APPLE_REFUND = "https://reportaproblem.apple.com/"
GOOGLE_PLAY_TOS = "https://play.google.com/about/play-terms/"
GOOGLE_PRIVACY = "https://policies.google.com/privacy"
GOOGLE_REFUND = "https://support.google.com/googleplay/answer/2479637"
GITHUB_PRIVACY = (
    "https://docs.github.com/site-policy/privacy-policies/github-general-privacy-statement"
)

UI = {
    "en": {
        "privacy": "Privacy Policy",
        "terms": "Terms of Use",
        "support": "Support",
        "updated": "Last updated",
        "other": ("uk", "Українська"),
        "home": "Legal information and support for the D-METER app",
    },
    "uk": {
        "privacy": "Політика конфіденційності",
        "terms": "Умови використання",
        "support": "Підтримка",
        "updated": "Оновлено",
        "other": ("en", "English"),
        "home": "Правова інформація та підтримка застосунку D-METER",
    },
}


def a(href, text=None):
    return f'<a href="{href}">{text or href}</a>'


MAIL = f'<a href="mailto:{EMAIL}">{EMAIL}</a>'

DOCS = {
    ("en", "privacy"): f"""
<p>D-METER (“the app”) is a fuel density calculator for iOS and Android developed by
{DEV} (“we”, “us”). This policy describes what information the app handles
and how.</p>

<h2>Summary</h2>
<ul>
<li>We do not collect personal data through the app.</li>
<li>The app has no account or sign-in.</li>
<li>The app contains no advertising, analytics, tracking or third-party
crash-reporting software.</li>
<li>The app does not send your data to us or to any third-party server.
On iOS it communicates only with Apple’s App Store, through Apple’s StoreKit,
for the subscription. On Android it does not connect to the internet.</li>
</ul>

<h2>Information stored on your device</h2>
<p>The app keeps a few settings on your device so that it opens the way you
left it: the interface language, the theme, whether the Blending demo button
is shown, and whether the introductory tutorial has been completed. These
settings stay on your device, are not sent to us, and are removed when you
delete the app.</p>
<p>Values you enter for calculations are processed on your device. The app
does not save them after it is closed.</p>

<h2>Purchases and subscriptions</h2>
<p>D-METER PRO Monthly is an auto-renewable subscription sold through the
Apple App Store. Payments are processed by Apple. We do not receive or store
your payment card details, Apple ID or billing address.</p>
<p>To decide whether PRO features are available, the app asks Apple’s
StoreKit framework on your device for the status of your subscription. The
transaction information StoreKit returns is used on the device only for this
purpose, is kept in memory only, and is not sent to us.</p>
<p>Apple provides developers with sales and subscription reports in App Store
Connect. Apple’s handling of your purchase information is described in the
{a(APPLE_PRIVACY, "Apple Privacy Policy")}.</p>

<h2>Google Play purchase (Android)</h2>
<p>On Android, D-METER is a paid app sold through Google Play. All features
are included in the purchase; there are no in-app purchases or
subscriptions. Payments are processed by Google. We do not receive or store
your payment card details, Google account or billing address, and the app
does not check your purchase with any server.</p>
<p>Google provides developers with order reports in the Google Play Console.
Google’s handling of your information is described in the
{a(GOOGLE_PRIVACY, "Google Privacy Policy")}.</p>

<h2>Diagnostics provided by Apple and Google</h2>
<p>If you choose to share analytics with app developers in your device
settings, Apple may provide us with crash reports and aggregated usage
statistics. You control this in iOS Settings → Privacy &amp; Security →
Analytics &amp; Improvements. Such data is provided by Apple under the Apple
Privacy Policy.</p>
<p>On Android, if you have chosen to share usage and diagnostics data with
Google, Google Play may provide us with crash reports and aggregated
statistics about the app. You control this in your Android device settings.
Such data is provided by Google under the Google Privacy Policy.</p>

<h2>Web pages opened from the app</h2>
<p>The app opens this policy, the Terms of Use and the Support page in your
web browser. These pages are hosted on GitHub Pages. When you visit them,
GitHub may process technical information such as your IP address, as
described in the {a(GITHUB_PRIVACY, "GitHub General Privacy Statement")}. The
iOS app also opens Apple’s subscription management, which is governed by Apple.</p>

<h2>Contacting us</h2>
<p>If you email us, we receive your email address and the content of your
message. We use them only to reply to you and do not share them with anyone.
You can send a request to delete your personal data to the address below. We
consider such requests and delete data in accordance with applicable law and
any retention obligations that apply to us.</p>

<h2>Your choices</h2>
<p>Because the app does not collect personal data, we hold no data about you
from the app. You can remove all settings stored by the app by deleting it
from your device. For anything about email correspondence, contact us.</p>

<h2>Changes to this policy</h2>
<p>If this policy changes, we will publish the new version on this page and
update the date above.</p>

<h2>Contact</h2>
<p>{DEV}<br>{MAIL}</p>
""",
    ("uk", "privacy"): f"""
<p>D-METER («застосунок») — калькулятор густини пального для iOS та Android, який
розробив {DEV} («ми»). Ця політика описує, яку інформацію обробляє
застосунок і як саме.</p>

<h2>Коротко</h2>
<ul>
<li>Ми не збираємо персональні дані через застосунок.</li>
<li>У застосунку немає облікового запису чи входу.</li>
<li>Застосунок не містить реклами, аналітики, відстеження чи сторонніх
засобів збору звітів про збої.</li>
<li>Застосунок не надсилає ваші дані ні нам, ні на сторонні сервери. Він
на iOS звертається лише до Apple App Store через Apple StoreKit — для
підписки. На Android застосунок не підключається до інтернету.</li>
</ul>

<h2>Інформація, що зберігається на пристрої</h2>
<p>Застосунок зберігає на вашому пристрої кілька налаштувань, щоб
відкриватися так, як ви його залишили: мову інтерфейсу, тему, показ кнопки
демонстрації змішування та те, чи пройдено вступний посібник. Ці
налаштування залишаються на пристрої, не надсилаються нам і видаляються
разом із застосунком.</p>
<p>Значення, які ви вводите для розрахунків, обробляються на пристрої.
Застосунок не зберігає їх після закриття.</p>

<h2>Покупки та підписка</h2>
<p>D-METER PRO Monthly — підписка з автоматичним поновленням, що продається
через Apple App Store. Платежі обробляє Apple. Ми не отримуємо і не
зберігаємо дані вашої платіжної картки, Apple ID чи платіжну адресу.</p>
<p>Щоб визначити, чи доступні функції PRO, застосунок запитує стан вашої
підписки у фреймворку Apple StoreKit на пристрої. Інформація про
транзакції, яку повертає StoreKit, використовується на пристрої лише для
цього, зберігається тільки в оперативній пам’яті й не надсилається нам.</p>
<p>Apple надає розробникам звіти про продажі та підписки в App Store
Connect. Як Apple обробляє інформацію про ваші покупки, описано в
{a(APPLE_PRIVACY, "Політиці конфіденційності Apple")}.</p>

<h2>Покупка в Google Play (Android)</h2>
<p>На Android D-METER — платний застосунок, що продається через Google
Play. Усі функції входять у покупку; вбудованих покупок і підписок немає.
Платежі обробляє Google. Ми не отримуємо і не зберігаємо дані вашої
платіжної картки, облікового запису Google чи платіжну адресу, а застосунок
не перевіряє покупку на жодному сервері.</p>
<p>Google надає розробникам звіти про замовлення в Google Play Console. Як
Google обробляє вашу інформацію, описано в
{a(GOOGLE_PRIVACY, "Політиці конфіденційності Google")}.</p>

<h2>Діагностика від Apple і Google</h2>
<p>Якщо ви в налаштуваннях пристрою погодилися ділитися аналітикою з
розробниками, Apple може надавати нам звіти про збої та узагальнену
статистику використання. Це налаштовується в Параметри iOS → Приватність і
безпека → Аналітика й покращення. Такі дані Apple надає відповідно до своєї
Політики конфіденційності.</p>
<p>На Android, якщо ви погодилися ділитися з Google даними про використання
та діагностику, Google Play може надавати нам звіти про збої та узагальнену
статистику щодо застосунку. Це налаштовується в параметрах пристрою Android.
Такі дані Google надає відповідно до Політики конфіденційності Google.</p>

<h2>Вебсторінки, що відкриваються із застосунку</h2>
<p>Застосунок відкриває цю політику, Умови використання та сторінку
підтримки у вашому браузері. Ці сторінки розміщено на GitHub Pages. Коли ви
їх відвідуєте, GitHub може обробляти технічну інформацію, як-от вашу
IP-адресу, відповідно до {a(GITHUB_PRIVACY, "GitHub General Privacy Statement")}.
Застосунок для iOS також відкриває керування підписками Apple, на яке поширюються
правила Apple.</p>

<h2>Звернення до нас</h2>
<p>Якщо ви пишете нам листа, ми отримуємо вашу електронну адресу та зміст
повідомлення. Ми використовуємо їх лише для відповіді вам і нікому не
передаємо. Запит на видалення ваших персональних даних можна надіслати на
адресу, зазначену нижче. Ми розглядаємо такі запити й видаляємо дані
відповідно до чинного законодавства та обов’язкових для нас вимог щодо
зберігання.</p>

<h2>Ваш вибір</h2>
<p>Оскільки застосунок не збирає персональних даних, ми не маємо даних про
вас із застосунку. Усі налаштування, збережені застосунком, можна видалити,
видаливши його з пристрою. З питань щодо листування звертайтеся до нас.</p>

<h2>Зміни політики</h2>
<p>У разі змін ми опублікуємо нову версію на цій сторінці й оновимо дату
вгорі.</p>

<h2>Контакти</h2>
<p>{DEV}<br>{MAIL}</p>
""",
    ("en", "terms"): f"""
<p>These terms apply to the D-METER app for iOS and Android developed by {DEV} (“we”,
“us”).</p>

<h2>1. Licence</h2>
<p>On iOS, your use of D-METER is governed by Apple’s
{a(APPLE_EULA, "Licensed Application End User License Agreement (Standard EULA)")}.
These terms add information about the PRO subscription and the use of
calculation results. If these terms conflict with the applicable Standard
EULA, the Standard EULA prevails.</p>
<p>On Android, D-METER is distributed through Google Play, and your use of it
is also subject to the {a(GOOGLE_PLAY_TOS, "Google Play Terms of Service")}.</p>

<h2>2. Free features (iOS)</h2>
<p>On iOS, the base density calculator, including AIR details, is available without
a subscription.</p>

<h2>3. D-METER PRO Monthly subscription (iOS)</h2>
<p>D-METER PRO Monthly unlocks the Density Chart (virtual hydrometer),
Blending and Density Escalation.</p>
<ul>
<li>It is an auto-renewable monthly subscription purchased with your Apple
ID.</li>
<li>The price, currency and whether a free trial is available to you are
determined by Apple StoreKit and shown in the app before you confirm the
purchase.</li>
<li>Payment is charged to your Apple ID account when you confirm the
purchase, or at the end of the free trial if one applies.</li>
<li>The subscription renews automatically unless it is cancelled at least 24
hours before the end of the current period. Your account is charged for
renewal within 24 hours before the end of the current period.</li>
<li>You can manage or cancel the subscription in your Apple ID account
settings, or with “Manage subscription” in the app. See
{a(APPLE_SUBS, "how to cancel a subscription from Apple")}.</li>
<li>Use “Restore purchases” in the app to restore an existing subscription,
for example after reinstalling the app or on another device with the same
Apple ID.</li>
<li>Payments and refunds are handled by Apple. You can request a refund at
{a(APPLE_REFUND)}.</li>
</ul>

<h2>4. Paid app on Google Play (Android)</h2>
<ul>
<li>On Android, D-METER is a paid app. The price shown in Google Play is a
one-time purchase that includes all features, including the Density Chart
(virtual hydrometer), Blending and Density Escalation.</li>
<li>There are no in-app purchases or subscriptions in the Android app.</li>
<li>The app is available on your Android devices signed in with the Google
account used for the purchase.</li>
<li>Payments and refunds are handled by Google Play under its refund
policies. See {a(GOOGLE_REFUND, "Google Play refund help")}.</li>
</ul>

<h2>5. Calculation results</h2>
<p>D-METER provides calculations for reference. Results depend on the values
you enter and on the methods implemented in the app. They are not a
certified measurement and do not replace laboratory analysis, calibrated
instruments or official and contractual documents. Results are provided for
information only: you decide whether they are suitable for your particular
use, and should check them before relying on them for commercial, safety or
legal decisions. Nothing in these terms limits any rights or remedies that
cannot be limited under applicable law.</p>

<h2>6. Changes</h2>
<p>We may update the app and these terms. The current version is always
published on this page with its date.</p>

<h2>7. Contact</h2>
<p>{DEV}<br>{MAIL}</p>
""",
    ("uk", "terms"): f"""
<p>Ці умови стосуються застосунку D-METER для iOS та Android, який розробив {DEV}
(«ми»).</p>

<h2>1. Ліцензія</h2>
<p>На iOS використання D-METER регулюється
{a(APPLE_EULA, "Ліцензійною угодою Apple з кінцевим користувачем (Standard EULA)")}.
Ці умови додають інформацію про підписку PRO та використання результатів
розрахунків. У разі суперечності цих умов із застосовною Standard EULA
переважає Standard EULA.</p>
<p>На Android D-METER поширюється через Google Play, і його використання
також регулюється {a(GOOGLE_PLAY_TOS, "Умовами використання Google Play")}.</p>

<h2>2. Безкоштовні функції (iOS)</h2>
<p>На iOS базовий калькулятор густини, зокрема деталі AIR, доступний без
підписки.</p>

<h2>3. Підписка D-METER PRO Monthly (iOS)</h2>
<p>D-METER PRO Monthly відкриває графік густини (віртуальний ареометр),
змішування та коригування за густиною.</p>
<ul>
<li>Це щомісячна підписка з автоматичним поновленням, яку оформлюють через
ваш Apple ID.</li>
<li>Ціну, валюту та доступність безкоштовного пробного періоду для вас
визначає Apple StoreKit; вони показуються в застосунку до підтвердження
покупки.</li>
<li>Оплата списується з рахунку Apple ID під час підтвердження покупки або
після завершення пробного періоду, якщо він діє.</li>
<li>Підписка поновлюється автоматично, якщо її не скасовано щонайменше за 24
години до кінця поточного періоду. Плата за поновлення списується протягом
24 годин до кінця поточного періоду.</li>
<li>Керувати підпискою чи скасувати її можна в налаштуваннях облікового
запису Apple ID або кнопкою «Керувати підпискою» в застосунку. Див.
{a(APPLE_SUBS, "інструкцію Apple зі скасування підписки")}.</li>
<li>Щоб відновити наявну підписку, наприклад після перевстановлення
застосунку або на іншому пристрої з тим самим Apple ID, скористайтеся
«Відновити покупки» в застосунку.</li>
<li>Платежі й повернення коштів здійснює Apple. Запит на повернення можна
подати на {a(APPLE_REFUND)}.</li>
</ul>

<h2>4. Платний застосунок у Google Play (Android)</h2>
<ul>
<li>На Android D-METER — платний застосунок. Ціна, показана в Google Play, —
це разова покупка, що включає всі функції, зокрема графік густини
(віртуальний ареометр), змішування та коригування за густиною.</li>
<li>У застосунку для Android немає вбудованих покупок і підписок.</li>
<li>Застосунок доступний на ваших пристроях Android, де виконано вхід в
обліковий запис Google, з якого здійснено покупку.</li>
<li>Платежі й повернення коштів здійснює Google Play відповідно до своїх
правил повернення. Див. {a(GOOGLE_REFUND, "довідку Google Play щодо повернення коштів")}.</li>
</ul>

<h2>5. Результати розрахунків</h2>
<p>D-METER надає розрахунки довідкового характеру. Результати залежать від
введених значень і методів, реалізованих у застосунку. Вони не є
сертифікованим вимірюванням і не замінюють лабораторного аналізу,
повірених приладів, офіційних чи договірних документів. Результати надаються
лише для інформації: ви самостійно визначаєте, чи придатні вони для вашого
конкретного застосування, і маєте перевірити їх, перш ніж спиратися на них
у комерційних, безпекових чи юридичних рішеннях. Ніщо в цих умовах не
обмежує прав чи засобів правового захисту, які не можуть бути обмежені
чинним законодавством.</p>

<h2>6. Зміни</h2>
<p>Ми можемо оновлювати застосунок і ці умови. Чинна версія завжди
публікується на цій сторінці з датою.</p>

<h2>7. Контакти</h2>
<p>{DEV}<br>{MAIL}</p>
""",
    ("en", "support"): f"""
<p>Questions, problems or suggestions about D-METER: write to {MAIL}.</p>
<p>To help us answer quickly, please include your device model, iOS or Android version,
the app version (Settings → APP → Version in D-METER), what you did and what
happened, and a screenshot if possible.</p>

<h2>Subscription (iOS)</h2>
<dl>
<dt>What does PRO include?</dt>
<dd>The Density Chart (virtual hydrometer), Blending and Density Escalation. The base
calculator, including AIR details, is free.</dd>
<dt>How much does it cost? Is there a free trial?</dt>
<dd>The price and the availability of a free trial are determined by Apple
StoreKit for your account and region, and are shown on the subscription
screen before you confirm.</dd>
<dt>I already subscribed, but PRO is locked.</dt>
<dd>Open D-METER PRO from the app menu and tap “Restore purchases”. Make sure you
are signed in with the Apple ID that was used for the purchase.</dd>
<dt>How do I cancel?</dt>
<dd>Tap “Manage subscription” in the app, or follow
{a(APPLE_SUBS, "Apple’s instructions")}. Cancel at least 24 hours before the
end of the current period to avoid renewal.</dd>
<dt>How do I get a refund?</dt>
<dd>Payments are processed by Apple, so refunds are requested from Apple at
{a(APPLE_REFUND)}.</dd>
</dl>

<h2>Android (Google Play)</h2>
<dl>
<dt>Is there a subscription on Android?</dt>
<dd>No. On Google Play, D-METER is a paid app: the purchase includes all
features, with no in-app purchases or subscriptions.</dd>
<dt>How do I get a refund?</dt>
<dd>Purchases on Google Play are refunded by Google. See
{a(GOOGLE_REFUND, "Google Play refund help")}.</dd>
</dl>

<h2>Documents</h2>
<ul>
<li>{a("../privacy/", "Privacy Policy")}</li>
<li>{a("../terms/", "Terms of Use")}</li>
</ul>

<h2>Developer</h2>
<p>{DEV}<br>{MAIL}</p>
""",
    ("uk", "support"): f"""
<p>Запитання, проблеми чи пропозиції щодо D-METER: пишіть на {MAIL}.</p>
<p>Щоб ми могли швидше відповісти, вкажіть модель пристрою, версію iOS чи Android, версію
застосунку (Налаштування → APP → Version у D-METER), що ви робили і що
сталося, та, за можливості, додайте знімок екрана.</p>

<h2>Підписка (iOS)</h2>
<dl>
<dt>Що входить у PRO?</dt>
<dd>Графік густини (віртуальний ареометр), змішування та коригування за густиною. Базовий
калькулятор, зокрема деталі AIR, безкоштовний.</dd>
<dt>Скільки це коштує? Чи є пробний період?</dt>
<dd>Ціну та доступність безкоштовного пробного періоду для вашого облікового
запису й регіону визначає Apple StoreKit; їх показано на екрані підписки до
підтвердження.</dd>
<dt>Підписку вже оформлено, але PRO закрито.</dt>
<dd>Відкрийте D-METER PRO з меню застосунку й натисніть «Відновити покупки». Переконайтеся,
що ви ввійшли з тим Apple ID, через який здійснено покупку.</dd>
<dt>Як скасувати?</dt>
<dd>Натисніть «Керувати підпискою» в застосунку або скористайтеся
{a(APPLE_SUBS, "інструкцією Apple")}. Щоб підписка не поновилася, скасуйте
її щонайменше за 24 години до кінця поточного періоду.</dd>
<dt>Як повернути кошти?</dt>
<dd>Платежі обробляє Apple, тому запит на повернення подається в Apple на
{a(APPLE_REFUND)}.</dd>
</dl>

<h2>Android (Google Play)</h2>
<dl>
<dt>Чи є підписка на Android?</dt>
<dd>Ні. У Google Play D-METER — платний застосунок: покупка включає всі
функції, без вбудованих покупок і підписок.</dd>
<dt>Як повернути кошти?</dt>
<dd>Покупки в Google Play повертає Google. Див.
{a(GOOGLE_REFUND, "довідку Google Play щодо повернення коштів")}.</dd>
</dl>

<h2>Документи</h2>
<ul>
<li>{a("../privacy/", "Політика конфіденційності")}</li>
<li>{a("../terms/", "Умови використання")}</li>
</ul>

<h2>Розробник</h2>
<p>{DEV}<br>{MAIL}</p>
""",
}


def page(lang, title, body, depth, nav_lang_href, current=None):
    ui = UI[lang]
    up = "../" * depth
    other_lang, other_label = ui["other"]
    nav = " ".join(
        f'<a href="{up}{lang}/{d}/"'
        + (' aria-current="page"' if d == current else "")
        + f">{ui[d]}</a>"
        for d in ("privacy", "terms", "support")
    )
    updated = (
        f'<p class="meta">{ui["updated"]}: {UPDATED[lang]}</p>' if current else ""
    )
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<meta name="referrer" content="no-referrer">
<title>{title}</title>
<link rel="stylesheet" href="{up}assets/style.css">
</head>
<body>
<header>
<a class="brand" href="{up}{lang}/">D-METER</a>
<a class="lang" href="{nav_lang_href}" hreflang="{other_lang}" lang="{other_lang}">{other_label}</a>
</header>
<main>
<h1>{title}</h1>
{updated}
{body.strip()}
</main>
<footer>
<nav>{nav}</nav>
<p>© 2026 {DEV} · <a href="mailto:{EMAIL}">{EMAIL}</a></p>
</footer>
</body>
</html>
"""


def write(rel, text):
    path = OUT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


for lang in ("en", "uk"):
    ui = UI[lang]
    other = ui["other"][0]
    for doc in ("privacy", "terms", "support"):
        title = f"D-METER — {ui[doc]}"
        write(
            f"{lang}/{doc}/index.html",
            page(lang, title, DOCS[(lang, doc)], 2, f"../../{other}/{doc}/", doc),
        )
    links = "\n".join(
        f'<li><a href="{d}/">{ui[d]}</a></li>' for d in ("privacy", "terms", "support")
    )
    write(
        f"{lang}/index.html",
        page(lang, "D-METER", f"<p>{ui['home']}.</p>\n<ul>\n{links}\n</ul>", 1, f"../{other}/"),
    )

root_body = """<p>Legal information and support · Правова інформація та підтримка</p>
<ul>
<li><a href="en/">English</a></li>
<li><a href="uk/" lang="uk">Українська</a></li>
</ul>"""
write("index.html", page("en", "D-METER", root_body, 0, "uk/"))
write(
    "404.html",
    page(
        "en",
        "Page not found",
        '<p>This page does not exist. · Сторінку не знайдено.</p>\n'
        '<p><a href="/d-meter-legal/">D-METER</a></p>',
        0,
        "/d-meter-legal/uk/",
    ).replace('href="assets/', 'href="/d-meter-legal/assets/')
    .replace('href="en/', 'href="/d-meter-legal/en/'),
)
