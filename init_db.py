"""
VERA-SD Database Initialization
Creates the SQLite database with 10 South Dakota demo districts and WIDA ACCESS data.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "vera_demo.db"

def init_database():
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Create districts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS districts (
            district_id TEXT PRIMARY KEY,
            district_name TEXT NOT NULL,
            county TEXT NOT NULL,
            ell_count INTEGER,
            native_pct REAL,
            csi_tsi TEXT
        )
    """)

    # Create WIDA results table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wida_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            district_id TEXT NOT NULL,
            district_name TEXT NOT NULL,
            grade INTEGER NOT NULL,
            subgroup TEXT NOT NULL,
            speaking_score REAL,
            writing_score REAL,
            listening_score REAL,
            reading_score REAL,
            composite_score REAL,
            year INTEGER DEFAULT 2025,
            FOREIGN KEY (district_id) REFERENCES districts(district_id)
        )
    """)

    # 10 Demo Districts from SD Research Brief
    districts = [
        ("49-5", "Sioux Falls School District", "Minnehaha", 3800, 8.0, "TSI"),
        ("51-4", "Rapid City Area Schools", "Pennington", 900, 25.0, "CSI"),
        ("66-1", "Oglala Lakota County Schools", "Oglala Lakota", 10, 95.0, "CSI"),
        ("6-1", "Aberdeen School District", "Brown", 400, 5.0, "TSI"),
        ("14-4", "Watertown School District", "Codington", 300, 4.0, "CSI"),
        ("17-2", "Mitchell School District", "Davison", 200, 5.0, "CSI"),
        ("2-2", "Huron School District", "Beadle", 600, 4.0, "TSI"),
        ("63-3", "Yankton School District", "Yankton", 150, 6.0, "TSI"),
        ("59-2", "Winner School District", "Tripp", 50, 35.0, "TSI"),
        ("66-2", "Todd County School District", "Todd", 10, 95.0, "CSI"),
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO districts (district_id, district_name, county, ell_count, native_pct, csi_tsi)
        VALUES (?, ?, ?, ?, ?, ?)
    """, districts)

    # WIDA ACCESS synthetic data
    # Based on SD ELP Progress Indicator data
    # Districts with lowest ELP progress rates get largest oral-written deltas
    # WIDA scale: 1.0-6.0, Type 4 threshold: delta >= 0.5

    wida_data = [
        # Sioux Falls - Karen/Nepali cluster - large Type 4 deltas
        ("49-5", "Sioux Falls School District", 3, "Karen", 3.8, 2.9, 3.2, 2.7, 3.2),
        ("49-5", "Sioux Falls School District", 4, "Karen", 3.9, 3.0, 3.3, 2.8, 3.3),
        ("49-5", "Sioux Falls School District", 5, "Karen", 4.0, 3.1, 3.4, 2.9, 3.4),
        ("49-5", "Sioux Falls School District", 3, "Nepali", 3.6, 2.8, 3.1, 2.6, 3.0),
        ("49-5", "Sioux Falls School District", 4, "Nepali", 3.7, 2.9, 3.2, 2.7, 3.1),
        ("49-5", "Sioux Falls School District", 5, "Nepali", 3.8, 3.0, 3.3, 2.8, 3.2),
        ("49-5", "Sioux Falls School District", 3, "Spanish", 3.4, 3.0, 3.2, 2.9, 3.1),
        ("49-5", "Sioux Falls School District", 4, "Spanish", 3.5, 3.1, 3.3, 3.0, 3.2),
        ("49-5", "Sioux Falls School District", 5, "Spanish", 3.6, 3.2, 3.4, 3.1, 3.3),
        ("49-5", "Sioux Falls School District", 6, "All EL", 3.7, 3.1, 3.3, 2.9, 3.2),
        ("49-5", "Sioux Falls School District", 7, "All EL", 3.8, 3.2, 3.4, 3.0, 3.4),
        ("49-5", "Sioux Falls School District", 8, "All EL", 3.9, 3.3, 3.5, 3.1, 3.5),

        # Rapid City - Native American focus
        ("51-4", "Rapid City Area Schools", 3, "Lakota", 3.2, 2.6, 2.9, 2.4, 2.8),
        ("51-4", "Rapid City Area Schools", 4, "Lakota", 3.3, 2.7, 3.0, 2.5, 2.9),
        ("51-4", "Rapid City Area Schools", 5, "Lakota", 3.4, 2.8, 3.1, 2.6, 3.0),
        ("51-4", "Rapid City Area Schools", 6, "Lakota", 3.5, 2.9, 3.2, 2.7, 3.1),
        ("51-4", "Rapid City Area Schools", 7, "All EL", 3.6, 3.0, 3.2, 2.8, 3.2),
        ("51-4", "Rapid City Area Schools", 8, "All EL", 3.7, 3.1, 3.3, 2.9, 3.3),

        # Oglala Lakota County - Nearly all Native
        ("66-1", "Oglala Lakota County Schools", 3, "Lakota", 2.8, 2.2, 2.5, 2.0, 2.4),
        ("66-1", "Oglala Lakota County Schools", 4, "Lakota", 2.9, 2.3, 2.6, 2.1, 2.5),
        ("66-1", "Oglala Lakota County Schools", 5, "Lakota", 3.0, 2.4, 2.7, 2.2, 2.6),
        ("66-1", "Oglala Lakota County Schools", 6, "Lakota", 3.1, 2.5, 2.8, 2.3, 2.7),

        # Aberdeen - Refugee resettlement
        ("6-1", "Aberdeen School District", 3, "Karen", 3.5, 2.8, 3.1, 2.6, 3.0),
        ("6-1", "Aberdeen School District", 4, "Karen", 3.6, 2.9, 3.2, 2.7, 3.1),
        ("6-1", "Aberdeen School District", 5, "Nepali", 3.4, 2.7, 3.0, 2.5, 2.9),
        ("6-1", "Aberdeen School District", 6, "All EL", 3.5, 3.0, 3.2, 2.8, 3.1),

        # Watertown - Growing refugee population
        ("14-4", "Watertown School District", 3, "Spanish", 3.3, 2.9, 3.1, 2.8, 3.0),
        ("14-4", "Watertown School District", 4, "Spanish", 3.4, 3.0, 3.2, 2.9, 3.1),
        ("14-4", "Watertown School District", 5, "Karen", 3.6, 2.9, 3.2, 2.7, 3.1),
        ("14-4", "Watertown School District", 6, "All EL", 3.5, 3.0, 3.2, 2.8, 3.1),

        # Mitchell - Mixed ELL
        ("17-2", "Mitchell School District", 3, "Spanish", 3.2, 2.8, 3.0, 2.7, 2.9),
        ("17-2", "Mitchell School District", 4, "Spanish", 3.3, 2.9, 3.1, 2.8, 3.0),
        ("17-2", "Mitchell School District", 5, "All EL", 3.4, 3.0, 3.2, 2.9, 3.1),
        ("17-2", "Mitchell School District", 6, "All EL", 3.5, 3.1, 3.3, 3.0, 3.2),

        # Huron - Large Spanish/Karen ELL
        ("2-2", "Huron School District", 3, "Spanish", 3.4, 2.9, 3.1, 2.7, 3.0),
        ("2-2", "Huron School District", 4, "Spanish", 3.5, 3.0, 3.2, 2.8, 3.1),
        ("2-2", "Huron School District", 5, "Karen", 3.7, 2.9, 3.2, 2.7, 3.1),
        ("2-2", "Huron School District", 6, "Karen", 3.8, 3.0, 3.3, 2.8, 3.2),
        ("2-2", "Huron School District", 7, "All EL", 3.6, 3.1, 3.3, 2.9, 3.2),

        # Yankton
        ("63-3", "Yankton School District", 3, "Spanish", 3.3, 2.9, 3.1, 2.8, 3.0),
        ("63-3", "Yankton School District", 4, "Spanish", 3.4, 3.0, 3.2, 2.9, 3.1),
        ("63-3", "Yankton School District", 5, "All EL", 3.5, 3.1, 3.3, 3.0, 3.2),

        # Winner - Native American
        ("59-2", "Winner School District", 3, "Lakota", 3.0, 2.5, 2.8, 2.3, 2.6),
        ("59-2", "Winner School District", 4, "Lakota", 3.1, 2.6, 2.9, 2.4, 2.7),
        ("59-2", "Winner School District", 5, "Lakota", 3.2, 2.7, 3.0, 2.5, 2.8),

        # Todd County - Native American dominant
        ("66-2", "Todd County School District", 3, "Lakota", 2.9, 2.3, 2.6, 2.1, 2.5),
        ("66-2", "Todd County School District", 4, "Lakota", 3.0, 2.4, 2.7, 2.2, 2.6),
        ("66-2", "Todd County School District", 5, "Lakota", 3.1, 2.5, 2.8, 2.3, 2.7),
        ("66-2", "Todd County School District", 6, "Lakota", 3.2, 2.6, 2.9, 2.4, 2.8),
    ]

    cursor.executemany("""
        INSERT INTO wida_results (district_id, district_name, grade, subgroup, speaking_score, writing_score, listening_score, reading_score, composite_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, wida_data)

    # Create access_requests table for authentication system
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS access_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            organization TEXT,
            requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending'
        )
    """)

    conn.commit()
    conn.close()

    print(f"Database created at {DB_PATH}")
    print(f"- 10 districts loaded")
    print(f"- {len(wida_data)} WIDA result records loaded")

if __name__ == "__main__":
    init_database()
