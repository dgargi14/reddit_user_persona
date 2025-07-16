import praw
import re
import os
from transformers import pipeline

REDDIT_CLIENT_ID = '5qcXpZ5Yqagn6udYqB-MWA'
REDDIT_CLIENT_SECRET = 'YKldqa-aMFkl8FPAlyqoobg0xu14dw'
REDDIT_USER_AGENT = 'persona_script'

reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID,
                     client_secret=REDDIT_CLIENT_SECRET,
                     user_agent=REDDIT_USER_AGENT)

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def extract_username(url):
    pattern = r'reddit\.com\/user\/([A-Za-z0-9_-]+)\/?'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid Reddit profile URL")

def fetch_user_data(username, post_limit=10, comment_limit=10):
    try:
        user = reddit.redditor(username)

        posts = []
        comments = []

        for submission in user.submissions.new(limit=post_limit):
            posts.append({
                'title': submission.title,
                'body': submission.selftext,
                'url': submission.url
            })

        for comment in user.comments.new(limit=comment_limit):
            comments.append({
                'body': comment.body,
                'link': f"https://reddit.com{comment.permalink}"
            })

        return posts, comments

    except Exception as e:
        print(f"Error fetching data for user '{username}': {e}")
        return [], []

from transformers import pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def generate_persona(posts, comments, username):
    text_data = f"Reddit Posts and Comments for user: {username}\n\n"

    for post in posts:
        text_data += f"POST: {post['title']}\n{post['body']}\nURL: {post['url']}\n\n"

    for comment in comments:
        text_data += f"COMMENT: {comment['body']}\nLink: {comment['link']}\n\n"

    # Truncate text_data to roughly 3000 characters (approx under 1024 tokens)
    text_data = text_data[:3000]

    prompt = (
        f"Based on the following Reddit posts and comments by user '{username}', "
        "generate a detailed USER PERSONA with these sections:\n"
        "- Personality Traits\n"
        "- Interests\n"
        "- Goals\n"
        "- Frustrations\n"
        "- Online Behavior\n\n"
        "For each section, cite the specific post or comment you used (quote the text and include the URL).\n"
        "Here is the data:\n\n"
        f"{text_data}"
    )

    print("Generating structured user persona with citations...")

    summary = summarizer(prompt, max_length=500, min_length=200, do_sample=False)[0]['summary_text']

    return summary

def save_output(username, persona_text):
    output_dir = 'sample_outputs'
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"{username}_persona.txt")

    with open(filepath, "w", encoding='utf-8') as f:
        f.write(persona_text)
    print(f"Persona saved to {filepath}")

def main():
    reddit_url = "https://www.reddit.com/user/kojied/"
    username = extract_username(reddit_url)

    if not username:
        print("Invalid Reddit URL.")
        return

    posts, comments = fetch_user_data(username)

    if not posts and not comments:
        print("No data found for this user.")
        return

    persona = generate_persona(posts, comments, username)
    save_output(username, persona)

if __name__ == "__main__":
    main()