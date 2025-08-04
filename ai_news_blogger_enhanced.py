import os
import json
import logging
import openai
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
from pathlib import Path
import re
import feedparser
import time
# Add Together import
from together import Together
import base64
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Embedded API Keys and Credentials
OPENAI_API_KEY = "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"
TOGETHER_API_KEY = "ea8bf961c3ba4a4a006a648a8cc55caaa53b43f3543b6f95224c3c9a07cbb1df"
WP_SITE_URL = "https://autoblog2.amartglobal.in"
WP_USERNAME = "admin"
WP_APP_PASSWORD = "Sjqp CdFY 2aka RfFi uOs7 BVnk"

class ChatGPTBlogGenerator:
    def __init__(self, openai_api_key: str = None, output_dir: str = "blog_posts"):
        # Use embedded key if none provided
        self.openai_api_key = openai_api_key or OPENAI_API_KEY
        openai.api_key = self.openai_api_key
        self.openai_model = "gpt-4o"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        # Together API setup with embedded key
        self.together_client = Together(api_key=TOGETHER_API_KEY)
        self.together_model = "black-forest-labs/FLUX.1-schnell-Free"
        # Processed URLs file
        self.processed_urls_file = self.output_dir / "processed_urls.txt"
        self.processed_urls = set()
        if self.processed_urls_file.exists():
            with open(self.processed_urls_file, 'r', encoding='utf-8') as f:
                for line in f:
                    self.processed_urls.add(line.strip())

    def _slugify(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s-]', '', text)
        text = re.sub(r'\s+', '-', text)
        text = re.sub(r'-+', '-', text)
        return text.strip('-')

    def fetch_articles_from_rss(self, max_articles: int = 3):
        feeds = [
            "https://www.artificialintelligence-news.com/feed/",
            "https://www.sciencedaily.com/rss/computers_math/artificial_intelligence.xml",
            "https://www.technologyreview.com/topic/artificial-intelligence/feed"
        ]
        articles = []
        for feed_url in feeds:
            try:
                logger.info(f"Fetching from feed: {feed_url}")
                feed = feedparser.parse(feed_url)
                if not feed.entries:
                    logger.warning(f"No entries found in feed: {feed_url}")
                    continue
                for entry in feed.entries[:max_articles]:
                    title = entry.title
                    summary = entry.summary if hasattr(entry, 'summary') else ''
                    link = entry.link
                    articles.append({
                        'title': title,
                        'summary': summary,
                        'link': link
                    })
            except Exception as e:
                logger.error(f"Error fetching feed {feed_url}: {str(e)}")
        return articles

    def generate_blog_post_with_chatgpt(self, article: dict) -> dict:
        prompt = f"""Write a unique and engaging tech blog post based on the following news article. The blog should be entirely original, sound human-written, natural, and highly engaging.\n\nGuidelines:\n- Make it simple and easy to understand for general tech readers, especially at the start (an abstract introduction for non-technical but curious audiences).\n- Preserve all technical concepts, facts, and key details for expert readers.\n- Where appropriate, add reliable extra context or recent related insights to make the blog comprehensive and trustworthy for technical audiences.\n- Maintain high accuracy and factual correctness at all times.\n\nTitle: {article['title']}\nSummary: {article['summary']}\n\nIn addition to the blog post, also provide a simple, minimalistic, clickbait, and attractive prompt for an AI image generator to create a thumbnail image for this blog.\n\nPlease format the response as a valid JSON object with the following fields:\n- title: An engaging, original title for the blog post\n- slug: A URL-friendly version of the title\n- tags: List of relevant tags (max 5)\n- summary: A brief summary (2-3 sentences)\n- content: The full blog post in Markdown format\n- thumbnail_prompt: The minimalistic, clickbait, and attractive thumbnail prompt for an AI image generator.\n\nIMPORTANT: Your response must be a properly formatted JSON object with no additional text before or after."""
        try:
            logger.info(f"Generating blog post with ChatGPT for article: {article['title']}")
            client = openai.OpenAI(api_key=self.openai_api_key)
            response = client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are a professional tech blogger who writes engaging and accurate blog posts. You are a native English speaker and you write in a way that is easy to understand for general tech readers, especially at the start (an abstract introduction for non-technical but curious audiences)."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2048
            )
            response_text = response.choices[0].message.content
            try:
                blog_post = json.loads(response_text)
            except json.JSONDecodeError:
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    blog_post = json.loads(json_match.group())
                else:
                    raise ValueError("Could not extract JSON from ChatGPT response")
            blog_post['date'] = datetime.now().strftime("%Y-%m-%d")
            blog_post['model'] = self.openai_model
            blog_post['source_link'] = article['link']
            logger.info(f"Successfully generated blog post: {blog_post['title']}")
            return blog_post
        except Exception as e:
            logger.error(f"Error generating blog post with ChatGPT: {str(e)}")
            return None

    def validate_blog_post_with_chatgpt(self, original_article: dict, generated_blog: dict) -> bool:
        """
        Validate the generated blog post against the original article to check for accuracy and hallucinations.
        Returns True if the blog is accurate, False otherwise.
        """
        prompt = f"""You are a fact-checking expert. Compare the original news article with the generated blog post and determine if the blog post is accurate and doesn't contain hallucinated or fake information.

Original Article:
Title: {original_article['title']}
Summary: {original_article['summary']}
Link: {original_article['link']}

Generated Blog Post:
Title: {generated_blog['title']}
Content: {generated_blog['content']}

Your task is to:
1. Check if all key facts, figures, names, and technical details in the generated blog match the original article
2. Verify that no fake information, dates, or claims have been added
3. Ensure the blog doesn't contain hallucinated quotes, statistics, or events
4. Confirm that any additional context provided is reasonable and doesn't contradict the source

Respond with a JSON object containing:
- "is_accurate": true/false
- "confidence": high/medium/low
- "issues": [list of specific issues found, if any]
- "recommendation": "approve" or "reject"

IMPORTANT: Be strict in your evaluation. If there's any doubt about accuracy, reject the blog post. Your response must be valid JSON only."""

        try:
            logger.info(f"Validating blog post: {generated_blog['title']}")
            client = openai.OpenAI(api_key=self.openai_api_key)
            response = client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are a strict fact-checking expert who prioritizes accuracy over creativity. You must reject any content that contains unverified claims, hallucinated information, or facts not supported by the source material. You must respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for more consistent validation
                max_tokens=1024
            )
            
            response_text = response.choices[0].message.content
            logger.info(f"Validation response: {response_text[:200]}...")  # Log first 200 chars for debugging
            
            # Clean the response text to extract JSON
            cleaned_response = response_text.strip()
            
            # Remove markdown code blocks if present
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]  # Remove ```json
            elif cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:]  # Remove ```
            
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]  # Remove trailing ```
            
            cleaned_response = cleaned_response.strip()
            
            try:
                validation_result = json.loads(cleaned_response)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                logger.error(f"Cleaned response: {cleaned_response}")
                # Try to extract JSON using regex as fallback
                import re
                json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
                if json_match:
                    try:
                        validation_result = json.loads(json_match.group())
                        logger.info("Successfully extracted JSON using regex")
                    except json.JSONDecodeError:
                        logger.error("Failed to parse JSON even with regex extraction")
                        return False
                else:
                    logger.error("Could not find JSON pattern in response")
                    return False
            
            is_accurate = validation_result.get('is_accurate', False)
            confidence = validation_result.get('confidence', 'low')
            issues = validation_result.get('issues', [])
            recommendation = validation_result.get('recommendation', 'reject')
            
            logger.info(f"Validation result - Accurate: {is_accurate}, Confidence: {confidence}, Recommendation: {recommendation}")
            if issues:
                logger.warning(f"Validation issues found: {issues}")
            
            return recommendation == "approve" and is_accurate
            
        except Exception as e:
            logger.error(f"Error validating blog post with ChatGPT: {str(e)}")
            return False  # Fail safe - reject if validation fails

    def regenerate_blog_post_with_chatgpt(self, article: dict, attempt: int = 1) -> dict:
        """
        Regenerate a blog post with additional instructions to be more conservative and accurate.
        """
        prompt = f"""Write a unique and engaging tech blog post based on the following news article. The blog should be entirely original, sound human-written, natural, and highly engaging.

CRITICAL REQUIREMENTS:
- ONLY include information that is directly supported by the source article
- DO NOT add any additional facts, statistics, or claims not mentioned in the source
- DO NOT create fake quotes, dates, or events
- If you need to add context, clearly indicate it's additional background information
- Be conservative and stick closely to the source material
- If the source doesn't provide enough detail for a comprehensive blog, focus on what is known

Guidelines:
- Make it simple and easy to understand for general tech readers
- Preserve all technical concepts, facts, and key details for expert readers
- Maintain high accuracy and factual correctness at all times
- If uncertain about any detail, omit it rather than guess

Title: {article['title']}
Summary: {article['summary']}

In addition to the blog post, also provide a simple, minimalistic, clickbait, and attractive prompt for an AI image generator to create a thumbnail image for this blog.

Please format the response as a valid JSON object with the following fields:
- title: An engaging, original title for the blog post
- slug: A URL-friendly version of the title
- tags: List of relevant tags (max 5)
- summary: A brief summary (2-3 sentences)
- content: The full blog post in Markdown format
- thumbnail_prompt: The minimalistic, clickbait, and attractive thumbnail prompt for an AI image generator.

IMPORTANT: Your response must be a properly formatted JSON object with no additional text before or after."""

        try:
            logger.info(f"Regenerating blog post (attempt {attempt}) with ChatGPT for article: {article['title']}")
            client = openai.OpenAI(api_key=self.openai_api_key)
            response = client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are a professional tech blogger who writes engaging and accurate blog posts. You are a native English speaker and you write in a way that is easy to understand for general tech readers. You are extremely careful to only include verified information from the source material."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,  # Lower temperature for more conservative generation
                max_tokens=2048
            )
            response_text = response.choices[0].message.content
            try:
                blog_post = json.loads(response_text)
            except json.JSONDecodeError:
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    blog_post = json.loads(json_match.group())
                else:
                    raise ValueError("Could not extract JSON from ChatGPT response")
            blog_post['date'] = datetime.now().strftime("%Y-%m-%d")
            blog_post['model'] = self.openai_model
            blog_post['source_link'] = article['link']
            blog_post['generation_attempt'] = attempt
            logger.info(f"Successfully regenerated blog post: {blog_post['title']}")
            return blog_post
        except Exception as e:
            logger.error(f"Error regenerating blog post with ChatGPT: {str(e)}")
            return None

    def generate_image_with_together(self, prompt: str, steps: int = 1, n: int = 1, out_path: Path = None, timeout: int = 90):
        result = {}
        def target():
            try:
                logger.info(f"Generating image with Together for prompt: {prompt}")
                response = self.together_client.images.generate(
                    prompt=prompt,
                    model=self.together_model,  # 'black-forest-labs/FLUX.1-schnell-Free'
                    steps=max(1, min(steps, 4)),
                    n=n
                )
                b64_data = response.data[0].b64_json if response.data and hasattr(response.data[0], 'b64_json') else None
                url = response.data[0].url if response.data and hasattr(response.data[0], 'url') else None
                if b64_data:
                    image_bytes = base64.b64decode(b64_data)
                    if out_path is not None:
                        with open(out_path, 'wb') as img_file:
                            img_file.write(image_bytes)
                        logger.info(f"Saved generated image to {out_path} (from base64)")
                        result['path'] = str(out_path)
                    else:
                        result['bytes'] = image_bytes
                elif url:
                    logger.info(f"Downloading image from URL: {url}")
                    img_response = requests.get(url)
                    if img_response.status_code == 200:
                        if out_path is not None:
                            with open(out_path, 'wb') as img_file:
                                img_file.write(img_response.content)
                            logger.info(f"Saved generated image to {out_path} (from URL)")
                            result['path'] = str(out_path)
                        else:
                            result['bytes'] = img_response.content
                    else:
                        logger.error(f"Failed to download image from URL. Status code: {img_response.status_code}")
                        result['error'] = f"Failed to download image from URL. Status code: {img_response.status_code}"
                else:
                    logger.error("Together API did not return a valid image (no b64_json or url).")
                    result['error'] = "No image data returned"
            except Exception as e:
                logger.error(f"Error generating image with Together: {str(e)}")
                result['error'] = str(e)

        thread = threading.Thread(target=target)
        thread.start()
        waited = 0
        interval = 5
        while thread.is_alive() and waited < timeout:
            print(f"Waiting for image generation... ({waited}s elapsed)")
            time.sleep(interval)
            waited += interval
        thread.join(0)  # Ensure thread cleanup
        if thread.is_alive():
            logger.error("Image generation timed out.")
            return None
        if 'error' in result:
            return None
        return result.get('path') or result.get('bytes')

    def save_blog_post(self, blog_post: dict):
        if not blog_post:
            return
        slug = self._slugify(blog_post['title']) if blog_post.get('title') else 'untitled'
        filename = f"{slug}.json"
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(blog_post, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved blog post: {filename}")
        return filepath

    def upload_to_wordpress(self, blog_post):
        # Use embedded WordPress credentials
        if not all([WP_SITE_URL, WP_USERNAME, WP_APP_PASSWORD]):
            logger.error("WordPress credentials not properly configured")
            return False

        # 1. Upload the thumbnail image (if present)
        media_id = None
        if blog_post.get('thumbnail_image') and os.path.exists(blog_post['thumbnail_image']):
            try:
                with open(blog_post['thumbnail_image'], 'rb') as img:
                    filename = os.path.basename(blog_post['thumbnail_image'])
                    # Guess content type from file extension
                    ext = os.path.splitext(filename)[1].lower()
                    content_type = 'image/png' if ext == '.png' else 'image/jpeg' if ext in ['.jpg', '.jpeg'] else 'application/octet-stream'
                    media_headers = {
                        'Content-Disposition': f'attachment; filename={filename}',
                        'Content-Type': content_type,
                        'User-Agent': 'Python WordPress Client'
                    }
                    media_response = requests.post(
                        f"{WP_SITE_URL}/wp-json/wp/v2/media",
                        headers=media_headers,
                        data=img,
                        auth=HTTPBasicAuth(WP_USERNAME, WP_APP_PASSWORD)
                    )
                    logger.info(f"Image upload status: {media_response.status_code}")
                    logger.info(f"Image upload response: {media_response.text}")
                    if media_response.status_code in [200, 201]:
                        media_id = media_response.json().get('id')
                        logger.info(f"Uploaded thumbnail to WordPress, media_id={media_id}")
                    else:
                        logger.error(f"Failed to upload image: {media_response.text}")
            except Exception as e:
                logger.error(f"Exception during image upload: {e}")

        # 2. Create the blog post
        post_data = {
            "title": blog_post['title'],
            "content": blog_post['content'],
            "status": "publish",
            "featured_media": media_id if media_id else None,
            "excerpt": blog_post.get('summary', ''),
        }
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Python WordPress Client"
        }
        try:
            post_response = requests.post(
                f"{WP_SITE_URL}/wp-json/wp/v2/posts",
                auth=HTTPBasicAuth(WP_USERNAME, WP_APP_PASSWORD),
                headers=headers,
                json=post_data
            )
            if post_response.status_code == 201:
                logger.info(f"Blog post '{blog_post['title']}' uploaded successfully!")
                logger.info(f"Post URL: {post_response.json().get('link')}")
                return True
            else:
                logger.error(f"Failed to upload blog post: {post_response.text}")
                return False
        except Exception as e:
            logger.error(f"Exception during blog post upload: {e}")
            return False

    def mark_url_processed(self, url: str):
        with open(self.processed_urls_file, 'a', encoding='utf-8') as f:
            f.write(url + '\n')
        self.processed_urls.add(url)

    def run(self, max_articles: int = 3):
        articles = self.fetch_articles_from_rss(max_articles)
        articles_to_process = [a for a in articles if a.get('link') not in self.processed_urls]
        for idx, article in enumerate(articles_to_process):
            url = article.get('link')
            
            # Generate blog post (no validation)
            blog_post = self.generate_blog_post_with_chatgpt(article)
            
            if blog_post:
                logger.info(f"Blog post generated successfully")
                # Generate image using Together API
                slug = self._slugify(blog_post['title']) if blog_post.get('title') else 'untitled'
                image_filename = f"{slug}_thumbnail.png"
                image_path = self.output_dir / image_filename
                image_file_path = self.generate_image_with_together(
                    prompt=blog_post.get('thumbnail_prompt', ''),
                    steps=1,  # steps must be between 1 and 4 for this model
                    n=1,
                    out_path=image_path
                )
                if image_file_path:
                    blog_post['thumbnail_image'] = image_file_path
                else:
                    blog_post['thumbnail_image'] = None
                self.save_blog_post(blog_post)
                # Upload to WordPress if not already uploaded
                uploaded_flag = blog_post.get('uploaded_to_wordpress', False)
                if not uploaded_flag:
                    success = self.upload_to_wordpress(blog_post)
                    if success:
                        blog_post['uploaded_to_wordpress'] = True
                        self.save_blog_post(blog_post)
                self.mark_url_processed(url)
                print(f"\nBlog post '{blog_post['title']}' created successfully.")
            else:
                logger.error(f"Failed to generate blog post for article: {article['title']}")
                print(f"Failed to generate blog post for article: {article['title']}")
                # Mark as processed to avoid retrying the same article
                self.mark_url_processed(url)
            
            # Wait 1 minute only if there are more articles to process
            if idx < len(articles_to_process) - 1:
                logger.info("Waiting 60 seconds before next article...")
                time.sleep(60)
            time.sleep(2)  # Be nice to APIs

def main():
    # Use embedded OpenAI API key
    generator = ChatGPTBlogGenerator(OPENAI_API_KEY)
    generator.run()

if __name__ == "__main__":
    main()
