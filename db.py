"""
Create test database for LangGraph Query Engine Agent
Run this first to create the test data
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_database(db_path: str = "test_dashboard.db"):
    """Create test database with diverse data for testing"""
    
    if os.path.exists(db_path):
        os.remove(db_path)
        logger.info(f"Removed existing database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    logger.info(f"Creating test database: {db_path}")
    
    # Create tables
    cursor.execute("""
    CREATE TABLE users (
        user_id INTEGER PRIMARY KEY,
        username VARCHAR(50) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        first_name VARCHAR(50),
        last_name VARCHAR(50),
        registration_date DATE,
        status VARCHAR(20) DEFAULT 'active',
        country VARCHAR(50),
        age INTEGER
    )
    """)
    
    cursor.execute("""
    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY,
        product_name VARCHAR(100) NOT NULL,
        category VARCHAR(50),
        price DECIMAL(10,2),
        cost DECIMAL(10,2),
        launch_date DATE,
        status VARCHAR(20) DEFAULT 'active',
        brand VARCHAR(50)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE sales (
        sale_id INTEGER PRIMARY KEY,
        user_id INTEGER,
        product_id INTEGER,
        sale_date DATE,
        quantity INTEGER,
        unit_price DECIMAL(10,2),
        total_amount DECIMAL(10,2),
        discount_amount DECIMAL(10,2) DEFAULT 0,
        sales_channel VARCHAR(30),
        region VARCHAR(50),
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )
    """)
    
    # Insert diverse sample data
    categories = ['Software', 'Hardware', 'Electronics', 'Books', 'Clothing', 'Home & Garden', 'Sports', 'Automotive']
    brands = ['TechCorp', 'DataViz', 'SmartSoft', 'ProTools', 'VizMaster']
    regions = ['North America', 'Europe', 'Asia', 'Australia', 'South America', 'Africa']
    channels = ['web', 'mobile', 'retail', 'partner', 'phone']
    
    # Insert products with diverse categories
    products = []
    product_id = 1
    for category in categories:
        for i in range(4):  # 4 products per category
            products.append((
                product_id,
                f"{category} Product {i+1}",
                category,
                round(random.uniform(19.99, 299.99), 2),
                round(random.uniform(10.00, 100.00), 2),
                (datetime.now() - timedelta(days=random.randint(30, 365))).date(),
                'active',
                random.choice(brands)
            ))
            product_id += 1
    
    cursor.executemany("INSERT INTO products VALUES (?,?,?,?,?,?,?,?)", products)
    
    # Insert users
    users = []
    for i in range(1, 51):  # 50 users
        users.append((
            i, f'user_{i}', f'user{i}@test.com', f'User{i}', 'Test',
            (datetime.now() - timedelta(days=random.randint(30, 730))).date(),
            random.choice(['active', 'inactive']),
            random.choice(['USA', 'Canada', 'UK', 'Germany', 'Australia']),
            random.randint(18, 65)
        ))
    cursor.executemany("INSERT INTO users VALUES (?,?,?,?,?,?,?,?,?)", users)
    
    # Insert sales data with good distribution
    sales = []
    sale_id = 1
    start_date = datetime.now() - timedelta(days=365)
    
    for day in range(365):
        current_date = start_date + timedelta(days=day)
        
        # More sales on weekdays and holidays
        base_sales = 3
        if current_date.weekday() < 5:  # Weekday
            base_sales += 2
        if current_date.month in [11, 12]:  # Holiday season
            base_sales += 3
        
        daily_sales = random.randint(1, base_sales + random.randint(0, 3))
        
        for _ in range(daily_sales):
            user_id = random.randint(1, 50)
            product_id = random.randint(1, len(products))
            quantity = random.choices([1, 2, 3, 4, 5], weights=[50, 25, 15, 7, 3])[0]
            unit_price = round(random.uniform(19.99, 299.99), 2)
            total_amount = round(quantity * unit_price, 2)
            discount_amount = round(total_amount * random.choice([0, 0.05, 0.10, 0.15]), 2)
            
            sales.append((
                sale_id, user_id, product_id, current_date.date(),
                quantity, unit_price, total_amount, discount_amount,
                random.choice(channels), random.choice(regions)
            ))
            sale_id += 1
    
    cursor.executemany("INSERT INTO sales VALUES (?,?,?,?,?,?,?,?,?,?)", sales)
    
    conn.commit()
    
    # Display summary
    print(f"\nDatabase created successfully: {db_path}")
    print(f"Products: {len(products)} across {len(categories)} categories")
    print(f"Users: {len(users)}")
    print(f"Sales: {len(sales)} records")
    
    # Show sample data
    cursor.execute("""
    SELECT p.category, COUNT(*) as sales_count, SUM(s.total_amount) as total_revenue
    FROM sales s
    JOIN products p ON s.product_id = p.product_id
    GROUP BY p.category
    ORDER BY total_revenue DESC
    """)
    
    print(f"\nRevenue by Category:")
    for row in cursor.fetchall()[:5]:
        print(f"  {row[0]}: ${row[2]:,.2f} ({row[1]} sales)")
    
    conn.close()
    return db_path

if __name__ == "__main__":
    create_test_database()