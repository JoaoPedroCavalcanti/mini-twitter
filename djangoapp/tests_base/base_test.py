from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import PostModel
from rest_framework_simplejwt.tokens import AccessToken


class BaseTest(TestCase):
    def refresh_user_profiles(self, *users):
        for user in users:
            user.profile.refresh_from_db()

    def create_user(self, username, email, password):
        self.User = get_user_model()
        return self.User.objects.create(
            username=username, email=email, password=password
        )

    def create_post(self, user, content):
        return PostModel.objects.create(poster_user=user, text_content=content)

    def create_token(self, user):
        return AccessToken.for_user(user)

    def follow(self, user_following, user_to_follow):
        user_following.profile.following.add(user_to_follow.profile)
        user_to_follow.profile.followers.add(user_following.profile)
        self.refresh_user_profiles(user_following, user_to_follow)

    def unfollow(self, user_following, user_to_follow):
        user_following.profile.following.remove(user_to_follow.profile)
        user_to_follow.profile.followers.remove(user_following.profile)
        self.refresh_user_profiles(user_following, user_to_follow)

    def setUp(self):
        self.User = get_user_model()

        self.user_a = self.create_user(
            "base_user_a", "base_user_a@email.com", password="Abcd123!"
        )
        self.user_b = self.create_user(
            "base_user_b", "base_user_b@email.com", password="Abcd123!"
        )
        self.user_c = self.create_user(
            "base_user_c", "base_user_c@email.com", password="Abcd123!"
        )

        self.post_a = self.create_post(self.user_a, "base post from user a")
        self.post_b = self.create_post(self.user_b, "base post from user b")
        self.post_c = self.create_post(self.user_c, "base post from user c")

        self.token_user_a = self.create_token(self.user_a)
        self.token_user_b = self.create_token(self.user_b)
        self.token_user_c = self.create_token(self.user_c)
