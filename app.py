import streamlit as st
import pandas as pd
import time
import copy
import datetime
import plotly.graph_objects as go # <-- NEW: Import Plotly

# --- Page Configuration ---
st.set_page_config(
    layout="wide",
    page_title="MuscleMap AI",
    page_icon="💪"
)

# --- Sidebar ---
with st.sidebar:
    st.title("MuscleMap AI 💪")
    st.markdown("Your AI-Powered Fitness Transformation Companion.")
    st.markdown("---")
    st.markdown("**Project By:**")
    st.markdown("Paramjit Singh (2228947)")
    st.markdown("Rahul Rana (2228955)")
    st.markdown("**Mentor:**")
    st.markdown("Er. Aditya Sharma")
    st.markdown("---")
    st.markdown(f"*{datetime.date.today().strftime('%B %d, %Y')}*")

# --- 1. AI "BRAIN" - FITNESS & NUTRITION RULES ---

def calculate_tdee(profile):
    """
    Calculates TDEE using the Harris-Benedict formula (revised).
    Uses real gym/nutrition rules.
    """
    age = profile['age']
    height = profile['height']
    weight = profile['start_weight']
    gender = profile['gender']
    activity_level = profile['activity_level']

    # Revised Harris-Benedict BMR Calculation
    if gender == "Male":
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else: # Female
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)

    # Activity Level Multiplier
    if activity_level == "Sedentary (office job)":
        multiplier = 1.2
    elif activity_level == "Lightly Active (1-2 days/week)":
        multiplier = 1.375
    elif activity_level == "Moderately Active (3-5 days/week)":
        multiplier = 1.55
    else: # Very Active (6-7 days/week)
        multiplier = 1.725
    
    tdee = bmr * multiplier
    return int(tdee)

def calculate_bmi_details(weight, height_cm):
    """
    Calculates BMI, determines the category, and assigns a color.
    Based on the user-provided image.
    """
    if height_cm == 0:
        return 0, "Unknown", "gray"
        
    height_m = height_cm / 100
    bmi = weight / (height_m ** 2)
    
    if bmi < 18.5:
        category = "Underweight"
        color = "#007bff" # Blue
    elif 18.5 <= bmi < 25:
        category = "Normal weight"
        color = "#28a745" # Green
    elif 25 <= bmi < 30:
        category = "Overweight"
        color = "#ffc107" # Yellow/Gold
    elif 30 <= bmi < 35:
        category = "Obese"
        color = "#fd7e14" # Orange
    else: # bmi >= 35
        category = "Extremely Obese"
        color = "#dc3545" # Red
        
    return bmi, category, color

def create_bmi_gauge(bmi):
    """
    Creates a Plotly gauge chart based on the user's BMI.
    """
    # Define the ranges and colors from the user's image
    ranges = [0, 18.5, 25, 30, 35, 50] # 50 is a reasonable max for the gauge
    colors = ["#007bff", "#28a745", "#ffc107", "#fd7e14", "#dc3545"]
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = bmi,
        number = {'suffix': " BMI", 'font': {'size': 24}, 'valueformat': ".1f"},
        title = {'text': "Your BMI Category", 'font': {'size': 20}},
        gauge = {
            'axis': {'range': [None, 50], 'tickwidth': 1, 'tickcolor': "darkgray"},
            'bar': {'color': "rgba(0,0,0,0)"}, # Make the value bar invisible
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [ranges[0], ranges[1]], 'color': colors[0], 'name': 'Underweight'},
                {'range': [ranges[1], ranges[2]], 'color': colors[1], 'name': 'Normal'},
                {'range': [ranges[2], ranges[3]], 'color': colors[2], 'name': 'Overweight'},
                {'range': [ranges[3], ranges[4]], 'color': colors[3], 'name': 'Obese'},
                {'range': [ranges[4], ranges[5]], 'color': colors[4], 'name': 'Extremely Obese'}
            ],
            
            # --- THIS IS THE "NEEDLE" ---
            # I've changed this to be a thick, red line
            # that looks much more like a "needle"
            'threshold': {
                'line': {'color': "red", 'width': 10},
                'thickness': 0.9,
                'value': bmi
            }
        }
    ))
    
    # Make it smaller and transparent for Streamlit
    fig.update_layout(
        height=350, 
        margin={'t': 50, 'b': 30, 'l': 30, 'r': 30},
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "black"} # Set font to black for visibility on white gauge
    )
    return fig

