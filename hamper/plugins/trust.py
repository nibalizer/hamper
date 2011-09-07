import re

from zope.interface import implements, Interface, Attribute

from hamper.interfaces import Command, Plugin

class Trust(Plugin):
    name = 'trust'

    def setup(self, factory):
        self.users = {}

    class KnowCommand(Command):
        regex = '(?:do you )?know (.*?)\??$'

        def command(self, bot, comm, groups):
            user = groups[0]

            if user in self.plugin.users:
                bot.reply(comm, 'Yes, I know {0}'.format(user))
            else:
                bot.reply(comm, "No, I don't know {0}".format(user))

    class LearnCommand(Command):
        regex = 'learn (?:about )?(.*)$'

        def command(self, bot, comm, groups):
            user = groups[0]
            self.plugin.users[user] = User(user, bot)

    class TrustCommand(Command):
        regex = '(?:do you )?trust (.*?)\??$'

        def command(self, bot, comm, groups):
            user = groups[0]

            if user in self.plugin.users and self.plugin.users[user].trust:
                bot.reply(comm, 'Yes, I trust {0}'.format(user))
            else:
                bot.reply(comm, "No, I don't trust {0}".format(user))


class User(object):

    def __init__(self, name, bot):
        self.name = name
        self.bot = bot
        self.trust = None

        self.do_auth()

    def do_auth(self):
        """Ask chanserv for this user's asuth status."""
        print 'trying to do auth'
        d = self.bot.claim_next(user='NickServ')
        d.addCallback(self.parse_auth)
        self.bot.msg('NickServ', 'acc {0}'.format(self.name))

    def parse_auth(self, comm):
        """Called from a deffered."""
        print 'Got callback'
        user, status = re.match('([^ ]*) ACC (\d)', comm['message']).groups()
        self.trust = (user == self.name and status == '3')
        print self.trust, user, status

trust = Trust()
