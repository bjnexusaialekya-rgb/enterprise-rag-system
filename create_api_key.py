import argparse
from app.auth.api_key_auth import generate_api_key, revoke_api_key
from app.database.connection import SessionLocal
from sqlalchemy import text

VALID_ROLES = ["admin", "hr_staff", "finance_staff", "legal_staff", "employee"]

def list_keys():
    db = SessionLocal()
    try:
        rows = db.execute(text("""
            SELECT owner, role, is_active, created_at, last_used_at
            FROM api_keys
            ORDER BY created_at DESC
        """)).fetchall()
        if not rows:
            print("\n No API keys found.\n")
            return
        print("\n" + "="*65)
        print(f"  {'OWNER':<20} {'ROLE':<15} {'ACTIVE':<8} {'LAST USED'}")
        print("="*65)
        for row in rows:
            owner, role, is_active, created_at, last_used = row
            status = "YES" if is_active else "NO"
            last = str(last_used)[:16] if last_used else "never"
            print(f"  {owner:<20} {role:<15} {status:<8} {last}")
        print("="*65 + "\n")
    finally:
        db.close()

parser = argparse.ArgumentParser(description="Manage API keys for Enterprise RAG")
parser.add_argument("--owner", help="Owner identifier")
parser.add_argument("--role", default="employee", choices=VALID_ROLES)
parser.add_argument("--revoke", metavar="OWNER")
parser.add_argument("--list", action="store_true")
args = parser.parse_args()

if args.list:
    list_keys()
elif args.revoke:
    revoke_api_key(args.revoke)
    print(f"\n✅ All keys revoked for owner: {args.revoke}\n")
elif args.owner:
    raw_key = generate_api_key(owner=args.owner, role=args.role)
    print("\n" + "="*55)
    print(f"  ✅ API Key Generated")
    print("="*55)
    print(f"  Owner : {args.owner}")
    print(f"  Role  : {args.role}")
    print(f"  Key   : {raw_key}")
    print("="*55)
    print("  Copy this key now - it will NOT be shown again.")
    print("="*55 + "\n")
else:
    parser.print_help()
