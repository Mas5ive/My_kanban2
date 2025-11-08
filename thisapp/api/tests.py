from http import HTTPStatus
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from ninja.testing import TestClient

from my_kanban2.utils import ParametrizedTestCaseMeta, parametrize
from thisapp.api.boards import router as boards_router
from thisapp.api.membership import router as membership_router
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


class MembershipAPITestCase(TestCase, metaclass=ParametrizedTestCaseMeta):
    fixtures = ['demo/demo-data.json']

    def setUp(self):
        self.client = TestClient(membership_router)


class GetInvitationsAPITestCase(MembershipAPITestCase):

    API_URL_PATH = '/invitations'

    def setUp(self):
        super().setUp()
        self.user = User.objects.get(username='TestUser1')

    @patch('thisapp.api.membership.invs.get_user_invitations')
    def test_get_success_for_user_with_invites(self, mock_get_user_invitations):
        mock_get_user_invitations.return_value = [
            {'sender_name': 'TestUser2', 'board_id': 4, 'board_title': 'Test Board'}
        ]
        response = self.client.get(self.API_URL_PATH, user=self.user)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['sender_name'], 'TestUser2')
        self.assertEqual(data[0]['board_title'], 'Test Board')
        mock_get_user_invitations.assert_called_once_with(self.user.username)

    @patch('thisapp.api.membership.invs.get_user_invitations')
    def test_get_success_for_user_without_invites(self, mock_get_user_invitations):
        mock_get_user_invitations.return_value = []
        response = self.client.get(self.API_URL_PATH, user=self.user)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json(), [])
        mock_get_user_invitations.assert_called_once_with(self.user.username)

    def test_get_for_unauthenticated_user(self):
        response = self.client.get(self.API_URL_PATH)
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)


class CreateInvitationAPITestCase(MembershipAPITestCase):

    API_URL_PATH = '/invitations'

    @patch('thisapp.api.membership.invs.create_invitation')
    @patch('thisapp.api.membership.invs.get_invitation')
    def test_create_invitation_successfully(self, mock_get_invitation, mock_create_invitation):
        self.user = User.objects.get(username='TestUser3')
        mock_get_invitation.return_value = None
        recipient_name = 'TestUser2'
        payload = {'board_id': 3, 'recipient': recipient_name}
        response = self.client.post(self.API_URL_PATH, json=payload, user=self.user)
        self.assertEqual(response.json()['details'], 'The invitation successfully sent!')
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        mock_get_invitation.assert_called_once_with(payload['board_id'], payload['recipient'])
        mock_create_invitation.assert_called_once_with(
            payload['board_id'], self.user.username, recipient_name
        )

    @parametrize(
        ('payload', 'expected_status', 'expected_details'),
        [
            (
                {'board_id': 999, 'recipient': 'TestUser2'},
                HTTPStatus.NOT_FOUND,
                'The board not found.'
            ),
            (
                {'board_id': 2, 'recipient': 'TestUser3'},
                HTTPStatus.FORBIDDEN,
                'Only the owner of the board can send invitations.'
            ),
            (
                {'board_id': 1, 'recipient': 'UnknownUser'},
                HTTPStatus.NOT_FOUND,
                'The user “UnknownUser” not found.'
            ),
            (
                {'board_id': 1, 'recipient': 'TestUser3'},
                HTTPStatus.BAD_REQUEST,
                'The user “TestUser3” is already a member of the board.'
            ),
        ]
    )
    def test_create_invitation_unsuccessfully(self, payload, expected_status, expected_details):
        self.user = User.objects.get(username='TestUser1')
        response = self.client.post(self.API_URL_PATH, json=payload, user=self.user)
        self.assertEqual(response.status_code, expected_status)
        self.assertEqual(response.json()['details'], expected_details)

    @patch('thisapp.api.membership.invs.create_invitation')
    @patch('thisapp.api.membership.invs.get_invitation')
    def test_create_invitation_when_already_invited(self, mock_get_invitation, mock_create_invitation):
        self.user = User.objects.get(username='TestUser3')
        mock_get_invitation.return_value = {'id': 3}
        payload = {'board_id': 3, 'recipient': 'TestUser1'}
        response = self.client.post(self.API_URL_PATH, json=payload, user=self.user)
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(
            response.json()['details'],
            f'The user “{payload["recipient"]}” has already received an invitation.'
        )
        mock_get_invitation.assert_called_once_with(payload['board_id'], payload['recipient'])
        mock_create_invitation.assert_not_called()

    def test_create_for_unauthenticated_user(self):
        payload = {'board_id': 1, 'recipient': 'TestUser2'}
        response = self.client.post(self.API_URL_PATH, json=payload)
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)


