# Stdlib
from secrets import token_hex

# External Libraries
from flask import abort, jsonify, request, send_file
from pony.orm import select, db_session
from simpleflake import simpleflake

# Sayonika Internals
from framework.models import Mod, User, Review
from framework.objects import database_handle
from framework.route import route, multiroute
from framework.route_wrappers import json
from framework.routecog import RouteCog
from framework.sayonika import Sayonika


class Userland(RouteCog):
    # === Compat with mods.py ===

    @staticmethod
    @db_session
    def new_path():
        used = [mod.path for mod in database_handle.mods]  # flake8: noqa pylint: disable=not-an-iterable
        path = token_hex(8)
        while path in used:
            path = token_hex(8)

        return path

    @staticmethod
    def new_id():
        return str(simpleflake())

    # === Mods ===

    @staticmethod
    def as_json(data: list):
        return [item.json for item in data]

    @staticmethod
    @db_session
    def verified():
        return [mod for mod in database_handle.mods if mod.verified]  # flake8: noqa pylint: disable=not-an-iterable

    @multiroute("/api/v1/mods", methods=["GET"], other_methods=["POST"])
    @json
    @db_session
    def get_mods(self):
        if "page" in request.args:
            try:
                page = int(request.args["page"])
            except ValueError:
                page = 1
        else:
            page = 1

        return jsonify(self.as_json(Mod.select(lambda mod: mod.verified).page(page)))

    @route("/api/v1/mods/recent_releases")
    @json
    def get_recent_releases(self):
        sorted_mods = reversed(sorted(self.verified(),
                                      key=lambda mod: mod.released_at))
        return jsonify(self.as_json(sorted_mods)[:10])

    @route("/api/v1/mods/popular")
    @json
    def get_popular(self):
        sorted_mods = reversed(sorted(self.verified(),
                                      key=lambda mod: mod.downloads))
        return jsonify(self.as_json(sorted_mods)[:10])

    @multiroute("/api/v1/mods/<mod_id>", methods=["GET"], other_methods=["PATCH"])
    @json
    def get_mod(self, mod_id: str):  # pylint: disable=no-self-use
        if not Mod.exists(mod_id):
            return abort(404, f"Mod '{mod_id}' not found on the server.")

        return jsonify(Mod.get_s(mod_id).json)

    @route("/api/v1/mods/<mod_id>/download")
    @json
    def get_download(self, mod_id: str):  # pylint: disable=no-self-use
        if not Mod.exists(mod_id):
            return abort(404, f"Mod '{mod_id}' not found on the server.")

        return send_file(f"mods/{Mod.get_s(mod_id).path}.zip")

    @multiroute("/api/v1/mods/<mod_id>/reviews", methods=["GET"], other_methods=["POST"])
    @json
    @db_session
    def get_mod_reviews(self, mod_id: str):
        if not Mod.exists(mod_id):
            return abort(404, f"Mod '{mod_id}' not found on the server.")

        reviews = select(review for review in Review if review.mod.id == mod_id)

        return jsonify(self.as_json(reviews))

    @route("/api/v1/mods/<mod_id>/authors")
    @json
    def get_mod_authors(self, mod_id: str):
        if not Mod.exists(mod_id):
            return abort(404, f"Mod '{mod_id}' not found on the server.")

        authors = select(user for user in User if Mod.get_s(mod_id) in user.mods)

        return jsonify(self.as_json(authors))

    # === Users ===

    @multiroute("/api/v1/users", methods=["GET"], other_methods=["POST"])
    @json
    @db_session
    def get_users(self):
        if "page" in request.args:
            try:
                page = int(request.args["page"])
            except ValueError:
                page = 1
        else:
            page = 1

        return jsonify(self.as_json(User.select().page(page)))

    @multiroute("/api/v1/users/<user_id>", methods=["GET"], other_methods=["POST"])
    @json
    def get_user(self, user_id: str):  # pylint: disable=no-self-use
        if not User.exists(user_id):
            return abort(404, f"User '{user_id}' not found on the server.")

        return jsonify(User.get_s(user_id).json)

    @route("/api/v1/users/<user_id>/favorites")
    @json
    @db_session
    def get_favorites(self, user_id: str):
        if not User.exists(user_id):
            return abort(404, f"User '{user_id}' not found on the server.")

        return jsonify(self.as_json(User.get_s(user_id).favorites))

    @route("/api/v1/users/<user_id>/mods")
    @json
    @db_session
    def get_user_mods(self, user_id: str):
        if not User.exists(user_id):
            return abort(404, f"User '{user_id}' not found on the server.")

        return jsonify(self.as_json(User.get_s(user_id).mods))

    @route("/api/v1/users/<user_id>/reviews")
    @json
    @db_session
    def get_user_reviews(self, user_id: str):
        if not User.exists(user_id):
            return abort(404, f"User '{user_id}' not found on the server.")

        if "page" in request.args:
            try:
                page = int(request.args["page"])
            except ValueError:
                page = 1
        else:
            page = 1

        return jsonify(self.as_json(
            Review.select(lambda review: review.author.id == user_id).page(page)
        ))


def setup(core: Sayonika):
    Userland(core).register()
