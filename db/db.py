import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, db_path: str = "supply_chain.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        try:
            schema_path = os.path.join(os.path.dirname(__file__), "models.sql")
            if os.path.exists(schema_path):
                with open(schema_path, "r") as file:
                    schema_sql = file.read()

                with sqlite3.connect(self.db_path) as conn:
                    conn.executescript(schema_sql)
                    conn.commit()
                logger.info("Database initialized successfully")
            else:
                logger.error(f"schema file not found: {schema_path}")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def execute_query(self, query, params=()) -> List[Dict[str, Any]]:
        try:
            with self.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise

    def execute_update(self, query, params=()) -> int:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            logger.error(f"Error executing update: {e}")
            raise

    def clear_all_data(self):
        """Clear all data from all tables - useful for testing"""
        tables = [
            "Ratings",
            "Orders",
            "Inspection",
            "Batch",
            "Manufacturer",
            "Aggregators",
            "Consumers",
            "Farmers",
            "KYC",
        ]
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                for table in tables:
                    cursor.execute(f"DELETE FROM {table}")
                conn.commit()
            logger.info("All data cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing data: {e}")

    # KYC Operations
    def create_kyc(self, kyc_id: str, document_number: str) -> bool:
        query = """
        INSERT INTO KYC (kyc_id, document_number, verification_status, verified_at)
        VALUES (?, ?, 'Pending', ?)
        """
        try:
            self.execute_update(query, (kyc_id, document_number, datetime.now()))
            return True
        except Exception as e:
            logger.error(f"Error creating KYC: {e}")
            return False

    def update_kyc_status(self, kyc_id: str, status: str) -> bool:
        query = (
            "UPDATE KYC SET verification_status = ?, verified_at = ? WHERE kyc_id = ?"
        )
        try:
            rows_affected = self.execute_update(query, (status, datetime.now(), kyc_id))
            return rows_affected > 0
        except Exception as e:
            logger.error(f"Error updating KYC status: {e}")
            return False

    def create_farmer(
        self, farmer_id: str, name: str, location: str, contact_number: str, kyc_id: str
    ) -> bool:
        """Create a new farmer record."""
        query = """
        INSERT INTO Farmers (farmer_id, name, location, contact_number, kyc_id)
        VALUES (?, ?, ?, ?, ?)
        """
        try:
            self.execute_update(
                query, (farmer_id, name, location, contact_number, kyc_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error creating farmer: {e}")
            return False

    def get_farmer(self, farmer_id: str) -> Optional[Dict[str, Any]]:
        """Get farmer details by ID."""
        query = "SELECT * FROM Farmers WHERE farmer_id = ?"
        try:
            results = self.execute_query(query, (farmer_id,))
            return results[0] if results else None
        except Exception as e:
            logger.error(f"Error getting farmer: {e}")
            return None

    # Batch Operations
    def create_batch(
        self, batch_id: str, batch_type: str, geotag: str, farmer_id: str
    ) -> bool:
        """Create a new batch record."""
        query = """
        INSERT INTO Batch (batch_id, type, geotag, farmer_id, date, time)
        VALUES (?, ?, ?, ?, DATE('now'), TIME('now'))
        """
        try:
            self.execute_update(query, (batch_id, batch_type, geotag, farmer_id))
            return True
        except Exception as e:
            logger.error(f"Error creating batch: {e}")
            return False

    def update_batch_status(self, batch_id: str, status: str) -> bool:
        """Update batch status."""
        query = "UPDATE Batch SET status = ? WHERE batch_id = ?"
        try:
            rows_affected = self.execute_update(query, (status, batch_id))
            return rows_affected > 0
        except Exception as e:
            logger.error(f"Error updating batch status: {e}")
            return False

    def get_batch(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Get batch details by ID."""
        query = "SELECT * FROM Batch WHERE batch_id = ?"
        try:
            results = self.execute_query(query, (batch_id,))
            return results[0] if results else None
        except Exception as e:
            logger.error(f"Error getting batch: {e}")
            return None

    # Consumer Operations
    def create_consumer(
        self, consumer_id: str, consumer_name: str, verification: str = "Pending"
    ) -> bool:
        """Create a new consumer record."""
        query = """
        INSERT INTO Consumers (consumer_id, consumer_name, verification)
        VALUES (?, ?, ?)
        """
        try:
            self.execute_update(query, (consumer_id, consumer_name, verification))
            return True
        except Exception as e:
            logger.error(f"Error creating consumer: {e}")
            return False

    # Order Operations
    def create_order(
        self,
        order_id: str,
        order_from: str,
        from_id: str,
        receiver: str,
        receiver_id: str,
        batch_id: str,
        quantity: float,
        price: float,
    ) -> bool:
        """Create a new order record."""
        query = """
        INSERT INTO Orders (order_id, order_from, from_id, reciever, reciever_id,
                            batch_id, quantity, price)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        try:
            self.execute_update(
                query,
                (
                    order_id,
                    order_from,
                    from_id,
                    receiver,
                    receiver_id,
                    batch_id,
                    quantity,
                    price,
                ),
            )
            return True
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            return False

    def update_order_status(self, order_id: str, status: str) -> bool:
        """Update order status."""
        query = "UPDATE Orders SET status = ? WHERE order_id = ?"
        try:
            rows_affected = self.execute_update(query, (status, order_id))
            return rows_affected > 0
        except Exception as e:
            logger.error(f"Error updating order status: {e}")
            return False

    # Rating Operations
    def create_rating(
        self, rating_id: str, consumer_id: str, farmer_id: str, rating: float
    ) -> bool:
        """Create a new rating record."""
        if not (0 <= rating <= 5):
            logger.error("Rating must be between 0 and 5")
            return False

        query = """
        INSERT INTO Ratings (rating_id, consumer_id, farmer_id, rating)
        VALUES (?, ?, ?, ?)
        """
        try:
            self.execute_update(query, (rating_id, consumer_id, farmer_id, rating))
            return True
        except Exception as e:
            logger.error(f"Error creating rating: {e}")
            return False

    # Utility methods
    def get_farmer_batches(self, farmer_id: str) -> List[Dict[str, Any]]:
        """Get all batches for a specific farmer."""
        query = "SELECT * FROM Batch WHERE farmer_id = ?"
        return self.execute_query(query, (farmer_id,))

    def get_farmer_ratings(self, farmer_id: str) -> List[Dict[str, Any]]:
        """Get all ratings for a specific farmer."""
        query = "SELECT * FROM Ratings WHERE farmer_id = ?"
        return self.execute_query(query, (farmer_id,))

    def get_batch_orders(self, batch_id: str) -> List[Dict[str, Any]]:
        """Get all orders for a specific batch."""
        query = "SELECT * FROM Orders WHERE batch_id = ?"
        return self.execute_query(query, (batch_id,))


# # Example usage and testing
# if __name__ == "__main__":
#     # Initialize database
#     db = DatabaseManager()
#     db.clear_all_data()

#     # Test data
#     print("Testing database operations...")

#     # Test KYC creation
#     if db.create_kyc("KYC001", "AADHAAR123456789"):
#         print("✅ KYC created successfully")

#     # Test farmer creation
#     if db.create_farmer("FARMER001", "John Doe", "Mumbai", "+919876543210", "KYC001"):
#         print("✅ Farmer created successfully")

#     # Test batch creation
#     if db.create_batch("BATCH001", "Organic Wheat", "19.0760,72.8777", "FARMER001"):
#         print("✅ Batch created successfully")


#     # Test consumer creation
#     if db.create_consumer("CONSUMER001", "Jane Smith"):
#         print("✅ Consumer created successfully")

#     # Test order creation
#     if db.create_order("ORDER001", "Consumer", "CONSUMER001", "Farmer",
#                       "FARMER001", "BATCH001", 100.0, 5000.0):
#         print("✅ Order created successfully")

#     # Test rating creation
#     if db.create_rating("RATING001", "CONSUMER001", "FARMER001", 4.5):
#         print("✅ Rating created successfully")

#     # Test data retrieval
#     farmer = db.get_farmer("FARMER001")
#     if farmer:
#         print(f"✅ Retrieved farmer: {farmer['name']}")

#     batch = db.get_batch("BATCH001")
#     if batch:
#         print(f"✅ Retrieved batch: {batch['type']}")

#     print("Database testing completed!")
