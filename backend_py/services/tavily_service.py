import os
from typing import List, Dict, Any
from tavily import TavilyClient
from ..utils.logger import log_api_call, log_error, log_success
from ..test_mode import is_test_mode, get_test_resources
import asyncio

class TavilyResourceService:
    def __init__(self):
        self.api_key = os.getenv("TAVILY_API_KEY")
        
        # Check if in test mode
        if is_test_mode():
            log_success("Tavily service initialized in test mode", "ResourceService")
            return
        
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not found in environment variables")
        
        self.client = TavilyClient(api_key=self.api_key)
        log_success("Tavily client initialized", "ResourceService")

    async def search_resources(self, query: str, subject: str = None, difficulty: str = None, 
                             resource_type: str = None, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for educational resources using Tavily API
        """
        try:
            log_api_call("tavily/search", "POST", query=query, subject=subject)
            
            # Check if in test mode
            if is_test_mode():
                log_success("Returning test resources", "ResourceService")
                return get_test_resources()
            
            # Build enhanced query with context
            enhanced_query = self._build_enhanced_query(query, subject, difficulty, resource_type)
            
            # Search with Tavily
            search_results = self.client.search(
                query=enhanced_query,
                max_results=max_results,
                search_depth="advanced",
                include_domains=[
                    "youtube.com", "coursera.org", "edx.org", "khanacademy.org",
                    "geeksforgeeks.org", "leetcode.com", "stackoverflow.com",
                    "docs.python.org", "developer.mozilla.org", "react.dev",
                    "arxiv.org", "ieee.org", "acm.org"
                ]
            )
            
            # Process and score results
            processed_results = self._process_search_results(search_results.get('results', []), 
                                                           subject, difficulty, resource_type)
            
            log_success(f"Found {len(processed_results)} resources", "ResourceService")
            return processed_results
            
        except Exception as e:
            log_error(e, "TavilyResourceService.search_resources")
            return []

    def _build_enhanced_query(self, query: str, subject: str = None, difficulty: str = None, 
                            resource_type: str = None) -> str:
        """Build enhanced search query with context"""
        
        base_query = query
        
        # Add subject context
        if subject and subject != "General":
            subject_keywords = {
                "DSA": "data structures algorithms programming",
                "OS": "operating systems computer science",
                "DBMS": "database management systems SQL",
                "CN": "computer networks networking",
                "SE": "software engineering development",
                "AI": "artificial intelligence machine learning",
                "ML": "machine learning data science",
                "Web Dev": "web development frontend backend",
                "Mobile Dev": "mobile development iOS Android"
            }
            base_query += f" {subject_keywords.get(subject, '')}"
        
        # Add difficulty context
        if difficulty:
            difficulty_terms = {
                "beginner": "tutorial basics introduction",
                "intermediate": "intermediate advanced concepts",
                "advanced": "advanced expert deep dive"
            }
            base_query += f" {difficulty_terms.get(difficulty, '')}"
        
        # Add resource type context
        if resource_type:
            type_terms = {
                "video": "video tutorial course",
                "course": "online course curriculum",
                "documentation": "documentation guide reference",
                "practice": "exercises problems practice",
                "paper": "research paper academic"
            }
            base_query += f" {type_terms.get(resource_type, '')}"
        
        return base_query

    def _process_search_results(self, results: List[Dict], subject: str = None, 
                              difficulty: str = None, resource_type: str = None) -> List[Dict[str, Any]]:
        """Process and score search results"""
        
        processed = []
        
        for result in results:
            try:
                # Extract basic info
                title = result.get('title', '')
                url = result.get('url', '')
                content = result.get('content', '')
                
                # Determine resource type
                detected_type = self._detect_resource_type(url, title, content)
                
                # Calculate quality score
                quality_score = self._calculate_quality_score(result, subject, difficulty, resource_type)
                
                # Determine difficulty level
                difficulty_level = self._detect_difficulty_level(content, title)
                
                # Extract relevant excerpts
                excerpts = self._extract_relevant_excerpts(content, 3)
                
                processed_result = {
                    "title": title,
                    "url": url,
                    "content": content[:500] + "..." if len(content) > 500 else content,
                    "excerpts": excerpts,
                    "resource_type": detected_type,
                    "difficulty_level": difficulty_level,
                    "quality_score": quality_score,
                    "relevance_score": self._calculate_relevance_score(content, subject),
                    "domain": self._extract_domain(url),
                    "last_updated": result.get('published_date', 'Unknown')
                }
                
                processed.append(processed_result)
                
            except Exception as e:
                log_error(e, f"Processing result: {result.get('title', 'Unknown')}")
                continue
        
        # Sort by quality score and relevance
        processed.sort(key=lambda x: (x['quality_score'], x['relevance_score']), reverse=True)
        
        return processed

    def _detect_resource_type(self, url: str, title: str, content: str) -> str:
        """Detect resource type from URL, title, and content"""
        
        url_lower = url.lower()
        title_lower = title.lower()
        content_lower = content.lower()
        
        if any(domain in url_lower for domain in ['youtube.com', 'vimeo.com']):
            return 'video'
        elif any(domain in url_lower for domain in ['coursera.org', 'edx.org', 'udemy.com']):
            return 'course'
        elif any(domain in url_lower for domain in ['docs.', 'developer.', '.dev']):
            return 'documentation'
        elif any(domain in url_lower for domain in ['leetcode.com', 'hackerrank.com', 'geeksforgeeks.org']):
            return 'practice'
        elif any(domain in url_lower for domain in ['arxiv.org', 'ieee.org', 'acm.org']):
            return 'paper'
        elif 'tutorial' in title_lower or 'guide' in title_lower:
            return 'documentation'
        elif 'course' in title_lower or 'curriculum' in title_lower:
            return 'course'
        elif 'exercise' in content_lower or 'problem' in content_lower:
            return 'practice'
        else:
            return 'general'

    def _calculate_quality_score(self, result: Dict, subject: str = None, 
                               difficulty: str = None, resource_type: str = None) -> float:
        """Calculate quality score based on various factors"""
        
        score = 0.0
        
        # Base score from Tavily
        score += result.get('score', 0) * 0.3
        
        # Title relevance
        title = result.get('title', '').lower()
        if subject and subject.lower() in title:
            score += 0.2
        
        # Content length (longer content generally better)
        content_length = len(result.get('content', ''))
        if content_length > 1000:
            score += 0.2
        elif content_length > 500:
            score += 0.1
        
        # Domain authority
        url = result.get('url', '').lower()
        authority_domains = [
            'youtube.com', 'coursera.org', 'edx.org', 'khanacademy.org',
            'geeksforgeeks.org', 'stackoverflow.com', 'docs.python.org',
            'developer.mozilla.org', 'react.dev', 'arxiv.org'
        ]
        
        if any(domain in url for domain in authority_domains):
            score += 0.2
        
        # Resource type match
        detected_type = self._detect_resource_type(url, title, result.get('content', ''))
        if resource_type and detected_type == resource_type:
            score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0

    def _detect_difficulty_level(self, content: str, title: str) -> str:
        """Detect difficulty level from content and title"""
        
        text = (content + " " + title).lower()
        
        beginner_keywords = ['beginner', 'basic', 'introduction', 'getting started', 'tutorial']
        intermediate_keywords = ['intermediate', 'advanced', 'deep dive', 'comprehensive']
        expert_keywords = ['expert', 'master', 'professional', 'enterprise']
        
        beginner_count = sum(1 for keyword in beginner_keywords if keyword in text)
        intermediate_count = sum(1 for keyword in intermediate_keywords if keyword in text)
        expert_count = sum(1 for keyword in expert_keywords if keyword in text)
        
        if expert_count > intermediate_count and expert_count > beginner_count:
            return 'advanced'
        elif intermediate_count > beginner_count:
            return 'intermediate'
        else:
            return 'beginner'

    def _extract_relevant_excerpts(self, content: str, max_excerpts: int = 3) -> List[str]:
        """Extract relevant excerpts from content"""
        
        sentences = content.split('. ')
        excerpts = []
        
        for sentence in sentences[:max_excerpts * 2]:  # Get more than needed for filtering
            if len(sentence.strip()) > 50:  # Only meaningful sentences
                excerpts.append(sentence.strip() + '.')
        
        return excerpts[:max_excerpts]

    def _calculate_relevance_score(self, content: str, subject: str = None) -> float:
        """Calculate relevance score based on subject"""
        
        if not subject or subject == "General":
            return 0.5
        
        content_lower = content.lower()
        
        subject_keywords = {
            "DSA": ['algorithm', 'data structure', 'programming', 'complexity'],
            "OS": ['operating system', 'process', 'memory', 'kernel'],
            "DBMS": ['database', 'sql', 'query', 'table'],
            "CN": ['network', 'protocol', 'tcp', 'ip'],
            "SE": ['software', 'development', 'engineering', 'architecture'],
            "AI": ['artificial intelligence', 'machine learning', 'neural'],
            "ML": ['machine learning', 'model', 'training', 'prediction'],
            "Web Dev": ['web', 'html', 'css', 'javascript', 'react'],
            "Mobile Dev": ['mobile', 'ios', 'android', 'app']
        }
        
        keywords = subject_keywords.get(subject, [])
        matches = sum(1 for keyword in keywords if keyword in content_lower)
        
        return min(matches / len(keywords) if keywords else 0, 1.0)

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return "unknown"

# Global instance - will be initialized when first accessed
tavily_service = None

def get_tavily_service():
    global tavily_service
    if tavily_service is None:
        tavily_service = TavilyResourceService()
    return tavily_service
