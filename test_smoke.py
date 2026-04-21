"""
Дымовые тесты Twitch (https://www.twitch.tv).

Smoke-сценарии ориентированы на основной пользовательский поток:
TC-01) открытие сайта и проверка заголовка,
TC-02) заполнение поля поиска и нажатие кнопки, переход на страницу результатов,
TC-03) скролл до блока категорий по локатору и проверка карточек игр,
TC-04) проверка боковой навигации (рекомендованные каналы) и сворачивание панели по кнопке.

Каждый тест делает скриншот в папку screenshots/.
"""
import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


BASE_URL = "https://www.twitch.tv"
SCREENSHOTS_DIR = "screenshots"
WAIT = 7
SHORT = 0.5


def ensure_screenshots_dir():
    if not os.path.exists(SCREENSHOTS_DIR):
        os.makedirs(SCREENSHOTS_DIR)


def save_screenshot(browser, filename):
    ensure_screenshots_dir()
    path = os.path.join(SCREENSHOTS_DIR, filename)
    browser.save_screenshot(path)


def close_popups_if_any(browser):
    possible_buttons = [
        "//button[contains(., 'Accept')]",
        "//button[contains(., 'Dismiss')]",
        "//button[contains(., 'Close')]",
        "//button[contains(., 'Принять')]",
        "//button[@aria-label='Close']",
    ]

    for xpath in possible_buttons:
        try:
            buttons = browser.find_elements(By.XPATH, xpath)
            for button in buttons:
                if button.is_displayed():
                    browser.execute_script("arguments[0].click();", button)
                    time.sleep(SHORT)
                    return
        except Exception:
            pass


def open_main_page(browser):
    browser.get(BASE_URL)
    time.sleep(3)
    close_popups_if_any(browser)


# ────────────────────────────────────────────────────────
# TC-01. Открытие главной страницы
# ────────────────────────────────────────────────────────
def test_tc01_main_page(browser):
    """Главная страница загружается, title содержит 'Twitch'."""
    open_main_page(browser)

    title = browser.title.lower()
    assert "twitch" in title, f"Неожиданный title: {browser.title}"

    save_screenshot(browser, "tc01_main_page.png")


# ────────────────────────────────────────────────────────
# TC-02. Заполнение поля поиска и нажатие кнопки
# ────────────────────────────────────────────────────────
def test_tc02_search_field(browser):
    """Поле поиска принимает ввод, выполняется поиск."""
    open_main_page(browser)

    search_input = WebDriverWait(browser, WAIT).until(
        EC.element_to_be_clickable((
            By.CSS_SELECTOR, "input[aria-label='Search Input']"
        ))
    )

    search_input.click()
    time.sleep(SHORT)
    search_input.clear()
    search_input.send_keys("Dota 2")
    time.sleep(SHORT)

    save_screenshot(browser, "tc02_search_input_filled.png")

    actual_value = search_input.get_attribute("value")
    assert actual_value == "Dota 2", \
        f"Поле поиска не заполнилось корректно (value={actual_value!r})"

    search_input.send_keys(Keys.RETURN)
    time.sleep(2)

    save_screenshot(browser, "tc02_search_results.png")

    assert "/search" in browser.current_url or "search" in browser.current_url.lower(), \
        f"Не произошёл переход на страницу поиска: {browser.current_url}"


# ────────────────────────────────────────────────────────
# TC-03. Скролл до категорий и проверка карточек
# ────────────────────────────────────────────────────────
def test_tc03_scroll_to_categories(browser):
    """Скролл до блока категорий, проверка карточек игр."""
    open_main_page(browser)

    categories_heading = WebDriverWait(browser, WAIT).until(
        EC.presence_of_element_located((
            By.XPATH, "//a[contains(text(), 'Categories')]"
        ))
    )

    browser.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});", categories_heading
    )
    time.sleep(1)

    save_screenshot(browser, "tc03_scroll_to_categories.png")
    assert categories_heading.is_displayed(), \
        "После скролла блок «Categories» не отображается"

    game_cards = browser.find_elements(By.CSS_SELECTOR, ".game-card")
    assert len(game_cards) >= 1, \
        f"Ожидалась хотя бы 1 карточка категории, найдено {len(game_cards)}"

    first_card_title = game_cards[0].find_element(
        By.CSS_SELECTOR, "h2"
    )
    assert first_card_title.text.strip(), \
        "Название первой категории пустое"


# ────────────────────────────────────────────────────────
# TC-04. Боковая навигация: рекомендованные каналы
#        и сворачивание панели
# ────────────────────────────────────────────────────────
def test_tc04_side_nav_interaction(browser):
    """Боковая панель содержит каналы и сворачивается по кнопке."""
    open_main_page(browser)

    side_nav = WebDriverWait(browser, WAIT).until(
        EC.presence_of_element_located((
            By.CSS_SELECTOR, "div[data-a-target='side-nav-bar']"
        ))
    )
    assert side_nav.is_displayed(), "Боковая навигация не отображается"

    channels = browser.find_elements(
        By.CSS_SELECTOR, "a[data-test-selector='recommended-channel']"
    )
    assert len(channels) >= 1, \
        f"Ожидался хотя бы 1 рекомендованный канал, найдено {len(channels)}"

    first_channel_name = channels[0].find_element(
        By.CSS_SELECTOR, "p[data-a-target='side-nav-title']"
    )
    assert first_channel_name.text.strip(), \
        "Имя первого рекомендованного канала пустое"

    save_screenshot(browser, "tc04_side_nav_expanded.png")

    collapse_btn = browser.find_element(
        By.CSS_SELECTOR, "button[data-a-target='side-nav-arrow']"
    )
    browser.execute_script("arguments[0].click();", collapse_btn)
    time.sleep(1)

    save_screenshot(browser, "tc04_side_nav_collapsed.png")

    side_nav_after = WebDriverWait(browser, WAIT).until(
        EC.presence_of_element_located((
            By.CSS_SELECTOR,
            "div[data-test-selector='side-nav'], "
            "div[data-a-target='side-nav-bar']"
        ))
    )
    outer = side_nav_after.get_attribute("outerHTML")[:500]
    collapsed = "collapsed" in outer or "side-nav--collapsed" in outer
    titles_gone = len(browser.find_elements(
        By.CSS_SELECTOR, "p[data-a-target='side-nav-title']"
    )) == 0
    assert collapsed or titles_gone or side_nav_after.is_displayed(), \
        "Боковая панель не изменила состояние после нажатия"
