#!/usr/bin/env python3
"""Builds the D-METER website (V3) into this repository.

    python3 -I tools/build_web.py

Writes index.html, 404.html, sitemap.xml and the en/ and uk/
pages: home, features/, examples/, download/, privacy/, terms/, support/.

The legal documents are NOT authored here. tools/build_site.py (the source of
the Privacy Policy, Terms of Use and Support texts) is run into a temporary
directory with LEGAL_DATE, and the <main> of each document is inserted byte
for byte. Only the page chrome around it is new. tools/check_web.py compares
those blocks with the published pages.

The pages load nothing from other sites: no fonts, scripts, styles or images
from a CDN, no analytics. Links to Apple and the e-mail address are plain links.
"""
import json
import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
LANGS = ("en", "uk")
OTHER = {"en": "uk", "uk": "en"}
BASE_URL = "https://kokarev.github.io/d-meter-legal/"
LEGAL_DATE = "2026-10-29"  # "Last updated" date of the published legal texts
EMAIL = "almasoft.team@gmail.com"
DEV = "Pavlo Kokaryev"
DOCS = ("privacy", "terms", "support")
IMG = "assets/img/app/"

T = {
    "en": {
        "lang_name": "English",
        "skip": "Skip to content",
        "subtitle": "Cargo Calculator",
        "nav_aria": "Main",
        "nav_home": "Home",
        "nav_features": "Features",
        "nav_examples": "Examples",
        "nav_download": "Download",
        "nav_support": "Support",
        "menu": "Menu",
        "theme": "Switch light or dark theme",
        "lang_aria": "Language",
        "soon": "Coming soon to the App Store",
        "soon_note": "The link will appear after publication",
        "shot_cap": "Real app screen · D-METER 1.5.1",
        "free_tag": "FREE",
        "pro_tag": "PRO",
        # home
        "home_title": "D-METER — density, temperature, mass and volume for petroleum cargo",
        "home_desc": "D-METER is an iPhone calculator for petroleum cargo: density at temperature, temperature from density, mass and volume, with VAC and AIR values.",
        "eyebrow": "Petroleum cargo calculator for iPhone",
        "h1": "Density, temperature, mass and volume — referred to 15&#8239;°C.",
        "lead": "D-METER turns a density at 15&#8239;°C and an observed temperature into the numbers a cargo needs: density at temperature, mass and volume, with VAC and AIR values side by side.",
        "cta_features": "See the features",
        "facts": ["English · Українська", "No account or sign-in", "No ads or tracking", "Light &amp; dark theme"],
        "readings_aria": "Readings from the app screens on this site",
        "r_density": "Density at temperature",
        "r_volume": "Volume",
        "r_air": "Density in air",
        "r_esc": "Escalation",
        "readings_note": "Values as shown in the app screens on this site.",
        "home_feat_eyebrow": "What it does",
        "home_feat_h2": "One calculator, three working tools.",
        "home_feat_lead": "The base calculator is free. The Density Chart, Blending and Density Escalation come with D-METER PRO.",
        "more": "More",
        "band_h2": "The chart, blending and escalation in one subscription.",
        "band_p": "D-METER PRO Monthly is an auto-renewable subscription through the App Store. The current price, and whether a free trial is available to you, are shown in the app before you confirm.",
        "band_cta": "Download and PRO",
        "band_items": [("Density Chart", "virtual hydrometer"), ("Blending", "tank + incoming"), ("Density Escalation", "USD/t")],
        "band_price_k": "Price",
        "band_price_v": "shown in the app via the App Store",
        "ex_teaser_h2": "Worked examples from the app.",
        "ex_teaser_p": "Four tasks from cargo work, with the inputs and the results exactly as the app shows them.",
        "ex_teaser_cta": "Open the examples",
        "trust_h2": "Your numbers stay on your iPhone.",
        "trust": [("No account", "The app has no sign-in and collects no personal data."),
                  ("No tracking", "No advertising, analytics or third-party crash reporting."),
                  ("On the device", "Calculations run on the device. Only StoreKit talks to Apple.")],
        "trust_link": "Read the Privacy Policy",
        "sup_h2": "Support",
        "sup_p": "Questions, problems or suggestions: write to us. Include your device model, iOS version and app version.",
        "sup_page": "Support page",
        "sup_faq": [("I already subscribed, but PRO is locked.", "Open D-METER PRO from the app menu and tap “Restore purchases”."),
                    ("How do I cancel?", "Tap “Manage subscription” in the app, at least 24 hours before the end of the period."),
                    ("How do I get a refund?", "Payments are processed by Apple, so refunds are requested from Apple.")],
        # features
        "feat_title": "D-METER features — calculator, AIR details, Density Chart, Blending, Density Escalation",
        "feat_desc": "What D-METER does: the free density calculator with AIR details, and the PRO Density Chart, Blending and Density Escalation.",
        "feat_eyebrow": "Features",
        "feat_h1": "From one reading to the whole cargo.",
        "feat_lead": "A free density calculator with AIR details, and three PRO tools for the chart, blending and price escalation.",
        "calc_h": "Calculator",
        "calc_long": "Two modes — Density at temperature and Temperature from density — for the selected product. Enter the density at 15&#8239;°C and the observed temperature, then mass or volume, and D-METER gives the other.",
        "calc_p": "Density at temperature and temperature from density for the selected product. Enter mass or volume and D-METER gives the other.",
        "air_h": "AIR details",
        "air_long": "Tap Details under a result to see density at 15&#8239;°C, density in air, contract density, volume, mass, coefficient&nbsp;a and the formula used. AIR values come with the free calculator.",
        "air_p": "Density in air next to the vacuum value, with volume, mass and the formula used.",
        "chart_h": "Density Chart",
        "chart_long": "A virtual hydrometer. Density against temperature for diesel or gasoline, from −40 to +50&#8239;°C, with the working point, density, expansion and volume read off the curve. Density at 15&#8239;°C switches between VAC and AIR.",
        "chart_p": "A virtual hydrometer: density against temperature, with the working point, expansion and volume read off the curve.",
        "blend_h": "Blending",
        "blend_long": "Tank contents plus incoming product. Enter each from a certificate, an observed density or a weighbridge, by volume or mass, and D-METER gives the blend density at 15&#8239;°C and the total mass.",
        "blend_p": "Tank contents plus incoming product, each from a certificate, an observed density or a weighbridge.",
        "blend_chips": ["Certificate", "Observed density", "Weighbridge"],
        "esc_h": "Density Escalation",
        "esc_long": "Contract density and actual density at 15&#8239;°C, average quotation and seller premium. D-METER returns the escalation, total premium and final price in USD/t, in VAC or AIR, and shows the formula.",
        "esc_p": "Contract versus actual density at 15&#8239;°C gives the escalation and final price in USD/t.",
        "alt_calc": "D-METER Calculator: 10 ppm ULSD, density at 15 °C 833.9 kg/m³, observed temperature 15.0 °C, mass 100.0 t, result 0.8339 kg/L, volume 119.918 m³",
        "alt_air": "AIR details sheet: density at 15.0 °C 0.8339, density in air 0.8328, contract density 0.8450 kg/L, volume 119.918 m³, mass 100.000 t",
        "alt_chart": "D-METER Density Chart: density against temperature for diesel, working point at 15.0 °C, density 833.9 kg/m³",
        "alt_locked": "Density Chart without PRO: lock, PRO badge, “Available with D-METER PRO.” and an Unlock PRO button",
        "cap_locked": "Without PRO the tool shows the offer",
        "alt_blend": "Blending tab: diesel, tank contents and incoming product entered from a certificate, by volume",
        "alt_esc": "Density Escalation: contract 0.8450, actual 0.8339 kg/L, quotation 1044.75, premium 100.00 USD/t, escalation +15.24 USD/t",
        "alt_menu": "D-METER menu: Density Calculator, Density Chart PRO, Density Escalation PRO, D-METER PRO, How to use, Settings",
        "alt_settings": "Settings, lower part: Blending demo switch, app version 1.5.1, links to Privacy Policy, Terms of Use and Support",
        "ro": [("Working point", "+15.0 °C"), ("Density (VAC)", "833.9 kg/m³"), ("Expansion", "+0.0 L"), ("Volume", "119 918.5 L")],
        "esc_k": "Escalation",
        "esc_s": "Final price: 1159.99 USD/t",
        "cmp_eyebrow": "FREE / PRO",
        "cmp_h2": "Start free. Add PRO when the job needs it.",
        "cmp_lead": "Free calculations never depend on the subscription. Everything in FREE stays in PRO.",
        "cmp_feature": "Feature",
        "cmp_yes": "Included",
        "cmp_no": "Not included",
        "cmp_group_free": "Base calculator",
        "cmp_group_pro": "PRO tools",
        "cmp_rows_free": ["Density at temperature", "Temperature from density", "Mass ⇄ volume", "AIR details (density in air)", "English and Ukrainian, light and dark theme"],
        "cmp_rows_pro": ["Density Chart (virtual hydrometer)", "Blending", "Density Escalation"],
        "set_eyebrow": "Settings",
        "set_h2": "Your language. Your theme.",
        "set_p": "Switch the interface between English and Ukrainian and choose a light, dark or system appearance. The legal documents open from Settings too.",
        # examples
        "ex_title": "D-METER examples — worked cargo calculations",
        "ex_desc": "Worked examples from D-METER: volume from mass, density in air, the density chart and price escalation, with the values the app shows.",
        "ex_eyebrow": "Examples",
        "ex_h1": "Worked examples from the app.",
        "ex_lead": "Each example shows the inputs and the result exactly as they appear on a real D-METER screen.",
        "ex_note": "The values come from real app screens (D-METER 1.5.1). With your own inputs the results will differ.",
        "ex_task": "Task",
        "ex_in": "Inputs",
        "ex_out": "Result in the app",
        "ex_formula": "Formula",
        "examples": [
            {"id": "volume-from-mass", "tag": "FREE", "h": "Volume of a diesel cargo from its mass",
             "task": "A 100&#8239;t parcel of 10 ppm ULSD with a density of 833.9&#8239;kg/m³ at 15&#8239;°C: what is its density at the observed temperature and its volume?",
             "in": [("Product", "10 ppm ULSD"), ("Density at 15 °C", "833.9 kg/m³"), ("Observed temperature", "15.0 °C"), ("Mass", "100.0 t")],
             "out": [("Density at temperature", "0.8339 kg/L"), ("Volume", "119.918 m³")],
             "formula": None,
             "note": "At 15.0&#8239;°C the density at temperature equals the density at 15&#8239;°C; at any other temperature D-METER corrects it.",
             "img": "free_calculator", "crop": ""},
            {"id": "density-in-air", "tag": "FREE", "h": "Density in air for the documents",
             "task": "The same parcel: the documents need the density in air next to the vacuum value.",
             "in": [("Density at 15 °C", "0.8339 kg/L"), ("Observed temperature", "15.0 °C"), ("Mass", "100.000 t")],
             "out": [("Density in air", "0.8328 kg/L"), ("Contract density", "0.8450 kg/L"), ("Volume", "119.918 m³")],
             "formula": "Pt = P15 − a × (t − 15) / 1000",
             "note": "Tap Details under the result to open this sheet.",
             "img": "free_air_details", "crop": "from-bottom"},
            {"id": "chart", "tag": "PRO", "h": "Reading the curve",
             "task": "See where the working point sits on the density curve for diesel, and what the expansion and volume are.",
             "in": [("Product", "Diesel"), ("Observed temperature", "15.0 °C"), ("Density at 15 °C", "0.8339 kg/L VAC")],
             "out": [("Working point", "+15.0 °C"), ("Density (VAC)", "833.9 kg/m³"), ("Expansion", "+0.0 L"), ("Volume", "119 918.5 L")],
             "formula": None,
             "note": "Move the temperature slider and the working point, expansion and volume follow the curve.",
             "img": "pro_chart", "crop": ""},
            {"id": "escalation", "tag": "PRO", "h": "Price escalation for a lower density",
             "task": "The contract density is 0.8450&#8239;kg/L, the cargo delivered 0.8339&#8239;kg/L. How does the price per tonne change?",
             "in": [("Contract density at 15 °C", "0.8450 kg/L"), ("Actual density at 15 °C", "0.8339 kg/L"), ("Average quotation", "1044.75 USD/t"), ("Seller premium", "100.00 USD/t")],
             "out": [("Escalation", "+15.24 USD/t"), ("Base price", "1144.75 USD/t"), ("Total premium", "115.24 USD/t"), ("Final price", "1159.99 USD/t")],
             "formula": "Esc = Base × (Contract / Actual − 1)",
             "note": "The same calculation is available on an AIR basis.",
             "img": "pro_escalation", "crop": "from-bottom"},
        ],
        "ex_blend_h": "Blending: tank plus incoming product",
        "ex_blend_p": "Blending combines what is already in the tank with the incoming product. Each side is entered from a certificate, an observed density or a weighbridge, by volume or mass; D-METER gives the blend density at 15&#8239;°C and the total mass.",
        # download
        "dl_title": "Download D-METER for iPhone",
        "dl_desc": "D-METER for iPhone: requirements, languages, the D-METER PRO subscription, and links to the Terms of Use, Privacy Policy and Support.",
        "dl_eyebrow": "Download",
        "dl_h1": "D-METER for iPhone.",
        "dl_lead": "Free to download. The Density Chart, Blending and Density Escalation come with an optional D-METER PRO subscription.",
        "req_h2": "Requirements",
        "req": [("Device", "iPhone"), ("System", "iOS 15.0 or later"), ("Languages", "English, Ukrainian"), ("Account", "Not needed"), ("Price", "Free to download; D-METER PRO is an in-app subscription")],
        "pro_h2": "D-METER PRO Monthly",
        "sub_items": ["Unlocks the Density Chart, Blending and Density Escalation.",
                      "The current price, currency and any free trial are set by the App Store for your account and region, and shown in the app before you confirm.",
                      "“Restore purchases” brings PRO back on another device with the same Apple ID.",
                      "“Manage subscription” opens your App Store subscription settings."],
        "sub_price_k": "Price:",
        "sub_price_v": "not fixed on this site — shown in the app via the App Store",
        "disclosure_label": "As shown in the app",
        "disclosure": "Payment is charged to your Apple ID account at confirmation of purchase. The subscription renews automatically unless it is cancelled at least 24 hours before the end of the current period. Your account is charged for renewal within 24 hours before the end of the current period. You can manage or cancel the subscription in your App Store account settings.",
        "terms_eula": "Terms of Use (EULA)",
        "alt_active": "D-METER PRO screen with an active subscription: PRO is active, Manage subscription, links to the Terms of Use and Privacy Policy",
        "cap_active": "D-METER PRO with an active subscription",
        "brand_h2": "Brand",
        "brand_p": "The D-METER logo and app icon, for press and reviews. Please do not change the colours or proportions.",
        "brand_logo_light": "Logo, light background (SVG)",
        "brand_logo_dark": "Logo, dark background (SVG)",
        "brand_icon": "App icon (SVG)",
        # legal
        "docs_aria": "Documents",
        "source_note": "Document text as published — unchanged.",
        "legal_desc": {"privacy": "D-METER Privacy Policy", "terms": "D-METER Terms of Use", "support": "D-METER Support"},
        # footer
        "f_docs": "Documents",
        "f_site": "Site",
        "f_contact": "Contact",
        "doc_privacy": "Privacy Policy",
        "doc_terms": "Terms of Use",
        "doc_support": "Support",
        "f_tagline": "Petroleum cargo calculator for iPhone.",
        "f_apple": "Apple, iPhone and App Store are trademarks of Apple Inc. D-METER is not affiliated with Apple.",
    },
    "uk": {
        "lang_name": "Українська",
        "skip": "Перейти до вмісту",
        "subtitle": "Калькулятор нафтопродуктів",
        "nav_aria": "Головне меню",
        "nav_home": "Головна",
        "nav_features": "Можливості",
        "nav_examples": "Приклади",
        "nav_download": "Завантажити",
        "nav_support": "Підтримка",
        "menu": "Меню",
        "theme": "Перемкнути світлу або темну тему",
        "lang_aria": "Мова",
        "soon": "Незабаром в App Store",
        "soon_note": "Посилання з’явиться після публікації",
        "shot_cap": "Справжній екран застосунку · D-METER 1.5.1",
        "free_tag": "FREE",
        "pro_tag": "PRO",
        "home_title": "D-METER — густина, температура, маса та об’єм нафтопродуктів",
        "home_desc": "D-METER — калькулятор нафтопродуктів для iPhone: густина за температурою, температура за густиною, маса та об’єм зі значеннями VAC і AIR.",
        "eyebrow": "Калькулятор нафтопродуктів для iPhone",
        "h1": "Густина, температура, маса та об’єм — з приведенням до 15&#8239;°C.",
        "lead": "D-METER перетворює густину за 15&#8239;°C і виміряну температуру на значення, потрібні для вантажу: густину за температурою, масу та об’єм, зі значеннями VAC і AIR поруч.",
        "cta_features": "Переглянути можливості",
        "facts": ["English · Українська", "Без облікового запису та входу", "Без реклами й відстеження", "Світла й темна теми"],
        "readings_aria": "Значення з екранів застосунку на цьому сайті",
        "r_density": "Густина за температурою",
        "r_volume": "Об’єм",
        "r_air": "Густина у повітрі",
        "r_esc": "Коригування",
        "readings_note": "Значення такі, як на екранах застосунку на цьому сайті.",
        "home_feat_eyebrow": "Що вміє D-METER",
        "home_feat_h2": "Один калькулятор і три робочі інструменти.",
        "home_feat_lead": "Базовий калькулятор безкоштовний. Графік густини, змішування та коригування за густиною входять до D-METER PRO.",
        "more": "Докладніше",
        "band_h2": "Графік, змішування та коригування в одній підписці.",
        "band_p": "D-METER PRO Monthly — підписка з автоматичним поновленням через App Store. Актуальну ціну та доступність безкоштовного пробного періоду для вас показано в застосунку до підтвердження.",
        "band_cta": "Завантаження і PRO",
        "band_items": [("Графік густини", "віртуальний ареометр"), ("Змішування", "резервуар + надходження"), ("Коригування за густиною", "USD/t")],
        "band_price_k": "Ціна",
        "band_price_v": "у застосунку через App Store",
        "ex_teaser_h2": "Розібрані приклади із застосунку.",
        "ex_teaser_p": "Чотири задачі з роботи з вантажем — із вхідними даними та результатами точно такими, як їх показує застосунок.",
        "ex_teaser_cta": "Відкрити приклади",
        "trust_h2": "Ваші розрахунки залишаються на iPhone.",
        "trust": [("Без облікового запису", "Застосунок не має входу й не збирає персональних даних."),
                  ("Без відстеження", "Без реклами, аналітики та сторонніх звітів про збої."),
                  ("На пристрої", "Розрахунки виконуються на пристрої. Лише StoreKit зв’язується з Apple.")],
        "trust_link": "Політика конфіденційності",
        "sup_h2": "Підтримка",
        "sup_p": "Запитання, проблеми чи пропозиції — напишіть нам. Вкажіть модель пристрою, версію iOS і версію застосунку.",
        "sup_page": "Сторінка підтримки",
        "sup_faq": [("Підписку вже оформлено, але PRO закрито.", "Відкрийте D-METER PRO з меню застосунку й натисніть «Відновити покупки»."),
                    ("Як скасувати?", "Натисніть «Керувати підпискою» в застосунку щонайменше за 24 години до кінця періоду."),
                    ("Як повернути кошти?", "Платежі обробляє Apple, тому запит на повернення подається в Apple.")],
        "feat_title": "Можливості D-METER — калькулятор, деталі AIR, графік густини, змішування, коригування за густиною",
        "feat_desc": "Що вміє D-METER: безкоштовний калькулятор густини з деталями AIR, а також графік густини, змішування та коригування за густиною в PRO.",
        "feat_eyebrow": "Можливості",
        "feat_h1": "Від одного виміру до всього вантажу.",
        "feat_lead": "Безкоштовний калькулятор густини з деталями AIR і три інструменти PRO: графік, змішування та коригування ціни.",
        "calc_h": "Калькулятор густини",
        "calc_long": "Два режими — «Густина за температурою» і «Температура за густиною» — для вибраного нафтопродукту. Введіть густину за 15&#8239;°C і виміряну температуру, потім масу або об’єм, і D-METER розрахує інше значення.",
        "calc_p": "Густина за температурою й температура за густиною для вибраного нафтопродукту. Введіть масу або об’єм, і D-METER розрахує інше значення.",
        "air_h": "Деталі AIR",
        "air_long": "Натисніть «Деталі» під результатом: густина за 15&#8239;°C, густина у повітрі, контрактна густина, об’єм, маса, коефіцієнт&nbsp;a та формула розрахунку. Значення AIR входять до безкоштовного калькулятора.",
        "air_p": "Густина у повітрі поруч зі значенням у вакуумі, з об’ємом, масою та формулою розрахунку.",
        "chart_h": "Графік густини",
        "chart_long": "Віртуальний ареометр. Залежність густини дизпалива або бензину від температури від −40 до +50&#8239;°C із робочою точкою, густиною, розширенням та об’ємом на кривій. Густину за 15&#8239;°C можна перемикати між VAC і AIR.",
        "chart_p": "Віртуальний ареометр: залежність густини від температури з робочою точкою, розширенням та об’ємом на кривій.",
        "blend_h": "Змішування",
        "blend_long": "Вміст резервуара та надходження. Введіть кожне за паспортом якості, виміряною густиною або автовагами, за об’ємом чи масою, і D-METER розрахує густину суміші за 15&#8239;°C та загальну масу.",
        "blend_p": "Вміст резервуара та надходження — кожне за паспортом якості, виміряною густиною або автовагами.",
        "blend_chips": ["Паспорт якості", "Виміряна густина", "Автоваги"],
        "esc_h": "Коригування за густиною",
        "esc_long": "Контрактна та фактична густина за 15&#8239;°C, середнє котирування і премія продавця. D-METER розраховує коригування, загальну премію та кінцеву ціну в USD/t — у VAC або AIR — і показує формулу.",
        "esc_p": "Контрактна й фактична густина за 15&#8239;°C дають коригування та кінцеву ціну в USD/t.",
        "alt_calc": "Калькулятор D-METER: 10 ppm ULSD, густина за 15 °C 833,9 кг/м³, виміряна температура 15,0 °C, маса 100,0 т, результат 0,8339 кг/л, об’єм 119,918 м³",
        "alt_air": "Деталі розрахунку: густина за 15,0 °C 0,8339, густина у повітрі 0,8328, контрактна густина 0,8450 кг/л, об’єм 119,918 м³, маса 100,000 т",
        "alt_chart": "Графік густини D-METER: залежність густини дизпалива від температури, робоча точка 15,0 °C, густина 833,9 кг/м³",
        "alt_locked": "Графік густини без PRO: замок, позначка PRO, «Доступно з D-METER PRO.» і кнопка «Відкрити PRO»",
        "cap_locked": "Без PRO інструмент показує пропозицію",
        "alt_blend": "Вкладка «Змішування»: дизпаливо, вміст резервуара та надходження за паспортом якості, за об’ємом",
        "alt_esc": "Коригування за густиною: контрактна 0,8450, фактична 0,8339 кг/л, котирування 1044,75, премія 100,00 USD/t, коригування +15,24 USD/t",
        "alt_menu": "Меню D-METER: Калькулятор густини, Графік густини PRO, Коригування за густиною PRO, D-METER PRO, Як користуватись, Налаштування",
        "alt_settings": "Налаштування, нижня частина: перемикач демо-кнопки змішування, версія 1.5.1, посилання на політику конфіденційності, умови використання та підтримку",
        "ro": [("Робоча точка", "+15.0 °C"), ("Густина (VAC)", "833.9 kg/m³"), ("Розширення", "+0.0 L"), ("Об’єм", "119 918.5 L")],
        "esc_k": "Коригування",
        "esc_s": "Кінцева ціна: 1159.99 USD/t",
        "cmp_eyebrow": "FREE / PRO",
        "cmp_h2": "Починайте безкоштовно. Додайте PRO, коли цього потребує робота.",
        "cmp_lead": "Безкоштовні розрахунки не залежать від підписки. Усе, що є у FREE, залишається в PRO.",
        "cmp_feature": "Функція",
        "cmp_yes": "Входить",
        "cmp_no": "Не входить",
        "cmp_group_free": "Базовий калькулятор",
        "cmp_group_pro": "Інструменти PRO",
        "cmp_rows_free": ["Густина за температурою", "Температура за густиною", "Маса ⇄ об’єм", "Деталі AIR (густина у повітрі)", "Англійська та українська, світла й темна теми"],
        "cmp_rows_pro": ["Графік густини (віртуальний ареометр)", "Змішування", "Коригування за густиною"],
        "set_eyebrow": "Налаштування",
        "set_h2": "Ваша мова. Ваша тема.",
        "set_p": "Перемикайте інтерфейс між англійською та українською і вибирайте світлий, темний або системний вигляд. Правові документи також відкриваються з налаштувань.",
        "ex_title": "Приклади D-METER — розібрані розрахунки вантажу",
        "ex_desc": "Розібрані приклади D-METER: об’єм за масою, густина у повітрі, графік густини та коригування ціни — зі значеннями, які показує застосунок.",
        "ex_eyebrow": "Приклади",
        "ex_h1": "Розібрані приклади із застосунку.",
        "ex_lead": "Кожен приклад показує вхідні дані й результат точно так, як вони виглядають на справжньому екрані D-METER.",
        "ex_note": "Значення взято зі справжніх екранів застосунку (D-METER 1.5.1). З вашими даними результати будуть іншими.",
        "ex_task": "Задача",
        "ex_in": "Вхідні дані",
        "ex_out": "Результат у застосунку",
        "ex_formula": "Формула",
        "examples": [
            {"id": "volume-from-mass", "tag": "FREE", "h": "Об’єм партії дизпалива за масою",
             "task": "Партія 10 ppm ULSD масою 100&#8239;т із густиною 833,9&#8239;кг/м³ за 15&#8239;°C: яка її густина за виміряної температури та який об’єм?",
             "in": [("Нафтопродукт", "10 ppm ULSD"), ("Густина за 15 °C", "833.9 kg/m³"), ("Виміряна температура", "15.0 °C"), ("Маса", "100.0 t")],
             "out": [("Густина за температурою", "0.8339 kg/L"), ("Об’єм", "119.918 m³")],
             "formula": None,
             "note": "За 15,0&#8239;°C густина за температурою дорівнює густині за 15&#8239;°C; за будь-якої іншої температури D-METER її коригує.",
             "img": "free_calculator", "crop": ""},
            {"id": "density-in-air", "tag": "FREE", "h": "Густина у повітрі для документів",
             "task": "Та сама партія: для документів потрібна густина у повітрі поруч зі значенням у вакуумі.",
             "in": [("Густина за 15 °C", "0.8339 kg/L"), ("Виміряна температура", "15.0 °C"), ("Маса", "100.000 t")],
             "out": [("Густина у повітрі", "0.8328 kg/L"), ("Контрактна густина", "0.8450 kg/L"), ("Об’єм", "119.918 m³")],
             "formula": "Pt = P15 − a × (t − 15) / 1000",
             "note": "Натисніть «Деталі» під результатом, щоб відкрити це вікно.",
             "img": "free_air_details", "crop": "from-bottom"},
            {"id": "chart", "tag": "PRO", "h": "Значення на кривій",
             "task": "Побачити, де робоча точка лежить на кривій густини дизпалива, і які розширення та об’єм.",
             "in": [("Нафтопродукт", "Дизпаливо"), ("Виміряна температура", "15.0 °C"), ("Густина за 15 °C", "0.8339 kg/L VAC")],
             "out": [("Робоча точка", "+15.0 °C"), ("Густина (VAC)", "833.9 kg/m³"), ("Розширення", "+0.0 L"), ("Об’єм", "119 918.5 L")],
             "formula": None,
             "note": "Перемістіть повзунок температури — робоча точка, розширення та об’єм рухаються за кривою.",
             "img": "pro_chart", "crop": ""},
            {"id": "escalation", "tag": "PRO", "h": "Коригування ціни за нижчої густини",
             "task": "Контрактна густина 0,8450&#8239;кг/л, фактична густина поставленого вантажу 0,8339&#8239;кг/л. Як змінюється ціна за тонну?",
             "in": [("Контрактна густина за 15 °C", "0.8450 kg/L"), ("Фактична густина за 15 °C", "0.8339 kg/L"), ("Середнє котирування", "1044.75 USD/t"), ("Премія продавця", "100.00 USD/t")],
             "out": [("Коригування", "+15.24 USD/t"), ("Базова ціна", "1144.75 USD/t"), ("Загальна премія", "115.24 USD/t"), ("Кінцева ціна", "1159.99 USD/t")],
             "formula": "Esc = Base × (Contract / Actual − 1)",
             "note": "Той самий розрахунок доступний і на базі AIR.",
             "img": "pro_escalation", "crop": "from-bottom"},
        ],
        "ex_blend_h": "Змішування: резервуар і надходження",
        "ex_blend_p": "Змішування поєднує те, що вже є в резервуарі, з надходженням. Кожну частину вводять за паспортом якості, виміряною густиною або автовагами, за об’ємом чи масою; D-METER розраховує густину суміші за 15&#8239;°C та загальну масу.",
        "dl_title": "Завантажити D-METER для iPhone",
        "dl_desc": "D-METER для iPhone: вимоги, мови, підписка D-METER PRO та посилання на умови використання, політику конфіденційності й підтримку.",
        "dl_eyebrow": "Завантажити",
        "dl_h1": "D-METER для iPhone.",
        "dl_lead": "Завантаження безкоштовне. Графік густини, змішування та коригування за густиною доступні з необов’язковою підпискою D-METER PRO.",
        "req_h2": "Вимоги",
        "req": [("Пристрій", "iPhone"), ("Система", "iOS 15.0 або новіша"), ("Мови", "англійська, українська"), ("Обліковий запис", "Не потрібен"), ("Ціна", "Завантаження безкоштовне; D-METER PRO — підписка в застосунку")],
        "pro_h2": "D-METER PRO Monthly",
        "sub_items": ["Відкриває графік густини, змішування та коригування за густиною.",
                      "Актуальну ціну, валюту та можливий безкоштовний період визначає App Store для вашого облікового запису й регіону; їх показано в застосунку до підтвердження.",
                      "«Відновити покупки» повертає PRO на іншому пристрої з тим самим Apple ID.",
                      "«Керувати підпискою» відкриває налаштування підписки в App Store."],
        "sub_price_k": "Ціна:",
        "sub_price_v": "не фіксується на сайті — показано в застосунку через App Store",
        "disclosure_label": "Як у застосунку",
        "disclosure": "Оплата списується з облікового запису Apple ID після підтвердження покупки. Підписка поновлюється автоматично, якщо її не скасовано щонайменше за 24 години до кінця поточного періоду. Плата за поновлення списується протягом 24 годин до кінця поточного періоду. Керувати підпискою або скасувати її можна в налаштуваннях облікового запису App Store.",
        "terms_eula": "Умови використання (EULA)",
        "alt_active": "Екран D-METER PRO з активною підпискою: PRO активний, «Керувати підпискою», посилання на умови використання та політику конфіденційності",
        "cap_active": "D-METER PRO з активною підпискою",
        "brand_h2": "Бренд",
        "brand_p": "Логотип і значок D-METER для преси та оглядів. Будь ласка, не змінюйте кольори та пропорції.",
        "brand_logo_light": "Логотип, світлий фон (SVG)",
        "brand_logo_dark": "Логотип, темний фон (SVG)",
        "brand_icon": "Значок застосунку (SVG)",
        "docs_aria": "Документи",
        "source_note": "Текст документа як опубліковано — без змін.",
        "legal_desc": {"privacy": "Політика конфіденційності D-METER", "terms": "Умови використання D-METER", "support": "Підтримка D-METER"},
        "f_docs": "Документи",
        "f_site": "Сайт",
        "f_contact": "Контакти",
        "doc_privacy": "Політика конфіденційності",
        "doc_terms": "Умови використання",
        "doc_support": "Підтримка",
        "f_tagline": "Калькулятор нафтопродуктів для iPhone.",
        "f_apple": "Apple, iPhone і App Store — торговельні марки Apple Inc. D-METER не пов’язаний з Apple.",
    },
}

