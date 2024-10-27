from django.urls import reverse
from rest_framework_simplejwt.tokens import AccessToken
from tests_base.base_test import BaseTest


class UserAuthenticationTests(BaseTest):
    def setUp(self):
        super().setUp()

    def test_create_user_status_201_with_valid_data(self):
        user_data = {
            "username": "johndoe",
            "email": "johndoe@email.com",
            "password": "Abcd123!",
        }
        response = self.client.post(reverse("users:users-api-list"), data=user_data)

        self.assertEqual(201, response.status_code)

    def test_create_user_status_400_when_username_already_exists(self):
        # Creating user_data with same name as self.user_a from BaseTest
        user_data = {
            "username": "base_user_a",
            "email": "anotheremail@email.com",
            "password": "Abcd123!",
        }
        response = self.client.post(reverse("users:users-api-list"), data=user_data)
        self.assertEqual(400, response.status_code)

    def test_create_user_status_400_when_email_already_exists(self):
        # Creating user_data with same name as self.user_a from BaseTest
        user_data = {
            "username": "johndoe3",
            "email": "base_user_a@email.com",
            "password": "Abcd123!",
        }

        response = self.client.post(reverse("users:users-api-list"), data=user_data)

        self.assertEqual(400, response.status_code)

    def test_create_user_status_400_when_password_does_not_meet_requirements(self):
        user_data_with_wrong_password = {
            "username": "johndoe",
            "email": "johndsdoe@email.com",
            "password": "abc",
        }

        response = self.client.post(
            reverse("users:users-api-list"), data=user_data_with_wrong_password
        )

        self.assertEqual(400, response.status_code)

    def test_create_user_status_400_when_email_format_is_invalid(self):
        user = {
            "username": "John",
            "email": "wrong_email_format",
            "password": "Abcd123!",
        }

        response = self.client.post(reverse("users:users-api-list"), data=user)

        self.assertEqual(400, response.status_code)

    def test_retrieve_user_details_successfully(self):
        # Using user_a created by BaseTest
        response = self.client.get(
            reverse("users:users-api-detail", args=[self.user_a.id]),  # type: ignore
            HTTP_AUTHORIZATION=f"Bearer {self.token_user_a}",
        )

        self.assertEqual(200, response.status_code)

    def test_update_user_details_successfully(self):
        # Creating user
        user_to_change = self.create_user(
            username="change", email="change@email.com", password="Change123!"
        )

        # Creating access token
        access_token = self.create_token(user_to_change)

        # Dict with new data
        new_username_email_and_password = {
            "username": "caca",
            "email": "caca@email.com",
            "password": "ABCD123!",
        }

        # Accessing the endpoint and passing the dict with new data
        response = self.client.patch(
            reverse("users:users-api-detail", args=[user_to_change.id]),  # type: ignore
            data=new_username_email_and_password,
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
            content_type="application/json",
        )
        self.assertEqual(200, response.status_code)

    def test_delete_user_status_204_and_user_is_removed(self):
        # Creating user to delete
        user = self.create_user(
            username="delete_me", email="deleteme@email.com", password="Abcd123!"
        )

        # Geting the access token
        access_token = self.create_token(user)

        # Deleting the user using endpoint
        response = self.client.delete(
            reverse("users:users-api-detail", args=[user.id]),  # type: ignore
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )

        self.assertEqual(204, response.status_code)


class UserFollowTests(BaseTest):
    def setUp(self):
        super().setUp()

    def test_user_can_follow_another_user_successfully(self):
        # Creating user
        user = self.create_user(
            username="user", email="user@email.com", password="Abcd123!"
        )

        # Creating access token
        user_access_token = AccessToken.for_user(user)

        # Creating another_user
        another_user = self.User.objects.create(
            username="another_user", email="anotheruser@email.com", password="Abcd123!"
        )

        # Making user follow another_user
        response = self.client.post(
            reverse("users:users-api-follow"),
            data={"id_user_to_follow": another_user.id},  # type: ignore
            HTTP_AUTHORIZATION=f"Bearer {user_access_token}",
        )
        self.assertEqual(204, response.status_code)

    def test_user_can_unfollow_another_user_successfully(self):
        # Creating user
        user = self.create_user(
            username="user", email="user@email.com", password="Abcd123!"
        )

        # Creating access token
        user_access_token = self.create_token(user)

        # Creating another_user
        another_user = self.create_user(
            username="another_user", email="anotheruser@email.com", password="Abcd123!"
        )

        # Making user follow another_user
        self.follow(user_following=user, user_to_follow=another_user)

        # Making user unfollow another_user
        response = self.client.post(
            reverse("users:users-api-unfollow"),
            data={"id_user_to_unfollow": another_user.id},  # type: ignore
            HTTP_AUTHORIZATION=f"Bearer {user_access_token}",
        )
        self.assertEqual(204, response.status_code)

    def test_following_self_status_400(self):
        # Creating user
        user = self.create_user(
            username="user", email="user@email.com", password="Abcd123!"
        )

        # Creating Acess token
        user_access_token = self.create_token(user)

        response = self.client.post(
            reverse("users:users-api-follow"),
            data={"id_user_to_follow": user.id},  # type: ignore
            HTTP_AUTHORIZATION=f"Bearer {user_access_token}",
        )
        self.assertEqual(400, response.status_code)

    def test_following_admin_user_status_400(self):
        # Creating super user
        super_user = self.create_super_user(
            username="super_user", email="super_user@email.com", password="Abcd123!"
        )

        # Access endpoint as user_a (created in BaseTest)
        response = self.client.post(
            reverse("users:users-api-follow"),
            data={"id_user_to_follow": super_user.id},  # type: ignore
            HTTP_AUTHORIZATION=f"Bearer {self.token_user_a}",
        )

        self.assertEqual(400, response.status_code)

    def test_following_already_followed_user_status_400(self):
        # Creating user
        user = self.create_user(
            username="user", email="user@email.com", password="Abcd123!"
        )

        # Creating Acess token
        user_access_token = self.create_token(user)

        # Creating another_user
        another_user = self.User.objects.create(
            username="another_user", email="anotheruser@email.com", password="Abcd123!"
        )

        # Making user follow another_user
        self.follow(user_following=user, user_to_follow=another_user)

        # User trying to follow another_user, again
        response = self.client.post(
            reverse("users:users-api-follow"),
            data={"id_user_to_follow": another_user.id},  # type: ignore
            HTTP_AUTHORIZATION=f"Bearer {user_access_token}",
        )
        self.assertEqual(400, response.status_code)
