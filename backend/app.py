import instaloader
import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure Gemini
try:
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables.")
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    print(f"Error configuring Gemini: {e}")
    model = None

# Initialize Instaloader
L = instaloader.Instaloader()

@app.route("/")
def index():
    return "Hello, World!"

@app.route("/scrape/<username>")
def scrape_profile(username):
    try:
        profile = instaloader.Profile.from_username(L.context, username)

        # Get recent posts
        posts_data = []
        count = 0
        for post in profile.get_posts():
            if count < 12:  # Limit to 12 recent posts
                if post.caption:
                    posts_data.append({
                        "caption": post.caption,
                        "url": post.url,
                        "likes": post.likes,
                        "comments": post.comments,
                        "date_utc": post.date_utc,
                    })
                count += 1
            else:
                break
        
        all_captions = " ".join([p["caption"] for p in posts_data if p["caption"]])
        
        persona_description = profile.biography
        if all_captions and model:
            try:
                prompt = (
                    "Based on the following Instagram captions and user biography, create a detailed persona description. "
                    "Describe their likely personality, interests, and communication style. Keep it to 2-3 sentences.\n\n"
                    f"**Biography:** {profile.biography}\n\n"
                    f"**Captions:**\n{all_captions}"
                )
                response = model.generate_content(prompt)
                persona_description = response.text
            except Exception as e:
                print(f"Error generating content with Gemini: {e}")
                # Fallback to biography + captions if Gemini fails
                persona_description = profile.biography + "\n\n" + (all_captions[:300] + '...') if len(all_captions) > 300 else all_captions
        elif all_captions:
            # Fallback if model wasn't configured
            persona_description = profile.biography + "\n\n" + (all_captions[:300] + '...') if len(all_captions) > 300 else all_captions

        profile_data = {
            "username": profile.username,
            "user_id": profile.userid,
            "full_name": profile.full_name,
            "biography": profile.biography,
            "followers": profile.followers,
            "followees": profile.followees,
            "posts_count": profile.mediacount,
            "profile_pic_url": profile.profile_pic_url,
            "is_private": profile.is_private,
            "posts": posts_data,
            "persona_description": persona_description,
        }
        
        return jsonify(profile_data)

    except instaloader.exceptions.ProfileNotFoundError:
        return jsonify({"error": "Profile not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
