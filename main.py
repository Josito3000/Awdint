from Packages import CochesNet

def main():

    CochesNet.ScrapeMainPageListings_Selenium_ListFileOutput(base_url="https://www.coches.net/concesionario/stellantisandyoubarcelonabadal") 
    #CochesNet.scrape_folder_links("C:/Users/PORTATIL/OneDrive/Documentos/Projects/CochecitosScrapping/CarLinks")


if __name__ == "__main__":
    main()   