# TaskHive: Web Navigation Tools
# Simulates browser navigation, search, and data extraction for the Web Nav Agent.

import random
import hashlib
import time
from datetime import datetime
from typing import Any


# ─── Expanded Cinema Halls ────────────────────────────────────────────────────

CINEMA_HALLS = [
    # Mumbai
    {"name": "PVR Phoenix Mall",       "city": "Mumbai",    "format": ["IMAX 3D", "4DX", "2D", "3D"]},
    {"name": "INOX R-City Mall",       "city": "Mumbai",    "format": ["Dolby Atmos", "3D", "2D"]},
    {"name": "Cinepolis Andheri",      "city": "Mumbai",    "format": ["2D", "3D", "Dolby Vision"]},
    {"name": "Carnival Cinemas Kurla", "city": "Mumbai",    "format": ["2D", "3D"]},
    {"name": "MovieMax Mira Road",     "city": "Mumbai",    "format": ["2D", "3D"]},
    # Delhi NCR
    {"name": "PVR Priya Complex",      "city": "Delhi",     "format": ["IMAX 3D", "2D", "3D"]},
    {"name": "INOX Nehru Place",       "city": "Delhi",     "format": ["Dolby Atmos", "2D", "3D"]},
    {"name": "DT Cinemas Saket",       "city": "Delhi",     "format": ["2D", "3D"]},
    {"name": "Cinepolis Vasant Kunj",  "city": "Delhi",     "format": ["2D", "3D", "4DX"]},
    # Bangalore
    {"name": "PVR Orion Mall",         "city": "Bangalore", "format": ["IMAX 3D", "3D", "2D"]},
    {"name": "INOX Garuda Mall",       "city": "Bangalore", "format": ["Dolby Atmos", "2D", "3D"]},
    {"name": "Cinepolis Forum Mall",   "city": "Bangalore", "format": ["2D", "3D"]},
    {"name": "SPI Cinemas Brigade",    "city": "Bangalore", "format": ["2D", "3D", "Dolby Vision"]},
    # Hyderabad
    {"name": "PVR INOX Manjeera",      "city": "Hyderabad", "format": ["IMAX 3D", "2D", "3D"]},
    {"name": "Asian Cinemas Miyapur",  "city": "Hyderabad", "format": ["2D", "3D"]},
    {"name": "AMB Cinemas Gachibowli", "city": "Hyderabad", "format": ["Dolby Atmos", "4DX", "3D"]},
    # Chennai
    {"name": "SPI Cinemas Chennai",    "city": "Chennai",   "format": ["IMAX 3D", "2D", "3D"]},
    {"name": "Rohini Silver Screens",  "city": "Chennai",   "format": ["Dolby Atmos", "2D", "3D"]},
    # Pune
    {"name": "PVR Pavilion Mall",      "city": "Pune",      "format": ["3D", "2D", "IMAX 3D"]},
    {"name": "INOX Westend Mall",      "city": "Pune",      "format": ["Dolby Atmos", "2D", "3D"]},
    {"name": "Cinepolis Xion Mall",    "city": "Pune",      "format": ["2D", "3D"]},
]

BOOKING_SITES = [
    {"name": "BookMyShow", "url": "https://bookmyshow.com",  "logo": "🎬"},
    {"name": "PVR Cinemas","url": "https://pvrinemas.com",   "logo": "🎥"},
    {"name": "INOX Movies", "url": "https://inoxmovies.com", "logo": "🍿"},
]

TIME_SLOTS = {
    "morning":   ["9:30 AM",  "10:00 AM", "10:30 AM", "11:15 AM"],
    "afternoon": ["12:30 PM", "1:30 PM",  "2:00 PM",  "2:45 PM",  "3:30 PM"],
    "evening":   ["5:30 PM",  "6:00 PM",  "6:30 PM",  "7:00 PM",  "7:30 PM"],
    "night":     ["9:00 PM",  "9:30 PM",  "10:00 PM", "10:30 PM"],
}

LANGUAGES = ["Hindi", "English", "Hindi (Dubbed)", "Tamil (Dubbed)", "Telugu (Dubbed)"]


# ─── Movie Lookup ─────────────────────────────────────────────────────────────

