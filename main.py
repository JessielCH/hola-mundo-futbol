import os
from typing import Generator

import requests
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/futbol_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(Integer, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    short_name = Column(String, nullable=True)
    crest_url = Column(String, nullable=True)
    website = Column(String, nullable=True)
    venue = Column(String, nullable=True)
    founded = Column(Integer, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "external_id": self.external_id,
            "name": self.name,
            "short_name": self.short_name,
            "crest_url": self.crest_url,
            "website": self.website,
            "venue": self.venue,
            "founded": self.founded,
        }


def fetch_premier_league_teams(api_key: str):
    url = "https://api.football-data.org/v4/competitions/PL/teams"
    headers = {"X-Auth-Token": api_key}
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    data = response.json()

    teams = []
    for item in data.get("teams", []):
        teams.append(
            {
                "external_id": item.get("id"),
                "name": item.get("name"),
                "short_name": item.get("shortName"),
                "crest_url": item.get("crest"),
                "website": item.get("website"),
                "venue": item.get("venue"),
                "founded": item.get("founded"),
            }
        )
    return teams


Base.metadata.create_all(bind=engine)
app = FastAPI(title="Hola Mundo Futbol")
templates = Jinja2Templates(directory="templates")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def index(request: Request, db: Session = Depends(get_db)):
    teams = db.query(Team).order_by(Team.name).all()
    return templates.TemplateResponse("index.html", {"request": request, "teams": teams})


@app.get("/api/teams")
def read_teams(db: Session = Depends(get_db)):
    teams = db.query(Team).order_by(Team.name).all()
    return [team.to_dict() for team in teams]


@app.post("/api/fetch-teams")
def refresh_teams(db: Session = Depends(get_db)):
    api_key = os.getenv("FOOTBALL_API_KEY")
    if not api_key:
        raise HTTPException(status_code=400, detail="FOOTBALL_API_KEY is required in environment variables")

    try:
        teams = fetch_premier_league_teams(api_key)
    except Exception as error:
        raise HTTPException(status_code=502, detail=str(error))

    saved_count = 0
    for team_data in teams:
        team = db.query(Team).filter(Team.external_id == team_data["external_id"]).first()
        if not team:
            team = Team(external_id=team_data["external_id"])
            db.add(team)
        team.name = team_data["name"]
        team.short_name = team_data["short_name"]
        team.crest_url = team_data["crest_url"]
        team.website = team_data["website"]
        team.venue = team_data["venue"]
        team.founded = team_data["founded"]
        saved_count += 1

    db.commit()
    return JSONResponse({"saved": saved_count})
