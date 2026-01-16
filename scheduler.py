import argparse
import time

import schedule

from modules.daily_runner import default_sports, persist_daily_predictions


def run_daily_job(sports):
    output_path = persist_daily_predictions(sports)
    print(f"Daily predictions saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Daily JayMoneyPickz runner")
    parser.add_argument(
        "--time",
        default="09:00",
        help="Local time to run daily job (HH:MM, 24-hour).",
    )
    parser.add_argument(
        "--sports",
        nargs="*",
        default=default_sports(),
        help="Sports to include in the daily run.",
    )
    args = parser.parse_args()

    schedule.every().day.at(args.time).do(run_daily_job, args.sports)
    print(f"Scheduled daily predictions at {args.time} for {', '.join(args.sports)}.")

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