MOVIE_DATABASE = {
    "mission impossible": {
        "title": "Mission: Impossible — The Final Reckoning",
        "rating": "UA", "genre": "Action / Thriller",
        "duration": "169 min", "cast": "Tom Cruise, Hayley Atwell, Simon Pegg",
    },
    "avengers": {
        "title": "Avengers: Endgame",
        "rating": "UA", "genre": "Action / Sci-Fi",
        "duration": "181 min", "cast": "Robert Downey Jr., Chris Evans, Scarlett Johansson",
    },
    "pushpa": {
        "title": "Pushpa 2: The Rule",
        "rating": "A", "genre": "Action / Drama",
        "duration": "179 min", "cast": "Allu Arjun, Rashmika Mandanna, Fahadh Faasil",
    },
    "deadpool": {
        "title": "Deadpool & Wolverine",
        "rating": "A", "genre": "Action / Comedy",
        "duration": "127 min", "cast": "Ryan Reynolds, Hugh Jackman",
    },
    "kalki": {
        "title": "Kalki 2898-AD",
        "rating": "UA", "genre": "Sci-Fi / Action",
        "duration": "181 min", "cast": "Prabhas, Deepika Padukone, Amitabh Bachchan",
    },
    "stree": {
        "title": "Stree 3",
        "rating": "UA", "genre": "Horror / Comedy",
        "duration": "142 min", "cast": "Rajkummar Rao, Shraddha Kapoor, Pankaj Tripathi",
    },
    "animal": {
        "title": "Animal",
        "rating": "A", "genre": "Action / Drama",
        "duration": "201 min", "cast": "Ranbir Kapoor, Anil Kapoor, Bobby Deol",
    },
    "jawan": {
        "title": "Jawan",
        "rating": "UA", "genre": "Action / Thriller",
        "duration": "169 min", "cast": "Shah Rukh Khan, Vijay Sethupathi, Nayanthara",
    },
    "dunki": {
        "title": "Dunki",
        "rating": "UA", "genre": "Drama / Comedy",
        "duration": "161 min", "cast": "Shah Rukh Khan, Taapsee Pannu",
    },
    "pathaan": {
        "title": "Pathaan",
        "rating": "UA", "genre": "Action / Spy",
        "duration": "146 min", "cast": "Shah Rukh Khan, Deepika Padukone, John Abraham",
    },
    "spider": {
        "title": "Spider-Man: No Way Home",
        "rating": "UA", "genre": "Action / Superhero",
        "duration": "148 min", "cast": "Tom Holland, Zendaya, Benedict Cumberbatch",
    },
    "batman": {
        "title": "The Batman",
        "rating": "UA", "genre": "Action / Crime",
        "duration": "176 min", "cast": "Robert Pattinson, Zoë Kravitz, Colin Farrell",
    },
    "doctor strange": {
        "title": "Doctor Strange in the Multiverse of Madness",
        "rating": "UA", "genre": "Action / Fantasy",
        "duration": "126 min", "cast": "Benedict Cumberbatch, Elizabeth Olsen",
    },
    "thor": {
        "title": "Thor: Love and Thunder",
        "rating": "UA", "genre": "Action / Comedy",
        "duration": "119 min", "cast": "Chris Hemsworth, Natalie Portman, Christian Bale",
    },
    "black panther": {
        "title": "Black Panther: Wakanda Forever",
        "rating": "UA", "genre": "Action / Drama",
        "duration": "161 min", "cast": "Letitia Wright, Angela Bassett",
    },
    "oppenheimer": {
        "title": "Oppenheimer",
        "rating": "UA", "genre": "Drama / History",
        "duration": "180 min", "cast": "Cillian Murphy, Emily Blunt, Matt Damon",
    },
    "barbie": {
        "title": "Barbie",
        "rating": "UA", "genre": "Comedy / Fantasy",
        "duration": "114 min", "cast": "Margot Robbie, Ryan Gosling, America Ferrera",
    },
    "inception": {
        "title": "Inception",
        "rating": "UA", "genre": "Sci-Fi / Thriller",
        "duration": "148 min", "cast": "Leonardo DiCaprio, Joseph Gordon-Levitt",
    },
    "interstellar": {
        "title": "Interstellar",
        "rating": "UA", "genre": "Sci-Fi / Drama",
        "duration": "169 min", "cast": "Matthew McConaughey, Anne Hathaway",
    },
}


