# External Libraries
from pony.orm import Set, Database, Required, PrimaryKey, db_session, Optional

db = Database()


class Base:
    @classmethod
    @db_session
    def exists(cls, id_: str):
        return cls.get(id=id_) is not None  # pylint: disable=no-member

    @classmethod
    @db_session
    def get_s(cls, arg):
        return cls.get(id=arg)  # pylint: disable=no-member

    @property
    @db_session
    def json(self):
        return self.__class__[self.id].to_dict(with_collections=True, exclude="password")  # pylint: disable=no-member


class Mod(db.Entity, Base):
    id = PrimaryKey(str)
    title = Required(str)
    icon = Optional(str, nullable=True)
    path = Required(str)
    # TODO: Media
    tagline = Required(str)
    description = Required(str)
    website = Required(str)
    # TODO: Category
    released_at = Required(int)
    last_updated = Required(int)
    downloads = Required(int)
    authors = Set('User', reverse='mods')
    favorite_by = Set('User', reverse='favorites')
    reviews = Set('Review', reverse="mod")
    verified = Required(bool)


class User(db.Entity, Base):
    id = PrimaryKey(str)
    username = Required(str)
    avatar = Optional(str, nullable=True)
    donator = Required(bool)
    developer = Required(bool)
    moderator = Required(bool)
    bio = Required(str)
    mods = Set(Mod)
    favorites = Set(Mod)
    reviews = Set('Review', reverse="author")
    upvoted = Set('Review', reverse='upvoters')
    downvoted = Set('Review', reverse='downvoters')
    helpful = Set('Review', reverse='helpfuls')
    password = Required(str)
    lastPassReset = Optional(int, nullable=True)


class Review(db.Entity, Base):
    id = PrimaryKey(str)
    rating = Required(str)
    mod = Required(Mod)
    content = Required(str)
    author = Required(User)
    upvoters = Set(User)
    downvoters = Set(User)
    helpfuls = Set(User)
