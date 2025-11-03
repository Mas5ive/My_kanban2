from http import HTTPStatus
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from ninja.testing import TestClient

from my_kanban2.utils import ParametrizedTestCaseMeta, parametrize
from thisapp.api.boards import router as boards_router
from thisapp.models import Board, Membership

User = get_user_model()


class BoardsAPITestCase(TestCase, metaclass=ParametrizedTestCaseMeta):
    API_URL_PATH = '/boards'
    fixtures = ['demo/demo-data.json']

    def setUp(self):
        self.client = TestClient(boards_router)
        self.user = User.objects.get(username='TestUser1')


class GetBoardsAPITestCase(BoardsAPITestCase):

    def test_get_success_for_user_with_boards(self):
        self.owner_board = Board.objects.get(id=1)
        self.member_board = Board.objects.get(id=2)
        response = self.client.get(self.API_URL_PATH, user=self.user)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.json()
        self.assertIn('owner_boards', data)
        self.assertIn('member_boards', data)
        self.assertEqual(len(data['owner_boards']), 1)
        self.assertEqual(data['owner_boards'][0]['id'], self.owner_board.id)
        self.assertEqual(data['owner_boards'][0]['title'], self.owner_board.title)
        self.assertEqual(len(data['member_boards']), 1)
        self.assertEqual(data['member_boards'][0]['id'], self.member_board.id)
        self.assertEqual(data['member_boards'][0]['title'], self.member_board.title)

    def test_get_for_unauthenticated_user(self):
        response = self.client.get(self.API_URL_PATH)
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)


class CreateBoardsAPITestCase(BoardsAPITestCase):

    def test_create_successefully(self):
        board_title = 'New Test Board'
        response = self.client.post(self.API_URL_PATH, json={'title': board_title}, user=self.user)
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertIn('details', response.json())
        self.assertEqual(response.json()['details'], 'The board created successfully')
        self.assertTrue(Board.objects.filter(title=board_title).exists())
        self.assertTrue(Membership.objects.filter(user=self.user, board__title=board_title).exists())

    @parametrize(
        'data', [
            [{}],
            [{'title': ''}],
            [{'title': ' '}],
            [{'title': 'a' * 33}],
        ]
    )
    def test_create_unsuccessfully(self, data):
        response = self.client.post(self.API_URL_PATH, json=data, user=self.user)
        self.assertEqual(response.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)

    def test_create_for_unauthenticated_user(self):
        response = self.client.post(self.API_URL_PATH, json={'title': 'Unauthorized Board'})
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)


class DeleteBoardsAPITestCase(BoardsAPITestCase):

    API_URL_PATH = BoardsAPITestCase.API_URL_PATH + '/{board_id}'

    @patch('thisapp.api.boards.invs.delete_board_invitations')
    def test_delete_successfully(self, mock_delete_board_invitations):
        board_id_to_delete = 1
        response = self.client.delete(self.API_URL_PATH.format(board_id=board_id_to_delete), user=self.user)
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
        self.assertFalse(Board.objects.filter(id=board_id_to_delete).exists())
        mock_delete_board_invitations.assert_called_once_with(board_id_to_delete)

    @parametrize(
        ('board_id', 'expected_status_code', 'message'),
        [
            (999, HTTPStatus.NOT_FOUND, 'The board not found.'),  # non existing board
            (2, HTTPStatus.FORBIDDEN, 'Only the owner can delete boards.'),  # Board owned by TestUser2
        ]
    )
    def test_delete_unsuccessfully(self, board_id, expected_status_code, message):
        response = self.client.delete(self.API_URL_PATH.format(board_id=board_id), user=self.user)
        self.assertEqual(response.status_code, expected_status_code)
        self.assertIn('details', response.json())
        self.assertEqual(response.json()['details'], message)

    def test_delete_for_unauthenticated_user(self):
        board_id_to_delete = 1
        response = self.client.delete(self.API_URL_PATH.format(board_id=board_id_to_delete))
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)