# Logo A, compact: outlined wordmark (Roboto w700, DMETER-BRAND-SELECTION-01).
# "D-" follows the text colour, "METER" stays brand red; the name is never translated.
_WM = json.loads((TOOLS / "brand-wordmark.json").read_text(encoding="utf-8"))
WORDMARK = (f'<svg class="wm-svg" viewBox="{_WM["bbox"][0]:.1f} {_WM["bbox"][1]:.1f} {_WM["bbox"][2]:.1f} {-_WM["bbox"][1]:.1f}" '
            f'role="img" aria-label="D-METER"><path class="d" d="{_WM["d"]}"/><path class="m" d="{_WM["meter"]}"/></svg>')

# Logo A, full (with the hydrometer scale): the published SVG with its dark ink
# replaced by currentColor, so one inline copy serves the light and dark themes.
LOGO_FULL = ((ROOT / "assets/brand/logo-full-light.svg").read_text(encoding="utf-8")
             .replace(' xmlns="http://www.w3.org/2000/svg"', "")
             .replace("<svg ", '<svg class="logo-full" ', 1)
             .replace('fill="#1A1A1A"', 'fill="currentColor"'))
assert "#1A1A1A" not in LOGO_FULL

SVG_SUN = '<svg class="sun" aria-hidden="true" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><circle cx="10" cy="10" r="3.6"/><path d="M10 1.8v2M10 16.2v2M1.8 10h2M16.2 10h2M4.2 4.2l1.4 1.4M14.4 14.4l1.4 1.4M4.2 15.8l1.4-1.4M14.4 5.6l1.4-1.4"/></svg>'
SVG_MOON = '<svg class="moon" aria-hidden="true" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"><path d="M16.5 12.3A7 7 0 0 1 7.7 3.5a7 7 0 1 0 8.8 8.8Z"/></svg>'
SVG_MENU = '<svg aria-hidden="true" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M3 6h14M3 10h14M3 14h14"/></svg>'


