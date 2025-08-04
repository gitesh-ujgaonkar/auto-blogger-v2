# NeuroScribe - AI News Blogger

An automated AI-powered blog generator that creates engaging tech blog posts from RSS feeds and validates them for accuracy.

## Features

- 🤖 **AI-Powered Content Generation**: Uses ChatGPT to create unique blog posts
- 🔍 **Fact-Checking**: Validates generated content against original sources
- 🖼️ **AI Image Generation**: Creates thumbnails using Together AI
- 📝 **WordPress Integration**: Automatically publishes to WordPress
- ⏰ **Scheduled Execution**: Runs automatically every 2 hours using Render's built-in cron
- ✅ **Hallucination Prevention**: Ensures accuracy and prevents fake information

## Setup

### 1. Environment Variables

Create a `.env` file with your API keys (see `env.example` for reference):

```env
OPENAI_API_KEY=your_openai_api_key_here
TOGETHER_API_KEY=your_together_api_key_here
WP_SITE_URL=https://your-wordpress-site.com
WP_USERNAME=your_wordpress_username
WP_APP_PASSWORD=your_wordpress_application_password
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Locally

```bash
python ai_news_blogger_enhanced.py
```

## Free Hosting Options

### Option 1: Render (Recommended - Built-in Cron Jobs)

1. **Fork this repository** to your GitHub account
2. **Sign up** at [Render.com](https://render.com)
3. **Create a new Cron Job** service
4. **Connect your GitHub repo**
5. **Configure the service**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python ai_news_blogger_enhanced.py`
   - **Schedule**: `0 */2 * * *` (every 2 hours)
6. **Add environment variables** in Render dashboard:
   - `OPENAI_API_KEY` - Your OpenAI API key
   - `TOGETHER_API_KEY` - Your Together AI API key
   - `WP_SITE_URL` - Your WordPress site URL (e.g., https://your-site.com)
   - `WP_USERNAME` - Your WordPress username
   - `WP_APP_PASSWORD` - Your WordPress application password
7. **Deploy** - Render will automatically run the job every 2 hours

**Alternative: Use render.yaml (Auto-deploy)**
- The `render.yaml` file is already configured
- Just connect your GitHub repo and Render will auto-deploy
- Add environment variables in the dashboard

### Option 2: Railway

1. **Fork this repository** to your GitHub account
2. **Sign up** at [Railway.app](https://railway.app)
3. **Connect your GitHub repo**
4. **Add environment variables** in Railway dashboard:
   - `OPENAI_API_KEY`
   - `TOGETHER_API_KEY`
   - `WP_SITE_URL`
   - `WP_USERNAME`
   - `WP_APP_PASSWORD`
5. **Deploy** - Railway will automatically detect Python and deploy
6. **Set up cron job** in Railway dashboard to run every 2 hours

### Option 3: PythonAnywhere

1. **Sign up** at [PythonAnywhere.com](https://www.pythonanywhere.com)
2. **Upload your code** via Git or file upload
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Set up a scheduled task** in the Tasks tab:
   - Command: `python ai_news_blogger_enhanced.py`
   - Schedule: Every 2 hours

### Option 4: Heroku

1. **Install Heroku CLI**
2. **Login to Heroku**:
   ```bash
   heroku login
   ```
3. **Create Heroku app**:
   ```bash
   heroku create your-app-name
   ```
4. **Add environment variables**:
   ```bash
   heroku config:set OPENAI_API_KEY=your_key
   heroku config:set TOGETHER_API_KEY=your_key
   heroku config:set WP_SITE_URL=your_site_url
   heroku config:set WP_USERNAME=your_username
   heroku config:set WP_APP_PASSWORD=your_password
   ```
5. **Deploy**:
   ```bash
   git add .
   git commit -m "Initial deployment"
   git push heroku main
   ```
6. **Add scheduler add-on**:
   ```bash
   heroku addons:create scheduler:standard
   ```
7. **Set up cron job** in Heroku dashboard:
   - Command: `python ai_news_blogger_enhanced.py`
   - Frequency: Every 2 hours

## Environment Variables Setup

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | `sk-...` |
| `TOGETHER_API_KEY` | Your Together AI API key | `...` |
| `WP_SITE_URL` | Your WordPress site URL | `https://your-site.com` |
| `WP_USERNAME` | WordPress username | `admin` |
| `WP_APP_PASSWORD` | WordPress application password | `...` |

### How to Get These Values

#### 1. OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up/login
3. Go to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-`)

#### 2. Together AI API Key
1. Go to [Together AI](https://together.ai/)
2. Sign up/login
3. Go to API Keys section
4. Create a new API key
5. Copy the key

#### 3. WordPress Credentials
1. **Site URL**: Your WordPress site URL (e.g., `https://your-site.com`)
2. **Username**: Your WordPress admin username
3. **Application Password**:
   - Go to WordPress admin → Users → Profile
   - Scroll down to "Application Passwords"
   - Add new application password
   - Copy the generated password

### Setting Environment Variables in Render

1. **Go to your Render dashboard**
2. **Select your cron job service**
3. **Click on "Environment" tab**
4. **Add each variable**:
   - Click "Add Environment Variable"
   - Enter the variable name (e.g., `OPENAI_API_KEY`)
   - Enter the value
   - Click "Save Changes"
5. **Repeat for all 5 variables**

## Configuration

### RSS Feeds

The system currently monitors these RSS feeds:
- Artificial Intelligence News
- Science Daily (AI section)
- MIT Technology Review (AI section)

## Monitoring

The application logs all activities. Check the logs in your hosting platform's dashboard to monitor:
- Blog generation success/failure
- Validation results
- WordPress upload status
- Error messages

## Cost Considerations

- **Render**: 750 free hours/month (perfect for cron jobs)
- **Railway**: 500 free hours/month (enough for 2-hour intervals)
- **PythonAnywhere**: Free tier available
- **Heroku**: Limited free tier (may require paid plan)

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure environment variables are set correctly
2. **WordPress Upload Failures**: Check credentials and site URL
3. **Image Generation Failures**: Verify Together API key and quota
4. **Validation Failures**: Check if source articles are accessible

### Logs

All operations are logged with timestamps. Check your hosting platform's log viewer for detailed information about:
- RSS feed fetching
- Blog generation attempts
- Validation results
- WordPress uploads

## License

This project is open source and available under the MIT License. 