def _lookup_movie(movie_name: str) -> dict:
    """Find movie details from DB or generate realistic metadata for unknown movies."""
    name_lower = movie_name.lower()
    # Try partial match
    for key, data in MOVIE_DATABASE.items():
        if key in name_lower or any(w in name_lower for w in key.split()):
            return data
    # Unknown movie — generate plausible metadata from the name
    genres = ["Action / Adventure", "Drama", "Thriller", "Comedy", "Sci-Fi / Action",
              "Romance / Drama", "Horror / Thriller", "Animation / Family"]
    rng = random.Random(int(hashlib.md5(name_lower.encode()).hexdigest()[:8], 16))
    return {
        "title": movie_name.title(),
        "rating": rng.choice(["U", "UA", "A"]),
        "genre": rng.choice(genres),
        "duration": f"{rng.randint(105, 185)} min",
        "cast": rng.choice([
            "Shah Rukh Khan, Deepika Padukone",
            "Ranveer Singh, Alia Bhatt",
            "Akshay Kumar, Katrina Kaif",
            "Ranbir Kapoor, Shraddha Kapoor",
            "Kartik Aaryan, Kiara Advani",
            "Tom Hanks, Meryl Streep",
            "Leonardo DiCaprio, Margot Robbie",
            "Dwayne Johnson, Ryan Reynolds",
        ]),
    }


# ─── Tool Functions ────────────────────────────────────────────────────────────

def search_booking_websites(query: str, task_category: str = "movies") -> dict[str, Any]:
    """Searches for relevant booking websites for a given task.

    Returns a list of trusted websites where the task can be completed.

    Args:
        query: The search query (e.g. 'Avengers tickets Mumbai').
        task_category: Category of task — 'movies', 'flights', 'hotels', 'bills', 'food'.
    """
    category_sites = {
        "movies": [
            {"name": "BookMyShow", "url": "https://bookmyshow.com",  "relevance": 98},
            {"name": "PVR Cinemas","url": "https://pvrinemas.com",   "relevance": 94},
            {"name": "INOX Movies","url": "https://inoxmovies.com",  "relevance": 91},
        ],
        "flights": [
            {"name": "MakeMyTrip","url": "https://makemytrip.com",  "relevance": 97},
            {"name": "Cleartrip", "url": "https://cleartrip.com",   "relevance": 93},
            {"name": "Goibibo",   "url": "https://goibibo.com",     "relevance": 90},
        ],
        "hotels": [
            {"name": "MakeMyTrip","url": "https://makemytrip.com",  "relevance": 95},
            {"name": "OYO Rooms", "url": "https://oyorooms.com",    "relevance": 92},
            {"name": "Treebo",    "url": "https://treebo.com",      "relevance": 88},
        ],
        "bills": [
            {"name": "Paytm",     "url": "https://paytm.com",      "relevance": 96},
            {"name": "PhonePe",   "url": "https://phonepe.com",     "relevance": 94},
            {"name": "Google Pay","url": "https://pay.google.com",  "relevance": 93},
        ],
        "food": [
            {"name": "Zomato",    "url": "https://zomato.com",     "relevance": 97},
            {"name": "Swiggy",    "url": "https://swiggy.com",     "relevance": 95},
        ],
    }
    sites = category_sites.get(task_category, category_sites["movies"])
    return {
        "query": query,
        "category": task_category,
        "sites_found": len(sites),
        "results": sites,
        "recommended": sites[0] if sites else None,
        "message": f"Found {len(sites)} relevant websites for '{query}'",
    }


def extract_movie_listings(
    website_url: str,
    movie_name: str,
    preferred_date: str = "Sunday",
    preferred_time: str = "evening",
    city: str = "Mumbai",
) -> dict[str, Any]:
    """Extracts available movie show listings from a booking website.

    Simulates navigating to the website and scraping showtime data.

    Args:
        website_url: The URL of the booking website to scrape.
        movie_name: Name of the movie to search for.
        preferred_date: Preferred date or day (e.g. 'Sunday', '2024-12-15').
        preferred_time: Preferred time of day — 'morning', 'afternoon', 'evening', 'night'.
        city: City to search in (e.g. 'Mumbai', 'Delhi', 'Bangalore').
    """
    movie = _lookup_movie(movie_name)

    # Truly random each call — no fixed seed
    rng = random.Random()   # seeded from os.urandom automatically

    time_key = preferred_time.lower()
    if time_key not in TIME_SLOTS:
        time_key = "evening"
    time_options = TIME_SLOTS[time_key]
    num_times = rng.randint(2, min(4, len(time_options)))
    selected_times = rng.sample(time_options, num_times)

    # Pick 3–4 random cinemas
    num_halls = rng.randint(3, 4)
    selected_halls = rng.sample(CINEMA_HALLS, num_halls)

    shows = []
    for hall in selected_halls:
        show_time = rng.choice(selected_times)
        chosen_format = rng.choice(hall["format"])
        # Base price always 200–400 INR
        base_price = rng.randint(200, 400)
        # IMAX / 4DX / Dolby add a small premium (max +80)
        premium = 0
        if "IMAX" in chosen_format:
            premium = rng.randint(40, 80)
        elif "4DX" in chosen_format or "Dolby" in chosen_format:
            premium = rng.randint(20, 60)
        price = base_price + premium
        available = rng.randint(8, 55)
        shows.append({
            "cinema":          hall["name"],
            "time":            show_time,
            "date":            preferred_date,
            "seat_category":   rng.choice(["Standard", "Premium", "Gold"]),
            "price_per_seat":  price,
            "available_seats": available,
            "format":          chosen_format,
            "language":        rng.choice(LANGUAGES[:3]),
        })

    # Sort cheapest first
    shows.sort(key=lambda s: s["price_per_seat"])

    return {
        "website":           website_url,
        "movie":             movie,
        "city":              city,
        "date":              preferred_date,
        "total_shows_found": len(shows),
        "shows":             shows,
        "message":           f"Found {len(shows)} shows for '{movie['title']}' on {preferred_date}",
    }