def get_initial_nutrition_plan(tdee, goal, weight):
    """
    Generates a structured nutrition plan based on TDEE and goal.
    Uses real gym rules:
    - Protein: 1.8g-2.2g per kg for muscle gain, 1.6g-2g for weight loss.
    - Fats: 20-30% of total calories.
    - Carbs: Remainder of calories.
    """
    plan = {
        "calories_kcal": 0,
        "protein_g": 0,
        "fats_g": 0,
        "carbs_g": 0,
        "notes": ""
    }

    if goal == "Weight Reduction":
        plan['calories_kcal'] = tdee - 400 # 400 kcal deficit
        plan['protein_g'] = int(weight * 2.0)
        plan['notes'] = "A 400-calorie deficit is aggressive but effective. Focus on hitting your protein target to maintain muscle while losing fat."
    
    elif goal == "Muscle Gain":
        plan['calories_kcal'] = tdee + 300 # 300 kcal surplus
        plan['protein_g'] = int(weight * 2.0)
        plan['notes'] = "A 300-calorie surplus is a lean bulk. This, combined with high protein, will help you build muscle while minimizing fat gain."
    
    else: # General Fitness
        plan['calories_kcal'] = tdee # Maintain weight
        plan['protein_g'] = int(weight * 1.5)
        plan['notes'] = "Eating at maintenance calories will fuel your workouts and help you recomp your body (build muscle and lose fat) over time."

    # Calculate Fats (25% of total calories)
    # 1g fat = 9 calories
    plan['fats_g'] = int((plan['calories_kcal'] * 0.25) / 9)
    
    # Calculate Carbs (Remaining calories)
    # 1g protein = 4 calories
    # 1g carb = 4 calories
    calories_from_protein_and_fats = (plan['protein_g'] * 4) + (plan['fats_g'] * 9)
    remaining_calories = plan['calories_kcal'] - calories_from_protein_and_fats
    plan['carbs_g'] = int(remaining_calories / 4)

    return plan

