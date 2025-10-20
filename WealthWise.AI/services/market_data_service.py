"""
Market Data Service for Financial News and Market Information

This service integrates with external APIs to provide real-time market data,
financial news, and economic indicators for the AI recommendation system.
"""

import asyncio
import logging
import aiohttp
import yfinance as yf
import pandas as pd
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
import json
import numpy as np

logger = logging.getLogger(__name__)

class MarketDataService:
    """
    Service for fetching and processing market data from multiple sources
    """

    def __init__(self):
        self.session = None
        self._is_ready = False
        self.data_cache = {}
        self.cache_duration = 300  # 5 minutes cache

        # API endpoints (configure with your API keys)
        self.api_endpoints = {
            'alpha_vantage': 'https://www.alphavantage.co/query',
            'finnhub': 'https://finnhub.io/api/v1',
            'newsapi': 'https://newsapi.org/v2/everything',
            'yahoo_finance': 'https://query1.finance.yahoo.com/v8/finance/chart'
        }

        # API keys (set via environment variables)
        import os
        self.api_keys = {
            'alpha_vantage': os.getenv('ALPHA_VANTAGE_API_KEY'),
            'finnhub': os.getenv('FINNHUB_API_KEY'),
            'newsapi': os.getenv('NEWS_API_KEY')
        }

    async def initialize(self):
        """Initialize the market data service"""
        try:
            self.session = aiohttp.ClientSession()

            # Test basic connectivity
            await self._test_connectivity()

            self._is_ready = True
            logger.info("Market data service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize market data service: {e}")
            self._is_ready = False

    def is_ready(self) -> bool:
        """Check if service is ready"""
        return self._is_ready and self.session is not None

    async def get_market_data(self, symbols: List[str], timeframe: str = "1M", 
                            include_technical: bool = True, 
                            include_fundamental: bool = True) -> Dict[str, Any]:
        """
        Get comprehensive market data for specified symbols
        """
        try:
            cache_key = f"market_data_{'-'.join(symbols)}_{timeframe}"

            # Check cache first
            if cache_key in self.data_cache:
                cache_data = self.data_cache[cache_key]
                if datetime.utcnow().timestamp() - cache_data['timestamp'] < self.cache_duration:
                    return cache_data['data']

            market_data = {
                'symbols': symbols,
                'timeframe': timeframe,
                'price_data': {},
                'technical_indicators': {},
                'fundamental_data': {},
                'market_metrics': {},
                'sector_data': {},
                'timestamp': datetime.utcnow().isoformat()
            }

            # Fetch price data for each symbol
            for symbol in symbols[:10]:  # Limit to 10 symbols
                try:
                    # Get price data using yfinance (free and reliable)
                    ticker = yf.Ticker(symbol)

                    # Historical price data
                    period_map = {
                        '1D': '1d', '1W': '5d', '1M': '1mo', 
                        '3M': '3mo', '6M': '6mo', '1Y': '1y'
                    }
                    hist_data = ticker.history(period=period_map.get(timeframe, '1mo'))

                    if not hist_data.empty:
                        # Basic price metrics
                        current_price = hist_data['Close'].iloc[-1]
                        price_change = hist_data['Close'].iloc[-1] - hist_data['Close'].iloc[0]
                        price_change_pct = (price_change / hist_data['Close'].iloc[0]) * 100

                        market_data['price_data'][symbol] = {
                            'current_price': current_price,
                            'price_change': price_change,
                            'price_change_pct': price_change_pct,
                            'volume': hist_data['Volume'].iloc[-1],
                            'high_52w': hist_data['High'].max(),
                            'low_52w': hist_data['Low'].min(),
                            'avg_volume': hist_data['Volume'].mean()
                        }

                        # Technical indicators
                        if include_technical:
                            market_data['technical_indicators'][symbol] = self._calculate_technical_indicators(hist_data)

                        # Fundamental data
                        if include_fundamental:
                            try:
                                info = ticker.info
                                market_data['fundamental_data'][symbol] = {
                                    'market_cap': info.get('marketCap', 0),
                                    'pe_ratio': info.get('trailingPE', 0),
                                    'dividend_yield': info.get('dividendYield', 0),
                                    'sector': info.get('sector', 'Unknown'),
                                    'industry': info.get('industry', 'Unknown')
                                }
                            except:
                                market_data['fundamental_data'][symbol] = {}

                except Exception as e:
                    logger.warning(f"Failed to fetch data for {symbol}: {e}")
                    continue

            # Add market-wide metrics
            market_data['market_metrics'] = await self._get_market_metrics()

            # Cache the result
            self.data_cache[cache_key] = {
                'data': market_data,
                'timestamp': datetime.utcnow().timestamp()
            }

            return market_data

        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            return self._get_fallback_market_data(symbols)

    async def get_financial_news(self, sources: List[str], keywords: Optional[List[str]] = None,
                               date_from: date = None, date_to: date = None) -> List[Dict[str, Any]]:
        """
        Fetch financial news from specified sources
        """
        try:
            if not date_from:
                date_from = date.today() - timedelta(days=7)
            if not date_to:
                date_to = date.today()

            news_data = []

            # Try to fetch from NewsAPI if available
            if self.api_keys.get('newsapi'):
                try:
                    news_data = await self._fetch_news_from_api(sources, keywords, date_from, date_to)
                except Exception as e:
                    logger.warning(f"Failed to fetch news from API: {e}")

            # Fallback to simulated news data for demo
            if not news_data:
                news_data = self._generate_sample_news(sources, keywords)

            return news_data

        except Exception as e:
            logger.error(f"Error fetching financial news: {e}")
            return self._generate_sample_news(sources, keywords or [])

    async def get_sector_data(self, sectors: List[str], analysis_depth: str = "comprehensive") -> Dict[str, Any]:
        """
        Get sector-specific performance and analysis data
        """
        try:
            sector_data = {
                'sectors': sectors,
                'analysis_depth': analysis_depth,
                'sector_performance': {},
                'sector_metrics': {},
                'top_performers': {},
                'sector_outlook': {},
                'timestamp': datetime.utcnow().isoformat()
            }

            # Map sectors to representative ETFs/indices
            sector_etfs = {
                'technology': 'XLK',
                'healthcare': 'XLV', 
                'finance': 'XLF',
                'energy': 'XLE',
                'consumer_goods': 'XLY',
                'utilities': 'XLU',
                'materials': 'XLB',
                'industrials': 'XLI',
                'real_estate': 'XLRE',
                'telecommunications': 'XLC'
            }

            # Fetch performance data for each sector
            for sector in sectors:
                etf_symbol = sector_etfs.get(sector.lower())
                if etf_symbol:
                    try:
                        ticker = yf.Ticker(etf_symbol)
                        hist_data = ticker.history(period='1y')

                        if not hist_data.empty:
                            # Calculate sector performance metrics
                            ytd_return = ((hist_data['Close'].iloc[-1] / hist_data['Close'].iloc[0]) - 1) * 100
                            volatility = hist_data['Close'].pct_change().std() * np.sqrt(252) * 100

                            sector_data['sector_performance'][sector] = {
                                'ytd_return': ytd_return,
                                'volatility': volatility,
                                'current_price': hist_data['Close'].iloc[-1],
                                'volume': hist_data['Volume'].iloc[-1]
                            }
                    except Exception as e:
                        logger.warning(f"Failed to fetch sector data for {sector}: {e}")

            return sector_data

        except Exception as e:
            logger.error(f"Error fetching sector data: {e}")
            return {'sectors': sectors, 'error': str(e)}

    def _calculate_technical_indicators(self, price_data: pd.DataFrame) -> Dict[str, float]:
        """Calculate basic technical indicators"""
        try:
            indicators = {}

            # Simple Moving Averages
            if len(price_data) >= 20:
                indicators['sma_20'] = price_data['Close'].rolling(20).mean().iloc[-1]
            if len(price_data) >= 50:
                indicators['sma_50'] = price_data['Close'].rolling(50).mean().iloc[-1]

            # RSI (Relative Strength Index)
            delta = price_data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            indicators['rsi'] = 100 - (100 / (1 + rs)).iloc[-1] if not rs.iloc[-1] == 0 else 50

            # Volatility
            indicators['volatility'] = price_data['Close'].pct_change().std() * 100

            return indicators

        except Exception as e:
            logger.warning(f"Error calculating technical indicators: {e}")
            return {}

    async def _get_market_metrics(self) -> Dict[str, Any]:
        """Get overall market metrics"""
        try:
            # Fetch major indices
            indices = {
                'SPY': 'S&P 500',
                'QQQ': 'NASDAQ 100', 
                'DIA': 'Dow Jones',
                'VTI': 'Total Stock Market'
            }

            market_metrics = {}

            for symbol, name in indices.items():
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period='5d')

                    if not hist.empty:
                        current = hist['Close'].iloc[-1]
                        previous = hist['Close'].iloc[0]
                        change_pct = ((current / previous) - 1) * 100

                        market_metrics[symbol] = {
                            'name': name,
                            'current_price': current,
                            'change_pct': change_pct,
                            'volume': hist['Volume'].iloc[-1]
                        }
                except:
                    continue

            return market_metrics

        except Exception as e:
            logger.warning(f"Error fetching market metrics: {e}")
            return {}

    def _generate_sample_news(self, sources: List[str], keywords: List[str]) -> List[Dict[str, Any]]:
        """Generate sample news data for demo purposes"""
        sample_news = [
            {
                'headline': 'Federal Reserve Announces Interest Rate Decision',
                'source': 'Reuters',
                'published_date': datetime.utcnow() - timedelta(hours=2),
                'content': 'The Federal Reserve announced its latest interest rate decision...',
                'sentiment': 0.1,
                'relevance': 0.9,
                'symbols': ['SPY', 'QQQ']
            },
            {
                'headline': 'Technology Sector Shows Strong Earnings Growth',
                'source': 'Bloomberg',
                'published_date': datetime.utcnow() - timedelta(hours=6),
                'content': 'Major technology companies reported stronger than expected earnings...',
                'sentiment': 0.7,
                'relevance': 0.8,
                'symbols': ['AAPL', 'MSFT', 'GOOGL']
            },
            {
                'headline': 'Healthcare Innovation Drives Market Optimism',
                'source': 'Financial Times',
                'published_date': datetime.utcnow() - timedelta(hours=12),
                'content': 'New breakthrough in healthcare technology sparks investor interest...',
                'sentiment': 0.6,
                'relevance': 0.7,
                'symbols': ['JNJ', 'PFE', 'UNH']
            }
        ]

        # Filter by keywords if provided
        if keywords:
            filtered_news = []
            for news in sample_news:
                if any(keyword.lower() in news['headline'].lower() or 
                      keyword.lower() in news['content'].lower() 
                      for keyword in keywords):
                    filtered_news.append(news)
            return filtered_news if filtered_news else sample_news

        return sample_news

    def _get_fallback_market_data(self, symbols: List[str]) -> Dict[str, Any]:
        """Provide fallback market data when APIs fail"""
        return {
            'symbols': symbols,
            'price_data': {symbol: {
                'current_price': 100.0,
                'price_change': 0.0,
                'price_change_pct': 0.0,
                'volume': 1000000
            } for symbol in symbols},
            'error': 'Using fallback data - external APIs unavailable',
            'timestamp': datetime.utcnow().isoformat()
        }

    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.session:
                await self.session.close()
            logger.info("Market data service cleanup completed")
        except Exception as e:
            logger.error(f"Error during market data cleanup: {e}")

    async def _test_connectivity(self):
        """Test basic connectivity"""
        try:
            # Test a simple request
            async with self.session.get('https://httpbin.org/status/200', timeout=5) as response:
                if response.status == 200:
                    logger.info("Market data service connectivity test passed")
        except:
            logger.warning("Market data service connectivity test failed")