def navigate_to_seat_selection(
    website_url: str,
    show_time: str,
    cinema_name: str,
    num_tickets: int = 2,
) -> dict[str, Any]:
    """Navigates to the seat selection page for a chosen show.

    Simulates clicking through to the seat picker and selecting seats.

    Args:
        website_url: The booking website URL.
        show_time: The showtime string (e.g. '7:00 PM').
        cinema_name: Name of the cinema hall.
        num_tickets: Number of tickets to select.
    """
    # Truly random each call — fresh seat layout every time
    rng = random.Random()

    seat_rows = ["A", "B", "C", "D", "E", "F", "G", "H"]
    available_seats = []
    for row in seat_rows:
        for num in range(1, 14):
            if rng.random() > 0.3:   # 70% seats available
                available_seats.append(f"{row}{num}")

    selected_seats: list[str] = []
    if num_tickets == 1:
        selected_seats = [rng.choice(available_seats)] if available_seats else ["D5"]
    else:
        # Find a run of adjacent seats in the same row
        for i in range(len(available_seats) - num_tickets + 1):
            group = available_seats[i: i + num_tickets]
            if (
                len({s[0] for s in group}) == 1
                and all(
                    int(group[j + 1][1:]) - int(group[j][1:]) == 1
                    for j in range(len(group) - 1)
                )
            ):
                selected_seats = group
                break
        if not selected_seats:
            selected_seats = available_seats[:num_tickets] if available_seats else [f"D{i+1}" for i in range(num_tickets)]

    return {
        "website":          website_url,
        "cinema":           cinema_name,
        "show_time":        show_time,
        "num_tickets":      num_tickets,
        "selected_seats":   selected_seats,
        "seat_map_url":     f"{website_url}/seats/{cinema_name.replace(' ', '-').lower()}",
        "navigation_steps": [
            f"Opened {website_url}",
            f"Selected {show_time} show at {cinema_name}",
            "Opened seat selection map",
            f"Selected {num_tickets} seats: {', '.join(selected_seats)}",
        ],
        "ready_for_checkout": len(selected_seats) == num_tickets,
        "message":          f"Selected seats {', '.join(selected_seats)} at {cinema_name} — {show_time}",
    }


def fill_booking_form(
    user_name: str,
    user_email: str,
    user_phone: str,
    num_tickets: int,
    selected_seats: list[str],
) -> dict[str, Any]:
    """Fills in the booking details form with user information.

    Simulates form filling on the booking page.

    Args:
        user_name: Full name of the user.
        user_email: Email address of the user.
        user_phone: Phone number of the user.
        num_tickets: Number of tickets being booked.
        selected_seats: List of selected seat identifiers.
    """
    errors = []
    if not user_name or len(user_name) < 2:
        errors.append("Name too short")
    if "@" not in user_email:
        errors.append("Invalid email format")
    if not user_phone.isdigit() or len(user_phone) < 10:
        errors.append("Invalid phone number")

    if errors:
        return {
            "success": False,
            "errors":  errors,
            "message": f"Form validation failed: {', '.join(errors)}",
        }

    return {
        "success": True,
        "status":  "OK",
        "form_data": {
            "name":    user_name,
            "email":   user_email,
            "phone":   user_phone,
            "tickets": num_tickets,
            "seats":   selected_seats,
        },
        "steps_completed": [
            "Filled name field",
            "Filled email field",
            "Filled phone number",
            "Confirmed seat selection",
            "Accepted terms & conditions",
        ],
        "ready_for_payment": True,
        "message": f"Booking form filled successfully for {user_name}",
    }
