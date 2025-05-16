import streamlit as st
from ai_helpers import generate_question, generate_feedback

# --- Password Check ---
def check_password():
    """Returns True if the user had the correct password."""

    # Read password from Streamlit secrets or default.
    
    correct_password = st.secrets.get("APP_PASSWORD", "default_password") # Replace "default_password" ONLY for local testing if needed

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.session_state["password_correct"] = False # Initialize password state

    if st.session_state["password_correct"]:
        # Password previously entered correctly
        return True

    # Show input for password.
    password = st.text_input("Enter Password", type="password", key="password_input")

    if not password:
        st.stop() # Don't render the rest of the app if password isn't entered

    if password == correct_password:
        # Password correct, set state and rerun
        st.session_state["password_correct"] = True
        st.rerun() # Rerun to show the app immediately
    elif password:
        # Password incorrect
        st.error("😕 Password incorrect")
        st.session_state["password_correct"] = False

    return False


if not check_password():
    st.stop() # Do not continue if check_password returns False


# --- Original App Code Starts Here ---
st.set_page_config(layout="wide")

st.title(" Interview Coach")

if 'session_active' not in st.session_state:
    st.session_state.session_active = False
    st.session_state.question_num = 1
    st.session_state.questions = []
    st.session_state.answers = []
    st.session_state.feedbacks = []
    st.session_state.job_title = ""
    st.session_state.difficulty = "easy"

with st.sidebar:
    st.header("⚙️ Setup")
    if not st.session_state.session_active:
        st.write("Enter your details to start practicing!")
        job_title_input = st.text_input("Enter your job title", placeholder="e.g., Software Engineer")
        seniority_input = st.selectbox("Select your seniority level", ["Junior", "Mid", "Senior"])
        
        if st.button("🚀 Start Interview Prep"):
            if job_title_input:
                st.session_state.session_active = True
                st.session_state.job_title = job_title_input
                st.session_state.difficulty = {"Junior": "easy", "Mid": "medium", "Senior": "hard"}[seniority_input]
                st.session_state.question_num = 1
                st.session_state.questions = []
                st.session_state.answers = []
                st.session_state.feedbacks = []
                st.rerun()
            else:
                st.warning("Please enter a job title.")
    else:
        st.write(f"**Current Role:** {st.session_state.job_title}")
        st.write(f"**Level:** {st.session_state.difficulty.capitalize()}")
        if st.button("🔁 Start Over"):
            st.session_state.session_active = False
            st.session_state.question_num = 1
            st.session_state.questions = []
            st.session_state.answers = []
            st.session_state.feedbacks = []
            st.session_state.job_title = ""
            st.session_state.difficulty = "easy"
            st.rerun()

if st.session_state.session_active:
    if st.session_state.question_num <= 5:
        st.subheader(f"Question {st.session_state.question_num} of 5")
        st.progress((st.session_state.question_num -1) / 5)
        
        question = generate_question(st.session_state.job_title, st.session_state.difficulty)
        st.markdown(f"**🗣️ Question:** {question}")
        
        answer = st.text_area("Your answer:", key=f"answer_{st.session_state.question_num}", height=150)
        
        if st.button("✅ Submit Answer"):
            if answer:
                with st.spinner("Generating feedback..."):
                    feedback, recommendation = generate_feedback(question, answer)
                
                st.info(f"**📝 Feedback:** {feedback}")
                
                if recommendation == "easier" and st.session_state.difficulty != "easy":
                    st.session_state.difficulty = "easy" if st.session_state.difficulty == "medium" else "medium"
                elif recommendation == "harder" and st.session_state.difficulty != "hard":
                    st.session_state.difficulty = "medium" if st.session_state.difficulty == "easy" else "hard"
                
                st.session_state.questions.append(question)
                st.session_state.answers.append(answer)
                st.session_state.feedbacks.append(feedback)
                st.session_state.question_num += 1
                
                st.rerun()
            else:
                st.warning("Please provide an answer before submitting.")
    else:
        st.balloons()
        st.success("**🎉 Interview Prep Complete!** Here's your summary:")
        st.divider()
        
        for i in range(5):
            with st.expander(f"**Question {i+1}:** {st.session_state.questions[i]}", expanded= (i == 4)):
                st.write(f"**Your Answer:**")
                st.text(st.session_state.answers[i])
                st.write("--- ")
                st.write(f"**Feedback:**")
                st.info(st.session_state.feedbacks[i])
        
else:
    st.info("Enter your job details in the sidebar to the left and click 'Start Interview Prep' to begin! ✨")

st.caption("by AB")
# This comment triggers CodeRabbit to review the file
#             