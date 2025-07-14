import pandas as pd
import numpy as np
from datetime import datetime
import os
import requests
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data_processing.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class COVIDDataProcessor:
    """
    Class to fetch and process COVID-19 data from Our World in Data.
    """
    
    def __init__(self, data_dir='../data'):
        """
        Initialize the data processor.
        
        Args:
            data_dir (str): Directory to save processed data.
        """
        self.data_dir = data_dir
        self.data_url = 'https://covid.ourworldindata.org/data/owid-covid-data.csv'
        self.processed_file = os.path.join(data_dir, 'processed_covid_data.csv')
        self.last_updated_file = os.path.join(data_dir, 'last_updated.txt')
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
    
    def fetch_data(self):
        """
        Fetch the latest COVID-19 data from Our World in Data.
        
        Returns:
            pandas.DataFrame: Raw COVID-19 data.
        """
        logger.info(f"Fetching data from {self.data_url}")
        try:
            df = pd.read_csv(self.data_url)
            logger.info(f"Data fetched successfully. Shape: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            raise
    
    def clean_data(self, df):
        """
        Clean and preprocess the COVID-19 data.
        
        Args:
            df (pandas.DataFrame): Raw COVID-19 data.
            
        Returns:
            pandas.DataFrame: Cleaned COVID-19 data.
        """
        logger.info("Cleaning and preprocessing data")
        
        # Convert date column to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Select relevant columns
        columns_to_keep = [
            'iso_code', 'continent', 'location', 'date', 
            'total_cases', 'new_cases', 'total_deaths', 'new_deaths',
            'total_cases_per_million', 'new_cases_per_million',
            'total_deaths_per_million', 'new_deaths_per_million',
            'reproduction_rate', 'icu_patients', 'hosp_patients',
            'total_tests', 'new_tests', 'total_vaccinations',
            'people_vaccinated', 'people_fully_vaccinated',
            'new_vaccinations', 'population', 'population_density',
            'median_age', 'gdp_per_capita', 'hospital_beds_per_thousand',
            'people_fully_vaccinated_per_hundred'
        ]
        
        # Only keep columns that exist in the dataframe
        columns_to_keep = [col for col in columns_to_keep if col in df.columns]
        df = df[columns_to_keep].copy()
        
        # Rename location to country for clarity
        df = df.rename(columns={'location': 'country'})
        
        # Fill missing values with appropriate methods
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        for col in numeric_cols:
            # For cumulative columns like total_cases, forward fill
            if col.startswith('total_'):
                df[col] = df.groupby('country')[col].fillna(method='ffill')
            # For rate columns, use median by country
            elif col.endswith('_rate') or col.endswith('_density'):
                df[col] = df.groupby('country')[col].transform(
                    lambda x: x.fillna(x.median())
                )
        
        # Drop rows with missing critical data
        critical_cols = ['iso_code', 'country', 'date']
        df = df.dropna(subset=critical_cols)
        
        logger.info(f"Data cleaned successfully. Shape after cleaning: {df.shape}")
        return df
    
    def process_data(self):
        """
        Main method to fetch, process, and save COVID-19 data.
        
        Returns:
            pandas.DataFrame: Processed COVID-19 data.
        """
        # Fetch data
        raw_data = self.fetch_data()
        
        # Clean data
        processed_data = self.clean_data(raw_data)
        
        # Save processed data
        self.save_data(processed_data)
        
        return processed_data
    
    def save_data(self, df):
        """
        Save processed data to CSV and update last updated timestamp.
        
        Args:
            df (pandas.DataFrame): Processed COVID-19 data to save.
        """
        logger.info(f"Saving processed data to {self.processed_file}")
        
        # Save to CSV
        df.to_csv(self.processed_file, index=False)
        
        # Update last updated timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.last_updated_file, 'w') as f:
            f.write(timestamp)
        
        logger.info(f"Data saved successfully. Last updated: {timestamp}")

if __name__ == "__main__":
    processor = COVIDDataProcessor()
    processor.process_data()