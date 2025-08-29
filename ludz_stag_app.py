import streamlit as st
import random
from supabase import create_client, Client

# -------------------- SUPABASE SETUP --------------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="Lüdz – München wird niedergestochen", layout="wide")
st.markdown(
    """
    <style>
    /* Background image */
    body::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: url('https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Flag_of_Munich_%28striped%29.svg/2560px-Flag_of_Munich_%28striped%29.svg.png');
        background-size: cover;
        background-repeat: repeat;
        z-index: -2;
    }

    /* Dark overlay for readability */
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

    /* Main container styling */
    .main .block-container {
        background-color: rgba(255, 255, 255, 0.85);
        padding: 2rem;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
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

def get_pub_rules(pub_id):
    response = supabase.table("pub_rules").select("*").eq("pub_id", pub_id).execute()
    return response.data if response.data else []

def add_pub_rule(pub_id, description):
    supabase.table("pub_rules").insert({"pub_id": pub_id, "description": description}).execute()

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

# -------------------- PARTICIPANT SETUP --------------------
st.sidebar.header("🍻 Add Participants with Custom Codenames")
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

# Fetch participants and pubs
participants = get_participants()
participant_names = [p["name"] for p in participants]
pubs = get_pubs()
pub_names = [p["name"] for p in pubs]

# -------------------- TABS --------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏠 Home", "📖 Pub Rules", "🥨 Drinking Games", "⚔️ Forfeits", "📜 History", "🏆 Leaderboard"
])

# -------------------- HOME TAB --------------------
with tab1:
    st.header("🍺 Willkommen zum Stag Night!")
    st.markdown("""
    This app is your Bavarian guide to stag night madness. 
    Track participants, assign codenames, and play hourly drinking games or 
    assign legendary forfeits. Keep your wits and drink responsibly!
    """)
    
    st.subheader("Participants & Codenames")
    if participants:
        for p in sorted(participants, key=lambda x: x['codename']):
            st.write(f"{p['name']} → **{p['codename']}**")
    else:
        st.write("No participants yet. Add some in the sidebar to get started!")

    # Hidden Easter Egg
    egg_clicked = st.button("🎯")
    if egg_clicked:
        pwd = st.text_input("Enter the secret password to nominate a level 3 forfeit", type="password")
        if pwd == "SCHOMILF69":
            st.success("Password correct! You can nominate a participant for a level 3 forfeit.")
            participant_name = st.selectbox("Select participant", participant_names)
            if st.button("Assign Level 3 Forfeit"):
                pid = next(p["id"] for p in participants if p["name"] == participant_name)
                add_forfeit(pid, "Secret Easter Egg Forfeit", "Tier 3 — Trials")
                st.balloons()

# -------------------- PUB RULES TAB --------------------
with tab2:
    st.header("📖 Pub Rules")
    selected_pub = st.selectbox("Select Pub", pub_names)
    pub_obj = next((p for p in pubs if p["name"] == selected_pub), None)
    if pub_obj:
        rules = get_pub_rules(pub_obj["id"])
        if rules:
            for r in rules:
                st.markdown(f"- {r['description']}")
        else:
            st.write("No rules set for this pub yet.")
    
    st.subheader("Add New Rule")
    new_rule = st.text_input("Rule Description")
    if st.button("Add Rule"):
        if pub_obj and new_rule:
            add_pub_rule(pub_obj["id"], new_rule)
            st.success("Rule added!")

# -------------------- DRINKING GAMES TAB --------------------
with tab3:
    st.header("🕰️ Hourly Challenges")
    st.write("Roll a dice to assign a random challenge for a participant.")

    dice_challenges = {
        1: "Mystery Round: One person secretly orders a random drink for another (bartender’s choice).",
        2: "Lost in Translation: One person orders the next round using mime only.",
        3: "Accent Round: Everyone speaks in the same accent for one drink.",
        4: "The Stag’s Shadow: Copy the groom’s body language for 10 minutes.",
        5: "Silent Selfie: Take a group photo in silence. Laugh/speak → drink.",
        6: "Cheers in Foreign: Pick a language and use it for the next toast."
    }

    if participants:
        participant_name = st.selectbox("Select Participant", participant_names, key="dg_participant")
        if st.button("Roll Dice for Challenge"):
            roll = random.randint(1, 6)
            challenge = dice_challenges[roll]
            st.success(f"🎲 Dice rolled: {roll}")
            st.info(f"**{participant_name}** must do: {challenge}")
            pid = next(p["id"] for p in participants if p["name"] == participant_name)
            add_challenge(pid, challenge)
    else:
        st.write("Add participants to start rolling hourly challenges.")

# -------------------- FORFEITS TAB --------------------
with tab4:
    st.header("⚔️ Forfeit Randomiser")
    st.write("Select a participant and tier to assign a forfeit.")

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
        participant_name = st.selectbox("Select Participant for Forfeit", participant_names, key="forfeit_participant")
        tier_choice = st.selectbox("Select Tier", list(tiers.keys()))
        if st.button("Randomise Forfeit"):
            name, desc = random.choice(list(tiers[tier_choice].items()))
            st.warning(f"**{participant_name} must do: {name}**")
            st.info(desc)
            pid = next(p["id"] for p in participants if p["name"] == participant_name)
            add_forfeit(pid, f"{name}: {desc}", tier_choice)
    else:
        st.write("Add participants to assign forfeits.")

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
        st.write("No participants to show history.")

# -------------------- LEADERBOARD TAB --------------------
with tab6:
    st.header("🏆 Forfeit Leaderboard")
    if participants:
        leaderboard = []
        tier_weights = {"Tier 1 — Light": 1, "Tier 2 — Medium": 2, "Tier 3 — Trials": 3}
        for p in participants:
            forfeits = get_forfeits(p["id"])
            score = sum(tier_weights.get(f['tier'], 0) for f in forfeits)
            leaderboard.append({"name": p["codename"], "score": score})
        leaderboard = sorted(leaderboard, key=lambda x: x["score"], reverse=True)
        for i, entry in enumerate(leaderboard, start=1):
            st.write(f"{i}. {entry['name']} — {entry['score']} points")
    else:
        st.write("No participants yet to generate leaderboard.")