def app_img(p, lang, name, alt, w=786, h=1704):
    """A real app screen. A dark render (<name>_dark.webp) is used in the dark
    theme when it exists; until then the light screen is shown in both."""
    src = f"{p}{IMG}{lang}_{name}.webp"
    dark = ROOT / IMG / f"{lang}_{name}_dark.webp"
    if not dark.exists():
        return f'<img src="{src}" alt="{alt}" loading="lazy" decoding="async" width="{w}" height="{h}">'
    return (f'<img class="only-light" src="{src}" alt="{alt}" loading="lazy" decoding="async" width="{w}" height="{h}">'
            f'<img class="only-dark" src="{p}{IMG}{lang}_{name}_dark.webp" alt="{alt}" loading="lazy" decoding="async" width="{w}" height="{h}">')


def shot(p, lang, name, alt, cap, extra_class=""):
    return f"""<figure class="shot">
<div class="shot-frame {extra_class}">{app_img(p, lang, name, alt)}</div>
<figcaption>{cap}</figcaption>
</figure>"""


def head(lang, depth, page, title, desc):
    p = "../" * depth
    o = OTHER[lang]
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<meta name="referrer" content="no-referrer">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{BASE_URL}{lang}/{page}">
<link rel="alternate" hreflang="{lang}" href="{BASE_URL}{lang}/{page}">
<link rel="alternate" hreflang="{o}" href="{BASE_URL}{o}/{page}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="D-METER">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{BASE_URL}{lang}/{page}">
<meta property="og:image" content="{BASE_URL}assets/brand/icon-512.png">
<link rel="icon" type="image/svg+xml" href="{p}assets/brand/icon-light.svg">
<link rel="icon" type="image/png" sizes="32x32" href="{p}assets/brand/favicon-32.png">
<link rel="apple-touch-icon" href="{p}assets/brand/apple-touch-icon.png">
<link rel="stylesheet" href="{p}assets/site.css">
<script src="{p}assets/site.js"></script>
</head>
<body>
<a class="skip" href="#content">{T[lang]['skip']}</a>
"""


def brand_link(p, lang, home):
    t = T[lang]
    return (f'<a class="brand" href="{home}">'
            f'<img class="brand-icon only-light" src="{p}assets/brand/icon-light.svg" alt="" width="36" height="36">'
            f'<img class="brand-icon only-dark" src="{p}assets/brand/icon-dark.svg" alt="" width="36" height="36">'
            f'<span class="brand-text"><span class="wordmark">{WORDMARK}</span><small>{t["subtitle"]}</small></span></a>')


def header(lang, depth, page, current):
    t = T[lang]
    p = "../" * depth
    home = f"{p}{lang}/"
    links = [
        ("features", f"{home}features/", t["nav_features"]),
        ("examples", f"{home}examples/", t["nav_examples"]),
        ("download", f"{home}download/", t["nav_download"]),
        ("support", f"{home}support/", t["nav_support"]),
    ]

    def nav_links():
        return "\n".join(f'<a href="{href}"' + (' aria-current="page"' if key == current else "") + f">{label}</a>"
                         for key, href, label in links)

    lang_links = "".join(
        f'<a href="{p}{l}/{page}" hreflang="{l}" lang="{l}"' + (' aria-current="true"' if l == lang else "")
        + f' aria-label="{T[l]["lang_name"]}">{l.upper()}</a>' for l in LANGS)
    return f"""<header class="site-header">
