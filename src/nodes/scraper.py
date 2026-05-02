import os
import urllib.parse
from typing import Any, Dict, List

from playwright.sync_api import Page, sync_playwright
from playwright_stealth import Stealth

from src.config import settings
from src.logger import get_logger
from src.state import JobSearchState
from src.utils import normalize_url

logger = get_logger(__name__)

PLATFORM_CONFIG: Dict[str, Dict[str, Any]] = {
    "shixiseng": {
        "name": "实习僧",
        "url_template": "https://www.shixiseng.com/interns?keyword={query}",
        "card_selector": ".intern-wrap, .f-l.intern-detail",
        "next_selectors": [
            "a:has-text('下一页')",
            ".pagination a.next",
            ".page a.next",
        ],
    },
    "nowcoder": {
        "name": "牛客网",
        "url_template": "https://www.nowcoder.com/search/job?query={query}",
        "card_selector": ".job-item, .job-card",
        "next_selectors": [
            "a:has-text('下一页')",
            ".pagination-box a.next",
            ".pagination a.next",
        ],
    },
}


def _scroll_to_load(page: Page) -> None:
    for _ in range(4):
        page.mouse.wheel(0, 2000)
        page.wait_for_timeout(500)


def _extract_cards(page: Page, platform: str, per_page_limit: int) -> List[Dict[str, Any]]:
    config = PLATFORM_CONFIG[platform]
    page_data: List[Dict[str, Any]] = []
    cards = page.locator(config["card_selector"]).all()
    logger.info("当前页捕获 %d 个卡片", len(cards))
    for card in cards[:per_page_limit]:
        try:
            raw_text = card.inner_text(timeout=1500).strip()
            href = card.locator("a").first.get_attribute("href")
            full_url = normalize_url(href, platform)
            if raw_text and full_url:
                page_data.append({
                    "url": full_url,
                    "text": raw_text,
                    "source": config["name"],
                })
        except Exception:
            continue
    return page_data


def _try_click_next(page: Page, platform: str) -> bool:
    config = PLATFORM_CONFIG[platform]
    for sel in config.get("next_selectors", []):
        try:
            btn = page.locator(sel).first
            if btn.count() == 0 or (not btn.is_visible()):
                continue
            cls = (btn.get_attribute("class") or "").lower()
            aria_dis = (btn.get_attribute("aria-disabled") or "").lower()
            if "disabled" in cls or aria_dis == "true":
                continue
            btn.click(timeout=5000)
            page.wait_for_load_state("domcontentloaded", timeout=10000)
            page.wait_for_timeout(1000)
            return True
        except Exception:
            continue
    return False


def _try_url_pagination(page: Page, page_idx: int) -> bool:
    parsed = urllib.parse.urlparse(page.url)
    q = urllib.parse.parse_qs(parsed.query)
    if "page" in q:
        q["page"] = [str(page_idx + 1)]
    elif "p" in q:
        q["p"] = [str(page_idx + 1)]
    else:
        q["page"] = [str(page_idx + 1)]
    next_query = urllib.parse.urlencode(q, doseq=True)
    next_url = urllib.parse.urlunparse(
        (parsed.scheme, parsed.netloc, parsed.path, parsed.params, next_query, parsed.fragment)
    )
    if next_url == page.url:
        return False
    page.goto(next_url, wait_until="domcontentloaded", timeout=15000)
    page.wait_for_timeout(1000)
    return True


def scraper_node(state: JobSearchState) -> Dict[str, Any]:
    current_query = state["current_queries"][0] if state["current_queries"] else "AI Engineer 校招 2026届"
    encoded_query = urllib.parse.quote(current_query)
    raw_platform = state.get("current_platform", "nowcoder")

    max_pages: int = settings.max_pages_per_query
    per_page_limit: int = settings.max_cards_per_page

    current_platform = raw_platform if raw_platform in PLATFORM_CONFIG else "nowcoder"
    config = PLATFORM_CONFIG[current_platform]
    target_url = config["url_template"].format(query=encoded_query)

    scraped_data: List[Dict[str, Any]] = []

    logger.info("正在潜入: %s | 关键词: %s | 最多翻页: %d", config["name"], current_query, max_pages)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=settings.headless,
            args=["--disable-blink-features=AutomationControlled"],
        )
        auth_file = f"auth_state_{current_platform}.json"
        context = (
            browser.new_context(storage_state=auth_file, user_agent=settings.user_agent)
            if os.path.exists(auth_file)
            else browser.new_context(user_agent=settings.user_agent)
        )
        page = context.new_page()

        Stealth().apply_stealth_sync(page)
        page.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        page.route(
            "**/*.{png,jpg,jpeg,gif,svg,mp4,woff,woff2}",
            lambda route: route.abort(),
        )

        try:
            page.goto(target_url, wait_until="domcontentloaded", timeout=20000)
            page.wait_for_selector(
                config["card_selector"], state="visible", timeout=12000
            )

            visited_page_urls: set = set()

            for page_idx in range(1, max_pages + 1):
                current_url = page.url
                if current_url in visited_page_urls:
                    logger.warning("检测到重复页面，提前终止翻页: %s", current_url)
                    break
                visited_page_urls.add(current_url)

                logger.info("正在抓取第 %d/%d 页: %s", page_idx, max_pages, current_url)
                _scroll_to_load(page)
                page.wait_for_timeout(700)

                items = _extract_cards(page, current_platform, per_page_limit)
                scraped_data.extend(items)
                logger.info(
                    "第 %d 页提取 %d 条，累计 %d 条",
                    page_idx,
                    len(items),
                    len(scraped_data),
                )

                if page_idx == max_pages:
                    break

                moved = _try_click_next(page, current_platform)
                if not moved:
                    moved = _try_url_pagination(page, page_idx)
                if not moved:
                    logger.info("无法翻页，结束抓取。")
                    break

            logger.info("抓取结束，总计 %d 条。", len(scraped_data))

        except Exception as e:
            logger.error("抓取受阻: %s", e)

        finally:
            browser.close()

    next_platform = "shixiseng" if current_platform == "nowcoder" else "nowcoder"
    remaining_queries = state["current_queries"][1:]

    return {
        "raw_html_data": scraped_data,
        "current_queries": remaining_queries,
        "current_platform": next_platform,
    }
