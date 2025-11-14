from flask import Blueprint, request, redirect, url_for, render_template
from extensions import db
from models import ScrapedData
import json
import io
import pandas as pd
from flask import Response
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

scraper_bp = Blueprint('scraper', __name__)

from scraper.scraper import scrape_site


@scraper_bp.route('/scrape', methods=['POST'])
def scrape():
    url = request.form['url']
    if not url:
        return redirect(url_for('home'))

    data = scrape_site(url)

    if data.get("error"):
        return f"Scrape error: {data['error']}", 400

    item = ScrapedData(
        title=data.get("title"),
        url=data.get("url"),
        meta_description=data.get("meta_description"),
        meta_keywords=data.get("meta_keywords"),
        first_image=data.get("first_image"),
        images=data.get("images"),
        headings=data.get("headings"),
        links_count=data.get("links_count"),
        domain=data.get("domain"),
        content_snippet=data.get("content_snippet")
    )

    db.session.add(item)
    db.session.commit()

    return redirect(url_for('scraper.dashboard'))


@scraper_bp.route('/dashboard')
def dashboard():
    page = int(request.args.get('page', 1))
    per_page = 10

    pagination = ScrapedData.query.order_by(
        ScrapedData.scraped_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('dashboard.html', data=pagination)


@scraper_bp.route('/preview/<int:item_id>')
def preview(item_id):
    item = ScrapedData.query.get_or_404(item_id)

    headings = json.loads(item.headings) if item.headings else []
    images = json.loads(item.images) if item.images else []

    return render_template('preview.html', item=item, headings=headings, images=images)

@scraper_bp.route('/export/csv')
def export_csv():
    items = ScrapedData.query.order_by(ScrapedData.scraped_at.desc()).all()
    rows = [a.to_dict() for a in items]
    df = pd.DataFrame(rows)
    csv_io = io.StringIO()
    df.to_csv(csv_io, index=False)
    csv_io.seek(0)
    return Response(csv_io.getvalue(), mimetype='text/csv',
                    headers={"Content-Disposition":"attachment;filename=scraped_data.csv"})

@scraper_bp.route('/export/pdf')
def export_pdf():
    items = ScrapedData.query.order_by(ScrapedData.scraped_at.desc()).all()
    buf = io.BytesIO()
    p = canvas.Canvas(buf, pagesize=letter)
    width, height = letter
    y = height - 40
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, y, "Scraped Data Report")
    p.setFont("Helvetica", 10)
    y -= 30
    for a in items:
        p.drawString(40, y, f"{a.id}. {a.title[:80]}")
        y -= 14
        if y < 60:
            p.showPage()
            y = height - 40
    p.save()
    buf.seek(0)
    return Response(buf.read(), mimetype='application/pdf',
                    headers={"Content-Disposition":"attachment;filename=scraped_data.pdf"})
