from backend.app import create_app
from backend.tasks.reminders import send_daily_reminders
from backend.tasks.reports import generate_monthly_reports
import sys

def main():
    print("Initializing App Context...")
    app = create_app()
    with app.app_context():
        print("\n--- Triggering Appointment Reminders ---")
        try:
            reminder_count = send_daily_reminders()
            print(f"Success: {reminder_count} reminders processed.")
        except Exception as e:
            print(f"Error triggering reminders: {e}")

        print("\n--- Triggering Monthly Activity Reports ---")
        try:
            report_msg = generate_monthly_reports()
            print(f"Success: {report_msg}")
        except Exception as e:
            print(f"Error triggering reports: {e}")

if __name__ == "__main__":
    main()