def get_initial_workout_plan(goal, experience):
    """
    Generates a structured workout plan based on goal and experience.
    Uses real gym rules:
    - Beginners: Full Body 3x/week to learn form and build a base.
    - Intermediate: PPL (Push-Pull-Legs) or Upper/Lower splits.
    - Advanced: Higher frequency, more specialization.
    - Rep Ranges: 6-10 for strength/hypertrophy, 10-15 for endurance.
    """
    plan = {
        "split_type": "",
        "frequency_per_week": 0,
        "notes": "",
        "weekly_schedule": []
    }

    # --- Plan for Beginners ---
    if experience == "Beginner (0-1 years)":
        plan['split_type'] = "Full Body"
        plan['frequency_per_week'] = 3
        plan['notes'] = "Focus on learning the main compound lifts (Squat, Bench, Deadlift, Overhead Press). Aim to get a little stronger each week."
        plan['weekly_schedule'] = [
            {"day": "Day 1", "focus": "Full Body A", "exercises": ["Squats: 3 sets of 8-10 reps", "Bench Press: 3 sets of 8-10 reps", "Barbell Row: 3 sets of 8-10 reps", "Plank: 3 sets of 60 seconds"]},
            {"day": "Day 2", "focus": "Rest"},
            {"day": "Day 3", "focus": "Full Body B", "exercises": ["Deadlift: 1 set of 5 reps", "Overhead Press: 3 sets of 8-10 reps", "Pull-Ups (or Lat Pulldown): 3 sets of 8-10 reps", "Lunges: 3 sets of 10-12 reps per leg"]},
            {"day": "Day 4", "focus": "Rest"},
            {"day": "Day 5", "focus": "Full Body A (Repeat)", "exercises": ["Squats: 3 sets of 8-10 reps", "Bench Press: 3 sets of 8-10 reps", "Barbell Row: 3 sets of 8-10 reps", "Bicep Curls: 2 sets of 12-15 reps"]},
            {"day": "Day 6", "focus": "Rest"},
            {"day": "Day 7", "focus": "Rest (or light cardio)"}
        ]

    # --- Plan for Intermediates ---
    elif experience == "Intermediate (1-3 years)":
        plan['split_type'] = "Push-Pull-Legs (PPL)"
        plan['frequency_per_week'] = 6 if goal == "Muscle Gain" else 4 # 4-day Upper/Lower for weight loss
        
        if goal == "Muscle Gain":
            plan['notes'] = "Push-Pull-Legs is a high-frequency split. The key is progressive overload: add a little weight or an extra rep to your main lifts each week."
            plan['weekly_schedule'] = [
                {"day": "Day 1", "focus": "Push (Chest, Shoulders, Triceps)", "exercises": ["Bench Press: 4 sets of 6-8 reps", "Overhead Press: 3 sets of 8-10 reps", "Incline Dumbbell Press: 3 sets of 10-12 reps", "Tricep Pushdown: 3 sets of 12-15 reps"]},
                {"day": "Day 2", "focus": "Pull (Back, Biceps)", "exercises": ["Deadlift: 3 sets of 5 reps", "Pull-Ups (or Lat Pulldown): 4 sets of 8-10 reps", "Barbell Row: 3 sets of 8-10 reps", "Bicep Curls: 3 sets of 12-15 reps"]},
                {"day": "Day 3", "focus": "Legs (Quads, Hamstrings, Calves)", "exercises": ["Squats: 4 sets of 6-8 reps", "Romanian Deadlift: 3 sets of 10-12 reps", "Leg Press: 3 sets of 12-15 reps", "Calf Raises: 4 sets of 15-20 reps"]},
                {"day": "Day 4", "focus": "Push (Repeat)", "exercises": ["Bench Press: 4 sets of 6-8 reps", "Overhead Press: 3 sets of 8-10 reps", "Incline Dumbbell Press: 3 sets of 10-12 reps", "Tricep Pushdown: 3 sets of 12-15 reps"]},
                {"day": "Day 5", "focus": "Pull (Repeat)", "exercises": ["Deadlift: 3 sets of 5 reps", "Pull-Ups (or Lat Pulldown): 4 sets of 8-10 reps", "Barbell Row: 3 sets of 8-10 reps", "Bicep Curls: 3 sets of 12-15 reps"]},
                {"day": "Day 6", "focus": "Legs (Repeat)", "exercises": ["Squats: 4 sets of 6-8 reps", "Romanian Deadlift: 3 sets of 10-12 reps", "Leg Press: 3 sets of 12-15 reps", "Calf Raises: 4 sets of 15-20 reps"]},
                {"day": "Day 7", "focus": "Rest"}
            ]
        else: # Weight Reduction or General Fitness
            plan['split_type'] = "Upper / Lower Split"
            plan['frequency_per_week'] = 4
            plan['notes'] = "This 4-day split balances strength training and recovery, leaving 3 days for cardio, which is key for weight loss."
            plan['weekly_schedule'] = [
                {"day": "Day 1", "focus": "Upper Body Strength", "exercises": ["Bench Press: 4 sets of 5-8 reps", "Barbell Row: 4 sets of 5-8 reps", "Overhead Press: 3 sets of 8-10 reps", "Lat Pulldown: 3 sets of 10-12 reps"]},
                {"day": "Day 2", "focus": "Lower Body Strength", "exercises": ["Squats: 4 sets of 5-8 reps", "Deadlift: 3 sets of 5-8 reps", "Leg Press: 3 sets of 12-15 reps", "Hamstring Curls: 3 sets of 12-15 reps"]},
                {"day": "Day 3", "focus": "Rest / Cardio"},
                {"day": "Day 4", "focus": "Upper Body Hypertrophy", "exercises": ["Incline Dumbbell Press: 3 sets of 10-15 reps", "Dumbbell Row: 3 sets of 10-15 reps", "Lateral Raises: 4 sets of 15-20 reps", "Bicep Curls: 3 sets of 12-15 reps", "Tricep Extensions: 3 sets of 12-15 reps"]},
                {"day": "Day 5", "focus": "Lower Body Hypertrophy", "exercises": ["Leg Press: 4 sets of 15-20 reps", "Lunges: 3 sets of 12-15 reps per leg", "Leg Extensions: 3 sets of 15-20 reps", "Calf Raises: 4 sets of 15-20 reps"]},
                {"day": "Day 6", "focus": "Cardio"},
                {"day": "Day 7", "focus": "Rest"}
            ]
    
    # --- Plan for Advanced ---
    else: # Advanced (3+ years)
        plan['split_type'] = "Advanced PPL or Body Part Split"
        plan['frequency_per_week'] = 5
        plan['notes'] = "As an advanced lifter, you need more volume and specialization. This 5-day split lets you dedicate entire days to specific muscle groups."
        plan['weekly_schedule'] = [
            {"day": "Day 1", "focus": "Chest & Triceps", "exercises": ["Bench Press: 5 sets of 5 reps", "Incline Dumbbell Press: 4 sets of 10-12 reps", "Cable Flys: 3 sets of 15-20 reps", "Skullcrushers: 4 sets of 10-12 reps"]},
            {"day": "Day 2", "focus": "Back & Biceps", "exercises": ["Deadlift: 5 sets of 3-5 reps", "Pull-Ups (Weighted): 4 sets of 6-10 reps", "T-Bar Row: 4 sets of 8-10 reps", "Barbell Curls: 4 sets of 10-12 reps"]},
            {"day": "Day 3", "focus": "Legs", "exercises": ["Squats: 5 sets of 5 reps", "Romanian Deadlift: 4 sets of 8-10 reps", "Leg Press: 4 sets of 15-20 reps", "Leg Curls: 3 sets of 12-15 reps", "Calf Raises: 5 sets of 15-20 reps"]},
            {"day": "Day 4", "focus": "Shoulders & Abs", "exercises": ["Overhead Press: 5 sets of 5 reps", "Lateral Raises: 5 sets of 15-20 reps", "Reverse Pec Deck: 4 sets of 12-15 reps", "Cable Crunches: 4 sets of 15-20 reps"]},
            {"day": "Day 5", "focus": "Full Body / Weak Point", "exercises": ["Squat: 3 sets of 5 reps", "Bench Press: 3 sets of 5 reps", "Barbell Row: 3 sets of 5 reps", "Focus on 2-3 exercises for a lagging muscle group."]},
            {"day": "Day 6", "focus": "Rest"},
            {"day": "Day 7", "focus": "Rest"}
        ]
        
    # Add cardio based on goal
    if goal == "Weight Reduction":
        plan['notes'] += " Add 3-4 cardio sessions (30-45 min) on rest days or after workouts."
    elif goal == "Muscle Gain":
        plan['notes'] += " Keep cardio minimal (1-2 sessions, 20 min) to maximize recovery."
    
    return plan

