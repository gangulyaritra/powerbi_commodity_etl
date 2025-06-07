import logging
import time

import pandas as pd
import pyautogui
from memory_profiler import profile
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from powerbi_etl.utils.base_classes import DataExtractor


class CammesaETL(DataExtractor):
    # Website = "https://cammesaweb.cammesa.com/informe-sintesis-mensual/"
    URL = "https://app.powerbi.com/view?r=eyJrIjoiYmFmN2RiMGItMGFhZC00M2UzLWJmYjAtMTdkNjE2M2EzOTNjIiwidCI6Ijk3NjQ0NjEyLTM3MWMtNGUzNC1hYzc1LTZlNmE1NGFmNDQyOSIsImMiOjR9"

    x_coordinate = 75
    y_coordinate = 1200

    POWERBI_TABLES = ("DEMANDA", "GENERACIÓN", "COMBUSTIBLES")

    def __init__(self):
        super().__init__()

    @staticmethod
    def show_table_from_chart(
        driver,
        button_text: str,
        chart_class_name: str = "visual-columnChart",
        timeout: int = 10,
    ) -> bool:
        """
        Clicks a button to display a table from a Power BI chart and waits for the table to load.

        Parameters:
            - driver (selenium.webdriver): A Selenium WebDriver instance with the page loaded.
            - button_text (str): The text of the button to click to show the table.
            - chart_class_name (str): The class name of the chart element to interact with.
            - timeout (int): Maximum time to wait for elements to become clickable or present.

        Returns:
            - bool: True if the table was successfully displayed, False otherwise.
        """
        try:
            # Locate and click the button with the provided text.
            WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        f'//div[@role="button" and .//div[text()="{button_text}"]]',
                    )
                )
            ).click()

            # Wait for the chart element using the provided class name.
            chart = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CLASS_NAME, chart_class_name))
            )

            # Perform a context (right) and click on the chart if specified.
            ActionChains(driver).context_click(chart).perform()

            # Locate and click on the "Show as a table" button.
            WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//button[@title="Show as a table"]')
                )
            ).click()

            return True
        except TimeoutException as e:
            logging.error(f"Element not found within {timeout} seconds: {e}")
            return False

    @staticmethod
    def scrape_powerbi_table(
        driver,
        x_coordinate: int = 100,
        y_coordinate: int = 1000,
        scroll_amount: int = -100,
        data_columns: list = ["date", "value"],
        header_skip_count: int = 3,
    ) -> pd.DataFrame:
        """
        Scrolls through and scrapes a dynamically loaded Power BI table from a webpage.

        Parameters:
            - driver (selenium.webdriver): A Selenium WebDriver instance with the page loaded.
            - x_coordinate (int): X pixel-coordinate to move the mouse to before scrolling.
            - y_coordinate (int): Y pixel-coordinate to move the mouse to before scrolling.
            - scroll_amount (int): Scroll increment per iteration (negative scrolls down).
            - data_columns (list): List of column names for the resulting DataFrame.
            - header_skip_count (int): Number of initial elements (typically headers) to skip.

        Returns:
            - pd.DataFrame: A DataFrame of unique rows scraped from the table.
        """
        pyautogui.moveTo(x_coordinate, y_coordinate, duration=1)

        scraped_rows = []
        last_row = None
        iterations = 0

        while True:
            table_data = driver.find_elements(
                By.CLASS_NAME, "scrollable-cells-container"
            )
            if not table_data:
                raise ValueError("No table data found; Stopping the Scraping.")

            # Process each visible row, skipping header elements.
            for row in table_data[header_skip_count:]:
                scraped_rows.append(row.text.split("\n"))

            # Use the last element on this iteration to check if further scrolling is needed.
            current_last_row = table_data[-1].text.split("\n")

            if current_last_row == last_row:
                print(f"Last Row Reached: {current_last_row}")
                break

            last_row = current_last_row
            pyautogui.scroll(scroll_amount)  # Scroll the element.
            time.sleep(0.3)
            iterations += 1

        # Back to the Main Menu.
        driver.find_element(By.CLASS_NAME, "menuItem").click()

        # Create DataFrame and remove any duplicates.
        df = pd.DataFrame(scraped_rows, columns=data_columns)
        df.drop_duplicates(inplace=True, ignore_index=True)
        print(f"Scraped {len(df)} rows after {iterations} iterations.")
        return df

    def extract(self):
        self.logger.info("Initiating the Data Extraction Method.")

        driver = self.selenium_handler.driver
        driver.get(self.URL)

        for table_name in self.POWERBI_TABLES:
            try:
                self.logger.info(
                    f"Attempting to display the Power BI {table_name} table from the chart."
                )
                if self.show_table_from_chart(driver, button_text=table_name):
                    try:
                        self.logger.info(
                            f"Successfully displayed the Power BI {table_name} table from the chart."
                        )
                        table_df = self.scrape_powerbi_table(
                            driver,
                            x_coordinate=self.x_coordinate,
                            y_coordinate=self.y_coordinate,
                            # scroll_amount=-100,  ## To Run Local Tests.
                            scroll_amount=-5,  ## To Run inside Docker.
                            data_columns=["date", "value"],
                            header_skip_count=3,
                        )
                        table_df["series_id"] = table_name
                        self.df = pd.concat([self.df, table_df], ignore_index=True)
                    except Exception as e:
                        raise ValueError(
                            f"Failed to scrape the Power BI {table_name} table from the chart."
                        ) from e
            except Exception as e:
                self.logger.error(
                    f"Error displaying the Power BI {table_name} table: {e}"
                )

        driver.quit()

    def transform(self):
        self.logger.info("Initiating the Data Transformation Method.")

        self.df["date"] = pd.to_datetime(self.df["date"])

        self.df.loc[:, "value"] = pd.to_numeric(
            self.df["value"]
            .str.replace(",", "", regex=False)
            .str.replace(" ", "", regex=False)
            .str.strip()
            .replace("", pd.NA),
            errors="coerce",
        )


@profile
def main():
    obj = CammesaETL()
    obj.etl()