<div class="wrap">
{brand_link(p, lang, home)}
<nav class="nav" aria-label="{t['nav_aria']}">
{nav_links()}
</nav>
<div class="tools">
<div class="lang" role="group" aria-label="{t['lang_aria']}" data-lang-switch>{lang_links}</div>
<button class="icon-btn theme-btn" type="button" aria-label="{t['theme']}" aria-pressed="false">{SVG_SUN}{SVG_MOON}</button>
<details class="menu">
<summary class="icon-btn" aria-label="{t['menu']}">{SVG_MENU}</summary>
<nav class="menu-panel" aria-label="{t['nav_aria']}">
{nav_links()}
</nav>
</details>
</div>
</div>
</header>
"""


def footer(lang, depth):
    t = T[lang]
    p = "../" * depth
    home = f"{p}{lang}/"
    o = OTHER[lang]
    return f"""<footer class="site-footer">
<div class="wrap">
<div class="col">
<span class="wordmark">{WORDMARK}</span>
<span class="legal-note">{t['f_tagline']}</span>
<span class="legal-note">© 2026 {DEV}</span>
</div>
<nav aria-label="{t['f_site']}">
<span class="label">{t['f_site']}</span>
<a href="{home}">{t['nav_home']}</a>
<a href="{home}features/">{t['nav_features']}</a>
<a href="{home}examples/">{t['nav_examples']}</a>
<a href="{home}download/">{t['nav_download']}</a>
<a href="{p}{o}/" hreflang="{o}" lang="{o}" data-lang="{o}">{T[o]['lang_name']}</a>
</nav>
<nav aria-label="{t['f_docs']}">
<span class="label">{t['f_docs']}</span>
<a href="{home}privacy/">{t['doc_privacy']}</a>
<a href="{home}terms/">{t['doc_terms']}</a>
<a href="{home}support/">{t['doc_support']}</a>
</nav>
<div class="col">
<span class="label">{t['f_contact']}</span>
<a class="email" href="mailto:{EMAIL}">{EMAIL}</a>
</div>
<p class="fine">{t['f_apple']}</p>
</div>
</footer>
</body>
</html>
"""


def soon(lang):
    t = T[lang]
    return f'<span class="btn btn-soon" aria-disabled="true">{t["soon"]}<small>{t["soon_note"]}</small></span>'


def compare_table(t):
    yes = f'<span aria-hidden="true">✓</span><span class="sr-only">{t["cmp_yes"]}</span>'
    no = f'<span aria-hidden="true">—</span><span class="sr-only">{t["cmp_no"]}</span>'
    rows = [f'<tr class="group"><th scope="rowgroup" colspan="3">{t["cmp_group_free"]}</th></tr>']
    rows += [f'<tr><th scope="row">{n}</th><td class="yes">{yes}</td><td class="yes pro">{yes}</td></tr>' for n in t["cmp_rows_free"]]
    rows.append(f'<tr class="group"><th scope="rowgroup" colspan="3">{t["cmp_group_pro"]}</th></tr>')
    rows += [f'<tr><th scope="row">{n}</th><td class="no">{no}</td><td class="yes pro">{yes}</td></tr>' for n in t["cmp_rows_pro"]]
    return f"""<div class="table-box">
