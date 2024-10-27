from rest_framework.routers import reverse
from tests_base.base_test import BaseTest


class PostTestsCRUD(BaseTest):
    def setUp(self):
        self.user_to_post = self.create_user(
            username="posts_username", email="posts@email.com", password="Abcd123!"
        )
        self.token_user_to_post = self.create_token(self.user_to_post)
        super().setUp()

    # Creation
    def test_create_post_status_201_with_valid_data(self):
        post_data = {"text_content": "My Post"}

        response = self.client.post(
            reverse("posts:posts-api-list"),
            data=post_data,
            HTTP_AUTHORIZATION=f"Bearer {self.token_user_to_post}",
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
            HTTP_AUTHORIZATION=f"Bearer {self.token_user_to_post}",
        )

        self.assertEqual(200, response.status_code)

    def test_list_posts_status_401_without_authentication(self):
        response = self.client.get(reverse("posts:posts-api-list"))

        self.assertEqual(401, response.status_code)

    # Details
    def test_retrieve_post_status_200(self):
        # Create post
        post = self.create_post(self.user_to_post, "My post")

        response = self.client.get(
            reverse("posts:posts-api-detail", args=[post.id]),  # type: ignore
            HTTP_AUTHORIZATION=f"Bearer {self.token_user_to_post}",
        )
        self.assertEqual(200, response.status_code)

    def test_retrieve_post_status_404_for_nonexistent_post(self):
        random_id_for_post = 10**9
        response = self.client.get(
            reverse("posts:posts-api-detail", args=[random_id_for_post]),  # type: ignore
            HTTP_AUTHORIZATION=f"Bearer {self.token_user_to_post}",
        )
        self.assertEqual(404, response.status_code)

    # Update
    def test_update_post_status_200_with_valid_data(self):
        post = self.create_post(self.user_to_post, content="Post to update")

        text_update = {"text_content": "text updated"}

        response = self.client.patch(
            reverse("posts:posts-api-detail", args=[post.id]),  # type: ignore
            data=text_update,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.token_user_to_post}",
        )
        self.assertEqual(200, response.status_code)

    def test_update_post_status_403_for_other_user_post(self):
        other_user = self.create_user(
            username="other_user", email="other_user@email.com", password="Abcd123!"
        )
        other_post = self.create_post(user=other_user, content="Other content")
        text_update = {"text_content": "text updated"}

        response = self.client.patch(
            reverse("posts:posts-api-detail", args=[other_post.id]),  # type: ignore
            data=text_update,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.token_user_to_post}",
        )

        self.assertEqual(403, response.status_code)

    # Delete
    def test_delete_post_status_204(self):
        post = self.create_post(self.user_to_post, content="Post to delete")

        response = self.client.delete(
            reverse("posts:posts-api-detail", args=[post.id]),  # type: ignore
            HTTP_AUTHORIZATION=f"Bearer {self.token_user_to_post}",
        )

        self.assertEqual(204, response.status_code)

    def test_delete_post_status_403_for_other_user_post(self):
        other_user = self.create_user(
            username="other_user", email="other_user@email.com", password="Abcd123!"
        )
        other_post = self.create_post(user=other_user, content="Post to delete")

        response = self.client.delete(
            reverse("posts:posts-api-detail", args=[other_post.id]),  # type: ignore
            HTTP_AUTHORIZATION=f"Bearer {self.token_user_to_post}",
        )

        self.assertEqual(403, response.status_code)


class PostTestsLikesAndDislike(BaseTest):
    def setUp(self):
        self.user_to_post = self.create_user(
            username="posts_username", email="posts@email.com", password="Abcd123!"
        )
        self.token_user_to_post = self.create_token(self.user_to_post)
        super().setUp()

    def test_like_post_status_200(self):
        user = self.create_user(
            username="like_username", email="lke@email.com", password="Abcd123!"
        )

        post = self.create_post(user=user, content="Post to like")

        post_id = {"post_id": post.id}  # type: ignore

        response = self.client.post(
            reverse("posts:posts-api-like-post"),
            data=post_id,
            HTTP_AUTHORIZATION=f"Bearer {self.token_user_to_post}",
        )

        self.assertEqual(200, response.status_code)

    def test_like_post_status_400_when_post_id_is_missing(self):
        response = self.client.post(
            reverse("posts:posts-api-like-post"),
            HTTP_AUTHORIZATION=f"Bearer {self.token_user_to_post}",
        )

        self.assertEqual(400, response.status_code)

    def test_like_post_status_400_when_post_already_liked(self):
        user = self.create_user(
            username="like_username", email="lke@email.com", password="Abcd123!"
        )

        post = self.create_post(user=user, content="Post to like")

        post_id = {"post_id": post.id}  # type: ignore

        self.client.post(
            reverse("posts:posts-api-like-post"),
            data=post_id,
            HTTP_AUTHORIZATION=f"Bearer {self.token_user_to_post}",
        )

        response = self.client.post(
            reverse("posts:posts-api-like-post"),
            data=post_id,
            HTTP_AUTHORIZATION=f"Bearer {self.token_user_to_post}",
        )
        self.assertEqual(400, response.status_code)

    def test_dislike_post_status_200(self):
        user = self.create_user(
            username="like_username", email="lke@email.com", password="Abcd123!"
        )

        post = self.create_post(user=user, content="Post to like")

        post_id = {"post_id": post.id}  # type: ignore

        self.client.post(
            reverse("posts:posts-api-like-post"),
            data=post_id,
            HTTP_AUTHORIZATION=f"Bearer {self.token_user_to_post}",
        )

        response = self.client.post(
            reverse("posts:posts-api-dislike-post"),
            data=post_id,
            HTTP_AUTHORIZATION=f"Bearer {self.token_user_to_post}",
        )
        self.assertEqual(200, response.status_code)

    def test_dislike_post_status_400_when_post_id_is_missing(self):
        response = self.client.post(
            reverse("posts:posts-api-dislike-post"),
            HTTP_AUTHORIZATION=f"Bearer {self.token_user_to_post}",
        )

        self.assertEqual(400, response.status_code)

    def test_dislike_post_status_400_when_post_not_liked(self):
        user = self.create_user(
            username="like_username", email="lke@email.com", password="Abcd123!"
        )

        post = self.create_post(user=user, content="Post to like")

        post_id = {"post_id": post.id}  # type: ignore

        response = self.client.post(
            reverse("posts:posts-api-dislike-post"),
            data=post_id,
            HTTP_AUTHORIZATION=f"Bearer {self.token_user_to_post}",
        )
        self.assertEqual(400, response.status_code)
