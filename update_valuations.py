import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime
import statistics

async def recalculate_sample_valuations():
    # Connect to MongoDB
    mongo_url = 'mongodb://localhost:27017'
    client = AsyncIOMotorClient(mongo_url)
    db = client['test_database']
    
    # Get unique jersey signatures
    signatures = await db.price_history.distinct('jersey_signature')
    
    for signature in signatures:
        # Get all price data for this jersey type
        price_data = await db.price_history.find({'jersey_signature': signature}).to_list(1000)
        
        if not price_data:
            continue
        
        # Extract prices and categorize
        all_prices = [item['price'] for item in price_data]
        sales_prices = [item['price'] for item in price_data if item['transaction_type'] == 'sale']
        listing_prices = [item['price'] for item in price_data if item['transaction_type'] == 'listing']
        
        # Calculate estimates with weighted approach
        if len(sales_prices) >= 3:
            prices = sales_prices
        else:
            weighted_prices = []
            for item in price_data:
                if item['transaction_type'] == 'sale':
                    weighted_prices.extend([item['price']] * 3)
                elif item['transaction_type'] == 'collector_estimate':
                    weighted_prices.extend([item['price']] * 2)
                else:
                    weighted_prices.append(item['price'])
            prices = weighted_prices
        
        if len(prices) < 2:
            continue
        
        # Sort prices
        prices.sort()
        
        # Calculate percentiles
        def percentile(data, p):
            n = len(data)
            if n == 0:
                return 0
            if n == 1:
                return data[0]
            
            k = (n - 1) * p / 100
            f = int(k)
            c = k - f
            
            if f + 1 < n:
                return data[f] * (1 - c) + data[f + 1] * c
            else:
                return data[f]
        
        low_estimate = percentile(prices, 25)
        median_estimate = percentile(prices, 50)
        high_estimate = percentile(prices, 75)
        
        # Market data analysis
        market_data = {
            'total_data_points': len(all_prices),
            'sales_count': len(sales_prices),
            'listings_count': len(listing_prices),
            'price_range': {
                'min': min(all_prices) if all_prices else 0,
                'max': max(all_prices) if all_prices else 0
            },
            'last_sale_price': sales_prices[-1] if sales_prices else None,
            'confidence_score': min(100, (len(sales_prices) * 30 + len(all_prices) * 10))
        }
        
        # Create valuation
        valuation = {
            'id': f'val_{signature}',
            'jersey_signature': signature,
            'low_estimate': round(low_estimate, 2),
            'median_estimate': round(median_estimate, 2),
            'high_estimate': round(high_estimate, 2),
            'total_listings': len(listing_prices),
            'total_sales': len(sales_prices),
            'last_updated': datetime.utcnow(),
            'market_data': market_data
        }
        
        # Upsert valuation
        await db.jersey_valuations.update_one(
            {'jersey_signature': signature},
            {'$set': valuation},
            upsert=True
        )
        
        print(f'Updated valuation for {signature}:')
        print(f'   Low: ${low_estimate:.2f} | Median: ${median_estimate:.2f} | High: ${high_estimate:.2f}')
    
    client.close()

# Run the async function
asyncio.run(recalculate_sample_valuations())