# --- THIS IS THE FIRST FIX ---
# The function now accepts the current plans as arguments
def get_ai_recommendation(profile, progress, current_nutrition_plan, current_workout_plan):
    """
    This is the "AI Coach" brain.
    It analyzes the user's weekly check-in data (the 'progress' dict)
    and makes an intelligent decision on how to adapt their plan.
    """
    
    # --- THIS IS THE SECOND FIX ---
    # We now deepcopy from the arguments, not from the profile dict
    new_nutrition_plan = copy.deepcopy(current_nutrition_plan)
    new_workout_plan = copy.deepcopy(current_workout_plan)
    
    # Get all the data from the check-in
    goal = profile['goal']
    start_weight = profile['start_weight'] # Weight at the *start* of this 1-week interval
    current_weight = progress['current_weight']
    weight_change = current_weight - start_weight
    
    diet_adherence = progress['diet_adherence']
    strength_progress = progress['strength_progress']
    energy_levels = progress['energy_levels']
    sleep_quality = progress['sleep_quality']
    
    # This list will hold all the AI's feedback messages
    feedback_log = []
    
    # --- AI Coaching Logic ---
    
    # 1. First, check for "confounders" (sleep, diet adherence).
    # A real coach knows not to change the plan if the user didn't follow it.
    
    if diet_adherence in ["Bad (I didn't follow the plan)"]:
        feedback_log.append("The most important factor is consistency. We can't know if the plan is working unless you follow it. **No changes this week.** Let's aim for 100% adherence.")
        return new_nutrition_plan, new_workout_plan, feedback_log
        
    if sleep_quality in ["Poor (4-5 hours)"] or energy_levels == "Low":
        feedback_log.append("Your sleep and energy are low. This is a huge factor in progress. This week, your #1 goal is to **get 7-8 hours of sleep**. We will keep the plan the same to allow your body to recover.")
        return new_nutrition_plan, new_workout_plan, feedback_log

    # 2. If sleep and adherence are good, check progress against the goal.
    
    # --- AI LOGIC: WEIGHT REDUCTION ---
    if goal == "Weight Reduction":
        # Target: ~0.5kg loss per week
        if weight_change < -0.8: # Lost too fast
            feedback_log.append(f"You lost {abs(weight_change):.1f} kg! This is great, but a bit fast. We'll **add 150 calories** (mostly from carbs) to make this more sustainable and preserve muscle.")
            new_nutrition_plan['calories_kcal'] += 150
            new_nutrition_plan['carbs_g'] += 38 # (150 / 4)
        elif -0.8 <= weight_change < -0.3: # Perfect range
            feedback_log.append(f"You lost {abs(weight_change):.1f} kg. This is the perfect range! **No changes to the plan.** Keep up the great work.")
        else: # Plateaued or gained weight
            feedback_log.append(f"Your weight stayed about the same (change: {weight_change:.1f} kg). This is a normal plateau. We will make two changes to break it:")
            feedback_log.append("1. **Decreasing calories by 200.**")
            feedback_log.append("2. **Adding one 30-minute cardio session.**")
            new_nutrition_plan['calories_kcal'] -= 200
            new_nutrition_plan['carbs_g'] -= 50 # (200 / 4)
            new_workout_plan['notes'] += " AI UPDATE: Add one 30-minute cardio session this week."

    # --- AI LOGIC: MUSCLE GAIN ---
    elif goal == "Muscle Gain":
        # Target: ~0.25kg gain per week
        if weight_change > 0.5: # Gained too fast (likely fat)
            feedback_log.append(f"You gained {weight_change:.1f} kg. This is a bit fast, which might mean we're adding too much fat. We'll **decrease calories by 150** to lean this out.")
            new_nutrition_plan['calories_kcal'] -= 150
            new_nutrition_plan['carbs_g'] -= 38 # (150 / 4)
        elif 0.1 <= weight_change < 0.4: # Perfect "lean bulk" range
            feedback_log.append(f"You gained {weight_change:.1f} kg. This is the perfect range for a lean bulk! **No changes to nutrition.**")
        else: # Plateaued or lost weight
            feedback_log.append(f"Your weight stayed about the same (change: {weight_change:.1f} kg). We need to eat more to grow. We'll **add 200 calories** (carbs & protein) to fuel muscle growth.")
            new_nutrition_plan['calories_kcal'] += 200
            new_nutrition_plan['carbs_g'] += 30
            new_nutrition_plan['protein_g'] += 20
        
        # Strength Progress Logic (Progressive Overload)
        if strength_progress == "Got stronger (added weight/reps)":
            feedback_log.append("You got stronger! This is the #1 rule of muscle growth (Progressive Overload). Your next workout, try to **add another 1-2 reps, or add 2.5kg** to your main lifts.")
            new_workout_plan['notes'] += " AI UPDATE: You're stronger. Apply progressive overload: add 2.5kg or 1-2 reps to main lifts."
        elif strength_progress == "Stalled (lifted the same)":
            feedback_log.append("You stalled on lifts. This is normal. This week, we will **change your rep scheme** to introduce a new stimulus. We'll move from 8-10 reps to 5-8 reps on your main lifts.")
            # This is a simple text replace, a real app would be more granular
            new_workout_plan['weekly_schedule'] = [str(day).replace('8-10', '5-8') for day in new_workout_plan['weekly_schedule']]

    # --- AI LOGIC: GENERAL FITNESS ---
    else:
        feedback_log.append("You're on the General Fitness plan. The main goal is consistency. Keep showing up!")
        if strength_progress == "Got stronger (added weight/reps)":
            feedback_log.append("You got stronger! This is fantastic. Keep adding weight or reps when you can.")
        
    return new_nutrition_plan, new_workout_plan, feedback_log

