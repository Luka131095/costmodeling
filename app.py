import streamlit as st
import openai
import os
from dotenv import load_dotenv
import base64
import time

# Set the page title for the browser tab
st.set_page_config(page_title="Cost Engineering Bot")

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
print("Script started")  # Debug print

# Static image with CSS to center and shift upward using transform
image_path = "rimac.svg"
if os.path.exists(image_path):
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
        st.markdown(
            f"""
            <style>
            .image-container {{
                text-align: center; /* Center the container */
                padding-top: 0px; /* Ensure no extra padding pushes image down */
            }}
            .image-container img {{
                max-width: 500px;
                height: auto;
                display: block;
                margin: 0 auto; /* Center horizontally */
                transform: translateY(-50px); /* Shift upward by 50 pixels */
                pointer-events: none; /* Disable interactivity */
            }}
            div[data-testid="stChatInput"] {{
                position: fixed !important;
                bottom: 40px !important; /* Chat input position */
                width: 100% !important;
                max-width: 700px !important;
                left: 50% !important;
                transform: translateX(-50%) !important;
                z-index: 1000 !important;
            }}
            .footer-text {{
                position: fixed !important;
                bottom: 10px !important; /* Below chat input */
                width: 100% !important;
                max-width: 700px !important;
                left: 50% !important;
                transform: translateX(-50%) !important;
                z-index: 900 !important;
                text-align: center;
                font-size: 14px;
                color: #666;
            }}
            </style>
            <div class="image-container">
                <img src="data:image/svg+xml;base64,{encoded}" alt="Rimac Logo">
            </div>
            """,
            unsafe_allow_html=True
        )
else:
    st.write(f"Debug: Image not found at {image_path}")

# Define type_writer function for model responses and initial message
def type_writer(text):
    for char in text:
        yield char
        time.sleep(0.005)  # Faster speed (0.005s per char)

# Define get_response function before it's called
def get_response():
    print("Processing query with history")  # Debug print
    try:
        # Build the full message history including the system prompt
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages
        response = openai.chat.completions.create(
            model="gpt-5.1",
            messages=messages,
            temperature=1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# Define SYSTEM_PROMPT
SYSTEM_PROMPT = """
You are the Cost Engineering Assistant specialized in building cost models for Powertrain and Chassis components.
Your mission is to support cost engineers in building **structured, replicable cost models** for Powertrain and Chassis components.
There are only three possible types of responses: 
1.) Responses that create cost models
2.) Responses that explain and clarify cost models 
3.) Response if user goes off topic - politely and briefly remind user of your main objective and never agree to go off topic.

### Core Principles:
- Think like a senior cost engineer with deep knowledge of chassis and powertrain components.  
- Always deconstruct a component into **sequential manufacturing steps** 
- The cost needs to be looked at as driven by two kinds of costs: fixed and variable. Fixed cost is cost of tooling - cost incurred in order to set up the process which can produce multiple control arms. Variable cost is associated with any kind of cost linked with cost of producing one additional unit of control arm. Therefore - cost model output should be two separate tables - one for fixed cost and one for variable cost.


### Output Format for cost model response (mandatory):

| Manufacturing Step | Description | % in total cost #fixed or variable | Cost driver 1 | Cost driver 2 | Cost driver n | 
|--------------------|-------------|------------------------------------|---------------|---------------|---------------|

Table comment: Add as many drivers as needed and replace "Cost driver" with actual name of the driver. For columns which describe cost drivers, along with cost driver description, the percentage of share of cost driver in that manufacturing step should be provided. In other words, every manufacturing step is driven by multiple cost drivers and percentage should be assigned to each cost driver for cost engineer to get a feel for how each cost driver contributes to the cost of that manufacturing step.


### Responsibilities:
1. **Process Deconstruction**: List all manufacturing steps in logical order.  
2. **Cost Driver Assignment**: For each step, populate the table with cost drivers. When necessary, precisely specify material number, tool and even standard for corresponding procedure (standard only if exists for particular step)


"""

# Create a container for the chat input and footer to render immediately after logo
input_container = st.container()
with input_container:
    prompt = st.chat_input("Your question...")
    st.markdown(
        '<div class="footer-text">Developed by Luka Vrzogic</div>',
        unsafe_allow_html=True
    )

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "initialized" not in st.session_state:
    st.session_state.initialized = False

# Create a container for chat history
chat_container = st.container()

# Display predefined first message and chat history
with chat_container:
    if not st.session_state.initialized:
        first_message = """Hello! This is Hypercar Cost Modeling tool.  

Main objective is to support cost engineers in two key ways:  
1. Help them build **structured cost models** for chassis and powertrain components, breaking each part down into manufacturing steps with detailed cost drivers.  
2. **Explain and clarify** any part of a cost model, so they understand how processes and drivers contribute to the total cost.  

Feel free to name any chassis or powertrain component, and the tool will attempt to create a cost model that reflects the cost breakdown of that component.  

All of tool's outputs follow a standardized structure, making them ready for benchmarking and cost database integration.  
"""
        st.session_state.messages.append({"role": "assistant", "content": first_message})
        with st.chat_message("assistant"):
            "".join(char for char in st.write_stream(type_writer(first_message)))
            print(f"Rendered first message: {first_message}")
        st.session_state.initialized = True
    else:
        # Display chat history with markdown (instant display)
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                print(f"Rendered message: {msg['content']}")

# Handle user input after chat input is rendered
if prompt:
    print(f"Received prompt: {prompt}")
    st.session_state.messages.append({"role": "user", "content": prompt})
    with chat_container:
        with st.chat_message("user"):
            st.markdown(prompt)  # Display user query instantly
            print("User message displayed")

        with st.chat_message("assistant"):
            response = get_response()
            "".join(char for char in st.write_stream(type_writer(response)))  # Typing effect for model response
            st.session_state.messages.append({"role": "assistant", "content": response})
            print(f"Assistant response: {response}")