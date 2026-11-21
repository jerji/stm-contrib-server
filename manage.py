#!/usr/bin/env python3
"""STM Contrib admin commands. Run via: docker compose exec stm-contrib-api python manage.py <command>"""

import sqlite3
import sys
import os
import secrets

DB_PATH = "/app/data/stmcontrib.db"
API_KEY_PATH = "/app/data/api_key.txt"


def print_table(rows, headers):
    if not rows:
        print("No results.")
        return
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            w = len(str(val))
            if w > col_widths[i]:
                col_widths[i] = w
    sep = "+".join("-" * (w + 2) for w in col_widths)
    print(sep)
    print("| " + " | ".join(h.ljust(w) for h, w in zip(headers, col_widths)) + " |")
    print(sep)
    for row in rows:
        print("| " + " | ".join(str(v).ljust(w) for v, w in zip(row, col_widths)) + " |")
    print(sep)


def cmd_list_products(*args):
    db = sqlite3.connect(DB_PATH)
    rows = db.execute(
        "SELECT id, product_code, product_name, operator_id, vote_score "
        "FROM product_submissions ORDER BY vote_score DESC"
    ).fetchall()
    print_table(rows, ["ID", "Code", "Name", "OpID", "Score"])
    db.close()


def cmd_delete_submission(args):
    if not args:
        print("Usage: delete-sub <submission_id>")
        return
    sid = int(args[0])
    db = sqlite3.connect(DB_PATH)
    db.execute("DELETE FROM product_submissions WHERE id=?", (sid,))
    db.execute("DELETE FROM product_votes WHERE submission_id=?", (sid,))
    db.commit()
    db.close()
    print(f"Submission {sid} deleted.")


def cmd_delete_bus_sub(args):
    if not args:
        print("Usage: delete-bus-sub <submission_id>")
        return
    sid = int(args[0])
    db = sqlite3.connect(DB_PATH)
    db.execute("DELETE FROM bus_submissions WHERE id=?", (sid,))
    db.commit()
    db.close()
    print(f"Bus submission {sid} deleted.")


def cmd_delete_bus_vote(args):
    if not args:
        print("Usage: delete-bus-vote <vote_id>")
        return
    vid = int(args[0])
    db = sqlite3.connect(DB_PATH)
    db.execute("DELETE FROM bus_votes WHERE id=?", (vid,))
    db.commit()
    db.close()
    print(f"Bus vote {vid} deleted.")


def cmd_reset_all(*args):
    db = sqlite3.connect(DB_PATH)
    db.execute("DELETE FROM product_submissions")
    db.execute("DELETE FROM product_votes")
    db.execute("DELETE FROM bus_submissions")
    db.execute("DELETE FROM bus_votes")
    db.commit()
    db.close()
    print("All submissions and votes deleted.")


def cmd_list_bus_votes(*args):
    db = sqlite3.connect(DB_PATH)
    rows = db.execute(
        "SELECT id, bus_name, operator_id, bus_id, vote, created_at "
        "FROM bus_votes ORDER BY id DESC LIMIT 50"
    ).fetchall()
    print_table(rows, ["ID", "Bus Name", "OpID", "BusID", "Vote", "Created"])
    db.close()


def cmd_list_bus_subs(*args):
    db = sqlite3.connect(DB_PATH)
    rows = db.execute(
        "SELECT id, bus_name, operator_name, created_at "
        "FROM bus_submissions ORDER BY id DESC LIMIT 50"
    ).fetchall()
    print_table(rows, ["ID", "Bus Name", "Operator", "Created"])
    db.close()


def cmd_stats(*args):
    db = sqlite3.connect(DB_PATH)
    product_count = db.execute("SELECT COUNT(*) FROM product_submissions").fetchone()[0]
    bus_votes = db.execute("SELECT COUNT(*) FROM bus_votes").fetchone()[0]
    bus_subs = db.execute("SELECT COUNT(*) FROM bus_submissions").fetchone()[0]
    db.close()
    print(f"Product submissions: {product_count}")
    print(f"Bus votes:           {bus_votes}")
    print(f"Bus submissions:     {bus_subs}")


def cmd_rotate_key(args):
    """Generate a new API key and save to config file."""
    key = secrets.token_hex(32)
    with open(API_KEY_PATH, "w") as f:
        f.write(key)
    print(f"New API key generated: {key}")
    print(f"Saved to {API_KEY_PATH}")
    print("Update the app's built-in key and rebuild.")


def cmd_show_key(args):
    """Display the current API key."""
    if os.path.exists(API_KEY_PATH):
        with open(API_KEY_PATH) as f:
            print(f"Current API key: {f.read().strip()}")
    else:
        print("No API key file found. Restart the container to generate one.")


def cmd_help():
    print("STM Contrib Admin Commands")
    print("=" * 40)
    print("  list-products       Show all product code submissions")
    print("  delete-sub <id>     Delete a submission (spam/wrong)")
    print("  list-bus-votes      Show recent bus line votes")
    print("  list-bus-subs       Show recent bus name submissions")
    print("  stats               Database statistics")
    print("  rotate-key          Generate a new API key")
    print("  show-key            Display the current API key")
    print()
    print("Usage: docker compose exec stm-contrib-api python manage.py <command> [args]")


COMMANDS = {
    "list-products": cmd_list_products,
    "delete-sub": cmd_delete_submission,
    "delete-bus-sub": cmd_delete_bus_sub,
    "delete-bus-vote": cmd_delete_bus_vote,
    "reset-all": cmd_reset_all,
    "list-bus-votes": cmd_list_bus_votes,
    "list-bus-subs": cmd_list_bus_subs,
    "stats": cmd_stats,
    "rotate-key": cmd_rotate_key,
    "show-key": cmd_show_key,
}


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        cmd_help()
        sys.exit(1 if len(sys.argv) > 1 else 0)
    COMMANDS[sys.argv[1]](sys.argv[2:])