from datetime import date, datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from sheet import upsert_line

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless=new")

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 15)


def wait_until(css):
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, css)))


def get_cards():
    cards = driver.find_elements(
        By.CSS_SELECTOR, "aside.cards__grid__card.produto")
    links = []

    for card in cards:
        link = card.find_element(
            By.CLASS_NAME, "btn-leilao").get_attribute("href")
        links.append(link)

    return links


def get_bids():
    wait_until("#listaDeLances td")

    title = driver.find_element(By.CSS_SELECTOR, ".container-leilao h1").text
    rows = driver.find_elements(By.CSS_SELECTOR, "#listaDeLances tr")

    bids = [r for r in rows if r.find_elements(By.TAG_NAME, "td")]
    bids_number = len(bids)
    date_today = date.today()

    if bids_number:
        last_row = bids[-1]

        last_bid = last_row.find_element(
            By.CSS_SELECTOR, "td:nth-child(1)").text
        user_last_bid = last_row.find_element(
            By.CSS_SELECTOR, "td:nth-child(2)").text

    else:
        last_bid = "Sem Lance"
        user_last_bid = "Sem Usuário"

    return {
        "titulo": title,
        "usuario": user_last_bid,
        "ultimo_lance": last_bid,
        "quantidade_lances": bids_number,
        "data_coleta": date_today,

    }


def get_time():
    temp_elements = driver.find_elements(By.CLASS_NAME, "tempo-completo")

    if not temp_elements:
        return "Sem Data"

    end_time = str(temp_elements[0].get_attribute("data-tempo"))
    end_dt = datetime.fromisoformat(end_time)
    now_dt = datetime.now(end_dt.tzinfo)

    delta = end_dt - now_dt

    if delta.total_seconds() <= 0:
        return "Encerrado"

    days = delta.days
    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60

    return f"Tempo: {days}d {hours}h {minutes}m"


def main():

    driver.get("https://ifgamesleiloes.com/leiloes-ifgames-diversoes/")
    wait_until("aside.cards__grid__card.produto")

    links = get_cards()

    print(f"{len(links)} leilões encontrados")

    for link in links:
        driver.get(link)

        bids_data = get_bids()
        time_left = get_time()

        auction = {
            "titulo": bids_data["titulo"],
            "ultimo_lance": bids_data["ultimo_lance"],
            "quantidade_lances": bids_data["quantidade_lances"],
            "link": link,
            "usuario": bids_data["usuario"],
            "tempo_restante": time_left,
            "data_coleta": bids_data["data_coleta"]
        }

        upsert_line(auction)


main()

driver.quit()
