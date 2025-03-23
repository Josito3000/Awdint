import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from datetime import datetime
import os
import json
from dataclasses import dataclass
from typing import Optional, List, Dict
import logging
import requests
import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa
from fake_useragent import UserAgent
from pathlib import Path
import signal
import sys
from concurrent.futures import ThreadPoolExecutor

# --- GLOBAL VARS ---
URL = os.getenv("URL")

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class ScraperConfig:
    """Clase para manejar la configuración del scraper"""
    base_url: str = URL
    output_folder: str = "./data"
    start_page: int = 1
    num_pages: int = 8500
    restart_every: int = 25
    delay_between_pages: tuple = (0.5, 1)
    delay_between_listings: tuple = (5, 12)
    timeout: int = 15
    max_retries: int = 3

class CarScraper:
    def __init__(self, config: ScraperConfig):
        self.config = config
        self.ua = UserAgent()
        self.session = requests.Session()
        self._setup_directories()
        self.current_links = []  # Para almacenar enlaces temporalmente
        self.current_car_data = []  # Para almacenar datos de coches temporalmente
        self.setup_signal_handlers()
        
    def setup_signal_handlers(self):
        """Configurar manejadores de señales para interrupciones"""
        signal.signal(signal.SIGINT, self.handle_interrupt)
        signal.signal(signal.SIGTERM, self.handle_interrupt)
        
    def handle_interrupt(self, signum, frame):
        """Manejar interrupciones guardando datos parciales"""
        logging.info("⚠️ Interrupción detectada. Guardando datos parciales...")
        
        try:
            # Guardar enlaces parciales si hay alguno
            if self.current_links:
                self._save_partial_links()
            
            # Guardar datos de coches parciales si hay alguno
            if self.current_car_data:
                self._save_partial_data()
                
            logging.info("✅ Datos parciales guardados exitosamente")
            
        except Exception as e:
            logging.error(f"❌ Error guardando datos parciales: {e}")
        finally:
            # Asegurarse de que el programa termine después de guardar
            os._exit(0)  # Usar os._exit en lugar de sys.exit para asegurar la terminación
            
    def _save_partial_links(self):
        """Guardar enlaces recopilados hasta el momento"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        partial_file = Path(self.config.output_folder) / f"car_links_partial_{timestamp}.txt"
        
        with open(partial_file, "w", encoding="utf-8") as f:
            for link in self.current_links:
                f.write(f"{link}\n")
                
        logging.info(f"Enlaces parciales guardados en: {partial_file}")
        
    def _save_partial_data(self):
        """Guardar datos de coches recopilados hasta el momento"""
        if not self.current_car_data:
            return
            
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        
        try:
            # Convertir a DataFrame
            df = pd.DataFrame(self.current_car_data)
            
            # Asegurar que todas las columnas existan
            required_columns = [
                "URL", "Title", "Price", "Features", "Description", 
                "Kilometers", "Year", "Location", "Seller_Type", 
                "Engine_Type", "Power", "Transmission", "Rate", 
                "Scrape Date", "ListingInfo", "Source File", "Success"
            ]
            
            for col in required_columns:
                if col not in df.columns:
                    df[col] = None
            
            # Guardar en parquet
            partial_file = Path(self.config.output_folder) / f"coches_data_partial_{timestamp}.parquet"
            df.to_parquet(partial_file, engine="pyarrow", index=False)
            logging.info(f"✅ Datos parciales guardados en: {partial_file}")
            
            # Guardar también en CSV como respaldo
            csv_file = Path(self.config.output_folder) / f"coches_data_partial_{timestamp}.csv"
            df.to_csv(csv_file, index=False)
            logging.info(f"✅ Backup guardado en CSV: {csv_file}")
            
            # Mostrar resumen
            logging.info(f"📊 Resumen: Total={len(df)}, Con características={df['Features'].notna().sum()}")
            
        except Exception as e:
            logging.error(f"❌ Error guardando datos: {e}")
            # Intentar guardar en JSON como último recurso
            try:
                json_file = Path(self.config.output_folder) / f"coches_data_partial_{timestamp}.json"
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(self.current_car_data, f, ensure_ascii=False, indent=2)
                logging.info(f"✅ Datos guardados como JSON: {json_file}")
            except Exception as e2:
                logging.error(f"❌ Error guardando JSON: {e2}")

    def _setup_directories(self):
        """Crear directorios necesarios"""
        Path(self.config.output_folder).mkdir(parents=True, exist_ok=True)
        
    def _get_chrome_options(self):
        """Configurar opciones de Chrome"""
        options = uc.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("start-maximized")
        options.add_argument("--disable-extensions")
        options.add_argument("--incognito")
        return options
        
    def _get_headers(self):
        """Generar headers aleatorios"""
        return {
            "User-Agent": self.ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
            "Connection": "keep-alive",
            "DNT": "1",
            "Upgrade-Insecure-Requests": "1"
        }

    def scrape_main_page(self) -> Optional[str]:
        """Scrape la página principal y guardar enlaces"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        file_path = Path(self.config.output_folder) / f"car_links_{timestamp}.txt"
        
        driver = uc.Chrome(options=self._get_chrome_options())
        
        try:
            with open(file_path, "a", encoding="utf-8") as outfile:
                for page in range(self.config.start_page, self.config.num_pages + 1):
                    if not self._scrape_page(driver, page, outfile):
                        break
                    
                    if page % self.config.restart_every == 0:
                        # Guardar enlaces parciales cada cierto número de páginas
                        self._save_partial_links()
                        self.current_links = []  # Limpiar lista temporal
                        time.sleep(random.uniform(2, 3))
                        
            return timestamp
            
        except Exception as e:
            logging.error(f"Error en scraping principal: {e}")
            return None
            
        finally:
            driver.quit()

    def _scrape_page(self, driver, page: int, outfile) -> bool:
        """Scrape una página individual"""
        url = f"{self.config.base_url}?pg={page}"
        logging.info(f"📄 Cargando página {page}: {url}")
        
        try:
            driver.get(url)
            time.sleep(random.uniform(*self.config.delay_between_pages))
            driver.execute_script("document.body.style.zoom='2%'")
            
            html_content = driver.page_source
            
            if "Ups! Parece que algo no va bien..." in html_content:
                logging.warning(f"🚨 Bloqueado en página {page}")
                return False
                
            soup = BeautifulSoup(html_content, "html.parser")
            links = self._extract_links(soup)
            
            if not links:
                logging.warning(f"No se encontraron enlaces en página {page}")
                return True
                
            self._save_links(links, outfile)
            self.current_links.extend(links)  # Guardar enlaces en memoria
            return True
            
        except Exception as e:
            logging.error(f"Error en página {page}: {e}")
            return False

    def _extract_links(self, soup: BeautifulSoup) -> List[str]:
        """Extraer enlaces de la página"""
        links = soup.find_all("a", class_="mt-CardAd-media")
        return [f"https://www.coches.net{link.get('href')}"
                for link in links if link.get("href")]

    def _save_links(self, links: List[str], outfile):
        """Guardar enlaces en archivo"""
        logging.info(f"🔗 Extraídos {len(links)} enlaces")
        for link in links:
            outfile.write(link + "\n")

    def scrape_car_listing(self, car_url: str, source_file: Optional[str] = None) -> Dict:
        """Scrape detalles de un coche individual"""
        # Inicializar diccionario base con valores None
        car_details = {
            "URL": car_url,
            "Title": None,
            "Price": None,
            "Features": None,
            "Description": None,
            "Kilometers": None,
            "Year": None,
            "Location": None,
            "Seller_Type": None,
            "Engine_Type": None,
            #"Power": None,
            "Transmission": None,
            "Rate": None,
            "Scrape Date": datetime.now().strftime("%Y-%m-%d"),
            "ListingInfo": None,
            "Source File": source_file,
            "Success": False
        }
        
        for attempt in range(self.config.max_retries):
            try:
                time.sleep(random.uniform(2, 4))
                
                # Usar Selenium para casos donde requests falla
                if attempt > 1:
                    return self._scrape_with_selenium(car_url, car_details)
                
                headers = {
                    "User-Agent": self.ua.random,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    "Cache-Control": "max-age=0",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
                    "Upgrade-Insecure-Requests": "1",
                    "Pragma": "no-cache"
                }
                
                response = self.session.get(
                    car_url,
                    headers=headers,
                    timeout=self.config.timeout,
                    allow_redirects=True
                )
                
                if "Ups! Parece que algo no va bien..." in response.text:
                    logging.warning(f"🚨 Bloqueado en: {car_url} (intento {attempt + 1})")
                    wait_time = (2 ** attempt) * random.uniform(1, 3)
                    logging.info(f"Esperando {wait_time:.2f} segundos antes del siguiente intento...")
                    time.sleep(wait_time)
                    
                    if attempt > 1:
                        self.session = requests.Session()
                    continue
                
                if response.status_code != 200:
                    logging.warning(f"Código de estado inesperado {response.status_code} para {car_url}")
                    continue
                
                # Intentar obtener los detalles
                details = self._parse_car_details(response.text, car_url, source_file)
                if details:
                    car_details.update(details)
                    car_details["Success"] = True
                    return car_details
                
            except requests.exceptions.RequestException as e:
                logging.error(f"Error de red en {car_url}: {e}")
                time.sleep(2 ** attempt)
            except Exception as e:
                logging.error(f"Error inesperado en {car_url}: {e}")
                if attempt == self.config.max_retries - 1:
                    break
                time.sleep(2 ** attempt)
        
        return car_details

    def _scrape_with_selenium(self, car_url: str, car_details: Dict) -> Dict:
        """Usar Selenium cuando requests falla"""
        try:
            driver = uc.Chrome(options=self._get_chrome_options())
            driver.get(car_url)
            time.sleep(random.uniform(3, 5))
            
            # Scroll para cargar todo el contenido
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            
            html_content = driver.page_source
            details = self._parse_car_details(html_content, car_url, car_details["Source File"])
            
            if details:
                car_details.update(details)
                car_details["Success"] = True
            
            return car_details
            
        except Exception as e:
            logging.error(f"Error usando Selenium para {car_url}: {e}")
            return car_details
        finally:
            if 'driver' in locals():
                driver.quit()

    def _parse_car_details(self, html_content: str, car_url: str, source_file: Optional[str]) -> Dict:
        """Parsear detalles del coche desde HTML"""
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Extraer características específicas
        features_dict = self._extract_features(soup)
        
        # Obtener todas las características como texto
        features_text = self._get_features(soup)
        
        details = {
            "Title": self._get_text(soup, "h1"),
            "Price": self._clean_price(self._get_text(soup, "h3", class_="mt-TitleBasic-title mt-TitleBasic-title--s mt-TitleBasic-title--currentColor")),
            "Features": features_text,  # Guardamos el texto completo de características
            "Description": self._get_text(soup, "div", class_="mt-PanelAdDetails-commentsContent", attrs={"data-testid": "mt-PanelAdDetails-description"}),
            "Rate": self._get_text(soup, "p", class_="mt-RatingBasic-infoValue"),
            "ListingInfo": self._get_text(soup, "p", class_="mt-PanelAdInfo-published"),
            "URL": car_url,
            "Source File": source_file,
            "Scrape Date": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Actualizar con características específicas
        details.update(features_dict)
        
        return details

    def _extract_features(self, soup: BeautifulSoup) -> Dict:
        """Extraer características específicas del coche"""
        features = {}
        
        try:
            # Buscar elementos de características
            feature_items = soup.find_all("li", class_="mt-PanelAdDetails-dataItem")
            
            for item in feature_items:
                text = item.text.strip().lower()
                
                # Extraer kilómetros
                if "km" in text:
                    features["Kilometers"] = self._clean_number(text)
                # Extraer año
                elif "año" in text:
                    features["Year"] = self._clean_number(text)
                # Extraer ubicación
                elif "provincia" in text or "ciudad" in text:
                    features["Location"] = text.split(":")[-1].strip()
                # Extraer tipo de vendedor
                elif "vendedor" in text:
                    features["Seller_Type"] = text.split(":")[-1].strip()
                # Extraer tipo de motor
                elif "combustible" in text:
                    features["Engine_Type"] = text.split(":")[-1].strip()
                # Extraer potencia
                elif "cv" in text or "potencia" in text:
                    features["Power"] = self._clean_number(text)
                # Extraer transmisión
                elif "cambio" in text:
                    features["Transmission"] = text.split(":")[-1].strip()
                
        except Exception as e:
            logging.error(f"Error extrayendo características: {e}")
            
        return features

    def _clean_price(self, price_text: str) -> Optional[int]:
        """Limpiar y convertir precio a número"""
        try:
            if price_text and price_text != "N/A":
                # Eliminar caracteres no numéricos y convertir a entero
                return int(''.join(filter(str.isdigit, price_text)))
        except Exception:
            pass
        return None

    def _clean_number(self, text: str) -> Optional[int]:
        """Extraer número de un texto"""
        try:
            # Encontrar todos los números en el texto
            numbers = ''.join(filter(str.isdigit, text))
            if numbers:
                return int(numbers)
        except Exception:
            pass
        return None

    def _get_text(self, soup: BeautifulSoup, tag: str, **kwargs) -> str:
        """Extraer texto de un elemento"""
        try:
            element = soup.find(tag, **kwargs)
            return element.text.strip() if element else "N/A"
        except Exception:
            return "N/A"

    def _get_features(self, soup: BeautifulSoup) -> str:
        """Extraer características generales del coche"""
        try:
            ul_element = soup.find("ul", class_="mt-PanelAdDetails-data")
            if not ul_element:
                return "N/A"
            
            features = []
            for li in ul_element.find_all("li", class_="mt-PanelAdDetails-dataItem"):
                # Obtener el texto y limpiarlo
                feature_text = li.text.strip()
                if feature_text:
                    features.append(feature_text)
            
            # Unir todas las características con comas
            return ", ".join(features) if features else "N/A"
            
        except Exception as e:
            logging.error(f"Error extrayendo características generales: {e}")
            return "N/A"

    def process_folder(self, folder_path: str, limit_per_file: Optional[int] = None):
        """Procesar todos los archivos de enlaces en una carpeta"""
        start_time = time.time()
        self.current_car_data = []  # Limpiar datos anteriores
        
        try:
            # Obtener solo archivos que empiecen con car_links_ y terminen en .txt
            txt_files = list(Path(folder_path).glob("car_links_*.txt"))
            if not txt_files:
                logging.warning("No se encontraron archivos de enlaces")
                return pd.DataFrame()
            
            # Obtener el archivo más reciente por fecha de modificación
            latest_file = max(txt_files, key=lambda x: x.stat().st_mtime)
            logging.info(f"📄 Procesando el archivo más reciente: {latest_file}")
            
            # Procesar solo el último archivo
            self.current_car_data = self._process_file(latest_file, limit_per_file)
            
            # Guardar los datos en parquet
            if self.current_car_data:
                self._save_to_parquet(self.current_car_data)
            
        except Exception as e:
            logging.error(f"Error procesando archivo: {e}")
            if self.current_car_data:
                self._save_partial_data()
        finally:
            logging.info(f"✅ Scraping completado en {time.time() - start_time:.2f} segundos.")
            return pd.DataFrame(self.current_car_data if self.current_car_data else [])

    def _process_file(self, file_path: Path, limit_per_file: Optional[int]) -> List[Dict]:
        """Procesar un archivo de enlaces individual"""
        car_data = []
        processed_count = 0
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                urls = [line.strip() for line in f.readlines()]
                
            if limit_per_file:
                urls = urls[:limit_per_file]
                
            total_urls = len(urls)
            logging.info(f"📄 Procesando {file_path.name} ({total_urls} enlaces)")
            
            time.sleep(random.uniform(1, 2))
            
            for index, url in enumerate(urls, start=1):
                try:
                    logging.info(f"🔗 Scraping coche {index}/{total_urls} de {file_path.name}: {url}")
                    
                    if index % 20 == 0:
                        self.session = requests.Session()
                        time.sleep(random.uniform(3, 5))
                    
                    details = self.scrape_car_listing(url, str(file_path))
                    if details:
                        car_data.append(details)
                        processed_count += 1
                        
                        # Guardar datos parciales cada 2 registros
                        if processed_count % 2 == 0:
                            self.current_car_data = car_data
                            self._save_partial_data()
                            logging.info(f"💾 Guardados {processed_count} registros parciales")
                            time.sleep(random.uniform(2, 4))
                    
                except Exception as e:
                    logging.error(f"Error procesando URL {url}: {e}")
                    car_data.append({
                        "URL": url,
                        "Title": None,
                        "Price": None,
                        "Features": None,
                        "Description": None,
                        "Kilometers": None,
                        "Year": None,
                        "Location": None,
                        "Seller_Type": None,
                        "Engine_Type": None,
                        "Power": None,
                        "Transmission": None,
                        "Rate": None,
                        "Scrape Date": datetime.now().strftime("%Y-%m-%d"),
                        "ListingInfo": None,
                        "Source File": str(file_path),
                        "Success": False,
                        "Error": str(e)
                    })
                    time.sleep(random.uniform(1, 3))
                
        except Exception as e:
            logging.error(f"Error leyendo archivo {file_path}: {e}")
        finally:
            if car_data:
                self.current_car_data = car_data
                self._save_partial_data()
        
        return car_data

    def _save_to_parquet(self, car_data: List[Dict]):
        """Guardar datos en formato Parquet"""
        df = pd.DataFrame(car_data)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        output_file = Path(self.config.output_folder) / f"coches_data_compiled_{timestamp}.parquet"
        df.to_parquet(output_file, engine="pyarrow", index=False)
        logging.info(f"✅ Datos guardados en: {output_file}")

    def scrape_parallel(self, urls, max_workers=5):
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(self.scrape_car_listing, urls))
        return [r for r in results if r is not None]

    def save_to_database(self, car_data):
        # Implementar guardado en base de datos
        pass

    def _validate_car_data(self, data: Dict) -> bool:
        required_fields = ["Title", "Price", "URL"]
        return all(data.get(field) != "N/A" for field in required_fields)

def main():
    # Configuración desde archivo o variables de entorno
    config = ScraperConfig(
        output_folder="./data",
        num_pages=2,  # menos páginas para pruebas
        delay_between_pages=(1, 2),  # más tiempo entre páginas
        max_retries=5  # más reintentos
    )
    
    scraper = CarScraper(config)
    
    # Ejecutar scraping principal
    if timestamp := scraper.scrape_main_page():
        # Procesar los enlaces recopilados
        scraper.process_folder("./data", limit_per_file=None)

if __name__ == "__main__":
    main() 