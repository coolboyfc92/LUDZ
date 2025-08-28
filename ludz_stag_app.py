import streamlit as st
import random
from supabase import create_client, Client

# -------------------- SUPABASE SETUP --------------------
# Streamlit Cloud secrets must be flat keys
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------- APP HEADER --------------------
st.set_page_config(page_title="Lüdz – München wird niedergestochen", layout="wide")
st.title("Lüdz")
st.subheader("München wird niedergestochen")
st.image(
    "https://scontent.fgla3-2.fna.fbcdn.net/v/t1.6435-9/82188351_10157905977513209_914144228009836544_n.jpg?_nc_cat=107&ccb=1-7&_nc_sid=2285d6&_nc_ohc=8O4HayFb4yMQ7kNvwGzbJd1&_nc_oc=AdnhH9iqNukXmPHkCY2ZmUWO65mN5zi_K8nrenyqlQ6wNqxTZd4V5La3B6pvW90UT20eZ_YTE7ANi1G-BXQ5siZO&_nc_zt=23&_nc_ht=scontent.fgla3-2.fna&_nc_gid=YbVcWtb7-j1WZarS-kHLMg&oh=00_AfVkCw2OCrt-i97EcySIjtgfynQsxRva2J7Z-SSjW4wmLw&oe=68CBD10E",
    width=600
)

# -------------------- UTILITY FUNCTIONS --------------------
def get_participants():
    response = supabase.table("participants").select("*").execute()
    return response.data if response.data else []

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
st.sidebar.header("Add Participants with Custom Codenames")

# Multi-line input: one participant per line in format "Name | Codename"
participants_input = st.sidebar.text_area(
    "Enter participants and codenames (Name | Codename)", ""
).splitlines()

if st.sidebar.button("Add Participants"):
    participants = get_participants()
    existing_names = [p["name"] for p in participants]
    existing_codenames = [p["codename"] for p in participants]

    for line in participants_input:
        if "|" in line:
            name, codename = [x.strip() for x in line.split("|", 1)]
            if name and codename:
                if name in existing_names or codename in existing_codenames:
                    st.warning(f"{name} or {codename} already exists!")
                else:
                    supabase.table("participants").insert({"name": name, "codename": codename}).execute()
    st.sidebar.success("Participants added!")

# Fetch all participants
participants = get_participants()
participant_names = [p["name"] for p in participants]

# -------------------- TABS --------------------
tab1, tab2, tab3, tab4 = st.tabs(["Home", "Drinking Games", "Forfeits", "History"])

# -------------------- HOME TAB --------------------
with tab1:
    st.header("Welcome to the Stag Do")
    
    st.subheader("Stag Night Rulebook")
    st.markdown("""
    **Main Rules**
    
    - **Code Names Only:** Everyone must pick a code name at the start of the night. If you use a real name, you take a forfeit sip.
    - **Foreign Drinks Rule:** Drinks may only be referred to in a foreign language. If you say 'beer' in English, sip as a penalty.
    - **Stag’s Word is Law:** The groom can invent a rule at any point, lasting only 30 minutes. Breaking it results in a sip.
    - **The Banned Word Game:** Pick a word that cannot be said all night. Whoever slips must sip.
    - **Left-Hand Rule:** Drinks must only be held in the left hand. If caught using the right hand, sip.
    - **Story Chain:** Begin a made-up story about how you all know each other. Each person adds one sentence when asked. Forgetting or breaking character means a sip.
    - **Silent Cheers:** Every toast must be silent, with only eye contact and clinking glasses. If someone speaks, they sip.
    """)
    
    st.subheader("Hourly Dice Challenges")
    st.markdown("""
    Roll a six-sided dice each hour to determine a random challenge:

    1. **Mystery Round:** One person secretly orders a random drink for another (bartender’s choice).
    2. **Lost in Translation:** One person orders the next round using mime only.
    3. **Accent Round:** Everyone speaks in the same accent for one drink.
    4. **The Stag’s Shadow:** Copy the groom’s body language for 10 minutes.
    5. **Silent Selfie:** Take a group photo in silence. Laugh/speak → drink.
    6. **Cheers in Foreign:** Pick a language and use it for the next toast.
    """)

    st.subheader("Participants & Code Names")
    for p in sorted(participants, key=lambda x: x['codename']):
        st.write(f"{p['name']} → {p['codename']}")


# -------------------- DRINKING GAMES TAB --------------------
with tab2:
    st.header("Hourly Challenges")
    st.write("Roll a six-sided dice to get a random hourly challenge.")

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
        st.success(f"Dice rolled: {roll}")
        st.info(f"{participant_name} must do: {challenge}")
        pid = next(p["id"] for p in participants if p["name"] == participant_name)
        add_challenge(pid, challenge)

# -------------------- FORFEITS TAB --------------------
with tab3:
    st.header("Forfeit Randomiser")
    st.write("Select a participant and a tier to randomise a forfeit.")

    tier1 = [
        "Do a Shot", "Down Your Drink", "Empty Hand",
        "The Bitter Swap", "Burden of Coin", "Tongue of Strangers"
    ]
    tier2 = [
        "Crown of Fools", "The Tangled Path", "The Shackled Bond",
        "Servant’s Load", "Herald of Kings", "High-Five Herald", "Voice of the Silver Screen"
    ]
    tier3 = [
        "Trial by Fire", "Trial by Water", "Trial by Earth", "Trial by Air"
    ]

    tiers = {"Tier 1": tier1, "Tier 2": tier2, "Tier 3": tier3}

    participant_name = st.selectbox("Select Participant for Forfeit", participant_names)
    tier_choice = st.selectbox("Select Tier", list(tiers.keys()))

    if st.button("Randomise Forfeit"):
        choice = random.choice(tiers[tier_choice])
        st.info(f"{participant_name} must do: {choice}")
        pid = next(p["id"] for p in participants if p["name"] == participant_name)
        add_forfeit(pid, choice, tier_choice)

# -------------------- HISTORY TAB --------------------
with tab4:
    st.header("Participant History")
    st.write("See all challenges and forfeits completed by each participant.")

    for p in participants:
        st.subheader(f"{p['codename']} ({p['name']})")
        st.write("**Forfeits Done:**")
        forfeits = get_forfeits(p["id"])
        if forfeits:
            for f in forfeits:
                st.write(f"- {f['description']} ({f['tier']})")
        else:
            st.write("None yet.")
        st.write("**Challenges Completed:**")
        challenges = get_challenges(p["id"])
        if challenges:
            for c in challenges:
                st.write(f"- {c['description']}")
        else:
            st.write("None yet.")

