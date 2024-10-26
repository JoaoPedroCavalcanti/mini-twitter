from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import PostModel
from rest_framework.routers import reverse
from rest_framework_simplejwt.tokens import AccessToken


class PostTestsCRUD(TestCase):
    def setUp(self):
        self.User = get_user_model()

        self.user = self.User.objects.create(
            username="posts_username", email="posts@email.com", password="Abcd123!"
        )
        self.user_token = AccessToken.for_user(self.user)

        self.post = PostModel.objects.create(
            poster_user=self.user, text_content="self post"
        )

    # Creation
    def test_create_post_status_201_with_valid_data(self):
        post_data = {"text_content": "My Post"}

        response = self.client.post(
            reverse("posts:posts-api-list"),
            data=post_data,
            HTTP_AUTHORIZATION=f"Bearer {self.user_token}",
        )

        self.assertEqual(201, response.status_code)

    def test_create_post_status_401_without_authentication(self):
        post_data = {"text_content": "My Post2"}

        response = self.client.post(reverse("posts:posts-api-list"), data=post_data)

        self.assertEqual(401, response.status_code)

    # List
    def test_list_posts_status_200(self):
        response = self.client.get(
            reverse("posts:posts-api-list"),
            HTTP_AUTHORIZATION=f"Bearer {self.user_token}",
        )

        self.assertEqual(200, response.status_code)

    def test_list_posts_status_401_without_authentication(self):
        response = self.client.get(reverse("posts:posts-api-list"))

        self.assertEqual(401, response.status_code)

    # Details
    def test_retrieve_post_status_200(self):
        response = self.client.get(
            reverse("posts:posts-api-detail", args=[self.post.id]),  # type: ignore
            HTTP_AUTHORIZATION=f"Bearer {self.user_token}",
        )
        self.assertEqual(200, response.status_code)

    def test_retrieve_post_status_404_for_nonexistent_post(self):
        random_id_for_post = 10**9
        response = self.client.get(
            reverse("posts:posts-api-detail", args=[random_id_for_post]),  # type: ignore
            HTTP_AUTHORIZATION=f"Bearer {self.user_token}",
        )
        self.assertEqual(404, response.status_code)

    # Update
    def test_update_post_status_200_with_valid_data(self):
        post = PostModel.objects.create(
            poster_user=self.user, text_content="post to test update with code 200"
        )
        text_update = {"text_content": "text updated"}

        response = self.client.patch(
            reverse("posts:posts-api-detail", args=[post.id]),  # type: ignore
            data=text_update,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.user_token}",
        )
        self.assertEqual(200, response.status_code)

    def test_update_post_status_403_for_other_user_post(self):
        other_user = self.User.objects.create(
            username="other_user", email="other_user@email.com", password="Abcd123!"
        )
        other_post = PostModel.objects.create(
            poster_user=other_user, text_content="other post"
        )
        text_update = {"text_content": "text updated"}

        response = self.client.patch(
            reverse("posts:posts-api-detail", args=[other_post.id]),  # type: ignore
            data=text_update,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.user_token}",
        )

        self.assertEqual(403, response.status_code)

    # Delete
    def test_delete_post_status_204(self):
        post = PostModel.objects.create(
            poster_user=self.user, text_content="post to delete"
        )

        response = self.client.delete(
            reverse("posts:posts-api-detail", args=[post.id]),  # type: ignore
            HTTP_AUTHORIZATION=f"Bearer {self.user_token}",
        )

        self.assertEqual(204, response.status_code)

    def test_delete_post_status_403_for_other_user_post(self):
        other_user = self.User.objects.create(
            username="other_user", email="other_user@email.com", password="Abcd123!"
        )
        other_post = PostModel.objects.create(
            poster_user=other_user, text_content="other post"
        )

        response = self.client.delete(
            reverse("posts:posts-api-detail", args=[other_post.id]),  # type: ignore
            HTTP_AUTHORIZATION=f"Bearer {self.user_token}",
        )

        self.assertEqual(403, response.status_code)


