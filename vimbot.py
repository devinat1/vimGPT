import time
from io import BytesIO
from PIL import Image
from playwright.sync_api import sync_playwright
from time import sleep

vimium_path = "./vimium-master"

class Vimbot:
    def __init__(self, headless=False):
        self.context = (
            sync_playwright()
            .start()
            .chromium.launch_persistent_context(
                "",
                headless=headless,
                args=[
                    f"--disable-extensions-except={vimium_path}",
                    f"--load-extension={vimium_path}",
                ],
                ignore_https_errors=True,
            )
        )

        self.page = self.context.new_page()
        self.page.set_viewport_size({"width": 1080, "height": 720})
        self.inject_xpath_capture_script()

    def inject_xpath_capture_script(self):
        script = """
        if (!window.xpathTrackingInjected) {
            window.clickedElementsData = []; // Global array to store XPaths and class names
            document.addEventListener('click', function(event) {
                var element = event.target;
                var xpath = generateXpath(element);
                var className = element.className;
                var data = xpath + ',' + className; // Combine XPath and class name
                window.clickedElementsData.push(data); // Append data to global array
            }, true);

            function generateXpath(element) {
                var path = [];
                while (element.nodeType === Node.ELEMENT_NODE) {
                    var index = 1;
                    for (var sibling = element.previousSibling; sibling; sibling = sibling.previousSibling) {
                        if (sibling.nodeType === Node.DOCUMENT_TYPE_NODE)
                            continue;
                        if (sibling.nodeName === element.nodeName)
                            ++index;
                    }
                    var tagName = element.nodeName.toLowerCase();
                    var pathIndex = '[' + index + ']';
                    path.unshift(tagName + pathIndex);
                    element = element.parentNode;
                }
                return path.length ? '/' + path.join('/') : null;
            }
            window.xpathTrackingInjected = true;
        }
        """
        self.page.add_init_script(script)

    def perform_action(self, action):
        if "done" in action:
            return True
        if "click" in action and "type" in action:
            self.click(action["click"])
            self.type(action["type"])
        if "navigate" in action:
            self.navigate(action["navigate"])
        elif "type" in action:
            self.type(action["type"])
        elif "click" in action:
            self.click(action["click"])

    def navigate(self, url):
        self.page.goto(url=url if "://" in url else "https://" + url, timeout=60000)

    def type(self, text):
        time.sleep(1)
        self.page.keyboard.type(text)
        self.page.keyboard.press("Enter")

    def click(self, text):
        self.page.keyboard.type(text)
        sleep(5)
        print("Getting clicked xpaths...")
        clicked_xpaths = self.get_clicked_xpaths()
        print(f"Clicked XPaths: {clicked_xpaths}")

    def capture(self):
        # capture a screenshot with vim bindings on the screen
        self.page.keyboard.press("Escape")
        self.page.keyboard.type("f")

        screenshot = Image.open(BytesIO(self.page.screenshot())).convert("RGB")
        return screenshot

    def get_clicked_xpaths(self):
        script = "window.clickedElementsData;"
        res = self.page.evaluate(script)
        return res
