import os
from src.utils import setup_logger, get_api_credentials

logger = setup_logger("Main")
creds = get_api_credentials()

def start_simulation():
    logger.info("Starting trade simulator with OKX credentials.")
    logger.info(f"API Key Loaded: {bool(creds['api_key'])}")
    print("✅ Trade simulator initialized")
    if creds["api_key"]:
        print("🔐 API key loaded successfully")
        print("✅ Launching Streamlit UI...")
        os.system("start cmd /k streamlit run ui/main_ui.py")
    else:
        print("❌ API key not found in .env")
    
    """print("✅ Launching Streamlit UI...")
    subprocess.run(["streamlit", "run", "ui/main_ui.py"])
    """


if __name__ == "__main__":
    start_simulation()
