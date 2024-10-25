from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework_simplejwt.tokens import AccessToken
from users.serializers import UserSerializer


class userAuthenticationTests(TestCase):
    def setUp(self):
        self.User = get_user_model()

        self.user = self.User.objects.create(
            username="authenticated_user",
            email="authenticated@email.com",
            password="Abcd123!",
        )

        self.access_token = AccessToken.for_user(self.user)

    def test_create_user_status_201_with_valid_data(
        self,
    ):
        user_data = {
            "username": "johndoe",
            "email": "johndoe@email.com",
            "password": "Abcd123!",
        }
        response = self.client.post(reverse("users:users-api-list"), data=user_data)

        self.assertEqual(201, response.status_code)

    def test_create_user_status_400_when_username_already_exists(self):
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

    def test_create_user_status_400_when_email_already_exists(self):
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

    def test_create_user_status_400_when_password_does_not_meet_requirements(self):
        # passing a right password
        user_data_with_right_password = {
            "username": "johndoe",
            "email": "johndsdoe@email.com",
            "password": "Abcd123!",
        }

        serializer = UserSerializer(data=user_data_with_right_password)
        self.assertTrue(serializer.is_valid())

        # passing a right password
        user_data_with_wrong_password = {
            "username": "johndoe",
            "email": "johndsdoe@email.com",
            "password": "abc",
        }

        serializer = UserSerializer(data=user_data_with_wrong_password)
        self.assertFalse(serializer.is_valid())

    def test_create_user_status_400_when_email_format_is_invalid(self):
        user = {
            "username": "John",
            "email": "wrong_email_format",
            "password": "Abcd123!",
        }

        response = self.client.post(reverse("users:users-api-list"), data=user)

        self.assertEqual(400, response.status_code)

    def test_retrieve_user_details_successfully(self):
        response = self.client.get(
            reverse("users:users-api-detail", args=[self.user.id]),  # type: ignore
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )

        self.assertEqual(200, response.status_code)

    def test_update_user_details_successfully(self):
        user_to_change = self.User.objects.create(
            username="change",
            email="change@email.com",
            password="Change123!",
        )

        access_token = AccessToken.for_user(user_to_change)

        new_username_email_and_password = {
            "username": "caca",
            "email": "caca@email.com",
            "password": "ABCD123!",
        }
        response = self.client.patch(
            reverse("users:users-api-detail", args=[user_to_change.id]),  # type: ignore
            data=new_username_email_and_password,
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
            content_type="application/json",
        )
        self.assertEqual(200, response.status_code)

    def test_delete_user_status_204_and_user_is_removed(self):
        user = self.User.objects.create(
            username="delete_me", email="deleteme@email.com", password="Abcd123!"
        )

        access_token = AccessToken.for_user(user)

        response = self.client.delete(
            reverse("users:users-api-detail", args=[user.id]),  # type: ignore
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )

        self.assertEqual(204, response.status_code)


class userFollowTests(TestCase):
    def setUp(self):
        self.User = get_user_model()

        self.user = self.User.objects.create(
            username="authenticated_user",
            email="authenticated@email.com",
            password="Abcd123!",
        )
        self.user_access_token = AccessToken.for_user(self.user)

        self.admin_user = self.User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="Admin123!",
        )
        self.admin_access_token = AccessToken.for_user(self.admin_user)

    def test_user_can_follow_another_user_successfully(self):
        user = self.User.objects.create(
            username="user", email="user@email.com", password="Abcd123!"
        )

        user_access_token = AccessToken.for_user(user)

        another_user = self.User.objects.create(
            username="another_user", email="anotheruser@email.com", password="Abcd123!"
        )

        # user => following => another_user
        response = self.client.post(
            reverse("users:users-api-follow"),
            data={"id_user_to_follow": another_user.id},  # type: ignore
            HTTP_AUTHORIZATION=f"Bearer {user_access_token}",
        )
        self.assertEqual(204, response.status_code)

    def test_user_can_unfollow_another_user_successfully(self):
        user = self.User.objects.create(
            username="user", email="user@email.com", password="Abcd123!"
        )

        user_access_token = AccessToken.for_user(user)

        another_user = self.User.objects.create(
            username="another_user", email="anotheruser@email.com", password="Abcd123!"
        )

        # user => following => another_user (without using the endpoint)
        user.profile.following.add(another_user.profile)  # type: ignore
        another_user.profile.followers.add(user.profile)  # type: ignore

        # user => unfollowing => another_user
        response = self.client.post(
            reverse("users:users-api-unfollow"),
            data={"id_user_to_unfollow": another_user.id},  # type: ignore
            HTTP_AUTHORIZATION=f"Bearer {user_access_token}",
        )
        self.assertEqual(204, response.status_code)

    def test_following_self_status_400(self):
        response = self.client.post(
            reverse("users:users-api-follow"),
            data={"id_user_to_follow": self.user.id},  # type: ignore
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )
        self.assertEqual(400, response.status_code)

    def test_following_admin_user_status_400(self):
        response = self.client.post(
            reverse("users:users-api-follow"),
            data={"id_user_to_follow": self.admin_user.id},  # type: ignore
            HTTP_AUTHORIZATION=f"Bearer {self.user_access_token}",
        )

        self.assertEqual(400, response.status_code)

    def test_following_already_followed_user_status_400(self):
        user = self.User.objects.create(
            username="user", email="user@email.com", password="Abcd123!"
        )

        user_access_token = AccessToken.for_user(user)

        another_user = self.User.objects.create(
            username="another_user", email="anotheruser@email.com", password="Abcd123!"
        )

        # user => following => another_user (without using the endpoint)
        user.profile.following.add(another_user.profile)  # type: ignore
        another_user.profile.followers.add(user.profile)  # type: ignore

        # user => try following again
        response = self.client.post(
            reverse("users:users-api-follow"),
            data={"id_user_to_follow": another_user.id},  # type: ignore
            HTTP_AUTHORIZATION=f"Bearer {user_access_token}",
        )
        self.assertEqual(400, response.status_code)
