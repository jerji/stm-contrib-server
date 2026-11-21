#!/usr/bin/env python3
"""STM Contrib admin commands. Run via: docker compose exec stm-contrib-api python manage.py <command>"""

import sqlite3
import sys
import os

DB_PATH = "/app/data/stmcontrib.db"


def print_table(rows, headers):
    """Simple formatted table output."""
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


def cmd_list_products():
    db = sqlite3.connect(DB_PATH)
    rows = db.execute(
        "SELECT id, product_code, product_name, operator_id, confirmed, vote_score "
        "FROM product_submissions ORDER BY vote_score DESC"
    ).fetchall()
    print_table(rows, ["ID", "Code", "Name", "OpID", "Confirmed", "Score"])
    db.close()


def cmd_confirm(args):
    if not args:
        print("Usage: confirm <submission_id>")
        return
    sid = int(args[0])
    db = sqlite3.connect(DB_PATH)
    db.execute("UPDATE product_submissions SET confirmed=1 WHERE id=?", (sid,))
    db.commit()
    affected = db.total_changes
    db.close()
    if affected:
        print(f"Submission {sid} confirmed.")
    else:
        print(f"No submission found with id={sid}")


def cmd_unconfirm(args):
    if not args:
        print("Usage: unconfirm <submission_id>")
        return
    sid = int(args[0])
    db = sqlite3.connect(DB_PATH)
    db.execute("UPDATE product_submissions SET confirmed=0 WHERE id=?", (sid,))
    db.commit()
    db.close()
    print(f"Submission {sid} unconfirmed.")


def cmd_delete_submission(args):
    if not args:
        print("Usage: delete-submission <submission_id>")
        return
    sid = int(args[0])
    db = sqlite3.connect(DB_PATH)
    db.execute("DELETE FROM product_submissions WHERE id=?", (sid,))
    db.execute("DELETE FROM product_votes WHERE submission_id=?", (sid,))
    db.commit()
    db.close()
    print(f"Submission {sid} deleted.")


def cmd_list_bus_votes():
    db = sqlite3.connect(DB_PATH)
    rows = db.execute(
        "SELECT id, bus_name, operator_id, bus_id, vote, created_at "
        "FROM bus_votes ORDER BY id DESC LIMIT 50"
    ).fetchall()
    print_table(rows, ["ID", "Bus Name", "OpID", "BusID", "Vote", "Created"])
    db.close()


def cmd_list_bus_submissions():
    db = sqlite3.connect(DB_PATH)
    rows = db.execute(
        "SELECT id, bus_name, operator_name, created_at "
        "FROM bus_submissions ORDER BY id DESC LIMIT 50"
    ).fetchall()
    print_table(rows, ["ID", "Bus Name", "Operator", "Created"])
    db.close()


def cmd_stats():
    db = sqlite3.connect(DB_PATH)
    product_count = db.execute("SELECT COUNT(*) FROM product_submissions").fetchone()[0]
    confirmed = db.execute("SELECT COUNT(*) FROM product_submissions WHERE confirmed=1").fetchone()[0]
    bus_votes = db.execute("SELECT COUNT(*) FROM bus_votes").fetchone()[0]
    bus_subs = db.execute("SELECT COUNT(*) FROM bus_submissions").fetchone()[0]
    db.close()
    print(f"Product submissions: {product_count} ({confirmed} confirmed)")
    print(f"Bus votes:          {bus_votes}")
    print(f"Bus submissions:    {bus_subs}")


def cmd_help():
    print("STM Contrib Admin Commands")
    print("=" * 40)
    print("  list-products       Show all product code submissions")
    print("  confirm <id>        Mark a product submission as confirmed")
    print("  unconfirm <id>      Unmark a confirmed submission")
    print("  delete-sub <id>     Delete a spurious submission")
    print("  list-bus-votes      Show recent bus line votes")
    print("  list-bus-subs       Show recent bus name submissions")
    print("  stats               Database statistics")
    print()
    print("Usage: docker compose exec stm-contrib-api python manage.py <command> [args]")


COMMANDS = {
    "list-products": cmd_list_products,
    "confirm": cmd_confirm,
    "unconfirm": cmd_unconfirm,
    "delete-sub": cmd_delete_submission,
    "list-bus-votes": cmd_list_bus_votes,
    "list-bus-subs": cmd_list_bus_submissions,
    "stats": cmd_stats,
}


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        cmd_help()
        sys.exit(1 if len(sys.argv) > 1 else 0)
    COMMANDS[sys.argv[1]](sys.argv[2:])