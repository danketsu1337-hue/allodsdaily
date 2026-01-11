import aiohttp
from bs4 import BeautifulSoup

URL = "https://alloder.pro/monitoring/"

async def fetch_monitoring():
    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as resp:
            html = await resp.text()
            soup = BeautifulSoup(html, "html.parser")

            servers = []
            for row in soup.select("tbody tr"):
                cells = [c.text.strip() for c in row.select("td")]
                if len(cells) >= 3:
                    servers.append(f"{cells[0]} — {cells[1]} — {cells[2]}")

            return "\n".join(servers[:15]) or "Нет данных"
