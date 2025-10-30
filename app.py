import streamlit as st
import pandas as pd
import time
import copy
import datetime

# --- Page Configuration ---
st.set_page_config(
    layout="wide",
    page_title="MuscleMap AI Coach",
    page_icon="🤖"
)

# --- Sidebar ---
with st.sidebar:
    st.title("MuscleMap AI Coach 🤖")
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
    Calculates TDEE (Total Daily Energy Expenditure) using Harris-Benedict Eq.
    This is the "engine" of the diet plan.
    """
    weight = profile['start_weight']
    height = profile['height']
    age = profile['age']
    gender = profile['gender']
    activity = profile['activity_level']

    # 1. Calculate BMR (Basal Metabolic Rate)
    if gender == "Male":
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else: # Female
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)

    # 2. Activity Multipliers
    if activity == "Sedentary (office job)":
        multiplier = 1.2
    elif activity == "Light (1-2 workouts/week)":
        multiplier = 1.375
    elif activity == "Moderate (3-5 workouts/week)":
        multiplier = 1.55
    else: # Active (6-7 workouts/week)
        multiplier = 1.725
        
    tdee = bmr * multiplier
    return int(tdee)

# --- NEW FUNCTION TO CALCULATE BMI ---
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

def get_initial_nutrition_plan(tdee, goal, weight):
    """
    Sets the initial Calories, Protein, Fats, and Carbs.
    """
    nutrition = {
        "calories": tdee,
        "protein_g": int(weight * 1.8), # 1.8g protein per kg of bodyweight
        "fats_g": 0,
        "carbs_g": 0
    }
    
    if goal == "Weight Reduction":
        nutrition['calories'] = tdee - 400 # 400 calorie deficit
    elif goal == "Muscle Gain":
        nutrition['calories'] = tdee + 300 # 300 calorie surplus
    # General Fitness stays at maintenance (tdee)

    # Calculate Fats (25% of calories)
    fats_calories = nutrition['calories'] * 0.25
    nutrition['fats_g'] = int(fats_calories / 9)

    # Calculate Carbs (Remaining calories)
    protein_calories = nutrition['protein_g'] * 4
    carb_calories = nutrition['calories'] - protein_calories - fats_calories
    nutrition['carbs_g'] = int(carb_calories / 4)
    
    return nutrition

def get_initial_workout_plan(goal, experience):
    """
    Creates a structured, science-based workout plan.
    """
    plan = {
        "split_type": "Full Body",
        "frequency_per_week": 3,
        "notes": "Focus on learning the movement and controlling the weight.",
        "weekly_schedule": []
    }

    if goal == "Weight Reduction":
        if experience == "Beginner":
            plan['split_type'] = "Full Body"
            plan['frequency_per_week'] = 3
            plan['weekly_schedule'] = [
                {"day": "Day 1", "focus": "Full Body A", "exercises": ["Goblet Squat: 3x10", "Push-ups (or Knee Push-ups): 3xAs many as possible", "Dumbbell Row: 3x10 (each side)", "Plank: 3x60 seconds"]},
                {"day": "Day 2", "focus": "Cardio", "exercises": ["30-40 min LISS (Low-Intensity Steady State) cardio"]},
                {"day": "Day 3", "focus": "Full Body B", "exercises": ["Dumbbell Deadlift: 3x10", "Dumbbell Overhead Press: 3x10", "Lat Pulldown: 3x12", "Leg Raises: 3x15"]},
                {"day": "Day 4", "focus": "Cardio", "exercises": ["30-40 min LISS cardio"]},
                {"day": "Day 5", "focus": "Full Body C (optional)", "exercises": ["Lunges: 3x12 (each side)", "Dumbbell Bench Press: 3x10", "Seated Cable Row: 3x12", "Ab Crunches: 3x20"]}
            ]
        else: # Intermediate/Advanced
            plan['split_type'] = "Upper/Lower Split"
            plan['frequency_per_week'] = 4
            plan['weekly_schedule'] = [
                {"day": "Day 1", "focus": "Upper Body (Strength)", "exercises": ["Bench Press: 4x5", "Pull-ups: 4xAs many as possible", "Overhead Press: 3x8", "Barbell Row: 3x8"]},
                {"day": "Day 2", "focus": "Lower Body (Strength)", "exercises": ["Squat: 4x5", "Romanian Deadlift: 3x8", "Leg Press: 3x10", "Calf Raises: 4x15"]},
                {"day": "Day 3", "focus": "HIIT Cardio", "exercises": ["20 min HIIT (1 min on, 2 min off)"]},
                {"day": "Day 4", "focus": "Upper Body (Hypertrophy)", "exercises": ["Incline Dumbbell Press: 3x12", "Lat Pulldown: 3x12", "Lateral Raises: 4x15", "Bicep Curls: 3x12", "Tricep Pushdown: 3x12"]},
                {"day": "Day 5", "focus": "Lower Body (Hypertrophy)", "exercises": ["Leg Extensions: 3x15", "Hamstring Curls: 3x15", "Lunges: 3x12", "Ab Circuit: 3 rounds"]}
            ]

    elif goal == "Muscle Gain":
        if experience == "Beginner":
            plan['split_type'] = "Full Body"
            plan['frequency_per_week'] = 3
            plan['weekly_schedule'] = [
                {"day": "Day 1", "focus": "Full Body A", "exercises": ["Squat: 3x8", "Bench Press: 3x8", "Barbell Row: 3x8"]},
                {"day": "Day 2", "focus": "Rest"},
                {"day": "Day 3", "focus": "Full Body B", "exercises": ["Deadlift: 3x5", "Overhead Press: 3x8", "Pull-ups (or Lat Pulldown): 3x8"]},
                {"day": "Day 4", "focus": "Rest"},
                {"day": "Day 5", "focus": "Full Body C", "exercises": ["Leg Press: 3x10", "Dumbbell Incline Press: 3x10", "Dumbbell Row: 3x10", "Bicep Curls: 2x12", "Tricep Pushdown: 2x12"]}
            ]
        else: # Intermediate/Advanced
            plan['split_type'] = "Push-Pull-Legs (PPL)"
            plan['frequency_per_week'] = 5 # PPL + Upper/Lower
            plan['notes'] = "Focus on Progressive Overload. Track your lifts!"
            plan['weekly_schedule'] = [
                {"day": "Day 1", "focus": "Push (Chest/Shoulders/Tris)", "exercises": ["Bench Press: 4x6-8", "Overhead Press: 3x8-10", "Incline Dumbbell Press: 3x10", "Lateral Raises: 4x12", "Tricep Pushdown: 3x12"]},
                {"day": "Day 2", "focus": "Pull (Back/Biceps)", "exercises": ["Deadlift: 4x5-6", "Pull-ups: 3xAMRAP", "Barbell Row: 3x8-10", "Face Pulls: 3x15", "Bicep Curls: 3x10-12"]},
                {"day": "Day 3", "focus": "Legs", "exercises": ["Squat: 4x6-8", "Romanian Deadlift: 3x10", "Leg Press: 3x12", "Leg Extensions: 2x15", "Hamstring Curls: 2x15"]},
                {"day": "Day 4", "focus": "Rest"},
                {"day": "Day 5", "focus": "Upper Body (Accessory)", "exercises": ["Dumbbell Bench Press: 3x10", "Lat Pulldown: 3x10", "Seated Cable Row: 3x10", "Dumbbell Curls: 3x12", "Overhead Tricep Ext: 3x12"]},
                {"day": "Day 6", "focus": "Lower Body (Accessory)", "exercises": ["Hack Squat: 3x12", "Good Mornings: 3x15", "Calf Raises: 4x20", "Ab Circuit"]}
            ]

    else: # General Fitness
        plan['split_type'] = "Full Body"
        plan['frequency_per_week'] = 3
        plan['weekly_schedule'] = [
            {"day": "Day 1", "focus": "Full Body", "exercises": ["Squat: 3x10", "Push-ups: 3xAMRAP", "Dumbbell Row: 3x10", "Plank: 3x60s"]},
            {"day": "Day 2", "focus": "Active Recovery", "exercises": ["30 min walk or light cardio"]},
            {"day": "Day 3", "focus": "Full Body", "exercises": ["Dumbbell Press: 3x10", "Lat Pulldown: 3x10", "Lunges: 3x12", "Leg Raises: 3x15"]},
            {"day": "Day 4", "focus": "Active Recovery", "exercises": ["30 min walk or light cardio"]},
            {"day": "Day 5", "focus": "Full Body", "exercises": ["Leg Press: 3x12", "Overhead Press: 3x10", "Seated Cable Row: 3x12", "Crunches: 3x20"]}
        ]
        
    return plan


def get_ai_recommendation(profile, progress):
    """
    This is the ADVANCED "AI" Brain.
    It analyzes the weekly progress log and adapts the plan.
    """
    # Get a deep copy of the current plan to modify
    new_plan = copy.deepcopy(st.session_state.current_plan)
    new_plan["plan_title"] = f"Adapted Plan (Week {len(st.session_state.progress_history) + 1})"
    
    # Get all the progress data
    goal = profile['goal']
    start_weight = profile['start_weight'] # Weight at start of *last* interval
    current_weight = progress['current_weight']
    diet = progress['diet_adherence']
    energy = progress['energy_levels']
    strength = progress['strength_progress']
    sleep = progress['sleep_quality']
    
    # --- RULE 0: THE ADHERENCE CHECK (Most Important Rule) ---
    if diet == "Didn't follow":
        new_plan['ai_feedback'] = f"**AI Feedback:** You reported you didn't follow the diet. The plan can't be adapted if it's not followed. **The #1 rule is adherence.**\n\nI am **not changing your plan.** Please try to follow the nutrition and workout plan for this week. You can do this!"
        return new_plan

    # --- RULE 1: WEIGHT REDUCTION LOGIC ---
    if goal == "Weight Reduction":
        weight_lost = start_weight - current_weight
        
        if weight_lost > 1.5: # Losing too fast (more than 1.5kg in a week)
            new_plan['ai_feedback'] = f"**AI Feedback:** You lost {weight_lost:.1f} kg this week. This is too fast and you risk losing muscle. We are **increasing your calories slightly** to slow this down to a sustainable rate."
            new_plan['nutrition_plan']['calories'] += 150
            
        elif weight_lost >= 0.4: # Perfect range (0.4 - 1.5kg)
            new_plan['ai_feedback'] = f"**AI Feedback:** Perfect progress! You lost {weight_lost:.1f} kg. This is the ideal range for sustainable fat loss. **No changes needed.** Keep up the great work!"

        elif weight_lost >= 0: # Lost 0 to 0.4kg (Plateau)
            if energy == "Low" and sleep == "Poor (<5 hrs)":
                new_plan['ai_feedback'] = f"**AI Feedback:** Your weight loss has stalled, but you also reported **low energy and poor sleep.** This is the likely cause. More cardio or fewer calories will only make you feel worse. \n\n**Your #1 goal this week is sleep.** No changes to the plan. Focus on 7+ hours."
            else:
                new_plan['ai_feedback'] = f"**AI Feedback:** Your weight loss has stalled. This is a normal plateau. We will **increase your cardio slightly** to get things moving again."
                # Find the first cardio day and add 5 mins
                for day in new_plan['workout_plan']['weekly_schedule']:
                    if "Cardio" in day['focus'] or "HIIT" in day['focus']:
                        day['exercises'][0] = day['exercises'][0].replace(str(int(day['exercises'][0][0:2])), str(int(day['exercises'][0][0:2]) + 5))
                        break

        else: # Weight was gained
             new_plan['ai_feedback'] = f"**AI Feedback:** It looks like we gained {abs(weight_lost):.1f} kg. This is okay, it's just data! You reported you **followed the diet**, so our calorie target must be too high. We are **reducing calories by 150** to create a larger deficit."
             new_plan['nutrition_plan']['calories'] -= 150

    # --- RULE 2: MUSCLE GAIN LOGIC ---
    elif goal == "Muscle Gain":
        weight_gained = current_weight - start_weight
        
        if weight_gained > 0.7: # Gaining too fast (likely fat)
            new_plan['ai_feedback'] = f"**AI Feedback:** You gained {weight_gained:.1f} kg this week. This is a bit too fast, which may lead to unwanted fat gain. We are **reducing your calories slightly**."
            new_plan['nutrition_plan']['calories'] -= 100
        
        elif weight_gained >= 0.2: # Perfect range (0.2 - 0.7kg)
            if strength == "Got stronger":
                new_plan['ai_feedback'] = f"**AI Feedback:** This is the **PERFECT** scenario. You gained {weight_gained:.1f} kg and you got stronger. This is 100% progress. We will apply **Progressive Overload.**"
                new_plan['workout_plan']['notes'] = "Add +1 rep or +2.5kg to your main compound lifts this week. This is how we grow!"
            else:
                new_plan['ai_feedback'] = f"**AI Feedback:** Good weight gain ({weight_gained:.1f} kg), but you felt your strength stalled. This is fine. **No changes to diet.** This week, focus on your form and hitting your protein target."

        else: # Gained 0kg or lost weight (Stalled)
            if energy == "Low" and sleep == "Poor (<5 hrs)":
                new_plan['ai_feedback'] = f"**AI Feedback:** Your muscle gain has stalled, but you also reported **low energy and poor sleep.** You cannot build muscle in this state. **Your #1 goal this week is sleep.** No changes to the plan. Focus on 7+ hours. Your body builds muscle *when you sleep*."
            elif strength == "Stayed the same" and diet == "Followed it okay":
                 new_plan['ai_feedback'] = f"**AI Feedback:** Gain has stalled. You reported you 'okay' followed the diet. This is the issue. To gain muscle, you **must** hit your calorie and protein targets. **No changes to plan.** Focus on 100% diet adherence this week."
            else: # Followed diet, good sleep, still stalled
                new_plan['ai_feedback'] = f"**AI Feedback:** You've hit a plateau. You're doing everything right, so it's time to **increase calories by 200** to fuel new growth. It's also time to **change the stimulus.**"
                new_plan['nutrition_plan']['calories'] += 200
                # Stimulus change: Change rep range
                if "5-6" in new_plan['workout_plan']['weekly_schedule'][0]['exercises'][0]:
                    new_plan['workout_plan']['notes'] = "New Stimulus: We are switching to Hypertrophy. Aim for 8-10 reps."
                else:
                    new_plan['workout_plan']['notes'] = "New Stimulus: We are switching to Strength. Aim for 5-6 reps."

    # --- RULE 3: GENERAL FITNESS LOGIC ---
    else:
        new_plan['ai_feedback'] = f"**AI Feedback:** Great job logging your week! For 'General Fitness', the main goal is consistency. You're doing great. **No changes to the plan.** Keep it up!"

    # Recalculate macros for all plans
    nutrition = new_plan['nutrition_plan']
    weight = current_weight # Use new weight for macro calcs
    nutrition['protein_g'] = int(weight * 1.8)
    fats_calories = nutrition['calories'] * 0.25
    nutrition['fats_g'] = int(fats_calories / 9)
    protein_calories = nutrition['protein_g'] * 4
    carb_calories = nutrition['calories'] - protein_calories - fats_calories
    nutrition['carbs_g'] = int(carb_calories / 4)
    new_plan['nutrition_plan'] = nutrition

    return new_plan


# --- 2. STREAMLIT APP UI ---

st.title("Welcome to Your MuscleMap Dashboard")

# Use st.session_state as a simple "database"
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = None
    st.session_state.current_plan = None
    st.session_state.progress_history = []
    st.session_state.page = "Onboarding"

# --- PAGE 1: ONBOARDING ---
if st.session_state.page == "Onboarding":
    st.header("Let's create your profile to get started.")
    st.markdown("To create the best AI-driven plan, we need to know about you.")
    
    with st.form("profile_form"):
        st.subheader("Your Body Details")
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", min_value=16, max_value=100, value=25)
            gender = st.selectbox("Gender", ("Male", "Female"))
            height = st.number_input("Height (cm)", min_value=100, max_value=250, value=170)
        with col2:
            start_weight = st.number_input("Current Weight (kg)", min_value=40.0, max_value=200.0, value=70.0, step=0.1)
            activity_level = st.selectbox("Daily Activity Level (excluding workouts)", 
                                        ("Sedentary (office job)", "Light (1-2 workouts/week)", 
                                         "Moderate (3-5 workouts/week)", "Active (6-7 workouts/week)"))
            experience_level = st.selectbox("What is your gym experience?", 
                                        ("Beginner (0-1 years)", "Intermediate (1-3 years)", "Advanced (3+ years)"))

        st.subheader("Your Fitness Goal")
        goal_options = ["Weight Reduction", "Muscle Gain", "General Fitness"]
        goal = st.selectbox("What is your primary goal?", goal_options)
        
        submitted = st.form_submit_button("Create My AI-Powered Plan")
        
        if submitted:
            # 1. Save the profile
            st.session_state.user_profile = {
                "age": age,
                "gender": gender,
                "height": height,
                "start_weight": start_weight,
                "activity_level": activity_level,
                "experience_level": experience_level,
                "goal": goal,
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
                st.session_state.current_plan = {
                    "plan_title": f"Initial Plan: {goal}",
                    "ai_feedback": "**AI Feedback:** Welcome! Here is your personalized starting plan. Follow this for one week, then log your progress. You've got this!",
                    "nutrition_plan": nutrition_plan,
                    "workout_plan": workout_plan
                }
                
                # 4. Add initial weight to history
                st.session_state.progress_history = [{"date": datetime.date.today(), "weight": start_weight, "notes": "Initial Profile"}]

            st.session_state.page = "Dashboard"
            st.success("Your new AI plan is ready!")
            st.balloons()
            st.rerun()

# --- PAGE 2: MAIN DASHBOARD ---
if st.session_state.page == "Dashboard":
    profile = st.session_state.user_profile
    plan = st.session_state.current_plan
    
    st.header(f"Your Goal: {profile['goal']} ({profile['experience_level']})")
    st.markdown("---")
    
    # AI Feedback Box
    st.subheader("🤖 AI Coach Feedback")
    st.info(plan['ai_feedback'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Nutrition Plan
        st.subheader("Your Nutrition Plan")
        with st.container(border=True):
            nutri = plan['nutrition_plan']
            c1, c2 = st.columns(2)
            c1.metric("Target Calories", f"{nutri['calories']} kcal")
            c2.metric("Target Protein", f"{nutri['protein_g']} g")
            st.progress(nutri['protein_g'] / (nutri['calories']/4)) # Show protein %
            
            st.markdown(f"- **Fats:** {nutri['fats_g']} g")
            st.markdown(f"- **Carbs:** {nutri['carbs_g']} g")

        # --- UPDATED PROFILE BOX TO SHOW BMI ---
        st.subheader("Your Health Metrics")
        with st.container(border=True):
            p1, p2 = st.columns(2)
            p1.metric("Your BMI", f"{profile['bmi']:.1f}")
            p2.metric("Maintenance Calories (TDEE)", f"{profile['tdee']} kcal")
            
            # Add the colored category from the image!
            st.markdown(f"**Your Category: <span style='color:{profile['bmi_color']}; font-weight:bold;'>{profile['bmi_category']}</span>**", unsafe_allow_html=True)
            st.markdown("---")
            st.markdown(f"**Current Weight:** {profile['start_weight']} kg | **Height:** {profile['height']} cm | **Age:** {profile['age']}")
            
    with col2:
        # Workout Plan
        st.subheader("Your Workout Plan")
        with st.container(border=True):
            wp = plan['workout_plan']
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
    st.header("Weekly Progress Check-in")
    st.markdown("Log your progress **once per week**. The AI will analyze your data and adapt your plan.")

    with st.form("progress_form"):
        st.subheader("Your Weekly Metrics")
        
        col1, col2 = st.columns(2)
        with col1:
            current_weight = st.number_input("Your New Current Weight (kg)", min_value=40.0, max_value=200.0, value=profile['start_weight'], step=0.1)
            diet_adherence = st.radio("How well did you follow the diet?", 
                                    ("Followed it perfectly", "Followed it okay", "Didn't follow"), horizontal=True)
            strength_progress = st.radio("How was your strength in the gym?",
                                       ("Got stronger", "Stayed the same", "Felt weaker"), horizontal=True)
        with col2:
            energy_levels = st.radio("How were your energy levels?",
                                   ("High", "Normal", "Low"), horizontal=True)
            sleep_quality = st.radio("How was your sleep quality (avg)?",
                                   ("Great (7+ hrs)", "Okay (5-6 hrs)", "Poor (<5 hrs)"), horizontal=True)
            notes = st.text_area("Any other notes for the AI? (e.g., 'Felt sick', 'Was very stressed')")

        submitted = st.form_submit_button("Analyze My Week & Adapt My Plan")
        
        if submitted:
            # This is the "Core Loop"!
            
            # 1. Create progress log
            progress_log = {
                "date": datetime.date.today(),
                "current_weight": current_weight,
                "diet_adherence": diet_adherence,
                "energy_levels": energy_levels,
                "strength_progress": strength_progress,
                "sleep_quality": sleep_quality,
                "notes": notes
            }
            
            with st.spinner("AI is analyzing your week and adapting your plan..."):
                time.sleep(3)
                
                # 2. Call the "AI Brain" to get a new plan
                new_plan = get_ai_recommendation(profile, progress_log)
                
                # 3. Update the user's plan in our "database"
                st.session_state.current_plan = new_plan
                
                # 4. Update the user's "start_weight" for the *next* interval
                st.session_state.user_profile['start_weight'] = current_weight
                
                # 5. Add to history
                st.session_state.progress_history.append({"date": datetime.date.today(), "weight": current_weight, "notes": notes or "N/A"})

            st.success("Your plan has been updated by the AI! Check your new feedback above.")
            st.balloons()
            st.rerun()

    # --- Progress History Chart & Table ---
    if st.session_state.progress_history:
        st.markdown("---")
        st.header("Your Progress History")
        
        history_data = []
        for i, log in enumerate(st.session_state.progress_history):
            history_data.append({
                "Check-in #": i,
                "Date": log['date'],
                "Weight (kg)": log['weight'],
                "Notes": log.get('notes', 'N/A')
            })

        history_df = pd.DataFrame(history_data).set_index("Check-in #")
        
        st.dataframe(history_df, use_container_width=True)
        
        # Create a line chart of the weight
        chart_df = history_df.rename(columns={"Weight (kg)": "Weight"}).set_index("Date")
        st.line_chart(chart_df, y="Weight")



