# --------------------------
# 1. Imports + API setup
# --------------------------
import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
import time

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --------------------------
# 2. Page Config
# --------------------------
st.set_page_config(page_title="AI Fitness Coach", page_icon="💪")

# --------------------------
# 3. CSS Styling
# --------------------------
st.markdown(""" 
    <style>
        /* Background Gradient */
.stApp {
    background: linear-gradient(to bottom right, #80A1BA, #B0E0E6);
    background-attachment: fixed;
}
    /* Hide default Streamlit header/footer */
        header {visibility: hidden;}
        footer {visibility: hidden;}

        /* Chat container */
        .chat-container {
            max-height: 500px;
            overflow-y: auto;
            padding: 10px;
            border-radius: 12px;
            background-color: #fafafa;
            border: 1px solid #ddd;
            margin-bottom: 20px;
        }

        /* Chat bubble base */
        .msg-bubble {
            padding: 12px 16px;
            margin: 10px;
            border-radius: 18px;
            max-width: 80%;
            font-size: 15px;
            line-height: 1.5;
            display: inline-block;
        }

        /* User bubble */
        .msg-user {
            background: #DCF8C6;
            color: #111;
            margin-left: auto;
            margin-right: 0;
            border: 1px solid #cce8b5;
        }

        /* Assistant bubble */
        .msg-bot {
            background: #ffffff;
            color: #111;
            border: 1px solid #e6e6e6;
            margin-right: auto;
            margin-left: 0;
        }

        /* Avatar row */
        .msg-row {
            display: flex;
            align-items: flex-start;
        }

        .msg-row.user {
            justify-content: flex-end;
        }

        .avatar {
            width: 38px;
            height: 38px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .avatar.user {
            margin-left: 8px;
            margin-right: 0px;
        }

        /* Typing indicator */
        .typing {
            height: 20px;
            padding-left: 15px;
            font-style: italic;
            color: #777;
            animation: blink 1s infinite;
        }

        @keyframes blink {
            0% { opacity: 0.2; }
            50% { opacity: 1; }
            100% { opacity: 0.2; }
        }

    </style>
""", unsafe_allow_html=True)

# --------------------------
# 4. Profile Inputs
# --------------------------
st.title("💬 Your AI Fitness Coach")
st.markdown("Get personalized workout and diet plans based on your fitness goals and lifestyle.")

# Goal selector
goal = st.selectbox("🎯 What's your fitness goal?", ["Weight Loss", "Bulking", "Endurance", "General Fitness"])

# Optional calorie calculator
st.markdown("### 🔢 Calorie Estimator (Optional)")
name = st.text_input("👤 What is your name?", value=st.session_state.get("name",""))
age = st.number_input("Age", min_value=10, max_value=100, value=30)
weight = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=70.0)
height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=170.0)
gender = st.radio("Gender", ["Male", "Female"])
activity_level = st.selectbox("Activity Level", [
    "Sedentary (little or no exercise)",
    "Lightly active (1–3 days/week)",
    "Moderately active (3–5 days/week)",
    "Very active (6–7 days/week)",
    "Super active (twice/day)"
])

st.session_state["name"] = name

# Estimate calories (Mifflin-St Jeor Equation)
def estimate_calories():
    bmr = 10 * weight + 6.25 * height - 5 * age + (5 if gender == "Male" else -161)
    activity_multiplier = {
        "Sedentary (little or no exercise)": 1.2,
        "Lightly active (1–3 days/week)": 1.375,
        "Moderately active (3–5 days/week)": 1.55,
        "Very active (6–7 days/week)": 1.725,
        "Super active (twice/day)": 1.9
    }
    return round(bmr * activity_multiplier[activity_level], 2)

calories = estimate_calories()
st.markdown(f"**Estimated daily calories:** {calories} kcal")

# --------------------------
# 5. Initialize chat history
# --------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": 
         "You are a certified fitness instructor. Provide guidance based on user profile."},
        {"role": "user", "content": f"I have the following personal information {name}, {age}, {weight}, {height}, {gender}, {activity_level}"}
    ]

# --------------------------
# 6. CHAT DISPLAY CONTAINER
# --------------------------
chat_box = st.container()

with chat_box:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)

    for msg in st.session_state.messages[1:]:  # skip system msg
        if msg["role"] == "user":
            st.markdown(f"""
                <div class="msg-row user">
                    <div class="msg-bubble msg-user">{msg['content']}</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="msg-row">
                    <div class="msg-bubble msg-bot">{msg['content']}</div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# --------------------------
# 7. STEP 4 — CHAT INPUT HANDLER 
# --------------------------
user_input = st.chat_input("Ask your coach...or Suggest a 4-day work out plan...")


if user_input:
    # Add user goal and calorie context
    st.chat_message("user").markdown(f"**You:** {user_input}")
    context = f"My goal is {goal.lower()}. I am {age} years old, weigh {weight} kg, and my estimated daily calories are {calories} kcal. This is my gender{gender}, and this is my name {name}."
    st.session_state.messages.append({"role": "user", "content": context + " " + user_input})
    
    if "user_name" not in st.session_state:
        st.session_state.user_name = "Junea"   # sample only, replace with your form input

    # Typing indicator
    typing = st.empty()
    typing.markdown(
        '<div class="typing">Coach is typing...</div>',
        unsafe_allow_html=True
    )

    # Call OpenAI
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=st.session_state.messages
    )

    bot_reply = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    
    # Display chat history with NAME + styled bubble
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(
                f"""
                <div class="user-chat">
                    <div class="name-label">{st.session_state.user_name}</div>
                    <div class="chat-bubble-user">{msg['content']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div class="bot-chat">
                    <div class="name-label">Coach</div>
                    <div class="chat-bubble-bot">{msg['content']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # Remove typing indicator
    typing.empty()

    # Refresh UI to show new messages
    st.rerun()

# --------------------------
# 8. Reset Button
# --------------------------
if st.button("🔄 Reset Chat 👋🏻"):
    st.success(f"🎉 Great job today!, {st.session_state.name or 'my dear friend'} 🌿 "
               "You’ve taken another step toward your fitness goals. Remember, consistency is key — keep going strong! 💪")
    st.session_state.messages = []
    st.rerun()