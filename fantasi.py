import json

class Character:
    def __init__(self, message=None, author=None, channel=None, content=None):
        if message:
            author = User(user=message.author)
            channel = Channel(channel=message.channel)
            content = message.content

        assert author and channel and content, 'Author, Channel, or content not set'

        self.author = author
        self.channel = channel
        self.content = content

        self.gold = 10
        self.level = 1

    def __repr__(self):
        return json.dumps(self.to_dict())

    def __str__(self):
        return f'{self.author.name}#{self.author.discriminator} | Level: {self.level} | Gold: {self.gold}'
    
    def to_dict(self):
        return {
            'author': self.author.to_dict(),
            'channel': self.channel.to_dict(),
            'content': self.content
        }
    
    @staticmethod
    def from_dict(source):
        author = User.from_dict(source['author'])
        channel = Channel.from_dict(source['channel'])
        content = source['content']
        return Character(author=author, channel=channel, content=content)

class User:
    def __init__(self, user=None, id=None, name=None, discriminator=None):
        if user:
            id = user.id
            name = user.name
            discriminator = user.discriminator

        assert id and name and discriminator, 'Id, name, or discriminator not set'

        self.id = id
        self.name = name
        self.discriminator = discriminator

    def __repr__(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'discriminator': self.discriminator,
        }

    @staticmethod
    def from_dict(source):
        return User(id=source['id'], name=source['name'], discriminator=source['discriminator'])

class Channel:
    def __init__(self, channel=None, id=None, name=None):
        if channel:
            id = channel.id
            name = channel.name

        assert id and name, 'Id or name not set'

        self.id = id
        self.name = name
        

    def __repr__(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
        }

    @staticmethod
    def from_dict(source):
        return Channel(id=source['id'], name=source['name'])