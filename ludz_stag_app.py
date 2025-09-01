import streamlit as st
import random
from datetime import datetime
import pytz
from supabase import create_client, Client

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="Lüdz – München wird niedergestochen",
    layout="wide"
)

# -------------------- SUPABASE SETUP --------------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------- STYLE & BACKGROUND --------------------
st.markdown("""
<style>
.stApp { 
    background-image: url("https://static.vecteezy.com/system/resources/previews/053/232/428/non_2x/the-flag-of-the-city-of-munich-germany-vector.jpg");
    background-size: cover;
    background-repeat: repeat;
    background-attachment: fixed;
}
.stApp > .main {
    background-color: rgba(255, 255, 255, 0.85) !important;
    padding: 2rem;
    border-radius: 10px;
    font-family: 'Almendra', serif !important;
    color: #000000 !important;
    min-height: 80vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}
.countdown-title { font-size: 2rem; font-weight: bold; margin-bottom: 1rem; text-align:center; }
.countdown-timer { font-size: 3rem; font-weight: bold; color: #b22222; text-align:center; margin-bottom:1rem; }
.stApp > .main p,
.stApp > .main h1,
.stApp > .main h2,
.stApp > .main h3,
.stApp > .main h4,
.stApp > .main h5,
.stApp > .main h6,
.stApp > .main div.stMarkdown {
    color: #000000 !important;
}
.css-1d391kg { 
    background-color: rgba(0,0,0,0.85) !important; 
    padding: 1rem; 
    border-radius: 10px; 
    font-family: 'Almendra', serif !important; 
    color: #ffffff !important; 
}
</style>
""", unsafe_allow_html=True)

# -------------------- COUNTDOWN LOGIC --------------------
uk = pytz.timezone("Europe/London")
target_time = uk.localize(datetime(2025, 9, 1, 3, 0, 0))

now = datetime.now(uk)
if now < target_time:
    countdown_container = st.empty()

    # Calculate remaining time
    remaining = target_time - now
    hours, remainder = divmod(int(remaining.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)

    # Display countdown
    countdown_container.markdown(f"""
        <div class="countdown-title">⏳ App Locked</div>
        <div class="countdown-timer">{hours:02d}h {minutes:02d}m {seconds:02d}s</div>
        <div class="countdown-title">The fun begins soon...</div>
    """, unsafe_allow_html=True)

    # JS to reload every second
    st.components.v1.html("""
        <script>
        setTimeout(function(){
           window.location.reload();
        }, 1000);
        </script>
    """, height=0)

    # Stop rest of app until countdown finishes
    st.stop()
# -------------------- UTILITY FUNCTIONS --------------------
def get_participants():
    resp = supabase.table("participants").select("*").execute()
    return resp.data if resp.data else []

def add_participant(name, codename):
    supabase.table("participants").insert({"name": name, "codename": codename}).execute()

def get_pubs():
    resp = supabase.table("pubs").select("*").execute()
    return resp.data if resp.data else []

def add_pub(pub_name):
    supabase.table("pubs").insert({"pub_name": pub_name}).execute()

def get_pub_rules(pub_id):
    resp = supabase.table("pub_rules").select("*").eq("pub_id", pub_id).execute()
    return resp.data if resp.data else []

def add_pub_rule(pub_id, rule):
    supabase.table("pub_rules").insert({"pub_id": pub_id, "rule": rule}).execute()

def add_forfeit(participant_id, description, tier):
    supabase.table("forfeits_done").insert({
        "participant_id": participant_id,
        "description": description,
        "tier": tier
    }).execute()

def add_challenge(participant_id, description):
    supabase.table("challenges_done").insert({
        "participant_id": participant_id,
        "description": description
    }).execute()

def get_forfeits(participant_id):
    resp = supabase.table("forfeits_done").select("*").eq("participant_id", participant_id).execute()
    return resp.data

def get_challenges(participant_id):
    resp = supabase.table("challenges_done").select("*").eq("participant_id", participant_id).execute()
    return resp.data

# -------------------- SIDEBAR --------------------
st.sidebar.header("🍻 Add Participants")
participants_input = st.sidebar.text_area("Enter participants and codenames (Name ; Codename)", "").splitlines()
if st.sidebar.button("Add Participants"):
    for line in participants_input:
        if ";" in line:
            name, codename = [x.strip() for x in line.split(";", 1)]
            if name and codename:
                add_participant(name, codename)
    st.sidebar.success("Participants added!")

st.sidebar.header("🍺 Add Pub")
new_pub_name = st.sidebar.text_input("Pub Name")
if st.sidebar.button("Add Pub"):
    if new_pub_name.strip():
        add_pub(new_pub_name.strip())
        st.sidebar.success(f"Pub '{new_pub_name.strip()}' added!")

# -------------------- FETCH DATA --------------------
participants = get_participants()
participant_names = [p["name"] for p in participants]
pubs = get_pubs()
pub_names = [p["pub_name"] for p in pubs]

# -------------------- TABS --------------------
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🏠 Home", 
    "📖 Pub Rules", 
    "🥨 Hourly Challenges",
    "⚔️ Forfeits", 
    "📜 History", 
    "🏆 Leaderboard",
    "📚 Pub Rules Overview"
])

