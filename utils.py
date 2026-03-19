import pandas as pd

def calculate_calories(age, gender, height, weight, activity, goal):
    if gender == "Male":
        bmi = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmi = 10 * weight + 6.25 * height - 5 * age + 161
        
    activity_factor = {"Sedentary": 1.2, "Moderate": 1.55, "Active": 1.725}.get(activity, 1.2)
    calories = bmi * activity_factor
    
    if goal == "Loose Weight":
        calories *= 0.85
    elif goal == "Gain Muscle":
        calories *= 1.15
        
    return calories

def get_meal_plan(goal, calories):
    df = pd.read_csv("nutrition.csv")
    
    if goal == "Loose Weight":
        meal_df = df[df['calories'] < 300].sample(3)
    elif goal == "Gain Muscle":
        meal_df = df[df['protein_g'] > 20].sample(3)
    else:
        meal_df = df.sample(3)
        
    return meal_df[['food_and_serving', 'calories', 'protein_g']]

def get_workout_plan(goal):
    df = pd.read_csv("fitness_chatbot/exercises.csv")
    
    if goal == "Loose Weight":
        workouts = df[df[]]