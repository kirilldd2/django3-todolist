from typing import List, Optional
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.remote.webelement import WebElement
from todo_app.models import Todo, GroupUser, Group, User
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from unittest import skip


def find_todo_item_by_text(blocks: List[WebElement], text) -> Optional[WebElement]:
    for block in blocks:
        items = block.find_elements_by_css_selector('a.list-group-item')
        for item in items:
            if item.find_element_by_tag_name('h5').text == text:
                return item
    else:
        return None


class SeleniumTests(StaticLiveServerTestCase):
    browser = None

    @classmethod
    def setUpClass(cls):
        """
        Setting selenium up
        """
        super().setUpClass()
        options = webdriver.ChromeOptions()
        binary_yandex_driver_file = 'yandexdriver.exe'
        cls.browser = webdriver.Chrome(binary_yandex_driver_file, options=options)
        cls.browser.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def setUp(self) -> None:
        """
        Filling database
        """
        user1 = User.objects.create_user(username='user1', password='12341')
        user2 = User.objects.create_user(username='user2', password='12342')
        user3 = User.objects.create_user(username='user3', password='12343')

        group1 = Group.objects.create(name='group1')
        group3 = Group.objects.create(name='group3')

        GroupUser.objects.create(group=group1, user=user1, status='C')
        GroupUser.objects.create(group=group1, user=user2, status='M')

        GroupUser.objects.create(group=group3, user=user3, status='C')
        GroupUser.objects.create(group=group3, user=user2, status='I')

        Todo.objects.create(title='test1', description='test 1 todo', importance=False, user=user1)
        Todo.objects.create(title='test2', description='test 2 todo', importance=True, user=user2, group=group1)
        Todo.objects.create(title='test3', description='test 3 todo', importance=True, user=user3, group=group3)
        Todo.objects.create(title='test31', description='test 3.1 todo', importance=True, user=user3)

    def test_create(self):
        """
        Creating a todo_ item
        """
        user = 'user1'
        group = 'group1'
        self.browser.get(f'{self.live_server_url}{"/login/"}')
        username_input = self.browser.find_element_by_name("username")
        username_input.send_keys(user)
        password_input = self.browser.find_element_by_name("password")
        password_input.send_keys('12341')
        self.browser.save_screenshot('test_screenshots/test_create/1.png')
        self.browser.find_element_by_xpath('/html/body/form/button').click()
        self.browser.find_element_by_xpath('/html/body/nav/div/ul[1]/li[3]/a').click()
        self.browser.save_screenshot('test_screenshots/test_create/2.png')
        self.browser.find_element_by_xpath("//input[@name='title']").send_keys('selenium todo')
        self.browser.find_element_by_xpath("//textarea[@name='description']").send_keys('some gibberish')
        self.browser.find_element_by_xpath("//input[@name='importance']").click()
        Select(self.browser.find_element_by_xpath("//select[@name='group']")).select_by_visible_text(group)
        self.browser.save_screenshot('test_screenshots/test_create/3.png')
        self.browser.find_element_by_xpath("/html/body/form/button").click()
        self.browser.save_screenshot('test_screenshots/test_create/4.png')
        blocks = self.browser.find_elements_by_css_selector('ul > div.list-group')
        self.assertTrue(find_todo_item_by_text(blocks, 'selenium todo'))
        todo = Todo.objects.get(title='selenium todo')
        self.assertEqual(todo.title, 'selenium todo')
        self.assertEqual(todo.description, 'some gibberish')
        self.assertTrue(todo.importance)
        self.assertEqual(todo.group.name, 'group1')

    def test_accept(self):
        """
        Accepting invitation, then trying to delete
        group todo_ without permission to do so
        """
        user = 'user2'
        group = 'group3'
        self.browser.get(f'{self.live_server_url}{"/login/"}')
        username_input = self.browser.find_element_by_name("username")
        username_input.send_keys(user)
        password_input = self.browser.find_element_by_name("password")
        password_input.send_keys('12342')
        self.browser.save_screenshot('test_screenshots/test_accept/1.png')
        self.browser.find_element_by_xpath('/html/body/form/button').click()
        self.browser.save_screenshot('test_screenshots/test_accept/2.png')
        self.browser.find_element_by_xpath('//div[@class="dropdown"]/button[@id="dropdownMenuButton"]').click()
        self.browser.save_screenshot('test_screenshots/test_accept/3.png')
        self.browser.find_element_by_xpath('//div[@class="dropdown-item"]/form/input[@type="submit"]').click()
        self.browser.save_screenshot('test_screenshots/test_accept/4.png')
        self.assertEqual(1, len(GroupUser.objects.filter(group__name=group, user__username=user)))
        blocks = self.browser.find_elements_by_css_selector('ul > div.list-group')
        find_todo_item_by_text(blocks, 'test3').click()
        self.browser.save_screenshot('test_screenshots/test_accept/5.png')
        self.browser.find_element_by_link_text('Edit').click()
        self.browser.save_screenshot('test_screenshots/test_accept/6.png')
        self.browser.find_element_by_xpath('//form[3]/button').click()
        self.browser.save_screenshot('test_screenshots/test_accept/6.png')
        # this is correct, user doesnt have permission
        self.assertEqual(1, len(Todo.objects.filter(title='test3')))
        self.browser.get(f'{self.live_server_url}{"/current/"}')
        self.browser.save_screenshot('test_screenshots/test_accept/7.png')
        blocks = self.browser.find_elements_by_css_selector('ul > div.list-group')
        self.assertTrue(find_todo_item_by_text(blocks, 'test3'))

    def test_delete(self):
        """
        Deleting todo_
        """
        user = 'user3'
        group = 'group3'
        self.browser.get(f'{self.live_server_url}{"/login/"}')
        username_input = self.browser.find_element_by_name("username")
        username_input.send_keys(user)
        password_input = self.browser.find_element_by_name("password")
        password_input.send_keys('12343')
        self.browser.save_screenshot('test_screenshots/test_delete/1.png')
        self.browser.find_element_by_xpath('/html/body/form/button').click()
        self.browser.save_screenshot('test_screenshots/test_delete/2.png')
        blocks = self.browser.find_elements_by_css_selector('ul > div.list-group')
        find_todo_item_by_text(blocks, 'test3').click()
        self.browser.save_screenshot('test_screenshots/test_delete/3.png')
        self.browser.find_element_by_link_text('Edit').click()
        self.browser.save_screenshot('test_screenshots/test_delete/4.png')
        self.browser.find_element_by_xpath('//form[3]/button').click()
        self.browser.save_screenshot('test_screenshots/test_delete/5.png')
        blocks = self.browser.find_elements_by_css_selector('ul > div.list-group')
        self.assertFalse(find_todo_item_by_text(blocks, 'test3'))
        self.assertEqual(0, len(Todo.objects.filter(title='test3')))

    def test_complete(self):
        """
        Completing todo_
        """
        user = 'user3'
        group = 'group3'
        self.browser.get(f'{self.live_server_url}{"/login/"}')
        username_input = self.browser.find_element_by_name('username')
        username_input.send_keys(user)
        password_input = self.browser.find_element_by_name('password')
        password_input.send_keys('12343')
        self.browser.save_screenshot('test_screenshots/test_complete/1.png')
        self.browser.find_element_by_xpath('/html/body/form/button').click()
        self.browser.save_screenshot('test_screenshots/test_complete/2.png')
        blocks = self.browser.find_elements_by_css_selector('ul > div.list-group')
        find_todo_item_by_text(blocks, 'test31').click()
        self.browser.save_screenshot('test_screenshots/test_complete/3.png')
        self.browser.find_element_by_link_text('Edit').click()
        self.browser.save_screenshot('test_screenshots/test_complete/4.png')
        self.browser.find_element_by_xpath('//form[2]/button').click()
        self.browser.save_screenshot('test_screenshots/test_complete/5.png')
        blocks = self.browser.find_elements_by_css_selector('ul > div.list-group')
        self.assertFalse(find_todo_item_by_text(blocks, 'test31'))
        self.assertEqual(1, len(Todo.objects.filter(title='test31')))
        self.assertIsNotNone(Todo.objects.get(title='test31').completion_time)
        self.browser.find_element_by_xpath('/html/body/nav/div/ul[1]/li[2]/a').click()
        self.browser.save_screenshot('test_screenshots/test_complete/6.png')
        self.assertTrue(self.browser.find_element_by_link_text('test31'))

    def test_group(self):
        """
        Creating a group, inviting user
        """
        user = 'user2'
        group = 'group2'
        self.browser.get(f'{self.live_server_url}{"/login/"}')
        username_input = self.browser.find_element_by_name("username")
        username_input.send_keys(user)
        password_input = self.browser.find_element_by_name("password")
        password_input.send_keys('12342')
        self.browser.save_screenshot('test_screenshots/test_group/1.png')
        self.browser.find_element_by_xpath('/html/body/form/button').click()
        self.browser.save_screenshot('test_screenshots/test_group/2.png')
        self.browser.find_element_by_partial_link_text('GROUP').click()
        self.browser.save_screenshot('test_screenshots/test_group/3.png')
        self.browser.find_element_by_link_text('Create group').click()
        self.browser.find_element_by_xpath("//input[@id='id_name']").send_keys(group)
        self.browser.save_screenshot('test_screenshots/test_group/4.png')
        self.browser.find_element_by_xpath('/html/body/form/button').click()
        self.browser.save_screenshot('test_screenshots/test_group/5.png')
        self.assertTrue(Group.objects.filter(name=group))
        self.assertTrue(GroupUser.objects.filter(group__name=group, user__username=user))
        self.assertEqual(GroupUser.objects.get(group__name=group, user__username=user).status, 'C')

        self.browser.find_element_by_link_text(group).click()
        self.browser.find_element_by_xpath("//input[@id='id_username']").send_keys('user1')
        self.browser.save_screenshot('test_screenshots/test_group/6.png')
        self.browser.find_element_by_xpath('/html/body/form[1]/button').click()
        self.assertTrue(GroupUser.objects.filter(group__name=group, user__username='user1'))
        self.assertEqual(GroupUser.objects.get(group__name=group, user__username='user1').status, 'I')

        self.browser.save_screenshot('test_screenshots/test_group/7.png')
        self.browser.find_element_by_xpath('/html/body/nav/div/ul[2]/li/form/button').click()
        self.browser.save_screenshot('test_screenshots/test_group/8.png')
        self.browser.find_element_by_link_text('Log in').click()
        user = 'user1'
        username_input = self.browser.find_element_by_name("username")
        username_input.send_keys(user)
        password_input = self.browser.find_element_by_name("password")
        password_input.send_keys('12341')
        self.browser.save_screenshot('test_screenshots/test_group/9.png')
        self.browser.find_element_by_xpath('/html/body/form/button').click()
        self.browser.save_screenshot('test_screenshots/test_group/10.png')
        self.browser.find_element_by_xpath('//div[@class="dropdown"]/button[@id="dropdownMenuButton"]').click()
        self.browser.save_screenshot('test_screenshots/test_group/11.png')
        self.browser.find_element_by_xpath('//div[@class="dropdown-item"]/form/input[@type="submit"]').click()
        self.browser.save_screenshot('test_screenshots/test_group/12.png')
        self.browser.find_element_by_partial_link_text('GROUP').click()
        self.browser.save_screenshot('test_screenshots/test_group/13.png')
        self.assertEqual(GroupUser.objects.get(group__name=group, user__username='user1').status, 'M')
        self.assertTrue(self.browser.find_element_by_link_text(group))














