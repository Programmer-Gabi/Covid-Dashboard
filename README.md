# COVID-19 Trends Dashboard

An interactive Streamlit dashboard to visualize and analyze COVID-19 data trends worldwide. This project includes a data processing pipeline, interactive visualizations, and automated daily updates via GitHub Actions.

## Features

- **Interactive Dashboard**: Filter data by countries, dates, and metrics
- **Multiple Views**: Overview, Time Series Analysis, Country Comparison, Vaccination Progress
- **Live Data**: Data is fetched from Our World in Data's COVID-19 dataset
- **Automated Updates**: Daily scheduled data updates via GitHub Actions
- **Data Pipeline**: Jupyter notebook with exploratory analysis and processing
- **Responsive Design**: Custom themed UI that works on various devices

## Project Structure

```
├── requirements.txt           # Project dependencies
├── covid_dashboard/          
│   ├── app.py                 # Streamlit dashboard application
│   ├── covid_data_pipeline.ipynb  # Data pipeline notebook
│   ├── data/                  # Processed data directory
│   └── scripts/               
│       └── data_processor.py  # Data processing utilities
└── .github/
    └── workflows/
        └── update_covid_data.yml  # GitHub Actions workflow for daily updates
```

## Setup and Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-directory>
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the data pipeline to fetch and process the data:
```bash
cd covid_dashboard
jupyter notebook covid_data_pipeline.ipynb
```
   Run all cells in the notebook to fetch and process the data.

4. Start the Streamlit dashboard:
```bash
cd covid_dashboard
streamlit run app.py
```

## Data Sources

This dashboard uses data from [Our World in Data COVID-19 dataset](https://github.com/owid/covid-19-data/tree/master/public/data), which is updated daily and contains data on confirmed cases, deaths, hospitalizations, testing, and vaccinations.

## Customization

You can customize the dashboard by:

1. Modifying the theme in `app.py` (look for the `local_css` function)
2. Adding new views or metrics to display
3. Adjusting the data processing steps in `data_processor.py`

## Automated Updates

The project uses GitHub Actions to update the COVID-19 data daily. The workflow is defined in `.github/workflows/update_covid_data.yml` and runs the data processor script each day.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Data provided by [Our World in Data](https://ourworldindata.org/)
- Built with [Streamlit](https://streamlit.io/), [Pandas](https://pandas.pydata.org/), and [Plotly](https://plotly.com/)