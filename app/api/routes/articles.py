from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from db.session import get_db

router = APIRouter()


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