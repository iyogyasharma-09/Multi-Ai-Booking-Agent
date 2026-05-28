"""
TaskHive — Web Navigation Tools
Simulates browser navigation, search, and data extraction for the Web Nav Agent.
"""

import random
import hashlib
from datetime import datetime, timedelta
from typing import Any


# ─── Realistic Mock Data ──────────────────────────────────────────────────────

MOVIE_DATABASE = {
    "mission impossible": {
        "title": "Mission: Impossible — The Final Reckoning",
        "rating": "UA",
        "genre": "Action / Thriller",
        "duration": "169 min",
        "language": "Hindi, English",
        "cast": "Tom Cruise, Hayley Atwell, Simon Pegg",
    },
    "kalki": {
        "title": "Kalki 2898-AD",
        "rating": "UA",
        "genre": "Sci-Fi / Action",
        "duration": "181 min",
        "language": "Hindi, Telugu, Tamil",
        "cast": "Prabhas, Deepika Padukone, Amitabh Bachchan",
    },
    "stree": {
        "title": "Stree 3",
        "rating": "UA",
        "genre": "Horror / Comedy",
        "duration": "142 min",
        "language": "Hindi",
        "cast": "Rajkummar Rao, Shraddha Kapoor, Pankaj Tripathi",
    },
    "default": {
        "title": "The Last Stand",
        "rating": "UA",
        "genre": "Action",
        "duration": "135 min",
        "language": "Hindi, English",
        "cast": "Various Artists",
    }
}

CINEMA_HALLS = [
    {"name": "PVR Phoenix Mall", "city": "Mumbai", "url": "https://pvrinemas.com"},
    {"name": "INOX R-City", "city": "Mumbai", "url": "https://inoxmovies.com"},
    {"name": "Cinepolis VR Mall", "city": "Delhi", "url": "https://cinepolis.com"},
    {"name": "PVR Orion Mall", "city": "Bangalore", "url": "https://pvrinemas.com"},
    {"name": "INOX Garuda Mall", "city": "Bangalore", "url": "https://inoxmovies.com"},
    {"name": "BookMyShow Mega Cinemas", "city": "Hyderabad", "url": "https://bookmyshow.com"},
]

BOOKING_SITES = [
    {"name": "BookMyShow", "url": "https://bookmyshow.com", "logo": "🎬"},
    {"name": "PVR Cinemas", "url": "https://pvrinemas.com", "logo": "🎥"},
    {"name": "INOX Movies", "url": "https://inoxmovies.com", "logo": "🍿"},
]

SEAT_CATEGORIES = [
    {"type": "Recliner", "price_multiplier": 2.2},
    {"type": "Gold", "price_multiplier": 1.6},
    {"type": "Premium", "price_multiplier": 1.3},
    {"type": "Standard", "price_multiplier": 1.0},
]

TIME_SLOTS = {
    "morning": ["10:00 AM", "10:30 AM", "11:15 AM"],
    "afternoon": ["1:30 PM", "2:00 PM", "2:45 PM", "3:30 PM"],
    "evening": ["6:00 PM", "6:30 PM", "7:00 PM", "7:30 PM"],
    "night": ["9:30 PM", "10:00 PM", "10:30 PM"],
}


# ─── Tool Functions ────────────────────────────────────────────────────────────

