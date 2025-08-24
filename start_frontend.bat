@echo off
echo 🎨 Starting AI Task Automation Assistant Frontend
echo ===============================================

echo.
echo 🌐 Starting Streamlit frontend...
echo Frontend will be available at: http://localhost:8501
echo.
echo 💡 Make sure the backend is running first!
echo Backend URL: http://127.0.0.1:8000
echo.
echo 📝 Logs:
streamlit run streamlit_app.py --server.port=8501