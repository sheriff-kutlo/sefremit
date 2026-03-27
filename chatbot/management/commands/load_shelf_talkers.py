from django.core.management.base import BaseCommand
from django.db import connection
from django.core.cache import cache
from datetime import datetime, timedelta, date
from django_redis import get_redis_connection

class Command(BaseCommand):
    help = "Load shelf talker data into Redis cache"

    def handle(self, *args, **options):

         # --- REDIS LOCK START ---
        redis = get_redis_connection("default")

        # Try to acquire lock
        if not redis.set("shelve_talker_lock", "1", nx=True, ex=3600):
            self.stdout.write("Job already running, exiting")
            return
        # --- REDIS LOCK END ---

        self.stdout.write("Starting shelf talker cache load...")

        # Clear Redis (safe if Redis is dedicated)
        cache.clear()

        today = date.today()

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT barcode, description, pack_size, price, vat_percent
                FROM shelve_talkers
            """)
            rows = cursor.fetchall()

        # Calculate TTL → seconds until next midnight
        now = datetime.now()
        next_midnight = (now + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        ttl_seconds = int((next_midnight - now).total_seconds())

        for barcode, desc, pack, price, vat in rows:
            key = f"shelve_talker:{barcode}"

            cache.set(
                key,
                {
                    "description": desc,
                    "pack_size": pack,
                    "price": str(price),
                    "vat_percent": str(vat),
                    "talker_date": today.isoformat(),
                },
                timeout=ttl_seconds
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Loaded {len(rows)} shelf talker records into Redis"
            )
        )

