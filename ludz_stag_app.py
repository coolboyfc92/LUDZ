import streamlit as st
import random
from supabase import create_client, Client

# -------------------- SUPABASE SETUP --------------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
## -------------------- BAVARIAN BACKGROUND --------------------
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://www.nationalflaggen.de/flaggen-shop/media/2d/0f/f6/1665859289/12e3bf1592aba0fef67348db8a6ad2cb4d54e42b.jpg");
        background-size: cover;
        background-repeat: repeat;
        background-attachment: scroll;  /* ✅ makes it move with the page */
    }

    .main .block-container {
        background-color: rgba(255, 255, 255, 0.9);
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
    "https://scontent.fgla3-2.fna.fbcdn.net/v/t1.6435-9/82188351_10157905977513209_914144228009836544_n.jpg?_nc_cat=107&ccb=1-7&_nc_sid=2285d6&_nc_ohc=8O4HayFb4yMQ7kNvwGzbJd1&_nc_oc=AdnhH9iqNukXmPHkCY2ZmUWO65mN5zi_K8nrenyqlQ6wNqxTZd4V5La3B6pvW90UT20eZ_YTE7ANi1G-BXQ5siZO&_nc_zt=23&_nc_ht=scontent.fgla3-2.fna&_nc_gid=YbVcWtb7-j1WZarS-kHLMg&oh=00_AfVkCw2OCrt-i97EcySIjtgfynQsxRva2J7Z-SSjW4wmLw&oe=68CBD10E",
    width=600
)

# -------------------- UTILITY FUNCTIONS --------------------
def get_participants():
    response = supabase.table("participants").select("*").execute()
    return response.data if response.data else []

def add_participant(name, codename):
    supabase.table("participants").insert({"name": name, "codename": codename}).execute()

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
    "Enter participants and codenames (Name | Codename)", ""
).splitlines()

if st.sidebar.button("Add Participants"):
    for line in participants_input:
        if "|" in line:
            name, codename = [x.strip() for x in line.split("|", 1)]
            if name and codename:
                add_participant(name, codename)
    st.sidebar.success("Participants added!")

# Fetch participants
participants = get_participants()
participant_names = [p["name"] for p in participants]

# -------------------- TABS --------------------
tab1, tab2, tab3, tab4 = st.tabs(["🏠 Home", "🥨 Drinking Games", "⚔️ Forfeits", "📜 History"])

# -------------------- HOME TAB --------------------
with tab1:
    st.header("🍺 Willkommen zum Stag Night!")
    st.subheader("Teilnehmer & Codenamen")
    for p in sorted(participants, key=lambda x: x['codename']):
        st.write(f"{p['name']} → **{p['codename']}**")
    
    st.markdown("---")
    st.header("📖 Stag Night Rulebook")
    st.markdown("""
**Main Rules**
- **Code Names Only:** Everyone must pick a codename. Using a real name = sip penalty.
- **Foreign Drinks Rule:** Drinks must be referred to in a foreign language. Break = sip.
- **Stag’s Word is Law:** Groom can invent a 30-min rule. Break = sip.
- **The Banned Word Game:** Pick a word for the night. Slip = sip.
- **Left-Hand Rule:** Drinks in left hand only. Right hand = sip.
- **Story Chain:** Build a story together; break character = sip.
- **Silent Cheers:** All toasts are silent; speaking = sip.
- """)
    st.markdown("Hourly challenges are rolled in the Drinking Games tab. 🍻")

# -------------------- DRINKING GAMES TAB --------------------
with tab2:
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
    st.write("Select a participant and tier to assign a forfeit.")

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
    st.write("See all challenges and forfeits completed by each participant.")

    for p in participants:
        with st.expander(f"{p['codename']} ({p['name']})"):
            st.markdown("**Forfeits Done:**")
            forfeits = get_forfeits(p["id"])
            if forfeits:
                for f in forfeits:
                    st.markdown(f"- **{f['description'].split(':')[0]}**: {':'.join(f['description'].split(':')[1:])} ({f['tier']})")
            else:
                st.write("None yet.")

            st.markdown("**Challenges Completed:**")
            challenges = get_challenges(p["id"])
            if challenges:
                for c in challenges:
                    st.markdown(f"- {c['description']}")
            else:
                st.write("None yet.")