# --- 2. STREAMLIT APP UI ---

# We use "page" in session_state to control navigation
if 'page' not in st.session_state:
    st.session_state.page = "Onboarding"
    st.session_state.user_profile = {}
    st.session_state.current_nutrition_plan = {}
    st.session_state.current_workout_plan = {}
    st.session_state.progress_history = []

# --- PAGE 1: ONBOARDING ---
if st.session_state.page == "Onboarding":
    st.title("Welcome to MuscleMap. Let's build your profile.")
    st.markdown("To create your personalized AI plan, we need some starting information.")
    
    with st.form("profile_form"):
        st.subheader("Step 1: Basic Information")
        col1, col2, col3 = st.columns(3)
        with col1:
            age = st.number_input("Age", min_value=16, max_value=100, value=25)
        with col2:
            gender = st.selectbox("Gender", ["Male", "Female"])
        with col3:
             activity_level = st.selectbox("Activity Level (at work/school)", 
                                           ["Sedentary (office job)", 
                                            "Lightly Active (1-2 days/week)", 
                                            "Moderately Active (3-5 days/week)", 
                                            "Very Active (6-7 days/week)"])
        
        st.subheader("Step 2: Body Metrics")
        col1, col2 = st.columns(2)
        with col1:
            height = st.number_input("Height (cm)", min_value=100, max_value=250, value=170)
        with col2:
            start_weight = st.number_input("Current Weight (kg)", min_value=40.0, max_value=200.0, value=70.0, step=0.1)

        st.subheader("Step 3: Your Goals")
        col1, col2 = st.columns(2)
        with col1:
            goal_options = ["Weight Reduction", "Muscle Gain", "General Fitness"]
            goal = st.selectbox("Primary Goal", goal_options)
        with col2:
            exp_options = ["Beginner (0-1 years)", "Intermediate (1-3 years)", "Advanced (3+ years)"]
            experience_level = st.selectbox("Gym Experience", exp_options)
        
        st.markdown("---")
        submitted = st.form_submit_button("Build My AI Plan!", type="primary")
        
        if submitted:
            # 1. Save the profile
            st.session_state.user_profile = {
                "age": age,
                "gender": gender,
                "activity_level": activity_level,
                "height": height,
                "start_weight": start_weight,
                "goal": goal,
                "experience_level": experience_level,
                "plan_start_date": datetime.date.today(),
                "weeks_on_plan": 0
            }
            profile = st.session_state.user_profile
            
            with st.spinner("Analyzing your profile and building your personalized AI plan..."):
                time.sleep(3)
                
                # 2. Calculate TDEE, BMI, & Initial Plans
                tdee = calculate_tdee(profile)
                bmi, bmi_category, bmi_color = calculate_bmi_details(profile['start_weight'], profile['height'])
                
                # 2b. SAVE new metrics to the profile
                st.session_state.user_profile['tdee'] = tdee
                st.session_state.user_profile['bmi'] = bmi
                st.session_state.user_profile['bmi_category'] = bmi_category
                st.session_state.user_profile['bmi_color'] = bmi_color

                nutrition_plan = get_initial_nutrition_plan(tdee, profile['goal'], profile['start_weight'])
                workout_plan = get_initial_workout_plan(profile['goal'], profile['experience_level'])

                # 3. Save the first plan to session state
                st.session_state.current_nutrition_plan = nutrition_plan
                st.session_state.current_workout_plan = workout_plan
            
            # 4. Move to the main dashboard
            st.session_state.page = "Dashboard"
            st.success("Your new AI plan is ready!")
            st.balloons()
            time.sleep(2)
            st.rerun()

