from flask import Flask, render_template
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

app = Flask(__name__)

# Function to create and save visualizations if they don't already exist
def create_visualizations():
    # Check if the plots are already generated
    if all(os.path.exists(f'static/plot{i}.png') for i in range(1, 6)):
        return  # Skip generation if files exist

    # Load the dataset
    diabetes_df = pd.read_csv('diabetes.csv')  # Ensure 'diabetes.csv' is in the same directory

    # Ensure static directory exists
    os.makedirs('static', exist_ok=True)

    sns.set(style='whitegrid')

    # 1. Distribution of Glucose Levels
    plt.figure(figsize=(10, 6))
    sns.histplot(diabetes_df['Glucose'], bins=30, kde=True, color='skyblue')
    plt.title('Distribution of Glucose Levels')
    plt.xlabel('Glucose Level')
    plt.ylabel('Frequency')
    plt.savefig('static/plot1.png')
    plt.close()

    # 2. Age vs. BMI Scatter Plot
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='Age', y='BMI', hue='Outcome', data=diabetes_df, palette='coolwarm')
    plt.title('Age vs BMI')
    plt.xlabel('Age')
    plt.ylabel('BMI')
    plt.savefig('static/plot2.png')
    plt.close()

    # 3. Boxplot of Blood Pressure by Outcome
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='Outcome', y='BloodPressure', data=diabetes_df, palette='Set2')
    plt.title('Blood Pressure by Outcome')
    plt.xlabel('Outcome')
    plt.ylabel('Blood Pressure')
    plt.savefig('static/plot3.png')
    plt.close()

    # 4. Pairplot of Features
    pair_plot = sns.pairplot(diabetes_df[['Glucose', 'BloodPressure', 'BMI', 'Age', 'Outcome']], hue='Outcome', palette='husl')
    pair_plot.savefig('static/plot4.png')
    plt.close()

    # 5. Bar Graph of Average Glucose Levels by Outcome
    plt.figure(figsize=(10, 6))
    avg_glucose_by_outcome = diabetes_df.groupby('Outcome')['Glucose'].mean()
    avg_glucose_by_outcome.plot(kind='bar', color=['lightcoral', 'cornflowerblue'])
    plt.title('Average Glucose Levels by Diabetes Outcome')
    plt.xlabel('Diabetes Outcome (0 = No, 1 = Yes)')
    plt.ylabel('Average Glucose Level')
    plt.xticks([0, 1], ['No Diabetes', 'Diabetes'], rotation=0)
    plt.savefig('static/plot5.png')
    plt.close()

# Route for the main page
@app.route('/')
def home():
    # Call the function to ensure plots are generated if needed
    create_visualizations()
    return render_template('index.html')

# Start the Flask application
if __name__ == '__main__':
    app.run(debug=True)