# -------------------- HOME TAB --------------------
with tab1:
    st.header("🍺 Welcome to the Stag of one Mr Schofield: Three time Lad of the year🐘🐘🐘")
    st.markdown(
        "Welcome to Lüdz! Each participant chooses a codename. "
        "Remember, Silent Cheers are serious business. 🍺 "
        "Lets shank this city and try not to bottle the hobbit"
    )

    # Easter egg
    egg_resp = supabase.table("easter_eggs").select("solved").eq("egg_name", "Level3Forfeit").execute()
    egg_solved = egg_resp.data[0]["solved"] if egg_resp.data else False
    if not egg_solved and st.button("🍺"):
        password_input = st.text_input("Enter the secret password")
        if password_input.upper() == "SCHOMILF69":
            st.success("Easter egg unlocked! You can nominate someone for a Level 3 forfeit.")
            if egg_resp.data:
                supabase.table("easter_eggs").update({"solved": True}).eq("egg_name", "Level3Forfeit").execute()
            else:
                supabase.table("easter_eggs").insert({"egg_name": "Level3Forfeit", "solved": True}).execute()

            if participants:
                chosen = st.selectbox("Select participant", participant_names)
                if st.button("Nominate for Level 3"):
                    add_forfeit(
                        next(p["id"] for p in participants if p["name"] == chosen),
                        "Secret Easter Egg Forfeit",
                        "Tier 3 — Trials"
                    )
                    st.success(f"{chosen} has been nominated!")
            else:
                st.write("No participants yet to nominate.")
    else:
        st.write("🍺 The Easter egg has already been discovered and used!")

    st.header("🦸‍♂️ No trip is complete without this legend")
    st.markdown("""
        <div style="display: flex; justify-content: center; margin-top: 20px;">
            <iframe width="560" height="315"
            src="https://www.youtube.com/embed/gxwWUiZ9b9M?si=yc-zy1xCvXpOLtPH"
            frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen></iframe>
        </div>
    """, unsafe_allow_html=True)

# -------------------- PUB RULES TAB --------------------
with tab2:
    st.header("📖 Pub Rules")
    if pubs:
        selected_pub = st.selectbox("Select a Pub", pub_names)
        pub_item = next((p for p in pubs if p["pub_name"] == selected_pub), None)
        if pub_item:
            pub_id = pub_item["id"]
            rules = get_pub_rules(pub_id)
            if rules:
                st.markdown("**Existing rules for this pub:**")
                for r in rules:
                    st.markdown(f"- {r['rule']}")
            else:
                st.write("No rules applied yet for this pub.")

            standard_rules = [
                "**Code Names Only:** Everyone must pick a codename. Using a real name = sip penalty.",
                "**Foreign Drinks Rule:** Drinks must be referred to in a foreign language. Break = sip.",
                "**Stag’s Word is Law:** Groom can invent a 30-min rule. Break = sip.",
                "**The Banned Word Game:** Pick a word for the night. Slip = sip.",
                "**Left-Hand Rule:** Drinks in left hand only. Right hand = sip.",
                "**Story Chain:** Build a story together; break character = sip.",
                "**Silent Cheers:** All toasts are silent; speaking = sip."
            ]

            if st.button("Roll Pub Rule"):
                selected_rule = random.choice(standard_rules)
                st.info(f"📜 Rule for **{selected_pub}**: {selected_rule}")
                add_pub_rule(pub_id, selected_rule)
                st.success("Rule saved for this pub!")
        else:
            st.write("Selected pub not found.")
    else:
        st.write("No pubs exist yet. Add one using the sidebar.")

# -------------------- HOURLY CHALLENGES TAB --------------------
with tab3:
    st.header("🥨 Hourly Challenges")
    dice_challenges = {
        1: "Mystery Round: One person secretly orders a random drink for another.",
        2: "Lost in Translation: One person orders the next round using mime only.",
        3: "Accent Round: Everyone speaks in the same accent for one drink.",
        4: "The Stag’s Shadow: Copy the groom’s body language for 10 minutes.",
        5: "Silent Selfie: Take a group photo in silence. Laugh or speak → drink.",
        6: "Cheers in Foreign: Pick a language and use it for the next toast."
    }

    if participants:
        if st.button("Use the Randomiser"):
            roll = random.randint(1,6)
            challenge = dice_challenges[roll]
            participant = random.choice(participants)
            participant_name = participant["name"]
            st.success(f"🎲 Dice rolled: {roll}")
            st.info(f"**{participant_name}** has been chosen to do: {challenge}")
            add_challenge(participant["id"], challenge)
    else:
        st.write("Add participants first to use the randomiser.")

