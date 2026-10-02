from playwright.sync_api import Page


class ProductsPage:
    URL = "http://127.0.0.1:8000/products"
    def __init__(self, page: Page):
        self.page = page

    # --------------------------------------------------
    # Navigation
    # --------------------------------------------------

    def open(self):
        self.page.goto(self.URL)
        self.page.wait_for_load_state("networkidle")

    def refresh(self):
        self.page.reload()
        self.page.wait_for_load_state("networkidle")

    # --------------------------------------------------
    # Page Information
    # --------------------------------------------------

    def get_title(self):
        return self.page.title()

    def get_url(self):
        return self.page.url

    # --------------------------------------------------
    # Main Page Elements
    # --------------------------------------------------

    @property
    def navbar(self):
        return self.page.locator("nav")

    @property
    def footer(self):
        return self.page.locator("footer")

    @property
    def product_grid(self):
        return self.page.locator("#product_grid")

    @property
    def product_cards(self):
        return self.page.locator("#product_grid .Product")

    # --------------------------------------------------
    # Product Information
    # --------------------------------------------------

    def product_count(self):
        return self.product_cards.count()

    def product_titles(self):
        return self.page.locator(".Product_title").all_inner_texts()

    def product_prices(self):
        return self.page.locator(".price").all_inner_texts()

    def product_images(self):
        return self.page.locator("#product_grid .Product img")

    # --------------------------------------------------
    # Product Actions
    # --------------------------------------------------

    def open_product(self, index=0):
        self.product_cards.nth(index).locator("a").click()
        self.page.wait_for_load_state("networkidle")

    # --------------------------------------------------
    # Category
    # --------------------------------------------------

    @property
    def category_buttons(self):
       return self.page.locator("#category_buttons_div button")

    def category_count(self):
        return self.category_buttons.count()

    def click_category(self, name):
        self.page.get_by_role("button",name=name,).click()
        self.page.wait_for_load_state("networkidle")

    # --------------------------------------------------
    # Filters
    # --------------------------------------------------

    @property
    def filter_popup_button(self):
        return self.page.locator("#filter_popup_button")

    @property
    def filter_popup(self):
        return self.page.locator("#filter_popup")

    @property
    def clear_filter_button(self):
        return self.page.locator("#clear_filter_button")

    def is_filter_popup_visible(self):
        return self.filter_popup.is_visible()

    def open_filter(self):
        self.filter_popup_button.click()

    def close_filter(self):
        self.page.keyboard.press("Escape")

    def clear_filters(self):
        self.clear_filter_button.click()
        self.page.wait_for_load_state("networkidle")

    def apply_filter(self,filter_sub_cats,):
        self.open_filter()
        selected =set()
        for option in self.page.locator('#filter_options_div .dropdown-item').all():
            label = option.locator("label")
            checkbox = option.locator("input")
            text = label.inner_text().strip()
            if text in filter_sub_cats:
                checkbox.check()
                selected.add(text)
            else:
                checkbox.uncheck()
        missing = set(filter_sub_cats) - selected
        #assert not missing, (f"Filter options not found: {missing}")
        self.page.locator("#apply_filter_button").click()
        self.wait_for_products_loaded()
        return selected, missing

    # --------------------------------------------------
    # Sorting
    # --------------------------------------------------

    @property
    def sort_popup_button(self):
        return self.page.locator("#sort_popup_button")

    @property
    def sort_button(self):
        return self.page.locator("#sort_button")
    
    def open_sort(self):
            self.sort_popup_button.click()

    def sort_by(self,value,):
        self.open_sort()
        self.page.locator(f'#sort_radio_{value}').click()
        self.sort_button.click()
        self.page.wait_for_load_state("networkidle")

    # --------------------------------------------------
    # Image Size
    # --------------------------------------------------

    def set_image_size(self,size,):
        self.page.locator(f'#image_size-{size}').check()
        self.page.wait_for_timeout(200)

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    def image_sources(self):
        return self.page.locator("#product_grid .Product img").evaluate_all("(imgs) => imgs.map(i => i.src)")

    def image_alt_text(self):
        return self.page.locator("#product_grid .Product img").evaluate_all("(imgs) => imgs.map(i => i.alt)")

    def visible_text(self):
        return self.page.locator("body").inner_text()

    def javascript_errors(self):
        errors = []
        self.page.on("pageerror",lambda e: errors.append(str(e)))
        return errors
    
    def get_product_ids(self):
        return self.page.locator("#product_grid .Product").evaluate_all("(cards) => cards.map(c => c.id)")
    
    def wait_for_products_loaded(self):
        self.product_cards.first.wait_for()