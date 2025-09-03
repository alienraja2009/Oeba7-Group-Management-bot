#!/usr/bin/env python3
"""
Debug script to test the redeem function directly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import datetime
import database

def debug_redeem_code(code):
    """Debug a specific redeem code"""
    print(f"🔍 Debugging code: {code}")
    print("=" * 50)

    try:
        code_data = database.get_redeem_code(code)
        if not code_data:
            print("❌ Code not found in database")
            return

        print("📊 Code data from database:")
        print(f"  ID: {code_data[0]}")
        print(f"  Code: {code_data[1]}")
        print(f"  Rank: {code_data[2]}")
        print(f"  Duration: {code_data[3]}")
        print(f"  Created At: {code_data[4]}")
        print(f"  Expires At: {code_data[5]}")
        print(f"  Used: {code_data[6]}")
        print(f"  Banned: {code_data[7]}")

        # Test the expiration logic
        print("\n🕐 Testing expiration logic:")

        expires_at_value = code_data[5]  # expires_at is at index 5
        print(f"  Raw expires_at value: {repr(expires_at_value)}")
        print(f"  Type: {type(expires_at_value)}")

        if expires_at_value:
            try:
                expires_at_str = str(expires_at_value).strip()
                print(f"  String version: '{expires_at_str}'")

                if expires_at_str.lower() in ['none', 'null', '']:
                    print("  ✅ No expiration date set (permanent code)")
                else:
                    print("  🔄 Attempting to parse date...")
                    expires_at = None

                    # Try ISO format first
                    try:
                        expires_at = datetime.datetime.fromisoformat(expires_at_str)
                        print(f"  ✅ Parsed as ISO format: {expires_at}")
                    except ValueError as e1:
                        print(f"  ❌ ISO format failed: {e1}")

                        # Try with microseconds
                        try:
                            expires_at = datetime.datetime.strptime(expires_at_str, "%Y-%m-%d %H:%M:%S.%f")
                            print(f"  ✅ Parsed with microseconds: {expires_at}")
                        except ValueError as e2:
                            print(f"  ❌ Microseconds format failed: {e2}")

                            # Try without microseconds
                            try:
                                expires_at = datetime.datetime.strptime(expires_at_str, "%Y-%m-%d %H:%M:%S")
                                print(f"  ✅ Parsed without microseconds: {expires_at}")
                            except ValueError as e3:
                                print(f"  ❌ Standard format failed: {e3}")
                                print("  ⚠️ All parsing attempts failed - would treat as not expired")

                    # Check if expired
                    now = datetime.datetime.now()
                    print(f"  Current time: {now}")
                    if expires_at is not None:
                        if expires_at < now:
                            print("  ❌ Code would be considered EXPIRED")
                        else:
                            print("  ✅ Code would be considered VALID")
                    else:
                        print("  ⚠️ Could not parse date - would treat as not expired")

            except Exception as e:
                print(f"  ❌ Unexpected error: {e}")
                print("  ⚠️ Would treat as not expired due to error")
        else:
            print("  ✅ No expiration date (None/null)")

    except Exception as e:
        print(f"❌ Database error: {e}")

    print("=" * 50)

def list_recent_codes():
    """List recent codes for debugging"""
    print("📋 Recent codes in database:")
    print("=" * 50)

    try:
        import sqlite3
        conn = sqlite3.connect(database.DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT code, rank, duration, created_at, expires_at, used, banned FROM redeem_codes ORDER BY created_at DESC LIMIT 10')
        codes = cursor.fetchall()
        conn.close()

        if not codes:
            print("No codes found in database")
            return

        for i, code_data in enumerate(codes, 1):
            code, rank, duration, created_at, expires_at, used, banned = code_data
            status = "✅ Active" if not used and not banned else "❌ Used" if used else "🚫 Banned"
            print(f"{i}. {code} | {rank} | {duration}s | {status}")
            print(f"   Created: {created_at}")
            print(f"   Expires: {expires_at}")
            print()

    except Exception as e:
        print(f"❌ Error listing codes: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        code = sys.argv[1].upper()
        debug_redeem_code(code)
    else:
        list_recent_codes()
        print("\n💡 Usage: python debug_redeem.py <CODE>")
        print("   Example: python debug_redeem.py ABC123")
