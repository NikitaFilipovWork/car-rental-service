from datetime import date
from decimal import Decimal

from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from car.models import Car

CARS_URL = reverse("car:car-list")


def detail_url(car_id):
    return reverse("car:car-detail", args=[car_id])


def sample_car(**params):
    defaults = {
        "brand": "Toyota",
        "model": "Corolla",
        "year": 2020,
        "fuel_type": Car.FuelTypeChoices.GAS,
        "daily_rate": Decimal("45.00"),
        "inventory": 5,
    }
    defaults.update(params)
    return Car.objects.create(**defaults)


def valid_payload(**params):
    payload = {
        "brand": "BMW",
        "model": "X5",
        "year": 2022,
        "fuel_type": "GAS",
        "daily_rate": "90.00",
        "inventory": 1,
    }
    payload.update(params)
    return payload


class AnonymousCarApiTests(APITestCase):
    def setUp(self):
        # on_commit cache invalidation never fires inside TestCase
        cache.clear()
        self.car = sample_car()

    def test_list_cars(self):
        response = self.client.get(CARS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_retrieve_car(self):
        response = self.client.get(detail_url(self.car.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["brand"], "Toyota")

    def test_retrieve_nonexistent_car_returns_404(self):
        response = self.client.get(detail_url(999))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_car_forbidden(self):
        response = self.client.post(CARS_URL, valid_payload(), format="json")

        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )
        self.assertFalse(Car.objects.filter(brand="BMW").exists())

    def test_update_car_forbidden(self):
        response = self.client.patch(
            detail_url(self.car.id), {"inventory": 10}, format="json"
        )

        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )
        self.car.refresh_from_db()
        self.assertEqual(self.car.inventory, 5)

    def test_delete_car_forbidden(self):
        response = self.client.delete(detail_url(self.car.id))

        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )
        self.assertTrue(Car.objects.filter(id=self.car.id).exists())


