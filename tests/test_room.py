import unittest

from pyshowdown import room


class RoomTest(unittest.TestCase):
    def test_init_room(self):
        r = room.Room("test")
        self.assertEqual(r.id, "test")
        self.assertEqual(r.users, {})
        self.assertEqual(r.is_battle, False)
        self.assertRaises(AttributeError, lambda: r.is_private_battle)
        self.assertRaises(AttributeError, lambda: r.password)

    def test_init_battle_room(self):
        r = room.Room("battle-test-12345")
        self.assertEqual(r.id, "battle-test-12345")
        self.assertEqual(r.users, {})
        self.assertEqual(r.is_battle, True)
        self.assertEqual(r.is_private_battle, False)
        self.assertRaises(AttributeError, lambda: r.password)

    def test_init_private_battle_room(self):
        r = room.Room("battle-test-12345-password")
        self.assertEqual(r.id, "battle-test-12345")
        self.assertEqual(r.users, {})
        self.assertEqual(r.is_battle, True)
        self.assertEqual(r.is_private_battle, True)
        self.assertEqual(r.password, "password")
