from Packages import CochesNet
import time
from config import BASE_URL  # Import the hidden URL

def main():
    # time.sleep(600)

    for i in range(1, 10):
        CochesNet.ScrapeMainPageListings_Selenium_ListFileOutput(base_url=BASE_URL, start_page=100 * i)

        for j in range(5, 0, -1):
            print(f"{j * 10} minutes left")
            time.sleep(600)

    CochesNet.scrape_folder_links("C:/Users/PORTATIL/OneDrive/Documentos/Projects/CochecitosScrapping/CarLinks2")

if __name__ == "__main__":
    main()
