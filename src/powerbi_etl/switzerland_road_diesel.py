import time

import pandas as pd
import pyautogui
from memory_profiler import profile
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from powerbi_etl.utils.base_classes import DataExtractor


class SwitzerlandRoadDiesel(DataExtractor):
    URL = "https://app.powerbi.com/view?r=eyJrIjoiMTYxMGJkZDMtM2U4Zi00YmMyLWFhODUtYzgyMDc4OTdhOTkzIiwidCI6IjlkZTFhZmM4LTBlOTQtNDM0ZC1iOWU5LTdhZDMyNzdkMGZjYyIsImMiOjl9"

    x_coordinate = 150
    y_coordinate = 900

    columns = ["date", "benzin", "dieselol", "flugtreibstoffe"]

    description_mapping = {
        "benzin": "Avenergy Suisse: Monthly petrol consumption in Switzerland in t",
        "dieselol": "Avenergy Suisse: Monthly road diesel consumption in Switzerland in t",
        "flugtreibstoffe": "Avenergy Suisse: Monthly aviation fuels consumption in Switzerland in t",
    }
    sid_mapping = {
        "benzin": "avenergy\\petrol",
        "dieselol": "avenergy\\diesel",
        "flugtreibstoffe": "avenergy\\jet",
    }
    energy_product_mapping = {
        "benzin": "gasoline",
        "dieselol": "gasoil",
        "flugtreibstoffe": "kerosene",
    }

    def __init__(self):
        super().__init__()

        # Metadata for the DataFrame.
        self.metadata = {
            "country": "Switzerland",
            "country_iso": "CH",
            "economic_property": "road_diesel_consumption",
            "energy_product": "fuel_consumption",
            "frequency": "monthly",
            "region": "EUR",
            "source": "Avenergy Suisse",
            "unit": "tonnes",
        }

    def extract(self):
        self.logger.info("Initiating the Data Extraction Method.")

        driver = self.selenium_handler.driver
        driver.get(self.URL)

        # Wait for the chart, right-click, and open it as a table.
        chart = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "visual-stackedAreaChart"))
        )
        ActionChains(driver).context_click(chart).perform()
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@title="Show as a table"]'))
        ).click()

        # Move the mouse to the specified location.
        pyautogui.moveTo(self.x_coordinate, self.y_coordinate, duration=1)

        all_rows = []
        count = 0

        # Initialize a variable to store the last row.
        last_row = None

        while True:
            # Scroll down to load more table data.
            table_data = driver.find_elements(
                By.CLASS_NAME, "scrollable-cells-container"
            )

            # Extract data from each row.
            for row in table_data[1:]:
                all_rows.append(row.text.split("\n"))

            # Check if the last row is the same as the previous last row.
            current_last_row = table_data[-1].text.split("\n") if table_data else None
            if current_last_row == last_row:
                self.logger.info(f"Last Row Reached: {current_last_row}")
                break
            last_row = current_last_row

            # Scroll down to 300 units.
            # pyautogui.scroll(-300)  ## To Run Local Tests.

            # Scroll down to 5 units (small scroll).
            pyautogui.scroll(-5)  ## To Run inside Docker.

            # Wait for the page to load more rows.
            time.sleep(0.3)

            count += 1
            self.logger.info(f"count = {count}; rows = {len(all_rows)}")

        driver.quit()

        # Create a DataFrame from the collected rows.
        self.df = pd.DataFrame(all_rows, columns=self.columns)
        self.df.drop_duplicates(inplace=True, ignore_index=True)

    def transform(self):
        self.logger.info("Initiating the Data Transformation Method.")

        self.df = pd.melt(
            self.df, id_vars=["date"], var_name="product", value_name="value"
        )
        self.df["date"] = pd.to_datetime(self.df["date"])
        self.df.loc[:, "value"] = pd.to_numeric(
            self.df["value"]
            .str.replace(",", "", regex=False)
            .str.replace(" ", "", regex=False)
            .str.strip()
            .replace("", pd.NA),
            errors="coerce",
        )
        self.df = self.df.dropna(subset=["value"])
        self.df["description"] = self.df["product"].map(self.description_mapping)
        self.df["series_id"] = self.df["product"].map(self.sid_mapping)
        self.df["energy_product"] = self.df["product"].map(self.energy_product_mapping)
        self.df = self.df.assign(**self.metadata)


@profile
def main():
    obj = SwitzerlandRoadDiesel()
    obj.etl()
