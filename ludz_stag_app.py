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
    body::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: url('https://i.postimg.cc/sgGGw8zW/124273818-3862144150464817-4969867150395063431-n.jpg');
        background-size: cover;
        background-repeat: repeat;
        z-index: -2;
    }
    body::after {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        z-index: -1;
    }
    .main .block-container {
        background-color: rgba(255, 255, 255, 0.85);
        padding: 2rem;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------- APP HEADER --------------------
st.set_page_config(page_title="Lüdz – München wird niedergestochen", layout="wide")
st.title("🍺 Lüdz")
st.subheader("München wird niedergestochen")
st.image(
    "https://scontent.fgla3-2.fna.fbcdn.net/v/t1.6435-9/82188351_10157905977513209_914144228009836544_n.jpg",
    width=600
)

# -------------------- UTILITY FUNCTIONS --------------------
def get_participants():
    response = supabase.table("participants").select("*").execute()
    return response.data if response.data else []

def add_participant(name, codename):
    supabase.table("participants").insert({"name": name, "codename": codename}).execute()

def get_pubs():
    response = supabase.table("pubs").select("*").execute()
    return response.data if response.data else []

def add_pub(name):
    supabase.table("pubs").insert({"name": name}).execute()

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
    response = supabase.table("forfeits_done").select("*").eq("participant_id", participant_id).execute()
    return response.data

def get_challenges(participant_id):
    response = supabase.table("challenges_done").select("*").eq("participant_id", participant_id).execute()
    return response.data

# -------------------- PARTICIPANT & PUB SETUP --------------------
st.sidebar.header("🍻 Add Participants")
participants_input = st.sidebar.text_area("Enter participants and codenames (Name ; Codename)", "").splitlines()
if st.sidebar.button("Add Participants"):
    for line in participants_input:
        if ";" in line:
            name, codename = [x.strip() for x in line.split(";", 1)]
            if name and codename:
                add_participant(name, codename)
    st.sidebar.success("Participants added!")

st.sidebar.header("🏠 Add New Pub")
pub_input = st.sidebar.text_input("Pub Name")
if st.sidebar.button("Add Pub"):
    if pub_input.strip():
        add_pub(pub_input.strip())
        st.sidebar.success(f"Pub '{pub_input.strip()}' added!")

# Fetch participants and pubs
participants = get_participants()
participant_names = [p["name"] for p in participants]
pubs = get_pubs()
pub_names = [p["name"] for p in pubs]

# -------------------- FORFEIT TIERS --------------------
tier1 = {
    "The Whisper of Glass": "Do a shot. The group chooses what.",
    "The Empty Hand": "Pour your drink out. You stay dry until the next bar.",
    "The Bitter Swap": "Swap drinks with someone else, even if half-finished.",
    "The Burden of Coin": "Buy a round for two random people in the group.",
    "The Tongue of Strangers": "Speak only in German until your next drink arrives. Fail, drink again."
}
tier2 = {
    "The Crown of Fools": "Wear a stupid hat, glasses, or accessory the group provides.",
    "The Shackled Bond": "Be handcuffed (or tied) to another member for 20 minutes.",
    "The Tangled Path": "Tie your shoelaces together until the next bar.",
    "The Servant's Load": "Carry the stag's shoes in your hands until the next venue.",
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

# -------------------- TABS --------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Home", "🥨 Drinking Games", "⚔️ Forfeits", "📜 History", "🏆 Leaderboard"])

# -------------------- HOME TAB --------------------
with tab1:
    st.header("🍺 Willkommen zum Stag Night!")
    
    if not participants:
        st.info(
            "Welcome! This app is for stag nights and Bavarian drinking fun. "
            "You can add participants and pubs on the sidebar, roll hourly challenges, "
            "assign forfeits, and track history. 🍻"
        )
    else:
        st.subheader("Teilnehmer & Codenamen")
        for p in sorted(participants, key=lambda x: x['codename']):
            st.write(f"{p['name']} → **{p['codename']}**")
    
    st.markdown("---")
    st.header("📖 Stag Night Rulebook")
    st.markdown("""
**Main Rules**
- **Code Names Only:** Everyone must pick a codename. Using a real name = sip penalty.
- **Foreign Drinks Rule:** Drinks must be referred to in a foreign language. Break = sip.
- **Stag's Word is Law:** Groom can invent a 30-minute rule. Break = sip.
- **The Banned Word Game:** Pick a word for the night. Slip = sip.
- **Left-Hand Rule:** Drinks in left hand only. Right hand = sip.
- **Story Chain:** Build a story together; break character = sip.
- **Silent Cheers:** All toasts are silent; speaking = sip.
""")
    st.markdown("Hourly challenges are rolled in the Drinking Games tab. 🍻")
    
    # -------------------- HIDDEN EASTER EGG --------------------
    if st.button("🕵️‍♂️", key="hidden_egg"):
        password_input = st.text_input("Enter secret password")
        if password_input:
            if password_input == "SCHOMILF69":
                egg = supabase.table("easter_eggs").select("*").eq("egg_name", "level3_nomination").execute().data
                if egg and not egg[0]["solved"]:
                    supabase.table("easter_eggs").update({"solved": True}).eq("egg_name", "level3_nomination").execute()
                    st.success("Secret unlocked! You may nominate a participant for a Tier 3 forfeit!")
                    if participants:
                        participant_name = st.selectbox("Select participant for Level 3", participant_names)
                        if st.button("Nominate for Level 3"):
                            pid = next((p["id"] for p in participants if p["name"] == participant_name), None)
                            if pid:
                                name, desc = random.choice(list(tier3.items()))
                                add_forfeit(pid, f"{name}: {desc}", "Tier 3 — Trials")
                                st.warning(f"{participant_name} has been nominated for: {name}")
                    else:
                        st.info("No participants yet to nominate.")
                else:
                    st.info("This secret has already been solved. Only one use!")
            else:
                st.error("Wrong password")

# -------------------- DRINKING GAMES TAB --------------------
with tab2:
    st.header("🕰️ Hourly Challenges")
    if not participants:
        st.info("Add participants to roll challenges.")
    else:
        dice_challenges = {
            1: "Mystery Round: One person secretly orders a random drink for another (bartender’s choice).",
            2: "Lost in Translation: One person orders the next round using mime only.",
            3: "Accent Round: Everyone speaks in the same accent for one drink.",
            4: "The Stag's Shadow: Copy the groom's body language for 10 minutes.",
             5: "Silent Selfie: Take a group photo in silence. Laugh/speak → drink.",
             6: "Cheers in Foreign: Pick a language and use it for the next toast."
        }
        participant_name = st.selectbox("Select Participant", participant_names)
        if st.button("Roll Dice for Challenge"):
            roll = random.randint(1, 6)
            challenge = dice_challenges[roll]
            st.success(f"🎲 Dice rolled: {roll}")
            st.info(f"**{participant_name}** must do: {challenge}")
            pid = next(p["id"] for p in participants if p["name"] == participant_name)
            add_challenge(pid, challenge)

# -------------------- FORFEITS TAB --------------------
with tab3:
    st.header("⚔️ Forfeit Randomiser")
    if not participants:
        st.info("Add participants to assign forfeits.")
    else:
        participant_name = st.selectbox("Select Participant for Forfeit", participant_names)
        tier_choice = st.selectbox("Select Tier", list(tiers.keys()))
        if st.button("Randomise Forfeit"):
            name, desc = random.choice(list(tiers[tier_choice].items()))
            st.warning(f"**{participant_name} must do: {name}**")
            st.info(desc)
            pid = next(p["id"] for p in participants if p["name"] == participant_name)
            add_forfeit(pid, f"{name}: {desc}", tier_choice)

# -------------------- HISTORY TAB --------------------
with tab4:
    st.header("📜 Participant History")
    if not participants:
        st.info("Add participants to see history.")
    else:
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

# -------------------- LEADERBOARD TAB --------------------
with tab5:
    st.header("🏆 Forfeit Leaderboard")
    if not participants:
        st.info("Add participants to see leaderboard.")
    else:
        leaderboard = []
        for p in participants:
            forfeits = get_forfeits(p["id"])
            tier_score = {"Tier 1 — Light":1, "Tier 2 — Medium":2, "Tier 3 — Trials":3}
            score = sum([tier_score.get(f['tier'],0) for f in forfeits])
            leaderboard.append({"name": p["codename"], "score": score, "forfeits": len(forfeits)})
        leaderboard = sorted(leaderboard, key=lambda x: x['score'], reverse=True)
        for entry in leaderboard:
            st.markdown(f"**{entry['name']}** — {entry['score']} points ({entry['forfeits']} forfeits)")