class PostTestsLikesAndDislike(TestCase):
    def setUp(self):
        self.User = get_user_model()

        self.user = self.User.objects.create(
            username="posts_username", email="posts@email.com", password="Abcd123!"
        )
        self.user_token = AccessToken.for_user(self.user)

        self.post = PostModel.objects.create(
            poster_user=self.user, text_content="self post"
        )

    def test_like_post_status_200(self):
        user = self.User.objects.create(
            username="like_username", email="lke@email.com", password="Abcd123!"
        )

        post = PostModel.objects.create(poster_user=user, text_content="post to like")

        post_id = {"post_id": post.id}  # type: ignore

        response = self.client.post(
            reverse("posts:posts-api-like-post"),
            data=post_id,
            HTTP_AUTHORIZATION=f"Bearer {self.user_token}",
        )

        self.assertEqual(200, response.status_code)

    def test_like_post_status_400_when_post_id_is_missing(self):
        response = self.client.post(
            reverse("posts:posts-api-like-post"),
            HTTP_AUTHORIZATION=f"Bearer {self.user_token}",
        )

        self.assertEqual(400, response.status_code)

    def test_like_post_status_400_when_post_already_liked(self):
        user = self.User.objects.create(
            username="like_username", email="lke@email.com", password="Abcd123!"
        )

        post = PostModel.objects.create(poster_user=user, text_content="post to like")

        post_id = {"post_id": post.id}  # type: ignore

        self.client.post(
            reverse("posts:posts-api-like-post"),
            data=post_id,
            HTTP_AUTHORIZATION=f"Bearer {self.user_token}",
        )

        response = self.client.post(
            reverse("posts:posts-api-like-post"),
            data=post_id,
            HTTP_AUTHORIZATION=f"Bearer {self.user_token}",
        )
        self.assertEqual(400, response.status_code)

    def test_dislike_post_status_200(self):
        user = self.User.objects.create(
            username="like_username", email="lke@email.com", password="Abcd123!"
        )

        post = PostModel.objects.create(poster_user=user, text_content="post to like")

        post_id = {"post_id": post.id}  # type: ignore

        self.client.post(
            reverse("posts:posts-api-like-post"),
            data=post_id,
            HTTP_AUTHORIZATION=f"Bearer {self.user_token}",
        )

        response = self.client.post(
            reverse("posts:posts-api-dislike-post"),
            data=post_id,
            HTTP_AUTHORIZATION=f"Bearer {self.user_token}",
        )
        self.assertEqual(200, response.status_code)

    def test_dislike_post_status_400_when_post_id_is_missing(self):
        user = self.User.objects.create(
            username="like_username", email="lke@email.com", password="Abcd123!"
        )

        post = PostModel.objects.create(poster_user=user, text_content="post to like")

        post_id = {"post_id": post.id}  # type: ignore

        self.client.post(
            reverse("posts:posts-api-like-post"),
            data=post_id,
            HTTP_AUTHORIZATION=f"Bearer {self.user_token}",
        )

        response = self.client.post(
            reverse("posts:posts-api-dislike-post"),
            HTTP_AUTHORIZATION=f"Bearer {self.user_token}",
        )

        self.assertEqual(400, response.status_code)

    def test_dislike_post_status_400_when_post_not_liked(self):
        user = self.User.objects.create(
            username="like_username", email="lke@email.com", password="Abcd123!"
        )

        post = PostModel.objects.create(poster_user=user, text_content="post to like")

        post_id = {"post_id": post.id}  # type: ignore

        response = self.client.post(
            reverse("posts:posts-api-dislike-post"),
            data=post_id,
            HTTP_AUTHORIZATION=f"Bearer {self.user_token}",
        )
        self.assertEqual(400, response.status_code)
