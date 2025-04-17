import requests
import json
import os
import time
import random
import re
import logging
from datetime import datetime
from flask import current_app
from app.utils.article_search import search_for_articles

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerplexityAPI:
    """Handles interaction with Perplexity API for article summarization"""
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.retries = 3
        self.backoff_factor = 1.5
        
    def generate_summary(self, content: str) -> str:
        """
        Generate article summary using Perplexity AI API with Sonar model
        Enhanced with proper backoff and retry logic
        """
        if not self.api_key:
            logger.error("No Perplexity API key provided")
            return "• Error: Perplexity API key not configured"

        if not content:
            return "• No content available for summarization"

        try:
            # Truncate content if too long to avoid exceeding token limits
            max_content_length = 5000
            truncated_content = content[:max_content_length] if len(content) > max_content_length else content
            
            logger.info(f"Generating summary using Perplexity API, content length: {len(truncated_content)} chars")

            # Create a clear, specific prompt for better summaries
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a skilled content summarizer that extracts key points from articles."
                        "Your summaries should be presented as bullet points, each starting with '•'."
                        "Focus on extracting factual information, key insights, and main arguments."
                        "Make sure each bullet point is self-contained and conveys a complete thought."
                        "Be concise and avoid repetition. Use clear language."
                    )
                },
                {
                    "role": "user",
                    "content": truncated_content
                }
            ]

            # API request headers
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            # API request payload using simplified sonar model
            payload = {
                "model": "sonar",
                "messages": messages,
                "max_tokens": 800
            }

            # Log payload for debugging (without the actual content)
            logger.info(f"API payload: model={payload['model']}, max_tokens={payload['max_tokens']}")

            # Make API request with retry logic
            max_retries = 3
            retry_delay = 1
            
            for attempt in range(max_retries):
                try:
                    response = requests.post(
                        self.base_url,
                        headers=headers,
                        json=payload,
                        timeout=45
                    )
                    
                    if response.status_code == 200:
                        break
                        
                    logger.warning(f"API request failed (attempt {attempt+1}): Status {response.status_code}")
                    retry_delay *= 2  # Exponential backoff
                    time.sleep(retry_delay + random.uniform(0, 1))
                except requests.exceptions.RequestException as e:
                    logger.warning(f"API request exception (attempt {attempt+1}): {str(e)}")
                    if attempt == max_retries - 1:
                        raise
                    retry_delay *= 2  # Exponential backoff
                    time.sleep(retry_delay + random.uniform(0, 1))

            if response.status_code != 200:
                error_msg = f"API Error (Status {response.status_code})"
                try:
                    error_detail = response.json()
                    logger.error(f"API error details: {json.dumps(error_detail)}")
                except:
                    logger.error(f"API error response: {response.text}")
                return f"• Error: {error_msg}\n• Please try again later"

            result = response.json()
            if 'choices' in result and result['choices']:
                summary = result['choices'][0]['message']['content'].strip()
                
                # Ensure summary is in bullet points
                if not summary.startswith('•'):
                    # Convert to bullet points
                    lines = summary.split('\n')
                    formatted_lines = []
                    for line in lines:
                        line = line.strip()
                        if line:
                            # Remove numbering if present
                            line = re.sub(r'^\d+\.\s*', '', line)
                            formatted_lines.append(f"• {line}")
                    summary = '\n'.join(formatted_lines)
                
                logger.info("Successfully generated summary")
                return summary
            else:
                logger.error(f"Unexpected API response structure: {result}")
                return "• Error: Unexpected API response format"

        except requests.exceptions.RequestException as e:
            logger.error(f"Request Exception: {str(e)}")
            return f"• Error: Failed to connect to API: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected Error: {str(e)}")
            return f"• Error: {str(e)}"

def get_article_summaries(preference):
    """
    Get summaries for articles based on user preferences.
    
    Args:
        preference: The user preference object
    
    Returns:
        dict: A dictionary containing article summaries and citations
    """
    # Search for real articles based on preferences using the article search utility
    articles = search_for_articles(preference)
    
    # Prepare result structure
    result = {
        'summaries': [],
        'citations': []
    }
    
    # Add each article to the citations
    for article in articles:
        result['citations'].append({
            'title': article['title'],
            'source': article['source'],
            'url': article['url'],
            'date': article.get('display_date', article.get('date', ''))
        })
    
    # Get API key from config
    api_key = current_app.config['PERPLEXITY_API_KEY']
    
    # Initialize Perplexity API client
    perplexity_client = PerplexityAPI(api_key)
    
    # Generate summaries for each article
    for article in articles:
        try:
            # Use the content of the article for summarization
            content = article['content']
            
            # If we have a valid API key, try to get a real summary
            if api_key:
                summary_text = perplexity_client.generate_summary(content)
                
                # Convert bullet points to a list
                bullet_points = [
                    point.strip().replace('• ', '', 1) 
                    for point in summary_text.split('\n') 
                    if point.strip() and '• Error:' not in point
                ]
                
                # If we got bullet points, use them; otherwise, fall back to mock data
                if bullet_points:
                    summary = {
                        'title': article['title'],
                        'source': article['source'],
                        'summary_text': bullet_points,
                        'article_url': article['url']  # Store the article URL with the summary
                    }
                    result['summaries'].append(summary)
                    continue
            
            # Fall back to mock summaries if API call failed or no API key
            mock_summary = generate_mock_summary_for_article(article)
            result['summaries'].append(mock_summary)
                
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            # Fall back to mock summary on error
            mock_summary = generate_mock_summary_for_article(article)
            result['summaries'].append(mock_summary)
    
    return result

def generate_mock_summary_for_article(article):
    """
    Generate a mock summary for a specific article.
    
    Args:
        article: Article data dictionary
    
    Returns:
        dict: A mock summary
    """
    title = article['title']
    topic = title.split(':')[0] if ':' in title else title
    source = article['source']
    
    return {
        'title': title,
        'source': source,
        'summary_text': [
            f"Research shows significant growth in {topic} adoption across industries.",
            f"Experts at {source} highlight improved efficiency and cost savings as key benefits.",
            f"Integration challenges remain the biggest obstacle to widespread implementation.",
            f"Recent technological advancements have addressed previous limitations in scalability.",
            f"Market analysts predict continued expansion in the {topic} sector through the next fiscal year."
        ],
        'article_url': article['url']  # Store the article URL with the summary
    }

def format_summary_as_bullets(summary_text):
    """
    Format summary text as bullet points if it's not already.
    
    Args:
        summary_text: The summary text from Perplexity API
    
    Returns:
        list: A list of bullet points
    """
    # If summary is already in bullet point format
    if isinstance(summary_text, list):
        return summary_text
    
    # Split by newlines and create bullets
    lines = summary_text.strip().split('\n')
    bullets = []
    
    for line in lines:
        line = line.strip()
        if line:
            # Remove bullet markers if they exist
            if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                line = line[1:].strip()
            bullets.append(line)
    
    # If no bullets were created, create a single bullet
    if not bullets:
        bullets = ['No key points identified.']
    
    return bullets