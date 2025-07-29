#!/usr/bin/env python3
"""
MySQL Database Setup Script for Semiconductor Trade Monitor
Creates database, user, and initial schema
"""

import mysql.connector
import os
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_database_and_user():
    """Create MySQL database and user"""
    
    # Try different MySQL root connection methods
    mysql_configs = [
        {
            'host': 'localhost',
            'user': 'root',
            'password': '',
            'unix_socket': '/var/run/mysqld/mysqld.sock'
        },
        {
            'host': 'localhost', 
            'user': 'root',
            'password': ''
        }
    ]
    
    # Database configuration
    db_name = os.getenv('MYSQL_DATABASE', 'semiconductor_trade')
    db_user = os.getenv('MYSQL_USER', 'semiconductor_user')
    db_password = os.getenv('MYSQL_PASSWORD', 'semiconductor_pass')
    
    connection = None
    for i, mysql_config in enumerate(mysql_configs):
        try:
            # Connect to MySQL server
            print(f"Attempting connection method {i+1}...")
            connection = mysql.connector.connect(**mysql_config)
            print("✓ Connected to MySQL server")
            break
        except Error as err:
            print(f"Connection method {i+1} failed: {err}")
            if i == len(mysql_configs) - 1:  # Last attempt
                raise err
            continue
    
    try:
        cursor = connection.cursor()
        
        # Create database
        print(f"Creating database: {db_name}")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        
        # Create user and grant privileges
        print(f"Creating user: {db_user}")
        cursor.execute(f"CREATE USER IF NOT EXISTS '{db_user}'@'localhost' IDENTIFIED BY '{db_password}'")
        cursor.execute(f"GRANT ALL PRIVILEGES ON {db_name}.* TO '{db_user}'@'localhost'")
        cursor.execute("FLUSH PRIVILEGES")
        
        print("✓ MySQL database and user created successfully")
        
        # Test connection with new user
        test_config = {
            'host': 'localhost',
            'user': db_user,
            'password': db_password,
            'database': db_name
        }
        
        test_conn = mysql.connector.connect(**test_config)
        test_cursor = test_conn.cursor()
        test_cursor.execute("SELECT 1")
        result = test_cursor.fetchone()
        
        if result[0] == 1:
            print("✓ Database connection test successful")
        
        test_cursor.close()
        test_conn.close()
        
    except Error as err:
        print(f"Error: {err}")
        if err.errno == 1045:  # Access denied
            print("\nTIP: If you get access denied, try:")
            print("sudo mysql -u root -p")
            print("Then run: ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '';")
        return False
    
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
    
    return True

def create_schema():
    """Create database schema with proper indexes and foreign keys"""
    
    from config.database import db_config
    
    # Set to MySQL mode
    os.environ['DB_TYPE'] = 'mysql'
    
    try:
        print("Creating database schema...")
        
        # Countries reference table
        countries_schema = """
        CREATE TABLE IF NOT EXISTS countries (
            iso3 VARCHAR(3) PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            region VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_country_name (name)
        ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """
        
        # HS codes reference table  
        hs_codes_schema = """
        CREATE TABLE IF NOT EXISTS hs_codes (
            hs6 VARCHAR(6) PRIMARY KEY,
            description TEXT NOT NULL,
            category VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_hs_category (category),
            FULLTEXT(description)
        ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """
        
        # Main trade flows table with optimized indexes
        trade_flows_schema = """
        CREATE TABLE IF NOT EXISTS trade_flows (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            period VARCHAR(10) NOT NULL,
            reporter_iso VARCHAR(3) NOT NULL,
            partner_iso VARCHAR(3) NOT NULL,
            hs6 VARCHAR(6) NOT NULL,
            hs_extended VARCHAR(10),
            value_usd DECIMAL(15,2),
            quantity DECIMAL(15,3),
            unit VARCHAR(20),
            src_system VARCHAR(20) DEFAULT 'api',
            data_quality_score TINYINT DEFAULT 100,
            load_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            
            -- Indexes for performance
            INDEX idx_period (period),
            INDEX idx_reporter (reporter_iso),
            INDEX idx_partner (partner_iso),
            INDEX idx_hs6 (hs6),
            INDEX idx_value (value_usd),
            INDEX idx_load_time (load_time),
            INDEX idx_composite_main (period, reporter_iso, partner_iso, hs6),
            INDEX idx_composite_value (period, hs6, value_usd),
            
            -- Foreign key constraints
            FOREIGN KEY (reporter_iso) REFERENCES countries(iso3) ON DELETE RESTRICT,
            FOREIGN KEY (partner_iso) REFERENCES countries(iso3) ON DELETE RESTRICT,
            FOREIGN KEY (hs6) REFERENCES hs_codes(hs6) ON DELETE RESTRICT,
            
            -- Unique constraint to prevent duplicates
            UNIQUE KEY uk_trade_flow (period, reporter_iso, partner_iso, hs6)
        ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """
        
        # Anomalies tracking table
        anomalies_schema = """
        CREATE TABLE IF NOT EXISTS trade_anomalies (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            period VARCHAR(10) NOT NULL,
            commodity VARCHAR(100) NOT NULL,
            trade_route VARCHAR(100) NOT NULL,
            current_value DECIMAL(15,2),
            previous_value DECIMAL(15,2),
            change_percent DECIMAL(8,2),
            alert_type ENUM('SPIKE', 'DROP') NOT NULL,
            severity ENUM('LOW', 'MEDIUM', 'HIGH') NOT NULL,
            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            INDEX idx_period_anomaly (period),
            INDEX idx_severity (severity),
            INDEX idx_detected_at (detected_at)
        ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """
        
        # API usage tracking table
        api_usage_schema = """
        CREATE TABLE IF NOT EXISTS api_usage_log (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            endpoint VARCHAR(100) NOT NULL,
            method VARCHAR(10) NOT NULL,
            parameters JSON,
            response_time_ms INT,
            status_code INT,
            user_ip VARCHAR(45),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            INDEX idx_endpoint (endpoint),
            INDEX idx_timestamp (timestamp),
            INDEX idx_status (status_code)
        ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """
        
        # Execute schema creation
        schemas = [
            ('countries', countries_schema),
            ('hs_codes', hs_codes_schema),
            ('trade_flows', trade_flows_schema),  
            ('trade_anomalies', anomalies_schema),
            ('api_usage_log', api_usage_schema)
        ]
        
        for table_name, schema in schemas:
            print(f"Creating table: {table_name}")
            db_config.execute_query(schema, fetch='none')
        
        print("✓ Database schema created successfully")
        return True
        
    except Exception as err:
        print(f"Error creating schema: {err}")
        return False

