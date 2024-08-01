# Run the application in the background
echo "** Running application in the background..."
lsof -t -i tcp:8501 | xargs kill -9
nohup streamlit run src/main.py &
