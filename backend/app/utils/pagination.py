from flask import request

def get_pagination_params():
    page = int(request.args.get("page", 1))
    per_page = min(int(request.args.get("per_page", 20)), 100)
    return page, per_page

def paginate_query(query, page, per_page):
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        "items": paginated.items,
        "total": paginated.total,
        "pages": paginated.pages,
        "current_page": paginated.page,
        "per_page": paginated.per_page,
        "has_next": paginated.has_next,
        "has_prev": paginated.has_prev,
    }
