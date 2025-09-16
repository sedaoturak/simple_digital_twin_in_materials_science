import streamlit as st
import time

# ----- Analytical functions on grain size and strength ----- #

def predict_grain_size(sigma):
	""" This function takes target yield strength of the part and predicts the necessary grain size by Hall-Petch relation,
	sigma = sigma_0 + k * (d^(-0.5))
	
	sigma : the yield strength
	sigma_0 : the friction stress (the stress needed to move dislocations within a single, infinitely large grain). 
			  It is 180 MPa for 304L SS.
	k : the Hall-Petch coefficient, or the strengthening coefficient, which measures the effectiveness of grain 
		boundaries at blocking dislocation motion. It is 7589 # MPa·μm^0.5 for 304L SS.
	d : the grain size diameter in μm"""
	
	sigma_0 = 180 # MPa
	k = 7589 # MPa·μm^0.5

	d = ((sigma - sigma_0) / k)**-2
	return d

def predict_annealing_time(d_0, d):
	"""This function takes the initial grain size and final grain size of the part and predicts the annealing time 
	to obtain the microstructure with the final grain size given target yield strength.
	The relation: (d)^n - (d_0)^n = K * t

	d : the final grain size diameter in μm
	d_0 : the initial grain size diameter in μm
	n : a time-independent material constant (n≥2). It is 2 for 304L stainless steel
	K : a time-indeppendent material constant. It is 8075 μm^2/h
	t : the annealing time in hour
	"""
	n = 2
	K = 8075
	t = ( d**n - d_0**n ) / K

	return t

####################################
# ---------- App starts ---------- #
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    # set the page features like name, logo on tab
    st.set_page_config(page_title='Case 1', layout='wide', initial_sidebar_state="auto", menu_items=None)

    st.write("""
            ### Case 2 – Real-time Heat Treatment Optimizer of Steel Disks
            This demo shows how Digital Twins can be used to monitor and optimize \
            the heat treatment process by the real-time prediction of the final grain \
            size of the disc with a target yield strength.""")
    
    # Initialize session state for the button click and progress bar
    if 'button_clicked' not in st.session_state:
        st.session_state.button_clicked = False
    if 'is_loaded' not in st.session_state:
        st.session_state.is_loaded = False
    if 'show_progress' not in st.session_state:
        st.session_state.show_progress = False
    if 'is_heated' not in st.session_state:
        st.session_state.is_heated = False

    # --- Section 1: Steel Disc - Initial State ---
    with st.container(border=True):
        st.markdown("<h3 style='text-align: center;'>Steel disc before heat treatment</h3>", unsafe_allow_html=True)
        image_file_path = "disc_initial.png"
        img_col1, img_col2, img_col3 = st.columns([1, 1, 1])
        with img_col2:
            st.image(image_file_path, caption="Steel Disc - initial grain size, g₀", width=300)
        st.markdown("""
            **Description:** The steel disc of 304L stainless steel is sent to heat treatment process for annealing process. 
              The part has an **initial grain size (g₀)**.
            """)
        
        # take the initial grain size (g_0) information from the previous process
        g_0 = st.number_input("Enter the initial grain size in μm:", min_value=10, value=300, step=10)
        st.session_state.g_0 = g_0
        
        # take the target strength according to customer's order
        sigma = st.number_input("Enter the target yield strength in MPa:", min_value=400, value=2000, step=50)
        st.session_state.sigma = sigma

        # predict final grain size that would give this target strength
        st.session_state.g_1 = predict_grain_size(st.session_state.sigma)

        # predict annealing time that is necessary to obtain final grain size and the target strength
        st.session_state.time = predict_annealing_time(st.session_state.g_0, st.session_state.g_1)

        if st.button("Load the part into furnace"):
            st.session_state.is_loaded = True

    # This condition controls the visibility of the rest of the flowchart
    if st.session_state.is_loaded:
        st.markdown("<p style='text-align:center; font-size: 20px;'>&#x2193;</p>", unsafe_allow_html=True)


        # --- Section 2: Heat Treatment ---
        with st.container(border=True):
            st.markdown("<h3 style='text-align: center;'> Heat treatment process</h3>", unsafe_allow_html=True)
            # report the predicted final grain size and annealing time
            st.markdown(f"<p style='text-align: left;'> The part needs to have grain size of {round(st.session_state.g_1)} μm</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: left;'> The annealing time is {round(st.session_state.time)} hours.</p>", unsafe_allow_html=True)
            
            image_file_path_1 = "furnace_stop.jpg"
            image_file_path_2 = "furnace_burning.gif"

            if st.button("Start Heat Treatment"):
                    st.session_state.button_clicked = True
                    st.session_state.show_progress = True
            
            col2_1, col2_2, col2_3 = st.columns([1, 1, 1])
            with col2_2:
                image_placeholder = st.empty()
                image_placeholder.image(image_file_path_1, caption="Part is loaded to the furnace.")
                if st.session_state.button_clicked:
                    image_placeholder.image(image_file_path_2, caption="Heating in progress...")
                    if st.session_state.show_progress:
                        progress_bar = st.progress(0)
                        for percent_complete in range(101):
                            time.sleep(0.2)
                            progress_bar.progress(percent_complete)
                        progress_bar.empty()
                        st.session_state.show_progress = False
                    
                    image_placeholder.image(image_file_path_1, caption="Heat treatment complete!")
                else:
                    image_placeholder.image(image_file_path_1, caption="The furnace is ready for the process!")
            st.markdown("""
                **Description:** The steel disc undergoes the annealing **heat treatment** process at 1100°C.
                  This stage is defined by one parameter:
                * **Time ($t$):** The duration for which the disc is exposed to 1100°C.""")

            st.info("""Digital Twin's predictive model will predict the annealing time based on 
                    **initial grain size (g₀)** and **time ($t$)**.
                    It will adjust the time of the furnace direclty.""")
            
            # This button appears after the heat treatment is complete
            if st.session_state.button_clicked and not st.session_state.show_progress:
                st.divider()
                if st.button("Take the part from the furnace"):
                    st.session_state.is_heated = True

     # This condition controls the visibility of the rest of the flowchart after heat treatment
    if st.session_state.is_heated:
        st.markdown("<p style='text-align:center; font-size: 20px;'>&#x2193;</p>", unsafe_allow_html=True)




        # --- Section 3: Steel Disc - Final State ---
        with st.container(border=True):
            st.markdown("<h3 style='text-align: center;'> Steel disc after heat treatment</h3>", unsafe_allow_html=True)
            image_file_path = "disc_final.png"
            img_col1, img_col2, img_col3 = st.columns([1, 2, 1])
            with img_col2:
                st.image(image_file_path, caption="Steel disc - final grain size, g₁", width=300)
            st.markdown(f"""
                **Description:** The steel disc was annealed at 1100°C for {round(st.session_state.time)} hours to obtain 
                final grain size of {round(st.session_state.g_1)} μm and yield strength of {round(st.session_state.sigma)} MPa.
                """, unsafe_allow_html=True)
