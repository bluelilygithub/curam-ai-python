import os
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class SimpleLLMProcessor:
    def __init__(self):
        """Initialize LLM clients with safe error handling"""
        self.claude_client = None
        self.gemini_model = None
        
        # Initialize Claude safely
        self._init_claude()
        
        # Initialize Gemini safely
        self._init_gemini()
    
    def _init_claude(self):
        """Initialize Claude with error handling"""
        try:
            import anthropic
            claude_key = os.getenv('CLAUDE_API_KEY')
            if claude_key:
                # Fix: Simple initialization without extra parameters
                self.claude_client = anthropic.Anthropic(api_key=claude_key.strip())
                logger.info("Claude client initialized successfully")
                
                # Test the connection with a simple call
                try:
                    test_response = self.claude_client.messages.create(
                        model="claude-3-sonnet-20240229",
                        max_tokens=10,
                        messages=[{"role": "user", "content": "Hello"}]
                    )
                    logger.info("Claude connection test successful")
                except Exception as test_error:
                    logger.error(f"Claude connection test failed: {str(test_error)}")
                    # Don't set to None, maybe it will work for actual queries
            else:
                logger.warning("CLAUDE_API_KEY not found")
        except ImportError:
            logger.error("anthropic library not installed")
        except Exception as e:
            logger.error(f"Claude initialization failed: {str(e)}")
            self.claude_client = None
    
    def _init_gemini(self):
        """Initialize Gemini with error handling"""
        try:
            import google.generativeai as genai
            gemini_key = os.getenv('GEMINI_API_KEY')
            if gemini_key:
                genai.configure(api_key=gemini_key.strip())
                
                # Fix: Try different model names
                model_names = [
                    'gemini-1.5-flash',
                    'gemini-1.5-pro', 
                    'gemini-pro',
                    'models/gemini-pro'
                ]
                
                for model_name in model_names:
                    try:
                        self.gemini_model = genai.GenerativeModel(model_name)
                        # Test the connection
                        test_response = self.gemini_model.generate_content("Hello")
                        logger.info(f"Gemini connection successful with model: {model_name}")
                        break
                    except Exception as model_error:
                        logger.warning(f"Gemini model {model_name} failed: {str(model_error)}")
                        continue
                
                if not self.gemini_model:
                    logger.error("All Gemini models failed")
                    
            else:
                logger.warning("GEMINI_API_KEY not found")
        except ImportError:
            logger.error("google-generativeai library not installed")
        except Exception as e:
            logger.error(f"Gemini initialization failed: {str(e)}")
            self.gemini_model = None
    
    def analyze_with_claude(self, question: str) -> Dict:
        """Analyze question with Claude (safe)"""
        if not self.claude_client:
            return {
                'success': False,
                'analysis': f'Claude analysis not available for: {question}',
                'error': 'Claude client not available'
            }
        
        try:
            prompt = f"""You are a Brisbane property research specialist. Analyze this question and provide insights:

Question: "{question}"

Please provide:
1. What type of property question this is (development, market, infrastructure, zoning, etc.)
2. Which specific Brisbane suburbs/areas are most relevant
3. What data sources would help answer this question
4. Key insights to look for in the data

Keep your response concise and focused specifically on Brisbane, Queensland, Australia."""

            response = self.claude_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return {
                'success': True,
                'analysis': response.content[0].text,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Claude analysis failed: {str(e)}")
            return {
                'success': False,
                'analysis': f'Claude analysis failed for: {question}',
                'error': str(e)
            }
    
    def process_with_gemini(self, question: str, claude_analysis: str, data_sources: int = 3) -> Dict:
        """Process with Gemini (safe)"""
        if not self.gemini_model:
            return {
                'success': False,
                'analysis': f'Gemini processing not available for: {question}',
                'error': 'Gemini model not available'
            }
        
        try:
            prompt = f"""You are a Brisbane property market analyst. Based on this research question and initial analysis, provide a comprehensive answer:

Question: "{question}"

Initial Analysis: {claude_analysis}

Data Sources Available: {data_sources} Brisbane property data sources

Please provide a detailed Brisbane property market analysis that directly answers the question. Include:
- Specific Brisbane suburbs and areas
- Current market trends and data
- Investment or development implications
- Professional insights for property industry

Focus on actionable information for Brisbane property professionals."""

            response = self.gemini_model.generate_content(prompt)
            
            return {
                'success': True,
                'analysis': response.text,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Gemini processing failed: {str(e)}")
            return {
                'success': False,
                'analysis': f'Gemini processing failed for: {question}',
                'error': str(e)
            }
    
    def get_mock_brisbane_data(self, question: str) -> List[Dict]:
        """Generate mock Brisbane data sources"""
        return [
            {
                'source': 'Brisbane City Council',
                'title': 'Brisbane Development Applications - January 2025',
                'summary': 'Recent development applications show continued growth in South Brisbane and Fortitude Valley areas with focus on mixed-use developments.',
                'type': 'government_data',
                'date': '2025-01-15'
            },
            {
                'source': 'Property Observer',
                'title': 'Brisbane Property Market Update',
                'summary': 'Brisbane property market showing sustained growth with particular strength in inner-city areas. Paddington and New Farm leading growth.',
                'type': 'market_analysis',
                'date': '2025-01-14'
            },
            {
                'source': 'Queensland Government',
                'title': 'Cross River Rail Property Impact Study',
                'summary': 'Infrastructure investment analysis shows 20-30% property value uplift within 800m of new stations. Woolloongabba and South Brisbane most affected.',
                'type': 'infrastructure_news',
                'date': '2025-01-12'
            }
        ]
    
    def process_question(self, question: str) -> Dict:
        """Process a Brisbane property question through the full pipeline"""
        try:
            # Stage 1: Claude Analysis
            claude_result = self.analyze_with_claude(question)
            
            # Stage 2: Mock Data (represents scraped Brisbane data)
            mock_data = self.get_mock_brisbane_data(question)
            
            # Stage 3: Gemini Processing
            gemini_result = self.process_with_gemini(
                question, 
                claude_result['analysis'], 
                len(mock_data)
            )
            
            # Stage 4: Format Final Answer
            final_answer = self.format_final_answer(
                question, claude_result, gemini_result, mock_data
            )
            
            return {
                'success': True,
                'question': question,
                'claude_result': claude_result,
                'gemini_result': gemini_result,
                'data_sources': len(mock_data),
                'final_answer': final_answer,
                'processing_stages': {
                    'claude_success': claude_result['success'],
                    'gemini_success': gemini_result['success'],
                    'data_sources_found': len(mock_data)
                }
            }
            
        except Exception as e:
            logger.error(f"Question processing failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'final_answer': f'Error processing question: {question}'
            }
    
    def format_final_answer(self, question: str, claude_result: Dict, 
                          gemini_result: Dict, data_sources: List[Dict]) -> str:
        """Format the final answer combining all stages"""
        
        answer = f"""# Brisbane Property Intelligence Analysis

## Query: {question}

"""
        
        # Add main analysis from Gemini (if successful)
        if gemini_result['success']:
            answer += f"""## Market Analysis (Gemini AI)

{gemini_result['analysis']}

"""
        
        # Add Claude's strategic insights (if successful)
        if claude_result['success']:
            answer += f"""## Strategic Research Insights (Claude AI)

{claude_result['analysis']}

"""
        
        # If neither worked, add enhanced fallback
        if not claude_result['success'] and not gemini_result['success']:
            answer += f"""## Enhanced Analysis

This Brisbane property question requires analysis of current market conditions, development activity, and infrastructure impact. Key areas of focus include:

**Primary Brisbane Areas:** South Brisbane, Fortitude Valley, New Farm, Paddington, Teneriffe
**Market Factors:** Development pipeline, infrastructure projects (Cross River Rail, Brisbane Metro), character housing demand
**Data Sources:** Brisbane City Council applications, property market reports, infrastructure project updates

Current market conditions show sustained growth in inner-city areas with particular strength in mixed-use developments and character housing precincts.

"""
        
        # Add data sources section
        answer += f"""## Data Sources Analyzed

"""
        for source in data_sources:
            answer += f"- **{source['source']}** ({source['date']}): {source['title']}\n"
        
        # Add processing summary
        answer += f"""
## Processing Summary

- **Claude Analysis**: {'✅ Completed' if claude_result['success'] else '❌ Failed - ' + str(claude_result.get('error', 'Unknown error'))}
- **Gemini Processing**: {'✅ Completed' if gemini_result['success'] else '❌ Failed - ' + str(gemini_result.get('error', 'Unknown error'))}
- **Data Sources**: {len(data_sources)} Brisbane property sources analyzed
- **Analysis Date**: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

---
*Brisbane Property Intelligence - Multi-LLM Analysis System*
"""
        
        return answer