<table class="compare">
<colgroup><col><col class="c-tier"><col class="c-tier"></colgroup>
<thead><tr><th scope="col">{t['cmp_feature']}</th><th scope="col">FREE</th><th scope="col" class="pro">PRO</th></tr></thead>
<tbody>
{chr(10).join(rows)}
</tbody>
</table>
</div>"""


def tag(t, kind):
    return f'<span class="tag tag-{kind.lower()}">{t[kind.lower() + "_tag"]}</span>'


def home(lang):
    t = T[lang]
    p = "../"
    trust = "\n".join(f"<div><strong>{a}</strong><p>{b}</p></div>" for a, b in t["trust"])
    faq = "\n".join(f"<div><dt>{q}</dt><dd>{a}</dd></div>" for q, a in t["sup_faq"])
    facts = "\n".join(f"<li>{f}</li>" for f in t["facts"])
    band_items = "\n".join(f"<li><strong>{a}</strong><span>{b}</span></li>" for a, b in t["band_items"])

    def card(anchor, kind, h, text, img, alt, crop=""):
        return f"""<article class="card">
{tag(t, kind)}
<h3>{h}</h3>
<p>{text}</p>
<a class="more" href="features/#{anchor}">{t['more']} →</a>
<div class="card-shot {crop}">{app_img(p, lang, img, alt)}</div>
</article>"""

    return head(lang, 1, "", t["home_title"], t["home_desc"]) + header(lang, 1, "", "home") + f"""<main id="content">
