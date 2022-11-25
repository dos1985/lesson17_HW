# app.py

from flask import Flask, request, jsonify
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app)
moves_ns = api.namespace('movies')
director_id = api.namespace('director')
genre_id = api.namespace('genre')


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")

class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Int() #dump_only=True
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)



"""возвращает список всех фильмов, разделенный по страницам;"""
@moves_ns.route('/')
class MovesView(Resource):
    def get(self):
        movies = Movie.query.all()
        return jsonify(movies_schema.dump(movies))

    def post(self):
        req_json = request.json
        new_movie = Movie(**req_json)
        with db.session.begin():
            db.session.add(new_movie)
        return "", 201



"""возвращает подробную информацию о фильме."""
@moves_ns.route('/<int:nid>')
class MoveView(Resource):
    def get(self, nid):
        movie = Movie.query.get(nid)
        return movie_schema.dump(movie), 200

    def put(self, nid):
        item_ = Movie.query.get(nid)
        new_item_reqeust = request.json
        item_.title = new_item_reqeust.get('title')
        item_.description = new_item_reqeust.get('description')
        item_.trailer = new_item_reqeust.get('trailer')
        item_.year = new_item_reqeust.get('year')
        item_.rating = new_item_reqeust.get('rating')
        item_.genre_id = new_item_reqeust.get('genre_id')
        item_.director_id = new_item_reqeust.get('director_id')
        db.session.add(item_)
        db.session.commit()
        return "", 201

    def delete(self, nid):
        movi_id = Movie.query.get(nid)
        db.session.delete(movi_id)
        db.session.commit()
        return "", 204

"""возвращает только фильмы с определенным режиссером по запросу типа"""
@director_id.route('/')
class DirectorsAll(Resource):
    def get(self):
        all_directors = db.session.query(Director).all()
        return jsonify(directors_schema.dump(all_directors))


@director_id.route('/<int:nid>')
class DirectorsView(Resource):
    def get(self, nid):
        all_directors = db.session.query(Director).get(nid)
        return jsonify(director_schema.dump(all_directors))


"""возвращает только фильмы определенного жанра  по запросу типа"""
@genre_id.route('/')
class GenresAll(Resource):
    def get(self):
        all_genres = db.session.query(Genre).all()
        return jsonify(genres_schema.dump(all_genres))


@genre_id.route('/<int:nid>')
class GenresView(Resource):
    def get(self, nid):
        all_genres = db.session.query(Genre).get(nid)
        return jsonify(genre_schema.dump(all_genres))







if __name__ == '__main__':
    app.run(debug=True)

