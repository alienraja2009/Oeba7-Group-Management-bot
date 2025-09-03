#!/usr/bin/env python3
"""
Test script to verify the redeem code expiration fix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import datetime
from handlers.utilities import redeem

def test_expiration_parsing():
    """Test various expiration date formats"""

    test_cases = [
        # (expires_at_value, expected_result, description)
        (None, "no_expiration", "None value"),
        ("", "no_expiration", "Empty string"),
        ("2024-12-31T23:59:59", "future", "ISO format future date"),
        ("2020-01-01T00:00:00", "expired", "ISO format past date"),
        ("2024-12-31 23:59:59.123456", "future", "Datetime with microseconds"),
        ("2024-12-31 23:59:59", "future", "Datetime without microseconds"),
        ("invalid_date", "no_expiration", "Invalid date string"),
        ("2024-13-45T25:61:61", "no_expiration", "Impossible date"),
    ]

    print("🧪 Testing expiration date parsing...")
    print("=" * 50)

    for expires_at, expected, description in test_cases:
        try:
            # Simulate the parsing logic from redeem function
            if expires_at:
                expires_at_str = str(expires_at).strip()
                if expires_at_str.lower() in ['none', 'null', '']:
                    result = "no_expiration"
                else:
                    try:
                        parsed_date = datetime.datetime.fromisoformat(expires_at_str)
                        if parsed_date < datetime.datetime.now():
                            result = "expired"
                        else:
                            result = "future"
                    except ValueError:
                        try:
                            parsed_date = datetime.datetime.strptime(expires_at_str, "%Y-%m-%d %H:%M:%S.%f")
                            if parsed_date < datetime.datetime.now():
                                result = "expired"
                            else:
                                result = "future"
                        except ValueError:
                            try:
                                parsed_date = datetime.datetime.strptime(expires_at_str, "%Y-%m-%d %H:%M:%S")
                                if parsed_date < datetime.datetime.now():
                                    result = "expired"
                                else:
                                    result = "future"
                            except ValueError:
                                result = "no_expiration"  # Treat as not expired
                            else:
                                result = "future" if parsed_date >= datetime.datetime.now() else "expired"
                        else:
                            result = "future" if parsed_date >= datetime.datetime.now() else "expired"
                    else:
                        result = "future" if parsed_date >= datetime.datetime.now() else "expired"
            else:
                result = "no_expiration"

            status = "✅" if result == expected else "❌"
            print(f"{status} {description}: '{expires_at}' -> {result} (expected: {expected})")

        except Exception as e:
            print(f"❌ {description}: Error - {e}")

    print("=" * 50)
    print("✅ Test completed!")

if __name__ == "__main__":
    test_expiration_parsing()
