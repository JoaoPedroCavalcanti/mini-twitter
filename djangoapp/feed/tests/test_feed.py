import json
from datetime import datetime

from minitwitter.settings import REST_FRAMEWORK
from rest_framework.routers import reverse
from tests_base.base_test import BaseTest


class TestsFeed(BaseTest):
    def setUp(self):
        super().setUp()

    def test_feed_status_200_for_authenticated_user(self):
        response = self.client.get(
            reverse("feed:user-feed"),
            HTTP_AUTHORIZATION=f"Bearer {self.token_user_a}",
        )

        self.assertEqual(200, response.status_code)

    def test_feed_status_403_for_unauthenticated_user(self):
        response = self.client.get(reverse("feed:user-feed"))

        self.assertEqual(401, response.status_code)

    def test_feed_shows_only_posts_from_followed_users(self):
        user_a = self.create_user(
            username="user_a", email="user_a@email.com", password="Abcd123!"
        )
        token_user_a = self.create_token(user=user_a)

        user_b = self.create_user(
            username="user_b", email="user_b@email.com", password="Abcd123!"
        )
        # creating two posts from user b
        self.create_post(user=user_b, content="post from user b")
        self.create_post(user=user_b, content="second post from user b")

        self.follow(user_a, user_b)

        response = self.client.get(
            reverse("feed:user-feed"),
            HTTP_AUTHORIZATION=f"Bearer {token_user_a}",
        )

        content = json.loads(response.content.decode("utf-8"))

        # Get ids of all posts returned
        all_post_user_ids = []
        for i in range(0, content.get("count")):
            all_post_user_ids.append(content.get("results")[i].get("poster_user"))

        followed_user_ids = []
        for user in user_a.profile.following.all():  # type: ignore
            followed_user_ids.append(user.id)

        for user_id in all_post_user_ids:
            self.assertIn(user_id, followed_user_ids)

    def test_feed_excludes_posts_from_unfollowed_users(self):
        # Creating three users
        user_a = self.create_user(
            username="user_a", email="user_a@email.com", password="Abcd123!"
        )
        user_b = self.create_user(
            username="user_b", email="user_b@email.com", password="Abcd123!"
        )
        user_c = self.create_user(
            username="user_c", email="user_c@email.com", password="Abcd123!"
        )

        # Get token for user_a
        token_user_a = self.create_token(user_a)

        # Creating two posts from user b and one for user c
        self.create_post(user=user_b, content="post from user b")
        self.create_post(user=user_b, content="second post from user b")
        post_from_user_c = self.create_post(user=user_c, content="post from user c")

        # Making user_a follow user_b
        self.follow(user_a, user_b)

        # Access the endpoint as user_a
        response = self.client.get(
            reverse("feed:user-feed"),
            HTTP_AUTHORIZATION=f"Bearer {token_user_a}",
        )

        content = json.loads(response.content.decode("utf-8"))

        # Get all id from posts of the feed
        all_post_user_ids = [post.get("poster_user") for post in content.get("results")]

        # Get the id of post from user c
        id_post_from_user_c = post_from_user_c.id  # type: ignore

        # Test if feed of user_a does not show the post from user_c
        self.assertNotIn(id_post_from_user_c, all_post_user_ids)

    def test_feed_shows_posts_in_reverse_chronological_order(self):
        # Creating three users
        user_a = self.create_user(
            username="user_a", email="user_a@email.com", password="Abcd123!"
        )
        user_b = self.create_user(
            username="user_b", email="user_b@email.com", password="Abcd123!"
        )

        # Get token for user_a
        token_user_a = self.create_token(user_a)

        # Creating two posts from user b
        self.create_post(user=user_b, content="First post")
        self.create_post(user=user_b, content="Second post")

        # Making user_a follow user_b
        self.follow(user_a, user_b)

        # Access the endpoint as user_a
        response = self.client.get(
            reverse("feed:user-feed"),
            HTTP_AUTHORIZATION=f"Bearer {token_user_a}",
        )

        content = json.loads(response.content.decode("utf-8"))

        # Extract the timestamps of the posts
        post_timestamps = []
        for i in range(0, content.get("count")):
            post_timestamps.append(content.get("results")[i].get("created_at"))

        # Converting to datetime
        datetimes = [datetime.fromisoformat(ts) for ts in post_timestamps]

        # Finding most recent
        most_recent = max(datetimes)

        # Test if is in cronological order
        self.assertEqual(most_recent, datetimes[0])

    def test_feed_pagination_returns_correct_number_of_posts_per_page(self):
        # Creating users
        user_a = self.create_user(
            username="user_a", email="user_a@email.com", password="Abcd123!"
        )
        user_b = self.create_user(
            username="user_b", email="user_b@email.com", password="Abcd123!"
        )

        # user_a token
        token_user_a = self.create_token(user_a)

        # Creating posts from user_b
        for i in range(20):
            self.create_post(user_b, content=f"Post number: {i}")

        # user_a following user_b
        self.follow(user_a, user_b)

        # Getting numbers of pages (from settings)
        nums_of_page = REST_FRAMEWORK.get("PAGE_SIZE")

        response = self.client.get(
            f"{reverse('feed:user-feed')}?page=1",
            HTTP_AUTHORIZATION=f"Bearer {token_user_a}",
        )

        self.assertEqual(nums_of_page, len(response.data.get("results")))  # type: ignore