def search_booking_websites(query: str, task_category: str = "movies") -> dict[str, Any]:
    """Searches for relevant booking websites for a given task.

    Returns a list of trusted websites where the task can be completed.

    Args:
        query: The search query (e.g. 'Mission Impossible tickets Mumbai').
        task_category: Category of task — 'movies', 'flights', 'hotels', 'bills', 'food'.
    """
    category_sites = {
        "movies": [
            {"name": "BookMyShow", "url": "https://bookmyshow.com", "relevance": 98},
            {"name": "PVR Cinemas", "url": "https://pvrinemas.com", "relevance": 94},
            {"name": "INOX Movies", "url": "https://inoxmovies.com", "relevance": 91},
        ],
        "flights": [
            {"name": "MakeMyTrip", "url": "https://makemytrip.com", "relevance": 97},
            {"name": "Cleartrip", "url": "https://cleartrip.com", "relevance": 93},
            {"name": "Goibibo", "url": "https://goibibo.com", "relevance": 90},
        ],
        "hotels": [
            {"name": "MakeMyTrip", "url": "https://makemytrip.com", "relevance": 95},
            {"name": "OYO Rooms", "url": "https://oyorooms.com", "relevance": 92},
            {"name": "Treebo Hotels", "url": "https://treebo.com", "relevance": 88},
        ],
        "bills": [
            {"name": "Paytm", "url": "https://paytm.com", "relevance": 96},
            {"name": "PhonePe", "url": "https://phonepe.com", "relevance": 94},
            {"name": "Google Pay", "url": "https://pay.google.com", "relevance": 93},
        ],
        "food": [
            {"name": "Zomato", "url": "https://zomato.com", "relevance": 97},
            {"name": "Swiggy", "url": "https://swiggy.com", "relevance": 95},
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
    # Find movie details
    movie_key = next(
        (k for k in MOVIE_DATABASE if k in movie_name.lower()), "default"
    )
    movie = MOVIE_DATABASE[movie_key]
    if movie_key == "default":
        movie = {**movie, "title": movie_name.title()}

    # Generate deterministic but realistic shows
    seed = int(hashlib.md5(f"{movie_name}{website_url}{city}".encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)

    time_options = TIME_SLOTS.get(preferred_time, TIME_SLOTS["evening"])
    selected_times = rng.sample(time_options, min(3, len(time_options)))

    city_halls = [h for h in CINEMA_HALLS if city.lower() in h["city"].lower()]
    if not city_halls:
        city_halls = CINEMA_HALLS[:2]

    shows = []
    for hall in city_halls[:2]:
        for show_time in selected_times[:2]:
            base_price = rng.randint(200, 350)
            seat_cat = rng.choice(SEAT_CATEGORIES[:3])
            price = int(base_price * seat_cat["price_multiplier"])
            available_seats = rng.randint(12, 60)

            shows.append({
                "cinema": hall["name"],
                "time": show_time,
                "date": preferred_date,
                "seat_category": seat_cat["type"],
                "price_per_seat": price,
                "available_seats": available_seats,
                "format": rng.choice(["2D", "3D", "IMAX 3D"]),
                "language": rng.choice(["Hindi", "English"]),
            })

    shows.sort(key=lambda x: x["price_per_seat"])

    return {
        "website": website_url,
        "movie": movie,
        "city": city,
        "date": preferred_date,
        "total_shows_found": len(shows),
        "shows": shows,
        "message": f"Found {len(shows)} shows for '{movie['title']}' on {preferred_date} in {city}",
    }


def navigate_to_seat_selection(
    website_url: str,
    show_id: str,
    cinema_name: str,
    num_tickets: int = 2,
) -> dict[str, Any]:
    """Navigates to the seat selection page for a chosen show.

    Simulates clicking through to the seat picker and selecting seats.

    Args:
        website_url: The booking website URL.
        show_id: The show identifier string (cinema + time).
        cinema_name: Name of the cinema hall.
        num_tickets: Number of tickets to select.
    """
    seed = int(hashlib.md5(show_id.encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)

    # Simulate seat map
    seat_rows = ["A", "B", "C", "D", "E", "F", "G"]
    available_seats = []
    for row in seat_rows:
        for num in range(1, 13):
            if rng.random() > 0.35:  # 65% seats available
                available_seats.append(f"{row}{num}")

    # Pick adjacent seats — exactly num_tickets of them
    selected_seats: list[str] = []
    if num_tickets == 1:
        # Single ticket: just pick the first available seat
        selected_seats = available_seats[:1]
    else:
        # Multiple tickets: find a run of adjacent seats in the same row
        for i in range(len(available_seats) - num_tickets + 1):
            group = available_seats[i: i + num_tickets]
            # All same row and consecutive seat numbers
            if (
                len({s[0] for s in group}) == 1  # same row letter
                and all(
                    int(group[j + 1][1:]) - int(group[j][1:]) == 1
                    for j in range(len(group) - 1)
                )
            ):
                selected_seats = group
                break
        if not selected_seats and available_seats:
            selected_seats = available_seats[:num_tickets]

    return {
        "website": website_url,
        "cinema": cinema_name,
        "num_tickets": num_tickets,
        "selected_seats": selected_seats,
        "seat_map_url": f"{website_url}/seats/{show_id}",
        "navigation_steps": [
            f"Opened {website_url}",
            f"Searched for show at {cinema_name}",
            "Navigated to seat selection",
            f"Selected {num_tickets} adjacent seats: {', '.join(selected_seats)}",
        ],
        "ready_for_checkout": len(selected_seats) == num_tickets,
        "message": f"Selected seats {', '.join(selected_seats)} at {cinema_name}",
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
    # Validate basic fields
    validation_errors = []
    if not user_name or len(user_name) < 2:
        validation_errors.append("Name too short")
    if "@" not in user_email:
        validation_errors.append("Invalid email format")
    if not user_phone.isdigit() or len(user_phone) < 10:
        validation_errors.append("Invalid phone number")

    if validation_errors:
        return {
            "success": False,
            "errors": validation_errors,
            "message": f"Form validation failed: {', '.join(validation_errors)}",
        }

    return {
        "success": True,
        "form_data": {
            "name": user_name,
            "email": user_email,
            "phone": user_phone,
            "tickets": num_tickets,
            "seats": selected_seats,
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
