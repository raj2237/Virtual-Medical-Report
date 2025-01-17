import streamlit as st
from google_api_key import google_api_key
import google.generativeai as genai

# Configure API key
genai.configure(api_key=google_api_key)

# Configure generation parameters
generation_config = {
    "temperature": 1.2,
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 1024
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# System prompt with detailed instructions
system_prompts = """
    You are a highly skilled medical analyst specializing in image-based diagnosis. Carefully analyze any uploaded medical image 
    following this format:

    **Detailed Analysis**: Provide an in-depth examination of abnormalities, patterns, or findings present.
    **Analysis Report**: Offer a structured summary of your observations.
    **Recommendations**: List further tests, consultations, or imaging requirements.
    **Treatments**: Suggest comprehensive treatment plans and methods for faster recovery.

    Notes:
    1. Include a disclaimer: "Consult with a doctor before making medical decisions."
    2. Indicate unclear or indeterminate areas explicitly if applicable.
"""

# Initialize model
model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=generation_config, safety_settings=safety_settings)

# Streamlit UI Settings

st.set_page_config(page_title="Visual Medical Assistant AI", layout="wide")
st.markdown("""
    <style>
        /* Set background color */
        .main {
            background-color: #2f2f2f; /* Dark gray */
        }
        
        /* Style header text (title, subheader) */
        h1, h2 {
            color: #4CAF50; /* Green */
        }
        
        /* Style all generated (dynamic) text */
        .generated-text {
            color: white; /* White text for generated content */
        }

        /* Style the file uploader to remove the white background */
        div[data-testid="stFileUploader"] {
            background-color: #444; /* Darker gray */
            border: 1px solid #4CAF50; /* Green border */
            border-radius: 10px;
            color: white; /* White text */
        }

        /* File uploader hover effect */
        div[data-testid="stFileUploader"]:hover {
            border: 1px solid #45a049; /* Slightly darker green */
        }

        /* File uploader text and icon */
        div[data-testid="stFileUploader"] label {
            font-size: 18px;
        }

        /* Buttons styling */
        .stButton>button {
            background-color: #4CAF50; /* Green */
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
        }

        .stButton>button:hover {
            background-color: #45a049; /* Darker green on hover */
        }

        /* Style spinner text */
        .stSpinner {
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)

# App layout and content
st.title(" Visual Medical Assistant AI 👨🏻‍⚕️")
st.subheader("An AI crafted for medical analysis using images ❤️‍🩹")

# Upload the file
file_uploaded = st.file_uploader("📂 Upload the image for analysis", type=['png', 'jpg', 'jpeg'])

if file_uploaded:
    st.image(file_uploaded, width=200, caption="✅ Uploaded image")

# Generate analysis button
submit = st.button("Generate Analysis")

if submit and file_uploaded:
    with st.spinner("Analyzing image and generating detailed report..."):
        try:
            image_data = file_uploaded.getvalue()  # Binary data of the image
            image_parts = [{"mime_type": "image/jpg", "data": image_data}]
            prompt_parts = [image_parts[0], system_prompts]
            
            # Generate content
            response = model.generate_content(prompt_parts)
        except Exception as e:
            st.error(f"An error occurred during generation: {e}")
            response = None

    if response and response.text:
        st.success("Analysis generated successfully!✅")
        st.header("Detailed Analysis Report 📝")

        detailed_analysis = ""
        analysis_report = ""
        recommendations = ""
        treatments = ""

        # Check for sections in the response text
        try:
            if "\nDetailed Analysis:" in response.text and "\nAnalysis Report:" in response.text:
                detailed_analysis = response.text.split("\nDetailed Analysis:")[1].split("\nAnalysis Report:")[0].strip()
            if "\nAnalysis Report:" in response.text and "\nRecommendations:" in response.text:
                analysis_report = response.text.split("\nAnalysis Report:")[1].split("\nRecommendations:")[0].strip()
            if "\nRecommendations:" in response.text and "\nTreatments:" in response.text:
                recommendations = response.text.split("\nRecommendations:")[1].split("\nTreatments:")[0].strip()
            if "\nTreatments:" in response.text:
                treatments = response.text.split("\nTreatments:")[1].strip()
        except IndexError:
            st.warning("Could not parse all sections of the response. Displaying full response instead.")
        
        # Show response sections if available
        if detailed_analysis:
            with st.expander("Detailed Analysis 🔬", expanded=True):
                st.write(detailed_analysis, use_container_width=True)
        if analysis_report:
            with st.expander("Analysis Report 📊", expanded=False):
                st.write(analysis_report, use_container_width=True)
        if recommendations:
            with st.expander("Recommendations ✅", expanded=False):
                st.write(recommendations, use_container_width=True)
        if treatments:
            with st.expander("Treatments 💊", expanded=False):
                st.write(treatments, use_container_width=True)
        
        # Fallback: Show entire response if sections were missing
        if not (detailed_analysis or analysis_report or recommendations or treatments):
            st.write(response.text, use_container_width=True)
    else:
        st.error("Failed to generate analysis. The response was empty or invalid.")