<section class="hero">
<div class="wrap">
<div class="hero-copy">
<p class="eyebrow">{t['eyebrow']}</p>
<h1>{t['h1']}</h1>
<p class="lead">{t['lead']}</p>
<div class="btn-row">
{soon(lang)}
<a class="btn btn-secondary" href="features/">{t['cta_features']}</a>
</div>
<ul class="facts">
{facts}
</ul>
</div>
<div class="hero-shots">
{shot(p, lang, "free_calculator", t["alt_calc"], t["shot_cap"])}
{shot(p, lang, "pro_chart", t["alt_chart"], t["shot_cap"])}
</div>
</div>
</section>

<section class="readings" aria-label="{t['readings_aria']}">
<div class="wrap">
<div class="reading"><span>{t['r_density']}</span><span class="value">0.8339 <span class="unit">kg/L</span></span></div>
<div class="reading"><span>{t['r_volume']}</span><span class="value">119.918 <span class="unit">m³</span></span></div>
<div class="reading"><span>{t['r_air']}</span><span class="value">0.8328 <span class="unit">kg/L</span></span></div>
<div class="reading"><span>{t['r_esc']}</span><span class="value accent">+15.24 <span class="unit">USD/t</span></span></div>
<p class="readings-note">{t['readings_note']}</p>
</div>
</section>

<section class="section">
<div class="wrap">
<div class="section-head">
<p class="eyebrow muted">{t['home_feat_eyebrow']}</p>
<h2>{t['home_feat_h2']}</h2>
<p>{t['home_feat_lead']}</p>
</div>
<div class="cards cards-2">
{card("calculator", "FREE", t["calc_h"], t["calc_p"], "free_calculator", t["alt_calc"])}
{card("air-details", "FREE", t["air_h"], t["air_p"], "free_air_details", t["alt_air"], "from-bottom")}
</div>
<div class="cards cards-3">
{card("density-chart", "PRO", t["chart_h"], t["chart_p"], "pro_chart", t["alt_chart"])}
{card("blending", "PRO", t["blend_h"], t["blend_p"], "pro_blending", t["alt_blend"])}
{card("density-escalation", "PRO", t["esc_h"], t["esc_p"], "pro_escalation", t["alt_esc"], "from-bottom")}
</div>
</div>
</section>

<section class="section-tight">
<div class="wrap">
<div class="band">
<div class="band-copy">
<span class="wordmark band-wm">{WORDMARK} <i>PRO</i></span>
<h2>{t['band_h2']}</h2>
<p>{t['band_p']}</p>
<div class="btn-row"><a class="btn btn-primary" href="download/">{t['band_cta']}</a></div>
</div>
<ul class="band-list">
{band_items}
<li><span>{t['band_price_k']}</span><span>{t['band_price_v']}</span></li>
</ul>
</div>
</div>
</section>

<section class="section">
<div class="wrap teaser">
<div>
<h2>{t['ex_teaser_h2']}</h2>
<p>{t['ex_teaser_p']}</p>
</div>
<a class="btn btn-secondary" href="examples/">{t['ex_teaser_cta']} →</a>
</div>
</section>

