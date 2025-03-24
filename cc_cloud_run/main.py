from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from google.cloud import firestore
from typing import Annotated
import datetime


app = FastAPI()

# mount static files
app.mount("/static", StaticFiles(directory="/app/static"), name="static")
templates = Jinja2Templates(directory="/app/template")

# init firestore client
db = firestore.Client()
votes_collection = db.collection("votes")


@app.get("/")
async def read_root(request: Request):
    # ====================================
    # ++++ START CODE HERE ++++
    # ========= =============== ============

    # stream all votes; count tabs / spaces votes, and get recent votes
    # Get all vote documents
    votes = votes_collection.stream()

    vote_data = []
    for v in votes:
        vote_data.append(v.to_dict())
    
    tabs_count = 0
    spaces_count = 0

    for v in vote_data:
        if v.get("team") == "TABS":
            tabs_count += 1
        elif v.get("team") == "SPACES":
            spaces_count += 1

    recent_votes_query = votes_collection.order_by("time_cast", direction=firestore.Query.DESCENDING).limit(5)
    recent_votes_snapshots = recent_votes_query.stream()

    recent_votes = []
    for vote in recent_votes_snapshots:
        recent_data = vote.to_dict()
        recent_votes.append({
            "team": recent_data.get("team"),
            "time_cast": datetime.datetime.fromisoformat(recent_data.get("time_cast"))
        })

    return templates.TemplateResponse("index.html", {
        "request": request,
        "tabs_count": tabs_count,
        "spaces_count": spaces_count,
        "recent_votes": recent_votes,
    })

    # ====================================
    # ++++ STOP CODE ++++
    # ====================================


@app.post("/")
async def create_vote(team: Annotated[str, Form()]):
    if team not in ["TABS", "SPACES"]:
        raise HTTPException(status_code=400, detail="Invalid vote")

    # ====================================
    # ++++ START CODE HERE ++++
    # ====================================

    # create a new vote document in firestore
    vote_data = {
        "team": team,
        "time_cast": datetime.datetime.utcnow().isoformat()
    }
    votes_collection.add(vote_data)

    return {"detail": f"Vote for {team} submitted successfully"}

    # ====================================
    # ++++ STOP CODE ++++
    # ====================================
