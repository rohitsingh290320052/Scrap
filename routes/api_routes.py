# routes/api_routes.py
from flask import Blueprint, request, jsonify
from extensions import db
from models import ScrapedData
from scraper.scraper import scrape_site

api_bp = Blueprint('api', __name__)

@api_bp.route('/articles', methods=['GET'])
def get_articles():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    pagination = ScrapedData.query.order_by(ScrapedData.scraped_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    items = [a.to_dict() for a in pagination.items]
    return jsonify({
        'items': items,
        'page': pagination.page,
        'pages': pagination.pages,
        'total': pagination.total
    })

@api_bp.route('/scrape', methods=['POST'])
def api_scrape():
    data = request.get_json() or {}
    url = data.get('url')
    if not url:
        return jsonify({'error': 'url required'}), 400
    scraped = scrape_site(url)
    if scraped.get('error'):
        return jsonify({'error': scraped['error']}), 400
    item = ScrapedData(
        title=scraped.get('title'),
        url=scraped.get('url'),
        meta_description=scraped.get('meta_description'),
        meta_keywords=scraped.get('meta_keywords'),
        first_image=scraped.get('first_image'),
        images=scraped.get('images'),
        headings=scraped.get('headings'),
        links_count=scraped.get('links_count'),
        domain=scraped.get('domain'),
        content_snippet=scraped.get('content_snippet')
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({'message': 'scraped', 'id': item.id}), 201

@api_bp.route('/articles/<int:id>', methods=['GET'])
def api_article(id):
    a = ScrapedData.query.get_or_404(id)
    return jsonify(a.to_dict())
