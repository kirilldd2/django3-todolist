from django.test import TestCase, Client
from django.contrib.auth.models import User
from todo_app.models import Todo, GroupUser, Group


# Create your tests here.
class UnsignedUserAccessCase(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_signup(self):
        response = self.client.get('/signup/')
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)

    def test_home(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_authorized_url(self):
        response = self.client.get('/current/', follow=True)
        self.assertTrue(response.redirect_chain)
        self.assertEqual(response.status_code, 200)


class UserAuthorizationCase(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_not_matching_passwords_signup(self):
        response = self.client.post(
            '/signup/',
            {'username': 'Vasek', 'password1': '1234', 'password2': '12345'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Passwords didn't match", html=True)

    def test_plain_signup(self):
        response = self.client.post(
            '/signup/',
            {'username': 'Vasek', 'password1': '1234', 'password2': '1234'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/current/')

    def test_taken_name_signup(self):
        self.client.post(
            '/signup/',
            {'username': 'Vasek', 'password1': '1234', 'password2': '1234'}
        )
        self.client.post('/logout/')
        response = self.client.post(
            '/signup/',
            {'username': 'Vasek', 'password1': '12345', 'password2': '12345'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This username is already taken")

    def test_login_with_not_existing_user(self):
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            '/login/',
            {'username': 'Vasek', 'password': '12345'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Username and/or password didn't match", html=True)

    def test_plain_login(self):
        self.client.post(
            '/signup/',
            {'username': 'Vasek', 'password1': '1234', 'password2': '1234'}
        )
        self.client.post('/logout/')
        response = self.client.post(
            '/login/',
            {'username': 'Vasek', 'password': '1234'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/current/')


class ModelTestsCase(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(**{'username': 'Vasek', 'password': '1234'})

    def test_todo_creation(self):
        Todo.objects.create(**{
            'title': 'Купить', 'description': 'Купить котлеты',
            'importance': True, 'user': self.user
        })

        self.assertIsInstance(Todo.objects.get(user=self.user), Todo)
        Todo.objects.get(user=self.user).delete()

    def test_group_creation(self):
        group = Group.objects.create(name='testgroup')
        GroupUser.objects.create(user=self.user, group=group, status='C')
        group.save()
        self.assertEqual(len(group.users.all()), 1)


class CreateActionsCase(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.client.post(
            '/signup/',
            {'username': 'Vasek', 'password1': '1234', 'password2': '1234'},
        )

    def test_create_todo(self):
        response = self.client.post(
            '/create/',
            {'title': 'Test TODO', 'description': 'TODODODO', 'importance': False},
            follow=True
        )
        self.assertRedirects(response, '/current/')
        self.assertTrue(Todo.objects.get(title='Test TODO'))

    def test_create_group(self):
        response = self.client.post(
            '/groups/create/',
            {'name': 'TestGroup'},
            follow=True
        )
        self.assertRedirects(response, '/groups/')
        self.assertContains(response, 'TestGroup')


class TodoActionsCase(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.client.post(
            '/signup/',
            {'username': 'Test', 'password1': '1234', 'password2': '1234'},
        )
        self.client.post('/logout')
        self.client.post(
            '/signup/',
            {'username': 'Vasek', 'password1': '1234', 'password2': '1234'},
        )
        self.client.post(
            '/groups/create/',
            {'name': 'TestGroup'},
            follow=True
        )
        self.client.post(
            '/create/',
            {'title': 'Test TODO', 'description': 'TODODODO', 'importance': False},
            follow=True
        )
        self.todo = Todo.objects.get(title='Test TODO')

    def test_edit_todo(self):
        response = self.client.post(
            f'/todo/{self.todo.pk}/edit/',
            {'description': 'actually do this', 'importance': 'on', 'group': '', 'title': self.todo.title},
            follow=True
        )
        self.assertRedirects(response, '/current/')
        self.assertContains(response, 'actually do this')

    def test_view_todo(self):
        response = self.client.get(f'/todo/{self.todo.pk}/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.todo.title)

    def test_complete_todo(self):
        response_completion = self.client.post(f'/todo/{self.todo.pk}/complete/', follow=True)
        self.assertRedirects(response_completion, '/current/')

        response_completed = self.client.get('/completed/')
        self.assertEqual(response_completed.status_code, 200)
        self.assertContains(response_completed, 'Test TODO')

    def test_delete_todo(self):
        response = self.client.post(f'/todo/{self.todo.pk}/delete/', follow=True)
        self.assertRedirects(response, '/current/')
        response_completed = self.client.get('/completed/')
        self.assertNotContains(response_completed, 'Test TODO')


class GroupActionsCase(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.client.post(
            '/signup/',
            {'username': 'Test', 'password1': '1234', 'password2': '1234'},
        )
        self.client.post('/logout')
        self.client.post(
            '/signup/',
            {'username': 'Vasek', 'password1': '1234', 'password2': '1234'},
        )
        self.client.post(
            '/groups/create/',
            {'name': 'TestGroup'},
            follow=True
        )
        self.group = Group.objects.get(name='TestGroup')

    def test_invitation(self):
        response_invitation = self.client.post(
            f'/groups/{self.group.pk}/',
            {'username': 'Test'},
            follow=True
        )
        self.assertEqual(response_invitation.status_code, 200)
        self.assertContains(response_invitation, 'Invitation has been sent')

        self.client.post('/logout/')
        self.client.post(
            '/login/',
            {'username': 'Test', 'password': '1234'},
            follow=True
        )
        response_acceptance = self.client.post(
            '/groups/accept/',
            {'group': self.group.name, 'next': '/groups/'},
            follow=True
        )
        self.assertRedirects(response_acceptance, '/groups/')
        self.assertContains(response_acceptance, 'TestGroup')










