from crew import build_crew


def main():
    input_data = {
        "crop": "maize",
        "location": "Masindi",
        "quantity_kg": 800,
        "need_cash_in_days": 14,
    }

    crew = build_crew(input_data)
    result = crew.kickoff()

    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
