from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from users.serializers import UserSerializer


class userModelTests(TestCase):
    def setUp(self):
        self.User = get_user_model()

    def test_if_when_create_user_status_is_201_and_user_is_saved_with_correct_data(
        self,
    ):
        user_data = {
            "username": "johndoe",
            "email": "johndoe@email.com",
            "password": "Abcd123!",
        }
        response = self.client.post(reverse("users:users-api-list"), data=user_data)

        self.assertEqual(201, response.status_code)
        self.assertTrue(
            self.User.objects.filter(username=user_data["username"]).exists()
        )
        self.assertEqual(response.data["username"], user_data["username"])  # type: ignore
        self.assertEqual(response.data["email"], user_data["email"])  # type: ignore

    def test_if_status_code_400_when_missing_username(self):
        user_data = {
            "email": "johndoe@email.com",
            "password": "Abcd123!",
        }

        response = self.client.post(reverse("users:users-api-list"), data=user_data)

        self.assertEqual(400, response.status_code)

    def test_if_status_code_400_when_missing_email(self):
        user_data = {"username": "johndoe", "password": "Abcd123!"}

        response = self.client.post(reverse("users:users-api-list"), data=user_data)

        self.assertEqual(400, response.status_code)

    def test_if_status_code_is_400_when_username_already_exists_in_db(self):
        self.User.objects.create_user(
            username="johndoe2", email="existing@email.com", password="Abcd123!"
        )

        user_data = {
            "username": "johndoe2",
            "email": "anotheremail@email.com",
            "password": "Abcd123!",
        }

        response = self.client.post(reverse("users:users-api-list"), data=user_data)

        self.assertEqual(400, response.status_code)

    def test_if_status_code_is_400_when_email_already_exists_in_db(self):
        self.User.objects.create_user(
            username="johndoe2", email="existing@email.com", password="Abcd123!"
        )

        user_data = {
            "username": "johndoe3",
            "email": "existing@email.com",
            "password": "Abcd123!",
        }

        response = self.client.post(reverse("users:users-api-list"), data=user_data)

        self.assertEqual(400, response.status_code)

    def test_if_email_meets_is_been_validate_by_it_requeriments(self):
        # passing a right password
        user_data_with_right_password = {
            "username": "johndoe",
            "email": "johndsdoe@email.com",
            "password": "Abcd123!",
        }

        serializer = UserSerializer(data = user_data_with_right_password)
        self.assertTrue(serializer.is_valid())
        
        # passing a right password
        user_data_with_wrong_password = {
            "username": "johndoe",
            "email": "johndsdoe@email.com",
            "password": "abc",
        }

        serializer = UserSerializer(data = user_data_with_wrong_password)
        self.assertFalse(serializer.is_valid())
        
