import streamlit as st
import pandas as pd
import time

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

# --- AI Adaptation Engine (The "Brain") ---
# This is our Stage 1 "Rule-Based AI" as described in the synopsis.

def get_ai_recommendation(profile, progress):
    """
    Analyzes user profile and progress to generate a new plan.
    This is the core "AI" logic.
    """
    goal = profile['goal']
    time_interval_weeks = profile['time_interval_weeks']
    start_weight = profile['start_weight']
    current_weight = progress['current_weight']
    
    # --- Logic for Weight Reduction ---
    if goal == "Weight Reduction":
        weight_lost = start_weight - current_weight
        target_loss_per_week = 0.5  # Target 0.5 kg/week
        expected_loss = target_loss_per_week * time_interval_weeks
        
        # Create a new plan based on progress
        new_plan = {
            "plan_title": f"New Plan: Continue Weight Reduction",
            "diet": "Focus on a 300-calorie deficit. Prioritize protein.",
            "workout": "3x week full-body strength, 2x week 30-min cardio.",
            "ai_feedback": ""
        }
        
        if weight_lost >= expected_loss:
            new_plan['ai_feedback'] = f"**AI Feedback:** Great job! You've lost {weight_lost:.1f} kg, meeting your target. We'll stick to a similar plan to keep the progress steady."
            new_plan['diet'] = "Maintain a 300-calorie deficit. Great consistency."
        elif weight_lost > 0:
            new_plan['ai_feedback'] = f"**AI Feedback:** Good progress! You've lost {weight_lost:.1f} kg. To help you hit your next target, we will slightly increase your cardio."
            new_plan['workout'] = "3x week full-body strength, 3x week 35-min cardio."
        else:
            new_plan['ai_feedback'] = f"**AI Feedback:** It looks like we didn't lose weight this period. Don't worry, this is common. We'll adjust your plan. Please double-check your diet logs and we will increase workout intensity."
            new_plan['diet'] = "Let's try a 400-calorie deficit. Please track your food intake carefully."
            
        return new_plan

    # --- Logic for Muscle Gain ---
    elif goal == "Muscle Gain":
        weight_gained = current_weight - start_weight
        target_gain_per_week = 0.25  # Target 0.25 kg/week
        expected_gain = target_gain_per_week * time_interval_weeks

        new_plan = {
            "plan_title": f"New Plan: Continue Muscle Gain",
            "diet": "Focus on a 250-calorie surplus. 1.8g protein per kg of bodyweight.",
            "workout": "4x week 'Push-Pull-Legs' split. Focus on progressive overload.",
            "ai_feedback": ""
        }

        if weight_gained >= expected_gain:
            new_plan['ai_feedback'] = f"**AI Feedback:** Excellent work! You've gained {weight_gained:.1f} kg, right on target. We'll increase the weights on your main lifts to continue progressing."
        else:
            new_plan['ai_feedback'] = f"**AI Feedback:** We've gained {weight_gained:.1f} kg. This is a solid start. To boost progress, let's slightly increase your calorie surplus and focus on lifting heavier."
            new_plan['diet'] = "Let's try a 350-calorie surplus. Ensure you're hitting your protein target."

        return new_plan
        
    # --- Logic for General Fitness ---
    else:
        return {
            "plan_title": "General Fitness Plan",
            "diet": "Eat a balanced diet of whole foods.",
            "workout": "3x week full-body workouts.",
            "ai_feedback": "**AI Feedback:** You've selected 'General Fitness'. Here is a solid plan to get you started."
        }

# --- Initial Plans (Before AI Adaptation) ---
def get_initial_plan(goal):
    if goal == "Weight Reduction":
        return {
            "plan_title": "Initial Plan: Weight Reduction",
            "diet": "Start with a 300-calorie deficit. Focus on protein and vegetables.",
            "workout": "3x week full-body strength, 2x week 30-min cardio.",
            "ai_feedback": "**AI Feedback:** Welcome! Here is your starting plan. Stick to it and we'll check your progress soon."
        }
    elif goal == "Muscle Gain":
        return {
            "plan_title": "Initial Plan: Muscle Gain",
            "diet": "Start with a 250-calorie surplus. Eat 1.8g of protein per kg of bodyweight.",
            "workout": "4x week 'Push-Pull-Legs' split. Focus on lifting heavy with good form.",
            "ai_feedback": "**AI Feedback:** Welcome! Here is your starting plan. Eat well, train hard, and we'll check your progress soon."
        }
    else:
        return {
            "plan_title": "Initial Plan: General Fitness",
            "diet": "Eat a balanced diet of whole foods.",
            "workout": "3x week full-body workouts.",
            "ai_feedback": "**AI Feedback:** Welcome! Here is your starting plan for general fitness."
        }

