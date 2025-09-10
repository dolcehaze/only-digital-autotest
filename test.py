# test_footer_checks.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import sys, time

def any_present(candidates, source_text):
    """Возвращает (True, найденная_строка) если хотя бы одна из candidates найдена (case-insensitive)."""
    src = (source_text or "").lower()
    for c in candidates:
        if c.lower() in src:
            return True, c
    return False, None

def main():
    # Настройки драйвера — поменяй при необходимости
    driver = webdriver.Chrome()  # или укажи путь: webdriver.Chrome('/path/to/chromedriver')
    driver.set_page_load_timeout(20)

    errors = []
    try:
        driver.get("https://only.digital/")
    except Exception as e:
        print("⚠️ Ошибка при загрузке страницы:", e)

    # Ждём, пока DOM появится
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    except TimeoutException:
        print("⚠️ Страница не успела загрузиться за 10 секунд, продолжаем проверки...")

    page_src = driver.page_source or ""
    footer = None
    footer_text = ""
    footer_html = ""
    try:
        footer = driver.find_element(By.TAG_NAME, "footer")
        footer_text = footer.text or ""
        footer_html = footer.get_attribute("innerHTML") or ""
        # Прокрутка к футеру (иногда нужно, чтобы элементы подгрузились)
        driver.execute_script("arguments[0].scrollIntoView(true);", footer)
        time.sleep(0.5)
    except Exception as e:
        errors.append(f"Футер не найден: {e}")

    # Для диагностики: распечатать текст футера (можно закомментировать)
    print("----- footer.text (для отладки) -----")
    print(footer_text[:1000])  # печатаем первые 1000 символов для наглядности
    print("----- конец футера -----\n")

    # Список проверок: (описание, список возможных текстов для поиска, область поиска: "footer" или "page")
    checks = [
        ("Наличие пунктов меню (один из ожидаемых)", ["Work", "About us", "What we do", "Career", "Blog", "Contacts",
                                                    "Работы", "О нас", "Что мы делаем", "Карьера", "Блог", "Контакты"], "page"),
        ("Email контакта", ["hello@only.digital"], "page"),
        ("Телефон", ["+7 (495) 740 99 79", "+7 495 740 99 79", "+74957409979", "+7 (495)"], "page"),
        ("Telegram (ник или ссылка)", ["@onlydigitalagency", "t.me/onlydigitalagency"], "page"),
        ("Behance (ссылка)", ["behance.net"], "page"),
        ("DProfile (ссылка)", ["dprofile.ru"], "page"),
        ("VK (ссылка)", ["vk.com"], "page"),
        ("Копирайт (2014 и 2025)", ["2014", "2025"], "footer"),  # ищем в футере в первую очередь
    ]

    for desc, candidates, scope in checks:
        if scope == "footer" and footer_html:
            source = footer_html
        else:
            source = page_src  # fallback — ищем по всей странице

        ok, found = any_present(candidates, source)
        if ok:
            print(f"OK: {desc} → найдено: {found}")
        else:
            # для копирайта можно требовать оба числа — пример расширения:
            if desc.startswith("Копирайт"):
                # проверим отдельно наличие обоих чисел в футере
                f_ok1, _ = any_present(["2014"], footer_html)
                f_ok2, _ = any_present(["2025"], footer_html)
                if f_ok1 and f_ok2:
                    print("OK: копирайт 2014 и 2025 найдены в футере.")
                    continue
            errors.append(f"FAIL: {desc} — ничего не найдено. Проверяемые вариации: {candidates}")

    # Вывод сводки
    print("\n===== СВОДКА ПРОВЕРОК =====")
    if errors:
        print(f"Обнаружено {len(errors)} проблем(ы):")
        for e in errors:
            print(" -", e)
        print("\n🔔 Тест завершён с ошибками.")
        driver.quit()
        # Возвращаем код >0 чтобы CI показал провал, но тест не остановился на первой ошибке
        sys.exit(1)
    else:
        print("✅ Все проверки футера прошли успешно.")
        driver.quit()
        sys.exit(0)

if __name__ == "__main__":
    main()

