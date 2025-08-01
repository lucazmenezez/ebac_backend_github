import asyncio
import aiohttp
import csv
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

BASE_URL = "https://www.imdb.com"

# ======== Função para buscar detalhes do filme =========
async def fetch_movie_details(session, movie_link):
    async with session.get(movie_link, headers=headers) as response:
        html = await response.text()
        soup = BeautifulSoup(html, 'html.parser')

        # --- Extrai Título ---
        title_tag = soup.select_one('h1[data-testid="hero-title-block__title"], h1')
        title = title_tag.get_text(strip=True) if title_tag else "N/A"

        # --- Extrai Data ---
        date_tag = soup.select_one('li[data-testid="title-details-releasedate"] a')
        if not date_tag:
            date_tag = soup.select_one('ul[data-testid="hero-title-block__metadata"] li')
        date = date_tag.get_text(strip=True) if date_tag else "N/A"

        # --- Extrai Nota ---
        rating_tag = soup.select_one('div[data-testid="hero-rating-bar__aggregate-rating__score"] span')
        rating = rating_tag.get_text(strip=True) if rating_tag else "N/A"

        # --- Extrai Sinopse ---
        plot_tag = soup.select_one('span[data-testid="plot-xl"], span[data-testid="plot-l"]')
        plot = plot_tag.get_text(strip=True) if plot_tag else "N/A"

        # Salvar no CSV
        async with asyncio.Lock():
            with open('movies_async.csv', 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([title, date, rating, plot])

        print(f"✔ {title} | {date} | {rating}")

# ======== Função para buscar a lista de filmes =========
async def fetch_movies_list(session):
    url = f"{BASE_URL}/chart/moviemeter/"
    async with session.get(url, headers=headers) as response:
        html = await response.text()
        soup = BeautifulSoup(html, 'html.parser')
        movies_list = soup.select('ul.ipc-metadata-list li.ipc-metadata-list-summary-item')
        movie_links = [BASE_URL + m.select_one('a')['href'] for m in movies_list if m.select_one('a')]
        print(f"🔗 {len(movie_links)} filmes encontrados!")
        return movie_links

# ======== Função Principal =========
async def main():
    async with aiohttp.ClientSession() as session:
        movie_links = await fetch_movies_list(session)

        tasks = [fetch_movie_details(session, link) for link in movie_links]
        await asyncio.gather(*tasks)

# ======== Execução =========
if __name__ == "__main__":
    # Cria CSV com cabeçalho
    with open('movies_async.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Título', 'Data', 'Nota', 'Sinopse'])

    asyncio.run(main())