# --- Streamlit App (The "Face") ---
st.title("Welcome to MuscleMap AI")

# Use st.session_state as a simple "database" to store user data
# This data only lasts for the user's browser session.
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = None
    st.session_state.current_plan = None
    st.session_state.progress_history = []

# --- 1. Onboarding / Profile Creation ---
if st.session_state.user_profile is None:
    st.header("Let's create your profile to get started.")
    
    with st.form("profile_form"):
        st.write("Tell us about yourself:")
        age = st.number_input("Age", min_value=16, max_value=100, value=25)
        height = st.number_input("Height (cm)", min_value=100, max_value=250, value=170)
        start_weight = st.number_input("Current Weight (kg)", min_value=40.0, max_value=200.0, value=70.0, step=0.1)
        
        st.write("What is your primary goal?")
        goal_options = ["Weight Reduction", "Muscle Gain", "General Fitness"]
        goal = st.selectbox("Goal", goal_options)
        
        time_interval_options = [2, 4, 6]
        time_interval_weeks = st.selectbox("How long is this goal interval?", time_interval_options, format_func=lambda x: f"{x} weeks")
        
        submitted = st.form_submit_button("Create My Profile & First Plan")
        
        if submitted:
            # Save the profile to our session_state "database"
            st.session_state.user_profile = {
                "age": age,
                "height": height,
                "start_weight": start_weight,
                "goal": goal,
                "time_interval_weeks": time_interval_weeks
            }
            # Generate the user's first plan
            st.session_state.current_plan = get_initial_plan(goal)
            
            with st.spinner("Generating your personalized plan..."):
                time.sleep(2)
            
            st.success("Your profile and first plan are ready!")
            st.balloons()
            st.rerun()

# --- 2. Main Dashboard (After Onboarding) ---
else:
    profile = st.session_state.user_profile
    plan = st.session_state.current_plan
    
    st.header(f"Your Goal: {profile['goal']}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Your Current AI-Generated Plan")
        with st.container(border=True):
            st.markdown(f"### {plan['plan_title']}")
            st.markdown(plan['ai_feedback'])
            st.markdown("---")
            st.markdown(f"**Your Diet:**\n{plan['diet']}")
            st.markdown(f"**Your Workout:**\n{plan['workout']}")

        st.subheader("Your Profile")
        with st.container(border=True):
            st.metric("Current Weight", f"{profile['start_weight']} kg")
            st.metric("Goal Interval", f"{profile['time_interval_weeks']} weeks")

    with col2:
        st.subheader("Log Your Progress")
        st.write(f"Your goal interval is {profile['time_interval_weeks']} weeks. When you're ready to check in, fill out the form below.")
        
        with st.form("progress_form"):
            current_weight = st.number_input("Your New Current Weight (kg)", min_value=40.0, max_value=200.0, value=profile['start_weight'], step=0.1)
            notes = st.text_area("How did the last period feel? (Optional)")
            
            submitted = st.form_submit_button("Analyze My Progress & Update My Plan")
            
            if submitted:
                # This is the "Core Loop" you described!
                
                # 1. Create a progress log
                progress_log = {
                    "current_weight": current_weight,
                    "notes": notes
                }
                
                # 2. Add to history
                st.session_state.progress_history.append(progress_log)
                
                with st.spinner("Analyzing your progress and generating new AI recommendations..."):
                    time.sleep(3)
                    
                    # 3. Call the "AI Brain" to get a new plan
                    new_plan = get_ai_recommendation(profile, progress_log)
                    
                    # 4. Update the user's plan in our "database"
                    st.session_state.current_plan = new_plan
                    
                    # 5. Update the user's "start_weight" for the *next* interval
                    st.session_state.user_profile['start_weight'] = current_weight
                
                st.success("Your plan has been updated by the AI!")
                st.balloons()
                st.rerun()

    # Display progress history
    if st.session_state.progress_history:
        st.subheader("Your Progress History")
        # Create a DataFrame from the history for nice formatting
        history_df = pd.DataFrame(st.session_state.progress_history)
        # Add the starting weight to the beginning
        initial_state = pd.DataFrame([{"current_weight": st.session_state.user_profile["start_weight"], "notes": "Initial Profile"}])
        full_history = pd.concat([initial_state, history_df]).reset_index(drop=True)
        full_history.index.name = "Check-in #"
        st.dataframe(full_history)