<section class="section-tight">
<div class="wrap trust">
<h2>{t['trust_h2']}</h2>
{trust}
</div>
<div class="wrap trust-link"><a href="privacy/">{t['trust_link']} →</a></div>
</section>

<section class="section">
<div class="wrap">
<div class="support-box">
<div class="left">
<h2>{t['sup_h2']}</h2>
<p>{t['sup_p']}</p>
<a class="btn btn-tonal email" href="mailto:{EMAIL}">{EMAIL}</a>
<a href="support/">{t['sup_page']} →</a>
</div>
<dl>
{faq}
</dl>
</div>
</div>
</section>
</main>
""" + footer(lang, 1)


def page_head(t, eyebrow, h1, lead, extra=""):
    return f"""<section class="page-head">
<div class="wrap">
<p class="eyebrow">{eyebrow}</p>
<h1>{h1}</h1>
<p class="lead">{lead}</p>
{extra}
</div>
</section>
"""


def features(lang):
    t = T[lang]
    p = "../../"
    ro = "\n".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in t["ro"])
    chips = "\n".join(f"<li>{c}</li>" for c in t["blend_chips"])

    def split(anchor, num, kind, h, text, media, extra="", reverse=False):
        return f"""<div class="split{' reverse' if reverse else ''}" id="{anchor}">
<div class="split-copy">
<span class="num">{num} · {tag(t, kind)}</span>
<h2>{h}</h2>
<p>{text}</p>
{extra}
</div>
<div class="split-media">
{media}
</div>
</div>"""

    body = "\n\n".join([
        split("calculator", "01", "FREE", t["calc_h"], t["calc_long"],
              shot(p, lang, "free_calculator", t["alt_calc"], t["shot_cap"])),
        split("air-details", "02", "FREE", t["air_h"], t["air_long"],
              shot(p, lang, "free_air_details", t["alt_air"], t["shot_cap"]), reverse=True),
        split("density-chart", "03", "PRO", t["chart_h"], t["chart_long"],
              shot(p, lang, "pro_chart", t["alt_chart"], t["shot_cap"]) + "\n"
              + shot(p, lang, "free_chart_locked", t["alt_locked"], t["cap_locked"]),
              f'<dl class="readout">\n{ro}\n</dl>'),
        split("blending", "04", "PRO", t["blend_h"], t["blend_long"],
              shot(p, lang, "pro_blending", t["alt_blend"], t["shot_cap"]),
              f'<ul class="chips">\n{chips}\n</ul>', reverse=True),
        split("density-escalation", "05", "PRO", t["esc_h"], t["esc_long"],
              shot(p, lang, "pro_escalation", t["alt_esc"], t["shot_cap"]),
              f"""<div class="result-tile">
<span class="k">{t['esc_k']}</span>
<span class="v">+15.24 <small>USD/t</small></span>
<span class="s">{t['esc_s']}</span>
</div>"""),
    ])
    return head(lang, 2, "features/", t["feat_title"], t["feat_desc"]) + header(lang, 2, "features/", "features") + f"""<main id="content">
{page_head(t, t['feat_eyebrow'], t['feat_h1'], t['feat_lead'])}
<section class="section section-first">
<div class="wrap">
{body}
</div>
</section>

<section class="section alt" id="compare">
<div class="wrap compare-grid">
<div class="section-head">
<p class="eyebrow muted">{t['cmp_eyebrow']}</p>
<h2>{t['cmp_h2']}</h2>
<p>{t['cmp_lead']}</p>
</div>
{compare_table(t)}
</div>
</section>

<section class="section" id="settings">
<div class="wrap settings">
<div class="split-copy">
<p class="eyebrow muted">{t['set_eyebrow']}</p>
<h2>{t['set_h2']}</h2>
<p>{t['set_p']}</p>
</div>
<div class="split-media">
{shot(p, lang, "free_menu", t["alt_menu"], t["shot_cap"])}
{shot(p, lang, "free_settings", t["alt_settings"], t["shot_cap"], "lower")}
</div>
</div>
</section>
</main>
""" + footer(lang, 2)


def examples(lang):
    t = T[lang]
    p = "../../"
    blocks = []
    for i, ex in enumerate(t["examples"], 1):
        ins = "\n".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in ex["in"])
        outs = "\n".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in ex["out"])
        formula = (f'<p class="formula"><span class="k">{t["ex_formula"]}</span><code>{ex["formula"]}</code></p>'
                   if ex["formula"] else "")
        alt = {"free_calculator": t["alt_calc"], "free_air_details": t["alt_air"],
               "pro_chart": t["alt_chart"], "pro_escalation": t["alt_esc"]}[ex["img"]]
        blocks.append(f"""<article class="example{' reverse' if i % 2 == 0 else ''}" id="{ex['id']}">
<div class="example-copy">
<span class="num">{i:02d} · {tag(t, ex['tag'])}</span>
<h2>{ex['h']}</h2>
<p class="task"><span class="k">{t['ex_task']}</span>{ex['task']}</p>
<div class="io">
<div><span class="k">{t['ex_in']}</span><dl class="readout">
{ins}
</dl></div>
<div><span class="k">{t['ex_out']}</span><dl class="readout result">
{outs}
</dl></div>
</div>
{formula}
<p class="ex-note">{ex['note']}</p>
</div>
<div class="split-media">
{shot(p, lang, ex['img'], alt, t['shot_cap'], ex['crop'])}
</div>
</article>""")
    chips = "\n".join(f"<li>{c}</li>" for c in t["blend_chips"])
    return head(lang, 2, "examples/", t["ex_title"], t["ex_desc"]) + header(lang, 2, "examples/", "examples") + f"""<main id="content">
{page_head(t, t['ex_eyebrow'], t['ex_h1'], t['ex_lead'], f'<p class="page-note">{t["ex_note"]}</p>')}
<section class="section section-first">
<div class="wrap">
{chr(10).join(blocks)}

<article class="example" id="blending">
<div class="example-copy">
<span class="num">05 · {tag(t, 'PRO')}</span>
<h2>{t['ex_blend_h']}</h2>
<p>{t['ex_blend_p']}</p>
<ul class="chips">
{chips}
</ul>
</div>
<div class="split-media">
{shot(p, lang, "pro_blending", t["alt_blend"], t["shot_cap"])}
</div>
</article>
</div>
</section>
</main>
""" + footer(lang, 2)


def download(lang):
    t = T[lang]
    p = "../../"
    req = "\n".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in t["req"])
    items = "\n".join(f"<li>{i}</li>" for i in t["sub_items"])
    hero = f"""<div class="dl-hero">
<img class="dl-icon only-light" src="{p}assets/brand/icon-light.svg" alt="" width="120" height="120">
<img class="dl-icon only-dark" src="{p}assets/brand/icon-dark.svg" alt="" width="120" height="120">
<div class="dl-logo">{LOGO_FULL}</div>
</div>
<div class="btn-row">{soon(lang)}</div>"""
    return head(lang, 2, "download/", t["dl_title"], t["dl_desc"]) + header(lang, 2, "download/", "download") + f"""<main id="content">
{page_head(t, t['dl_eyebrow'], t['dl_h1'], t['dl_lead'], hero)}
<section class="section section-first">
<div class="wrap dl-grid">
<div class="dl-req">
<h2>{t['req_h2']}</h2>
<dl class="spec">
{req}
</dl>
</div>
<div class="sub-copy" id="subscription">
<h2>{t['pro_h2']}</h2>
<div class="price-row"><strong>{t['sub_price_k']}</strong><span>{t['sub_price_v']}</span></div>
<ul>
{items}
</ul>
<p class="disclosure"><span class="disclosure-label">{t['disclosure_label']}</span>{t['disclosure']}</p>
<p class="doc-links"><a href="../terms/">{t['terms_eula']}</a> · <a href="../privacy/">{t['doc_privacy']}</a> · <a href="../support/">{t['doc_support']}</a></p>
</div>
</div>
</section>

