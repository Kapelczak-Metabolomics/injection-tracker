import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from pyopenms import *
import hashlib
import sqlite3
import os

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Database setup
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password TEXT)''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username=?", (username,))
    result = c.fetchone()
    conn.close()
    if result and result[0] == hash_password(password):
        return True
    return False

# Initialize database
init_db()

# Main app
def main():
    st.title("Total Ion Chromatogram Viewer")
    
    if not st.session_state.logged_in:
        st.subheader("Login")
        login_tab, signup_tab = st.tabs(["Login", "Sign Up"])
        
        with login_tab:
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login"):
                if verify_user(username, password):
                    st.session_state.logged_in = True
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        
        with signup_tab:
            new_username = st.text_input("Username", key="signup_username")
            new_password = st.text_input("Password", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            if st.button("Sign Up"):
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                elif not new_username or not new_password:
                    st.error("Please fill in all fields")
                else:
                    if add_user(new_username, new_password):
                        st.success("Account created successfully! Please login.")
                    else:
                        st.error("Username already exists")
    
    else:
        # Logout button
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()
            
        # File uploader
        uploaded_file = st.file_uploader("Upload an mzXML file", type=["mzXML"])

        if uploaded_file is not None:
            # Save the uploaded file temporarily
            with open("temp.mzXML", "wb") as f:
                f.write(uploaded_file.getbuffer())

            try:
                # Load the mzXML file using PyOpenMS
                exp = MSExperiment()
                MzXMLFile().load("temp.mzXML", exp)

                # Extract the total ion chromatogram (TIC)
                chromatograms = exp.getChromatograms()
                if len(chromatograms) > 0:
                    tic = chromatograms[0]
                    times = [point.getRT() for point in tic]
                    intensities = [point.getIntensity() for point in tic]

                    # Plot the TIC
                    fig, ax = plt.subplots()
                    ax.plot(times, intensities, label="TIC")
                    ax.set_xlabel("Time (s)")
                    ax.set_ylabel("Intensity")
                    ax.set_title("Total Ion Chromatogram")
                    ax.legend()

                    # Display the plot in Streamlit
                    st.pyplot(fig)
                else:
                    st.error("No chromatograms found in the uploaded file.")
            
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
            
            finally:
                # Clean up temporary file
                if os.path.exists("temp.mzXML"):
                    os.remove("temp.mzXML")

if __name__ == "__main__":
    main()