def populate_reference_data():
    """Populate reference tables with initial data"""
    
    from config.database import db_config
    
    try:
        print("Populating reference data...")
        
        # Country data
        countries_data = [
            ('KOR', 'South Korea', 'Asia'),
            ('TWN', 'Taiwan', 'Asia'),
            ('USA', 'United States', 'North America'),  
            ('CHN', 'China', 'Asia'),
            ('JPN', 'Japan', 'Asia'),
            ('NLD', 'Netherlands', 'Europe'),
            ('DEU', 'Germany', 'Europe'),
            ('SGP', 'Singapore', 'Asia'),
            ('MYS', 'Malaysia', 'Asia'),
            ('THA', 'Thailand', 'Asia')
        ]
        
        country_query = """
        INSERT IGNORE INTO countries (iso3, name, region)
        VALUES (%s, %s, %s)
        """
        
        rows_inserted = db_config.execute_many(country_query, countries_data)
        print(f"✓ Inserted {rows_inserted} countries")
        
        # HS codes data
        hs_codes_data = [
            ('854232', 'HBM/DRAM/SRAM ICs', 'Memory'),
            ('854231', 'GPU/AI Accelerators', 'Processors'),
            ('848620', 'Lithography Tools', 'Equipment')
        ]
        
        hs_query = """
        INSERT IGNORE INTO hs_codes (hs6, description, category)
        VALUES (%s, %s, %s)
        """
        
        rows_inserted = db_config.execute_many(hs_query, hs_codes_data)
        print(f"✓ Inserted {rows_inserted} HS codes")
        
        return True
        
    except Exception as err:
        print(f"Error populating reference data: {err}")
        return False

def main():
    """Main setup function"""
    
    print("=" * 70)
    print("SEMICONDUCTOR TRADE MONITOR - MySQL Setup")
    print("=" * 70)
    
    # Step 1: Create database and user
    if not create_database_and_user():
        print("❌ Failed to create database and user")
        return False
    
    # Step 2: Create schema
    if not create_schema():
        print("❌ Failed to create schema")
        return False
    
    # Step 3: Populate reference data
    if not populate_reference_data():
        print("❌ Failed to populate reference data")
        return False
    
    # Step 4: Test configuration
    from config.database import db_config
    test_result = db_config.test_connection()
    
    if test_result['status'] == 'connected':
        print(f"✓ Database test successful")
        print(f"  Version: {test_result['version']}")
        print(f"  Timestamp: {test_result['timestamp']}")
    else:
        print(f"❌ Database test failed: {test_result['error']}")
        return False
    
    print("\n" + "=" * 70)
    print("✅ MySQL SETUP COMPLETED SUCCESSFULLY")
    print("Database is ready for the Semiconductor Trade Monitor!")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    main()