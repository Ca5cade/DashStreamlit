import pandas as pd
import numpy as np
from datetime import datetime
import warnings
import os
import traceback

def load_data():
    """Load and preprocess the dataset"""
    try:
        csv_path = "res.csv"
        
        if os.path.exists(csv_path):
            try:
                print("Loading CSV file...")
                data = pd.read_csv(csv_path)
                print("Successfully loaded CSV file")
                
                # Convert date columns to datetime
                if 'DATE' in data.columns:
                    data['DATE'] = pd.to_datetime(data['DATE'])
                
                # Map the actual columns to our expected structure
                data['Chaine'] = data['IDChaineMontage']
                data['Operation'] = data['Operation']  # Already exists
                data['Controleur'] = data['IDControleur']
                data['Quantite'] = data['Qtte']
                
                # Calculate CNQ components
                # Retouche (rework) based on NbrReclamations
                if 'NbrReclamations' in data.columns:
                    rework_cost = 50  # Cost per rework
                    data['Retouche'] = data['NbrReclamations'] * rework_cost
                else:
                    data['Retouche'] = 0
                
                # Rebut (scrap) based on DeuxiemeChoix (second choice/defective items)
                if 'DeuxiemeChoix' in data.columns:
                    scrap_cost = 100  # Cost per scrapped item
                    data['Rebut'] = data['DeuxiemeChoix'].fillna(0) * scrap_cost
                else:
                    data['Rebut'] = 0
                
                # Penalite (penalties) based on Note (assuming it represents penalty score)
                if 'Note' in data.columns:
                    penalty_cost = 75  # Cost per penalty point
                    data['Penalite'] = data['Note'].fillna(0) * penalty_cost
                else:
                    data['Penalite'] = 0
                
                # Calculate total CNQ
                data['CNQ'] = data['Retouche'] + data['Rebut'] + data['Penalite']
                
                # Calculate CNQ percentage using ValeurOF (OF value) if available
                if 'ValeurOF' in data.columns:
                    data['CNQ_Percentage'] = (data['CNQ'] / data['ValeurOF'].replace(0, np.nan)) * 100
                else:
                    # Fallback to using quantity with assumed unit price
                    unit_price = 100  # Assumed price per unit
                    total_value = data['Quantite'] * unit_price
                    data['CNQ_Percentage'] = (data['CNQ'] / total_value) * 100
                
                # Fill NaN values with 0
                data = data.fillna(0)
                
                # Get reference data
                if 'Operation' in data.columns:
                    data['Operation'] = data['Operation'].fillna('Unknown')
                if 'Libelle' in data.columns:
                    data['OperationName'] = data['Libelle']
                
                print(f"Data loaded successfully: {data.shape[0]} rows, {data.shape[1]} columns")
                print("Available columns:", data.columns.tolist())
                return data
                
            except Exception as e:
                print(f"Error loading CSV: {str(e)}")
                print(traceback.format_exc())
                return create_sample_data()
        else:
            print("CSV file not found, creating sample data")
            return create_sample_data()
            
    except Exception as e:
        print(f"Unexpected error in load_data: {str(e)}")
        print(traceback.format_exc())
        return create_sample_data()

def create_sample_data():
    """Create sample data for testing"""
    # Create date range
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    n_rows = len(dates)
    
    # Create sample data
    data = pd.DataFrame({
        'DATE': dates,
        'Chaine': np.random.choice(['CH1', 'CH2', 'CH3'], n_rows),
        'Operation': np.random.choice(['OP1', 'OP2', 'OP3', 'OP4'], n_rows),
        'Controleur': np.random.choice(['CTR1', 'CTR2', 'CTR3'], n_rows),
        'Quantite': np.random.randint(100, 1000, n_rows),
        'NbrReclamations': np.random.poisson(2, n_rows),
        'DeuxiemeChoix': np.random.binomial(1, 0.05, n_rows),
        'Note': np.random.randint(0, 5, n_rows)
    })
    
    # Calculate CNQ components
    rework_cost = 50
    scrap_cost = 100
    penalty_cost = 75
    
    data['Retouche'] = data['NbrReclamations'] * rework_cost
    data['Rebut'] = data['DeuxiemeChoix'] * scrap_cost
    data['Penalite'] = data['Note'] * penalty_cost
    data['CNQ'] = data['Retouche'] + data['Rebut'] + data['Penalite']
    
    # Calculate CNQ percentage
    unit_price = 100  # Assumed price per unit
    total_value = data['Quantite'] * unit_price
    data['CNQ_Percentage'] = (data['CNQ'] / total_value) * 100
    
    return data

def get_filter_options(data):
    """Get unique values for filter dropdowns"""
    options = {}
    
    categorical_columns = ['Chaine', 'Operation', 'Controleur']
    for col in categorical_columns:
        if col in data.columns:
            options[col] = sorted(data[col].dropna().unique())
    
    return options