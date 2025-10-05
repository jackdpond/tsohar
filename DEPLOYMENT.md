# Deployment Guide

This guide explains how to deploy the BibleProject Pod-Search web app to Render.

## Prerequisites

1. **API Keys**: You'll need to set up API keys for:
   - OpenAI API (for embeddings)
   - Assembly AI API (for transcription)

2. **Database Files**: Ensure you have the following files in `scripts/database/`:
   - `bp_db.index` (FAISS index)
   - `bp_db.json` (transcript data)

## Render Deployment

### 1. Prepare Your Repository

The repository is already configured with:
- `Procfile` - Tells Render how to start the app
- `render.yaml` - Render-specific configuration
- `requirements.txt` - Python dependencies including gunicorn
- `site/app.py` - Production WSGI application

### 2. Deploy to Render

1. **Connect Repository**:
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub account and select this repository

2. **Configure Service**:
   - **Name**: `pod-search-app` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd site && gunicorn --bind 0.0.0.0:$PORT --timeout 120 --workers 2 app:app`

3. **Set Environment Variables**:
   In the Render dashboard, go to Environment and add:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `ASSEMBLY_API_KEY`: Your Assembly AI API key

4. **Deploy**:
   - Click "Create Web Service"
   - Render will automatically build and deploy your app

### 3. Database Files

**Database files are already configured with Git LFS**: The database files (`bp_db.index` and `bp_db.json`, ~902MB total) are stored using Git LFS and will be automatically downloaded during deployment.

**No additional action needed** - Render will automatically:
1. Download the Git LFS files during the build process
2. Place them in the correct location (`scripts/database/`)
3. The app will find them when it starts up

**If you need to update the database files**:
```bash
# Make changes to database files
git add scripts/database/
git commit -m "Update database files"
git push
```

### 4. Custom Domain (Optional)

1. In Render dashboard, go to your service settings
2. Click "Custom Domains"
3. Add your domain and follow the DNS instructions

## Local Development

To run locally with the same configuration as production:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the production server locally
cd site
python app.py
```

Visit `http://localhost:5000` to see the app.

## Architecture

The deployed app serves:
- **Static files**: HTML, CSS, JS, JSON files
- **Search API**: `/search` endpoint for semantic search
- **Health check**: `/health` endpoint

The app loads the FAISS vector database on startup and serves search results through the Flask API.

## Troubleshooting

### Common Issues:

1. **Database not found**: Ensure `bp_db.index` and `bp_db.json` are in the correct location
2. **API key errors**: Verify environment variables are set correctly in Render dashboard
3. **Timeout errors**: The app may take time to load the database on startup
4. **Memory issues**: Large databases may require upgrading to a higher Render plan

### Logs:
Check Render logs for any startup or runtime errors.

## Cost Considerations

- **Render Free Tier**: Limited to 750 hours/month, sleeps after inactivity
- **Render Starter Plan**: $7/month, always-on, better for production use
- **Database Size**: Large FAISS indices may require more memory

## Alternative: Cloudflare Pages + Workers

If you prefer Cloudflare, you could:
1. Deploy the frontend to Cloudflare Pages
2. Deploy the API to Cloudflare Workers (requires refactoring)
3. This would be more complex but potentially cheaper for high-traffic scenarios
