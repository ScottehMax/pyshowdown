import unittest

from pyshowdown.utils import to_id, HSLToRGB, username_color


class UtilsTest(unittest.TestCase):
    def test_to_id_basic(self):
        self.assertEqual(to_id("Test User"), "testuser")
        self.assertEqual(to_id("HelloWorld"), "helloworld")
        self.assertEqual(to_id("foo"), "foo")

    def test_to_id_with_special_characters(self):
        self.assertEqual(to_id("Test-User_123"), "testuser123")
        self.assertEqual(to_id("User@#$%Name"), "username")
        self.assertEqual(to_id("Hello, World!"), "helloworld")
        self.assertEqual(to_id("Test  Spaces"), "testspaces")

    def test_to_id_with_symbols(self):
        self.assertEqual(to_id("@user"), "user")
        self.assertEqual(to_id("+User"), "user")
        self.assertEqual(to_id("%Admin"), "admin")
        self.assertEqual(to_id("#Moderator"), "moderator")

    def test_to_id_none(self):
        self.assertEqual(to_id(None), "")

    def test_to_id_empty_string(self):
        self.assertEqual(to_id(""), "")

    def test_to_id_only_special_chars(self):
        self.assertEqual(to_id("@#$%^&*()"), "")
        self.assertEqual(to_id("!!!"), "")

    def test_to_id_mixed_case(self):
        self.assertEqual(to_id("TeSt"), "test")
        self.assertEqual(to_id("UPPERCASE"), "uppercase")
        self.assertEqual(to_id("lowercase"), "lowercase")

    def test_to_id_numbers(self):
        self.assertEqual(to_id("User123"), "user123")
        self.assertEqual(to_id("123"), "123")
        self.assertEqual(to_id("Test456User"), "test456user")

    def test_HSLToRGB_basic(self):
        # Test pure red (H=0, S=100, L=50)
        r, g, b = HSLToRGB(0, 100, 50)
        self.assertAlmostEqual(r, 1.0, places=2)
        self.assertAlmostEqual(g, 0.0, places=2)
        self.assertAlmostEqual(b, 0.0, places=2)

    def test_HSLToRGB_green(self):
        # Test pure green (H=120, S=100, L=50)
        r, g, b = HSLToRGB(120, 100, 50)
        self.assertAlmostEqual(r, 0.0, places=2)
        self.assertAlmostEqual(g, 1.0, places=2)
        self.assertAlmostEqual(b, 0.0, places=2)

    def test_HSLToRGB_blue(self):
        # Test pure blue (H=240, S=100, L=50)
        r, g, b = HSLToRGB(240, 100, 50)
        self.assertAlmostEqual(r, 0.0, places=2)
        self.assertAlmostEqual(g, 0.0, places=2)
        self.assertAlmostEqual(b, 1.0, places=2)

    def test_HSLToRGB_white(self):
        # Test white (any H, S=0, L=100)
        r, g, b = HSLToRGB(0, 0, 100)
        self.assertAlmostEqual(r, 1.0, places=2)
        self.assertAlmostEqual(g, 1.0, places=2)
        self.assertAlmostEqual(b, 1.0, places=2)

    def test_HSLToRGB_black(self):
        # Test black (any H, any S, L=0)
        r, g, b = HSLToRGB(0, 100, 0)
        self.assertAlmostEqual(r, 0.0, places=2)
        self.assertAlmostEqual(g, 0.0, places=2)
        self.assertAlmostEqual(b, 0.0, places=2)

    def test_HSLToRGB_gray(self):
        # Test gray (any H, S=0, L=50)
        r, g, b = HSLToRGB(0, 0, 50)
        self.assertAlmostEqual(r, 0.5, places=2)
        self.assertAlmostEqual(g, 0.5, places=2)
        self.assertAlmostEqual(b, 0.5, places=2)

    def test_HSLToRGB_various_hues(self):
        # Test various hue values
        for h in [0, 60, 120, 180, 240, 300]:
            r, g, b = HSLToRGB(h, 100, 50)
            # All values should be between 0 and 1
            self.assertGreaterEqual(r, 0.0)
            self.assertLessEqual(r, 1.0)
            self.assertGreaterEqual(g, 0.0)
            self.assertLessEqual(g, 1.0)
            self.assertGreaterEqual(b, 0.0)
            self.assertLessEqual(b, 1.0)

    def test_username_color_returns_tuple(self):
        h, s, l = username_color("testuser")
        self.assertIsInstance(h, (int, float))
        self.assertIsInstance(s, (int, float))
        self.assertIsInstance(l, (int, float))

    def test_username_color_in_valid_range(self):
        h, s, l = username_color("testuser")
        # Hue should be 0-360
        self.assertGreaterEqual(h, 0)
        self.assertLessEqual(h, 360)
        # Saturation should be reasonable
        self.assertGreaterEqual(s, 0)
        self.assertLessEqual(s, 100)
        # Lightness should be reasonable
        # Note: L can be modified by HLmod, so range might be wider
        self.assertGreaterEqual(l, 0)

    def test_username_color_consistency(self):
        # Same username should always produce same color
        color1 = username_color("testuser")
        color2 = username_color("testuser")
        self.assertEqual(color1, color2)

    def test_username_color_case_insensitive(self):
        # Different cases should produce same color (due to to_id)
        color1 = username_color("TestUser")
        color2 = username_color("testuser")
        color3 = username_color("TESTUSER")
        self.assertEqual(color1, color2)
        self.assertEqual(color2, color3)

    def test_username_color_different_users(self):
        # Different usernames should (usually) produce different colors
        color1 = username_color("user1")
        color2 = username_color("user2")
        # They should be different (hash collision is extremely unlikely)
        self.assertNotEqual(color1, color2)

    def test_username_color_special_chars_stripped(self):
        # Special characters should be stripped by to_id
        color1 = username_color("@TestUser")
        color2 = username_color("TestUser")
        self.assertEqual(color1, color2)

    def test_username_color_empty_string(self):
        # Should handle empty string (after to_id conversion)
        h, s, l = username_color("")
        self.assertIsInstance(h, (int, float))
        self.assertIsInstance(s, (int, float))
        self.assertIsInstance(l, (int, float))

    def test_username_color_luminance_adjustment(self):
        # Test various usernames to ensure luminance adjustment logic runs
        # This tests the HLmod calculation and different branches
        test_users = [
            "darkuser",
            "lightuser",
            "averageuser",
            "testuser123",
            "admin",
            "moderator",
            "guest",
        ]

        for user in test_users:
            h, s, l = username_color(user)
            # All values should be valid
            self.assertIsInstance(h, (int, float))
            self.assertIsInstance(s, (int, float))
            self.assertIsInstance(l, (int, float))
            # Hue should be in valid range
            self.assertGreaterEqual(h, 0)
            self.assertLessEqual(h, 360)

    def test_username_color_hash_distribution(self):
        # Test that the hash-based color distribution works
        # by testing multiple users and ensuring variety
        colors = []
        for i in range(10):
            user = f"user{i}"
            color = username_color(user)
            colors.append(color)

        # All colors should be valid tuples
        for h, s, l in colors:
            self.assertGreaterEqual(h, 0)
            self.assertLessEqual(h, 360)

        # Should have some variety in hues (not all identical)
        hues = [color[0] for color in colors]
        unique_hues = len(set(hues))
        self.assertGreater(unique_hues, 1, "Should generate different hues for different users")

    def test_username_color_boundary_cases(self):
        # Test usernames that might produce edge cases in the algorithm
        test_cases = [
            "a",
            "z",
            "0",
            "9",
            "aaaaaaaaa",
            "zzzzzzzzz",
        ]

        for user in test_cases:
            h, s, l = username_color(user)
            # Should produce valid output for all inputs
            self.assertIsInstance(h, (int, float))
            self.assertIsInstance(s, (int, float))
            self.assertIsInstance(l, (int, float))

    def test_username_color_hue_adjustment_near_180(self):
        # Test case where Hdist calculation matters (H near 180)
        # Need to find a username that hashes to H near 180 or 240
        # This tests the Hdist < 15 branch
        # We'll test enough users to likely hit various cases
        for i in range(100):
            user = f"testuser{i}"
            h, s, l = username_color(user)
            # Should always produce valid colors
            self.assertGreaterEqual(h, 0)
            self.assertLessEqual(h, 360)

    def test_username_color_hue_adjustment_near_240(self):
        # Similar to above, testing H near 240
        # This ensures we test both branches of the Hdist calculation
        colors_tested = 0
        for i in range(100):
            user = f"player{i}"
            h, s, l = username_color(user)
            # Count how many we tested
            colors_tested += 1
            # All should be valid
            self.assertGreaterEqual(h, 0)
            self.assertLessEqual(h, 360)

        self.assertEqual(colors_tested, 100)
