from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from db.models import Article
from db.session import get_db
from db.schemas import ArticleOut, HomeArticlesResponse, PaginatedArticlesOut
from urllib.parse import urlparse
from typing import List, Optional


router = APIRouter()

def generate_slug(url: str, title: str) -> str:
    """
    Generate a URL-friendly slug for an article.
    - Prefer last path segment from URL if available.
    - Fallback to title-based slug if URL path is empty.
    """
    if url:
        path = urlparse(url).path  # /news/grant-cardone-bitcoin-real-estate-trump-housing/
        last_segment = path.rstrip("/").split("/")[-1]  # grant-cardone-bitcoin-real-estate-trump-housing
        if last_segment:
            return last_segment.lower()
    # Fallback to title
    slug = (
        title.lower()
        .replace("&", "and")
        .replace("?", "")
        .replace("'", "")
    )
    slug = "-".join(slug.split())  # replace spaces with hyphens
    return slug

def map_article(article: Article, locale: str) -> ArticleOut:
    title = (
        article.jp_title if locale == "ja" and article.jp_title
        else article.title
    )

    content = (
        article.jp_content if locale == "ja" and article.jp_content
        else article.content or ""
    )

    slug = generate_slug(article.url, title)

    return ArticleOut(
        id=article.id,
        title=title,
        excerpt=content,
        image=article.image_url or "",
        slug=slug,
        date=article.publish_date.strftime("%d %b %Y %H:%M"),
        source = article.source
    )

@router.get("/articles/home", response_model=HomeArticlesResponse)
def get_home_articles(
    locale: str = Query("en", regex="^(en|ja)$"),
    db: Session = Depends(get_db),
):
    articles = (
        db.query(Article)
        .filter(Article.credibility_score >= 0.3)
        .order_by(
            Article.credibility_score.desc(),
            Article.publish_date.desc(),
        )
        .limit(15)
        .all()
    )

    if not articles:
        raise ValueError("No articles found")

    mapped = [map_article(a, locale) for a in articles]

    return HomeArticlesResponse(
        featuredArticle=mapped[0],
        sideArticles=mapped[1:6],
        storyCards=mapped[6:8],
        articleListItems=mapped[8:],
    )


@router.get("/articles/counts")
def get_article_counts(db: Session = Depends(get_db)):
    # Priority counts: top, major, breaking
    priority_counts = (
        db.query(Article.priority, func.count(Article.id))
        .group_by(Article.priority)
        .all()
    )
    priority_dict = {p: c for p, c in priority_counts}

    # Category counts
    category_counts = (
        db.query(Article.category, func.count(Article.id))
        .filter(Article.credibility_score > 0)
        .group_by(Article.category)
        .all()
    )
    category_dict = {c: n for c, n in category_counts}

    return {
        "priority": priority_dict,
        "category": category_dict
    }
    
@router.get("/articles/breaking", response_model=List[ArticleOut])
def get_breaking_articles(
    locale: str = Query("en", regex="^(en|ja)$"),
    limit: int = 10,
    db: Session = Depends(get_db),
):
    """
    Return latest articles with priority 'breaking'.
    """
    articles = (
        db.query(Article)
        .filter(Article.priority == "breaking")
        .order_by(Article.publish_date.desc())
        .limit(limit)
        .all()
    )

    # ALWAYS return a list
    return [map_article(article, locale) for article in articles]


@router.get("/articles", response_model=PaginatedArticlesOut)
def get_articles(
    category: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, le=50),
    db: Session = Depends(get_db),
):
    query = (
        db.query(Article)
        .filter(Article.credibility_score > 0)
    )

    if category:
        query = query.filter(
            func.lower(Article.category) == category.lower()
        )

    if priority:
        query = query.filter(
            func.lower(Article.priority) == priority.lower()
        )

    total = query.count()

    articles = (
        query.order_by(Article.publish_date.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": [
            {   
                "id": a.id,
                "slug": generate_slug(a.url, a.title),
                "title": a.title,
                "excerpt": a.content,
                "image": a.image_url,
                "date": a.publish_date.strftime("%d %b %Y %H:%M"),
                "source": a.source,

            }
            for a in articles
        ],
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": (total + page_size - 1) // page_size,
    }        

@router.get("/articles/featured", response_model=ArticleOut | None)
def get_featured_article(
    category: Optional[str] = None,
    priority: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = (
        db.query(Article)
        .filter(Article.credibility_score > 0)
    )

    if category:
        query = query.filter(Article.category == category)

    if priority:
        query = query.filter(Article.priority == priority)

    article = (
        query.order_by(Article.publish_date.desc())
        .first()
    )

    if not article:
        return None

    return {
        "id": article.id,
        "slug": generate_slug(article.url, article.content),
        "title": article.title,
        "excerpt": article.content,
        "image": article.image_url,
        "date": article.publish_date.strftime("%d %b %Y %H:%M"),
        "source": article.source,
    }
    
@router.get("/article/latest")
def latest(db: Session = Depends(get_db)):
    result = db.execute(
        text("""
            SELECT *
            FROM articles
            WHERE credibility_score != 0
            ORDER BY publish_date DESC NULLS LAST
            LIMIT 10
        """)
    )
    return result.mappings().all()


@router.get("/article/by-category")
def articles_by_category(db: Session = Depends(get_db)):
    result = db.execute(
        text("""
            SELECT
                category,
                json_agg(a ORDER BY publish_date DESC) AS articles
            FROM articles a
            WHERE credibility_score != 0
            GROUP BY category
        """)
    )
    return result.mappings().all()

@router.get("/article/by-priority")
def articles_by_priority(db: Session = Depends(get_db)):
    result = db.execute(
        text("""
            SELECT
                priority,
                json_agg(a ORDER BY publish_date DESC) AS articles
            FROM articles a
            WHERE credibility_score != 0
            GROUP BY priority
        """)
    )
    return result.mappings().all()

@router.get("/article/latest/category/{category}")
def latest_by_category(category: str, db: Session = Depends(get_db)):
    result = db.execute(
        text("""
            SELECT *
            FROM articles
            WHERE category = :category
              AND credibility_score != 0
            ORDER BY publish_date DESC NULLS LAST
            LIMIT 10
        """),
        {"category": category}
    )
    return result.mappings().all()



@router.get("/article/{id}")
def article(id: int, db: Session = Depends(get_db)):
    result = db.execute(text("SELECT * FROM articles WHERE id = :id"), {"id" : id})
    return result.mappings().first()