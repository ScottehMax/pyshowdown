import random
import unittest

from pyshowdown import message
from pyshowdown.user import User


class MessageTest(unittest.TestCase):
    def test_init(self):
        m = message.parse_message("techcode", "|init|chat")

        assert isinstance(m, message.InitMessage)
        self.assertEqual(m.roomtype, "chat")
        self.assertEqual(m.room, "techcode")

    def test_title(self):
        m = message.parse_message("", "|title|Lobby")

        assert isinstance(m, message.TitleMessage)
        self.assertEqual(m.title, "Lobby")
        self.assertFalse(m.room)

    def test_users(self):
        m = message.parse_message("techcode", "|users|4,@foo@!,+bar@!,@baz@!,%quux")
        expected = {
            "foo": User(rank="@", name="foo", status="", away=True),
            "bar": User(rank="+", name="bar", status="", away=True),
            "baz": User(rank="@", name="baz", status="", away=True),
            "quux": User(rank="%", name="quux", status="", away=False),
        }

        assert isinstance(m, message.UsersMessage)
        self.assertEqual(m.usercount, 4)
        self.assertDictEqual(m.users, expected)
        self.assertEqual(m.room, "techcode")

    def test_html(self):
        m = message.parse_message("", "|html|<b>Hello!</b>")

        assert isinstance(m, message.HTMLMessage)
        self.assertEqual(m.html, "<b>Hello!</b>")

    def test_uhtml(self):
        m = message.parse_message("", "|uhtml|foo|<b>Hello!</b>")

        assert isinstance(m, message.UHTMLMessage)
        self.assertEqual(m.name, "foo")
        self.assertEqual(m.html, "<b>Hello!</b>")

    def test_uhtmlchange(self):
        m = message.parse_message("", "|uhtmlchange|foo|<b>Hello!</b>")

        assert isinstance(m, message.UHTMLChangeMessage)
        self.assertEqual(m.name, "foo")
        self.assertEqual(m.html, "<b>Hello!</b>")

    def test_join(self):
        m = message.parse_message("", "|j|@foo")

        assert isinstance(m, message.JoinMessage)
        self.assertIsNotNone(m.user)
        self.assertEqual(m.user.rank, "@")
        self.assertEqual(m.user.name, "foo")

    def test_leave(self):
        m = message.parse_message("", "|l|@foo")

        assert isinstance(m, message.LeaveMessage)
        self.assertEqual(m.user.rank, "@")
        self.assertEqual(m.user.name, "foo")

    def test_name(self):
        m = message.parse_message("", "|name|@bar|foo")

        assert isinstance(m, message.RenameMessage)
        self.assertEqual(m.user.name, "bar")
        self.assertEqual(m.oldid, "foo")

        m2 = message.parse_message("", "|N|#Bar@!|foo")
        assert isinstance(m2, message.RenameMessage)
        self.assertEqual(m2.user.name, "Bar")
        self.assertEqual(m2.oldid, "foo")
        self.assertEqual(m2.user.rank, "#")
        self.assertTrue(m2.user.away)

    def test_chat(self):
        m = message.parse_message("lobby", "|c|@foo|hello!")

        assert isinstance(m, message.ChatMessage)
        self.assertIsNone(m.timestamp)
        self.assertEqual(m.room, "lobby")
        self.assertEqual(m.user.name, "foo")
        self.assertEqual(m.user.rank, "@")
        self.assertEqual(m.message, "hello!")

    def test_timestamp(self):
        m = message.parse_message("lobby", "|:|1636113111")

        assert isinstance(m, message.TimestampMessage)
        self.assertEqual(m.timestamp, 1636113111)

    def test_timestamp_chat(self):
        m = message.parse_message("lobby", "|c:|1636113111|@foo|hello!")

        assert isinstance(m, message.ChatMessage)
        self.assertEqual(m.timestamp, 1636113111)
        self.assertEqual(m.room, "lobby")
        self.assertEqual(m.user.name, "foo")
        self.assertEqual(m.user.rank, "@")
        self.assertEqual(m.message, "hello!")

    def test_battle(self):
        m = message.parse_message("lobby", "|battle|battleid|foo|bar")

        assert isinstance(m, message.BattleMessage)
        self.assertEqual(m.roomid, "battleid")
        self.assertEqual(m.user1, "foo")
        self.assertEqual(m.user2, "bar")

    def test_popup(self):
        m = message.parse_message("", "|popup|Hello!")

        assert isinstance(m, message.PopupMessage)
        self.assertEqual(m.message, "Hello!")

    def test_pm(self):
        m = message.parse_message("", "|pm|@foo|@bar|Hello!")

        assert isinstance(m, message.PMMessage)
        self.assertEqual(m.user.name, "foo")
        self.assertEqual(m.user.rank, "@")
        self.assertEqual(m.receiver.name, "bar")
        self.assertEqual(m.receiver.rank, "@")
        self.assertEqual(m.message, "Hello!")

    def test_usercount(self):
        m = message.parse_message("", "|usercount|1")

        assert isinstance(m, message.UserCountMessage)
        self.assertEqual(m.usercount, 1)

    def test_nametaken(self):
        m = message.parse_message("", "|nametaken|@foo|sorry")

        assert isinstance(m, message.NameTakenMessage)
        self.assertEqual(m.user.name, "foo")
        self.assertEqual(m.user.rank, "@")
        self.assertEqual(m.message, "sorry")

    def test_challstr(self):
        m = message.parse_message(
            "",
            "|challstr|4|a6ad910c2eda1e23530b1d794bd245e416c3ed14baee99db044b8a952ffcc9962961f32197300e974f5b3aae83c3f7a3a3a8ad5e9024677729239a1f3ad113dfde3de087ac318e3b7f51d81c3b18f147643fe16043f25e6e605d6d2532b2db4e9d20aba05dd82c7f5edded8e0c941a83c6db23aa0e66fd86b4ccc6d980d0c064",
        )

        assert isinstance(m, message.ChallstrMessage)
        self.assertEqual(
            m.challstr,
            "4|a6ad910c2eda1e23530b1d794bd245e416c3ed14baee99db044b8a952ffcc9962961f32197300e974f5b3aae83c3f7a3a3a8ad5e9024677729239a1f3ad113dfde3de087ac318e3b7f51d81c3b18f147643fe16043f25e6e605d6d2532b2db4e9d20aba05dd82c7f5edded8e0c941a83c6db23aa0e66fd86b4ccc6d980d0c064",
        )

    def test_updateuser(self):
        m = message.parse_message(
            "",
            '|updateuser|@foo|1|winona|{"blockChallenges":false,"blockPMs":false,"ignoreTickets":false,"hideBattlesFromTrainerCard":false,"blockInvites":false,"doNotDisturb":false,"blockFriendRequests":false,"allowFriendNotifications":false,"displayBattlesToFriends":false,"hideLogins":false,"hiddenNextBattle":false,"inviteOnlyNextBattle":false,"language":null}',
        )

        assert isinstance(m, message.UpdateUserMessage)
        self.assertEqual(m.user.name, "foo")
        self.assertEqual(m.user.rank, "@")
        self.assertTrue(m.named)
        self.assertEqual(m.avatar, "winona")
        self.assertFalse(m.settings["blockChallenges"])
        self.assertFalse(m.settings["blockPMs"])
        self.assertFalse(m.settings["ignoreTickets"])
        self.assertFalse(m.settings["hideBattlesFromTrainerCard"])
        self.assertFalse(m.settings["blockInvites"])
        self.assertFalse(m.settings["doNotDisturb"])
        self.assertFalse(m.settings["blockFriendRequests"])
        self.assertFalse(m.settings["allowFriendNotifications"])
        self.assertFalse(m.settings["displayBattlesToFriends"])
        self.assertFalse(m.settings["hideLogins"])
        self.assertFalse(m.settings["hiddenNextBattle"])
        self.assertFalse(m.settings["inviteOnlyNextBattle"])
        self.assertIsNone(m.settings["language"])

    def test_formats(self):
        m = message.parse_message(
            "",
            "|formats|,1|Sw/Sh Singles|[Gen 8] Random Battle,f|[Gen 8] Unrated Random Battle,b|[Gen 8] Free-For-All Random Battle,7|[Gen 8] Multi Random Battle,5|[Gen 8] OU,e|[Gen 8] OU (Blitz),e|[Gen 8] Ubers,e|[Gen 8] UU,e|[Gen 8] RU,e|[Gen 8] NU,e|[Gen 8] PU,e|[Gen 8] LC,e|[Gen 8] Monotype,e|[Gen 8] 1v1,e|[Gen 8] Anything Goes,e|[Gen 8] ZU,e|[Gen 8] LC UU,c|[Gen 8] CAP,e|[Gen 8] CAP LC,c|[Gen 8] Battle Stadium Singles,1e|[Gen 8] Battle Stadium Singles Series 9,1c|[Gen 8] Gym Challenge,1e|[Gen 8] Custom Game,c|,1|Sw/Sh Doubles|[Gen 8] Random Doubles Battle,f|[Gen 8] Doubles OU,e|[Gen 8] Doubles Ubers,e|[Gen 8] Doubles UU,e|[Gen 8] Doubles LC,c|[Gen 8] VGC 2021 Series 11,1e|[Gen 8] VGC 2021 Series 9,1c|[Gen 8] VGC 2020,1c|[Gen 8] 2v2 Doubles,e|[Gen 8] Metronome Battle,e|[Gen 8] Doubles Custom Game,c|,1|National Dex|[Gen 8] National Dex,e|[Gen 8] National Dex UU,e|[Gen 8] National Dex Monotype,e|[Gen 8] National Dex AG,e|,1|Pet Mods|[Gen 8] Fusion Evolution UU,e|[Gen 6] NEXT OU,8|,2|OM of the Month|[Gen 8] Sketchmons,e|[Gen 8] AAA Doubles,e|,2|Other Metagames|[Gen 8] Balanced Hackmons,e|[Gen 8] Mix and Mega,e|[Gen 8] Almost Any Ability,e|[Gen 8] STABmons,e|[Gen 8] NFE,e|[Gen 8] Free-For-All,6|,2|Challengeable OMs|[Gen 8] Camomons,c|[Gen 8] Godly Gift,c|[Gen 8] Inheritance,c|[Gen 8] Multibility,c|[Gen 8] Nature Swap,c|[Gen 8] Pure Hackmons,c|[Gen 8] Shared Power,c|[Gen 8] The Loser's Game,c|[Gen 8] Trademarked,c|,2|Randomized Metas|[Gen 8] Monotype Random Battle,f|[Gen 8] Random Battle (No Dmax),f|[Gen 8] BSS Factory,1f|[Gen 8] Super Staff Bros 4,f|[Gen 8] Challenge Cup,d|[Gen 8] Challenge Cup 1v1,f|[Gen 8] Challenge Cup 2v2,d|[Gen 8] Hackmons Cup,f|[Gen 8] Doubles Hackmons Cup,d|[Gen 8] CAP 1v1,d|[Gen 7] Random Battle,f|[Gen 7] Random Doubles Battle,d|[Gen 7] Battle Factory,f|[Gen 7] Monotype Battle Factory,f|[Gen 7] BSS Factory,1d|[Gen 7] Hackmons Cup,d|[Gen 7 Let's Go] Random Battle,d|[Gen 6] Random Battle,f|[Gen 6] Battle Factory,d|[Gen 5] Random Battle,f|[Gen 4] Random Battle,f|[Gen 3] Random Battle,f|[Gen 2] Random Battle,f|[Gen 1] Random Battle,f|[Gen 1] Challenge Cup,d|[Gen 1] Hackmons Cup,d|,3|RoA Spotlight|[Gen 6] Ubers,e|[Gen 4] UU,e|[Gen 3] Doubles OU,e|,3|Past Gens OU|[Gen 7] OU,e|[Gen 6] OU,e|[Gen 5] OU,e|[Gen 4] OU,e|[Gen 3] OU,e|[Gen 2] OU,e|[Gen 1] OU,e|,3|Retro Other Metagames|[Gen 7] Balanced Hackmons,e|[Gen 7] Mix and Mega,e|[Gen 7] STABmons,c|[Gen 6] Almost Any Ability,c|[Gen 6] Pure Hackmons,e|,3|US/UM Singles|[Gen 7] Ubers,e|[Gen 7] UU,c|[Gen 7] RU,c|[Gen 7] NU,c|[Gen 7] PU,c|[Gen 7] LC,c|[Gen 7] Monotype,c|[Gen 7] 1v1,c|[Gen 7] Anything Goes,e|[Gen 7] ZU,c|[Gen 7] CAP,c|[Gen 7] Battle Spot Singles,1c|[Gen 7 Let's Go] OU,1c|[Gen 7] Custom Game,c|,3|US/UM Doubles|[Gen 7] Doubles OU,e|[Gen 7] Doubles UU,c|[Gen 7] VGC 2019,1c|[Gen 7] VGC 2018,1c|[Gen 7] VGC 2017,1c|[Gen 7] Battle Spot Doubles,1c|[Gen 7] Doubles Custom Game,c|,4|OR/AS Singles|[Gen 6] UU,c|[Gen 6] RU,c|[Gen 6] NU,c|[Gen 6] PU,c|[Gen 6] LC,c|[Gen 6] Monotype,c|[Gen 6] 1v1,c|[Gen 6] Anything Goes,c|[Gen 6] CAP,c|[Gen 6] Battle Spot Singles,1c|[Gen 6] Custom Game,c|,4|OR/AS Doubles/Triples|[Gen 6] Doubles OU,c|[Gen 6] VGC 2016,1c|[Gen 6] VGC 2015,1c|[Gen 6] VGC 2014,1c|[Gen 6] Battle Spot Doubles,1c|[Gen 6] Doubles Custom Game,c|[Gen 6] Battle Spot Triples,1c|[Gen 6] Triples Custom Game,c|,4|B2/W2 Singles|[Gen 5] Ubers,c|[Gen 5] UU,c|[Gen 5] RU,c|[Gen 5] NU,c|[Gen 5] PU,c|[Gen 5] LC,c|[Gen 5] Monotype,c|[Gen 5] 1v1,c|[Gen 5] GBU Singles,1c|[Gen 5] Custom Game,c|,4|B2/W2 Doubles|[Gen 5] Doubles OU,c|[Gen 5] VGC 2013,1c|[Gen 5] VGC 2012,1c|[Gen 5] VGC 2011,1c|[Gen 5] Doubles Custom Game,c|[Gen 5] Triples Custom Game,c|,5|DPP Singles|[Gen 4] Ubers,c|[Gen 4] NU,c|[Gen 4] PU,c|[Gen 4] LC,c|[Gen 4] 1v1,c|[Gen 4] Anything Goes,c|[Gen 4] Custom Game,c|,5|DPP Doubles|[Gen 4] Doubles OU,c|[Gen 4] VGC 2010,1c|[Gen 4] VGC 2009,1c|[Gen 4] Doubles Custom Game,c|,5|Past Generations|[Gen 3] Ubers,c|[Gen 3] UU,c|[Gen 3] NU,c|[Gen 3] 1v1,c|[Gen 3] Custom Game,c|[Gen 3] Doubles Custom Game,c|[Gen 2] Ubers,c|[Gen 2] UU,c|[Gen 2] NU,c|[Gen 2] 1v1,c|[Gen 2] Nintendo Cup 2000,c|[Gen 2] Stadium OU,c|[Gen 2] Custom Game,c|[Gen 1] Ubers,c|[Gen 1] UU,c|[Gen 1] NU,c|[Gen 1] Japanese OU,c|[Gen 1] Nintendo Cup 1997,c|[Gen 1] Stadium OU,c|[Gen 1] Tradebacks OU,c|[Gen 1] Custom Game,c",
        )

        assert isinstance(m, message.FormatsMessage)
        self.assertListEqual(
            list(m.formats.keys()),
            [
                "Sw/Sh Singles",
                "Sw/Sh Doubles",
                "National Dex",
                "Pet Mods",
                "OM of the Month",
                "Other Metagames",
                "Challengeable OMs",
                "Randomized Metas",
                "RoA Spotlight",
                "Past Gens OU",
                "Retro Other Metagames",
                "US/UM Singles",
                "US/UM Doubles",
                "OR/AS Singles",
                "OR/AS Doubles/Triples",
                "B2/W2 Singles",
                "B2/W2 Doubles",
                "DPP Singles",
                "DPP Doubles",
                "Past Generations",
            ],
        )

        self.assertListEqual(
            list(m.formats["Past Generations"].keys()),
            [
                "[Gen 3] Ubers",
                "[Gen 3] UU",
                "[Gen 3] NU",
                "[Gen 3] 1v1",
                "[Gen 3] Custom Game",
                "[Gen 3] Doubles Custom Game",
                "[Gen 2] Ubers",
                "[Gen 2] UU",
                "[Gen 2] NU",
                "[Gen 2] 1v1",
                "[Gen 2] Nintendo Cup 2000",
                "[Gen 2] Stadium OU",
                "[Gen 2] Custom Game",
                "[Gen 1] Ubers",
                "[Gen 1] UU",
                "[Gen 1] NU",
                "[Gen 1] Japanese OU",
                "[Gen 1] Nintendo Cup 1997",
                "[Gen 1] Stadium OU",
                "[Gen 1] Tradebacks OU",
                "[Gen 1] Custom Game",
            ],
        )

        self.assertListEqual(
            m.formats["Past Gens OU"]["[Gen 3] OU"],
            [
                "Available for Search",
                "Available for Challenge",
                "Available for Tournaments",
            ],
        )

    def test_player(self):
        m = message.parse_message("battle-gen3ou-1234567890", "|player|p1|Foo|60|1200")

        assert isinstance(m, message.PlayerMessage)
        self.assertEqual(m.player, "p1")
        self.assertEqual(m.name, "Foo")
        self.assertEqual(m.avatar, "60")
        self.assertEqual(m.rating, 1200)
        self.assertEqual(m.room, "battle-gen3ou-1234567890")

        m = message.parse_message("battle-gen3ou-1234567890", "|player|p3|Bar|koga|")

        assert isinstance(m, message.PlayerMessage)
        self.assertEqual(m.player, "p3")
        self.assertEqual(m.name, "Bar")
        self.assertEqual(m.avatar, "koga")
        self.assertIsNone(m.rating)

        m = message.parse_message("battle-gen3ou-1234567890", "|player|p3|Bar|koga")

        assert isinstance(m, message.PlayerMessage)
        self.assertEqual(m.player, "p3")
        self.assertEqual(m.name, "Bar")
        self.assertEqual(m.avatar, "koga")
        self.assertIsNone(m.rating)

        m = message.parse_message("battle-gen3ou-1234567890", "|player|p2|")

        assert isinstance(m, message.PlayerMessage)
        self.assertEqual(m.player, "p2")
        self.assertFalse(m.name)
        self.assertIsNone(m.avatar)
        self.assertIsNone(m.rating)

    def test_noproto(self):
        m = message.parse_message(
            "battle-gen3ou-1234567890",
            "No Pokémon, item, move, ability or nature named 'healee' was found. Showing the data of 'Healer' instead.",
        )

        assert isinstance(m, message.Message)
        self.assertEqual(m.room, "battle-gen3ou-1234567890")
        self.assertEqual(
            m.message_str,
            "No Pokémon, item, move, ability or nature named 'healee' was found. Showing the data of 'Healer' instead.",
        )

    def test_fuzz_message(self):
        # Some of these will be invalid and end up being a generic Message.
        random_str = lambda: "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=20))
        message_types = [
            "init",
            "title",
            "html",
            "uhtml",
            "uhtmlchange",
            "j",
            "l",
            "name",
            "c",
            "battle",
            "popup",
            "pm",
            "nametaken",
        ]

        assumes_numbers = [
            "users",
            ":",
            "usercount",
            "challstr",
            "updateuser",
            # "formats", # This one is a bit more complicated
            "player",
        ]

        for i in range(100):
            base_msg = "|".join(
                [
                    "",
                    random.choice(message_types),
                    *[random_str() for _ in range(5)],
                ]
            )

            m = message.parse_message("", base_msg)

            assert isinstance(m, message.Message)

            base_msg = "|".join(
                [
                    "",
                    random.choice(message_types + assumes_numbers),
                    *[str(random.randint(1, 100)) for _ in range(5)],
                ]
            )

            m2 = message.parse_message("", base_msg)

            assert isinstance(m2, message.Message)

    def test_pagehtml(self):
        m = message.parse_message("", "|pagehtml|<b>Hello!</b>")

        assert isinstance(m, message.PageHTMLMessage)
        self.assertEqual(m.html, "<b>Hello!</b>")
