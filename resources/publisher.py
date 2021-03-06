from flask_restful import Resource
from models.book import Publisher
from flask_jwt_extended import jwt_required
from schemas.book import PaginatedPublisherSchema, PublisherSchema
from http import HTTPStatus
from webargs import fields
from webargs.flaskparser import use_kwargs
from sqlalchemy import asc, desc
from extension import cache, limiter


class PublisherCollectionResource(Resource):
    decorators = [
        limiter.limit(
            "100/minute",
            error_message="Too many request")]

    @jwt_required()
    @use_kwargs({
        "page": fields.Integer(missing=1),
        "per_page": fields.Integer(missing=5),
        "order": fields.String(missing="asc"),
        "sort": fields.String(missing="id"),
        "q": fields.String(missing="")
    }, location="querystring")
    @cache.cached(query_string=True)
    def get(self, page, per_page, sort, order, q):
        keyword = f"%{q}%"
        if sort not in ["id", "name"]:
            sort = "id"
        if order == "desc":
            sort_logic = desc(getattr(Publisher, sort))
        else:
            sort_logic = asc(getattr(Publisher, sort))
        publishers = Publisher.query.filter(
            Publisher.name.ilike(keyword)).order_by(sort_logic).paginate(
            page=page, per_page=per_page)
        return PaginatedPublisherSchema().dump(publishers), HTTPStatus.OK


class PublisherResource(Resource):
    decorators = [
        limiter.limit(
            "100/minute",
            error_message="Too much message.")]

    @jwt_required()
    @cache.cached()
    def get(self, publisher_id):
        publisher = Publisher.query.filter_by(id=publisher_id).first()
        if not publisher:
            return {"message": "Publisher not found!"}, HTTPStatus.NOT_FOUND

        return PublisherSchema(exclude=["id"]).dump(publisher), HTTPStatus.OK