# --- PAGE 2: MAIN DASHBOARD ---
elif st.session_state.page == "Dashboard":
    
    # Get all the current user data
    profile = st.session_state.user_profile
    nutri_plan = st.session_state.current_nutrition_plan
    plan = st.session_state.current_workout_plan
    
    st.title(f"Your AI Dashboard: {profile['goal']}")
    
    # Check if AI has feedback, and show it as an info box
    if 'ai_feedback' in st.session_state and st.session_state.ai_feedback:
        st.info("".join([f"- {msg}\n" for msg in st.session_state.ai_feedback]))
        # Clear feedback after showing it
        st.session_state.ai_feedback = None 
    
    col1, col2 = st.columns([1.5, 1]) # Make first column wider
    
    with col1:
        # Nutrition Plan
        st.subheader("Your AI Nutrition Plan")
        with st.container(border=True):
            nutri = nutri_plan
            st.metric("Target Calories", f"{nutri['calories_kcal']} kcal")
            st.markdown(f"**Notes:** {nutri['notes']}")
            st.markdown("---")
            p1, p2, p3 = st.columns(3)
            p1.metric("Protein", f"{nutri['protein_g']} g")
            p2.metric("Fats", f"{nutri['fats_g']} g")
            p3.metric("Carbs", f"{nutri['carbs_g']} g")

        # --- UPDATED PROFILE BOX TO SHOW BMI GAUGE ---
        st.subheader("Your Health Metrics")
        with st.container(border=True):
            
            # --- HERE IS THE NEW GAUGE ---
            bmi_gauge_fig = create_bmi_gauge(profile['bmi'])
            st.plotly_chart(bmi_gauge_fig, use_container_width=True)
            # --- END OF GAUGE ---

            p1, p2 = st.columns(2)
            p1.metric("Maintenance Calories (TDEE)", f"{profile['tdee']} kcal")
            p2.metric("Current Weight", f"{profile['start_weight']} kg")
            
            st.markdown(f"**Height:** {profile['height']} cm | **Age:** {profile['age']}")
            
    with col2:
        # Workout Plan
        st.subheader("Your AI Workout Plan")
        with st.container(border=True):
            wp = plan
            st.markdown(f"**Split Type:** {wp['split_type']} ({wp['frequency_per_week']} days/week)")
            st.markdown(f"**Notes:** {wp['notes']}")
            st.markdown("---")
            for day in wp['weekly_schedule']:
                with st.expander(f"**{day['day']}: {day['focus']}**"):
                    # --- THIS IS THE FIX ---
                    # Check if the 'exercises' key exists before trying to loop
                    if 'exercises' in day and day['exercises']:
                        for exercise in day['exercises']:
                            st.markdown(f"- {exercise}")
                    else:
                        # If no 'exercises' key, it's a Rest Day
                        st.markdown("- *Rest Day*")

    # --- Weekly Check-in Form ---
    st.markdown("---")
    st.subheader("Weekly AI Check-in")
    
    # Calculate when the next check-in is due
    next_checkin_date = profile['plan_start_date'] + datetime.timedelta(days=(profile['weeks_on_plan'] * 7) + 7)
    days_until_checkin = (next_checkin_date - datetime.date.today()).days

    # --- MODIFICATION FOR DEMO ---
    # The 'if/else' block that hides the form is removed.
    # We now ALWAYS show the form, so you can test the app.
    if days_until_checkin > 0:
        st.info(f"Your next weekly check-in is due in **{days_until_checkin} day(s)**. (Demo mode: The form is always available for testing.)")
    else:
        st.success("Your weekly check-in is ready! Please fill out the form below.")
    
    # This form is now ALWAYS visible, not inside an 'else' block.
    with st.form("progress_form"):
        st.markdown("Log your progress for the past week. Be as honest as possible!")
        
        # 1. New Weight
        current_weight = st.number_input("Your New Current Weight (kg)", 
                                         min_value=40.0, max_value=200.0, 
                                         value=profile['start_weight'], step=0.1)
        
        # --- THIS IS THE FIX ---
        # The code below was over-indented. It has been fixed.
        col1, col2 = st.columns(2)
        with col1:
            # 2. Diet Adherence
            diet_adherence = st.selectbox("How was your diet adherence?",
                                          ["Great (I hit my targets)", 
                                           "Good (I was pretty close)", 
                                           "Okay (I slipped up a few times)", 
                                           "Bad (I didn't follow the plan)"])
            
            # 3. Energy Levels
            energy_levels = st.selectbox("How were your energy levels?",
                                         ["High", "Normal", "Low"])
        
        with col2:
            # 4. Strength Progress (Only ask if not on a "Rest" day)
            strength_progress = st.selectbox("How was your strength in the gym?",
                                             ["Got stronger (added weight/reps)", 
                                              "Stalled (lifted the same)", 
                                              "Got weaker (had to lower weight)"])
            
            # 5. Sleep Quality
            sleep_quality = st.selectbox("How was your sleep quality?",
                                         ["Great (7-8+ hours)", 
                                          "Okay (6-7 hours)", 
                                          "Poor (4-5 hours)"])

        submitted = st.form_submit_button("Analyze My Week & Update My Plan", type="primary")

        if submitted:
            with st.spinner("Your AI Coach is analyzing your week..."):
                
                # 1. Create the detailed progress log
                progress_log = {
                    "date": datetime.date.today(),
                    "week_number": profile['weeks_on_plan'] + 1,
                    "start_weight_of_week": profile['start_weight'],
                    "current_weight": current_weight,
                    "diet_adherence": diet_adherence,
                    "strength_progress": strength_progress,
                    "energy_levels": energy_levels,
                    "sleep_quality": sleep_quality
                }
                
                # 2. Call the "AI Brain" to get new plans and feedback
                # --- THIS IS THE THIRD FIX ---
                # We now pass the current plans to the function
                new_nutrition_plan, new_workout_plan, ai_feedback = get_ai_recommendation(
                    profile, 
                    progress_log, 
                    st.session_state.current_nutrition_plan, 
                    st.session_state.current_workout_plan
                )
                
                # 3. Save all the new data to our session_state "database"
                st.session_state.progress_history.append(progress_log)
                st.session_state.current_nutrition_plan = new_nutrition_plan
                st.session_state.current_workout_plan = new_workout_plan
                st.session_state.ai_feedback = ai_feedback
                
                # 4. Update the profile for the *next* week
                st.session_state.user_profile['start_weight'] = current_weight
                st.session_state.user_profile['weeks_on_plan'] += 1
                
                # 5. Update BMI with new weight
                bmi, bmi_category, bmi_color = calculate_bmi_details(current_weight, profile['height'])
                st.session_state.user_profile['bmi'] = bmi
                st.session_state.user_profile['bmi_category'] = bmi_category
                st.session_state.user_profile['bmi_color'] = bmi_color

            st.success("Your AI Coach has updated your plan! Reloading...")
            st.balloons()
            time.sleep(2)
            st.rerun()

    # --- Progress History Chart ---
    if st.session_state.progress_history:
        st.markdown("---")
        st.subheader("Your Weight Progress")
        history_df = pd.DataFrame(st.session_state.progress_history)
        
        # Create a clean DataFrame for the chart
        chart_data = history_df[['date', 'current_weight']].copy()
        chart_data.rename(columns={'current_weight': 'Weight (kg)'}, inplace=True)
        chart_data.set_index('date', inplace=True)
        
        # Add the user's starting weight to the beginning of the chart
        start_data = pd.DataFrame(
            {'Weight (kg)': [st.session_state.user_profile['start_weight']]},
            index=[st.session_state.user_profile['plan_start_date']]
        )
        full_chart_data = pd.concat([start_data, chart_data])
        
        st.line_chart(full_chart_data)