# -------------------- FORFEITS TAB --------------------
with tab4:
    st.header("⚔️ Forfeit Randomiser")
    tier1 = {
        "The Whisper of Glass": "Do a shot. The group chooses what.",
        "Pints Out for Harambe": "Pour your drink out. You stay dry until the next bar.",
        "The Bitter Swap": "Swap drinks with someone else, even if half-finished.",
        "The Burden of Coin": "Buy a round for two random people in the group.",
        "The Tongue of Strangers": "Speak only in German until your next drink arrives. Fail, drink again."
    }
    tier2 = {
        "The Crown of Fools": "Wear a stupid hat, glasses, or accessory the group provides.",
        "The Shackled Bond": "Be handcuffed (or tied) to another member for 20 minutes.",
        "The Tangled Path": "Tie your shoelaces together until the next bar.",
        "The Servant’s Load": "Carry the stag’s shoes in your hands until the next venue.",
        "The Herald of Kings": "Introduce yourself to the next bartender as 'The King of Bavaria.'",
        "The High-Five Herald": "Get strangers to high-five you outside the next bar.",
        "The Voice of the Silver Screen": "Speak only in movie quotes for 10 minutes."
    }
    tier3 = {
        "Trial by Fire": "Eat a ghost pepper or insanely hot wing. No drink for 2 minutes.",
        "Trial by Water": "Down a pint of water while the group pours more on you.",
        "Trial by Earth": "Lick something grim but safe (classic: armpit). Outdoors? Eat a handful of grass.",
        "Trial by Air": "Stand on a chair or table and give a dramatic toast in your best Shakespearean voice."
    }
    tiers = {"Tier 1 — Light": tier1, "Tier 2 — Medium": tier2, "Tier 3 — Trials": tier3}

    if participants:
        participant_name = st.selectbox("Select Participant for Forfeit", participant_names)
        tier_choice = st.selectbox("Select Tier", list(tiers.keys()))
        if st.button("Randomise Forfeit"):
            name, desc = random.choice(list(tiers[tier_choice].items()))
            st.warning(f"**{participant_name} must do: {name}**")
            st.info(desc)
            pid = next(p["id"] for p in participants if p["name"] == participant_name)
            add_forfeit(pid, f"{name}: {desc}", tier_choice)
    else:
        st.write("Add participants first to assign forfeits.")

# -------------------- HISTORY TAB --------------------
with tab5:
    st.header("📜 Participant History")
    if participants:
        for p in participants:
            with st.expander(f"{p['codename']} ({p['name']})"):
                st.markdown("**Forfeits Done:**")
                forfeits = get_forfeits(p["id"])
                if forfeits:
                    for f in forfeits:
                        parts = f['description'].split(":", 1)
                        if len(parts) == 2:
                            title, detail = parts
                            st.markdown(f"- **{title.strip()}**: {detail.strip()} ({f['tier']})")
                        else:
                            st.markdown(f"- {f['description']} ({f['tier']})")
                else:
                    st.write("None yet.")

                st.markdown("**Challenges Completed:**")
                challenges = get_challenges(p["id"])
                if challenges:
                    for c in challenges:
                        st.markdown(f"- {c['description']}")
                else:
                    st.write("None yet.")
    else:
        st.write("No participants yet.")

# -------------------- LEADERBOARD TAB --------------------
with tab6:
    st.header("🏆 Forfeit Leaderboard")
    if participants:
        leaderboard = []
        for p in participants:
            forfeits = get_forfeits(p["id"])
            score = 0
            if forfeits:
                for f in forfeits:
                    tier = f['tier']
                    if "Tier 1" in tier: score += 1
                    elif "Tier 2" in tier: score += 3
                    elif "Tier 3" in tier: score += 9
            leaderboard.append((p['codename'], score))
        leaderboard.sort(key=lambda x: x[1], reverse=True)
        for codename, score in leaderboard:
            st.write(f"**{codename}**: {score} points")
    else:
        st.write("No participants yet.")

# -------------------- PUB RULES OVERVIEW TAB --------------------
with tab7:
    st.header("📚 Pub Rules Overview")
    if pubs:
        for pub in pubs:
            st.subheader(f"🍺 {pub['pub_name']}")
            rules = get_pub_rules(pub["id"])
            if rules:
                for r in rules:
                    st.markdown(f"- {r['rule']}")
            else:
                st.write("No rules set yet for this pub.")
    else:
        st.write("No pubs yet. Add one using the sidebar.")
