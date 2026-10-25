from decimal import Decimal

from rest_framework import status
from rest_framework.test import APITestCase

from rentals.models import Rental
from rentals.tests.test_base import (
    sample_user,
    sample_user_staff,
    sample_car,
    sample_rental,
    get_rental_list_url,
    today_plus_days,
    CANCELED,
    get_rental_detail_url,
    BOOKED,
    COMPLETED,
    today_minus_days,
    get_rental_cancel_url,
    get_rental_return_url,
    today,
    OVERDUE,
)


class RentalListRetrieveTests(APITestCase):
    def setUp(self):
        self.user1 = sample_user(email="user1@test.com")
        self.user2 = sample_user(email="user2@test.com")
        self.staff = sample_user_staff(email="admin@test.com")
        self.car = sample_car()
        self.rental = sample_rental(self.user1, self.car)
        self.rental_2 = sample_rental(
            self.user2,
            self.car,
            start_date=today_plus_days(20),
            end_date=today_plus_days(23),
        )

    def test_unauthenticated_get_is_denied(self):
        res = self.client.get(get_rental_list_url())
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_customer_sees_only_own_rentals(self):
        self.client.force_authenticate(self.user1)
        res = self.client.get(get_rental_list_url())
        ids = [r["id"] for r in res.data["results"]]
        self.assertEqual(res.data["count"], 1)
        self.assertEqual(ids, [self.rental.id])

    def test_staff_sees_all_rentals(self):
        self.client.force_authenticate(self.staff)
        res = self.client.get(get_rental_list_url())
        self.assertEqual(res.data["count"], 2)

    def test_staff_can_filter_by_user_id(self):
        self.client.force_authenticate(self.staff)
        res = self.client.get(get_rental_list_url(), {"user_id": self.user2.id})
        ids = [r["id"] for r in res.data["results"]]
        self.assertEqual(ids, [self.rental_2.id])

    def test_filter_by_status(self):
        canceled = sample_rental(
            self.user1,
            self.car,
            start_date=today_plus_days(12),
            end_date=today_plus_days(15),
            status=CANCELED,
        )
        self.client.force_authenticate(self.user1)
        res = self.client.get(get_rental_list_url(), {"status": CANCELED})
        ids = [r["id"] for r in res.data["results"]]
        self.assertEqual(ids, [canceled.id])

    def test_retrieve_own_rental(self):
        self.client.force_authenticate(self.user1)
        res = self.client.get(get_rental_detail_url(self.rental.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["id"], self.rental.id)

    def test_retrieve_other_users_rental_is_404(self):
        self.client.force_authenticate(self.user1)
        res = self.client.get(get_rental_detail_url(self.rental_2.id))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_staff_can_retrieve_any_rental(self):
        self.client.force_authenticate(self.staff)
        res = self.client.get(get_rental_detail_url(self.rental_2.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class RentalCreateTests(APITestCase):
    def setUp(self):
        self.user1 = sample_user(email="user1@test.com")
        self.user2 = sample_user(email="user2@test.com")
        self.car = sample_car(inventory=2)
        self.client.force_authenticate(self.user1)

    def payload(self, **params):
        data = {
            "car": self.car.id,
            "start_date": today_plus_days(3),
            "end_date": today_plus_days(6),
        }
        data.update(params)
        return data

    def test_create_success(self):
        res = self.client.post(get_rental_list_url(), self.payload())
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        rental = Rental.objects.get(pk=res.data["id"])
        self.assertEqual(rental.user, self.user1)
        self.assertEqual(rental.status, BOOKED)
        self.assertEqual(rental.price_per_day, Decimal("45.00"))
        self.assertIsNone(rental.actual_return_date)

        self.car.refresh_from_db()
        self.assertEqual(self.car.inventory, 1)

    def test_client_cannot_set_user_status_or_price(self):
        data = self.payload(user=self.user2.id, status=COMPLETED, price_per_day="0.01")
        res = self.client.post(get_rental_list_url(), data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        rental = Rental.objects.get(pk=res.data["id"])
        self.assertEqual(rental.user, self.user1)
        self.assertEqual(rental.status, BOOKED)
        self.assertEqual(rental.price_per_day, Decimal("45.00"))

    def test_start_date_in_past_rejected(self):
        data = self.payload(start_date=today_minus_days(1), end_date=today_plus_days(2))
        res = self.client.post(get_rental_list_url(), data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.car.refresh_from_db()
        self.assertEqual(self.car.inventory, 2)
        self.assertEqual(Rental.objects.count(), 0)

    def test_end_date_earlier_start_date_rejected(self):
        data = self.payload(
            start_date=today_plus_days(6),
            end_date=today_plus_days(3),
        )
        res = self.client.post(get_rental_list_url(), data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.car.inventory, 2)
        self.assertEqual(Rental.objects.count(), 0)

    def test_car_without_inventory_rejected(self):
        self.car.inventory = 0
        self.car.save()
        res = self.client.post(get_rental_list_url(), self.payload())
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.car.inventory, 0)
        self.assertEqual(Rental.objects.count(), 0)

    def test_unknown_car_rejected(self):
        res = self.client.post(
            get_rental_list_url(), self.payload(car=99999), format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_fields_rejected(self):
        res = self.client.post(get_rental_list_url(), {}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_cannot_create(self):
        self.client.force_authenticate(None)
        res = self.client.post(get_rental_list_url(), self.payload())
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_overlapping_dates_for_same_car_rejected(self):
        start_date = today_plus_days(3)
        end_date = today_plus_days(6)
        sample_rental(self.user2, self.car, start_date=start_date, end_date=end_date)

        res = self.client.post(
            get_rental_list_url(),
            self.payload(start_date=start_date, end_date=end_date),
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class RentalCancelTests(APITestCase):
    def setUp(self):
        self.user = sample_user(email="user1@test.com")
        self.other = sample_user(email="user2@test.com")
        self.staff = sample_user_staff(email="admin@test.com")
        self.car = sample_car(inventory=0)
        self.client.force_authenticate(self.user)

    def test_owner_cancels_booked_rental(self):
        rental = sample_rental(self.user, self.car)
        res = self.client.post(get_rental_cancel_url(rental.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["status"], CANCELED)
        rental.refresh_from_db()
        self.car.refresh_from_db()
        self.assertEqual(rental.status, CANCELED)
        self.assertEqual(self.car.inventory, 1)

    def test_cancel_day_before_start_is_still_allowed(self):
        rental = sample_rental(
            self.user,
            self.car,
            start_date=today_plus_days(1),
            end_date=today_plus_days(4),
        )
        res = self.client.post(get_rental_cancel_url(rental.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_cancel_after_start_date_rejected(self):
        rental = sample_rental(
            self.user,
            self.car,
            start_date=today_minus_days(1),
            end_date=today_plus_days(2),
        )
        res = self.client.post(get_rental_cancel_url(rental.id))

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        rental.refresh_from_db()
        self.car.refresh_from_db()
        self.assertEqual(rental.status, BOOKED)
        self.assertEqual(self.car.inventory, 0)

    def test_cancel_twice_rejected_and_inventory_not_doubled(self):
        rental = sample_rental(self.user, self.car)

        self.client.post(get_rental_cancel_url(rental.id))
        res = self.client.post(get_rental_cancel_url(rental.id))

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.car.refresh_from_db()
        self.assertEqual(self.car.inventory, 1)

    def test_cannot_cancel_completed_rental(self):
        rental = sample_rental(self.user, self.car, status=COMPLETED)
        res = self.client.post(get_rental_cancel_url(rental.id))
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_cancel_other_users_rental(self):
        rental = sample_rental(self.other, self.car)
        res = self.client.post(get_rental_cancel_url(rental.id))

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        rental.refresh_from_db()
        self.assertEqual(rental.status, BOOKED)

    def test_staff_can_cancel_any_rental(self):
        self.client.force_authenticate(self.staff)
        rental = sample_rental(self.user, self.car)
        res = self.client.post(get_rental_cancel_url(rental.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_unauthenticated_cancel_denied(self):
        self.client.force_authenticate(None)
        rental = sample_rental(self.user, self.car)
        res = self.client.post(get_rental_cancel_url(rental.id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class RentalReturnTests(APITestCase):
    def setUp(self):
        self.user = sample_user(email="user1@test.com")
        self.other = sample_user(email="user2@test.com")
        self.staff = sample_user_staff(email="admin@test.com")
        self.car = sample_car(inventory=0)
        self.client.force_authenticate(self.user)

    def test_return_in_time(self):
        rental = sample_rental(
            self.user,
            self.car,
            start_date=today_minus_days(1),
            end_date=today_plus_days(2),
        )
        res = self.client.post(get_rental_return_url(rental.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        rental.refresh_from_db()
        self.car.refresh_from_db()
        self.assertEqual(rental.status, COMPLETED)
        self.assertEqual(rental.actual_return_date, today())
        self.assertEqual(self.car.inventory, 1)

    def test_late_return_is_still_completed(self):
        rental = sample_rental(
            self.user,
            self.car,
            start_date=today_minus_days(5),
            end_date=today_minus_days(2),
        )
        res = self.client.post(get_rental_return_url(rental.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        rental.refresh_from_db()
        self.car.refresh_from_db()
        self.assertEqual(rental.status, COMPLETED)
        self.assertEqual(rental.actual_return_date, today())
        self.assertEqual(self.car.inventory, 1)

    def test_overdue_rental_can_be_returned(self):
        rental = sample_rental(
            self.user,
            self.car,
            start_date=today_minus_days(5),
            end_date=today_minus_days(2),
            status=OVERDUE,
        )
        res = self.client.post(get_rental_return_url(rental.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        rental.refresh_from_db()
        self.assertEqual(rental.status, COMPLETED)

    def test_return_before_rental_start_rejected(self):
        rental = sample_rental(self.user, self.car)
        res = self.client.post(get_rental_return_url(rental.id))

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        rental.refresh_from_db()
        self.car.refresh_from_db()
        self.assertEqual(rental.status, BOOKED)
        self.assertEqual(self.car.inventory, 0)

    def test_return_twice_rejected_and_inventory_not_doubled(self):
        rental = sample_rental(
            self.user,
            self.car,
            start_date=today_minus_days(1),
            end_date=today_plus_days(2),
        )

        self.client.post(get_rental_return_url(rental.id))
        res = self.client.post(get_rental_return_url(rental.id))

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.car.refresh_from_db()
        self.assertEqual(self.car.inventory, 1)

    def test_cannot_return_canceled_rental(self):
        rental = sample_rental(self.user, self.car, status=CANCELED)
        res = self.client.post(get_rental_return_url(rental.id))
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_return_other_users_rental(self):
        rental = sample_rental(
            self.other,
            self.car,
            start_date=today_minus_days(3),
            end_date=today(),
        )
        res = self.client.post(get_rental_return_url(rental.id))

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        rental.refresh_from_db()
        self.assertEqual(rental.status, BOOKED)

    def test_staff_can_return_any_rental(self):
        self.client.force_authenticate(self.staff)
        rental = sample_rental(self.user, self.car, start_date=today_minus_days(2))
        res = self.client.post(get_rental_return_url(rental.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        rental.refresh_from_db()
        self.car.refresh_from_db()
        self.assertEqual(rental.status, COMPLETED)
        self.assertEqual(rental.actual_return_date, today())
        self.assertEqual(self.car.inventory, 1)

    def test_unauthenticated_return_denied(self):
        self.client.force_authenticate(None)
        rental = sample_rental(self.user, self.car)
        res = self.client.post(get_rental_return_url(rental.id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
