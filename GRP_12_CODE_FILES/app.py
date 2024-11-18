import streamlit as st
import pandas as pd
import joblib
from sklearn.preprocessing import LabelEncoder, StandardScaler
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import time

# Set background color to white
st.markdown(
    """
    <style>
    body {
        background-color: white;
    }
    .stApp {
        background-color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Load the trained model
MODEL_PATH = "decision_tree_model.pkl"  # Update with your model path
model = joblib.load(MODEL_PATH)

# Helper function to send email with CSV attachment
def send_email_with_csv(fraud_data):
    sender_email = "harishsarav21@gmail.com"  # Your email
    receiver_email = "thayumanavan.12a@gmail.com"  # Receiver's email
    password = "mvum cwzp zbwj pdxu"  # Your Gmail app password

    if not sender_email or not receiver_email or not password:
        st.error("Email credentials are missing. Provide valid sender email, receiver email, and password.")
        return

    # Save fraud data to a temporary CSV file
    csv_filename = "fraudulent_records.csv"
    fraud_data.to_csv(csv_filename, index=False)

    # Email details
    subject = "Fraudulent Records Detected"
    body = "Fraudulent records were detected. Please find the details in the attached CSV file."

    # Create email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Add body text
    msg.attach(MIMEText(body, 'plain'))

    # Attach the CSV file
    with open(csv_filename, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={csv_filename}",
        )
        msg.attach(part)

    # Send email
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        #display_message("Fraud alert email with CSV attachment sent successfully!", success=True)
    except Exception as e:
        st.error(f"Failed to send email: {e}")

    # Clean up temporary file
    if os.path.exists(csv_filename):
        os.remove(csv_filename)

# Function to preprocess the data before prediction
def preprocess_data(data, scaler=None, label_encoders=None):
    # Define columns that need encoding
    columns_to_encode = ['fraud_reported', 'authorities_contacted', 'auto_model', 'policy_state']

    # Initialize label encoders if not provided
    if not label_encoders:
        label_encoders = {col: LabelEncoder() for col in columns_to_encode}

    # Encode categorical columns
    for col in columns_to_encode:
        if col in data.columns:
            if col not in label_encoders:
                label_encoders[col] = LabelEncoder()
            data[col] = label_encoders[col].fit_transform(data[col])

    # Scale numerical columns
    numerical_cols = data.select_dtypes(include=['float64', 'int64']).columns
    if not scaler:
        scaler = StandardScaler()
    data[numerical_cols] = scaler.fit_transform(data[numerical_cols])

    return data, scaler, label_encoders

# Function to display custom messages in black
def display_message(message, success=False):
    color = "green" if success else "black"  # Use green for success messages, black for others
    st.markdown(
        f"<p style='color: {color}; font-size: 16px; font-weight: bold;'>{message}</p>",
        unsafe_allow_html=True,
    )

# Function to display custom messages with specific colors
def display_custom_message(message, color="black"):
    st.markdown(
        f"<p style='color: {color}; font-size: 16px; font-weight: bold;'>{message}</p>",
        unsafe_allow_html=True,
    )

# Function to detect fraudulent records
def detect_fraud(data):
    # Preprocess the input data
    try:
        processed_data, scaler, label_encoders = preprocess_data(data)

        # Predict fraud using the trained model
        processed_data['fraud_prediction'] = model.predict(processed_data)

        # Check for fraudulent records
        fraud_data = processed_data[processed_data['fraud_prediction'] == 1]

        if not fraud_data.empty:
            display_message(f"{len(fraud_data)} fraudulent record(s) detected.", success=False)
            send_email_with_csv(fraud_data)
        else:
            display_message("No fraudulent records detected.", success=True)
        
        return processed_data

    except Exception as e:
        st.error(f"Error processing data: {e}")
        return None

# Function to display custom messages with a background color
def display_message_with_bg(message, bg_color="#D9F9E5", text_color="black"):
    st.markdown(
        f"""
        <div style='background-color: {bg_color}; padding: 10px; border-radius: 5px;'>
            <p style='color: {text_color}; font-size: 16px; font-weight: bold; margin: 0;'>{message}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Function to display the title, tagline, and logo
def display_title_with_logo():
    logo_path = r"C:\Users\tjtha\Downloads\insurance-policy-conceptdocument-report-shield-600nw-1600704538 (1).png"  # Correct path to the image file

    # Use Streamlit columns to align the title and logo
    col1, col2 = st.columns([3, 1])  # Adjust column widths
    with col1:
        # Title and tagline
        st.markdown(
            """
            <div style="text-align: center;">
                <h1 style="color: black; font-size: 28px; margin-bottom: 5px;">Automobile Insurance Fraud Detection System</h1>
                <p style="color: grey; font-weight: bold; font-style: italic; margin: 5px 0 0;">Driving Trust, Stopping Fraud.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        try:
            # Use st.image to display the logo directly from the file path
            st.image(logo_path, use_container_width=True, caption="")
        except Exception as e:
            st.error(f"Unable to load the logo. Please check the file path. Error: {e}")


# Function to simulate a pop-up window
def show_popup():
    st.markdown(
        """
        <style>
            .popup-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 9999;
            }
            .popup-content {
                background-color: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
                text-align: center;
                max-width: 400px;
                font-family: Arial, sans-serif;
            }
            .popup-content h4 {
                margin: 0;
                font-size: 18px;
                color: black;
            }
        </style>
        <div class="popup-overlay">
            <div class="popup-content">
                <h4>E-Mail sent with Fraudulent Report to the Admin(s)</h4>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    time.sleep(5)  # Display the pop-up for 5 seconds
    st.markdown('<style>.popup-overlay { display: none; }</style>', unsafe_allow_html=True)  # Hide the pop-up


# Streamlit app main logic
def main():
    st.sidebar.title("Fraud Detection System")
    st.sidebar.write("Analyze your Data Here!")

    # Sidebar file uploader
    uploaded_file = st.sidebar.file_uploader("Upload your file (CSV format)", type=["csv"])

    # Spacer to push content to the bottom
    st.sidebar.markdown("<div style='height: 300px;'></div>", unsafe_allow_html=True)

    # Names of Insurance Risk Analysts at the bottom
    st.sidebar.markdown(
        """
        <div style="width: 100%; text-align: center; color: white;">
            <h4 style="margin-bottom: 10px;">Insurance Risk Analysts</h4>
            <ul style="list-style: none; padding: 0; margin: 0; font-size: 12px; line-height: 1.8;">
                <li><strong>Susilasha M</strong> <em>(EMP ID - 21MIA1006)</em></li>
                <li><strong>Thayumanavan T</strong> <em>(EMP ID - 21MIA1007)</em></li>
                <li><strong>Revathy P</strong> <em>(EMP ID - 21MIA1016)</em></li>
                <li><strong>Harish A S</strong> <em>(EMP ID - 21MIA1021)</em></li>
                <li><strong>Harish S</strong> <em>(EMP ID - 21MIA1046)</em></li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Display title, tagline, and logo
    display_title_with_logo()

    if uploaded_file is not None:
        try:
            # Read the uploaded file into a DataFrame
            data = pd.read_csv(uploaded_file)

            # Display the uploaded data
            st.write("Uploaded Data Preview:")
            st.dataframe(data.head())

            # Detect fraud with spinner
            if st.button("Detect Fraud 🔎"):
                with st.spinner("Detecting fraud... Please wait."):
                    result = detect_fraud(data)

                # Save results to file and display
                if result is not None:
                    result_file = "fraud_detection_results.csv"
                    result.to_csv(result_file, index=False)

                    # Message for email success
                    st.markdown(
                        """
                        <div style="background-color: #FFEBCC; padding: 10px; border-radius: 5px; margin-bottom: 15px;">
                            <p style="color: black; font-size: 16px; font-weight: bold; margin: 0;">
                                Fraud alert email with CSV attachment sent successfully!
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    # Message for file-saving success
                    st.markdown(
                        """
                        <div style="background-color: #D9F9E5; padding: 10px; border-radius: 5px;">
                            <p style="color: black; font-size: 16px; font-weight: bold; margin: 0;">
                                Results saved to 'fraud_detection_results.csv'.
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    st.write("Processed Data Preview:")
                    st.dataframe(result)

                    # Finally, show the pop-up after all outputs
                    show_popup()

        except Exception as e:
            st.error(f"Error processing the uploaded file: {e}")

if __name__ == "__main__":
    main()