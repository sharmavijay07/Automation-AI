"""
Minimal Streamlit app for testing
This version has minimal dependencies to identify auto-stop issues
"""

import streamlit as st

# Page configuration - MUST be first
st.set_page_config(
    page_title="AI Assistant Test",
    page_icon="🤖",
    layout="wide"
)

def main():
    """Main function for the test app"""
    try:
        st.title("🤖 AI Task Automation Assistant - Test Version")
        st.write("✅ Streamlit is running successfully!")
        
        # Test basic functionality
        st.markdown("### Basic Functionality Test")
        
        if st.button("Test Button"):
            st.success("Button clicked successfully!")
        
        user_input = st.text_input("Test Input:", placeholder="Type something here...")
        if user_input:
            st.write(f"You typed: {user_input}")
        
        # Test session state
        if "click_count" not in st.session_state:
            st.session_state.click_count = 0
        
        if st.button("Click Counter"):
            st.session_state.click_count += 1
        
        st.write(f"Button clicked {st.session_state.click_count} times")
        
        st.markdown("---")
        st.info("If you can see this message, Streamlit is working correctly!")
        st.info("The main app should also work. Try running: streamlit run streamlit_app.py --server.port=8501")
        
    except Exception as e:
        st.error(f"Error in test app: {str(e)}")

if __name__ == "__main__":
    main()
else:
    main()