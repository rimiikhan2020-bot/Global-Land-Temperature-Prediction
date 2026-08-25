# 🌍 Global Land Temperature Analysis & Forecasting

Capstone mini-project for NAVTTC's Artificial Intelligence (Machine Learning & Deep Learning) course, Prime Minister's Hunarmand Pakistan Program.

**Author:** Rimsha

## Problem Statement

Long-term land surface temperature change is one of the clearest signals of climate change. This project analyzes over a century of historical monthly city-level temperature records to uncover global, seasonal, and geographic patterns, then builds a supervised model that forecasts a city's future average temperature from its recent temperature history — deployed as a public web app.

## Dataset

[Berkeley Earth — Climate Change: Earth Surface Temperature Data](https://www.kaggle.com/datasets/berkeleyearth/climate-change-earth-surface-temperature-data) (Kaggle), specifically `GlobalLandTemperaturesByCity.csv`: ~8.6M monthly observations, 3,448 cities, 159 countries, 1743–2013.

## Project Pipeline

`Load → Clean → EDA Dashboard → Feature Engineering (lags + rolling means + cyclical month encoding) → Classical ML (Linear Regression, Random Forest, HistGradientBoosting) → Deep Learning (LSTM) → Chronological Evaluation → Multi-Month Forecasting → Streamlit Deployment`

## Repository Structure
