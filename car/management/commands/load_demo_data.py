from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.management import call_command
from django.core.management.base import BaseCommand

DEMO_IMAGES_DIR = Path(__file__).resolve().parents[2] / "fixtures" / "images"
# Must match the "image" paths of cars in initial_data.json
DEMO_IMAGES_PATH = "uploads/cars/demo"


class Command(BaseCommand):
    help = "Load demo data (initial_data.json) and copy demo car photos to MEDIA_ROOT."

    def add_arguments(self, parser):
        parser.add_argument(
            "--fixture",
            default=str(settings.BASE_DIR / "initial_data.json"),
            help="Fixture to load (default: initial_data.json in the project root).",
        )

    def handle(self, *args, **options):
        copied = 0
        for image in sorted(DEMO_IMAGES_DIR.glob("*.jpg")):
            name = f"{DEMO_IMAGES_PATH}/{image.name}"
            if default_storage.exists(name):
                continue
            with image.open("rb") as file:
                default_storage.save(name, File(file))
            copied += 1

        call_command("loaddata", options["fixture"], verbosity=options["verbosity"])

        self.stdout.write(
            self.style.SUCCESS(
                f"Demo data loaded, {copied} car photos copied to media."
            )
        )