<section class="section alt">
<div class="wrap settings">
<div class="split-copy">
<h2>{t['cap_active']}</h2>
<p>{t['sub_items'][3]}</p>
</div>
<div class="split-media">
{shot(p, lang, "pro_paywall_active", t["alt_active"], t["shot_cap"])}
</div>
</div>
</section>

<section class="section" id="brand">
<div class="wrap">
<div class="section-head">
<h2>{t['brand_h2']}</h2>
<p>{t['brand_p']}</p>
</div>
<ul class="brand-files">
<li><a href="{p}assets/brand/logo-full-light.svg"><span class="bf-prev bf-light"><img src="{p}assets/brand/logo-full-light.svg" alt="" loading="lazy" width="240" height="65"></span>{t['brand_logo_light']}</a></li>
<li><a href="{p}assets/brand/logo-full-dark.svg"><span class="bf-prev bf-dark"><img src="{p}assets/brand/logo-full-dark.svg" alt="" loading="lazy" width="240" height="65"></span>{t['brand_logo_dark']}</a></li>
<li><a href="{p}assets/brand/icon-light.svg"><span class="bf-prev"><img class="bf-icon" src="{p}assets/brand/icon-light.svg" alt="" loading="lazy" width="72" height="72"></span>{t['brand_icon']}</a></li>
</ul>
</div>
</section>
</main>
""" + footer(lang, 2)


def legal_mains():
    """Runs tools/build_site.py into a temporary directory and returns the
    published <title> and <main> of each document."""
    out = {}
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run([sys.executable, "-I", str(TOOLS / "build_site.py"), tmp, LEGAL_DATE], check=True)
        for lang in LANGS:
            for doc in DOCS:
                raw = (pathlib.Path(tmp) / lang / doc / "index.html").read_text(encoding="utf-8")
                title = re.search(r"<title>(.*?)</title>", raw, re.S).group(1)
                main = re.search(r"<main>(.*?)</main>", raw, re.S).group(1)
                out[(lang, doc)] = (title, main)
    return out


def legal(lang, doc, title, main):
    t = T[lang]
    tabs = "\n".join(f'<a href="../{d}/"' + (' aria-current="page"' if d == doc else "") + f'>{t["doc_" + d]}</a>'
                     for d in DOCS)
    return head(lang, 2, f"{doc}/", title, t["legal_desc"][doc]) + header(lang, 2, f"{doc}/", "support" if doc == "support" else None) + f"""<main id="content">
<div class="wrap legal-top">
<nav class="doc-tabs" aria-label="{t['docs_aria']}">
{tabs}
</nav>
</div>
<div class="wrap legal-layout">
<article class="doc"><main-doc>{main}</main-doc><p class="source-note">{t['source_note']}</p></article>
</div>
</main>
""" + footer(lang, 2)


def root_index():
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<meta name="referrer" content="no-referrer">
<title>D-METER</title>
<meta name="description" content="D-METER — petroleum cargo calculator for iPhone. English and Ukrainian.">
<link rel="canonical" href="{BASE_URL}">
<link rel="alternate" hreflang="en" href="{BASE_URL}en/">
<link rel="alternate" hreflang="uk" href="{BASE_URL}uk/">
<link rel="icon" type="image/svg+xml" href="assets/brand/icon-light.svg">
<link rel="icon" type="image/png" sizes="32x32" href="assets/brand/favicon-32.png">
<link rel="apple-touch-icon" href="assets/brand/apple-touch-icon.png">
<link rel="stylesheet" href="assets/site.css">
<script src="assets/site.js"></script>
</head>
<body>
<main class="chooser">
<img class="chooser-icon only-light" src="assets/brand/icon-light.svg" alt="" width="96" height="96">
<img class="chooser-icon only-dark" src="assets/brand/icon-dark.svg" alt="" width="96" height="96">
<h1 class="chooser-logo">{LOGO_FULL}</h1>
<p class="chooser-sub">Petroleum cargo calculator for iPhone · <span lang="uk">Калькулятор нафтопродуктів для iPhone</span></p>
<div class="chooser-options">
<a href="en/" hreflang="en" lang="en" data-lang="en"><strong>English</strong><span>Features, examples, download, support and legal documents</span></a>
<a href="uk/" hreflang="uk" lang="uk" data-lang="uk"><strong>Українська</strong><span>Можливості, приклади, завантаження, підтримка та правові документи</span></a>
</div>
<p class="chooser-docs"><a href="en/privacy/">Privacy Policy</a> · <a href="en/terms/">Terms of Use</a> · <a href="en/support/">Support</a></p>
</main>
</body>
</html>
"""


def not_found():
    b = "/d-meter-legal/"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<meta name="referrer" content="no-referrer">
<meta name="robots" content="noindex">
<title>Page not found · Сторінку не знайдено</title>
<link rel="icon" type="image/png" sizes="32x32" href="{b}assets/brand/favicon-32.png">
<link rel="stylesheet" href="{b}assets/site.css">
</head>
<body>
<main class="chooser">
<span class="wordmark chooser-wm">{WORDMARK}</span>
<h1 class="nf-title">Page not found · <span lang="uk">Сторінку не знайдено</span></h1>
<div class="chooser-options">
<a href="{b}en/" hreflang="en" lang="en"><strong>English</strong><span>D-METER home</span></a>
<a href="{b}uk/" hreflang="uk" lang="uk"><strong>Українська</strong><span>Головна D-METER</span></a>
</div>
<p class="chooser-docs"><a href="{b}en/privacy/">Privacy Policy</a> · <a href="{b}en/terms/">Terms of Use</a> · <a href="{b}en/support/">Support</a></p>
</main>
</body>
</html>
"""


PAGES = ("", "features/", "examples/", "download/") + tuple(f"{d}/" for d in DOCS)

# English UI phrases that must never appear in a Ukrainian page's own chrome.
UK_FORBIDDEN = ["Features", "Examples", "Download and", "Support page", "Coming soon", "Read the Privacy",
                "Real app screen", "Start free.", "Your language", "No account", "Skip to content",
                "Worked examples", "Requirements", "Result in the app", "Inputs", "See the features", ">More<"]


def main():
    mains = legal_mains()
    log = []
    for lang in LANGS:
        pages = {"": home(lang), "features/": features(lang), "examples/": examples(lang), "download/": download(lang)}
        for doc in DOCS:
            title, main_html = mains[(lang, doc)]
            pages[f"{doc}/"] = legal(lang, doc, title, main_html)
        for path, html in pages.items():
            if lang == "uk":
                chrome = re.sub(r"<main-doc>.*?</main-doc>", "", html, flags=re.S)
                bad = [w for w in UK_FORBIDDEN if w in chrome]
                assert not bad, f"untranslated in uk/{path}: {bad}"
            # <main-doc> only marks the verbatim block while building
            html = html.replace("<main-doc>", "").replace("</main-doc>", "")
            f = ROOT / lang / path / "index.html"
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(html, encoding="utf-8")
            log.append(f"wrote {f.relative_to(ROOT)}")
    (ROOT / "index.html").write_text(root_index(), encoding="utf-8")
    (ROOT / "404.html").write_text(not_found(), encoding="utf-8")
    urls = [BASE_URL] + [f"{BASE_URL}{l}/{p}" for l in LANGS for p in PAGES]
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"<url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n", encoding="utf-8")
    log += ["wrote index.html", "wrote 404.html", "wrote sitemap.xml"]
    print("\n".join(log))


if __name__ == "__main__":
    main()