class RegularUserCarApiTests(APITestCase):
    def setUp(self):
        # on_commit cache invalidation never fires inside TestCase
        cache.clear()
        self.user = get_user_model().objects.create_user(
            email="user@test.com", password="testpass123"
        )
        self.client.force_authenticate(self.user)
        self.car = sample_car()

    def test_list_cars(self):
        response = self.client.get(CARS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_car_forbidden(self):
        response = self.client.post(CARS_URL, valid_payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Car.objects.filter(brand="BMW").exists())

    def test_update_car_forbidden(self):
        response = self.client.patch(
            detail_url(self.car.id), {"inventory": 10}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.car.refresh_from_db()
        self.assertEqual(self.car.inventory, 5)

    def test_delete_car_forbidden(self):
        response = self.client.delete(detail_url(self.car.id))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Car.objects.filter(id=self.car.id).exists())


class StaffCarApiTests(APITestCase):
    def setUp(self):
        # on_commit cache invalidation never fires inside TestCase
        cache.clear()
        self.staff = get_user_model().objects.create_user(
            email="staff@test.com", password="testpass123", is_staff=True
        )
        self.client.force_authenticate(self.staff)
        self.car = sample_car()

    def test_create_car(self):
        response = self.client.post(CARS_URL, valid_payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        car = Car.objects.get(id=response.data["id"])
        self.assertEqual(car.brand, "BMW")
        self.assertEqual(car.daily_rate, Decimal("90.00"))

    def test_full_update_car(self):
        response = self.client.put(
            detail_url(self.car.id),
            valid_payload(brand="Honda", model="Civic"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.car.refresh_from_db()
        self.assertEqual(self.car.brand, "Honda")
        self.assertEqual(self.car.model, "Civic")

    def test_partial_update_car(self):
        response = self.client.patch(
            detail_url(self.car.id), {"inventory": 10}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.car.refresh_from_db()
        self.assertEqual(self.car.inventory, 10)

    def test_delete_car(self):
        response = self.client.delete(detail_url(self.car.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Car.objects.filter(id=self.car.id).exists())


class CarValidationTests(APITestCase):
    def setUp(self):
        # on_commit cache invalidation never fires inside TestCase
        cache.clear()
        self.staff = get_user_model().objects.create_user(
            email="staff@test.com", password="testpass123", is_staff=True
        )
        self.client.force_authenticate(self.staff)

    def test_current_year_is_valid(self):
        response = self.client.post(
            CARS_URL, valid_payload(year=date.today().year), format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_future_year_is_invalid(self):
        response = self.client.post(
            CARS_URL, valid_payload(year=date.today().year + 1), format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("year", response.data)

    def test_too_old_year_is_invalid(self):
        response = self.client.post(CARS_URL, valid_payload(year=1800), format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("year", response.data)

    def test_invalid_fuel_type(self):
        response = self.client.post(
            CARS_URL, valid_payload(fuel_type="WATER"), format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("fuel_type", response.data)

    def test_negative_inventory(self):
        response = self.client.post(
            CARS_URL, valid_payload(inventory=-1), format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("inventory", response.data)

    def test_negative_daily_rate(self):
        response = self.client.post(
            CARS_URL, valid_payload(daily_rate="-10.00"), format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("daily_rate", response.data)


class CarFilterTests(APITestCase):
    def setUp(self):
        # on_commit cache invalidation never fires inside TestCase
        cache.clear()
        self.corolla = sample_car(
            brand="Toyota",
            model="Corolla",
            year=2020,
            fuel_type=Car.FuelTypeChoices.GAS,
            inventory=5,
        )
        self.prius = sample_car(
            brand="Toyota",
            model="Prius",
            year=2021,
            fuel_type=Car.FuelTypeChoices.HYBRID,
            inventory=0,
        )
        self.tesla = sample_car(
            brand="Tesla",
            model="Model 3",
            year=2023,
            fuel_type=Car.FuelTypeChoices.ELECTRIC,
            inventory=2,
        )
        self.passat = sample_car(
            brand="Volkswagen",
            model="Passat",
            year=2019,
            fuel_type=Car.FuelTypeChoices.DIESEL,
            inventory=3,
        )

    def get_ids(self, params):
        response = self.client.get(CARS_URL, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return {car["id"] for car in response.data["results"]}

    def test_no_filters_returns_all(self):
        self.assertEqual(
            self.get_ids({}),
            {self.corolla.id, self.prius.id, self.tesla.id, self.passat.id},
        )

    def test_filter_by_brand_case_insensitive(self):
        self.assertEqual(
            self.get_ids({"brand": "TOYOTA"}),
            {self.corolla.id, self.prius.id},
        )

    def test_filter_by_partial_brand(self):
        self.assertEqual(self.get_ids({"brand": "volks"}), {self.passat.id})

    def test_filter_by_fuel_type(self):
        self.assertEqual(self.get_ids({"fuel_type": "ELECTRIC"}), {self.tesla.id})

    def test_filter_by_invalid_fuel_type(self):
        response = self.client.get(CARS_URL, {"fuel_type": "WATER"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_by_min_year(self):
        self.assertEqual(
            self.get_ids({"min_year": 2021}), {self.prius.id, self.tesla.id}
        )

    def test_filter_by_max_year(self):
        self.assertEqual(
            self.get_ids({"max_year": 2020}),
            {self.corolla.id, self.passat.id},
        )

    def test_filter_by_year_range(self):
        self.assertEqual(
            self.get_ids({"min_year": 2020, "max_year": 2021}),
            {self.corolla.id, self.prius.id},
        )

    def test_filter_available_true(self):
        self.assertEqual(
            self.get_ids({"available": "true"}),
            {self.corolla.id, self.tesla.id, self.passat.id},
        )

    def test_filter_available_false(self):
        self.assertEqual(self.get_ids({"available": "false"}), {self.prius.id})

    def test_combined_filters(self):
        self.assertEqual(
            self.get_ids({"brand": "toyota", "available": "true"}),
            {self.corolla.id},
        )
