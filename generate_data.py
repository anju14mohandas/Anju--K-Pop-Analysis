import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Defining specific track variables to match K-pop distribution models
songs_pool = [
    {"song": "Supernova", "artist": "aespa", "album_type": "single", "total_tracks": 1, "is_explicit": False, "pop_base": 90},
    {"song": "Armageddon", "artist": "aespa", "album_type": "album", "total_tracks": 10, "is_explicit": False, "pop_base": 82},
    {"song": "How Sweet", "artist": "NewJeans", "album_type": "single", "total_tracks": 2, "is_explicit": False, "pop_base": 88},
    {"song": "SPOT!", "artist": "ZICO (feat. JENNIE)", "album_type": "single", "total_tracks": 1, "is_explicit": True, "pop_base": 85},
    {"song": "Magnetic", "artist": "ILLIT", "album_type": "album", "total_tracks": 5, "is_explicit": False, "pop_base": 80}
]

start_date = datetime(2026, 5, 1)
data_rows = []

# Generate exactly 30 tracking days to build our chart history
for day in range(30):
    current_date = start_date + timedelta(days=day)
    active_songs = []
    
    for s in songs_pool:
        # Simulate Chart Dropouts (Exit Windows)
        if s["song"] == "Armageddon" and (5 <= day <= 11):
            continue # Drops entirely out of the tracking panel
        if s["song"] == "SPOT!" and (15 <= day <= 22):
            continue # Drops out during a dead promotion cycle
            
        # Add random baseline noise to popularity scores
        daily_pop = s["pop_base"] + np.random.randint(-3, 4)
        
        # Simulate Coordinated Comeback Surges (Re-entry spikes)
        if s["song"] == "Armageddon" and day == 12:
            daily_pop += 15 # Coordinated fandom stream surge
        if s["song"] == "SPOT!" and day == 23:
            daily_pop += 12 # Post-award show performance bounce
            
        active_songs.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "song": s["song"],
            "artist": s["artist"],
            "popularity": max(1, min(100, daily_pop)),
            "duration_ms": 178000 if s["album_type"] == "single" else 212000,
            "album_type": s["album_type"],
            "total_tracks": s["total_tracks"],
            "is_explicit": s["is_explicit"],
            "album_cover_url": f"https://images.example.com/{s['song'].lower().replace('!', '')}.jpg"
        })
        
    # Strictly enforce 50 row validation (pad out with generic tracks if needed)
    rank = 1
    for item in sorted(active_songs, key=lambda x: x["popularity"], reverse=True):
        item["position"] = rank
        data_rows.append(item)
        rank += 1
        
    # Ensure our simulation maintains a true Top-50 distribution daily
    while rank <= 50:
        data_rows.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "position": rank,
            "song": f"Catalog Track {rank}",
            "artist": "Indie/OST Artist",
            "popularity": max(1, 60 - rank),
            "duration_ms": 200000,
            "album_type": "single",
            "total_tracks": 1,
            "is_explicit": False,
            "album_cover_url": "https://images.example.com/catalog.jpg"
        })
        rank += 1

df = pd.DataFrame(data_rows)
df.to_csv("mock_data.csv", index=False)
print("SUCCESS: mock_data.csv built flawlessly with 50 rows per day.")