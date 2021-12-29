from flask_restful import Resource
from flask_jwt_extended import jwt_required
from http import HTTPStatus
from models.book import Category
from schemas.book import PaginatedCategorySchema, CategorySchema
from webargs.flaskparser import use_kwargs
from webargs import fields
from sqlalchemy import asc, desc


class CategoryCollectionResource(Resource):
    @jwt_required()
    @use_kwargs(
        {
            "page": fields.Integer(missing=1),
            "per_page": fields.Integer(missing=5),
            "sort": fields.String(missing="id"),
            "order": fields.String(missing="asc"),
            "q": fields.String(missing="")
        }, location="querystring")
    def get(self, page, per_page, sort, order, q):
        keyword = f"%{q}%"
        if sort not in ["id", "name"]:
            sort = "id"
        if order == "desc":
            sort_logic = desc(getattr(Category, sort))
        else:
            sort_logic = asc(getattr(Category, sort))

        categories = Category.query.filter(Category.name.ilike(keyword)).order_by(sort_logic).paginate(page=page,
                                                                                                       per_page=per_page)
        return PaginatedCategorySchema().dump(categories), HTTPStatus.OK


class CategoryResource(Resource):
    @jwt_required()
    def get(self, category_id):
        category = Category.query.filter_by(id=category_id).first()
        if not category:
            return {"message": "Category not found!"}, HTTPStatus.NOT_FOUND

        return CategorySchema(exclude=["id"]).dump(category), HTTPStatus.OK