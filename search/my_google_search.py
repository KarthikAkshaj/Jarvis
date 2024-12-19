import webbrowser


class GoogleSearch:
    @staticmethod
    def perform_search(item: str):
        url = f"https://www.google.com/search?q={item}"
        webbrowser.open(url)
        print(f"Searching for '{item}' in Google...")
