"""
Challenge Arena - Meme/GIF Reactions
Shows fun GIFs after submission based on score categories.
"""

import streamlit as st

# GIF URLs from GIPHY CDN (free, no API key needed)
# These are permanent GIPHY CDN links that work in any browser
MEME_GIFS = {
    "not_good": {
        "url": "https://media.giphy.com/media/3o6Zt481isNVuQI1lW/giphy.gif",  # Facepalm / disappointment
        "tier": "😤 Not Good",
        "caption": "Brother ughh... you can do better!",
        "color": "#ff4444",
    },
    "needs_work": {
        "url": "https://media.giphy.com/media/3o7aD2saalBwwftBIY/giphy.gif",  # Facepalm
        "tier": "😬 Needs Work",
        "caption": "Oof! Time to hit the books again!",
        "color": "#ff8800",
    },
    "getting_there": {
        "url": "https://media.giphy.com/media/26ufdipQqU2lhNA4g/giphy.gif",  # Confused thinking
        "tier": "🤔 Getting There",
        "caption": "Hmm... not bad, but there's room to grow!",
        "color": "#ffcc00",
    },
    "not_bad": {
        "url": "https://media.giphy.com/media/3o6Zt6hF5QhTgGqF6M/giphy.gif",  # Not bad / nodding
        "tier": "👍 Not Bad",
        "caption": "Not bad at all! You're on the right track!",
        "color": "#44bb44",
    },
    "great_job": {
        "url": "https://media.giphy.com/media/l0HlNQ03J5JxX6lva/giphy.gif",  # Celebration
        "tier": "🎉 Great Job",
        "caption": "Amazing work! You're crushing it!",
        "color": "#0088ff",
    },
    "legendary": {
        "url": "https://media.giphy.com/media/26ufdipQqU2lhNA4g/giphy.gif",  # Mind blown / legendary
        "tier": "🏆 LEGENDARY!",
        "caption": "ABSOLUTE LEGEND! PERFECT SCORE! 🔥🔥🔥",
        "color": "#8800ff",
    },
}


def get_meme_for_score(score):
    """
    Get the appropriate meme GIF based on score.
    
    Args:
        score: Float between 0 and 1 (or 0-100)
    
    Returns:
        dict with keys: url, tier, caption, color
    """
    # Normalize score to 0-100 if it's 0-1
    if score is not None:
        if score <= 1:
            score_pct = score * 100
        else:
            score_pct = score
    else:
        score_pct = 0

    if score_pct >= 95:
        return MEME_GIFS["legendary"]
    elif score_pct >= 90:
        return MEME_GIFS["great_job"]
    elif score_pct >= 80:
        return MEME_GIFS["not_bad"]
    elif score_pct >= 60:
        return MEME_GIFS["getting_there"]
    elif score_pct >= 40:
        return MEME_GIFS["needs_work"]
    else:
        return MEME_GIFS["not_good"]


def display_meme(score, score_label="Score"):
    """
    Display a meme GIF based on the score in a styled container.
    
    Args:
        score: Float score value
        score_label: Label to show (e.g., "Your Score")
    """
    meme = get_meme_for_score(score)
    
    # Normalize for display
    if score is not None:
        if score <= 1:
            display_score = score * 100
        else:
            display_score = score
        score_text = f"{display_score:.1f}%"
    else:
        score_text = "N/A"

    # Create a styled container
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, {meme['color']}22, {meme['color']}44);
            border: 2px solid {meme['color']};
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            margin: 20px 0;
        ">
            <h2 style="color: {meme['color']}; margin: 0;">{meme['tier']}</h2>
            <p style="font-size: 24px; font-weight: bold; margin: 10px 0;">
                {score_label}: {score_text}
            </p>
            <p style="font-size: 18px; font-style: italic; margin: 5px 0;">
                {meme['caption']}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Display the GIF
    st.image(meme["url"], use_container_width=True)