class CreateMemberAPITestCase(MembershipAPITestCase):

    API_URL_PATH = '/boards/{board_id}/members'

    def setUp(self):
        super().setUp()
        self.user = User.objects.get(username='TestUser1')
        self.board_id = 3

    @patch('thisapp.api.membership.invs.delete_invitation')
    @patch('thisapp.api.membership.invs.get_invitation')
    def test_accept_invitation_successfully(self, mock_get_invitation, mock_delete_invitation):
        mock_get_invitation.return_value = True
        response = self.client.post(
            self.API_URL_PATH.format(board_id=self.board_id),
            json={'operation': 'accept'},
            user=self.user
        )
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertEqual(response.json()['details'], 'The invitation accepted.')
        self.assertTrue(Membership.objects.filter(user=self.user, board_id=self.board_id).exists())
        mock_get_invitation.assert_called_once_with(self.board_id, self.user.username)
        mock_delete_invitation.assert_called_once_with(self.board_id, self.user.username)

    @patch('thisapp.api.membership.invs.delete_invitation')
    @patch('thisapp.api.membership.invs.get_invitation')
    def test_reject_invitation_successfully(self, mock_get_invitation, mock_delete_invitation):
        mock_get_invitation.return_value = True
        response = self.client.post(
            self.API_URL_PATH.format(board_id=self.board_id),
            json={'operation': 'reject'},
            user=self.user
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json()['details'], 'The invitation rejected.')
        self.assertFalse(Membership.objects.filter(user=self.user, board_id=self.board_id).exists())
        mock_get_invitation.assert_called_once_with(self.board_id, self.user.username)
        mock_delete_invitation.assert_called_once_with(self.board_id, self.user.username)

    @patch('thisapp.api.membership.invs.get_invitation')
    def test_action_on_non_existent_invitation(self, mock_get_invitation):
        mock_get_invitation.return_value = None
        response = self.client.post(
            self.API_URL_PATH.format(board_id=self.board_id),
            json={'operation': 'accept'},
            user=self.user
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(response.json()['details'], 'The invitation not found.')
        mock_get_invitation.assert_called_once_with(self.board_id, self.user.username)

    def test_action_for_unauthenticated_user(self):
        response = self.client.post(
            self.API_URL_PATH.format(board_id=self.board_id),
            json={'operation': 'accept'}
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)


class DeleteMemberAPITestCase(MembershipAPITestCase):

    API_URL_PATH = '/boards/{board_id}/members/{member}'

    def setUp(self):
        super().setUp()
        self.user = User.objects.get(username='TestUser1')

    def test_delete_member_successfully(self):
        response = self.client.delete(
            self.API_URL_PATH.format(board_id=1, member='TestUser2'),
            user=self.user
        )
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
        self.assertFalse(Membership.objects.filter(board_id=1, user__username='TestUser2').exists())

    @parametrize(
        ('board_id', 'member_to_delete', 'expected_status', 'expected_details'),
        [
            (999, 'TestUser2', HTTPStatus.NOT_FOUND, 'The board not found.'),
            (2, 'TestUser2', HTTPStatus.FORBIDDEN, 'Only the owner of the board can delete members.'),
            (1, 'NonExistingUser', HTTPStatus.NOT_FOUND, 'The member not found.'),
            (1, 'TestUser1', HTTPStatus.BAD_REQUEST, 'incorrect operation for this user.')
        ]
    )
    def test_delete_member_unsuccessfully(self, board_id, member_to_delete, expected_status, expected_details):
        response = self.client.delete(
            self.API_URL_PATH.format(board_id=board_id, member=member_to_delete),
            user=self.user
        )
        self.assertEqual(response.status_code, expected_status)
        self.assertEqual(response.json()['details'], expected_details)

    def test_delete_member_for_unauthenticated_user(self):
        response = self.client.delete(
            self.API_URL_PATH.format(board_id=1, member='TestUser2')
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)
