import unittest


from pyshowdown.user import User


class UserTest(unittest.TestCase):
    def test_user(self):
        user = User("TeSt", "@", "", True)

        self.assertEqual(user.name, "TeSt")
        self.assertEqual(user.id, "test")
        self.assertEqual(user.rank, "@")
        self.assertEqual(user.fullname, "@TeSt")
        self.assertEqual(user.away, True)
        self.assertEqual(user.to_string(), "@TeSt@!")

        user2 = User("test", "@", "", False)

        self.assertEqual(user2.to_string(), "@test")

    def test_sorting(self):
        users = [
            User("alpha", "@", "", True),
            User("bravo", "@", "", False),
            User("charlie", "%", "", True),
            User("delta", "%", "", False),
            User("echo", "+", "", True),
            User("foxtrot", "+", "", False),
            User("golf", " ", "", True),
            User("hotel", " ", "", False),
            User("india", "~", "", True),
            User("juliet", "~", "", False),
            User("kilo", "#", "", True),
            User("lima", "#", "", False),
            User("mike", "&", "", True),
            User("november", "&", "", False),
            User("oscar", "!", "", True),
            User("papa", "!", "", False),
            User("quebec", "‽", "", True),
            User("romeo", "‽", "", False),
        ]

        sorted_users = sorted(users)

        self.assertListEqual(
            [user.name for user in sorted_users],
            [
                "juliet",
                "india",
                "lima",
                "kilo",
                "november",
                "mike",
                "bravo",
                "alpha",
                "delta",
                "charlie",
                "foxtrot",
                "echo",
                "hotel",
                "golf",
                "papa",
                "oscar",
                "romeo",
                "quebec",
            ],
        )
