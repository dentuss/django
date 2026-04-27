import urllib.parse


class Helper:
    """Допоміжний клас для аналізу URL-адрес."""

    def parse_url(self, url: str) -> dict:
        """
        Аналізує URL та виділяє query-string як рядок і як словник параметрів.

        Повертає словник з ключами:
          - 'raw'    : рядок query string (те, що йде після '?'), або '' якщо немає
          - 'params' : словник { ім'я параметра -> значення (або список значень) }
        """
        parsed = urllib.parse.urlparse(url)
        raw_query = parsed.query  # рядок після '?', до '#'

        # Розбираємо рядок у словник; urllib.parse.parse_qs зберігає списки значень
        params_multi = urllib.parse.parse_qs(raw_query, keep_blank_values=True)

        # Спрощуємо: одне значення -> рядок, кілька -> список
        params = {
            key: values[0] if len(values) == 1 else values
            for key, values in params_multi.items()
        }

        return {"raw": raw_query, "params": params}


# ──────────────────────────────────────────────
# Демонстрація роботи класу
# ──────────────────────────────────────────────
if __name__ == "__main__":
    helper = Helper()

    test_urls = [
        "https://example.com/search?q=python&lang=uk&page=2",
        "https://shop.example.com/items?category=books&sort=price&sort=rating",
        "https://api.example.com/v1/users?active=true&role=admin&role=editor&limit=",
        "https://example.com/about",                          # без query string
        "/local/path?debug=1&verbose=true",                   # відносний URL
        "https://example.com/page?encoded=%D0%BF%D1%80%D0%B8%D0%B2%D1%96%D1%82&num=42",
    ]

    for url in test_urls:
        result = helper.parse_url(url)
        print(f"URL    : {url}")
        print(f"  raw    -> {result['raw']!r}")
        print(f"  params -> {result['params']}")
        print()
