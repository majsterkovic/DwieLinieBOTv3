"""DwieLinieBOT v3 – łączy 2 losowe tytuły znalezisk z Wykopu w jedno zdanie."""

import random
import WykopAPI


def extract_titles(links_data: list[dict]) -> list[tuple[str, int]]:
    """Return list of (title, id) from API response, keeping only titles with spaces."""
    return [
        (item["title"], item["id"])
        for item in links_data
        if "title" in item and " " in item["title"]
    ]


def generate_mixed_title(titles: list[tuple[str, int]]) -> tuple[str, tuple, tuple]:
    """Pick 2 random titles and merge them at the middle space.

    Returns (new_title, link_a, link_b).
    Raises ValueError if there aren't at least 2 usable titles.
    """
    if len(titles) < 2:
        raise ValueError(
            f"Za mało tytułów ze spacjami do połączenia (znaleziono {len(titles)}, potrzeba 2)."
        )

    link_a, link_b = random.sample(titles, 2)

    spaces_a = [i for i, ch in enumerate(link_a[0]) if ch == " "]
    spaces_b = [i for i, ch in enumerate(link_b[0]) if ch == " "]

    mid_a = spaces_a[len(spaces_a) // 2]
    mid_b = spaces_b[len(spaces_b) // 2]

    part_a = link_a[0][:mid_a]
    part_b = link_b[0][mid_b:]
    
    last_word = part_a.split()[-1].lower().strip(".,:;!?'\"") if part_a.split() else ""
    first_word = part_b.split()[0].lower().strip(".,:;!?'\"") if part_b.split() else ""
    
    if last_word == first_word and last_word != "":
        # Jeśli słowa na złączeniu są takie same, usuwamy je z początku drugiej połowy (part_b)
        split_b = part_b.split(maxsplit=1)
        part_b = " " + split_b[1] if len(split_b) > 1 else ""
        
    new_title = part_a + part_b
    return new_title, link_a, link_b


def build_entry_content(new_title: str, link_a: tuple, link_b: tuple) -> str:
    """Format the mikroblog entry content."""
    return (
        f"**{new_title}**\n\n"
        f"https://www.wykop.pl/link/{link_a[1]}\n"
        f"https://www.wykop.pl/link/{link_b[1]}\n\n"
        'O co w tym chodzi?\n'
        'Jestem botem i losowo tworzę "zdanie" łącząc 2 tytuły z popularnych znalezisk.\n\n'
        "Tag do obserwowania / czarnolistowania #dwielinie"
    )


def rob_wpis():
    print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Zaczynam publikację...")
    try:
        api = WykopAPI.WykopAPI()
        api.refresh_user_token()

        response = api.get_links(page="1", sort="newest", link_type="homepage")
        titles = extract_titles(response["data"])

        new_title, link_a, link_b = generate_mixed_title(titles)
        content = build_entry_content(new_title, link_a, link_b)
        
        print("=== Wygenerowany wpis ===")
        print(content)
        
        result = api.post_entry(content)
        print("\n✅ Opublikowano pomyślnie:", result.get("data", {}).get("id"))
    except Exception as err:
        print("❌ Wystąpił błąd podczas generowania lub publikacji wpisu:", err)

def main():
    import os
    import time
    import schedule
    from dotenv import load_dotenv

    load_dotenv()
    
    print("Bot uruchomiony. Harmonogram włączony (08:00, 12:00, 16:00, 20:00).")
    
    schedule.every().day.at("04:00").do(rob_wpis)
    schedule.every().day.at("09:00").do(rob_wpis)
    schedule.every().day.at("14:00").do(rob_wpis)
    schedule.every().day.at("19:00").do(rob_wpis)
    schedule.every().day.at("00:00").do(rob_wpis)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    import time
    main()