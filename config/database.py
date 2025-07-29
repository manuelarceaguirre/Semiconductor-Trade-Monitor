#!/usr/bin/env python3
"""
Database configuration and connection management
Supports both SQLite (development) and MySQL (production)
"""

import os
import mysql.connector
from mysql.connector import pooling
import sqlite3
from typing import Optional, Dict, Any
from contextlib import contextmanager
import logging

class DatabaseConfig:
    def __init__(self):
        self.db_type = os.getenv('DB_TYPE', 'sqlite')  # 'sqlite' or 'mysql'
        
        # MySQL Configuration
        self.mysql_config = {
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'port': int(os.getenv('MYSQL_PORT', '3306')),
            'user': os.getenv('MYSQL_USER', 'semiconductor_user'),
            'password': os.getenv('MYSQL_PASSWORD', 'semiconductor_pass'),
            'database': os.getenv('MYSQL_DATABASE', 'semiconductor_trade'),
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci',
            'autocommit': False,
            'pool_name': 'semiconductor_pool',
            'pool_size': 10,
            'pool_reset_session': True,
            'sql_mode': 'TRADITIONAL,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO'
        }
        
        # SQLite Configuration (fallback)
        self.sqlite_config = {
            'database': os.getenv('SQLITE_DATABASE', 'semiconductor_trade.db'),
            'check_same_thread': False,
            'timeout': 30
        }
        
        self._connection_pool = None
        self._setup_logging()
    
    def _setup_logging(self):
        """Set up database logging"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def initialize_mysql_pool(self):
        """Initialize MySQL connection pool"""
        if self.db_type != 'mysql':
            return
        
        try:
            self._connection_pool = pooling.MySQLConnectionPool(**self.mysql_config)
            self.logger.info("MySQL connection pool initialized successfully")
        except mysql.connector.Error as err:
            self.logger.error(f"Failed to initialize MySQL pool: {err}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get database connection (context manager)"""
        if self.db_type == 'mysql':
            if not self._connection_pool:
                self.initialize_mysql_pool()
            
            connection = None
            try:
                connection = self._connection_pool.get_connection()
                yield connection
            except mysql.connector.Error as err:
                if connection:
                    connection.rollback()
                self.logger.error(f"MySQL connection error: {err}")
                raise
            finally:
                if connection and connection.is_connected():
                    connection.close()
        
        else:  # SQLite fallback
            connection = None
            try:
                connection = sqlite3.connect(**self.sqlite_config)
                connection.row_factory = sqlite3.Row  # Enable dict-like access
                yield connection
            except sqlite3.Error as err:
                if connection:
                    connection.rollback()
                self.logger.error(f"SQLite connection error: {err}")
                raise
            finally:
                if connection:
                    connection.close()
    
    def get_cursor(self, connection):
        """Get cursor with proper configuration"""
        if self.db_type == 'mysql':
            return connection.cursor(dictionary=True, buffered=True)
        else:
            return connection.cursor()
    
    def execute_query(self, query: str, params: Optional[tuple] = None, fetch: str = 'all'):
        """Execute query and return results"""
        with self.get_connection() as conn:
            cursor = self.get_cursor(conn)
            try:
                cursor.execute(query, params or ())
                
                if fetch == 'all':
                    result = cursor.fetchall()
                elif fetch == 'one':
                    result = cursor.fetchone()
                elif fetch == 'none':
                    result = None
                else:
                    result = cursor.fetchmany(fetch)
                
                conn.commit()
                return result
            
            except Exception as err:
                conn.rollback()
                self.logger.error(f"Query execution error: {err}")
                raise
            finally:
                cursor.close()
    
    def execute_many(self, query: str, data: list):
        """Execute query with multiple parameter sets"""
        with self.get_connection() as conn:
            cursor = self.get_cursor(conn)
            try:
                cursor.executemany(query, data)
                conn.commit()
                return cursor.rowcount
            except Exception as err:
                conn.rollback()
                self.logger.error(f"Bulk query execution error: {err}")
                raise
            finally:
                cursor.close()
    
    def test_connection(self) -> Dict[str, Any]:
        """Test database connection and return status"""
        try:
            with self.get_connection() as conn:
                cursor = self.get_cursor(conn)
                
                if self.db_type == 'mysql':
                    cursor.execute("SELECT VERSION() as version, NOW() as timestamp")
                else:
                    cursor.execute("SELECT sqlite_version() as version, datetime('now') as timestamp")
                
                result = cursor.fetchone()
                cursor.close()
                
                return {
                    'status': 'connected',
                    'database_type': self.db_type,
                    'version': result['version'] if self.db_type == 'mysql' else result['version'],
                    'timestamp': result['timestamp']
                }
        
        except Exception as err:
            return {
                'status': 'error',
                'database_type': self.db_type,
                'error': str(err)
            }

# Global database configuration instance
db_config = DatabaseConfig()