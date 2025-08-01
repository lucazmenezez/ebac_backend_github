import requests
import time
import csv
import random
import concurrent.futures
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

MAX_THREADS = 10


def extract_movie_details(movie_link):
    """Extrai título, data, nota e sinopse de cada filme"""
    time.sleep(random.uniform(0, 0.3))
    response = requests.get(movie_link, headers=headers)
    movie_soup = BeautifulSoup(response.content, 'html.parser')

    if movie_soup:
        # --- Título ---
        title_tag = movie_soup.select_one('h1[data-testid="hero-title-block__title"], h1')
        title = title_tag.get_text(strip=True) if title_tag else "N/A"

        # --- Data de lançamento ---
        date_tag = movie_soup.select_one('li[data-testid="title-details-releasedate"] a')
        if not date_tag:
            # fallback: pega do metadata
            date_tag = movie_soup.select_one('ul[data-testid="hero-title-block__metadata"] li')
        date = date_tag.get_text(strip=True) if date_tag else "N/A"

        # --- Nota IMDb ---
        rating_tag = movie_soup.select_one('div[data-testid="hero-rating-bar__aggregate-rating__score"] span')
        rating = rating_tag.get_text(strip=True) if rating_tag else "N/A"

        # --- Sinopse ---
        plot_tag = movie_soup.select_one('span[data-testid="plot-xl"], span[data-testid="plot-l"]')
        plot = plot_tag.get_text(strip=True) if plot_tag else "N/A"

        # --- Salvar no CSV ---
        with open('movies.csv', 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([title, date, rating, plot])

        print(f"✔ {title} | {date} | {rating}")


def extract_movies(soup):
    """Extrai os links dos filmes mais populares"""
    movies_list = soup.select('ul.ipc-metadata-list li.ipc-metadata-list-summary-item')
    movie_links = ['https://imdb.com' + m.select_one('a')['href'] for m in movies_list if m.select_one('a')]

    print(f"🔗 {len(movie_links)} filmes encontrados!")

    threads = min(MAX_THREADS, len(movie_links))
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(extract_movie_details, movie_links)


def main():
    start_time = time.time()

    url = 'https://www.imdb.com/chart/moviemeter/'
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    extract_movies(soup)

    print(f"⏳ Tempo total: {time.time() - start_time:.2f} segundos")


if __name__ == '__main__':
    with open('movies.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Título', 'Data', 'Nota', 'Sinopse'])

    main()
