import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging
import json
import time
from bs4 import BeautifulSoup
import trafilatura
import re
from urllib.parse import urlparse, urljoin
import dateutil.parser

logger = logging.getLogger(__name__)

class PerplexityAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai/chat/completions"

    def generate_summary(self, content: str) -> str:
        """
        Generate article summary using Perplexity AI API with Sonar model
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

            # Make API request
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=45
            )

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

class ArticleFetcher:
    def __init__(self, perplexity_api_key: str = None):
        self.perplexity_api = PerplexityAPI(perplexity_api_key) if perplexity_api_key else None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
        }
        
    def is_article_page(self, url: str, html_content: str) -> bool:
        """
        Determine if a URL is an actual article page and not a search result, category, or home page
        """
        # Parse URL path
        parsed_url = urlparse(url)
        path = parsed_url.path.lower()
        
        # Common patterns for search, category, or tag pages
        search_patterns = [
            '/search', '/tag/', '/category/', '/topics/', 
            '/index', '/page/', '/author/', '/about/',
            '/contact', '/terms', '/privacy', '/feed/'
        ]
        
        # Check URL path first
        for pattern in search_patterns:
            if pattern in path:
                return False
                
        # Search results often have q= or query= in query params
        if 'q=' in parsed_url.query or 'query=' in parsed_url.query:
            return False
            
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Articles usually have an article tag or main content div
        article_element = soup.find(['article', 'main'])
        if article_element:
            return True
            
        # Articles typically have multiple paragraphs with substantial text
        paragraphs = soup.find_all('p')
        if len(paragraphs) >= 3:
            total_text = sum(len(p.get_text(strip=True)) for p in paragraphs)
            if total_text > 500:  # At least 500 characters of text
                return True
                
        # Articles often have a headline/title
        if soup.find(['h1', 'h2']):
            return True
            
        # If we can't determine, default to True and let other filtering catch bad content
        return True

    def extract_publication_date(self, url: str, html_content: str) -> str:
        """
        Try to extract publication date from article
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Try common meta tags first
            meta_tags = [
                ('meta[property="article:published_time"]', 'content'),
                ('meta[property="og:published_time"]', 'content'),
                ('meta[name="pubdate"]', 'content'),
                ('meta[name="publishdate"]', 'content'),
                ('meta[name="date"]', 'content'),
                ('meta[itemprop="datePublished"]', 'content')
            ]
            
            for selector, attr in meta_tags:
                tag = soup.select_one(selector)
                if tag and tag.get(attr):
                    try:
                        date_str = tag.get(attr)
                        parsed_date = dateutil.parser.parse(date_str)
                        return parsed_date.strftime('%Y-%m-%d')
                    except:
                        pass
            
            # Try looking for time tags
            time_tags = soup.find_all('time')
            for time_tag in time_tags:
                if time_tag.get('datetime'):
                    try:
                        date_str = time_tag.get('datetime')
                        parsed_date = dateutil.parser.parse(date_str)
                        return parsed_date.strftime('%Y-%m-%d')
                    except:
                        pass
            
            # Try looking for common date patterns in text
            date_elements = soup.select('span.date, div.date, p.date, .byline, .meta, .post-date, .published')
            for element in date_elements:
                text = element.get_text(strip=True)
                try:
                    parsed_date = dateutil.parser.parse(text, fuzzy=True)
                    return parsed_date.strftime('%Y-%m-%d')
                except:
                    pass
            
            # Default to current date
            return datetime.utcnow().strftime('%Y-%m-%d')
            
        except Exception as e:
            logger.error(f"Error extracting publication date: {str(e)}")
            return datetime.utcnow().strftime('%Y-%m-%d')

    def is_within_timeframe(self, date_str: str, timeframe: str) -> bool:
        """
        Check if a date is within the specified timeframe
        """
        try:
            # Parse article date
            article_date = datetime.strptime(date_str, '%Y-%m-%d')
            
            # Calculate the cutoff date based on timeframe
            today = datetime.utcnow()
            
            if timeframe == 'daily':
                cutoff_date = today - timedelta(days=1)
            elif timeframe == 'weekly':
                cutoff_date = today - timedelta(days=7)
            elif timeframe == 'fortnightly':
                cutoff_date = today - timedelta(days=14)
            elif timeframe == 'monthly':
                cutoff_date = today - timedelta(days=30)
            elif timeframe == 'quarterly':
                cutoff_date = today - timedelta(days=90)
            else:
                cutoff_date = today - timedelta(days=7)  # Default to weekly
            
            # Check if article date is on or after the cutoff date
            return article_date >= cutoff_date
            
        except Exception as e:
            logger.error(f"Error checking timeframe for date {date_str}: {str(e)}")
            return True  # Default to including if we can't parse the date

    def fetch_article_content(self, url: str, timeframe: str) -> Dict[str, Any]:
        """
        Fetch article content with improved filtering
        """
        try:
            # Make direct request
            response = requests.get(url, headers=self.headers, timeout=10)
            if not response.ok:
                logger.warning(f"Failed to fetch {url}, status: {response.status_code}")
                return None
            
            # Check if this is actually an article page and not search results
            if not self.is_article_page(url, response.text):
                logger.info(f"Skipping non-article page: {url}")
                return None
                
            # Extract publication date
            pub_date = self.extract_publication_date(url, response.text)
            
            # Check if within timeframe
            if not self.is_within_timeframe(pub_date, timeframe):
                logger.info(f"Skipping article outside timeframe: {url}, date: {pub_date}")
                return None
                
            # Extract with trafilatura
            content = trafilatura.extract(response.text, include_links=False, include_images=False)
            
            # If trafilatura fails, use BeautifulSoup as fallback
            if not content or len(content) < 100:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Try known article containers
                article_containers = soup.find_all(['article', 'main', 'div'], class_=lambda c: c and any(term in str(c).lower() for term in ['content', 'article', 'body', 'main', 'text']))
                
                if article_containers:
                    for container in article_containers:
                        # Remove navigation, ads, etc.
                        for tag in container.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                            tag.decompose()
                        
                        extracted_content = container.get_text(separator="\n", strip=True)
                        if len(extracted_content) > 200:
                            content = extracted_content
                            break
                
                # If still no content, try paragraphs
                if not content or len(content) < 100:
                    paragraphs = [p.get_text(strip=True) for p in soup.find_all('p') if len(p.get_text(strip=True)) > 40]
                    if paragraphs:
                        content = "\n\n".join(paragraphs)
            
            # Get title
            title = ""
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try h1 first
            h1 = soup.find('h1')
            if h1:
                title = h1.get_text(strip=True)
            
            # Fallback to title tag
            if not title:
                title_tag = soup.find('title')
                if title_tag:
                    title = title_tag.get_text(strip=True)
            
            # Last resort: use URL
            if not title:
                title = url.split('/')[-1].replace('-', ' ').replace('_', ' ').title()
            
            # Validate content
            if not content or len(content) < 200:
                logger.warning(f"Insufficient content from {url}, length: {len(content) if content else 0} chars")
                return None
                
            logger.info(f"Successfully extracted article from {url}, date: {pub_date}, length: {len(content)} chars")
            
            return {
                'title': title,
                'content': content,
                'url': url,
                'date': pub_date
            }
                
        except Exception as e:
            logger.error(f"Error fetching article from {url}: {str(e)}")
            return None

    def find_links_containing_keyword(self, url: str, keyword: str) -> List[str]:
        """Find links on a page that contain a specific keyword"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if not response.ok:
                return []
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Parse base URL for relative links
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            keyword_links = []
            
            # Find links containing the keyword
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                
                # Process the URL
                if href.startswith('/'):
                    full_url = urljoin(base_url, href)
                elif href.startswith('http'):
                    full_url = href
                else:
                    full_url = urljoin(url, href)
                
                # Skip non-HTTP URLs
                if not full_url.startswith('http'):
                    continue
                    
                # Skip common non-article paths
                skip_patterns = ['.pdf', '.jpg', '.png', '.gif', '/wp-content/', '/static/', 
                                '/images/', '/css/', '/js/', '/login', '/register', '/sitemap']
                if any(pattern in full_url.lower() for pattern in skip_patterns):
                    continue
                
                # Check if link is from same domain
                if parsed_url.netloc in urlparse(full_url).netloc:
                    # Check if keyword is in URL or link text
                    link_text = a_tag.get_text(strip=True).lower()
                    if keyword.lower() in full_url.lower() or keyword.lower() in link_text:
                        keyword_links.append(full_url)
            
            # Remove duplicates
            return list(set(keyword_links))
                
        except Exception as e:
            logger.error(f"Error finding links on {url} with keyword {keyword}: {str(e)}")
            return []

    def find_articles_on_site(self, url: str, topic: str, timeframe: str) -> List[Dict[str, Any]]:
        """Find articles on a website related to a specific topic within timeframe"""
        articles = []
        
        try:
            # Parse the URL
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            # First check the base URL
            relevant_links = self.find_links_containing_keyword(base_url, topic)
            
            # If not enough links, check if the site has a search function
            if len(relevant_links) < 3:
                search_paths = [
                    f"/search?q={topic}",
                    f"/search?query={topic}",
                    f"/search/{topic}",
                    f"/?s={topic}"
                ]
                
                for path in search_paths:
                    search_url = urljoin(base_url, path)
                    search_links = self.find_links_containing_keyword(search_url, topic)
                    relevant_links.extend(search_links)
                    if len(relevant_links) >= 5:
                        break
            
            # Process the most relevant links
            unique_links = list(set(relevant_links))[:10]  # Increase limit to find more candidates
            
            for link in unique_links:
                # Check if we have enough articles
                if len(articles) >= 5:
                    break
                    
                article = self.fetch_article_content(link, timeframe)
                if article and article['content'] and len(article['content']) > 200:
                    articles.append(article)
            
            # If still no articles, check the provided URL directly
            if not articles and url != base_url:
                direct_article = self.fetch_article_content(url, timeframe)
                if direct_article and direct_article['content'] and len(direct_article['content']) > 200:
                    articles.append(direct_article)
            
            return articles
                
        except Exception as e:
            logger.error(f"Error finding articles on {url} about {topic}: {str(e)}")
            return []

    def process_articles(self, source_urls: List[str], area_of_interest: str, timeframe: str) -> List[Dict[str, Any]]:
        """
        Find articles related to the area of interest on the provided sources 
        that were published within the specified timeframe
        """
        all_articles = []
        sources_used = []
        
        # Search each source for relevant articles
        for source_url in source_urls:
            try:
                logger.info(f"Searching for articles about '{area_of_interest}' on {source_url} within {timeframe} timeframe")
                articles = self.find_articles_on_site(source_url, area_of_interest, timeframe)
                
                if articles:
                    logger.info(f"Found {len(articles)} relevant articles on {source_url}")
                    all_articles.extend(articles)
                    
                    # Add to sources used
                    for article in articles:
                        sources_used.append({
                            'title': article['title'],
                            'url': article['url']
                        })
                else:
                    logger.warning(f"No relevant articles found on {source_url} within timeframe {timeframe}")
            except Exception as e:
                logger.error(f"Error processing source {source_url}: {str(e)}")
        
        # If no articles found
        if not all_articles:
            logger.warning(f"No articles found on any source for topic: {area_of_interest} within timeframe {timeframe}")
            return []
        
        # Combine content for summarization
        combined_content = f"Based on these articles about {area_of_interest}, provide a comprehensive summary:\n\n"
        
        for idx, article in enumerate(all_articles, 1):
            # Add article title and excerpt to combined content
            combined_content += f"Article {idx}: {article['title']}\n\n"
            content_excerpt = article['content'][:2000] if len(article['content']) > 2000 else article['content']
            combined_content += f"{content_excerpt}\n\n"
        
        # Generate summary
        if self.perplexity_api:
            summary = self.perplexity_api.generate_summary(combined_content)
            logger.info(f"Generated summary for {area_of_interest} using {len(all_articles)} articles")
        else:
            summary = "• Perplexity API key not configured\n• Please add your API key to enable summarization"
            logger.error("Failed to generate summary: Perplexity API key not configured")
        
        # Create summary object
        summary_object = {
            'title': f"Summary: {area_of_interest}",
            'url': "#",
            'summary': summary,
            'source': f"{len(sources_used)} Articles",
            'date': datetime.utcnow().strftime('%Y-%m-%d'),
            'sources_used': sources_used
        }
        
        return [summary_object]