import time
import threading

from matches.services.results_updater import update_match_results
from scoring.services.scoring_engine import run_scoring


def auto_update_loop():
    while True:
        try:
            print("🔄 Running auto update...")

            updated = update_match_results()
            scored = run_scoring()

            print(f"✅ Matches updated: {updated}")
            print(f"✅ Predictions scored: {scored}")

        except Exception as e:
            print("❌ ERROR in auto update:", e)

        # ⏱️ 30 minutos = 1800 segundos
        time.sleep(1800)



_started = False


def start_auto_update():
    thread = threading.Thread(target=auto_update_loop)
    thread.daemon = True  # ✅ no bloquea Django
    thread.start()