import streamlit as st
import random
from supabase import create_client, Client

# -------------------- SUPABASE SETUP --------------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------- BAVARIAN BACKGROUND --------------------
st.markdown(
    """
    <style>
    /* Background image for the whole app */
    .stApp {
        background-image: url("https://static.vecteezy.com/system/resources/previews/053/232/428/non_2x/the-flag-of-the-city-of-munich-germany-vector.jpg");
        background-size: cover;
        background-repeat: repeat;
        background-attachment: fixed;
    }

    /* Main container */
    .stApp > .main {
        background-color: rgba(255, 255, 255, 0.8) !important; /* white-ish */
        padding: 2rem;
        border-radius: 10px;
        font-family: 'Almendra', serif !important;
    }

    /* Force text color for common elements inside main */
    .stApp > .main p,
    .stApp > .main h1,
    .stApp > .main h2,
    .stApp > .main h3,
    .stApp > .main h4,
    .stApp > .main h5,
    .stApp > .main h6,
    .stApp > .main div.stMarkdown {
        color: #000000 !important; /* black text */
    }

    /* Tab headers container */
    div[role="tablist"] {
        background-color: rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px;
        padding: 0.3rem;
        margin-bottom: 1rem;
    }

    /* Individual tab buttons */
    div[role="tab"] {
        background-color: rgba(255, 255, 255, 0.2) !important;
        border-radius: 5px;
        padding: 0.4rem 0.8rem;
        margin: 0 0.2rem;
        color: #000000 !important; /* black text for tabs */
    }

    /* Selected tab */
    div[role="tab"][aria-selected="true"] {
        background-color: rgba(255, 255, 255, 0.4) !important;
        font-weight: bold;
        color: #000000 !important; /* ensure selected tab text is black */
    }

    /* Tab content panels */
    div[role="tabpanel"] {
        background-color: rgba(255, 255, 255, 0.2) !important;
        border-radius: 10px;
        padding: 1rem;
        margin-top: 0.5rem;
        color: #000000 !important; /* force black inside tab panels */
    }

    /* Sidebar */
    .css-1d391kg {
        background-color: rgba(0,0,0,0.85) !important;
        padding: 1rem;
        border-radius: 10px;
        font-family: 'Almendra', serif !important;
        color: #ffffff !important; /* white text in sidebar */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------- APP HEADER --------------------
st.set_page_config(page_title="Lüdz – München wird niedergestochen", layout="wide")
st.image(
    "https://scontent.fgla3-2.fna.fbcdn.net/v/t1.6435-9/82188351_10157905977513209_914144228009836544_n.jpg?_nc_cat=107&ccb=1-7&_nc_sid=2285d6&_nc_ohc=8O4HayFb4yMQ7kNvwGzbJd1&_nc_oc=AdnhH9iqNukXmPHkCY2ZmUWO65mN5zi_K8nrenyqlQ6wNqxTZd4V5La3B6pvW90UT20eZ_YTE7ANi1G-BXQ5siZO&_nc_zt=23&_nc_ht=scontent.fgla3-2.fna&_nc_gid=YbVcWtb7-j1WZarS-kHLMg&oh=00_AfVkCw2OCrt-i97EcySIjtgfynQsxRva2J7Z-SSjW4wmLw&oe=68CBD10E",
    width=400
)
st.title("🍺 Lüdz")
st.subheader("München wird niedergestochen")

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
    supabase.table("pubs").insert({"name": pub_name}).execute()

def get_pub_rules(pub_id):
    resp = supabase.table("pub_rules").select("*").eq("pub_id", pub_id).execute()
    return resp.data if resp.data else []

def add_pub_rule(pub_id, rule_text):
    supabase.table("pub_rules").insert({"pub_id": pub_id, "rule": rule_text}).execute()

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
participants_input = st.sidebar.text_area(
    "Enter participants and codenames (Name ; Codename)", ""
).splitlines()

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
pub_names = [p["name"] for p in pubs]

# -------------------- TABS --------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏠 Home", "📖 Pub Rules", "🥨 Hourly Challenges",
    "⚔️ Forfeits", "📜 History", "🏆 Leaderboard"
])

# -------------------- HOME TAB --------------------
with tab1:
    st.header("🍺 Welcome to the Stag of one Mr Schofield: Three time Lad of the year🐘🐘🐘")
    home_text = (
        "Welcome to Lüdz! Each participant chooses a codename. "
        "Remember, Silent Cheers are serious business. 🍺 "
        "Lets shank this city and try not to bottle the hobbit"
    )
    st.markdown(home_text)

    # Check if the Easter egg has already been solved
    egg_resp = supabase.table("easter_eggs").select("solved").eq("egg_name", "Level3Forfeit").execute()
    egg_solved = egg_resp.data[0]["solved"] if egg_resp.data else False

    if not egg_solved:
        if st.button("🍺"):  # hidden trigger emoji
            password_input = st.text_input("Enter the secret password")
            if password_input.upper() == "SCHOMILF69":
                st.success("Easter egg unlocked! You can nominate someone for a Level 3 forfeit.")

                # Mark the Easter egg as solved
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

# -------------------- PUB RULES TAB --------------------
with tab2:
    st.header("📖 Pub Rules")
    if pubs:  # Only show selectbox if pubs exist
        selected_pub = st.selectbox("Select a Pub", pub_names)
        pub_item = next((p for p in pubs if p["name"] == selected_pub), None)
        if pub_item:
            pub_id = pub_item["id"]

            # Show existing rules
            rules = get_pub_rules(pub_id)
            if rules:
                st.markdown("**Existing rules for this pub:**")
                for r in rules:
                    st.markdown(f"- {r['rule']}")
            else:
                st.write("No rules applied yet for this pub.")

            # Standard stag night rules
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
    st.header("🕰️ Hourly Challenges")
    dice_challenges = {
        1: "Mystery Round: One person secretly orders a random drink for another.",
        2: "Lost in Translation: One person orders the next round using mime only.",
        3: "Accent Round: Everyone speaks in the same accent for one drink.",
        4: "The Stag’s Shadow: Copy the groom’s body language for 10 minutes.",
        5: "Silent Selfie: Take a group photo in silence. Laugh/speak → drink.",
        6: "Cheers in Foreign: Pick a language and use it for the next toast."
    }

    if participants:
        participant_name = st.selectbox("Select Participant", participant_names)
        if st.button("Roll Dice for Challenge"):
            roll = random.randint(1, 6)
            challenge = dice_challenges[roll]
            st.success(f"🎲 Dice rolled: {roll}")
            st.info(f"**{participant_name}** must do: {challenge}")
            pid = next(p["id"] for p in participants if p["name"] == participant_name)
            add_challenge(pid, challenge)
    else:
        st.write("Add participants first to roll challenges.")

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
                    if "Tier 1" in tier:
                        score += 1
                    elif "Tier 2" in tier:
                        score += 3
                    elif "Tier 3" in tier:
                        score += 9
            leaderboard.append((p['codename'], score))
        leaderboard.sort(key=lambda x: x[1], reverse=True)
        for codename, score in leaderboard:
            st.write(f"**{codename}**: {score} points")
    else:
        st.write("No participants yet.")
